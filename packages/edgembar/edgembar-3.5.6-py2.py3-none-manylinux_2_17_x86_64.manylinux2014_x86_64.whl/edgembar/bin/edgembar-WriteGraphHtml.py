#!/usr/bin/env python3

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    
import edgembar
import argparse
import glob
from pathlib import Path
from edgembar.GlobalOptions import GlobalOptions

parser = argparse.ArgumentParser\
    (formatter_class=argparse.RawDescriptionHelpFormatter,
     description="""Output analysis of the edge in the desired format""")
    
parser.add_argument\
    ("-o","--out",
     help="Output HTML filename",
     required=True)
    
parser.add_argument\
    ("-s","--solver",
     default='linear',
     const='linear',
     nargs='?',
     choices=('linear','mixed','nonlinear'),
     help=("Graph solution: either linear, mixed, "
           "or nonlinear (default: linear)") )

parser.add_argument\
    ("--exclude",
     help="Exclude the specified edge",
     nargs='+',
     type=str,
     action='append',
     required=False)
    
parser.add_argument\
    ("--refnode",
     help="Name of node to select as the reference",
     type=str,
     required=False)



parser.add_argument\
    ("-x","--expt",
     help=("Filename containing the node names and "
           "experimental/reference free energies"),
     type=str,
     required=False)


parser.add_argument\
    ("-c","--constrain",
     help=("Constrain the specified edge. The constraint "
           "value is the difference between the experimental "
           "node free energies listed in the --expt file."),
     nargs='+',
     type=str,
     action='append',
     required=False)
    
parser.add_argument\
    ("--skip-outliers",
     help=("Skip all trials deemed to be 'outliers' when computing the"
           " unconstrained free energies. This does not effect the"
           " solution for the constrained free energies because the"
           " edge objective function is precomputed by the edgembar"
           " C++ program. To obtain the constrained solution, you"
           " need to re-run the edge without the offending trials."),
     action='store_true',
     required=False)

parser.add_argument\
    ("--shift-xgt-tol",
     help=("Exclude all edges whose constrained linear solution"
           " differs from the unconstrained edge free energy"
           " by more than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
    
parser.add_argument\
    ("--shift-xlt-tol",
     help=("Exclude all edges whose constrained linear solution"
           " differs from the unconstrained edge free energy"
           " by less than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
    
parser.add_argument\
    ("--avgcc-xgt-tol",
     help=("Exclude all edges whose average cycle closure error"
           " is larger than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
   
parser.add_argument\
    ("--avgcc-xlt-tol",
     help=("Exclude all edges whose average cycle closure error"
           " is smaller than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
   
parser.add_argument\
    ("--maxcc-xgt-tol",
     help=("Exclude all edges whose maximum cycle closure error"
           " is larger than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
   
parser.add_argument\
    ("--maxcc-xlt-tol",
     help=("Exclude all edges whose maximum cycle closure error"
           " is smaller than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
   
parser.add_argument\
    ("--lmi-xgt-tol",
     help=("Exclude all edges whose Lagrange multiplier index"
           " is larger than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)

parser.add_argument\
    ("--lmi-xlt-tol",
     help=("Exclude all edges whose Lagrange multiplier index"
           " is smaller than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)

parser.add_argument\
    ("--dufe-xgt-tol",
     help=("Exclude all edges whose unconstrained uncertainty"
           " is larger than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
   
parser.add_argument\
    ("--dufe-xlt-tol",
     help=("Exclude all edges whose unconstrained uncertainty"
           " is smaller than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=float,
     required=False)
   
parser.add_argument\
    ("--errmsgs-xgt-tol",
     help=("Exclude all edges that produce more error messages"
           " than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=int,
     required=False)

parser.add_argument\
    ("--errmsgs-xlt-tol",
     help=("Exclude all edges that produce fewer error messages"
           " than the specified tolerance. An edge is only"
           " excluded if it doesn't split the graph."),
     type=int,
     required=False)

    
parser.add_argument\
    ("--all-cycles",
     help=("Include all cycles rather than minimum-length cycles."),
     action='store_true')


parser.add_argument\
    ( 'efiles',
      metavar='edge.py',
      type=str,
      nargs='+',
      help=("List of edge (python) files to include in the graph. "
            "The filenames should be named: A~B.py, where A and B "
            "are node names."))

version = get_package_version("edgembar")

    
parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format\
                    (version=version))


args = parser.parse_args()
regular_list =  [ glob.glob(f) for f in args.efiles ]
efiles = list(set([ item for sublist in regular_list for item in sublist ]))

exclusions = None
if args.exclude is not None:
    exclusions = list(set([ Path(item).stem for sublist in args.exclude
                            for item in sublist ]))


GlobalOptions.CalcMinPathLengths = True
if args.all_cycles:
    GlobalOptions.CalcMinPathLengths = False


    
g = edgembar.Graph(efiles,
                   exclude=exclusions,
                   refnode=args.refnode)
g.Read()

if args.refnode is not None:
    refnode = args.refnode
else:
    refnode = g.topology.nodes[0]

if args.skip_outliers:
    for entry in g.entries:
        entry.edge.RemoveOutliers()
    

        
convals = []
conedges = []
expt = None
if args.expt is not None:
    
    expt = {}
    f = Path(args.expt)
    if not f.is_file():
        raise Exception(f"File not found: {f}")
    fh = open(f,"r")
    for line in fh:
        cs = line.strip().split()
        if len(cs) > 1:
            if cs[0] in g.topology.nodes:
                expt[cs[0]] = float(cs[1])
                
    if refnode not in expt:
        raise Exception((f"Reference node {refnode} does not have an "
                         f"experimental value within {args.expt}"))
    refene = expt[refnode]
    for node in expt:
        expt[node] -= refene
    
    
    if args.constrain is not None:
        conedges = list(set([ Path(item).stem for sublist in args.constrain
                              for item in sublist ]))
        for edge in conedges:
            nodes = edge.split("~")
            for node in nodes:
                if node not in expt:
                    raise Exception((f"Cannot constrain {edge} because "
                                     f"node {node} was not in {args.expt}"))
            if nodes[-1] != nodes[0]:
                convals.append( expt[nodes[-1]] - expt[nodes[0]] )
elif args.constrain is not None:
    raise Exception("Cannot apply constraints because --expt was not used")



props = None
if args.shift_xgt_tol is not None or args.avgcc_xgt_tol is not None or \
   args.lmi_xgt_tol is not None or args.errmsgs_xgt_tol is not None or \
   args.dufe_xgt_tol is not None or args.maxcc_xgt_tol is not None or\
   args.shift_xlt_tol is not None or args.avgcc_xlt_tol is not None or \
   args.lmi_xlt_tol is not None or args.errmsgs_xlt_tol is not None or \
   args.dufe_xlt_tol is not None or args.maxcc_xlt_tol is not None:
    solution = g.LinearSolve(conedges=conedges,convals=convals)
    props = g.GetEdgeProperties(*solution,expt=expt)

#
# xgt tolerances
#

if args.dufe_xgt_tol is not None:
    print("GT exclusions for dUFE")
    dufe = [ row["dUFE"] for row in props ]
    delidxs = g.ExcludeEdgesIfGreaterThan(dufe,args.dufe_xgt_tol)
    for idx in delidxs:
        del props[idx]
 
if args.shift_xgt_tol is not None:
    print("GT exclusions for Shift")
    shifts = [ row["Shift"] for row in props ]
    delidxs = g.ExcludeEdgesIfGreaterThan(shifts,args.shift_xgt_tol)
    for idx in delidxs:
        del props[idx]
 
if args.avgcc_xgt_tol is not None:
    print("GT exclusions for AvgCC")
    avgcc = [ row["AvgCC"] for row in props ]
    delidxs = g.ExcludeEdgesIfGreaterThan(avgcc,args.avgcc_xgt_tol)
    for idx in delidxs:
        del props[idx]

if args.maxcc_xgt_tol is not None:
    print("GT exclusions for MaxCC")
    maxcc = [ row["MaxCC"] for row in props ]
    delidxs = g.ExcludeEdgesIfGreaterThan(maxcc,args.maxcc_xgt_tol)
    for idx in delidxs:
        del props[idx]

if args.lmi_xgt_tol is not None:
    print("GT exclusions for LMI")
    lmi = [ row["LMI"] for row in props ]
    delidxs = g.ExcludeEdgesIfGreaterThan(lmi,args.lmi_xgt_tol)
    for idx in delidxs:
        del props[idx]

if args.errmsgs_xgt_tol is not None:
    print("GT exclusions for ErrMsgs")
    errmsgs = [ row["ErrMsgs"] for row in props ]
    delidxs = g.ExcludeEdgesIfGreaterThan(errmsgs,args.errmsgs_xgt_tol)
    for idx in delidxs:
        del props[idx]


#
# xlt tolerances
#

if args.dufe_xlt_tol is not None:
    print("LT exclusions for dUFE")
    dufe = [ row["dUFE"] for row in props ]
    delidxs = g.ExcludeEdgesIfLessThan(dufe,args.dufe_xlt_tol)
    for idx in delidxs:
        del props[idx]
 
if args.shift_xlt_tol is not None:
    print("LT exclusions for Shift")
    shifts = [ row["Shift"] for row in props ]
    delidxs = g.ExcludeEdgesIfLessThan(shifts,args.shift_xlt_tol)
    for idx in delidxs:
        del props[idx]
 
if args.avgcc_xlt_tol is not None:
    print("LT exclusions for AvgCC")
    avgcc = [ row["AvgCC"] for row in props ]
    delidxs = g.ExcludeEdgesIfLessThan(avgcc,args.avgcc_xlt_tol)
    for idx in delidxs:
        del props[idx]

if args.maxcc_xlt_tol is not None:
    print("LT exclusions for MaxCC")
    maxcc = [ row["MaxCC"] for row in props ]
    delidxs = g.ExcludeEdgesIfLessThan(maxcc,args.maxcc_xgt_tol)
    for idx in delidxs:
        del props[idx]

if args.lmi_xlt_tol is not None:
    print("LT exclusions for LMI")
    lmi = [ row["LMI"] for row in props ]
    delidxs = g.ExcludeEdgesIfLessThan(lmi,args.lmi_xlt_tol)
    for idx in delidxs:
        del props[idx]

if args.errmsgs_xlt_tol is not None:
    print("LT exclusions for ErrMsgs")
    errmsgs = [ row["ErrMsgs"] for row in props ]
    delidxs = g.ExcludeEdgesIfLessThan(errmsgs,args.errmsgs_xlt_tol)
    for idx in delidxs:
        del props[idx]

               
     
     
if args.solver == 'linear':
    solution = g.LinearSolve(conedges=conedges,convals=convals)
elif args.solver == 'mixed':
    solution == g.MixedSolve(conedges=conedges,convals=convals)
else:
    solution == g.NonlinearSolve(conedges=conedges,convals=convals)

edgembar.WriteGraphHtmlFile(g,args.out,*solution,expt=expt)


