#!/usr/bin/env python3


def ReadDisang(fname):
    """
    Reads an amber restraint file and return a list of dictionaries.
    Each element of the list corresponds to a namelist entry.
    Each key of a dictionary corresponds to the namelist key.
    """
    
    fh=open(fname,"r")
    entries = []
    entry=""
    for line in fh:
        line = line.strip()
        if "&rst" in line:
            entry = line
        else:
            entry += " " + line
        if "/" in entry:
            entries.append(entry)
            entry = ""
    for i in range(len(entries)):
        entries[i] = entries[i].replace("&rst","").replace("/","").replace(","," ")

    data=[]
    for entry in entries:
        sections = entry.split("=")
        edict = {}
        for isec in range(1,len(sections)):
            arr = sections[isec-1].split()
            key = arr[-1]
            vals = sections[isec].split()
            if isec < len(sections)-1:
                vals = vals[:-1]
            if key == "iat":
                vals = [ int(v) for v in vals ]
            else:
                vals = [ float(v) for v in vals ]
            edict[key] = vals
        data.append(edict)
    return data


#def MakeChunks( istart, istop, nchunks ):
#    import numpy as np
#    nchunks = min(istop-istart,nchunks)
#    return np.array_split( range(istart,istop), nchunks )

def SizedChunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
def MakeChunksWithSize( istart, istop, size ):
    # return a list of list of indexes from istart to istop
    # each sublist contains approximately "size" elements
    chunks = [ [ i for i in gen ]
               for gen in SizedChunks(range(istart,istop),size) ]
    
    if len(chunks) > 1:
        if len(chunks[-1]) < size*2/3:
            chunks[-2].extend(chunks[-1])
            del chunks[-1]
    return chunks


def MakeGroupedChunks( ene, size ):
    # return a list of list of indexes. This extends MakeChunksWithSize
    # by grouping adjacent chunks together if their means pass the t-test
    from scipy.stats import ttest_ind
    cidxs = MakeChunksWithSize(0,ene.shape[0],size)
    nchk = len(cidxs)
    ichk = 0
    #print("input chunk len ",nchk)
    while ichk < nchk-1:
        t,p = ttest_ind(ene[cidxs[ichk]],ene[cidxs[ichk+1]],
                        equal_var=False)
        if p > 0.05:
            cidxs[ichk].extend(cidxs[ichk+1])
            del cidxs[ichk+1]
            nchk -= 1
        else:
            ichk += 1
    #print("output chunk len",len(cidxs))
    return cidxs



def extract_traditional_ti( fname, write=False, odir="", skip_bad=False,
                            maxsamples=1000000, undefene=None ):
    import os
    from collections import defaultdict as ddict
    import re
    import numpy as np
    from pathlib import Path

    fh = open(fname,"r")
    if not fh:
        raise Exception("Could not open %s\n"%(fname))

    hasmbar=True
    
    numexchg=0
    nstlim=None
    ntpr=None
    dt=None
    irest=0
    mbar_states=0
    mbar_lambda=[]
    lam_values=[]
    for line in fh:
        cmdstr,sepstr,comstr = line.partition("!")
        cmdstr = cmdstr.strip()
        if "mbar_lambda" in cmdstr:
            lams=[]
            cols = cmdstr.replace("="," ").replace(","," ").strip().split()
            for icol in range(len(cols)-1):
                if "mbar_lambda" in cols[icol]:
                    fcol=icol+1
                    break
            cs = [ float(x) for x in cols[fcol:] ]
            m = re.search(r"mbar_lambda\( *([0-9]+) *: *([0-9]+) *\).*",cmdstr)
            if m:
                i0 = int( m.group(1) )-1
                i1 = int( m.group(2) )-1
                while len(mbar_states) < i1+1:
                    mbar_lambda.append(-1.)
                for ii,i in enumerate(range(i0,i1+1)):
                    mbar_lambda[i] = lams[ii]
            else:
                m = re.search(r"mbar_lambda\( *([0-9]+) *\).*",cmdstr)
                if m:
                    i0 = int( m.group(1) )-1
                    while len(mbar_lambda) < i0+1:
                        mbar_lambda.append(-1.)
                    mbar_lambda[i0] = cs[0]
                else:
                    mbar_lambda=cs
        if "mbar_states" in cmdstr:
            cols = cmdstr.replace("=","").replace(",","").strip().split()
            for icol in range(len(cols)-1):
                if cols[icol] == "mbar_states":
                    mbar_states = int( cols[icol+1] )
                    break
        if "lambda values considered:" in line:
            while True:
                line = next(fh)
                if "Extra" in line:
                    break
                cmdstr,sepstr,comstr = line.partition("!")
                if "total:" in cmdstr:
                    cs = cmdstr.split()[2:]
                else:
                    cs = cmdstr.split()
                lam_values.extend( [float(x) for x in cs] )

        if "ntpr" in cmdstr:
            cols = cmdstr.replace("=","").replace(",","").strip().split()
            #print(cols)
            for icol in range(len(cols)-1):
                if cols[icol] == "ntpr":
                    ntpr = int( cols[icol+1] )
                    break
        if "dt" in cmdstr:
            cols = cmdstr.replace("=","").replace(",","").strip().split()
            for icol in range(len(cols)-1):
                if cols[icol] == "dt":
                    dt = float( cols[icol+1] )
                    break
        if "numexchg" in cmdstr:
            cols = cmdstr.replace("=","").replace(",","").strip().split()
            for icol in range(len(cols)-1):
                if cols[icol] == "numexchg":
                    numexchg = int( cols[icol+1] )
                    break
        if "nstlim" in cmdstr:
            cols = cmdstr.replace("="," ").replace(",","").strip().split()
            for icol in range(len(cols)-1):
                if cols[icol] == "nstlim":
                    nstlim = int( cols[icol+1] )
                    break
        if "irest" in cmdstr:
            cols = cmdstr.replace("="," ").replace(",","").strip().split()
            for icol in range(len(cols)-1):
                if cols[icol] == "irest":
                    irest = int( cols[icol+1] )
                    break

    if ntpr is None:
        raise Exception("Could not determine ntpr from %s"%(fname))

    if dt is None:
        raise Exception("Could not determine dt from %s"%(fname))

    if nstlim is None:
        raise Exception("Could not determine nstlim from %s"%(fname))

    if numexchg < 1:
        numexchg = 1


    if len(mbar_lambda) > 0 or mbar_states > 0:
        if len(mbar_lambda) != mbar_states:
            if len(lam_values) == mbar_states:
                mbar_lambda = lam_values
            else:
                print("len(mbar_lambda) != mbar_states: %i vs %i"%(len(mbar_lambda),mbar_states))




    dt = dt
    nstep_per_sim = nstlim * numexchg
    nframe_per_sim = nstep_per_sim / ntpr

    if nstep_per_sim % ntpr != 0:
        print("num md steps per simulation is not a multiple of ntpr. Unclear how the simulation time works")

    t_per_frame = dt * ntpr
    t_per_sim = t_per_frame * nframe_per_sim


    fh = open(fname,"r")


    efeps = []
    dvdls = []
    dvdlts = []
    efepts = []
    
    efep = []
    reading_region_1 = False
    reading_summary = False
    reading_first_step = False
    lam = None
    nlam = 0
    dvdl = None
    store_dvdl = False
    store_efep = False
    ctime = None
    read_dvdl = False

    valid_mbar_states = [True]*len(mbar_lambda)
    my_valid_mbar_states = []
    
    for line in fh:
        
        store_data = False
        
        if "A V E R A G E S" in line \
           or "AVERAGES OVER" in line \
           or "R M S  F L U C T U A T I O N S" in line:
            reading_summary = True  
        elif "---------" in line and not reading_region_1:
            reading_summary = False
            
        if "NSTEP =        0" in line:
            reading_first_step = True
        elif "NSTEP =" in line:
            reading_first_step = False

        if not reading_summary and reading_region_1:
            if "TIME(PS) =" in line:
                ctime = float(line.strip().split()[5])
            
        if "MBAR Energy analysis:" in line:
            efep = []
            
        if "clambda" in line:
            if lam is None:
                cols = line.replace("="," ").replace(","," ").split()
                for i in range(len(cols)):
                    if cols[i] == "clambda":
                        lam = float(cols[i+1])
                        break
        elif "Energy at " in line:
            val = line.strip().split()[-1]
            if "****" in val:
                #val = 10000.00
                #val = 1.e+5
                if undefene is not None:
                    val = undefene
                    my_valid_mbar_states.append(True)
                else:
                    val = 1.e+5
                    hasmbar=False
                    my_valid_mbar_states.append(False)
            else:
                val = float(val)
                my_valid_mbar_states.append(True)

            efep.append( val )
        elif "TI region  1" in line:
            reading_region_1 = True
            dvdl_read = False
        elif "| TI region  2" in line:
            reading_region_1 = False
            if dvdl is not None:
                store_dvdl = True
            if len(efep) > 0:
                store_efep = True
        elif "TI region " in line:
            reading_region_1 = False
        elif "5.  TIMINGS" in line:
            if dvdl is not None:
                store_dvdl = True
            if len(efep) > 0:
                store_efep = True

        should_read_dvdl = reading_region_1 and \
            (not reading_summary) and (not reading_first_step)

        if should_read_dvdl:
            if "DV/DL  =" in line:
                cols = line.strip().split()
                dvdl = float( cols[-1] )
                dvdl_read = True
            elif "---------" in line and (not dvdl_read):
                dvdl = 0.0

        if nlam > 0:
            if store_dvdl and store_efep and len(efep) != nlam:
                store_dvdl=False
                store_efep=False
                dvdl=None
                efep=[]
                my_valid_mbar_states=[]
                
                
        if store_dvdl and not reading_first_step:
            store_dvdl = False
            dvdls.append(dvdl)
            dvdlts.append(ctime)
            dvdl = None
        if store_efep:
            store_efep = False
            efeps.append( efep )
            efepts.append( ctime )
            nlam = len(efep)
            if len(my_valid_mbar_states) != len(valid_mbar_states):
                raise Exception("Expected array of %i bool"%(len(my_valid_mbar_states)))
            else:
                for ilam in range(len(my_valid_mbar_states)):
                    if not my_valid_mbar_states[ilam]:
                        valid_mbar_states[ilam] = False
            efep = []
            my_valid_mbar_states=[]


    iclam = 0
    lams = mbar_lambda
    for i,l in enumerate(lams):
        if abs(l-lam) < 0.001:
            iclam = i
            break
            
            
    if write:
        lams = mbar_lambda
        lam = lams[iclam]
        try:
            odir = Path(odir)
            if odir.is_dir():
                dvdl_fname = Path(odir, "dvdl_%.8f.dat"%(lam))
                rem_analysis_fname = os.path.join(odir, "rem.log.yaml")
            else:
                raise RuntimeError
        except Exception:
            raise RuntimeError(f"Invalid output dir: {odir}")


        efeps = np.array(efeps)
        efepts = np.array(efepts)
        dvdls = np.array(dvdls)
        dvdlts = np.array(dvdlts)
        nsamples = efeps.shape[0]

        if nsamples == 0:
            raise ValueError("Could not read MBAR Energies. Check the .mdout files actually have MBAR Energies.")

        # s = max(1, (nsamples) // maxsamples)
        # idxs = [ i for i in range(0,nsamples,s) ]
        # o = len(idxs) - min(len(idxs),maxsamples)
        # idxs = idxs[o:]
        # print("Extracting %7i of %7i samples from %s using offset %5i and stride %5i"%(len(idxs),nsamples,fname,idxs[0],s))
        # efeps = efeps[idxs,:]
        # efepts = efepts[idxs]


        
        efep_stride = max(1, len(efepts) // maxsamples)
        efep_idxs = [ i for i in range(0,len(efepts),efep_stride) ]
        efep_offset = len(efep_idxs) - min(len(efep_idxs),maxsamples)
        efep_idxs = efep_idxs[efep_offset:]
        efeps = efeps[efep_idxs,:]
        efepts = efepts[efep_idxs]
        
        print("Extracting %7i of %7i samples from %s using offset %5i and stride %5i"%(len(efep_idxs),nsamples,fname,efep_idxs[0],efep_stride))

        dvdl_stride = max(1, len(dvdlts) // maxsamples)
        dvdl_idxs = [ i for i in range(0,len(dvdlts),dvdl_stride) ]
        dvdl_offset = len(dvdl_idxs) - min(len(dvdl_idxs),maxsamples)
        dvdl_idxs = dvdl_idxs[dvdl_offset:]
        dvdls = dvdls[dvdl_idxs]
        dvdlts = dvdlts[dvdl_idxs]

        
        nsamples = efeps.shape[0]
        

        
        skips = [False]*nsamples
        
        #
        # Mixed precision in Amber GTI may lead to cases where
        # very large positive numbers turn into large negative numbers.
        # This can happen with absolute binding/solvation free energy
        # simulations, where it wants to calculate the energy of
        # something totally there based on the coordinates when it
        # is decoupled.
        #
                
        if skip_bad:

            avgs = np.mean(efeps,axis=0)
            meds = np.median(efeps,axis=0)
            meds = meds - meds[iclam]
            
            cidxs = MakeGroupedChunks( efeps[:,iclam], 200 )
            nchunks = len(cidxs)
            for ichunk in range(nchunks):
                idxs = cidxs[ichunk]
                ref = [ x for x in efeps[idxs,iclam] ]
                ref.sort()
                n = len(idxs)
                nmin = int(0.05*n)
                nmax = int(0.95*n)
                ref = ref[nmin:nmax]
                refm = np.median(ref)
                refs = np.std(ref)

                for i in idxs:
                    for ilam,plam in enumerate(lams):
                        if meds[ilam] > 10000:
                            if efeps[i,ilam] < refm-3*refs - 1000:
                                skips[i] = True
                                #print("skip %6i e=%12.3e avg=%12.3e median=%12.3e std=%12.3e"%(i,efeps[i,ilam],refa,refm,refs))
                                break

        print("Excluding  %7i  extracted samples from %s"%(np.count_nonzero(skips),fname))
                            
        fh = open(dvdl_fname,"w")
        for i in range(len(dvdls)):
            fh.write("%.4f %.4f\n"%(dvdlts[i],dvdls[i]))
        fh.close()


        ilams = [i for i in range(len(lams))]
        if not hasmbar:
            ilam=0
            dlam=1.e+10
            for i,l in enumerate(lams):
                d = abs(lam-l)
                if d < dlam:
                    dlam = d
                    ilam = i
            lolam = max(0,ilam-1)
            hilam = min(len(lams),ilam+2)

            has_bad_state = False
            for l in range(lolam,hilam):
                if not valid_mbar_states[l]:
                    has_bad_state = True
            if has_bad_state:
                raise Exception("ERROR: Invalid energies within %s, including those needed for BAR analysis. Use the --nan option."%(fname))
            else:
                print("Invalid energies within %s; writing output for BAR. See the --nan option"%(fname))
            lams = [lams[l] for l in range(lolam,hilam)]
            ilams = [l for l in range(lolam,hilam)]

        
        for ilam,plam in zip(ilams,lams):
            efep_fname = os.path.join(odir, "efep_%.8f_%.8f.dat"%( lam, plam ) )
            
            fh = open(efep_fname,"w")
            for i in range(len(efepts)):
                if skips[i]:
                    continue
                fh.write("%.4f %.6f\n"%(efepts[i],efeps[i,ilam]))
            fh.close()

    return dvdls,efeps

def get_rst_type(iat_values):
    number_of_atoms = sum(1 for val in iat_values if val != 0)
    if number_of_atoms == 2: 
        return "Bond"
    elif number_of_atoms == 3:
        return "Angle"
    elif number_of_atoms == 4:
        return "Dihedral"
    else:
        return "Unknown"

def read_rst_file(inputfile, remodir):
    import yaml
    import os
    from pathlib import Path
    
    print("")
    print("Analyzing restraints file", )
    print("")

    restraints = {
        "Bond": {"r2": [], "rk2": []},
        "Angle": {"r2": [], "rk2": []},
        "Dihedral": {"r2": [], "rk2": []}
    }

    try:
        rsts = ReadDisang(inputfile)
        #with open(inputfile, 'r') as f:
        #    lines = f.readlines()
    except FileNotFoundError:
        raise Exception(f"File '{inputfile}' not found.")

    for irst,rst in enumerate(rsts):
        if "iat" in rst:
            rst_type = get_rst_type(rst["iat"])
        else:
            raise Exception(f"Expected 'iat' in restraint definition {inputfile}")
        if "r2" in rst and "rk2" in rst:
            restraints[rst_type]["r2"].append(rst["r2"])
            restraints[rst_type]["rk2"].append(rst["rk2"])
        else:
            raise Exception(f"Expected 'r2' and 'rk2' in restraint definition {inputfile}")
        
    # for line in lines:
    #     if line.startswith("&rst"):
    #         rst_type = None
    #         iat_values = re.search(r"iat=([0-9,]+)", line)
    #         if iat_values: 
    #             iat_values = list(map(int, iat_values.group(1).split(',')))
    #             rst_type = get_rst_type(iat_values)
    #     if "r2=" in line and "rk2=" in line:
    #         r2_match = re.search(r"r2=([-\d.]+)", line)
    #         rk2_match = re.search(r"rk2=([-\d.]+)", line)
    #         if r2_match and rk2_match:
    #             r2_value = float(r2_match.group(1))
    #             rk2_value = float(rk2_match.group(1))

    #             # Add the r2 and rk2 values to the corresponding interaction type list
    #             if rst_type in restraints:
    #                 restraints[rst_type]["r2"].append(r2_value)
    #                 restraints[rst_type]["rk2"].append(rk2_value)

    try:
        remodir = Path(remodir)
        if remodir.is_dir():
            vba_analysis_fname = remodir / "boresch_vba_rst.yaml"
        else:
            raise RuntimeError
    except Exception:
        raise RuntimeError(f"Invalid output dir: {remodir}")

    with open(vba_analysis_fname, 'w') as fh:
        yaml.dump(restraints, fh)

    print("")   
    print("Done analyzing the Boresch Restraints", )
    print("")

    #return interactions


class RESample(object):
    def __init__(self,line):
        self.rep=int(line[0:6])
        self.neigh=int(line[6:12])
        if line[66] == 'T' or line[66] == 'F':
            self.succ = line[66:67]
        else:
            self.succ = line[91:92]
        if self.succ != 'T' and self.succ != 'F':
            import sys
            sys.stderr.write(f"Error processing T/F from replica exchange log line: {line}\n")
        self.line = line[:107]

def read_rem_log(inputfile):
    import numpy as np
    import sys
    import copy
    
    print("")
    print("Analyzing remlog file", )
    print("")

    np.set_printoptions(precision=2, linewidth=150,
                        formatter={'int': '{:2d}'.format})

    rep=[]
    neigh=[]
    succ=[]
    count=0
    n_replica=0
    try:
        with open(inputfile, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise Exception(f"File '{inputfile}' not found.")

    exchanges = []
    cursamples = []
    for line in lines:
        count=count+1
        if "# exchange" in line:
            if len(cursamples) > 0:
                if n_replica == 0:
                    n_replica = len(cursamples)
                else:
                    if n_replica != len(cursamples):
                        sys.stderr.write(f"Replica exchange data is truncated in {inputfile}\n")
                        break
                # We only need the lines from the last exchange attempt
                # Delete the previous set of lines to save space
                if len(exchanges) > 0:
                    for s in exchanges[-1]:
                        s.line = None
                exchanges.append(copy.deepcopy(cursamples))

            cursamples = []
        if line[0] != '#':
            cursamples.append(RESample(line))
        #if count>200:n_replica=max(rep[0:200])

    if len(cursamples) > 0:
        if n_replica == 0:
            n_replica = len(cursamples)
        if n_replica != len(cursamples):
            sys.stderr.write(f"Replica exchange data is truncated in {inputfile}")
        else:
            # We only need the lines from the last exchange attempt
            # Delete the previous set of lines to save space
            if len(exchanges) > 0:
                for s in exchanges[-1]:
                    s.line = None
            exchanges.append(copy.deepcopy(cursamples))

    #print("len(exchanges)",len(exchanges))
    for exchange in exchanges:
        #print("len(exchange)",len(exchange))
        for sample in exchange:
            rep.append(sample.rep)
            neigh.append(sample.neigh)
            succ.append(sample.succ)

    f.close()
    print("Done reading the remlog")



    n_replica=max(rep[0:200])  
    n_step=int(len(rep)/n_replica)
    print("# of Replicas:", n_replica, "# of Steps:", n_step)
    n_state=n_replica
    # get the lines from the last exchange
    mylines = [ s.line for s in exchanges[-1] ]
    # get the last column from each line
    ARs = [line.strip().split()[-1] for line in mylines ]
    #ARs = [line.strip().split()[-1] for line in lines[-n_replica:-1]]
    ARs = [float(AR) for AR in ARs]
    #print("ARs=",ARs)
    

    replica_trajectory=np.zeros((n_replica, n_step+1), np.int64)
    replica_state_count=np.zeros((n_replica, n_state), np.int64)
    replica_ex_count=np.zeros((n_replica, n_state-1), np.int64)
    replica_ex_succ=np.zeros((n_replica, n_state-1), np.int64)

    for i in range(n_replica):
        replica_trajectory[i][0]=i+1
        replica_state_count[i][i]=1

    for m in range(n_step):
        replica_trajectory[0:n_replica, m+1]=replica_trajectory[0:n_replica, m]
        for i in range((m+1)%2,n_replica-1,2): 
            k=m*n_replica+i
            x=np.where(replica_trajectory[:,m+1]==i+1)
            y=np.where(replica_trajectory[:,m+1]==i+2)
            replica_ex_count[x[0],i]+=1
            if succ[k]=='T':
                replica_ex_succ[x[0],i]+=1
                replica_trajectory[y[0],m+1]=i+1
                replica_trajectory[x[0],m+1]=i+2

        for j in range(n_replica) :
            replica_state_count[j, replica_trajectory[j,m+1]-1]+=1
    
    return replica_trajectory, replica_state_count, \
        replica_ex_count, replica_ex_succ, ARs



def remd_analysis(replica_trajectory, ARs, remodir):
    import numpy as np
    import os
    import yaml
    from pathlib import Path
    
    n_replica=np.size(replica_trajectory, 0)
    n_state=n_replica
    n_step=np.size(replica_trajectory, 1)

    print("Analyzing", n_replica, n_step)

    h1n=[]
    hn1=[] 
    k1n=[]
    kn1=[] 
    trip_count_1n=[0]*n_replica
    trip_count_n1=[0]*n_replica
    for i in range(n_replica):
        first_step_at_1=-1
        first_step_at_n=-1
        last_step_at_1=-1
        last_step_at_n=-1
        at_1=0
        at_n=0
      
        for j in range(n_step):
            if replica_trajectory[i][j] == 1:
                last_step_at_1=j
                if at_1 ==0:
                    at_1=1
                    at_n=0
                    first_step_at_1=j
                if first_step_at_n >=0:
                    #print("Rep #",i, 'At state 1:', first_step_at_n, j, j-first_step_at_n);
                    hn1.append(j-first_step_at_n)
                    first_step_at_n=-1 
                    trip_count_n1[i]+=1
                if last_step_at_n >=0:
                    #print('**At state 1:', last_step_at_n, j, j-last_step_at_n);
                    kn1.append(j-last_step_at_n)
                    last_step_at_n=-1 
            if replica_trajectory[i][j] == n_replica:
                last_step_at_n=j
                if at_n ==0:
                    at_n=1
                    at_1=0
                    first_step_at_n=j
                    if first_step_at_1 >=0:
                        #print("Rep #",i, 'At state N:', first_step_at_1, j, j-first_step_at_1);
                        h1n.append(j-first_step_at_1)
                        first_step_at_1=-1 
                        trip_count_1n[i]+=1
                    if last_step_at_1 >=0:
                        #print('**At state N:', last_step_at_1, j, j-last_step_at_1);
                        k1n.append(j-last_step_at_1)
                        last_step_at_1=-1 


    output_data = {}
    if len(h1n)==0 or len(hn1)==0:
        print("")
        print("No single pass found", )
        print("")
        output_data["Average single pass steps:"] = 1.e+8
        output_data["Round trips per replica:"] = 0.
        output_data["Total round trips:"] = 0.
        output_data["neighbor_acceptance_ratio"] = ARs
    else:
        hh=h1n+hn1
        mean_value = np.mean(hh)
        output_data["Average single pass steps:"] = float(mean_value)
        output_data["Round trips per replica:"] = float(len(hh)/2/n_replica)
        output_data["Total round trips:"] = float(len(hh)/2)
        output_data["neighbor_acceptance_ratio"] = ARs

    try:
        remodir = Path(remodir)
        if remodir.is_dir():
            rem_analysis_fname = os.path.join(remodir, "rem.log.yaml" )
        else:
            raise RuntimeError
    except Exception:
        raise RuntimeError(f"Invalid output dir: {remodir}")

    with open(rem_analysis_fname, 'w') as fh:
        yaml.dump(output_data, fh)

    print("")
    print("Done analyzing the remlog", )
    print("")

