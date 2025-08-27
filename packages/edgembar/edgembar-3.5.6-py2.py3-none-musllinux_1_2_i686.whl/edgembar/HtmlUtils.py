#!/usr/bin/env python3
import numpy as np
from typing import Optional
from typing import Tuple
from typing import Union
from typing import List
import xml.etree.ElementTree as ET
from . Edge import Edge
from . Env import Env
from . Stage import Stage
from . Trial import Trial
from . Graph import Graph
from . Results import Results



class HexColorMap(object):
    def __init__(self,vmin,vmax,cmap='coolwarm'):
        import matplotlib.cm as cm
        from matplotlib.colors import Normalize
        self.vmin=vmin
        self.vmax=vmax
        self.cmap = cm.get_cmap(cmap)
        self.norm = Normalize(self.vmin,self.vmax)

    def sprint(self,x):
        from matplotlib.colors import to_hex
        s = self.norm(x)
        c = to_hex(self.cmap(s))
        return "{ color: \"%s\", size: %.5f }"%(c,s)

    def __call__(self,x):
        return self.sprint(x)
    

def GetGoogleChartsScript() -> ET.Element:
    return ET.Element('script',
            attrib={ 'type': "text/javascript",
                     'src': "https://www.gstatic.com/charts/loader.js" })


def GetVisNetworkScript() -> ET.Element:
    return ET.Element('script',
            attrib={ 'type': "text/javascript",
                     'src': "https://unpkg.com/vis-network/standalone/umd/vis-network.min.js" })


def GetTimeseriesChartScript() -> ET.Element:
    from . import pkgdata
    import importlib.resources as import_resources
    ele = ET.Element('script', attrib={'type': "text/javascript"})
    ele.text = import_resources.read_text( pkgdata, "tschart.js" )
    return ele


def GetEdgeCSS() -> ET.Element:
    from . import pkgdata
    import importlib.resources as import_resources
    ele = ET.Element('style')
    ele.text = import_resources.read_text( pkgdata, "edge.css" )
    return ele


def GetGraphCSS() -> ET.Element:
    from . import pkgdata
    import importlib.resources as import_resources
    ele = ET.Element('style')
    ele.text = import_resources.read_text( pkgdata, "graph.css" )
    return ele


def GetGraphCanvasScript() -> ET.Element:
    from . import pkgdata
    import importlib.resources as import_resources
    ele = ET.Element('script', attrib={'type': "text/javascript"})
    ele.text = import_resources.read_text( pkgdata, "vis-iface.js" )
    return ele

def GetSortTableScript() -> ET.Element:
    from . import pkgdata
    import importlib.resources as import_resources
    ele = ET.Element('script', attrib={'type': "text/javascript"})
    ele.text = import_resources.read_text( pkgdata, "sorttable.js" )
    return ele


def GetSeleRowScript() -> ET.Element:
    from . import pkgdata
    import importlib.resources as import_resources
    ele = ET.Element('script', attrib={'type': "text/javascript"})
    ele.text = import_resources.read_text( pkgdata, "selerow.js" )
    return ele


def GetReplExchData( self: Trial ) -> Union[dict,None]:
    from pathlib import Path
    import yaml

    fname = Path(self.datadir) / "rem.log.yaml"
    #print(f"Looking for {fname}")
    data = None
    if fname.is_file():
        #print(f"Found {fname}")
        with open(fname,"r") as fh:
            data = yaml.safe_load(fh)
        keys = [ 'Average single pass steps:',
                 'Round trips per replica:',
                 'Total round trips:',
                 'neighbor_acceptance_ratio']
        for k in keys:
            if k not in data:
                #print("Missing key: ",k)
                data = None
                break
        if data is not None:
            if len(data[keys[-1]]) != len(self.ene)-1:
                data = None
    #print("leaving with ",data)
    return data


def GetEdgeSummaryTable( self: Edge ) -> ET.Element:
    from . Names import GetHtmlSymbol, GetHtmlId

    envs = self.GetEnvs()
    
    ncols = 3 + len(envs)
        
    feqs = []
    gs = []
    for t in self.GetAllTrials():
        for isim,res in enumerate(t.results):
            if res is not None:
                feqs.append( res.pstart/res.osize )
                gs.append( res.pstride )
    feqs = [ np.mean(feqs) ]
    gs = [ np.mean(gs) ]
    if self.timeseries is not None:
        if self.timeseries.frtimes is not None:
            for t in self.timeseries.frtimes:
                feqs.append( 1-t )
                gs.append(-1)
        elif self.timeseries.fltimes is not None:
            for t in self.timeseries.fltimes:
                feqs.append( 0.5 * ( 1-t ) )
                gs.append(-1)
                

    sdata = [ [""]*ncols for i in range(len(gs)) ]
    for i in range(len(gs)):
        if gs[i] > 0:
            sdata[i][-1] = "%i"%(gs[i])
        else:
            sdata[i][-1] = ""
        sdata[i][-2] = "%.2f"%(feqs[i])
    if self.timeseries is not None:
        v,e = self.timeseries.prod
        sdata[0][0] = "%.3f &plusmn; %.3f"%(v,e)
        #if len(envs) > 1:
        for ienv,env in enumerate(envs):
            v,e = env.timeseries.prod
            sdata[0][ienv+1] = "%.3f &plusmn; %.3f"%(v,e)
    else:
        v,e = self.GetValueAndError( self.results.prod )
        sdata[0][0] = "%.3f &plusmn; %.3f"%(v,e)
        #if len(envs) > 1:
        for ienv,env in enumerate(envs):
            v,e = env.GetValueAndError( self.results.prod )
            sdata[0][ienv+1] = "%.3f &plusmn; %.3f"%(v,e)
                
    if self.timeseries is not None:
        if self.timeseries.frtimes is not None:
            for i in range(len(self.timeseries.frtimes)):
                v,e = self.timeseries.rev[i]
                sdata[i+1][0] = "%.3f &plusmn; %.3f"%(v,e)
                #if len(envs) > 1:
                for ienv,env in enumerate(envs):
                    v,e = env.timeseries.rev[i]
                    sdata[i+1][ienv+1] = "%.3f &plusmn; %.3f"%(v,e)
        elif self.timeseries.fltimes is not None:
            for i in range(len(self.timeseries.frtimes)):
                v,e = self.timeseries.lhalf[i]
                sdata[i+1][0] = "%.3f &plusmn; %.3f"%(v,e)
                #if len(envs) > 1:
                for ienv,env in enumerate(envs):
                    v,e = env.timeseries.lhalf[i]
                    sdata[i+1][ienv+1] = "%.3f &plusmn; %.3f"%(v,e)
        
    table = ET.Element('table',attrib={'class':'simprop'})
    tr = ET.SubElement(table,'tr',attrib={'class':'ul'})

    ET.SubElement(tr,'th').text = "Sampling"
    ET.SubElement(tr,'th').text = GetHtmlSymbol(None,None,None,None)
    
    #if len(envs) > 1:
    #ET.SubElement(tr,'th').text = GetHtmlSymbol(envs[0].name,None,None,None)
    #ET.SubElement(tr,'th').text = GetHtmlSymbol(envs[1].name,None,None,None)
    for env in envs:
        ET.SubElement(tr,'th').text = GetHtmlSymbol(env.name,None,None,None)
    
    feq = ET.SubElement(tr,"th")
    #feq = ET.SubElement(feq,"span")
    ET.SubElement(feq,'span').text = "&lang;f"
    ET.SubElement(feq,"sub").text = "eq"
    ET.SubElement(feq,'span').text = "&rang;"

    gprod = ET.SubElement(tr,"th")
    #gprod = ET.SubElement(gprod,"span")
    ET.SubElement(gprod,'span').text = "&lang;g"
    ET.SubElement(gprod,"sub").text = "prod"
    ET.SubElement(gprod,'span').text = "&rang;"

        
    labels = []
    for ix,x in enumerate([ fs[-2] for fs in sdata ]):
        if ix == 0:
            labels.append("Prod.")
        else:
            labels.append("%2i%% Eq."%(100*float(x)))

    for irow,label in enumerate(labels):
        tr = ET.SubElement(table,'tr')
        for c in [label] + sdata[irow]:
            ET.SubElement(tr,'td').text = c

    return table


def GetEnvSummaryTable( self: Env ) -> ET.Element:
    from . Names import GetHtmlSymbol, GetHtmlId

    ncols = 3 + len(self.stages)
        
    feqs = []
    gs = []
    for t in self.GetAllTrials():
        for isim,res in enumerate(t.results):
            if res is not None:
                feqs.append( res.pstart/res.osize )
                gs.append( res.pstride )
    feqs = [ np.mean(feqs) ]
    gs = [ np.mean(gs) ]
    if self.timeseries is not None:
        if self.timeseries.frtimes is not None:
            for t in self.timeseries.frtimes:
                feqs.append( 1-t )
                gs.append(-1)
        elif self.timeseries.fltimes is not None:
            for t in self.timeseries.fltimes:
                feqs.append( 0.5 * ( 1-t ) )
                gs.append(-1)
                

    sdata = [ [""]*ncols for i in range(len(gs)) ]
    for i in range(len(gs)):
        if gs[i] > 0:
            sdata[i][-1] = "%i"%(gs[i])
        else:
            sdata[i][-1] = ""
        sdata[i][-2] = "%.2f"%(feqs[i])
    if self.timeseries is not None:
        v,e = self.timeseries.prod
        sdata[0][0] = "%.3f &plusmn; %.3f"%(v,e)
        for istg,stg in enumerate(self.stages):
            v,e = stg.timeseries.prod
            sdata[0][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
    else:
        v,e = self.GetValueAndError(self.edge.results.prod)
        sdata[0][0] = "%.3f &plusmn; %.3f"%(v,e)
        for istg,stg in enumerate(self.stages):
            v,e = stg.GetValueAndError(self.edge.results.prod)
            sdata[0][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
    
    if self.timeseries is not None:
        if self.timeseries.frtimes is not None:
            for i in range(len(self.timeseries.frtimes)):
                v,e = self.timeseries.rev[i]
                sdata[i+1][0] = "%.3f &plusmn; %.3f"%(v,e)
                for istg,stg in enumerate(self.stages):
                    v,e = stg.timeseries.rev[i]
                    sdata[i+1][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
        elif self.timeseries.fltimes is not None:
            for i in range(len(self.timeseries.fltimes)):
                v,e = self.timeseries.lhalf[i]
                sdata[i+1][0] = "%.3f &plusmn; %.3f"%(v,e)
                for istg,stg in enumerate(self.stages):
                    v,e = stg.timeseries.lhalf[i]
                    sdata[i+1][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
        
    table = ET.Element('table',attrib={'class':'simprop'})
    tr = ET.SubElement(table,'tr',attrib={'class':'ul'})

    ET.SubElement(tr,'th').text = "Sampling"
    ET.SubElement(tr,'th').text = GetHtmlSymbol(self.name,None,None,None)
    
    for stg in self.stages:
        ET.SubElement(tr,'th').text = GetHtmlSymbol(self.name,stg.name,None,None)

    feq = ET.SubElement(tr,"th")
    feq = ET.SubElement(feq,"span")
    ET.SubElement(feq,'span').text = "&lang;f"
    ET.SubElement(feq,"sub").text = "eq"
    ET.SubElement(feq,'span').text = "&rang;"

    gprod = ET.SubElement(tr,"th")
    gprod = ET.SubElement(gprod,"span")
    ET.SubElement(gprod,'span').text = "&lang;g"
    ET.SubElement(gprod,"sub").text = "prod"
    ET.SubElement(gprod,'span').text = "&rang;"

        
    labels = []
    for ix,x in enumerate([ fs[-2] for fs in sdata ]):
        if ix == 0:
            labels.append("Prod.")
        else:
            labels.append("%2i%% Eq."%(100*float(x)))

    for irow,label in enumerate(labels):
        tr = ET.SubElement(table,'tr')
        for c in [label] + sdata[irow]:
            ET.SubElement(tr,'td').text = c

    return table



def GetStageSummaryTable( self: Stage ) -> ET.Element:
    from . Names import GetHtmlSymbol, GetHtmlId

    ncols = []
    cidxs = []
    tncols = len(self.trials)+1
    for i in range(len(self.trials)+1):
        cidxs.append(i)
        if len(cidxs) == 5 or i == len(self.trials):
            ncols.append(cidxs)
            cidxs=[]
    
    feqs = []
    gs = []
    for t in self.trials:
        for isim,res in enumerate(t.results):
            if res is not None:
                feqs.append( res.pstart/res.osize )
                gs.append( res.pstride )
    feqs = [ np.mean(feqs) ]
    gs = [ np.mean(gs) ]
    if self.timeseries is not None:
        if self.timeseries.frtimes is not None:
            for t in self.timeseries.frtimes:
                feqs.append( 1-t )
                gs.append(-1)
        elif self.timeseries.fltimes is not None:
            for t in self.timeseries.fltimes:
                feqs.append( 0.5 * ( 1-t ) )
                gs.append(-1)
                

    sdata = [ [""]*tncols for i in range(len(gs)) ]

    if self.timeseries is not None:
        v,e = self.timeseries.prod
        sdata[0][0] = "%.3f &plusmn; %.3f"%(v,e)
        for istg,stg in enumerate(self.trials):
            v,e = stg.timeseries.prod
            sdata[0][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
    else:
        v,e = self.GetValueAndError(self.edge.results.prod)
        sdata[0][0] = "%.3f &plusmn; %.3f"%(v,e)
        for istg,stg in enumerate(self.trials):
            v,e = stg.GetValueAndError(self.edge.results.prod)
            sdata[0][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
            
    if self.timeseries is not None:
        if self.timeseries.frtimes is not None:
            for i in range(len(self.timeseries.frtimes)):
                v,e = self.timeseries.rev[i]
                sdata[i+1][0] = "%.3f &plusmn; %.3f"%(v,e)
                for istg,stg in enumerate(self.trials):
                    v,e = stg.timeseries.rev[i]
                    sdata[i+1][istg+1] = "%.3f &plusmn; %.3f"%(v,e)
        elif self.timeseries.fltimes is not None:
            for i in range(len(self.timeseries.frtimes)):
                v,e = self.timeseries.lhalf[i]
                sdata[i+1][0] = "%.3f &plusmn; %.3f"%(v,e)
                for istg,stg in enumerate(self.trials):
                    v,e = stg.timeseries.lhalf[i]
                    sdata[i+1][ienv+1] = "%.3f &plusmn; %.3f"%(v,e)

    table = ET.Element('table',attrib={'class':'simprop'})
    for itable,cs in enumerate(ncols):
        tr = ET.SubElement(table,'tr',attrib={'class':'ul'})

        ET.SubElement(tr,'th').text = "Sampling"
    
        for c in cs:
            if c > 0:
                t = self.trials[c-1]
                ET.SubElement(tr,'th').text = GetHtmlSymbol\
                    (self.env.name,self.name,t.name,None)
            else:
                ET.SubElement(tr,'th').text = GetHtmlSymbol\
                    (self.env.name,self.name,None,None)
                
        if itable > 0 and len(cs) < 5:
            for c in range(len(cs),5):
                ET.SubElement(tr,'th')
        
        labels = []
        for ix,x in enumerate(feqs):
            if ix == 0:
                labels.append("Prod.")
            else:
                labels.append("%2i%% Eq."%(100*float(x)))

        for irow,label in enumerate(labels):
            tr = ET.SubElement(table,'tr')
            mydata = [ sdata[irow][c] for c in cs ]
            for c in [label] + mydata:
                ET.SubElement(tr,'td').text = c
            if itable > 0 and len(cs) < 5:
                for c in range(len(cs),5):
                    ET.SubElement(tr,'th')

    return table


def GetTrialSummaryTable( trial: Trial, results: Results, options: dict ) -> ET.Element:
    from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj

    table = ET.Element('table',attrib={'class':"simprop"})
    tr = ET.SubElement(table,'tr',attrib={'class':'top'})
    th = ET.SubElement(tr,'th')
    th.text = "Traj"
    th = ET.SubElement(tr,'th')
    th.text = "&Delta;G"
    th = ET.SubElement(tr,'th',attrib={'colspan':'3','class':'ul'})
    th.text = "Prod. Region"
    th = ET.SubElement(tr,'th')
    th = ET.SubElement(tr,'th')
    th = ET.SubElement(tr,'th')
    th = ET.SubElement(tr,'th',attrib={'colspan':'2','class':'ul'})
    th.text = "All Data"
    th = ET.SubElement(tr,'th')
    th.text = "S"
    th = ET.SubElement(tr,'th',attrib={'colspan':'2','class':'ul'})
    th.text = "RE"
    th = ET.SubElement(tr,'th')
    th.text = "Conv?"
                    
    tr = ET.SubElement(table,'tr',attrib={'class':'ul'})
    th = ET.SubElement(tr,'th')
    th = ET.SubElement(tr,'th',attrib={'style':'text-align:center;'})
    th.text = trial.mode
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span')
    span.text = "f"
    sub = ET.SubElement(th,'sub')
    sub.text = "eq"
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span')
    span.text = "N"
    sub = ET.SubElement(th,'sub')
    sub.text = "eq"
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span')
    span.text = "g"
    sub = ET.SubElement(th,'sub')
    sub.text = "prod"
    
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span')
    span.text = "g"
    sub = ET.SubElement(th,'sub')
    sub.text = "ana"
    
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span')
    span.text = "N"
    sub = ET.SubElement(th,'sub')
    sub.text = "ana"
    
    th = ET.SubElement(tr,'th')
    th = ET.SubElement(tr,'th')
    th.text = "g"
    th = ET.SubElement(tr,'th')
    th.text = "N"
    th = ET.SubElement(tr,'th')
    th.text = "Fwd"
    th = ET.SubElement(tr,'th')
    th.text = "Fwd"
    th = ET.SubElement(tr,'th')
    th.text = "Rev"
    th = ET.SubElement(tr,'th')

        
    for isim in range(len(trial.ene)):
        tr = ET.SubElement(table,'tr')
        traj = trial.ene[isim]
        p = trial.results[isim]
        td = ET.SubElement(tr,'td')

        if p is not None:
            f = p.pstart/p.osize
            if options["du_print_thresh"] >= 0:
                prtsim = f >= options["du_print_thresh"]
            else:
                prtsim = not p.isequil
            
            if prtsim:
                sid = GetHtmlIdFromObj(trial,istate=isim,sym="U")
                ET.SubElement(td,'a',attrib={'href':f"#{sid}"}).text = traj
            else:
                td.text = traj
        else:
            td.text = traj
        
        #v,e = trial.GetValueAndError(self.results.prod,iene=isim)
        v,e = trial.GetValueAndError(results.prod,iene=isim)
        td = ET.SubElement(tr,'td')
        td.text = "%6.3f &plusmn; %5.3f"%(v,e)

        if p is None:
            for ii in range(11):
                td = ET.SubElement(tr,'td')
        else:
            f = p.pstart/p.osize
            td = ET.SubElement(tr,'td')
            td.text = "%.2f"%(f)
            #print(f,results.fmaxeq,f > results.fmaxeq)
            if f > results.ferreq:
                td.attrib["class"]="error"
            #elif f > 0.6:
            #    td.attrib["class"]="warn"

            td = ET.SubElement(tr,'td')
            td.text = "%i"%(p.pstart)

            td = ET.SubElement(tr,'td')
            td.text = "%i"%(p.pstride)
            if p.pstride > 100:
                td.attrib["class"]="error"
            elif p.pstride > 50:
                td.attrib["class"]="warn"

                
            td = ET.SubElement(tr,'td')
            td.text = "%i"%(p.cstride)
            if p.pstride > 100:
                td.attrib["class"]="error"
            elif p.pstride > 50:
                td.attrib["class"]="warn"
                
            td = ET.SubElement(tr,'td')
            td.text = "%i"%(p.csize)
            if p.csize < 80:
                td.attrib["class"]="error"
            elif p.csize < 100:
                td.attrib["class"]="warn"
                    
            td = ET.SubElement(tr,'td')
                
            td = ET.SubElement(tr,'td')
            td.text = "%i"%(p.ostride)
                
            td = ET.SubElement(tr,'td')
            td.text = "%i"%(p.osize)
                
            if isim < len(trial.ene) - 1:
                f = p.overlaps[isim+1]
                td = ET.SubElement(tr,'td')
                if f >= 0:
                    td.text = "%.2f"%(f)
                    if f < 0.15:
                        td.attrib["class"]="error"
                    elif f < 0.25:
                        td.attrib["class"]="warn"

                f = p.entropies[isim+1]
                td = ET.SubElement(tr,'td')
                if f >= 0:
                    td.text = "%.2f"%(f)
                    if f < 0.4:
                        td.attrib["class"]="error"
                    elif f < 0.6:
                        td.attrib["class"]="warn"
            else:
                td = ET.SubElement(tr,'td')
                td = ET.SubElement(tr,'td')
            if isim > 0:
                f = p.entropies[isim-1]
                td = ET.SubElement(tr,'td')
                if f >= 0:
                    td.text = "%.2f"%(f)
                    if f < 0.4:
                        td.attrib["class"]="error"
                    elif f < 0.6:
                        td.attrib["class"]="warn"
            else:
                td = ET.SubElement(tr,'td')
            if p.isequil:
                td = ET.SubElement(tr,'td')
            else:
                td = ET.SubElement(tr,'td',attrib={'class':'error'})
                td.text = "No"
    return table


def GetReplExchTable( trial: Trial ) -> ET.Element:
    from . Names import GetHtmlSymbolFromObj
    name = GetHtmlSymbolFromObj(trial)
    data = GetReplExchData( trial )
    eles = None
    if data is not None:
        title_p = ET.Element('p',attrib={'style':"text-align:center;"})
        title_1 = ET.SubElement(title_p,'span',attrib={'style':"font-weight:bold;"})
        title_2 = ET.SubElement(title_p,'br')
        title_3 = ET.SubElement(title_p,'span')
        title_1.text = f"Hamiltonian replica exchange neighbor acceptance ratio (AR) for {name}. "
        title_3.text = f" Average single pass num. steps: {data['Average single pass steps:']:.1f}. Round trips/replica: {data['Round trips per replica:']:.1f}. Total num. round trips: {data['Total round trips:']:.1f}"
        table = ET.Element('table',attrib={'class':"simprop"})
        tr = ET.SubElement(table,'tr',attrib={'class':'ul'})
        th = ET.SubElement(tr,'th')
        th.text = "&lambda;"
        th = ET.SubElement(tr,'th')
        th.text = "AR (fwd)"
        for i,lam in enumerate(trial.ene[:-1]):
            tr = ET.SubElement(table,'tr')
            td = ET.SubElement(tr,'td')
            td.text = lam
            td = ET.SubElement(tr,'td')
            td.text = "%.2f"%( data['neighbor_acceptance_ratio'][i] )
        eles = [ title_p, table ]
    return eles


def GetReplExchEdgeStats( edge: Edge ) -> dict:
    import numpy as np
    
    data = {}
    for key in ["tgt","ref"]:
        data[key] = {}
        for e in ["spsmax","spsavg","spsstd",
                  "rtprmin","rtpravg","rtprstd",
                  "tnrtmin","tnrtavg","tnrtstd"]:
            data[key][e] = None

    envs = edge.GetEnvs()
    for env in envs:
        key = "tgt"
        if "ref" in env.name:
            key = "ref"
        spsteps = []
        nrtripsper = []
        trtrips = []
        for stage in env.stages:
            for trial in stage.trials:
                d = GetReplExchData(trial)
                if d is None:
                    continue
                spsteps.append( d['Average single pass steps:'] )
                nrtripsper.append( d['Round trips per replica:'] )
                trtrips.append( d['Total round trips:'] )
        if len(spsteps) > 0:
            data[key]["spsmax"] = np.amax(spsteps)
            data[key]["spsavg"] = np.mean(spsteps)
            ddof=0
            if len(spsteps) > 1:
                ddof=1
            data[key]["spsstd"] = np.std(spsteps,ddof=ddof)
        if len(nrtripsper) > 0:
            data[key]["rtprmin"] = np.amin(nrtripsper)
            data[key]["rtpravg"] = np.mean(nrtripsper)
            ddof=0
            if len(nrtripsper) > 1:
                ddof=1
            data[key]["rtprstd"] = np.std(nrtripsper,ddof=ddof)
        if len(trtrips) > 0:
            data[key]["tnrtmin"] = np.amin(trtrips)
            data[key]["tnrtavg"] = np.mean(trtrips)
            ddof=0
            if len(trtrips) > 1:
                ddof=1
            data[key]["tnrtstd"] = np.std(trtrips,ddof=ddof)
    return data

                
            
                

                                                  
def GetTIComparisonTable( trial: Union[Edge,Env,Stage,Trial],
                          results: Results,
                          ddG=False ) -> ET.Element:
    res = trial.GetTIValuesAndErrors()
    table = None
    if res is not None:

        v,e = trial.GetValueAndError(results.prod)
        
        table = ET.Element('table',attrib={'class':"simprop"})
        tr = ET.SubElement(table,'tr',attrib={'class':'ul'})
        th = ET.SubElement(tr,'th')
        th.text = "Method"
        th = ET.SubElement(tr,'th')
        if not ddG:
            th.text = "&Delta;G"
        else:
            th.text = "&Delta;&Delta;G"
            
        th = ET.SubElement(tr,'th')
        if not ddG:
            th.text = "&Delta;G-" + trial.GetMode()
        else:
            th.text = "&Delta;&Delta;G-" + trial.GetMode()

        th = ET.SubElement(tr,'th')
        th.text = "T"

        a,b = res["Linear"]
        d = a-v
        dd = np.sqrt( e*e + b*b )
        t = abs(d)/dd
        
        tr = ET.SubElement(table,'tr')
        td = ET.SubElement(tr,'td')
        td.text = "Linear Interp."
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(a,b)
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(d,dd)
        td = ET.SubElement(tr,'td')
        td.text = "%.3f"%(t)
    
        
        a,b = res["Natural"]
        d = a-v
        dd = np.sqrt( e*e + b*b )
        t = abs(d)/dd
        
        tr = ET.SubElement(table,'tr')
        td = ET.SubElement(tr,'td')
        td.text = "Natural Cubic"
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(a,b)
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(d,dd)
        td = ET.SubElement(tr,'td')
        td.text = "%.3f"%(t)


        a,b = res["Clamped"]
        d = a-v
        dd = np.sqrt( e*e + b*b )
        t = abs(d)/dd
        
        tr = ET.SubElement(table,'tr')
        td = ET.SubElement(tr,'td')
        td.text = "Clamped Cubic"
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(a,b)
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(d,dd)
        td = ET.SubElement(tr,'td')
        td.text = "%.3f"%(t)


        if "USub" in res:
            a,b = res["USub"]
            d = a-v
            dd = np.sqrt( e*e + b*b )
            t = abs(d)/dd
        
            tr = ET.SubElement(table,'tr')
            td = ET.SubElement(tr,'td')
            td.text = "USub"
            td = ET.SubElement(tr,'td')
            td.text = "%.3f &plusmn; %.3f"%(a,b)
            td = ET.SubElement(tr,'td')
            td.text = "%.3f &plusmn; %.3f"%(d,dd)
            td = ET.SubElement(tr,'td')
            td.text = "%.3f"%(t)

        
        tr = ET.SubElement(table,'tr')
        td = ET.SubElement(tr,'td')
        td.text = trial.GetMode()
        td = ET.SubElement(tr,'td')
        td.text = "%.3f &plusmn; %.3f"%(v,e)
        td = ET.SubElement(tr,'td')
        td = ET.SubElement(tr,'td')

        
    return table


def GetResetFormsScript():
    
    s = ET.Element("script",attrib={'type':'text/javascript'})
    s.text = ("function resetForms() {\n"
              "document.getElementById('NodeChartX-input').reset();\n"
              "document.getElementById('NodeChartY-input').reset();\n"
              "document.getElementById('EdgeChartX-input').reset();\n"
              "document.getElementById('EdgeChartY-input').reset();\n"
              "document.getElementById('ncolor-input').reset();\n"
              "document.getElementById('ecolor-input').reset();\n"
              "document.getElementById('esize-input').reset();\n"
              "document.getElementById('data-input').reset();\n"
              "}\n\n"
              
              "window.onload = function() {\n"
              "resetForms();\n"
              "}\n\n")
    return s

def GetObFcnHtml(self):
    import numpy as np
    from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj
    res = None
    if self.results is not None:
        if self.results.conobj is not None and self.results.con is not None:
            res = []
            p = self.results.conobj
            odata = np.zeros( (len(self.results.con),2) )
            odata[:,0] = [ con.conval for con in self.results.con ]
            odata[:,1] = [ con.chisq - p.f0 for con in self.results.con ]
            minx = np.amin( odata[:,0] )
            maxx = np.amax( odata[:,0] )
            n = 21
            fdata = np.zeros( (n,3) )
            fdata[:,0] = np.linspace(minx,maxx,n)
            fdata[:,1] = p.c2*(fdata[:,0]-p.q0)**2
            fdata[:,2] = fdata[:,1] + p.c3*(fdata[:,0]-p.q0)**3
            miny   = min( np.amin(fdata[:,1:3]), np.amin(odata[:,1]) )
            maxy   = max( np.amax(fdata[:,1:3]), np.amax(odata[:,1]) )
            ddx    = (maxx-minx)*0.05
            minx  -= ddx
            maxx  += ddx
            ddy    = (maxy-miny)*0.05
            miny  -= ddy
            maxy  += ddy
            name   = "chi_" + GetHtmlIdFromObj(self)
            colors = '["#09204e","#b00b13","#09bfb8"]'
            odstr  = "[" + ",".join(["[" + ",".join(["%14.5e"%(x) for x in row]) + "]" for row in odata ]) + "]"
            fdstr  = "[" + ",".join(["[" + ",".join(["%14.5e"%(x) for x in row]) + "]" for row in fdata ]) + "]"
            
            s = ET.Element("script",attrib={'type':'text/javascript'})
            s.text = (f"function {name}() {{ "
                      f"chichart( \"{name}\", {colors}, {minx}, {maxx}, "
                      f"{miny}, {maxy}, {odstr}, {fdstr} ); }}; "
                      f"google.charts.setOnLoadCallback({name});")
            res.append(s)
            
            div = ET.Element("div",attrib={'class':'timeseries'})
            table = ET.SubElement(div,'table',attrib={'class':'timeseries'})
            tr = ET.SubElement(table,'tr')
            th = ET.SubElement(tr,'th')
            span = ET.SubElement(th,'span').text = GetHtmlSymbolFromObj(self)
            br = ET.SubElement(th,'br')
            span = ET.SubElement(th,'span').text = "Shifted Edge Objective Function (kcal/mol)"
            tr = ET.SubElement(table,'tr')
            td = ET.SubElement(tr,'td',attrib={'id':name})
            res.append(div)

            d = ET.Element('div')
            h = ET.SubElement(d,'p').text = "The objective function polynomial fit is of the form:"
            h = ET.SubElement(d,'p').text = "F(x) = c0 + c2*(x-x0)^2 + c3*(x-x0)^3"
            h = ET.SubElement(d,'p').text = "where x0=%12.10e c0=%12.10e c2=%12.10e c3=%12.10e. The plot excludes the c0 term."\
                %(p.q0,p.f0,p.c2,p.c3)
            h = ET.SubElement(d,'p').text = "A cubic fit produces a Pearson correlation of %.5f."%(p.Rcub) 
            h = ET.SubElement(d,'p').text = "A quadratic fit produces a Pearson correlation of %.5f."%(p.Rquad) 
            res.append(d)

    return res
                      


def GetLigandImages(edge,imgdir):
    from pathlib import Path
    import io
    import base64
    import xml.etree.ElementTree as ET
    from PIL import Image
    
    imgtable = None
    base_width = 400

    try:
        lig1,lig2 = edge.split("~")
    except ValueError:
        raise ValueError(f"Bad edge name: {edge.name}. There should always be a '~' and there should be text on either side of the tilde describing the states.")

    f1 = Path("%s/%s_%s.png"%(imgdir,edge,lig1))
    f2 = Path("%s/%s_%s.png"%(imgdir,edge,lig2))
    if f1.exists():
        #
        # LIGAND 1
        #
        img = Image.open(str(f1))
        wpercent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((base_width, hsize), Image.Resampling.LANCZOS)
        imgstr = io.BytesIO()
        img.save(imgstr,'PNG')
        img1 = base64.b64encode(imgstr.getvalue()).decode("utf-8").replace("\n", "")

        if f2.exists():
            #
            # LIGAND 2
            #
            img = Image.open(str(f2))
            wpercent = (base_width / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((base_width, hsize), Image.Resampling.LANCZOS)
            imgstr = io.BytesIO()
            img.save(imgstr,'PNG')
            img2 = base64.b64encode(imgstr.getvalue()).decode("utf-8").replace("\n", "")

        
        imgtable = ET.Element('table',attrib={'style': "border: 1px solid black; margin-left: auto; margin-right: auto;"})
        thead = ET.SubElement(imgtable,'thead')
        tr = ET.SubElement(thead,'tr')
        th = ET.SubElement(tr,'th')
        th.text = lig1
        th = ET.SubElement(tr,'th')
        th.text = lig2
        tr = ET.SubElement(thead,'tr')
        td = ET.SubElement(tr,'td')
        img = ET.SubElement(td,'img',attrib={'src': "data:image/%s;base64,%s"%("png",img1)})
        td = ET.SubElement(tr,'td')
        if f2.exists():
            img = ET.SubElement(td,'img',attrib={'src': "data:image/%s;base64,%s"%("png",img2)})
        
    return imgtable



def GetEdgeHtml( self: Edge, imgfmt: Optional[str] = None, options: Optional[dict] = None ) -> ET.Element:
    from collections import defaultdict as ddict
    from . Names import GetHtmlSymbol, GetHtmlId
    from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj
    from . TimeSeriesAnalysis import SimplifiedAutoEqAnalysis

    cats = { "S": "the phase-space overlap is small",
             "RE": "the reweighting entropy is small",
             "equil": "the simulations did not equilibrate",
             "psize": "there are too few statistically independent samples",
             "feq": "most of the simulation should be discarded",
             "pstride": "there is a large statistical inefficiency" }

    severity = { "S": 12, "RE": 10,
                 "equil": 8, "psize": 6, "feq": 4,
                 "pstride": 2 }

    if options is None:
        options = {}
        options["du_print_thresh"] = 1.0
        
    
    html = StartEdgeHtml( self.name )
    body = ET.SubElement(html,'body')
    div = ET.SubElement(body,'div', attrib={'class':"decomp"})
    div = ET.SubElement(div,'div', attrib={'class':"desc"})
    h1 = ET.SubElement(div,'h1')
    h1.text = self.name
    p = ET.SubElement(div,'p')

    ET.SubElement(p,'span').text = ("Results calculated with edgembar"+
                                    f" version {self.results.version}"+
                                    f" hash {self.results.hash}"+
                                    f" on {self.results.date} using "+
                                    "the command:")
    p = ET.SubElement(div,'p')
    ET.SubElement(p,'span',attrib={'class':"code"}).text \
        = self.results.command

    try:
        imgtable = GetLigandImages(self.name,options["imgdir"])
        if imgtable is not None:
            div.append(imgtable)
    except ValueError as e:
        raise e
    except Exception:
        # no ligand images
        pass
    
    
    p = ET.SubElement(div,'p')
    envs = self.GetEnvs()

        

    if True:    
        ret  = ""

        seen_objs = {}


        msgs = self.GetErrorMsgs()
        
        errs = [ m for m in msgs if m.iserr  ]
        nerr = len(errs)
        #errcats = ddict(list)
        #for msg in errs:
        #    errcats[msg.kind].append(msg)
        
        uerrs = ddict(None)
        for e in errs:
            if e.htmlsym in uerrs:
                if severity[e.kind] > severity[ uerrs[e.htmlsym].kind ]:
                    uerrs[e.htmlsym] = e
            else:
                uerrs[e.htmlsym] = e

        outliers = [ m for m in msgs if m.kind == "outlier" ]
        
        warns = [ m for m in msgs if not m.iserr and m.kind != "outlier" ]
        nwarn = len(warns)
        #warncats = ddict(list)
        #for msg in warns:
        #    warncats[msg.kind].append(msg)

        uwarns = ddict(None)
        for e in warns:
            if e.htmlsym in warns:
                if severity[e.kind] > severity[ uwarns[e.htmlsym].kind ]:
                    uwarns[e.htmlsym] = e
            else:
                uwarns[e.htmlsym] = e

        for e in uerrs:
            uwarns.pop(e,None)

        errcats = ddict(list)
        for name in uerrs:
            msg = uerrs[name]
            errcats[msg.kind].append(msg)
        
        warncats = ddict(list)
        for name in uwarns:
            msg = uwarns[name]
            warncats[msg.kind].append(msg)

        ET.SubElement(p,'span').text = \
            (f"There are a total of {nerr} errors "+
             f"and {nwarn} warnings. The most severe "+
             "errors (without repeats) are listed "+
             "below.")
        
        if nerr > 0:
            for cat in [ c for c in severity if c in errcats ]:
                p = ET.SubElement(div,'p')
                span = ET.SubElement(p,'span')
                span.text = "Errors reported because " + cats[cat] + ":"
                for msg in errcats[cat]:
                    divid = msg.divid
                    sym = msg.htmlsym
                    br = ET.SubElement(p,'br')
                    a = ET.SubElement(p,'a',
                                      attrib={'href':f"#{divid}",
                                              'class':"error"})
                    a.text = sym

        if nwarn > 0:
            for cat in [ c for c in severity if c in warncats ]:
                p = ET.SubElement(div,'p')
                span = ET.SubElement(p,'span')
                span.text = "Warnings reported because " + cats[cat] + ":"
                for msg in warncats[cat]:
                    divid = msg.divid
                    sym = msg.htmlsym
                    br = ET.SubElement(p,'br')
                    a = ET.SubElement(p,'a',
                                      attrib={'href':f"#{divid}",
                                              'class':"warn"})
                    a.text = sym

        if len(outliers) > 0:
            p = ET.SubElement(div,'p')
            span = ET.SubElement(p,'span')
            span.text = ("The following trials may be outliers because "+
                         "they differ from both the mean and median by "+
                         "more than 2 kcal/mol:")
            for msg in outliers:
                divid = msg.divid
                sym = msg.htmlsym
                br = ET.SubElement(p,'br')
                a = ET.SubElement(p,'a',
                                  attrib={'href':f"#{divid}",
                                          'class':"outlier"})
                a.text = sym



        res =  GetObFcnHtml(self)
        if res is not None:
            p = ET.SubElement(div,'p')
            for ele in res:
                p.append(ele)


                
                
        if len(envs) == 2:
            name = GetHtmlSymbolFromObj(self) #(None,None,None,None)
            divid = GetHtmlIdFromObj(self) #(self.name,None,None,None,None)
            seen_objs[name] = self
            div = ET.SubElement(body,'div', attrib={'class':"decomp",'id':divid})
            if self.timeseries is not None:
                for ele in self.timeseries.GetHtml(imgfmt):
                    div.append( ele )

            
            if len(self.cmpl.stages) > 1:
                cname = GetHtmlSymbolFromObj( self.cmpl )
                cid = GetHtmlIdFromObj( self.cmpl )
            elif len(self.cmpl.stages[0].trials) > 1:
                cname = GetHtmlSymbolFromObj(self.cmpl.stages[0])
                cid = GetHtmlIdFromObj(self.cmpl.stages[0])
            else:
                cname = GetHtmlSymbolFromObj(self.cmpl.stages[0].trials[0])
                cid = GetHtmlIdFromObj(self.cmpl.stages[0].trials[0])
            if len(self.solv.stages) > 1:
                sname = GetHtmlSymbolFromObj(self.solv)
                sid = GetHtmlIdFromObj(self.solv)
            elif len(self.solv.stages[0].trials) > 1:
                sname = GetHtmlSymbolFromObj(self.solv.stages[0])
                sid = GetHtmlIdFromObj(self.solv.stages[0])
            else:
                sname = GetHtmlSymbolFromObj(self.solv.stages[0].trials[0])
                sid = GetHtmlIdFromObj(self.solv.stages[0].trials[0])


            div = ET.SubElement(div,'div', attrib={'class':"desc"})
                
            p = ET.SubElement(div,'p')
            span = ET.SubElement(p,'span')
            span.text = (f"The relative free energy {name} is the " +
                "difference in complexed and solvated environments:")

            br = ET.SubElement(p,'br')
            b = ET.SubElement(p,'b')
            b.text = f"{name} = {cname} - {sname}"
            br = ET.SubElement(p,'br')
                
            a = ET.SubElement(p,'a',attrib={'href':f"#{cid}"})
            a.text = "Click here"
            span = ET.SubElement(p,'span')
            span.text = f" to see {cname}"
            br = ET.SubElement(p,'br')
                
            a = ET.SubElement(p,'a',attrib={'href':f"#{sid}"})
            a.text = "Click here"
            span = ET.SubElement(p,'span')
            span.text = f" to see {sname}"
            
            title = ET.SubElement(p,'p',
                                  attrib={'style':"text-align:center; font-weight:bold;"})
            title.text = "Decomposition of %s into environmental &Delta;G values"%(name)

                
            table = GetEdgeSummaryTable(self)
            p.append(table)

            table = GetTIComparisonTable( self, self.results, ddG=True )
            if table is not None:
                title = ET.SubElement(p,'p',attrib={'style':"text-align:center; font-weight:bold;"})
                title.text = f"Comparison of {name} {self.GetMode()} and TI results"
                p.append(table)
                
        # if self.timeseries is not None:
            
        #     if len(envs) == 2:
        #         for ele in self.timeseries.GetHtml(imgfmt):
        #             div.append( ele )
        #         name = self.timeseries.htmlsym
            
        #         seen_objs[name] = self
            
        #         if len(self.cmpl.stages) > 1:
        #             cname = self.cmpl.timeseries.htmlsym
        #             cid = self.cmpl.timeseries.divid
        #         elif len(self.cmpl.stages[0].trials) > 1:
        #             cname = self.cmpl.stages[0].timeseries.htmlsym
        #             cid = self.cmpl.stages[0].timeseries.divid
        #         else:
        #             cname = self.cmpl.stages[0].trials[0].timeseries.htmlsym
        #             cid = self.cmpl.stages[0].trials[0].timeseries.divid
        #         if len(self.solv.stages) > 1:
        #             sname = self.solv.timeseries.htmlsym
        #             sid = self.solv.timeseries.divid
        #         elif len(self.solv.stages[0].trials) > 1:
        #             sname = self.solv.stages[0].timeseries.htmlsym
        #             sid = self.solv.stages[0].timeseries.divid
        #         else:
        #             sname = self.solv.stages[0].trials[0].timeseries.htmlsym
        #             sid = self.solv.stages[0].trials[0].timeseries.divid

        #         div = ET.SubElement(div,'div', attrib={'class':"desc"})
                
        #         p = ET.SubElement(div,'p')
        #         span = ET.SubElement(p,'span')
        #         span.text = "The relative free energy %s is the " \
        #             "difference in complexed and solvated environments:"%\
        #             (GetHtmlSymbol(None,None,None,None))
        #         br = ET.SubElement(p,'br')
        #         b = ET.SubElement(p,'b')
        #         b.text = f"{name} = {cname} - {sname}"
        #         br = ET.SubElement(p,'br')
                
        #         a = ET.SubElement(p,'a',attrib={'href':f"#{cid}"})
        #         a.text = "Click here"
        #         span = ET.SubElement(p,'span')
        #         span.text = f" to see {cname}"
        #         br = ET.SubElement(p,'br')
                
        #         a = ET.SubElement(p,'a',attrib={'href':f"#{sid}"})
        #         a.text = "Click here"
        #         span = ET.SubElement(p,'span')
        #         span.text = f" to see {sname}"

        #         title = ET.SubElement(p,'p',
        #                 attrib={'style':"text-align:center; font-weight:bold;"})
        #         title.text = "Decomposition of %s into environmental &Delta;G values"%(GetHtmlSymbol(None,None,None,None))

                
        #         table = GetEdgeSummaryTable(self)
        #         p.append(table)

        # elif len(envs) == 2:
            
        #     div = ET.SubElement(body,'div', attrib={'class':"decomp"})
        #     div = ET.SubElement(div,'div',  attrib={'class':"desc"})
        #     p = ET.SubElement(div,'p')
            
        #     title = ET.SubElement(p,'p',
        #             attrib={'style':"text-align:center; font-weight:bold;"})
        #     title.text = "Decomposition of %s into &lang;&Delta;G&rang; values"%\
        #         (GetHtmlSymbol(None,None,None,None))
                
        #     table = GetEdgeSummaryTable(self)
        #     p.append(table)
            
        for env in envs:
            if len(env.stages) > 1 or len(envs) == 1:
                name = GetHtmlSymbolFromObj(env)
                divid = GetHtmlIdFromObj(env)
                seen_objs[name] = env
                div = ET.SubElement(body,'div',attrib={'class':'decomp','id':divid})
                if env.timeseries is not None:
                    for ele in env.timeseries.GetHtml(imgfmt):
                        div.append( ele )

                divids = []
                terms = []
                for s in env.stages:
                    if len(s.trials) > 1:
                        terms.append( GetHtmlSymbolFromObj(s) )
                        divids.append( GetHtmlIdFromObj(s) )
                    else:
                        terms.append(GetHtmlSymbolFromObj(s.trials[0]))
                        divids.append(GetHtmlIdFromObj(s.trials[0]))
                        
                ssum = " + ".join(terms)
                div = ET.SubElement(div,'div',attrib={'class':'desc'})
                p = ET.SubElement(div,'p')
                span = ET.SubElement(p,'span')
                span.text = f"The free energy {name} is the sum:"
                br = ET.SubElement(p,'br')
                b = ET.SubElement(p,'b')
                b.text = f"{name} = {ssum}"
                br = ET.SubElement(p,'br')
                                    
                for term,divid in zip(terms,divids):
                    a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
                    a.text = "Click here"
                    span = ET.SubElement(p,'span')
                    span.text = f" to see {term}"
                    br = ET.SubElement(p,'br')

                divids = []
                terms = []
                for obj in [self]:
                    tsym = GetHtmlSymbolFromObj(obj)
                    tid = GetHtmlIdFromObj(obj)
                    if tsym in seen_objs:
                        divids.append( tid )
                        terms.append( tsym )

                span = ET.SubElement(p,'span')
                span.text = (f"The free energy {name} was used in the "+
                             "calculation of the following quantities:")
                br = ET.SubElement(p,'br')

                for term,divid in zip(terms,divids):
                    a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
                    a.text = "Click here"
                    span = ET.SubElement(p,'span')
                    span.text = f" to see {term}"
                    br = ET.SubElement(p,'br')

                title = ET.SubElement(p,'p',
                                      attrib={'style':"text-align:center; font-weight:bold;"})
                title.text = f"Decomposition of {name} into stages"
                
                table = GetEnvSummaryTable(env)
                p.append(table)


                table = GetTIComparisonTable( env, self.results )
                if table is not None:
                    title = ET.SubElement(p,'p',attrib={'style':"text-align:center; font-weight:bold;"})
                    title.text = f"Comparison of {name} {env.GetMode()} and TI results"
                    p.append(table)
                
            # if self.timeseries is not None:
            #     if len(env.stages) > 1 or len(envs) == 1:
            #         for ele in env.timeseries.GetHtml(imgfmt):
            #             div.append( ele )
            #         name = env.timeseries.htmlsym
            #         seen_objs[name] = env
                
            #         divids = []
            #         terms = []
            #         for s in env.stages:
            #             if len(s.trials) > 1:
            #                 terms.append(s.timeseries.htmlsym)
            #                 divids.append(s.timeseries.divid)
            #             else:
            #                 terms.append(s.trials[0].timeseries.htmlsym)
            #                 divids.append(s.trials[0].timeseries.divid)
                        
            #         ssum = " + ".join(terms)
            #         div = ET.SubElement(div,'div',attrib={'class':'desc'})
            #         p = ET.SubElement(div,'p')
            #         span = ET.SubElement(p,'span')
            #         span.text = f"The free energy {name} is the sum:"
            #         br = ET.SubElement(p,'br')
            #         b = ET.SubElement(p,'b')
            #         b.text = f"{name} = {ssum}"
            #         br = ET.SubElement(p,'br')
                                    
            #         for term,divid in zip(terms,divids):
            #             a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
            #             a.text = "Click here"
            #             span = ET.SubElement(p,'span')
            #             span.text = f" to see {term}"
            #             br = ET.SubElement(p,'br')


            #         divids = []
            #         terms = []
            #         for obj in [self]:
            #             if obj.timeseries.htmlsym in seen_objs:
            #                 divids.append( obj.timeseries.divid )
            #                 terms.append( obj.timeseries.htmlsym )

            #         span = ET.SubElement(p,'span')
            #         span.text = (f"The free energy {name} was used in the "+
            #                      "calculation of the following quantities:")
            #         br = ET.SubElement(p,'br')

            #         for term,divid in zip(terms,divids):
            #             a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
            #             a.text = "Click here"
            #             span = ET.SubElement(p,'span')
            #             span.text = f" to see {term}"
            #             br = ET.SubElement(p,'br')

            #         title = ET.SubElement(p,'p',
            #                 attrib={'style':"text-align:center; font-weight:bold;"})
            #         title.text = f"Decomposition of {name} into stages"
                
            #         table = GetEnvSummaryTable(env)
            #         p.append(table)

            # if len(env.stages) > 1 or len(envs) == 1:
            #     div = ET.SubElement(div,'div',attrib={'class':'desc'})
            #     name = GetHtmlSymbol(env.name,None,None,None)
            #     p = ET.SubElement(div,'p')

            #     title = ET.SubElement(p,'p',
            #                 attrib={'style':"text-align:center; font-weight:bold;"})
            #     title.text = f"Decomposition of {name} into stages"
                
            #     table = GetEnvSummaryTable(env)
            #     p.append(table)
            

        for env in envs:
            for stage in env.stages:
                if len(stage.trials) > 1:
                    name = GetHtmlSymbolFromObj(stage)
                    divid = GetHtmlIdFromObj(stage)
                    seen_objs[name] = stage
                    div = ET.SubElement(body,'div', attrib={'class':"decomp",'id':divid})
                    if stage.timeseries is not None:
                        for ele in stage.timeseries.GetHtml(imgfmt):
                            div.append( ele )
                            
                    divids = []
                    terms = []
                    for t in stage.trials:
                        terms.append(GetHtmlSymbolFromObj(t))
                        divids.append(GetHtmlIdFromObj(t))

                    ssum = " + ".join(terms)
                    div = ET.SubElement(div,'div',attrib={'class':'desc'})
                    p = ET.SubElement(div,'p')
                    span = ET.SubElement(p,'span')
                    span.text = f"The free energy {name} is the average:"
                    br = ET.SubElement(p,'br')
                    b = ET.SubElement(p,'b')
                    n = len(stage.trials)
                    b.text = f" {name} = (1/{n}) [ {ssum} ]"
                    br = ET.SubElement(p,'br')
                    
                    for term,divid in zip(terms,divids):
                        a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
                        a.text = "Click here"
                        span = ET.SubElement(p,'span')
                        span.text = f" to see {term}"
                        br = ET.SubElement(p,'br')


                    divids = []
                    terms = []
                    for obj in [self,env]:
                        tsym = GetHtmlSymbolFromObj(obj)
                        tid = GetHtmlIdFromObj(obj)
                        if tsym in seen_objs:
                            divids.append( tid )
                            terms.append( tsym )
                            
                    span = ET.SubElement(p,'span')
                    span.text = (f"The free energy {name} was used in the "+
                                 "calculation of the following quantities:")
                        
                    for term,divid in zip(terms,divids):
                        br = ET.SubElement(p,'br')
                        a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
                        a.text = "Click here"
                        span = ET.SubElement(p,'span')
                        span.text = f" to see {term}"


                    title = ET.SubElement(p,'p',
                                          attrib={'style':"text-align:center; font-weight:bold;"})
                    title.text = f"Decomposition of {name} into trials"
                    table = GetStageSummaryTable(stage)
                    p.append(table)

                    table = GetTIComparisonTable( stage, self.results )
                    if table is not None:
                        title = ET.SubElement(p,'p',attrib={'style':"text-align:center; font-weight:bold;"})
                        title.text = f"Comparison of {name} {stage.GetMode()} and TI results"
                        p.append(table)

                        figeles = GetMultiDVDLHtml(stage)
                        if figeles is not None:
                            p.extend(figeles)
                
                        figeles = GetMultiARHtml(stage)
                        if figeles is not None:
                            p.extend(figeles)
                
        # for env in envs:
        #     for stage in env.stages:
        #         if self.timeseries is not None:
        #             if len(stage.trials) > 1:
        #                 div = ET.SubElement(body,'div', attrib={'class':"decomp"})

        #                 for ele in stage.timeseries.GetHtml(imgfmt):
        #                     div.append( ele )

        #                 name = stage.timeseries.htmlsym
        #                 seen_objs[name] = stage
        #                 divids = []
        #                 terms = []
        #                 for t in stage.trials:
        #                     terms.append(t.timeseries.htmlsym)
        #                     divids.append(t.timeseries.divid)

        #                 ssum = " + ".join(terms)
        #                 div = ET.SubElement(div,'div',attrib={'class':'desc'})
        #                 p = ET.SubElement(div,'p')
        #                 span = ET.SubElement(p,'span')
        #                 span.text = f"The free energy {name} is the average:"
        #                 br = ET.SubElement(p,'br')
        #                 b = ET.SubElement(p,'b')
        #                 n = len(stage.trials)
        #                 b.text = f" {name} = (1/{n}) [ {ssum} ]"
        #                 br = ET.SubElement(p,'br')

        #                 for term,divid in zip(terms,divids):
        #                     a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
        #                     a.text = "Click here"
        #                     span = ET.SubElement(p,'span')
        #                     span.text = f" to see {term}"
        #                     br = ET.SubElement(p,'br')


        #                 divids = []
        #                 terms = []

        #                 for obj in [self,env]:
        #                     if obj.timeseries is not None:
        #                         if obj.timeseries.htmlsym in seen_objs:
        #                             divids.append( obj.timeseries.divid )
        #                             terms.append( obj.timeseries.htmlsym )
        #                 span = ET.SubElement(p,'span')
        #                 span.text = (f"The free energy {name} was used in the "+
        #                              "calculation of the following quantities:")
                        
        #                 for term,divid in zip(terms,divids):
        #                     br = ET.SubElement(p,'br')
        #                     a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
        #                     a.text = "Click here"
        #                     span = ET.SubElement(p,'span')
        #                     span.text = f" to see {term}"


        #                 title = ET.SubElement(p,'p',
        #                                       attrib={'style':"text-align:center; font-weight:bold;"})
        #                 title.text = "Decomposition of %s into trials"%(GetHtmlSymbol(env.name,stage.name,None,None))
                
                            
        #                 table = GetStageSummaryTable(stage)
        #                 p.append(table)
        #         elif len(stage.trials) > 1:
        #             div = ET.SubElement(body,'div', attrib={'class':"decomp"})
        #             div = ET.SubElement(div,'div',attrib={'class':'desc'})
        #             p = ET.SubElement(div,'p')
                
        #             title = ET.SubElement(p,'p',
        #                                   attrib={'style':"text-align:center; font-weight:bold;"})
        #             title.text = "Decomposition of %s into trials"%\
        #                 (GetHtmlSymbol(env.name,stage.name,None,None))
                
        #             table = GetStageSummaryTable(stage)
        #             p.append(table)  



        for env in envs:
            for stage in env.stages:
                for trial in stage.trials:
                    name = GetHtmlSymbolFromObj(trial)
                    divid = GetHtmlIdFromObj(trial)
                    seen_objs[name] = trial
                    div = ET.SubElement(body,'div', attrib={'class':"decomp",'id':divid})
                    if trial.timeseries is not None:
                        for ele in trial.timeseries.GetHtml(imgfmt):
                            div.append( ele )
                            

                    divids = []
                    terms = []
                    for obj in [self,env,stage]:
                        tid = GetHtmlIdFromObj(obj)
                        tsym = GetHtmlSymbolFromObj(obj)
                        if tsym in seen_objs:
                            divids.append( tid )
                            terms.append( tsym )

                    div = ET.SubElement(div,'div',attrib={'class':'desc'})
                    p = ET.SubElement(div,'p')
                    span = ET.SubElement(p,'span')
                    span.text = (f"The free energy {name} was used in the "+
                                 "calculation of the following quantities:")
                    br = ET.SubElement(p,'br')

                    for term,divid in zip(terms,divids):
                        a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
                        a.text = "Click here"
                        span = ET.SubElement(p,'span')
                        span.text = f" to see {term}"
                        br = ET.SubElement(p,'br')

                    ele = p
                    p = ET.SubElement(ele,'p',attrib={'style':"text-align:center; font-weight:bold;"})
                    p.text = name
                    table = GetTrialSummaryTable( trial, self.results, options )
                    ele.append(table)
                    table = GetTIComparisonTable( trial, self.results )
                    if table is not None:
                        p = ET.SubElement(ele,'p',attrib={'style':"text-align:center; font-weight:bold;"})
                        p.text = f"Comparison of {name} {trial.mode} and TI results"
                        ele.append(table)
                        figeles = GetDVDLHtml(trial)
                        if figeles is not None:
                            ele.extend(figeles)
                    table = GetReplExchTable( trial )
                    if table is not None:
                        ele.extend(table)
                        
                    
        for env in envs:
            for stage in env.stages:
                for trial in stage.trials:
                    for iene in range(len(trial.ene)):

                        p = trial.results[iene]
                        if p is not None:
                            f = p.pstart/p.osize

                            if options["du_print_thresh"] >= 0:
                                prtsim = f >= options["du_print_thresh"]
                            else:
                                prtsim = not p.isequil
            

                            
                            if prtsim:
                                if True:
                                    name = GetHtmlSymbolFromObj(trial,istate=iene,sym="U")
                                    divid = GetHtmlIdFromObj(trial,istate=iene,sym="U")
                                    div = ET.SubElement(body,'div', attrib={'class':"decomp",'id':divid})
                                    eqana = SimplifiedAutoEqAnalysis(trial,iene)
                                    #if eqana is not None:
                                    for ele in eqana.GetHtml(imgfmt):
                                        div.append( ele )
                            

        return html



def StartEdgeHtml( title: str ) -> ET.Element:
    
    html = ET.Element('html', attrib={'lang':'en'})
    
    head = ET.SubElement(html,'head')
    
    ET.SubElement(head,'title').text = title
    
    ET.SubElement(head,'meta',
                  attrib={ 'http-equiv': "content-type",
                           'content': "text/html; charset=utf-8" })

    head.append( GetGoogleChartsScript() )
    head.append( GetTimeseriesChartScript() )
    head.append( GetEdgeCSS() )
    
    return html


def WriteEdgeHtmlFile( self,
                       fname: str,
                       imgfmt: Optional[str] = None,
                       options: Optional[dict] = None ) -> None:
        
    import xml.etree.ElementTree as ET
    import html as HTML
    import xml.dom.minidom as md
    import os

    fh = open(fname,"w")
    html = GetEdgeHtml(self,imgfmt=imgfmt,options=options)
    fh.write( HTML.unescape( ET.tostring(html,encoding="unicode",
                                         method='html') ) )
    fh.close()

    

# =============================================================
# =============================================================


def StartGraphHtml() -> ET.Element:
    
    html = ET.Element('html', attrib={'lang':'en'})
    
    head = ET.SubElement(html,'head')
    
    ET.SubElement(head,'title').text = "Graph Analysis"
    
    ET.SubElement(head,'meta',
                  attrib={ 'http-equiv': "content-type",
                           'content': "text/html; charset=utf-8" })

    head.append( GetGraphCSS() )
    head.append( GetGoogleChartsScript() )
    head.append( GetVisNetworkScript() )
    head.append( GetSeleRowScript() )
    head.append( GetResetFormsScript() )
    s = ET.SubElement(head,"script",attrib={'type':"text/javascript"})
    s.text = "\ngoogle.charts.load('current', {'packages':['corechart']});\n"
    return html


def WriteGraphHtmlFile( self : Graph,
                        fname: str,
                        node_values : List[float],
                        node_errors : List[float],
                        edge_lagmult : List[float],
                        expt : Optional[str] = None ) -> None:
        
    import xml.etree.ElementTree as ET
    import html as HTML
    import xml.dom.minidom as md
    import os
    import numpy as np

    fh = open(fname,"w")
    html = GetGraphHtml(self,node_values,node_errors,edge_lagmult,expt=expt)
    fh.write( HTML.unescape( ET.tostring(html,encoding="unicode",
                                         method='html') ) )
    fh.close()



def GetSortTable(data,headings,cfmts,cidxs):
    import xml.etree.ElementTree as ET
    table = ET.Element('table')
    thead = ET.SubElement(table,'thead')
    tr = ET.SubElement(thead,'tr')
    for icol in cidxs:
        heading = headings[icol]
        numNone = len( [ 1 for row in data if row[icol] is None ] )
        th = ET.SubElement(tr,'th')
        ET.SubElement(th,'span').text = heading + " "
        if numNone == 0:
            ET.SubElement(th,'span').text = '&uarr;'
    tbody = ET.SubElement(table,'tbody')
    for row in data:
        tr = ET.SubElement(tbody,'tr',attrib={'id':f"row_{row[0]}",
                                              'onclick':row[1]})
        for i in cidxs:
            td = ET.SubElement(tr,'td')
            islink = False
            if i == 0:
                #print(i,row[i],row[i].split("~"),len(row[i].split("~")))
                numNodes = len(row[i].split("~"))
                if numNodes == 2:
                    islink = True
            if islink:
                link = ET.SubElement(td,'a',attrib={
                    "href":f"{row[i]}.html",
                    "target":"_blank"
                })
                link.text = '{0:{1}}'.format(row[i],cfmts[i])
            else:
                if row[i] is not None:
                    td.text = '{0:{1}}'.format(row[i],cfmts[i])
                else:
                    td.text = ""
    pres = {}
    for icol in cidxs:
        if icol > 0:
            vs = np.array([row[icol] for row in data if row[icol] is not None])
            stddev = 0
            minval = 0
            maxval = 0
            meanval = 0
            meanabsval = 0
            if vs.shape[0] > 1:
                stddev = np.std(vs,ddof=1)
            if vs.shape[0] > 0:
                meanval = np.mean(vs)
                meanabsval = np.mean(np.abs(vs))
                minval = np.amin(vs)
                maxval = np.amax(vs)
            pvals = { "N": vs.shape[0],
                      "Mean": meanval,
                      "MeanAbs": meanabsval,
                      "StdDev": stddev,
                      "Min": minval,
                      "Max": maxval }
            if cfmts[icol] == "d":
                for x in pvals:
                    pvals[x] = int(pvals[x])
            pres[icol] = pvals
                    
    thead = ET.SubElement(table,'thead')
    for prop in ["N","Mean","MeanAbs","StdDev","Min","Max"]:
        tr = ET.SubElement(thead,'tr')
        th = ET.SubElement(tr,'th').text = prop
        for icol in cidxs:
            if icol > 0:
                x = pres[icol][prop]
                if prop == "N":
                    ET.SubElement(tr,'th').text = str(x)
                else:
                    if "f" not in cfmts[icol] and "e" not in cfmts[icol]:
                        ET.SubElement(tr,'th').text = \
                            "%i"%(x)
                    else:
                        ET.SubElement(tr,'th').text = \
                            '{0:{1}}'.format(x,cfmts[icol])
    return table


def HeadingIsDirectionDep(heading):
    return heading == "CFE" or heading == "UFE" or \
        heading == "Expt" or heading == "CFE-Expt"


def HeadingIdxsWithDirectionDeps(headings,cidxs):
    idxs = []
    for ii,idx in enumerate(cidxs):
        if HeadingIsDirectionDep(headings[idx]):
            idxs.append(ii)
    return idxs


def GetRegresScript(dtype,data,headings,cfmts,cidxs):
    import xml.etree.ElementTree as ET
    s = ET.Element('script',attrib={'type':'text/javascript'})
    s.text = (f"\n\nvar Glb{dtype}TblRow=0;\n"
              f"var Glb{dtype}TblCol=0;\n"
              f"function draw{dtype}Tbl() {{\n"
	      f"var Glb{dtype}Tbl = new google.visualization.DataTable();\n")
    for i in cidxs:
        s.text += f"Glb{dtype}Tbl.addColumn('number','{headings[i]}');\n"
    s.text += (f"Glb{dtype}Tbl.addColumn( {{ type: 'string', "
               f"label: '{dtype}', role: 'tooltip' }});\n")
    rows = []
    for row in data:
        cols = []
        for i in cidxs:
            if row[i] is not None:
                cols.append( '{0:{1}}'.format(row[i],cfmts[i]) )
            else:
                cols.append( 'null' )
        cols.append( f"'{row[0]}'" )
        rows.append( "[" + ",".join(cols) + "]" )
    dstr = "[" + ",\n".join( rows ) + "]"
    s.text += f"var idata = {dstr};\n"
    s.text += "var odata = idata.map(function(arr) { return arr.slice(); });\n"

    ###########################################################################################
    ## THIS MESSES WITH THE SIGN OF EDGE PROPERTIES IF THE PROPERTY IS DIRECTION-DEPENDENT
    if dtype == "Edge":
        s.text += "var dirdepidxs = [ %s ];\n"%(",".join(["%i"%(x)
                            for x in HeadingIdxsWithDirectionDeps(headings,cidxs)]))
        s.text += f"var rowdep = dirdepidxs.includes(Glb{dtype}TblRow);\n"
        s.text += f"var coldep = dirdepidxs.includes(Glb{dtype}TblCol);\n"
        s.text += ("if ( rowdep && coldep ) {\n"
                   "   for ( var i=0; i<odata.length; i++ ) {\n"
                   f"     if ( odata[i][Glb{dtype}TblRow] != null ) {{\n"
                   f"        if ( odata[i][Glb{dtype}TblRow] < 0 ) {{\n"
                   f"           odata[i][Glb{dtype}TblRow] *= -1;\n"
                   f"              if ( Glb{dtype}TblRow != Glb{dtype}TblCol ) {{\n"
                   f"                 if ( odata[i][Glb{dtype}TblCol] != null ) {{\n"
                   f"                    odata[i][Glb{dtype}TblCol] *= -1;\n"
                   "                  };\n"
                   "}}}}} else if ( rowdep ) {\n"
                   "  for ( var i=0; i<odata.length; i++ ) {\n"
                   f"   if ( odata[i][Glb{dtype}TblRow] != null ) {{\n"
                   f"      odata[i][Glb{dtype}TblRow] = Math.abs(odata[i][Glb{dtype}TblRow]);\n"
                   "}}} else if ( coldep ) {\n"
                   "  for ( var i=0; i<odata.length; i++ ) {\n"
                   f"   if ( odata[i][Glb{dtype}TblCol] != null ) {{\n"
                   f"      odata[i][Glb{dtype}TblCol] = Math.abs(odata[i][Glb{dtype}TblCol]);\n"
                   "}}};\n")
    ###########################################################################################
    
    s.text += f"Glb{dtype}Tbl.addRows(odata);\n"
    s.text += (f"var view = new google.visualization.DataView(Glb{dtype}Tbl);\n"
	       f"view.setColumns( [Glb{dtype}TblRow,Glb{dtype}TblCol,{len(cidxs)}] )\n"
	       "var options = { interpolateNulls: false,\n"
	       "hAxis: { title: view.getColumnLabel(0),\n"
	       "titleTextStyle: { italic: false } },\n"
	       "vAxis: { title: view.getColumnLabel(1),\n"
	       "titleTextStyle: { italic: false } },\n"
	       "lineWidth: 2,pointSize: 0,\n"
	       "chartArea: { left: 55, top: 10, bottom: 50, right: 10,\n"
	       "width: \"100%\", height: \"100%\" },\n"
	       "series:{0:{color:'#000000',lineWidth:0,pointSize:6,"
               "visibleInLegend:false}},\n"
	       "trendlines:{0:{type: 'linear',showR2:true,"
               "visibleInLegend:false,opacity:0.25}},\n"
               "width: 440,height: 440};\n"	  
	       "var chart = new google.visualization.LineChart("
               f"document.getElementById('{dtype}Chart'));\n"
	       "chart.draw(view, options);\n"
	       "google.visualization.events.addListener(chart,'select',function(){\n"
	       "var selectedItem = chart.getSelection()[0];\n"
	       "if (selectedItem) {\n"
	       "var tooltip = view.getValue(selectedItem.row, 2);\n"
	       f"sele{dtype}(tooltip);\n"
               "seleRow(\"row_\" + tooltip);\n"
	       "}});\n"
               f"document.querySelectorAll('.regres-{dtype}').forEach(function(elem){{\n"
               "elem.style.display='none';});\n"
	       f"let tableId=\"regres-{dtype}-\" + view.getColumnLabel(0) + "
               "\"-\" + view.getColumnLabel(1);\n"
	       "let ele = document.getElementById(tableId);\n"
	       "if ( ele != undefined ) {\n"
               "ele.style.display='block';\n"
	       "}};\n"
               f"google.charts.setOnLoadCallback(draw{dtype}Tbl);\n\n")
    return s
    
def GetRegresTables(dtype,data,headings,cidxs):
    import xml.etree.ElementTree as ET
    from scipy.stats import linregress
    import numpy as np
    tps = ["N","R","R^2","MAD","MSD","RMSD","m","b"]
    tables = []
    for irow in cidxs:
        hrow = headings[irow]
        rowdep = HeadingIsDirectionDep(hrow) and dtype == "Edge"
        for icol in cidxs:
            hcol = headings[icol]
            coldep = HeadingIsDirectionDep(hcol) and dtype == "Edge"
            cls = f"regres-{dtype}"
            name = f"{cls}-{hrow}-{hcol}"
            div = ET.Element('div',attrib={'id':name,'class':cls})
            xs=[]
            ys=[]
            for i in range(len(data)):
                x = data[i][irow]
                y = data[i][icol]
                if x is not None and y is not None:
                    xs.append(x)
                    ys.append(y)
            xs = np.array(xs)
            ys = np.array(ys)
            N = len(xs)

            ################################################
            ## THIS MESSES WITH THE SIGN OF EDGE PROPERTIES
            if rowdep and coldep:
                for i in range(N):
                    if xs[i] < 0:
                        xs[i] *= -1
                        ys[i] *= -1
            elif rowdep:
                xs = np.abs(xs)
            elif coldep:
                ys = np.abs(ys)
            ################################################

            ok=False
            if N > 0:
                if np.amax(xs) > np.amin(xs):
                    ok=True
                    m,b,R,P,stderr = linregress(xs,ys)
                    ds = ys-xs
                    msd = np.mean(ds)
                    mad = np.mean(np.abs(ds))
                    rmsd = np.sqrt(np.mean(ds*ds))
                    ps = [str(N),
                          "%.3f"%(R),"%.3f"%(R*R),
                          "%.3f"%(mad),"%.3f"%(msd),"%.3f"%(rmsd),
                          "%.3f"%(m),"%.3f"%(b)]
            if not ok:
                ps = ["0"] + ["na"] * 7
            t = ET.SubElement(div,'table')
            thead = ET.SubElement(t,"thead")
            tr = ET.SubElement(thead,"tr")
            for p in tps:
                ET.SubElement(tr,"th").text = p
            tbody = ET.SubElement(t,"tbody")
            tr = ET.SubElement(tbody,"tr")
            for p in ps:
                ET.SubElement(tr,"td").text = p
            tables.append(div)
    return tables


def GetRegresInput(dtype,headings,cidxs):
    import xml.etree.ElementTree as ET
    pinps = ET.Element("div",attrib={"class":"pair-inputs"})
    for xy,rc in zip(["X","Y"],["Row","Col"]):
        name = f"{dtype}Chart{xy}"
        fset = ET.SubElement(pinps,"fieldset",attrib={'id':f"{name}-input"})
        ET.SubElement(fset,"legend").text = f"{dtype} {xy}:"
        for i,idx in enumerate(cidxs):
            h = headings[idx]
            onclick = f"Glb{dtype}Tbl{rc}={i}; draw{dtype}Tbl();"
            d = ET.SubElement(fset,"div")
            idname=f"{name}-{h}"
            inp = ET.SubElement(d,"input",
                    attrib={'type':'radio','id':idname,'name':name,
                            'onclick':onclick})
            if i == 0:
                inp.attrib['checked'] = "checked"
            ET.SubElement(d,"label",attrib={"for":idname}).text = h
    return pinps


def GetRegresDiv(dtype,data,headings,cidxs):
    import xml.etree.ElementTree as ET
    div = ET.Element("div",attrib={"class":"regres"})
    t = ET.SubElement(div,"table")
    thead = ET.SubElement(t,"thead")
    tr = ET.SubElement(thead,"tr")
    ET.SubElement(tr,"th").text = dtype
    tbody = ET.SubElement(t,"tbody")
    tr = ET.SubElement(tbody,"tr")
    ET.SubElement(tr,"td",attrib={'id':f"{dtype}Chart"})
    for table in GetRegresTables(dtype,data,headings,cidxs):
        div.append(table)
    div.append(GetRegresInput(dtype,headings,cidxs))

    return div


                
def GetGraphHtml( self: Graph,
                  node_values : List[float],
                  node_errors : List[float],
                  edge_lagmult : List[float],
                  expt : Optional[str] = None ) -> ET.Element:
    
    from collections import defaultdict as ddict
    import numpy as np
    #from . Names import GetHtmlSymbol, GetHtmlId
    #from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj


    html = StartGraphHtml()
    body = ET.SubElement(html,'body')
    main_grid      = ET.SubElement(body,'div', attrib={'id':"main-grid"})
    bottom_content = ET.SubElement(body,'div',attrib={'id':"bottom-content"})
    main_left      = ET.SubElement(main_grid,'div', attrib={'id':"main-left"})
    mynetwork      = ET.SubElement(main_left,'div', attrib={'id':"mynetwork"})
    main_right     = ET.SubElement(main_grid,'div',attrib={'id':"main-right"})
    

    ######################################################
    
    ncolor_input = ET.SubElement(main_right,'fieldset',
                                 attrib={'id':"ncolor-input"})
    ET.SubElement(ncolor_input,'legend').text = "Node color:"

    nprops = [ ("Default", "DEF", "def"),
               ("CFE", "CONFE", "confe"),
               ("AvgCC","AVGCC","avgcc"),
               ("AvgLMI","LMI","lmi") ]
    for iprop,prop in enumerate(nprops):
        div =  ET.SubElement(ncolor_input,'div')
        attrib = {'type':"radio",
                  'id':f"ncolorid-{prop[2]}",
                  'name':"ncolor",
                  'onclick':f"updateNodeColors('{prop[1]}')"}
        if iprop == 0:
            attrib["checked"]="checked"
        ET.SubElement(div,'input',attrib=attrib)
        ET.SubElement(div,'label',attrib=
                      {'for':f"ncolorid-{prop[2]}"}).text=prop[0]
    

    ######################################################
    
    right_bottom_inputs = ET.SubElement(main_right,'div',
                                        attrib={'id':"right-bottom-inputs"})
    
    
    eprops = [ ("Default", "DEF",     "def"),
               ("UFE",     "UNCONFE", "unconfe"),
               ("dUFE",    "UNCONERR","unconerr"),
               ("CFE",     "CONFE",   "confe"),
               ("dCFE",    "CONERR",  "conerr"),
               ("|Shift|",   "SHIFT",   "shiftfe"),
               ("AvgCC",   "AVGCC",   "avgcc"),
               ("MaxCC",   "MAXCC",   "maxcc"),
               ("LMI",     "LMI",     "lmi"),
               ("OFC2",    "OFC2",    "ofc2"),
               ("ErrMsgs", "ERR",     "err"),
               ("Outliers","OUT",     "out") ]


    for disp in ["color","size"]:
        Disp = disp.capitalize()
        fieldset = ET.SubElement(right_bottom_inputs,'fieldset',
                                 attrib={'id':f"e{disp}-input"})
        ET.SubElement(fieldset,'legend').text = f"Edge {disp}:"
        for iprop,prop in enumerate(eprops):
            attrib = {'type':"radio",
                      'id':f"e{disp}-{prop[2]}",
                      'name':f"e{disp}sele",
                      'onclick':f"updateEdge{Disp}s('{prop[1]}')"}
            if iprop == 0:
                attrib["checked"] = "checked"
            div = ET.SubElement(fieldset,'div')
            ET.SubElement(div,'input',attrib=attrib)
            ET.SubElement(div,'label',
                          attrib={'for':f"e{disp}-{prop[2]}"}).text=prop[0]

            
    ######################################################

            
    datainps = [ ("Hints", "tips","tip_table"),
                 ("Nodes", "node-data","node_data"),
                 ("Edges", "edge-data","edge_data"),
                 ("Cycles","cycle-data","cyc_data"),
                 ("TI","ti-data","ti_data"),
                 ("RepEx","repex-data","repex_data") ]
    
    fieldset = ET.SubElement(bottom_content,'fieldset',
                             attrib={'id':"data-input"})
    ET.SubElement(fieldset,'legend').text = "Property:"
    for iprop,prop in enumerate(datainps):
        attrib = {'type':"radio",
                  'id':prop[2],
                  'name':f"datasele",
                  'onclick':f"showTable('{prop[1]}'); seleRow();"}
        if iprop == 0:
            attrib["checked"] = "checked"
        div = ET.SubElement(fieldset,'div')
        ET.SubElement(div,'input',attrib=attrib)
        ET.SubElement(div,'label',
                      attrib={'for':prop[2]}).text=prop[0]

        
    ######################################################

        
    action_tips = [ ("Click canvas: ",      "Unselect"),
                    ("Hold-click canvas: ", "Translate graph"),
                    ("Click node: ",        "Select"),
                    ("Hold-click node: ",   "Move node"),
                    ("Scrollwheel: ",       "Zoom"),
                    ("Double-click edge: ", "Open link to edge details"),
                    ("Click property: ",    "Show data table / highlight all"),
                    ("Click table data: ",  "Highlight node, edge, or cycle"),
                    ("Click table header: ","Sort rows") ]

    abbrev_tips = [ ("CFE: ","Constrained net free energy (complexed-solvated) in kcal/mol."),
                    ("dCFE: ","Standard error of the constrained net free energy in kcal/mol."),
                    ("UFE: ","Unconstrained net free energy (complexed-solvated) in kcal/mol."),
                    ("dUFE: ","Standard error of the unconstrained net free energy in kcal/mol."),
                    ("CC: ","Cycle closure error of the unconstrained free energy in kcal/mol."),
                    ("MaxCC: ","Maximum CC for any cycle traversing this node or edge."),
                    ("AvgCC: ","Average CC for all cycles traversing this node or edge."),
                    ("|Shift|: ","The absolute change in energy |CFE-UFE| upon enforcing cycle closure contraints."),
                    ("LMI: ","Lagrange multiplier index (unitless)."),
                    ("AvgLMI: ","Average LMI of all edges connected to this node."),
                    ("OFC2: ","Twice the objective force constant in 1/(kcal/mol)."),
                    ("ErrMsgs: ","Number of errors reported by edge analysis."),
                    ("Outliers: ","Number of warnings reported by edge analysis."),
                    ("TI: ","Unconstrained TI free energy (kcal/mol) using trapezoidal rule integration"),
                    ("TI3n: ","Unconstrained TI free energy (kcal/mol) using natural cubic spline (zero 2nd derivative end-point conditions)"),
                    ("TI3c: ","Unconstrained TI free energy (kcal/mol) using clamped cubic spline (zero derivative end-point conditions)"),
                    ("DTI: ","The minimum difference in free energy (kcal/mol) between MBAR and the various TI interpolations"),

                    ("tgtSPSmax: ","Trial-maximum replica exch. single pass steps in the target environment"),
                    ("tgtSPSavg: ","Trial-average replica exch. single pass steps in the target environment"),
                    ("tgtTNRTmin: ","Trial-minimum num. round trips in the target environment"),
                    ("tgtTNRTavg: ","Trial-average num. round trips in the target environment"),
                    ("refSPSmax: ","Trial-maximum replica exch. single pass steps in the reference environment"),
                    ("refSPSavg: ","Trial-average replica exch. single pass steps in the reference environment"),
                    ("refTNRTmin: ","Trial-minimum num. round trips in the reference environment"),
                    ("refTNRTavg: ","Trial-average num. round trips in the reference environment"),

    
    ]

    tips = ET.SubElement(bottom_content,'div',
                         attrib={'id':"tips",
                                 'class':"hidable"})
    tips_lists = ET.SubElement(tips,'div',
                         attrib={'id':"tips-lists"})
    for disp,props in zip(["Actions","Abbreviations"],
                          [action_tips,abbrev_tips]):
        div = ET.SubElement(tips_lists,'div')
        ET.SubElement(div,'h3').text = disp
        ul = ET.SubElement(div,'ul')
        for prop in props:
            li = ET.SubElement(ul,'li')
            ET.SubElement(li,'span',attrib={'class':"tip"}).text=prop[0]
            ET.SubElement(li,'span').text=prop[1]

    ######################################################

    ccs = self.GetCycleClosures()
    #ccs = []

    nnode = len(self.topology.nodes)
    node_maxcc = np.zeros( (nnode,) )
    node_avgcc = np.zeros( (nnode,) )
    node_ncc = [0]*nnode

    nedge = len(self.entries)
    edge_maxcc = np.zeros( (nedge,) )
    edge_avgcc = np.zeros( (nedge,) )
    edge_ncc = [0]*nedge
    
    for cc in ccs:
        v = abs(cc.value)
        for node in cc.path[:-1]:
            inode = self.topology.nodes.index(node)
            node_ncc[inode] += 1
            node_avgcc[inode] += v
            node_maxcc[inode] = max(node_maxcc[inode],v)
        for eidx in cc.eidxs:
            edge_ncc[eidx] += 1
            edge_avgcc[eidx] += v
            edge_maxcc[eidx] = max(edge_maxcc[eidx],v)
            
    for inode in range(nnode):
        if node_ncc[inode] > 0:
            node_avgcc[inode] /= node_ncc[inode]
    for iedge in range(nedge):
        if edge_ncc[iedge] > 0:
            edge_avgcc[iedge] /= edge_ncc[iedge]


    node_lmi = np.zeros( (nnode,) )
    node_nlmi = np.zeros( (nnode,) )
    for iedge,entry in enumerate(self.entries):
        inode = self.topology.nodes.index( entry.nodes[0] )
        jnode = self.topology.nodes.index( entry.nodes[1] )
        lmi = abs(edge_lagmult[iedge])
        node_lmi[inode] += lmi
        node_lmi[jnode] += lmi
        node_nlmi[inode] += 1
        node_nlmi[jnode] += 1
    for inode in range(nnode):
        if node_nlmi[inode] > 0:
            node_lmi[inode] /= node_nlmi[inode]
            
    nodedata = []
    node_expt = [None] * nnode
    for inode,node in enumerate(self.topology.nodes):
        name = node
        confe = node_values[inode]
        conerr = node_errors[inode]
        avgcc = node_avgcc[inode]
        maxcc = node_maxcc[inode]
        cfemexpt = None
        if expt is not None:
            if name in expt:
                node_expt[inode] = expt[node]
                cfemexpt = expt[node] - confe
        lmi = node_lmi[inode]
        onclick=f"seleNode('{name}'); seleRow(this.id);"
        nodedata.append( [name,onclick, # 0 1
                          confe,conerr, # 2 3
                          lmi,avgcc,maxcc, # 4 5 6
                          node_expt[inode],cfemexpt] ) # 7,8

    
    edgedata = []
    for iedge,entry in enumerate(self.entries):
        e = self.GetPathFreeEnergy(self.topology.StrToPath(entry.fwdname))
        name = entry.fwdname
        unconfe = e.value
        unconerr = e.error
        inode = self.topology.nodes.index( e.path[0] )
        jnode = self.topology.nodes.index( e.path[1] )
        confe = node_values[jnode] - node_values[inode]
        conerr = np.sqrt( node_errors[jnode]**2 + node_errors[inode]**2 )
        dconfe = abs(confe-unconfe)
        cfemexpt = None
        exptedge = None
        if node_expt[inode] is not None and node_expt[jnode] is not None:
            exptedge = node_expt[jnode] - node_expt[inode]
            cfemexpt = confe - exptedge
        ti = None
        ti3n = None
        ti3c = None
        dti = None
        if e.ti is not None:
            ti = e.ti["Linear"][0]
            ti3n = e.ti["Natural"][0]
            ti3c = e.ti["Clamped"][0]
            dti = min(min(abs(unconfe-ti),abs(unconfe-ti3n)),abs(unconfe-ti3c))

            
        #nodeidxs = [inode,jnode]

        lmi = abs(edge_lagmult[iedge])
        ofc2 = entry.edge.results.conobj.c2
        # maxcc = 0
        # avgcc = 0
        # ncc = 0
        # for cc in ccs:
        #    if entry.fwdname in cc.name or entry.revname in cc.name:
        #        v = abs(cc.value)
        #        maxcc = max(maxcc,v)
        #        avgcc += v
        #        ncc += 1
        # if ncc > 0:
        #    avgcc /= ncc
        # print(ncc,edge_ncc[iedge],avgcc,edge_avgcc[iedge])
        maxcc = edge_maxcc[iedge]
        avgcc = edge_avgcc[iedge]

        redata = GetReplExchEdgeStats( entry.edge )
        
        msgs = entry.edge.GetErrorMsgs()
        nerr = sum( [1 for msg in msgs if msg.iserr] )
        nout = sum( [1 for msg in msgs if msg.kind == 'outlier'] )
        onclick = f"seleEdge('{name}'); seleRow(this.id);"
        edgedata.append( [name,onclick, # 0 1
                          unconfe,unconerr,confe,conerr, # 2 3 4 5
                          dconfe, lmi, # 6 7
                          avgcc,maxcc,nerr,nout, # 8 9 10 11
                          ofc2,exptedge,cfemexpt, # 12 13 14
                          ti,ti3n,ti3c, # 15 16 17
                          dti, # 18
                          redata["tgt"]["spsmax"], # 19
                          redata["tgt"]["spsavg"], # 20
                          redata["tgt"]["spsstd"], # 21
                          redata["tgt"]["rtprmin"], # 22
                          redata["tgt"]["rtpravg"], # 23
                          redata["tgt"]["rtprstd"], # 24
                          redata["tgt"]["tnrtmin"], # 25
                          redata["tgt"]["tnrtavg"], # 26
                          redata["tgt"]["tnrtstd"], # 27
                          redata["ref"]["spsmax"], # 28
                          redata["ref"]["spsavg"], # 29
                          redata["ref"]["spsstd"],  # 30
                          redata["ref"]["rtprmin"], # 31
                          redata["ref"]["rtpravg"], # 32
                          redata["ref"]["rtprstd"], # 33
                          redata["ref"]["tnrtmin"], # 34
                          redata["ref"]["tnrtavg"], # 35
                          redata["ref"]["tnrtstd"]  # 36
        ] )

    cycdata = []
    for cc in ccs:
        name = cc.name
        onclick="seleCycle([%s]); seleRow(this.id);"%\
            (",".join(["'%s'"%(self.entries[iedge].fwdname)
                       for iedge in cc.eidxs]))
        ti = None
        ti3n = None
        ti3c = None
        if cc.ti is not None:
            ti = abs(cc.ti["Linear"][0])
            ti3n = abs(cc.ti["Natural"][0])
            ti3c = abs(cc.ti["Clamped"][0])
        cycdata.append( [name,onclick,
                         len(name.split("~"))-1,
                         cc.value,cc.error,abs(cc.value),ti,ti3n,ti3c] )
        
    node_table = ET.SubElement(bottom_content,'div',
                              attrib={'id':"node-data",
                                      'class':"hidable"})
    nodeheadings = ['Node','onclick','CFE','dCFE','LMI','AvgCC','MaxCC','Expt','CFE-Expt']
    nodefmts = ['','','.3f','.3f','.2e','.3f','.3f','.3f','.3f']
    if expt is not None:
        nodecols = [0,7,8,2,3,4,5]
    else:
        nodecols = [0,2,3,4,5]
    node_table.append(
        GetSortTable( nodedata,
                      nodeheadings,
                      nodefmts,
                      nodecols) )

    
    edge_table = ET.SubElement(bottom_content,'div',
                              attrib={'id':"edge-data",
                                      'class':"hidable"})

    repex_table = ET.SubElement(bottom_content,'div',
                                attrib={'id':"repex-data",
                                        'class':"hidable"})

    ti_table = ET.SubElement(bottom_content,'div',
                             attrib={'id':"ti-data",
                                     'class':"hidable"})

    edgeheadings = ['Edge','onclick',
                    'UFE','dUFE','CFE','dCFE',
                    'Shift',
                    'LMI','AvgCC','MaxCC',
                    'ErrMsgs','Outliers','OFC2','Expt','CFE-Expt', 
                    'TI','TI3n','TI3c',
                    'DTI',
                    "tgtSPSmax",
                    "tgtSPSavg",
                    "tgtSPSstd",
                    "tgtRTPRmin",
                    "tgtRTPRavg",
                    "tgtRTPRstd",
                    "tgtTNRTmin",
                    "tgtTNRTavg",
                    "tgtTNRTstd",
                    "refSPSmax",
                    "refSPSavg",
                    "refSPSstd",
                    "refRTPRmin",
                    "refRTPRavg",
                    "refRTPRstd",
                    "refTNRTmin",
                    "refTNRTavg",
                    "refTNRTstd"
    ]
    edgefmts = ['','',
                '.3f','.3f','.3f','.3f',
                '.3f',
                '.2e','.3f','.3f',
                'd','d','.2e','.3f','.3f',
                '.3f','.3f','.3f',
                '.3f',
                '.0f','.0f','.0f',
                '.0f','.0f','.0f',
                '.0f','.0f','.0f',
                '.0f','.0f','.0f',
                '.0f','.0f','.0f',
                '.0f','.0f','.0f']
    if expt is not None:
        edgecols = [0,13,14,2,3,4,5,
                    #15,16,17,
                    6,7,12,8,9,10,11]
    else:
        edgecols = [0,2,3,4,5,
                    #15,16,17,
                    6,7,12,8,9,10,11]

        
    edge_table.append(
        GetSortTable( edgedata,
                      edgeheadings,
                      edgefmts,
                      edgecols) )

    repexcols = [0,19,20,25,26,28,29,34,35]

    repex_table.append(
        GetSortTable( edgedata,
                      edgeheadings,
                      edgefmts,
                      repexcols) )

    
    ticols = [0,2,15,16,17,18]

    ti_table.append(
        GetSortTable( edgedata,
                      edgeheadings,
                      edgefmts,
                      ticols) )

    

    cyc_table = ET.SubElement(bottom_content,'div',
                              attrib={'id':"cycle-data",
                                      'class':"hidable"})
    cyc_table.append(
        GetSortTable( cycdata,
                      ['Cycle','onclick',
                       'Length','UFE','dUFE','CC','CC(TI)','CC(TI3n)','CC(TI3c)'],
                      ['','','1','.3f','.3f','.3f','.3f','.3f','.3f'],
                      [0,2,3,4,5,6,7,8]) )

    script = ET.SubElement(body,'script', attrib={'type': "text/javascript"})
    nodelist = ",".join([ "\"%s\""%(row[0]) for row in nodedata])
    edgelist = ",".join([ "\"%s\""%(row[0]) for row in edgedata])

    minfe =  1.e+20
    maxfe = -1.e+20
    for row in edgedata:
        for i in [2,4]:
            minfe = min(minfe,row[i])
            maxfe = max(maxfe,row[i])
        
    minnodefe =  1.e+20
    maxnodefe = -1.e+20
    for row in nodedata:
        minnodefe = min(minnodefe,row[2])
        maxnodefe = max(maxnodefe,row[2])


    minerr =  1.e+20
    maxerr = -1.e+20
    for row in edgedata:
        for i in [3,5]:
            minerr = min(minerr,row[i])
            maxerr = max(maxerr,row[i])

    minshift =  1.e+20
    maxshift = -1.e+20
    for row in edgedata:
        minshift = min(minshift,row[6])
        maxshift = max(maxshift,row[6])

    minnodelag =  1.e+20
    maxnodelag = -1.e+20
    for row in nodedata:
        minnodelag = min(minnodelag,row[4])
        maxnodelag = max(maxnodelag,row[4])
        
    minlag =  1.e+20
    maxlag = -1.e+20
    for row in edgedata:
        minlag = min(minlag,row[7])
        maxlag = max(maxlag,row[7])
        
    mincc =  1.e+20
    maxcc = -1.e+20
    for row in edgedata:
        for i in [9]:
            mincc = min(mincc,row[i])
            maxcc = max(maxcc,row[i])

    minavgcc =  1.e+20
    maxavgcc = -1.e+20
    for row in edgedata:
        for i in [8]:
            minavgcc = min(minavgcc,row[i])
            maxavgcc = max(maxavgcc,row[i])
    minnavgcc =  1.e+20
    maxnavgcc = -1.e+20
    for row in nodedata:
        for i in [5]:
            minnavgcc = min(minnavgcc,row[i])
            maxnavgcc = max(maxnavgcc,row[i])

            

    minerrmsgs = 0
    maxerrmsgs = 0
    for row in edgedata:
        for i in [10]:
            maxerrmsgs = max(maxerrmsgs,row[i])

    minoutliers = 0
    maxoutliers = 0
    for row in edgedata:
        for i in [11]:
            maxoutliers = max(maxoutliers,row[i])

    minofc2 =  1.e+30
    maxofc2 = -1.e+30
    for row in edgedata:
        for i in [12]:
            maxofc2 = max(maxofc2,row[i])
            minofc2 = min(minofc2,row[i])

            
            
    fecolors = HexColorMap(minfe,maxfe)
    nodefecolors = HexColorMap(minnodefe,maxnodefe)
    errcolors = HexColorMap(minerr,maxerr)
    shiftcolors = HexColorMap(minshift,maxshift)
    cccolors = HexColorMap(mincc,maxcc)
    avgcccolors = HexColorMap(minavgcc,maxavgcc)
    nodeavgcccolors = HexColorMap(minnavgcc,maxnavgcc)
    lagcolors = HexColorMap(minlag,maxlag)
    nodelagcolors = HexColorMap(minnodelag,maxnodelag)
    errmsgcolors = HexColorMap(minerrmsgs,maxerrmsgs)
    outliercolors = HexColorMap(minoutliers,maxoutliers)
    ofc2colors = HexColorMap(minofc2,maxofc2)

    script.text  = "var gnodes = [%s];\n"%(nodelist)
    script.text += "var gedges = [%s];\n"%(edgelist)
    script.text += "var gnode_def = { color: \"rgb(170,170,220)\", size: 1 };\n"
    script.text += "var gedge_def = { color: \"rgb(0,0,0)\", size: 1 };\n"
    script.text += "var gdata = {\n"
    nnode = len(nodedata)
    lines = []
    for row in nodedata:
        props=[ "\"%s\" : %s"%( "CONFE", nodefecolors(row[2]) ),
                "\"%s\" : %s"%( "AVGCC", nodeavgcccolors(row[5]) ),
                "\"%s\" : %s"%( "LMI", nodelagcolors(row[4]) ) ]
        lines.append( "\"%s\": { %s }"%(row[0],",".join(props)) )
    for row in edgedata:
        props=[ "\"%s\" : %s"%( "UNCONFE", fecolors(row[2]) ),
                "\"%s\" : %s"%( "UNCONERR", errcolors(row[3]) ),
                "\"%s\" : %s"%( "CONFE", fecolors(row[4]) ),
                "\"%s\" : %s"%( "CONERR", errcolors(row[5]) ),
                "\"%s\" : %s"%( "SHIFT", shiftcolors(abs(row[6])) ),
                "\"%s\" : %s"%( "AVGCC", avgcccolors(row[8]) ),
                "\"%s\" : %s"%( "MAXCC", cccolors(row[9]) ),
                "\"%s\" : %s"%( "LMI", lagcolors(row[7]) ),
                "\"%s\" : %s"%( "OFC2", ofc2colors(row[12]) ),
                "\"%s\" : %s"%( "ERR", errmsgcolors(row[10]) ),
                "\"%s\" : %s"%( "OUT", outliercolors(row[11]) )
               ]
        lines.append( "\"%s\": { %s }"%(row[0],",".join(props)) )
        
    script.text += "%s\n"%(",\n".join(lines))
    
    script.text += "};\n"
    

    regres = ET.SubElement(body,"div",attrib={'id':'regres-content'})
    
    if expt is not None:
        cols = [7,8,2,3,4,5]
    else:
        cols = [2,3,4,5]
    regres.append( GetRegresDiv("Node",nodedata,nodeheadings,cols) )
    regres.append( GetRegresScript("Node",nodedata,nodeheadings,nodefmts,cols) )

    
    if expt is not None:
        cols = [13,14,2,3,4,5,6,7,12,8,9,10,11]
    else:
        cols = [2,3,4,5,6,7,12,8,9,10,11]

    regres.append( GetRegresDiv("Edge",edgedata,edgeheadings,cols) )
    regres.append( GetRegresScript("Edge",edgedata,edgeheadings,edgefmts,cols) )
    
    
    ######################################################

    body.append( GetGraphCanvasScript() )
    body.append( GetSortTableScript() )

    return html





def GetMultiDVDLHtml(self):
    import numpy as np
    from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj
    from . Splines import CubicSplineWithErrorProp


    class TrialData(object):
        def __init__(self,name,dvdldata):
            self.name = name
            self.xs = []
            nx = 4
            for i in range(dvdldata.shape[0]-1):
                dx = (dvdldata[i+1,0]-dvdldata[i,0])/nx
                for j in range(nx):
                    self.xs.append( dvdldata[i,0] + dx*j )
            self.xs.append(data[-1,0])
            self.ss = ["%.6f"%(x) for x in self.xs]
            nspl = CubicSplineWithErrorProp(dvdldata[:,0],None,None)
            self.ns = nspl.GetValues(dvdldata[:,1],self.xs)

        def GetY(self,x):
            y = "null"
            s = "%.6f"%(x)
            if s in self.ss:
                idx = self.ss.index(s)
                y = "%22.13e"%(self.ns[idx])
            return y


    tdata = []
    for itrial,trial in enumerate(self.trials):
        data = trial.GetDVDLProfile()
        if data is not None:
            tdata.append( TrialData(trial.name,data) )

    if len(tdata) == 0:
        return None

    res=[]
    
    ss=[]
    for t in tdata:
        ss.extend(t.ss)
    ss = list(set([float(x) for x in ss]))
    ss.sort()
    ss = ["%.6f"%(x) for x in ss]

    maxy=-1.e+30
    miny= 1.e+30
    for t in tdata:
        maxy=max(maxy,max(t.ns))
        miny=min(miny,min(t.ns))
    ddy    = (maxy-miny)*0.05
    miny  -= ddy
    maxy  += ddy
    
    maxx=1
    minx=0
    ddx    = (maxx-minx)*0.05
    minx  -= ddx
    maxx  += ddx

    nxs = len(ss)
    nts = len(tdata)
    data = []
    #print("ss=",ss)
    for i in range(nxs):
        vals = [ t.GetY(float(ss[i])) for t in tdata ]
        data.append([ss[i]] + vals)

    name   = "dvdl_" + GetHtmlIdFromObj(self)

    dstr  = "[" + ",".join(["[" + ",".join([x for x in row]) + "]" for row in data ]) + "]"
    
    allcolors = [ "#182a22", "#d82429", "#006b3c", "#0a1195", "#ed872d", "#fff600", "#884bc1", "#00e5ff" ]
    colors = "[" + ",".join([ "\"%s\""%(allcolors[i%len(allcolors)]) for i in range(nts) ]) + "]"
    
    names = ["Lambda"] + [t.name for t in tdata]
    names = "[" + ",".join(["\"%s\""%(x) for x in names]) + "]"


    s = ET.Element("script",attrib={'type':'text/javascript'})
    s.text = (f"function {name}() {{ "
              f"multidvdlchart( \"{name}\", {colors}, {minx}, {maxx}, "
              f"{miny}, {maxy}, {dstr}, {names} ); }}; "
              f"google.charts.setOnLoadCallback({name});")
    res.append(s)
        
    div = ET.Element("div",attrib={'class':'timeseries'})
    table = ET.SubElement(div,'table',attrib={'class':'timeseries'})
    tr = ET.SubElement(table,'tr')
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span').text = GetHtmlSymbolFromObj(self)
    br = ET.SubElement(th,'br')
    span = ET.SubElement(th,'span').text = "DV/DL (kcal/mol)"
    tr = ET.SubElement(table,'tr')
    td = ET.SubElement(tr,'td',attrib={'id':name})
    res.append(div)
    return res

    

def GetMultiARHtml(self):
    import numpy as np
    from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj

    class TrialData(object):
        def __init__(self,name,xs,ys):
            self.name = name
            self.xs = xs
            self.ss = ["%.6f"%(x) for x in self.xs]
            self.ys = ys

        def GetY(self,x):
            y = "null"
            s = "%.6f"%(x)
            if s in self.ss:
                idx = self.ss.index(s)
                y = "%22.13e"%(self.ys[idx])
            return y


    tdata = []
    for itrial,trial in enumerate(self.trials):
        data = GetReplExchData( trial )

        if data is not None:
            ars = data['neighbor_acceptance_ratio']
            lams = [ float(lam) for lam in trial.ene ]
            mids = [ (lams[i]+lams[i+1])/2 for i in range(len(lams)-1) ]
            if len(ars) == len(mids):
                tdata.append( TrialData(trial.name,mids,ars) )

    if len(tdata) == 0:
        return None

    res=[]
    
    ss=[]
    for t in tdata:
        ss.extend(t.ss)
    ss = list(set([float(x) for x in ss]))
    ss.sort()
    ss = ["%.6f"%(x) for x in ss]

    # maxy=-1.e+30
    # miny= 1.e+30
    # for t in tdata:
    #     maxy=max(maxy,max(t.ys))
    #     miny=min(miny,min(t.ys))
    maxy=1
    miny=0
    ddy    = (maxy-miny)*0.05
    miny  -= ddy
    maxy  += ddy
    
    maxx=1
    minx=0
    ddx    = (maxx-minx)*0.05
    minx  -= ddx
    maxx  += ddx

    nxs = len(ss)
    nts = len(tdata)
    data = []
    #print("ss=",ss)
    for i in range(nxs):
        vals = [ t.GetY(float(ss[i])) for t in tdata ]
        data.append([ss[i]] + vals)

    name   = "ar_" + GetHtmlIdFromObj(self)

    dstr  = "[" + ",".join(["[" + ",".join([x for x in row]) + "]" for row in data ]) + "]"
    
    allcolors = [ "#182a22", "#d82429", "#006b3c", "#0a1195", "#ed872d", "#fff600", "#884bc1", "#00e5ff" ]
    colors = "[" + ",".join([ "\"%s\""%(allcolors[i%len(allcolors)]) for i in range(nts) ]) + "]"
    
    names = ["Lambda"] + [t.name for t in tdata]
    names = "[" + ",".join(["\"%s\""%(x) for x in names]) + "]"


    s = ET.Element("script",attrib={'type':'text/javascript'})
    s.text = (f"function {name}() {{ "
              f"multidvdlchart( \"{name}\", {colors}, {minx}, {maxx}, "
              f"{miny}, {maxy}, {dstr}, {names} ); }}; "
              f"google.charts.setOnLoadCallback({name});")
    res.append(s)
        
    div = ET.Element("div",attrib={'class':'timeseries'})
    table = ET.SubElement(div,'table',attrib={'class':'timeseries'})
    tr = ET.SubElement(table,'tr')
    th = ET.SubElement(tr,'th')
    span = ET.SubElement(th,'span').text = GetHtmlSymbolFromObj(self)
    br = ET.SubElement(th,'br')
    span = ET.SubElement(th,'span').text = "Accept. Ratio"
    tr = ET.SubElement(table,'tr')
    td = ET.SubElement(tr,'td',attrib={'id':name})
    res.append(div)
    return res




def GetDVDLHtml(self):
    import numpy as np
    from . Names import GetHtmlSymbolFromObj, GetHtmlIdFromObj
    from . Splines import CubicSplineWithErrorProp
    from . Splines import USubSplineWithErrorProp
    from . GlobalOptions import GlobalOptions
    
    #DO_USPL = CalcUsubSpline()
    gopts = GlobalOptions()
    DO_USPL = gopts.CalcUsubSpline
    
    res = None
    data = self.GetDVDLProfile()    
    if data is not None:
        res = []
        
        cspl = CubicSplineWithErrorProp(data[:,0],0,0)
        nspl = CubicSplineWithErrorProp(data[:,0],None,None)
        if DO_USPL:
            uspl = USubSplineWithErrorProp(data[:,0],data[:,1],None)
        else:
            uspl=None
            
        xs = []
        nx = 4
        for i in range(data.shape[0]-1):
            dx = (data[i+1,0]-data[i,0])/nx
            for j in range(nx):
                xs.append( data[i,0] + dx*j )
        xs.append(data[-1,0])
        xs = np.array(xs)
        cs = cspl.GetValues(data[:,1],xs)
        ns = nspl.GetValues(data[:,1],xs)
        if uspl is not None:
            us = uspl.GetValues(xs)
        else:
            us = None

        odata = data[:,:2]
        minx = np.amin( odata[:,0] )
        maxx = np.amax( odata[:,0] )
        n = len(xs)
        if uspl is not None:
            fdata = np.zeros( (n,4) )
        else:
            fdata = np.zeros( (n,3) )
        fdata[:,0] = xs
        fdata[:,1] = ns
        fdata[:,2] = cs
        if uspl is not None:
            fdata[:,3] = us
            miny   = min( np.amin(fdata[:,1:4]), np.amin(odata[:,1]) )
            maxy   = max( np.amax(fdata[:,1:4]), np.amax(odata[:,1]) )
        else:
            miny   = min( np.amin(fdata[:,1:3]), np.amin(odata[:,1]) )
            maxy   = max( np.amax(fdata[:,1:3]), np.amax(odata[:,1]) )
            
        ddx    = (maxx-minx)*0.05
        minx  -= ddx
        maxx  += ddx
        ddy    = (maxy-miny)*0.05
        miny  -= ddy
        maxy  += ddy
        name   = "dvdl_" + GetHtmlIdFromObj(self)
        colors = '["#09204e","#b00b13","#09bfb8","#418FFF"]'
        odstr  = "[" + ",".join(["[" + ",".join(["%22.13e"%(x) for x in row]) + "]" for row in odata ]) + "]"
        fdstr  = "[" + ",".join(["[" + ",".join(["%22.13e"%(x) for x in row]) + "]" for row in fdata ]) + "]"
            
        s = ET.Element("script",attrib={'type':'text/javascript'})
        if uspl is not None:
            fname = "dvdlchart3"
        else:
            fname = "dvdlchart2"
            
        s.text = (f"function {name}() {{ "
                  f"{fname}( \"{name}\", {colors}, {minx}, {maxx}, "
                  f"{miny}, {maxy}, {odstr}, {fdstr} ); }}; "
                  f"google.charts.setOnLoadCallback({name});")
        res.append(s)
        
        div = ET.Element("div",attrib={'class':'timeseries'})
        table = ET.SubElement(div,'table',attrib={'class':'timeseries'})
        tr = ET.SubElement(table,'tr')
        th = ET.SubElement(tr,'th')
        span = ET.SubElement(th,'span').text = GetHtmlSymbolFromObj(self)
        br = ET.SubElement(th,'br')
        span = ET.SubElement(th,'span').text = "DV/DL (kcal/mol)"
        tr = ET.SubElement(table,'tr')
        td = ET.SubElement(tr,'td',attrib={'id':name})
        res.append(div)

    return res
                      
