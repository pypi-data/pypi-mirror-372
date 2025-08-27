#!/usr/bin/env python3

from typing import Optional
from typing import List

def CleanName( name: str ):
    return name.replace("~","_to_")\
               .replace(".","d")\
               .replace("/","s")\
               .replace(" ","")



def GetUnicodeName( edge: str,
                    env: Optional[str],
                    stage: Optional[str],
                    trial: Optional[str],
                    ene: Optional[str],
                    sym: Optional[str] = "G") -> str:

    if env is None:
        name = f"\u3008\u0394\u0394{sym}\u3009 {edge}"
    else:
        e = "tgt"
        if "ref" in env:
            e = "ref"
        if stage is not None:
            e += f",{stage[:3]}"
        if trial is None:
            name = f"\u3008\u0394{sym}({e})\u3009 {edge}"
        elif ene is None:
            name = f"\u0394{sym}({e},\u0023 {trial}) {edge}"
        else:
            name = f"{sym}({e},\u0023 {trial},\u03bb:{ene}) {edge}"

    return name


def GetNameFromObj( eneobj,
                    istate: Optional[int] = None ) -> List[Optional[str]]:
    edge =None
    env  =None
    stage=None
    trial=None
    ene=None
    if hasattr(eneobj,'edge'):
        edge = eneobj.edge.name
        if hasattr(eneobj,'env'):
            env = eneobj.env.name
            if hasattr(eneobj,'stage'):
                stage = eneobj.stage.name
                trial = eneobj.name
                if istate is not None:
                    ene = eneobj.ene[istate]
            else:
                stage = eneobj.name
        else:
            env = eneobj.name
    else:
        edge = eneobj.name
    return [edge,env,stage,trial,ene]

def GetHtmlSymbolFromObj( eneobj, istate: Optional[int] = None, sym: Optional[str] = "G" ) -> str:
    x = GetNameFromObj(eneobj,istate=istate)
    return GetHtmlSymbol(x[1],x[2],x[3],x[4],sym=sym)


def GetHtmlIdFromObj( eneobj, istate: Optional[int] = None, sym: Optional[str] = "G" ) -> str:
    x = GetNameFromObj(eneobj,istate=istate)
    return GetHtmlId(x[0],x[1],x[2],x[3],x[4],sym=sym)

        

def GetHtmlSymbol( env: Optional[str],
                   stage: Optional[str],
                   trial: Optional[str],
                   ene: Optional[str],
                   sym: Optional[str] = "G" ) -> str:
    
    if env is None:
        name = f"&lang;&Delta;&Delta;{sym}&rang;"
    else:
        e = "tgt"
        if "ref" in env:
            e = "ref"
        if stage is not None:
            e += f",{stage[:3]}"
        if trial is None:
            name = f"&lang;&Delta;{sym}({e})&rang;"
        elif ene is None:
            name = f"&Delta;{sym}({e},&num;{trial})"
        else:
            name = f"&Delta;{sym}({e},&num;{trial},&lambda;:{ene})"
    return name


def GetHtmlName( edge: str,
                 env: Optional[str],
                 stage: Optional[str],
                 trial: Optional[str],
                 ene: Optional[str],
                 sym: Optional[str] = "G" ) -> str:

    return GetHtmlSymbol(env,stage,trial,ene,sym=sym) + " " + edge



def GetHtmlId( edge: str,
               env: Optional[str],
               stage: Optional[str],
               trial: Optional[str],
               ene: Optional[str],
               sym: Optional[str] = "G" ) -> str:
        
    name = "ts_" + sym + "_" + edge
    if env is not None:
        name += env
    if stage is not None:
        name += stage
    if trial is not None:
        name += trial
    if ene is not None:
        name += ene
    return CleanName(name)

