#/usr/bin/env python3

"""
The edgembar python module provides a base class that can be
used to write input files for the graphmbar C++ program and
analyze the output of that program.

Brief summary of classes
------------------------
Trial
    A set of states defining a transformation

Stage
    A collection of trials used to calculate a transformation
    The free energy of a stage is trial-averaged

Env
    A collection of stages within an environment
    The free energy is a sum of stages

Edge
    The free energy in complexed and solvated environments
    The free energy is a difference between the environments

Graph
    Graph analysis

Results
    Stores the free energy values and bootstrap errors from
    different forms of analysis. This includes: analysis of
    the production sampling, forward and reverse time series
    analysis of the correlated samples, and objective function
    dependence on the free energy constraint value

SimProperty
    Stores properties of a simulation, including the stride
    between statistically independent samples, the overlap
    with other simulations, and reweighting entropy.

Brief summary of functions
--------------------------
DiscoverEdges(str) -> list
    Creates a list of Edge objects by reading the filesystem.
    The user must supply a format string that looks something like:
    DiscoverEdges("dats/{trial}/free_energy/{edge}_ambest/{env}/{stage}/efep_{traj}_{ene}.dat")
    That is, the string must contain the format placeholders: 
    {trial}, {edge}, {env}, {stage}, {traj}, and {ene}
    
ImportEdge(str) -> Edge
    Opens and imports a python file, given its filename, and
    returns the Edge object. The file is assumed to define a
    variable named "edge"

"""


from . Trial   import Trial
from . Stage   import Stage
from . Env     import Env
#from . Edge   import Trial
#from . Edge   import Stage
#from . Edge    import Env
from . Edge    import Edge
from . Graph   import Graph
from . Results import Results
from . Results import TimeSeriesData
from . Results import ConstraintData
from . Results import SimProperty
from . DiscoverEdges import DiscoverEdges
from . ImportEdge import ImportEdge
from . Cli import ProcessEdgeCli
from . Names import GetNameFromObj
from . HtmlUtils import WriteGraphHtmlFile
from . import Splines

__all__ = [ 'Splines',
            'Trial',
            'Stage',
            'Env',
            'Edge',
            'Graph',
            'Results',
            'TimeSeriesData',
            'ConstraintData',
            'SimProperty',
            'DiscoverEdges',
            'ImportEdge',
            'ProcessEdgeCli',
            'GetNameFromObj',
            'WriteGraphHtmlFile']

