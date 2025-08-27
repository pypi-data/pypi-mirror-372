#!/usr/bin/env python3

from typing import List
import numpy
from . CenteredCubic import CenteredCubic

class TimeSeriesData(object):
    def __init__( self,
                  time: float,
                  values: numpy.ndarray ):
        
        self.time=time
        self.values=values

        
class ConstraintData(object):
    def __init__( self,
                  conval: float,
                  chisq: float,
                  values: numpy.ndarray ):
        
        self.conval=conval
        self.chisq=chisq
        self.values=values

        
class Results(object):
    def __init__( self,
                  prod: numpy.ndarray = None,
                  fwd: List[TimeSeriesData] = None,
                  rev: List[TimeSeriesData] = None,
                  con: List[ConstraintData] = None,
                  fhalf: List[TimeSeriesData] = None,
                  lhalf: List[TimeSeriesData] = None,
                  version: str = "undefined",
                  hash: str = "undefined",
                  command: str = "undefined",
                  date: str = "undefined",
                  ptol: float = None ):
        
        self.prod=prod
        self.fwd=fwd
        self.rev=rev
        self.con=con
        self.fhalf=fhalf
        self.lhalf=lhalf
        self.version = version
        self.hash = hash
        self.command = command
        self.date = date
        self.ptol = ptol
        self.conobj = None
        if con is not None:
            qs = [ c.conval for c in con ]
            chis = [ c.chisq for c in con ]
            self.conobj = CenteredCubic.from_lsq(qs,chis)
        self.fstart = 0
        self.fstop = 1
        self.stride = 1
        self.fmaxeq = 0.5
        self.ferreq = -1
        self.temp = 298.
        self.dtol = 0.1
        args = command.replace("=", " ").split()
        for iarg,arg in enumerate(args):
            if arg == "--fstart" or arg == "-s":
                self.fstart = float(args[iarg+1])
            elif arg == "--fstop" or arg == "-S":
                self.fstop = float(args[iarg+1])
            elif arg == "--stride" or arg == "-g":
                self.stride = int(args[iarg+1])
            elif arg == "--fmaxeq":
                self.fmaxeq = float(args[iarg+1])
            elif arg == "--ferreq":
                self.ferreq = float(args[iarg+1])
            elif arg == "--temp" or arg == "-t":
                self.temp = float(args[iarg+1])
            elif arg == "--dtol":
                self.dtol = float(args[iarg+1])
        self.ferreq = max(self.ferreq,self.fmaxeq)
        
                



class PathData(object):
    def __init__( self, name : str, path : List[str],
                  eidxs : List[int], esigns : List[int],
                  value : float, error : float ):
        self.name = name
        self.path = path
        self.eidxs = eidxs
        self.esigns = esigns
        self.value = value
        self.error = error
        
            
        
class SimProperty(object):
    def __init__( self,
                  ostride: int,
                  osize: int,
                  pstart: int,
                  pstride: int,
                  cstride: int,
                  csize: int,
                  autoeqmode: int,
                  isequil: bool,
                  overlaps: numpy.ndarray,
                  entropies: numpy.ndarray,
                  dvdlavg: float,
                  dvdlerr: float ):
        
        self.ostride = ostride
        self.osize = osize
        self.pstart = pstart
        self.pstride = pstride
        self.psize = self.osize-self.pstart
        self.cstride = cstride
        self.csize = csize
        self.autoeqmode = autoeqmode
        self.isequil = isequil
        self.overlaps = overlaps
        self.entropies = entropies
        self.dvdlavg = dvdlavg
        self.dvdlerr = dvdlerr
        

        
class ErrorT(object):
    
    @classmethod
    def from_trial( cls, trial, iene, kind, iserr ):
        return cls( trial.edge.name,
                    trial.env.name,
                    trial.stage.name,
                    trial.name,
                    trial.ene[iene],
                    kind, iserr )
    
    def __init__( self,
                  edge: str,
                  env: str,
                  stage: str,
                  trial: str,
                  ene: str,
                  kind: str,
                  iserr: bool ):
        
        from . Names import GetHtmlId
        from . Names import GetHtmlSymbol
        self.edge=edge
        self.env=env
        self.stage=stage
        self.trial=trial
        self.ene=ene
        self.kind=kind
        self.iserr = iserr
        if len(self.ene) == 0:
            self.ene = None
        self.divid=GetHtmlId(self.edge,self.env,self.stage,self.trial,None)
        self.htmlsym=GetHtmlSymbol(self.env,self.stage,self.trial,self.ene)

