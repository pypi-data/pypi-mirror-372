#!/usr/bin/env python3
from typing import List
from typing import Tuple
from typing import Optional
from typing import TextIO
from typing import Union
import xml.etree.ElementTree as ET
import numpy as np

from . Trial import Trial
from . Stage import Stage
from . Env import Env
from . Results import Results
from . Results import ErrorT

class Edge(object):
    
    def __init__( self,
                  name: str,
                  cmpl: Optional['Env'],
                  solv: Optional['Env'],
                  results: Results = None ):
        
        self.name = name
        self.cmpl = cmpl
        self.solv = solv

        self.results=results
        
        if self.cmpl is not None:
            self.cmpl.SetLinkedList(self)
        if self.solv is not None:
            self.solv.SetLinkedList(self)

        self.timeseries = None
            
        if self.results is not None:
            self._SetTimeseries()

            
    @classmethod
    def from_xml( cls, fname: str ):
        
        import xml.etree.ElementTree as ET
        tree = ET.parse(fname)
        return cls.from_xmlnode(tree.getroot())

    
    @classmethod
    def from_xmlnode( cls, node: ET.Element ):
        
        from . Env import Env
        name = node.get("name")
        
        cmpl = node.find(".//env[@name='target']")
        if cmpl is not None:
            cmpl = Env.from_xmlnode(cmpl)
        else:
            cmpl = None
            
        solv = node.find(".//env[@name='reference']")
        if solv is not None:
            solv = Env.from_xmlnode(solv)
        else:
            solv = None

        return cls(name,cmpl,solv)

    
    def __str__(self) -> str:
        
        import xml.etree.ElementTree as ET
        import xml.dom.minidom as md
        import os
        pretty_xml = md.parseString(ET.tostring( \
                        self.GetXml(),encoding="unicode")).toprettyxml()
        return os.linesep.join([s for s in pretty_xml.splitlines()
                                if s.strip()])

    
    def GetXml(self) -> ET.Element:
        
        import xml.etree.ElementTree as ET
        edge = ET.Element('edge')
        edge.attrib["name"] = self.name
        if self.cmpl is not None:
            self.cmpl.GetXml(edge)
        if self.solv is not None:
            self.solv.GetXml(edge)
        return edge

    
    def WriteXml( self, fname: str = None ) -> None:
        
        if fname is None:
            fname = self.name + ".xml"
        fh = open(fname,"w")
        fh.write(str(self) + "\n")
        fh.close()

        
    def GetEnvs(self) -> List[Env]:
        
        envs = []
        if self.cmpl is not None:
            envs.append(self.cmpl)
        if self.solv is not None:
            envs.append(self.solv)
        return envs

    
    def GetAllTrials(self) -> List[Trial]:
        
        return [t for e in self.GetEnvs()
                for s in e.stages
                for t in s.trials ]

    def GetValueAndError( self, data: np.ndarray ) -> Tuple[float,float]:
        v = 0
        e = 0
        if self.cmpl is not None:
            v,e = self.cmpl.GetValueAndError(data)
        if self.solv is not None:
            a,b = self.solv.GetValueAndError(data)
            v -= a
            e = np.sqrt(e**2 + b**2)
        return v,e



            
    def _SetTimeseries(self) -> None:
        from . TimeSeriesAnalysis import TimeSeriesAnalysis

        envs = self.GetEnvs()
        #self.timeseries = None
        #if len(envs) == 2:
        #   ts = TimeSeriesAnalysis.factory(self,self.results)
        self.timeseries = TimeSeriesAnalysis.factory(self,self.results)
            
        for env in envs:
            ts = TimeSeriesAnalysis.factory(env,self.results)
            env.timeseries = ts
            

        for env in envs:
            for stage in env.stages:
                ts = TimeSeriesAnalysis.factory(stage,self.results)
                stage.timeseries = ts
                    
        for env in envs:
            for stage in env.stages:
                for trial in stage.trials:
                    ts = TimeSeriesAnalysis.factory(trial,self.results)
                    trial.timeseries = ts

        for env in envs:
            for stage in env.stages:
                for trial in stage.trials:
                    trial.stateseries = []
                    for iene in range(len(trial.ene)):
                        ts = TimeSeriesAnalysis.factory(trial,self.results,iene)
                        trial.stateseries.append( ts )
                        
        
    def GetErrorMsgs(self) -> List[ErrorT]:
        msgs=[]
        for trial in self.GetAllTrials():
            msgs.extend( trial.GetErrorMsgs() )
        return msgs

    
    def RemoveOutliers(self):
        envs = self.GetEnvs()
        for env in envs:
            for stage in env.stages:
                stage.RemoveOutliers()

    def GetTIValuesAndErrors(self) -> Union[dict,None]:
        res = { "Linear" : [0,0],
                "Natural" : [0,0],
                "Clamped" : [0,0],
                "USub" : [0,0] }
        
        skipmodes = []
        if self.cmpl is not None:
            v = self.cmpl.GetTIValuesAndErrors()
            if v is None:
                return None
            for mode in res:
                if mode in v:
                    res[mode][0] = v[mode][0]
                    res[mode][1] = v[mode][1]**2
                else:
                    skipmodes.append(mode)
        if self.solv is not None:
            v = self.solv.GetTIValuesAndErrors()
            if v is None:
                return None
            for mode in res:
                if mode in v:
                    res[mode][0] -= v[mode][0]
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

    def SetVBAShift(self) -> None:
        from . VBA import GetBoreschRstData
        for env in self.GetEnvs():
            if env.name != "target":
                continue
            for stage in env.stages:
                for trial in stage.trials:
                    shift = GetBoreschRstData(trial)
                    trial.SetShift(shift)


