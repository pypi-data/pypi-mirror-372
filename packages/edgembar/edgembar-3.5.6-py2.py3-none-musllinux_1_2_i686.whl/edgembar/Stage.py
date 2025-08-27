#!/usr/bin/env python3
from typing import List
from typing import Tuple
from typing import Union
import xml.etree.ElementTree as ET
from . Trial import Trial
import numpy as np

class Stage(object):
    
    def __init__( self,
                  name: str,
                  trials: List[Trial]):
        
        self.name = name
        self.trials = trials        
        self.env = None
        self.edge = None

        
    @classmethod
    def from_xmlnode( cls, node: ET.Element ):
        
        from . Trial import Trial
        name = node.get("name")
        trials = [ Trial.from_xmlnode(x)
                   for x in node.findall("trial") ]
        return cls(name,trials)

    def reverse(self):
        for trial in self.trials:
            trial.reverse()
    
    def GetXml( self, node: ET.Element ) -> ET.Element:
        
        import xml.etree.ElementTree as ET
        stage = ET.SubElement(node,"stage")
        stage.attrib["name"] = self.name
        for trial in self.trials:
            trial.GetXml(stage)
        return stage


    def SetShift( self, s: float ) -> None:
        for trial in self.trials:
            trial.SetShift( s )
    
    def SetLinkedList( self,
                       edge,
                       env ) -> None:
        
        self.edge=edge
        self.env=env
        for i in range(len(self.trials)):
            self.trials[i].SetLinkedList(edge,env,self)
    

    def GetValueAndError( self, data: np.ndarray ) -> Tuple[float,float]:
        import numpy as np
        
        vs=[]
        es=[]
        for t in self.trials:
            tv,te = t.GetValueAndError(data)
            vs.append( tv )
            es.append( te**2 )
        mu = np.mean(vs)
        tvar = 0
        if len(self.trials) > 1:
            tvar = np.var(vs,ddof=1)
        totvar = tvar + np.mean( es )
        err = np.sqrt( totvar / len(self.trials) )
        return mu,err
    
    def RemoveOutliers(self):
        bad_trials = []
        for itrial,trial in enumerate(self.trials):
            is_outlier = False
            for err in trial.GetErrorMsgs():
                if err.kind == "outlier":
                    is_outlier = True
                    break
            if is_outlier:
                bad_trials.append(itrial)
        bad_trials.sort()
        bad_trials.reverse()
        for itrial in bad_trials:
            del self.trials[itrial]

        
    def GetTIValuesAndErrors(self) -> Union[dict,None]:
        vals = { "Linear": [],
                 "Natural": [],
                 "Clamped": [],
                 "USub": [] }
        errs = { "Linear": [],
                 "Natural": [],
                 "Clamped": [],
                 "USub": []}
        for itrial, trial in enumerate(self.trials):
            res = trial.GetTIValuesAndErrors()
            if res is None:
                return None
            else:
                skipmodes = []
                for mode in vals:
                    if mode in res:
                        vals[mode].append( res[mode][0] )
                        errs[mode].append( res[mode][1]**2 )
                    else:
                        skipmodes.append(mode)
                for mode in skipmodes:
                    del vals[mode]
                    del errs[mode]

        res = {}
        for mode in vals:
            
            vs = np.array(vals[mode])
            es = np.array(errs[mode])
            N = vs.shape[0]
            mu = np.mean(vs)
            var = 0
            if len(vs) > 1:
                var = np.var(vs,ddof=1)
            err = np.sqrt( (1/N) * ( var + np.mean(es) ) )
            res[mode] = (mu,err)
        return res
    
    def GetMode(self) -> str:
        from collections import defaultdict as ddict
        modes = ddict(int)
        for trial in self.trials:
            modes[ trial.mode ] += 1
        maxcnt = 0
        maxmode = "undef"
        for mode in modes:
            if modes[mode] > maxcnt:
                maxcnt=modes[mode]
                maxmode=mode
        return maxmode
    
