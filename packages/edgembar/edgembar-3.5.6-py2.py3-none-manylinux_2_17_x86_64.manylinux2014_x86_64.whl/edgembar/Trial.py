#!/usr/bin/env python3
from pathlib import Path
from typing import List
from typing import Tuple
from typing import Union
import xml.etree.ElementTree as ET
import numpy as np
from . Results import SimProperty
from . Results import ErrorT


def FindOutliers(data,thresh):
    # data = np.array(data)
    # d = np.abs(data - np.median(data))
    # mdev = np.median(d)
    # s = d / (mdev if mdev else 1.)
    # print(d,mdev,s)
    # return [i for i in range(len(data))
    #         if s[i] > thresh]
    data = np.array(data)
    dist_from_median = np.abs(data - np.median(data))
    dist_from_mean = np.abs(data - np.mean(data))
    return [i for i in range(len(data))
             if dist_from_median[i] > thresh
            and dist_from_mean[i] > thresh ]
        



class Trial(object):
    def __init__( self,
                  name: str,
                  datadir: str,
                  ene: List[str],
                  mode: str = None,
                  offset: int = None,
                  results: List[Union[SimProperty,None]] = None,
                  shift=0):
        
        self.name = name
        self.datadir = datadir
        self.ene = ene
        self.mode = mode
        self.offset = offset
        self.results = results
        self.edge = None
        self.env = None
        self.stage = None
        self.timeseries = None
        self.shift = shift
        
        
    @classmethod
    def from_xmlnode( cls, node: ET.Element ):
        
        name = node.get("name")
        datadir = node.find("dir").text
        mode = node.get("mode")
        shift=0
        for shiftnode in node.findall("shift"):
            shift = float( shiftnode.text )
        enes = []
        for ene in node.findall("ene"):
            enes.append( ene.text )
            state = ene.get("state")
        return cls(name,datadir,enes,mode=mode,shift=shift)

    def SetShift( self, s: float ) -> None:
        self.shift = s
        
    
    def reverse(self):
        self.ene.reverse()

    
    def GetXml( self, node: ET.Element ) -> ET.Element:
        
        import xml.etree.ElementTree as ET
        
        trial = ET.SubElement(node,"trial")
        trial.attrib["name"] = self.name
        if self.mode is not None:
            if self.mode in ["AUTO","MBAR","MBAREXP0",
                             "MBAREXP1","MBAREXP",
                             "BAR","BAREXP0","BAREXP1",
                             "BAREXP"]:
                trial.attrib["mode"] = self.mode
            else:
                raise Exception("Invalid mode '%s'"%(self.mode))
        datadir = ET.SubElement(trial,"dir")
        datadir.text = self.datadir
        if abs(self.shift) > 0:
            shiftnode = ET.SubElement(trial,"shift")
            shiftnode.text = "%.5f"%(self.shift)
        for e in self.ene:
            ene = ET.SubElement(trial,"ene")
            ene.text = e
        return trial


    def GetMode(self) -> str:
        return self.mode
    
    
    def SetLinkedList( self,
                       edge,
                       env,
                       stage) -> None:
        self.edge=edge
        self.env=env
        self.stage=stage

    def GetValueAndError( self,
                          data: np.ndarray,
                          iene: int = None ) -> Tuple[float,float]:
        o = self.offset
        if iene is None:
            n = len(self.ene)-1
        else:
            n = iene
        v = data[o+n,0]-data[o,0]
        e = np.sqrt( data[o+n,1]**2+data[o,1]**2 )
        return v,e

    def GetDVDLProfile(self) -> Union[np.ndarray,None]:
        nsim = len(self.ene)
        has_dvdl = True
        if self.results is None:
            has_dvdl = False
        else:
            for isim in range(nsim):
                try:
                    lam = float(self.ene[isim])
                except:
                    has_dvdl = False
                p = self.results[isim]
                if p is None:
                    has_dvdl = False
                else:
                    if p.dvdlavg is None or p.dvdlerr is None:
                        has_dvdl = False
        prof = None
        if has_dvdl:
            prof = np.zeros( (nsim,3) )
            for isim in range(nsim):
                p = self.results[isim]
                prof[isim,0] = float(self.ene[isim])
                prof[isim,1] = p.dvdlavg
                prof[isim,2] = p.dvdlerr
            if prof[0,0] > prof[-1,0]:
                prof[:,1] *= -1
            prof = prof[prof[:,0].argsort()]
        return prof

    
    def GetTIValuesAndErrors(self) -> Union[dict,None]:
        from . Splines import LinearSplineWithErrorProp
        from . Splines import CubicSplineWithErrorProp
        from . Splines import USubSplineWithErrorProp
        
        from . GlobalOptions import GlobalOptions
        gopts = GlobalOptions()
        
        #DO_USUB = CalcUsubSpline()
        DO_USUB = gopts.CalcUsubSpline
        
        prof = self.GetDVDLProfile()
        res = None
        if prof is not None:
            lspl = LinearSplineWithErrorProp( prof[:,0] )
            nspl = CubicSplineWithErrorProp( prof[:,0], None, None )
            cspl = CubicSplineWithErrorProp( prof[:,0], 0, 0 )
            res = {}
            res["Linear"]  = lspl.Integrate(prof[:,1],prof[:,2])
            res["Natural"] = nspl.Integrate(prof[:,1],prof[:,2])
            res["Clamped"] = cspl.Integrate(prof[:,1],prof[:,2])
            if DO_USUB:
                uspl = USubSplineWithErrorProp(prof[:,0],prof[:,1],prof[:,2])
                res["USub"] = uspl.Integrate()

        return res
        
    
    def GetErrorMsgs( self ) -> List[ErrorT]:
        msg = []
        
        if self.results is not None:

            if len(self.stage.trials) > 2:
                tenes = []
                for itrial,trial in enumerate(self.stage.trials):
                    t = self.stage.trials[itrial]
                    v,e = t.GetValueAndError(self.edge.results.prod)
                    tenes.append(v)
                tenes = np.array(tenes)
                outs = FindOutliers(tenes,2)
                itrial = self.stage.trials.index(self)
                if itrial in outs:
                    msg.append( ErrorT(self.edge.name,self.env.name,
                                       self.stage.name,self.name,"",
                                       'outlier',False) )
                
            
            for isim,p in enumerate(self.results):
                if p is None:
                    continue
                
                if not p.isequil:
                    msg.append( ErrorT.from_trial(self,isim,"equil",True) )
                
                x = p.pstart/p.osize
                if x > self.edge.results.ferreq:
                    msg.append( ErrorT.from_trial(self,isim,"feq",True) )
                #elif x > 0.6:
                #    msg.append( ErrorT.from_trial(self,isim,"feq",False) )
                    
                x = p.psize
                if x < 80:
                    msg.append( ErrorT.from_trial(self,isim,"psize",True) )
                elif x < 100:
                    msg.append( ErrorT.from_trial(self,isim,"psize",False) )
                    
                x = p.pstride
                if x > 100:
                    msg.append( ErrorT.from_trial(self,isim,"pstride",True) )
                elif x > 50:
                    msg.append( ErrorT.from_trial(self,isim,"pstride",False) )
                    
                RE = 1
                nre = 0
                if isim < len(self.ene) - 1:
                    x = p.overlaps[isim+1]
                    if x >= 0:
                        if x < 0.15:
                            msg.append( ErrorT.from_trial(self,isim,"S",True) )
                        elif x < 0.25:
                            msg.append( ErrorT.from_trial(self,isim,"S",False) )
                    RE = p.entropies[isim+1]
                    nre = 1
                    
                if isim > 0:
                    if nre > 0:
                        minRE = min(RE,p.entropies[isim-1])
                        x = minRE
                        #if minRE < 0.3:
                        #    x = minRE
                        #else:
                        #    x = 0.5*(RE+p.entropies[isim-1])

                    else:
                        x=RE
                else:
                    x = RE
                if x >= 0:
                    if x < 0.4:
                        msg.append( ErrorT.from_trial(self,isim,"RE",True) )
                    elif x < 0.6:
                        msg.append( ErrorT.from_trial(self,isim,"RE",False) )

        return msg

#    def SetVBAShift(self, disang_filepath: Path) -> float:
#        from .VBA import calc_vba_shift
#        self.SetShift(calc_vba_shift(disang_filepath))

