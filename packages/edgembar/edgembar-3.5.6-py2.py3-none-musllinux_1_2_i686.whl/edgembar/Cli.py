#!/usr/bin/env python3
import typing
from . Edge import Edge

def ProcessEdgeCli( edge: Edge ) -> None:
    
    import argparse
    import sys
    from pathlib import Path
    from . HtmlUtils import WriteEdgeHtmlFile
    
    parser = argparse.ArgumentParser\
        (formatter_class=argparse.RawDescriptionHelpFormatter,
         description="""Output analysis of the edge in the desired format""")

    parser.add_argument\
        ("--skip-outliers",
         help="Remove outlier trials before processing the other options",
         action='store_true',
         required=False)
    
    parser.add_argument\
        ("--html",
         help="Write HTML file with the same name as the python script,"+
         " but with a .html suffix",
         action='store_true',
         required=False)
    
    parser.add_argument\
        ("--html-du-print-thresh",
         help="If writing an HTML with --html, then include time series"+
         " analysis of the forward and reverse Delta U values used to "+
         "perform automatic equilibration detection. Only perform the "+
         "analysis if the equilibration fraction is larger than the "+
         "specified threshold. If the threshold is 1, then no analysis "+
         "is printed. If it is 0, then all simulations are analyzed, but "+
         "this would yield a massive HTML file that may take a long time "+
         "to load. The default (-1) will print every 'unconverged' simulation.",
         type=float,
         default=-1,
         required=False)
    
    parser.add_argument\
        ("--xml",
         help="Write XML to stdout",
         action='store_true',
         required=False)

    parser.add_argument\
        ("--brief",
         help="Write a brief summary of the transformation energies",
         action='store_true',
         required=False)

    
    parser.add_argument\
        ("--imgdir",
         help="A directory name (default: ./imgdir). When writing an HTML edge report, the script will check to see if files named lig1~lig2_lig1.png and lig1~lig2_lig2.png files exist within imgdir. If so, then the images are included in the HTML page.",
         type=str,
         default="imgdir",
         required=False)


    args = parser.parse_args()

    if args.skip_outliers:
        edge.RemoveOutliers()
    
    if args.xml:
        print(edge)
    elif args.brief:
        sys.stdout.write("%20s %10s %10s %10s %9s %8s\n"\
                         %("Edge","Env","Stage",
                           "Trial","Energy","Error"))
        
        v,e = edge.GetValueAndError(edge.results.prod)
        sys.stdout.write("%20s %10s %10s %10s %9.3f %8.3f\n"\
                         %(edge.name,"","","",v,e))
        for env in edge.GetEnvs():
            v,e = env.GetValueAndError(edge.results.prod)
            sys.stdout.write("%20s %10s %10s %10s %9.3f %8.3f\n"\
                             %(edge.name,env.name,"","",v,e))
            for stage in env.stages:
                v,e = stage.GetValueAndError(edge.results.prod)
                sys.stdout.write("%20s %10s %10s %10s %9.3f %8.3f\n"\
                                 %(edge.name,env.name,stage.name,"",v,e))
                for trial in stage.trials:
                    v,e = trial.GetValueAndError(edge.results.prod)
                    sys.stdout.write("%20s %10s %10s %10s %9.3f %8.3f\n"\
                                     %(edge.name,env.name,stage.name,
                                       trial.name,v,e))


    else:
        fname = Path(sys.argv[0]).with_suffix(".html")
        options = {}
        options["du_print_thresh"] = args.html_du_print_thresh
        options["imgdir"] = args.imgdir
        WriteEdgeHtmlFile(edge,fname,options=options)
