#!/usr/bin/env python3

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
 

if __name__ == "__main__":


    from edgembar.amber2dats import extract_traditional_ti
    from edgembar.amber2dats import remd_analysis
    from edgembar.amber2dats import read_rst_file, read_rem_log

       
    import os
    import numpy as np
    import yaml
    
    import argparse
    from pathlib import Path


    parser = argparse.ArgumentParser \
        ( formatter_class=argparse.RawTextHelpFormatter,
          description="""
          Extracts DVDL and MBAR data from 1-or-more mdout files and writes
          the data into timeseries files
          """)

    parser.add_argument \
        ("-o","--odir",
         help="Output directory. If empty, then same dir as mdout",
         type=str,
         required=False,
         default="" )
    
    parser.add_argument \
        ("--nmax",
         help="""Maximum number of samples to extract from an mdout 
file.  The stride through the data is:
         
s = min( 1, n//nmax )

where // represents integer division. Upon striding through
the data, only the last nmax samples are written.
If --exclude is also used, the striding and tail-extraction 
occurs BEFORE testing for suspicious samples.
The default value is: --nmax=10000""",
         default=10000,
         type=int,
         required=False)
 

    parser.add_argument \
        ("--exclude",
         help="""If true, then do not extract samples deemed to be
untrustworthy.  When performing absolute binding free
energy simulations, for example, the potential energy 
of 'distant' lambda  states may be very large, and the 
mixed-precision  floating point model in pmemd.cuda may 
occasionally  overflow, resulting in a large negative 
energy when it is, in fact, a very large positive energy.
This option will try to identify and exclude the errant 
samples. It does this using the following procedure:

1. We read a mdout file corresponding to a simulation 
of state slam (the simulated lambda), and we obtain a 
time-series of energies for all lambdas, E[:,lam].

2. The median of each time-series is evaluated, 
m[lam] = median(E[:,lam]).

3. The standard deviation of E[:,slam] is calculated, 
std[slam] = std( E[:,slam] ).

4. Mark each sample as being not excluded.

For each lam...

5. If m[lam] - m[slam] > 10000 kcal/mol, then inspect
the samples, and mark suspicious samples to exclude.
Otherwise continue to the next lambda value.

6. Mark sample i for exclusion if: 
E[i,lam] < m[slam] - 3*std[slam] - 1000 kcal/mol""",
         action='store_true')


    parser.add_argument \
        ('mdout',
         metavar='mdout',
         type=str,
         nargs='*',
         help='Amber mdout file')
    
    parser.add_argument \
        ('-r', '--remlog', 
         type=str, 
         help="""Replica exchange log file. Using this option will
output a 'rem.log.yaml' in the --odir folder
with single pass time and round trip analysis""",
         required=False)


    parser.add_argument \
        ('-V', '--vba',
         type=str,
         help="""Boresch/VBA restraints file. Using this option will
output a 'boresch_vba_rst.yaml' in the --odir folder
with the force constants and potential minimums used 
for the Boresch restraints""",
         required=False)


    parser.add_argument \
        ('--nan',
         type=float,
         default=None,
         help="""If an MBAR energy is '*******', then instead write
the value specified here. Default: None, which will only write the
files for BAR analysis instead of MBAR analysis.""",
         required=False)



    
    version = get_package_version("edgembar")

    
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format\
                        (version=version))


    args = parser.parse_args()



    odir = None
    tdir = None
    if len(args.odir) > 0:
        odir = args.odir
        tdir = args.odir


    for arg in args.mdout:
        if os.path.isfile( arg ):
            if ".mdout" in arg or ".out" in arg:
                tdir = odir
                if tdir is None:
                    tdir = str(Path(arg).parent)
                extract_traditional_ti\
                    ( arg,
                      write=True,
                      odir=tdir,
                      skip_bad=args.exclude,
                      maxsamples=args.nmax,
                      undefene=args.nan)
            else:
                print("File does not end in .mdout nor .out: %s"%(arg))
        else:
            print("File not found: %s"%(arg))

            
    if args.remlog:
        if tdir is None:
            if not os.path.exists(args.remlog):
                raise Exception(f"File not found: {args.remlog}")
            tdir = str(Path(args.remlog).parent)

        reptraj, nstate, nexch, nsucc, ARs = read_rem_log(args.remlog)
        np.set_printoptions(precision=5, linewidth=150,
                            formatter={'int': '{:2d}'.format})
        remd_analysis(reptraj, ARs, tdir)
        print("")
        print("Done analyzing the remlog", )
        print("")


        
    if args.vba:
        if tdir is None:
            if not os.path.exists(args.vba):
                raise Exception(f"File not found: {args.vba}")
            tdir = str(Path(args.vba).parent)

        read_rst_file(args.vba, tdir)
        print("")
        print("Analyzed restraints file")
        print("")


