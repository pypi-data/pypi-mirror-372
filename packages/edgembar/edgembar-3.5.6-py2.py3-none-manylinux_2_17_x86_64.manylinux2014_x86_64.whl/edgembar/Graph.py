#!/usr/bin/env python3
import typing
from typing import List, Optional, Tuple, DefaultDict, Dict
from . Edge import Edge
from . Results import PathData
import numpy as np

class EdgeMatch(object):
    def __init__(self, idx : int, match : bool, sign : int ):
        self.idx = idx
        self.match = match
        self.sign = sign
        

class EdgeEntry(object):
    def __init__(self,fname : str):
        from pathlib import Path
        self.idx=0
        self.fname = Path(fname)
        name = self.fname.stem
        self.nodes = name.split("~")
        for inode in range(len(self.nodes)):
            self.nodes[inode] = self.nodes[inode].split(".")[0]

        if len(self.nodes) != 2:
            raise Exception((f"Filename {fname} could not be understood "
                             f"to be an edge because it has {len(self.nodes)-1}"
                             " '~' characters"))
            
        self.fwdname = "%s~%s"%(self.nodes[0],self.nodes[1])
        self.revname = "%s~%s"%(self.nodes[1],self.nodes[0])
        self.edge = None

    def Read(self):
        from . ImportEdge import ImportEdge
        if not self.fname.is_file():
            raise Exception(f"File not found: {self.fname}")
        else:
            self.edge = ImportEdge(str(self.fname))

    def Match(self,snode,tnode):
        if snode == self.nodes[0] and tnode == self.nodes[1]:
            m = EdgeMatch(self.idx,True,1)
        elif snode == self.nodes[1] and tnode == self.nodes[0]:
            m = EdgeMatch(self.idx,True,-1)
        else:
            m = EdgeMatch(self.idx,False,0)
        return m



    

class Graph(object):

    @classmethod
    def from_glob( cls,
                   filename_glob: str,
                   exclude: Optional[List[str]] = None,
                   refnode: Optional[str] = None ):
        from glob import glob
        return cls( glob(filename_glob),
                    exclude=exclude,
                    refnode=refnode )

    
    def __init__( self,
                  fnames : List[str],
                  exclude: Optional[List[str]] = None,
                  refnode: Optional[str] = None ):
        
        import copy
        from . GraphSearch import GraphSearch
        from pathlib import Path

        self.exclude = exclude
        if exclude is not None:
            for x in exclude:
                a,b = x.split("~")
                fname = "%s~%s"%(a,b)
                rname = "%s~%s"%(b,a)
                fnames = [ f for f in fnames
                           if fname not in f and rname not in f ]
        
        self.entries = [ EdgeEntry(f) for f in fnames ]
        self.entries.sort( key = lambda e: e.fwdname )
        for i,e in enumerate(self.entries):
            e.idx = i
            
        #fnames = [ e.fwdname for e in self.entries ]
        
        self.topology = GraphSearch( [e.fwdname for e in self.entries] )

        # Make the reference node the first node
        if refnode is not None:
            if refnode in self.topology.nodes:
                idx = self.topology.nodes.index(refnode)
            else:
                raise Exception((f"Cannot use {refnode} as a reference"
                                 " node because it's not in the graph"))
            sidx = 0
            if sidx == idx:
                sidx += 1
            if sidx < len(self.topology.nodes):
                self.topology.nodes[idx],self.topology.nodes[sidx] = \
                    self.topology.nodes[sidx],self.topology.nodes[idx]
        


    def Read(self):
        did_read = False
        for e in self.entries:
            if e.edge is None:
                e.Read()
                did_read = True
            
        if did_read:
            nores = [ e.fwdname for e in self.entries
                      if e.edge.results is None ]
            if len(nores) > 0:
                raise Exception("Cannot perform graph analysis because "+
                                "some edges do not have any results: "+
                                "%s"%(str(nores)))

            nocon = [ e.fwdname for e in self.entries
                      if e.edge.results.con is None ]

            if len(nocon) > 0:
                raise Exception("Cannot perform graph analysis because "+
                                "some edges do not have constraint results: "+
                                "%s"%(str(nocon)))

            
    def Match(self, snode : str, tnode : str ) -> EdgeMatch:
        m = None
        for e in self.entries:
            m = e.Match(snode,tnode)
            if m.match:
                break
        if m is None:
            raise Exception(f"No match for {snode} -> {tnode}")
        return m
        

    def CanExcludeEdge(self, e : str):
        a,b = e.split("~")
        paths = self.topology.FindMinPaths(a,b,minsize=3)
        reachable = False
        if len(paths) > 0:
            reachable = True
        return reachable

    def ExcludeEdge(self, e : str):
        a,b = e.split("~")
        m = self.Match(a,b)
        idx = m.idx
        del self.entries[idx]
        self.topology.edges[a].remove(b)
        self.topology.edges[b].remove(a)
        for i,e in enumerate(self.entries):
            e.idx = i
        return idx

    def ExcludeEdgesIfGreaterThan(self,edgevals,tol):
        if len(edgevals) != len(self.entries):
            raise Exception((f"Expected {len(self.entries)} values, "
                             f"but received {len(edgevals)}"))
        valdict = {}
        for i,val in enumerate(edgevals):
            if val > tol:
                valdict[val] = i
                #print(f"Testing {self.entries[i].fwdname} for exclusion...")
        sortedidxs = [valdict[val] for val in sorted(valdict)]
        sortednames = [ self.entries[i].fwdname for i in sortedidxs ]
        exclusions = []
        for name in sortednames:
            print(f"Testing {name} for exclusion:",end=" ")
            if self.CanExcludeEdge(name):
                print(f"excluding")
                exclusions.append( self.ExcludeEdge(name) )
            else:
                print(f"not excluding {name} because it's the only path")
        return exclusions

    
    def ExcludeEdgesIfLessThan(self,edgevals,tol):
        if len(edgevals) != len(self.entries):
            raise Exception((f"Expected {len(self.entries)} values, "
                             f"but received {len(edgevals)}"))
        valdict = {}
        for i,val in enumerate(edgevals):
            if val < tol:
                valdict[val] = i
                #print(f"Testing {self.entries[i].fwdname} for exclusion...")
        sortedidxs = [valdict[val] for val in sorted(valdict)]
        sortedidxs.reverse()
        sortednames = [ self.entries[i].fwdname for i in sortedidxs ]
        exclusions = []
        for name in sortednames:
            print(f"Testing {name} for exclusion:",end=" ")
            if self.CanExcludeEdge(name):
                print(f"excluding")
                exclusions.append( self.ExcludeEdge(name) )
            else:
                print(f"not excluding {name} because it's the only path")
        return exclusions
    

    def GetPathData(self, path : List[str]) -> PathData:
        name = self.topology.PathToStr(path)
        eidxs = []
        esigns = []
        for igap in range(len(path)-1):
            m = self.Match( path[igap], path[igap+1] )
            if m.match:
                eidxs.append( m.idx )
                esigns.append( m.sign )
            else:
                raise Exception(f"No edge connecting {snode} and {tnode}")
        return PathData(name,path,eidxs,esigns,0,0)

    
    def GetPathFreeEnergy(self, path : List[str]) -> Tuple[float,float]:
        import numpy as np
        self.Read()
        data = self.GetPathData(path)
        etot = 0
        errtot = 0
        tidata = { "Linear": [0,0],
                   "Clamped": [0,0],
                   "Natural": [0,0],
                   "USub": [0,0] }
        skipmodes = []
        for idx,sign in zip(data.eidxs,data.esigns):
            e = self.entries[idx].edge
            fe,err = e.GetValueAndError( e.results.prod )
            etot += fe * sign
            errtot += err*err
            ti = e.GetTIValuesAndErrors()
            if ti is not None and tidata is not None:
                for mode in tidata:
                    if mode in ti:
                        tidata[mode][0] += ti[mode][0] * sign
                        tidata[mode][1] += ti[mode][1]**2
                    else:
                        skipmodes.append(mode)
            else:
                tidata = None
        if tidata is not None:
            for mode in skipmodes:
                if mode in tidata:
                    del tidata[mode]
        if tidata is not None:
            for mode in tidata:
                tidata[mode] = (tidata[mode][0],np.sqrt(tidata[mode][1]))
        data.value = etot
        data.error = np.sqrt(errtot)
        data.ti = tidata
        return data

    
    def GetAvgPathFreeEnergy(self, snode : str, tnode : str ) -> Tuple[float,float]:
        import numpy as np
        from . GlobalOptions import GlobalOptions
        gopts = GlobalOptions()
        if gopts.CalcMinPathLengths:
            data = [ self.GetPathFreeEnergy(path)
                     for path in self.topology.FindMinPaths(snode,tnode) ]
        else:
            data = [ self.GetPathFreeEnergy(path)
                     for path in self.topology.FindAllPaths(snode,tnode) ]
        fes = np.array( [e.value for e in data] )
        errs = np.array( [e.error for e in data] )
        mu = np.mean(fes)
        stderr = errs[0]
        N = fes.shape[0]
        if N > 1:
            var = np.var(fes,ddof=1)
            avgvar = np.mean( errs**2 )
            stderr = np.sqrt( (var + avgvar) / N )
        return mu, stderr

    
    def GetAvgMinPathFreeEnergy(self, snode : str, tnode : str ) -> Tuple[float,float]:
        import numpy as np
        data = [ self.GetPathFreeEnergy(path)
                 for path in self.topology.FindMinPaths(snode,tnode) ]
        fes = np.array( [e.value for e in data] )
        errs = np.array( [e.error for e in data] )
        mu = np.mean(fes)
        stderr = errs[0]
        N = fes.shape[0]
        if N > 1:
            var = np.var(fes,ddof=1)
            avgvar = np.mean( errs**2 )
            stderr = np.sqrt( (var + avgvar) ) # / N )
        return mu, stderr

    
    def GetMinPathFreeEnergy(self, snode : str, tnode : str ) -> Tuple[float,float]:
        import numpy as np
        paths = self.topology.FindMinPaths(snode,tnode)
        data = self.GetPathFreeEnergy(paths[0])
        return data.value, data.error

    
    def GetCycleClosures(self) -> List[PathData]:
        
        from . GlobalOptions import GlobalOptions
        gopts = GlobalOptions()
        
        if gopts.CalcMinPathLengths:
            data = [ self.GetPathFreeEnergy(path)
                     for path in self.topology.FindMinCycles() ]
        else:
            data = [ self.GetPathFreeEnergy(path)
                     for path in self.topology.FindAllCycles() ]
        data.sort( key=lambda p: abs(p.value), reverse=True )
        return data


    def GetEdgeProperties( self,
                           node_values : np.ndarray,
                           node_errors : np.ndarray,
                           edge_lagmult : np.ndarray,
                           expt : Optional[Dict[str,float]] = None ) \
                           -> List[Dict[str,float]]:

        ccs = self.GetCycleClosures()
        
        nedge = len(self.entries)
        edge_maxcc = np.zeros( (nedge,) )
        edge_avgcc = np.zeros( (nedge,) )
        edge_ncc = [0]*nedge
    
        for cc in ccs:
            v = abs(cc.value)
            for eidx in cc.eidxs:
                edge_ncc[eidx] += 1
                edge_avgcc[eidx] += v
                edge_maxcc[eidx] = max(edge_maxcc[eidx],v)
            
        for iedge in range(nedge):
            if edge_ncc[iedge] > 0:
                edge_avgcc[iedge] /= edge_ncc[iedge]
        
        props = []
        for iedge,entry in enumerate(self.entries):
            e = self.GetPathFreeEnergy(self.topology.StrToPath(entry.fwdname))

            prop = {}
            prop["Name"] = entry.fwdname
            if e.ti is not None:
                prop["TI"]   = e.ti["Linear"][0]
                prop["TI3n"] = e.ti["Natural"][0]
                prop["TI3c"] = e.ti["Clamped"][0]
            else:
                prop["TI"]   = None
                prop["TI3n"] = None
                prop["TI3c"] = None

            prop["UFE"] = e.value
            prop["dUFE"] = e.error
            inode = self.topology.nodes.index( e.path[0] )
            jnode = self.topology.nodes.index( e.path[1] )
            prop["Expt"] = None
            if expt is not None:
                if e.path[0] in expt and e.path[1] in expt:
                    prop["Expt"] = expt[e.path[1]] - expt[e.path[0]]
            prop["CFE"]  = node_values[jnode] - node_values[inode]
            prop["dCFE"] = np.sqrt( node_errors[jnode]**2 + node_errors[inode]**2 )
            prop["Shift"] = abs(prop["CFE"]-prop["UFE"])
            prop["LMI"]  = abs(edge_lagmult[iedge])
            prop["OFC2"] = entry.edge.results.conobj.c2
            prop["AvgCC"] = edge_avgcc[iedge]
            prop["MaxCC"] = edge_maxcc[iedge]
            msgs = entry.edge.GetErrorMsgs()
            prop["ErrMsgs"]  = sum( [1 for msg in msgs if msg.iserr] )
            prop["Outliers"] = sum( [1 for msg in msgs if msg.kind == 'outlier'] )
            props.append(prop)
        return props
    

    def GetConstraints(self,
                       nfree : int,
                       lagedge : Optional[str],
                       lagval : Optional[float],
                       xedges : Optional[List[str]],
                       xvals : Optional[float] ) \
                       -> Tuple[np.ndarray,np.ndarray]:
        
        from collections import OrderedDict
        nodes = self.topology.nodes
        cons = OrderedDict()
        if lagedge is not None and lagval is not None:
            a,b = lagedge.split("~")
            ia = nodes.index(a)
            ib = nodes.index(b)
            cons[(ia,ib)] = lagval
        if xedges is not None and xvals is not None:
            for e,v in zip(xedges,xvals):
                a,b = e.split("~")
                if a in nodes:
                    ia = nodes.index(a)
                else:
                    raise Exception((f"Constraint {e} involves node"
                                     f" {a} which is not in the graph"))
                if b in nodes:
                    ib = nodes.index(b)
                else:
                    raise Exception((f"Constraint {e} involves node"
                                     f" {b} which is not in the graph"))
                if (ib,ia) in cons:
                    cons[(ib,ia)] = -v
                else:
                    cons[(ia,ib)] = v
        ncon = len(cons)
        Cmat = np.zeros( (ncon,nfree) )
        Cvals = np.zeros( (ncon,) )
        for icon,e in enumerate(cons):
            Cvals[icon] = cons[e]
            if e[0] > 0:
                Cmat[icon,e[0]-1] = -1.
            if e[1] > 0:
                Cmat[icon,e[1]-1] = 1.
        return Cmat,Cvals
    
    

    def NonlinearSolve(self,nboot=100,dolagmult=True,guess=None,
                       verbose=False,conedges=None,convals=None) \
                       -> Tuple[List[float],List[float],List[float]]:
        import numpy as np
        #from numpy.random import normal as rnormal
        from scipy.optimize import minimize
        from scipy.optimize import LinearConstraint
        from copy import deepcopy
        from . OptUtils import GraphObjective
        from numpy.random import default_rng

        #
        # A list of node names
        #
        nodes = self.topology.nodes

        #
        # The number of nodes, edges, and free parameters
        #
        nnode = len(nodes)
        nedge = len(self.entries)
        nfree = nnode - 1

        #
        # Initial guess for the nfree node free energies are the
        # minimum-path free energies connecting each node to the
        # reference (first) node
        #
        if guess is not None:
            pguess = guess[1:] - guess[0]
        else:
            pguess = np.array([ self.GetMinPathFreeEnergy( nodes[0], node )[0]
                                for node in nodes[1:] ])

        #
        # Treat each edge as a trivial "path", from which we can
        # easily lookup the edge free energy and identify the
        # node indexes
        #
        edgedata = [ self.GetPathFreeEnergy(self.topology.StrToPath(e.fwdname))
                     for e in self.entries ]

        edge_values = [e.value for e in edgedata]
        edge_errors = [e.error for e in edgedata]
        edge_names =  [e.name for e in edgedata]
        
        #
        # node_idxs is a list (len=nedge). Each element of the list
        # is a list of 2 numbers: the edge's node indexes
        #
        # I then feed that to numpy to turn it into a matrix.
        # The matrix is transposed so the fast index loops over the edges
        # and slow index loops over the indexes of the two nodes
        #
        node_idxs = np.array([ [nodes.index( nname ) for nname in e.path]
                               for e in edgedata ], dtype=int).T

        #
        # A list of CenteredCubic objects
        #
        polynomials = [ deepcopy(self.entries[e.eidxs[0]].edge.results.conobj)
                        for e in edgedata ]

        #
        # Instead of passing the polynomial objects to the
        # objective function, I'm going to store a list of
        # raw polynomial parameters to optimize the evaluation.
        # pcenter is the "center" of the polynomial
        # pc2 and pc3 are the coefficients of the quadratic
        # and cubic monomials
        #
        pcenter = np.array([ p.q0 for p in polynomials ])
        pc2 = np.array([ p.c2 for p in polynomials ])
        pc3 = np.array([ p.c3 for p in polynomials ])


        
        # =========================================================
        # Optimize the node free energies, assuming the first node
        # has a free energy of 0.0
        # =========================================================

        Cmat,Cvals = self.GetConstraints(nfree,None,None,conedges,convals)
        constraints=None
        method='L-BFGS-B'
        tol=1.e-12
        options={ 'gtol': 1.e-24, 'maxiter': 5000 }
        if Cvals.shape[0] > 0:
            constraints = LinearConstraint(Cmat,Cvals,Cvals)
            method = 'trust-constr'
            
        res = minimize( GraphObjective,
                        pguess,
                        method=method,
                        args=(node_idxs,pcenter,pc2,pc3),
                        jac=True,
                        tol=tol,
                        constraints=constraints,
                        options=options )
            
        if verbose:
            print(res)

        
        #
        # Use the optimized result as the initial guess for all
        # future optimizations
        #
        pguess = np.array( [x for x in res.x] )
        
        #
        # The node free energies (the first node is the 0.0)
        #
        node_values = np.array( [ 0.0 ] + [x for x in res.x] )
        node_errors = np.zeros( node_values.shape )
        edge_lagmult = np.zeros( (nedge,) )


        if nboot > 0:
            # =========================================================
            # Bootstrap error estimate of the node free energies
            # =========================================================

            #
            # The "center" of each polynomial is the expected edge
            # free energy, so we will bootstrap by shifting the
            # center so it obeys a normal distribution whose
            # standard deviation is the standard error of the edge
            # free energy.
            #
            # poly_centers is the list of randomly-drawn centers
            # drawn from the normal distribution for each edge
            #
            # poly_centers = np.zeros( (nedge,nboot) )
            # for iedge in range(nedge):
            #     poly_centers[iedge,:] = rnormal(edge_values[iedge],
            #                                     edge_errors[iedge],
            #                                     size=nboot)

            #
            # We will compute the node free energies nboot times
            # and store the results in node_bootvalues
            #
            node_bootvalues = []
            rng = default_rng()

            for iboot in range(nboot):
                poly_centers = rng.normal( edge_values, edge_errors )
                bootres = minimize\
                    ( GraphObjective,
                      pguess,
                      method=method,
                      args=(node_idxs,poly_centers,pc2,pc3),
                      jac=True,
                      tol=tol,
                      constraints=constraints,
                      options=options )
                # Before storing the node free energies, shift them by
                # a constant to minimize the variance with the original
                # set of (nonbootstrap) values
                values = np.array( [ 0. ] + [x for x in bootres.x] )
                values += np.mean( node_values-values )
                node_bootvalues.append(values)
            #
            # The standard error of the node_values are the standard
            # deviation of the bootstrap trials. Store the standard
            # error in node_errors
            #
            node_bootvalues = np.array(node_bootvalues)
            node_means = np.mean(node_bootvalues,axis=0)
            node_errors = np.std(node_bootvalues,axis=0)
            

        
        # =========================================================
        # Calculate a Lagrange multiplier index for each edge.
        # For each edge, reoptimize the node free energies under
        # a single constraint: the node free energies must
        # reproduce the isolated edge free energy
        # =========================================================

        if dolagmult:
            for iedge in range(nedge):
                Cmat,Cvals = self.GetConstraints\
                    (nfree, edge_names[iedge], edge_values[iedge],
                     conedges, convals)
                constraints = LinearConstraint(Cmat,Cvals,Cvals)
            
                conres = minimize( GraphObjective,
                                   pguess,
                                   method='trust-constr',
                                   args=(node_idxs,pcenter,pc2,pc3),
                                   jac=True,
                                   tol=tol,
                                   constraints=constraints,
                                   options=options )

                edge_lagmult[iedge] = -conres.v[0][0]


                # if True:
                #     # Test finite difference
                #     constraint = GetEdgeConstraint(nfree,
                #                                    node_idxs[:,iedge],
                #                                    edge_values[iedge]+0.5)
            
                #     conres_hi = minimize( GraphObjective,
                #                           pguess,
                #                           method='trust-constr',
                #                           args=(node_idxs,pcenter,pc2,pc3),
                #                           jac=True,
                #                           constraints = constraint,
                #                           options = { 'gtol': 1.e-18,
                #                                       'maxiter': 5000 } )

                #     constraint = GetEdgeConstraint(nfree,
                #                                    node_idxs[:,iedge],
                #                                    edge_values[iedge]-0.5)
                
                #     conres_lo = minimize( GraphObjective,
                #                           pguess,
                #                           method='trust-constr',
                #                           args=(node_idxs,pcenter,pc2,pc3),
                #                           jac=True,
                #                           constraints = constraint,
                #                           options = { 'gtol': 1.e-18,
                #                                       'maxiter': 5000 } )
                    
                #     app = (conres_hi.fun - conres_lo.fun)
                #     #edge_lagmult[iedge] = app
                
                #     ana = edge_lagmult[iedge]
                #     print("%3i %14.5e %14.5e %14.5e"%(iedge,ana,app,ana-app))


        return node_values,node_errors,edge_lagmult

    
    def OldLinearSolve(self,nboot=200) -> Tuple[List[float],List[float],List[float]]:
        import numpy as np
        from copy import deepcopy
        #from numpy.random import normal as rnormal
        from numpy.random import default_rng
        

        #
        # A list of node names
        #
        nodes = self.topology.nodes

        #
        # The number of nodes, edges, and free parameters
        #
        nnode = len(nodes)
        nedge = len(self.entries)

        #
        # Treat each edge as a trivial "path", from which we can
        # easily lookup the edge free energy and identify the
        # node indexes
        #
        edgedata = [ self.GetPathFreeEnergy(self.topology.StrToPath(e.fwdname))
                     for e in self.entries ]

        edge_values = np.array([e.value for e in edgedata])
        edge_errors = np.array([e.error for e in edgedata])
        
        #
        # node_idxs is a list (len=nedge). Each element of the list
        # is a list of 2 numbers: the edge's node indexes
        #
        # I then feed that to numpy to turn it into a matrix.
        # The matrix is transposed so the fast index loops over the edges
        # and slow index loops over the indexes of the two nodes
        #
        node_idxs = np.array([ [nodes.index( nname ) for nname in e.path]
                               for e in edgedata ], dtype=int).T

        #
        # A list of CenteredCubic objects
        #
        polynomials = [ deepcopy(self.entries[e.eidxs[0]].edge.results.conobj)
                        for e in edgedata ]

        #
        # Instead of passing the polynomial objects to the
        # objective function, I'm going to store a list of
        # raw polynomial parameters to optimize the evaluation.
        # pcenter is the "center" of the polynomial
        # pc2 and pc3 are the coefficients of the quadratic
        # and cubic monomials
        #
        pcenter = np.array([ p.q0 for p in polynomials ])
        pc2 = np.array([ p.c2 for p in polynomials ])
        pc3 = np.array([ p.c3 for p in polynomials ])

        A = np.diag(pc2)
        Z = np.zeros( (nedge,nnode-1) )
        for iedge in range(nedge):
            if node_idxs[0,iedge] > 0:
                Z[iedge,node_idxs[0,iedge]-1] = -1
            if node_idxs[1,iedge] > 0:
                Z[iedge,node_idxs[1,iedge]-1] = 1
        q = np.array(pcenter,copy=True)

        ZA = np.dot( Z.T, A )
        ZAZ = np.dot( ZA, Z )
        ZAZi = np.linalg.inv(ZAZ)

        dcdq = np.dot( ZAZi, ZA )
        c = np.dot( dcdq, q )

        node_values = np.concatenate( ([0],c) )
        
        #dc = np.sqrt( np.dot( dcdq**2, edge_errors**2 ) )

        
        
        rng = default_rng()

        if nboot > 0:
            node_bootvalues = []
            for iboot in range(nboot):
                poly_centers = rng.normal( edge_values, edge_errors )
                values=np.concatenate(([0.],
                            np.dot(dcdq,rng.normal(edge_values,edge_errors))))
                values += np.mean( node_values-values )
                node_bootvalues.append(values)
            node_bootvalues = np.array(node_bootvalues)
            node_means = np.mean(node_bootvalues,axis=0)
            node_errors = np.std(node_bootvalues,axis=0)
        else:
            node_errors = np.zeros( node_values.shape )
            
        edge_lagmult = np.zeros( (nedge,) )
        for iedge in range(nedge):
            d = Z[iedge,:]
            g = edge_values[iedge]
            edge_lagmult[iedge] = 2*(g-np.dot(d,c))/np.dot(d,np.dot(ZAZi,d))
            
        return node_values,node_errors,edge_lagmult

    
    def LinearSolve(self,nboot=200,conedges=None,convals=None) \
        -> Tuple[List[float],List[float],List[float]]:
        import numpy as np
        from copy import deepcopy
        #from numpy.random import normal as rnormal
        from numpy.random import default_rng
        

        #
        # A list of node names
        #
        nodes = self.topology.nodes

        #
        # The number of nodes, edges, and free parameters
        #
        nnode = len(nodes)
        nedge = len(self.entries)
        nfree = nnode-1

        #
        # Treat each edge as a trivial "path", from which we can
        # easily lookup the edge free energy and identify the
        # node indexes
        #
        edgedata = [ self.GetPathFreeEnergy(self.topology.StrToPath(e.fwdname))
                     for e in self.entries ]

        edge_values = np.array([e.value for e in edgedata])
        edge_errors = np.array([e.error for e in edgedata])
        edge_names  = np.array([e.name for e in edgedata])

        #
        # node_idxs is a list (len=nedge). Each element of the list
        # is a list of 2 numbers: the edge's node indexes
        #
        # I then feed that to numpy to turn it into a matrix.
        # The matrix is transposed so the fast index loops over the edges
        # and slow index loops over the indexes of the two nodes
        #
        node_idxs = np.array([ [nodes.index( nname ) for nname in e.path]
                               for e in edgedata ], dtype=int).T

        #
        # A list of CenteredCubic objects
        #
        polynomials = [ deepcopy(self.entries[e.eidxs[0]].edge.results.conobj)
                        for e in edgedata ]

        #
        # Instead of passing the polynomial objects to the
        # objective function, I'm going to store a list of
        # raw polynomial parameters to optimize the evaluation.
        # pcenter is the "center" of the polynomial
        # pc2 and pc3 are the coefficients of the quadratic
        # and cubic monomials
        #
        pcenter = np.array([ p.q0 for p in polynomials ])
        pc2 = np.array([ p.c2 for p in polynomials ])
        pc3 = np.array([ p.c3 for p in polynomials ])



        node_values = np.zeros( (nnode,) )
        node_errors = np.zeros( (nnode,) )
        edge_lagmult = np.zeros( (nedge,) )

        
        K = np.diag(pc2)
        X = np.zeros( (nedge,nnode-1) )
        for iedge in range(nedge):
            if node_idxs[0,iedge] > 0:
                X[iedge,node_idxs[0,iedge]-1] = -1
            if node_idxs[1,iedge] > 0:
                X[iedge,node_idxs[1,iedge]-1] = 1
        e = np.array(pcenter,copy=True)

        XK = np.dot( X.T, K )
        XKX = np.dot( XK, X )
        XKXi = np.linalg.inv(XKX)
        dnde = np.dot( XKXi, XK )
        n_uncon = np.dot( dnde, e )
        
        rng = default_rng()

        D,G = self.GetConstraints(nfree, None, None, conedges, convals)
        ncon = G.shape[0]

        if ncon == 0:
            node_values[1:] = n_uncon
            
            if nboot > 0:
                node_bootvalues = []
                for iboot in range(nboot):
                    poly_centers = rng.normal( edge_values, edge_errors )
                    values=np.concatenate(([0.],
                                np.dot(dnde,rng.normal(edge_values,
                                                       edge_errors))))
                    values += np.mean( node_values-values )
                    node_bootvalues.append(values)
                node_bootvalues = np.array(node_bootvalues)
                node_means = np.mean(node_bootvalues,axis=0)
                node_errors = np.std(node_bootvalues,axis=0)
            
            for iedge in range(nedge):
                d = X[iedge,:]
                g = edge_values[iedge]
                den = np.dot(d,np.dot(XKXi,d))
                edge_lagmult[iedge] = 2*(g-np.dot(d,n_uncon))/den

        else:
            
            XKXiD = np.dot(XKXi,D.T)
            DDi = np.linalg.inv( np.dot(D,XKXiD) )
            A =  2 * np.dot(DDi,G)
            B = -2 * np.dot(DDi,np.dot(D,dnde))
            C =  0.5 * np.dot(XKXiD,A)
            D =  0.5 * np.dot(XKXiD,B) + dnde
            #L = 2 * np.dot(DDi,G-np.dot(D,n_uncon))
            #L = A+np.dot(B,e)
            #node_values[1:] = 0.5*np.dot(XKXiD,L) + n_uncon
            node_values[1:] = C + np.dot(D,e)
            
            if nboot > 0:
                node_bootvalues = []
                for iboot in range(nboot):
                    poly_centers = rng.normal( edge_values, edge_errors )
                    values=np.concatenate(([0.],
                            C + np.dot(D,rng.normal(edge_values,
                                                    edge_errors))))
                    values += np.mean( node_values-values )
                    node_bootvalues.append(values)
                node_bootvalues = np.array(node_bootvalues)
                node_means = np.mean(node_bootvalues,axis=0)
                node_errors = np.std(node_bootvalues,axis=0)


            for iedge in range(nedge):
                D,G = self.GetConstraints\
                    (nfree, edge_names[iedge], edge_values[iedge],
                     conedges, convals)
                DDi = np.linalg.inv( np.dot(D,np.dot(XKXi,D.T)) )
                L = 2 * np.dot(DDi,G-np.dot(D,n_uncon))
                edge_lagmult[iedge] = L[0]
            
        return node_values,node_errors,edge_lagmult

    
    def MixedSolve(self,
                   nboot=200,
                   verbose=False,
                   conedges=None,
                   convals=None) \
                   -> Tuple[List[float],List[float],List[float]]:
        lin = self.LinearSolve(nboot,conedges,convals)
        opt = self.NonlinearSolve\
            (nboot=0, dolagmult=False, guess=lin[0],
             verbose=verbose, conedges=conedges, convals=convals)
        return opt[0],lin[1],lin[2]
