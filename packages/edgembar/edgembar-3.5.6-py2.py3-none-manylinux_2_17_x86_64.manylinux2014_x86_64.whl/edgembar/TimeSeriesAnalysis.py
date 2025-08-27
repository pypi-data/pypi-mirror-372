#!/usr/bin/env python3
import numpy as np
from typing import Optional
from typing import Tuple
from typing import List
import xml.etree.ElementTree as ET

import warnings
warnings.filterwarnings('error', "Mean of empty slice.")


def GetDualTimeSeriesImg(t,p,f,r,yrange,labels,xlabel,fmt="png") -> ET.Element:
    import io
    import base64
    import matplotlib.pyplot as plt
    import numpy as np
    
    
    w = 420
    h = 420

    px = 1/plt.rcParams['figure.dpi']
    plt.style.use('seaborn-whitegrid')
    fig,ax = plt.subplots(figsize=(w*px, h*px))
    # "[\"#ffff99\",\"#0000cc\",\"#ff0000\"]"
    #pcolor = '#ffff99'
    #pcolor = 'gray'
    #pcolor = '#d3d3d3'
    pcolor = "#09bfb8"
    if p is not None:
        xp = np.array([0,1])
        yp = np.array([p[0],p[0]])
        dp = np.array([1.96*p[1],1.96*p[1]])

    #fcolor = '#0000cc'
    fcolor = "#09204e"
    if f is not None:
        yf = np.array([x[0] for x in f])
        df = np.array([1.96*x[1] for x in f])

    #rcolor = '#ff0000'
    rcolor = "#b00b13"
    if r is not None:
        yr = np.array([x[0] for x in r])
        dr = np.array([1.96*x[1] for x in r])

    if p is not None:
        ax.plot(xp,yp,color=pcolor,lw=3.25,
                linestyle='dotted',label=labels[0])
        ax.fill_between(xp,yp-dp,yp+dp,
                        color=pcolor,alpha=0.4)
    if f is not None:
        ax.plot(t,yf,color=fcolor,lw=2.3, marker='o', markersize=5,label=labels[1])
        ax.fill_between(t,yf-df,yf+df,
                        color=fcolor,alpha=0.2)

    if r is not None:
        ax.plot(t,yr,color=rcolor,lw=2.3, marker='o', markersize=5,label=labels[2])
        ax.fill_between(t,yr-dr,yr+dr,
                        color=rcolor,alpha=0.2)
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02),
          ncol=3, fancybox=True, shadow=True)
    
    plt.xlim([0,1.05])
    if yrange[1] > yrange[0]:
        plt.ylim(yrange)

    ax.set_xlabel(xlabel)

    plt.tight_layout(pad=0.5) #, w_pad=0, h_pad=0)


    #fmt = "jpeg" 
    #fmt = "png" 
    img64 = io.BytesIO()
    plt.savefig(img64,format=fmt)
    plt.close('all')
    img64.seek(0)
    img64 = base64.b64encode(img64.getvalue()).decode("utf-8").replace("\n", "")
    return ET.Element('img',attrib={'src': "data:image/%s;base64,%s"%(fmt,img64)})
    #return '<img src="data:image/%s;base64,%s">'%(fmt,img64)




class TimeSeriesAnalysis(object):


    @classmethod
    def factory( cls,
                 eneobj,
                 glbresults,
                 istate=None ):

        ftimes = None
        fvals = None
        rvals = None
        htimes = None
        fhalf = None
        lhalf = None
        hasdata = False
        if istate is None:
            pvals = eneobj.GetValueAndError(glbresults.prod)
        else:
            pvals = eneobj.GetValueAndError(glbresults.prod,istate)

        if glbresults.fwd is not None and \
           glbresults.rev is not None:
            hasdata = True
            ftimes = [ t.time for t in glbresults.fwd ]
            if istate is None:
                fvals = [ eneobj.GetValueAndError(t.values)
                          for t in glbresults.fwd ]
                rvals = [ eneobj.GetValueAndError(t.values)
                          for t in glbresults.rev ]
            else:
                fvals = [ eneobj.GetValueAndError(t.values,istate)
                          for t in glbresults.fwd ]
                rvals = [ eneobj.GetValueAndError(t.values,istate)
                          for t in glbresults.rev ]

        if glbresults.fhalf is not None and \
           glbresults.lhalf is not None:
            hasdata = True
            htimes = [ t.time for t in glbresults.fhalf ]
            if istate is None:
                fhalf = [ eneobj.GetValueAndError(t.values)
                          for t in glbresults.fhalf ]
                lhalf = [ eneobj.GetValueAndError(t.values)
                          for t in glbresults.lhalf ]
            else:
                fhalf = [ eneobj.GetValueAndError(t.values,istate)
                          for t in glbresults.fhalf ]
                lhalf = [ eneobj.GetValueAndError(t.values,istate)
                          for t in glbresults.lhalf ]

        ret = None
        if hasdata:
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

            ret = TimeSeriesAnalysis(edge,env,stage,trial,ene,pvals,
                                     ftimes,fvals,rvals,
                                     htimes,fhalf,lhalf )

        return ret

    
    
    def __init__( self,
                  edge: str,
                  env: Optional[str],
                  stage: Optional[str],
                  trial: Optional[str],
                  ene: Optional[str],
                  prod: Tuple[float,float],
                  frtimes: Optional[np.ndarray],
                  fwd: Optional[np.ndarray],
                  rev: Optional[np.ndarray],
                  fltimes: Optional[np.ndarray],
                  fhalf: Optional[np.ndarray],
                  lhalf: Optional[np.ndarray],
                  sym: Optional[str] = "G" ):
        
        from . Names import GetUnicodeName, GetHtmlId, GetHtmlName, GetHtmlSymbol
        
        self.edge = edge
        self.env = env
        self.stage = stage
        self.trial = trial
        self.ene = ene
        self.prod = prod
        self.frtimes = frtimes
        self.fwd = fwd
        self.rev = rev
        self.fltimes = fltimes
        self.fhalf = fhalf
        self.lhalf = lhalf

        self.ymin =  1.e+100
        self.ymax = -1.e+100
        
        def minmax(MinMax,arr):
            Min,Max = MinMax
            for x,y in arr:
                u = x+1.96*y
                v = x-1.96*y
                Min = min(Min,min(u,v))
                Max = max(Max,max(u,v))
            return Min,Max

        mm = (1.e+100,-1.e+100)
        if self.fwd is not None:
            mm = minmax(mm,self.fwd)
        if self.rev is not None:
            mm = minmax(mm,self.rev)
        if self.fhalf is not None:
            mm = minmax(mm,self.fhalf)
        if self.lhalf is not None:
            mm = minmax(mm,self.lhalf)
        self.ymin,self.ymax = mm
        if self.prod is not None:
            u = self.prod[0]+1.96*self.prod[1]
            v = self.prod[0]-1.96*self.prod[1]
            self.ymin = min(self.ymin,min(u,v))
            self.ymax = max(self.ymax,max(u,v))
        c = 0.5*(self.ymin+self.ymax)
        d = 0.5*(self.ymax-self.ymin)
        self.ymax = c + d*1.05
        self.ymin = c - d*1.05

        
        self.title = GetUnicodeName(edge,env,stage,trial,ene,sym=sym)
        self.divid = GetHtmlId(edge,env,stage,trial,ene,sym=sym)
        self.htmlname = GetHtmlName(edge,env,stage,trial,ene,sym=sym)
        self.htmlsym = GetHtmlSymbol(env,stage,trial,ene,sym=sym)
        self.fwdrevid = "fr_" + self.divid
        self.firstlastid = "fl_" + self.divid
        
        
    def _GetScript(self, imgfmt: Optional[str] ) -> ET.Element:

        if imgfmt is not None:
            return ""
        
        ret = ""
        if self.fwd is not None and self.rev is not None:
            myid = self.fwdrevid
            title = "\"" + self.title.strip() + "\\nFwd & Rev Analysis (kcal/mol)" + "\""
            ymin = "%.8f"%(self.ymin)
            ymax = "%.8f"%(self.ymax)
            labels = "[\"Prod\",\"Fwd\",\"Rev\"]"
            #colors = "[\"#ffff99\",\"#0000cc\",\"#ff0000\"]"
            ##colors = "[\"#d3d3d3\",\"#0000cc\",\"#ff0000\"]"
            colors = "[\"#09bfb8\",\"#09204e\",\"#b00b13\"]"
            xlabel = "\"Sampling Fraction\""
            allcs = []
            for i in range(len(self.frtimes)):
                cs = []
                cs.append( "{0:.8f}".format(self.frtimes[i]) )
                if self.prod is not None:
                    v,e = self.prod
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                if self.fwd is not None:
                    v,e = self.fwd[i]
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                if self.rev is not None:
                    v,e = self.rev[i]
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                allcs.append( "[" + ",".join(cs) + "]" )
            dmat = ",\n".join(allcs)
            ret += f"function {myid}() {{ tschart( \"{myid}\", {title}, {ymin}, {ymax}, {labels}, {colors}, {xlabel}, \n[{dmat}] ); }}\n"
            ret += f"google.charts.setOnLoadCallback({myid});\n"

        elif self.fwd is not None:
            myid = self.fwdrevid
            title = "\"" + self.title.strip() + "\\nDelta-U Time Series (kcal/mol)" + "\""
            ymin = "%.8f"%(self.ymin)
            ymax = "%.8f"%(self.ymax)
            labels = "[\"Obs\"]"
            #colors = "[\"#ffff99\",\"#0000cc\",\"#ff0000\"]"
            ##colors = "[\"#d3d3d3\",\"#0000cc\",\"#ff0000\"]"
            colors = "[\"#09204e\"]"
            xlabel = "\"Simulation time\""
            allcs = []
            for i in range(len(self.frtimes)):
                cs = []
                cs.append( "{0:.8f}".format(self.frtimes[i]) )
                # if self.prod is not None:
                #     v,e = self.prod
                #     e *= 1.96
                #     cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                if self.fwd is not None:
                    v,e = self.fwd[i]
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                # if self.rev is not None:
                #     v,e = self.rev[i]
                #     e *= 1.96
                #     cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                allcs.append( "[" + ",".join(cs) + "]" )
            dmat = ",\n".join(allcs)
            
            
            ret += f"function {myid}() {{ tschart1( \"{myid}\", {title}, {ymin}, {ymax}, {labels}, {colors}, {xlabel}, \n[{dmat}] ); }}\n"
            ret += f"google.charts.setOnLoadCallback({myid});\n"



            
        if self.fhalf is not None and self.lhalf is not None:
            xlabel = "\"Sampling Fraction\""
            myid = self.firstlastid
            title = "\"" + self.title.strip() + "\\nFirst & Last Half Analysis (kcal/mol)" + "\""
            ymin = "%.8f"%(self.ymin)
            ymax = "%.8f"%(self.ymax)
            labels = "[\"Prod\",\"First\",\"Last\"]"
            #colors = "[\"#ffff99\",\"#0000cc\",\"#ff0000\"]"
            colors = "[\"#09bfb8\",\"#09204e\",\"#b00b13\"]"
            xlabel = "\"Exclusion Fraction\""
            allcs = []
            for i in range(len(self.fltimes)):
                cs = []
                cs.append( "{0:.8f}".format(self.fltimes[i]) )
                if self.prod is not None:
                    v,e = self.prod
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                if self.fhalf is not None:
                    v,e = self.fhalf[i]
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                if self.lhalf is not None:
                    v,e = self.lhalf[i]
                    e *= 1.96
                    cs.append( "{0:.4f},{1:.4f},{2:.4f}".format(v,v-e,v+e) )
                allcs.append( "[" + ",".join(cs) + "]" )
            dmat = ",\n".join(allcs)
            ret += f"function {myid}() {{ tschart( \"{myid}\", {title}, {ymin}, {ymax}, {labels}, {colors}, {xlabel}, \n[{dmat}] ); }}\n"
            ret += f"google.charts.setOnLoadCallback({myid});\n"
        ele = ET.Element('script',attrib={'type': "text/javascript"})
        ele.text = ret
        return ele



    
    
    
    def _GetDiv( self, imgfmt: Optional[str] ) -> ET.Element:

        ret = None
        if (self.fwd is not None and self.rev is None) \
           or (self.fwd is not None and self.rev is not None) \
           or (self.fhalf is not None and self.lhalf is not None):
            ret = ET.Element('div',attrib={'class':"timeseries"}) #,attrib={'id':self.divid})
            table = ET.SubElement(ret,'table',attrib={'class':"timeseries"})
            tr = ET.SubElement(table,'tr')
            if self.fwd is not None and self.rev is not None:
                th = ET.SubElement(tr,'th')
                span = ET.SubElement(th,'span')
                span.text = self.htmlname
                br = ET.SubElement(th,'br')
                span = ET.SubElement(th,'span')
                span.text = "Fwd &amp; Rev Analysis (kcal/mol)"
            elif self.fwd is not None:
                th = ET.SubElement(tr,'th')
                span = ET.SubElement(th,'span')
                span.text = self.htmlname
                br = ET.SubElement(th,'br')
                span = ET.SubElement(th,'span')
                span.text = "Nonoverlapping block average (kcal/mol)"
            if self.fhalf is not None and self.lhalf is not None:
                th = ET.SubElement(tr,'th')
                span = ET.SubElement(th,'span')
                span.text = self.htmlname
                br = ET.SubElement(th,'br')
                span = ET.SubElement(th,'span')
                span.text = "First- &amp; Last-Half Analysis (kcal/mol)"
            tr = ET.SubElement(table,'tr')
            if self.fwd is not None and self.rev is not None:
                td = ET.SubElement(tr,'td')
                if imgfmt is not None:
                    img=GetDualTimeSeriesImg(self.frtimes,self.prod,self.fwd,self.rev,
                                             [self.ymin,self.ymax],["Prod","Fwd","Rev"],
                                             "Sampling Fraction",
                                             fmt=imgfmt)
                    td.append(img)
                else:
                    td.attrib["id"] = self.fwdrevid
            elif self.fwd is not None:
                td = ET.SubElement(tr,'td')
                if imgfmt is not None:
                    img=GetDualTimeSeriesImg(self.frtimes,None,self.fwd,None,
                                             [self.ymin,self.ymax],["Prod","Obs.","Rev"],
                                             "Simulation Time",
                                             fmt=imgfmt)
                    td.append(img)
                else:
                    td.attrib["id"] = self.fwdrevid

                    
            if self.fhalf is not None and self.lhalf is not None:
                td = ET.SubElement(tr,'td')
                if imgfmt is not None:
                    img=GetDualTimeSeriesImg(self.fltimes,self.prod,self.fhalf,self.lhalf,
                                             [self.ymin,self.ymax],["Prod","First","Last"],
                                             "Exclusion Fraction",
                                             fmt=imgfmt)
                    td.append(img)
                else:
                    td.attrib["id"] = self.firstlastid

        if ret is None:
            raise Exception("expected to return an ET.Element, but returning None")
                    
        return ret

    
    def GetHtml( self, imgfmt: Optional[str] ) -> List[ET.Element]:
        nodes = []
        if imgfmt is None:
            nodes.append( self._GetScript(imgfmt) )
        nodes.append( self._GetDiv(imgfmt) )
        return nodes





##################################################
##################################################
##################################################






class SimplifiedAutoEqAnalysis(object):
    def __init__(self,trialobj,isim):
        from pathlib import Path
        
        from . AutoEquil import AutoEquil
        from . AutoEquil import CptMeanAndStderr
        from . AutoEquil import GetBeta, StatIneff, SliceAnalysis
        
        from . Names import GetNameFromObj
        import numpy as np
        from collections import defaultdict as ddict
        
        self.trial   = trialobj
        self.simidx  = isim
        self.fwddata = None
        self.fwdblks = None
        self.revdata = None
        self.revblks = None
        self.prod_start = 0
        self.fwdana = None
        self.revana = None

        
        self.beta = GetBeta(self.trial.edge.results.temp)
        names = GetNameFromObj(self.trial,istate=isim)
        datadir = Path( self.trial.datadir )
        simene = self.trial.ene[self.simidx]
        simfile = datadir / f"efep_{simene}_{simene}.dat"

        if self.trial.results is not None and simfile.is_file():
            fstart = self.trial.edge.results.fstart
            fstop  = self.trial.edge.results.fstop
            stride = self.trial.edge.results.stride
            
            simdata = np.loadtxt(str(simfile))[:,1]

            sim_isequil = self.trial.results[self.simidx].isequil
            
            if isim < len(self.trial.ene) - 1:
                self.fwdidx = isim+1
                fwdene = self.trial.ene[self.fwdidx]
                fwdfile = datadir / f"efep_{simene}_{fwdene}.dat"
                if fwdfile.is_file():
                    self.fwddata = self.beta*(np.loadtxt(str(fwdfile))[:,1]-simdata)
                    
                    N = len(self.fwddata)
                    istart = int(N*fstart+0.5)
                    istop = int(N*fstop+0.5)
                    self.rawdata = self.fwddata[istart:istop:stride]

                    fstart = 0
                    fstop = 1
                    fmaxeq = 0.95
                    fdelta = 0.05
                    
                    self.fwdblks = SliceAnalysis\
                        (fstart,fstop,fmaxeq,fdelta,
                         self.fwddata,
                         self.trial.edge.results.ptol,
                         self.trial.edge.results.dtol*self.beta)

                    self.fwdana = SliceAnalysis\
                        (fstart,fstop,self.trial.edge.results.ferreq,fdelta,
                         self.fwddata,
                         self.trial.edge.results.ptol,
                         self.trial.edge.results.dtol*self.beta)
                    
                    ffhalf   = np.array( [[ blk.mean_fhalf,blk.stde_fhalf] for blk in self.fwdblks ] )
                    flhalf   = np.array( [[ blk.mean_lhalf,blk.stde_lhalf] for blk in self.fwdblks ] )

                    for blk in self.fwdblks:
                        start = blk.offset
                        N = len(self.fwddata)
                        fmaxeq = self.trial.edge.results.fmaxeq
                        imax = int( N*fmaxeq )
                        if start >= imax:
                            start = imax
                            break
                        elif blk.test:
                            break

                    self.prod_start = start

                    
            if isim > 0:
                self.revidx = isim-1
                revene = self.trial.ene[self.revidx]
                revfile = datadir / f"efep_{simene}_{revene}.dat"
                if revfile.is_file():
                    self.revdata = self.beta*(np.loadtxt(str(revfile))[:,1]-simdata)
                    
                    N = len(self.revdata)
                    istart = int(N*fstart+0.5)
                    istop = int(N*fstop+0.5)
                    self.revdata = self.revdata[istart:istop:stride]
                    
                    fstart = 0
                    fstop = 1
                    fmaxeq = 0.95
                    fdelta = 0.05
                    
                    self.revblks = SliceAnalysis\
                        (fstart,fstop,fmaxeq,fdelta,
                         self.revdata,
                         self.trial.edge.results.ptol,
                         self.trial.edge.results.dtol*self.beta)
                    
                    self.revana = SliceAnalysis\
                        (fstart,fstop,self.trial.edge.results.ferreq,fdelta,
                         self.revdata,
                         self.trial.edge.results.ptol,
                         self.trial.edge.results.dtol*self.beta)
                    
                    rfhalf   = np.array( [[ blk.mean_fhalf,blk.stde_fhalf] for blk in self.revblks ] )
                    rlhalf   = np.array( [[ blk.mean_lhalf,blk.stde_lhalf] for blk in self.revblks ] )

                    for blk in self.revblks:
                        start = blk.offset
                        N = len(self.revdata)
                        fmaxeq = self.trial.edge.results.fmaxeq
                        imax = int( N*fmaxeq )
                        if start >= imax:
                            start = imax
                            break
                        elif blk.test:
                            break

                    self.prod_start = max(self.prod_start,start)

            self.fwd_avg = None
            self.fwd_err = None
            self.rev_avg = None
            self.rev_err = None
            self.prod_stride = 1
            if self.fwddata is not None:
                self.prod_stride = StatIneff(self.fwddata[self.prod_start:])
            if self.revdata is not None:
                self.prod_stride = max(self.prod_stride,StatIneff(self.revdata[self.prod_start:]))


            if self.fwddata is not None:
                c = self.fwddata[self.prod_start:]
                u = c[::self.prod_stride]
                self.fwd_avg = np.mean(c)
                self.fwd_err = np.sqrt( np.var(u,ddof=1) / len(u) )
                fltimes = [ blk.offset / N for blk in self.fwdblks]

            if self.revdata is not None:
                c = self.revdata[self.prod_start:]
                u = c[::self.prod_stride]
                self.rev_avg = np.mean(c)
                self.rev_err = np.sqrt( np.var(u,ddof=1) / len(u) )
                fltimes = [ blk.offset / N for blk in self.revblks]


                
            if self.fwddata is not None:

                prod = np.array( [self.fwd_avg,self.fwd_err/1.96] )
                
                tmpfhalf = np.array(ffhalf,copy=True)
                tmpfhalf[:,1] /= 1.96
                tmplhalf = np.array(flhalf,copy=True)
                tmplhalf[:,1] /= 1.96

                tmpseg = np.array( [ [blk.seg_mean,blk.seg_stde/1.96] for blk in self.fwdblks ] )
                segts = np.array( [blk.offset/N for blk in self.fwdblks[1:]] + [1] )

                tmpfhalf /= self.beta
                tmplhalf /= self.beta
                tmpseg /= self.beta
                prod /= self.beta
                
                #tmpseg = None
                #segts = None
                
                self.fwdts = TimeSeriesAnalysis\
                    ( names[0], names[1], names[2], names[3],
                      simene, prod,
                      segts, tmpseg, None,
                      fltimes, tmpfhalf, tmplhalf,
                      sym = "Ufwd" )
                
            if self.revdata is not None:
                                
                prod = np.array( [self.rev_avg,self.rev_err/1.96] )
                
                tmpfhalf = np.array(rfhalf,copy=True)
                tmpfhalf[:,1] /= 1.96
                tmplhalf = np.array(rlhalf,copy=True)
                tmplhalf[:,1] /= 1.96

                tmpseg = np.array( [ [blk.seg_mean,blk.seg_stde/1.96] for blk in self.revblks ] )
                segts = np.array( [blk.offset/N for blk in self.revblks[1:]] + [1] )

                tmpfhalf /= self.beta
                tmplhalf /= self.beta
                tmpseg /= self.beta
                prod /= self.beta

                #tmpseg = None
                #segts = None
                
                self.revts = TimeSeriesAnalysis\
                    ( names[0], names[1], names[2], names[3],
                      simene, prod,
                      segts, tmpseg, None,
                      fltimes, tmpfhalf, tmplhalf,
                      sym = "Urev" )
                
            if self.revdata is not None or self.fwddata is not None:
                self.hasdata = True

                


    def GetHtml( self, imgfmt: Optional[str] ) -> List[ET.Element]:
        nodes = []
        if self.fwddata is not None and self.revdata is not None:
            nodes = self.fwdts.GetHtml(imgfmt)
            rnodes = self.revts.GetHtml(imgfmt)
            # for inode,node in enumerate(nodes):
            #     print("fwd",inode,node)
            # for inode,node in enumerate(rnodes):
            #     print("rev",inode,node,node) #node.find("table"))
            #     for child in node:
            #         print("  child",child)
            rchildren = [ child for child in rnodes[-1] ]
            nodes[-1].append( rchildren[0] )
            if len(rnodes) > 1:
                nodes.insert(0,rnodes[0])
        elif self.fwddata is not None:
            nodes = self.fwdts.GetHtml(imgfmt)
        elif self.revdata is not None:
            nodes = self.revts.GetHtml(imgfmt)
        nodes.append( self.GetHtmlTable() )
        return nodes
    


    def GetHtmlTable(self) -> ET.Element:
        import numpy as np
        from . Names import GetHtmlSymbolFromObj
        from . Names import GetHtmlIdFromObj
        #from . AutoEquil import AnalysisSegment
        from . AutoEquil import AreTheSame
        from collections import defaultdict as ddict

        ptol = self.trial.edge.results.ptol
        dtol = self.trial.edge.results.dtol
        
        div = ET.Element('div',attrib={'class':'desc'})
        p = ET.SubElement(div,'p')
        span = ET.SubElement(p,'span')
        term = GetHtmlSymbolFromObj(self.trial)
        divid = GetHtmlIdFromObj(self.trial)
        a = ET.SubElement(p,'a',attrib={'href':f"#{divid}"})
        a.text = "Click here"
        span = ET.SubElement(p,'span')
        span.text = f" to see {term}"
        br = ET.SubElement(p,'br')

        ele = p
        p = ET.SubElement(ele,'p',attrib={'style':"text-align:center; font-weight:bold;"})
        p.text = GetHtmlSymbolFromObj(self.trial,istate=self.simidx,sym="U")
        
        table = ET.SubElement(ele,'table',attrib={'class':"simprop"})
        tr = ET.SubElement(table,'tr',attrib={'class':'top'})
        th = ET.SubElement(tr,'th').text = "f0"
        
        if self.fwdana is not None:
            th = ET.SubElement(tr,'th',attrib={'colspan':'4','class':'ul'})
            th.text = "&Delta;Ufwd"

        if self.fwdana is not None and self.revana is not None:
            th = ET.SubElement(tr,'th')

        if self.revana is not None:
            th = ET.SubElement(tr,'th',attrib={'colspan':'4','class':'ul'})
            th.text = "&Delta;Urev"

            
        tr = ET.SubElement(table,'tr',attrib={'class':'ul'})
        th = ET.SubElement(tr,'th')
        if self.fwdana is not None:
            #th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            #th.text = "&Delta;"
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "&Delta; &lt; %.2f"%(dtol)
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "p<sub>means</sub>"
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "p<sub>slope</sub>"
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "N<sub>pass</sub>"
            
            if self.revana is not None:
                th = ET.SubElement(tr,'th')
                
        if self.revana is not None:
            #th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            #th.text = "&Delta;"
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "&Delta; &lt; %.2f"%(dtol)
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "p<sub>means</sub>"
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "p<sub>slope</sub>"
            th = ET.SubElement(tr,'th',attrib={'style':'text-align:center'})
            th.text = "N<sub>pass</sub>"
            th = ET.SubElement(tr,'th')

        nrow = 0
        if self.fwdana is not None:
            nrow = max(nrow,len(self.fwdana))
        if self.revana is not None:
            nrow = max(nrow,len(self.revana))

        for irow in range(nrow):
            tr = ET.SubElement(table,'tr')
            
            ftime = -1
            if self.fwdana is not None:
                if irow < len(self.fwdana):
                    ftime = self.fwdana[irow].offset / self.fwdana[0].n
            if self.revana is not None:
                if irow < len(self.revana):
                    ftime = self.revana[irow].offset / self.revana[0].n
            td = ET.SubElement(tr,'td')
            td.text = "%.2f"%(ftime)

            if self.fwdana is not None:
                if irow < len(self.fwdana):
                    
                    td = ET.SubElement(tr,'td')
                    td.text = "%0.2f"%(self.fwdana[irow].delta/self.beta)
                    #td.text = "F"
                    if self.fwdana[irow].delta_test:
                        #td.text = "T"
                        td.attrib["class"]="greenok"
                    #td.text = "%.4f %.4f"%(abs(self.fwdana[irow].delta),self.fwdana[irow].delta_tol)

                    td = ET.SubElement(tr,'td')
                    td.text = "%.3f"%(self.fwdana[irow].mean_p)
                    if self.fwdana[irow].mean_p > ptol:
                        td.attrib["class"]="greenok"
                    td = ET.SubElement(tr,'td')
                    td.text = "%.3f"%(self.fwdana[irow].linreg_p)
                    if self.fwdana[irow].linreg_p > ptol:
                        td.attrib["class"]="greenok"
                    td = ET.SubElement(tr,'td')
                    npass = int(self.fwdana[irow].delta_test) + \
                        int(self.fwdana[irow].mean_test) + \
                        int(self.fwdana[irow].linreg_test)
                    td.text = "%i"%(npass)
                    if npass > 1:
                        td.attrib["class"]="greenok"
                    

                        
                if self.revana is not None:
                    td = ET.SubElement(tr,'td')
                
            if self.revana is not None:
                if irow < len(self.revana):
                    td = ET.SubElement(tr,'td')
                    td.text = "%0.2f"%(self.revana[irow].delta/self.beta)
                    #td.text = "F"
                    if self.revana[irow].delta_test:
                        #td.text = "T"
                        td.attrib["class"]="greenok"
                    #td.text = "%.4f %.4f"%(abs(self.revana[irow].delta),self.revana[irow].delta_tol)

                        
                    td = ET.SubElement(tr,'td')
                    td.text = "%.3f"%(self.revana[irow].mean_p)
                    if self.revana[irow].mean_p > ptol:
                        td.attrib["class"]="greenok"
                    td = ET.SubElement(tr,'td')
                    td.text = "%.3f"%(self.revana[irow].linreg_p)
                    if self.revana[irow].linreg_p > ptol:
                        td.attrib["class"]="greenok"
                    td = ET.SubElement(tr,'td')
                    npass = int(self.revana[irow].delta_test) + \
                        int(self.revana[irow].mean_test) + \
                        int(self.revana[irow].linreg_test)
                    td.text = "%i"%(npass)
                    if npass > 1:
                        td.attrib["class"]="greenok"
                        
        return div
