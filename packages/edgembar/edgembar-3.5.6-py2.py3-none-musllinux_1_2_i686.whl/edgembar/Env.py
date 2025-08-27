#!/usr/bin/env python3
from typing import List
from typing import Tuple
from typing import Union
import xml.etree.ElementTree as ET
from . Trial import Trial
from . Stage import Stage
import numpy as np


class Env(object):
    def __init__( self,
                  name: str,
                  stages: List[Stage] ):
        
        self.name = name
        self.stages = stages
        self.edge = None

        
    @classmethod
    def from_xmlnode( cls, node: ET.Element):
        
        from . Stage import Stage
        name = node.get("name")
        stages = [ Stage.from_xmlnode(x)
                   for x in node.findall("stage") ]
        return cls(name,stages)

    
    def GetXml( self, node: ET.Element ) -> ET.Element:
        
        import xml.etree.ElementTree as ET
        env = ET.SubElement(node,"env")
        env.attrib["name"] = self.name
        for stage in self.stages:
            stage.GetXml(env)
        return env

    def SetShift( self, s: float ) -> None:
        for stage in self.stages:
            stage.SetShift(s)
    
    def SetLinkedList( self, edge ) -> None:
        
        self.edge=edge
        for i in range(len(self.stages)):
            self.stages[i].SetLinkedList(edge,self)
    

    def GetValueAndError( self, data: np.ndarray ) -> Tuple[float,float]:
        v = 0
        e = 0
        for s in self.stages:
            tv,te = s.GetValueAndError(data)
            v += tv
            e += te**2
        return v,np.sqrt(e)
    
    def GetAllTrials(self) -> List[Trial]:
        
        return [t for s in self.stages
                for t in s.trials ]
    
    def GetTIValuesAndErrors(self) -> Union[dict,None]:
        res = { "Linear" : [0,0],
                "Natural" : [0,0],
                "Clamped" : [0,0],
                "USub" : [0,0]}
        skipmodes=[]
        for stage in self.stages:
            v = stage.GetTIValuesAndErrors()
            if v is None:
                return None
            for mode in res:
                if mode in v:
                    res[mode][0] += v[mode][0]
                    res[mode][1] += v[mode][1]**2
                else:
                    skipmodes.append(mode)
        for mode in skipmodes:
            if mode in res:
                del res[mode]
        for mode in res:
            mu = res[mode][0]
            err = np.sqrt( res[mode][1] )
            res[mode] = (mu,err)
        return res

    
    def GetMode(self) -> str:
        trials = self.GetAllTrials()
        
        from collections import defaultdict as ddict
        modes = ddict(int)
        for trial in trials:
            modes[ trial.mode ] += 1
        maxcnt = 0
        maxmode = "undef"
        for mode in modes:
            if modes[mode] > maxcnt:
                maxcnt=modes[mode]
                maxmode=mode
        return maxmode

