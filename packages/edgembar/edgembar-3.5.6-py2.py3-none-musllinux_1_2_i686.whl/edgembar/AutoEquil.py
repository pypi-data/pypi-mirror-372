#!/usr/bin/env python3

def GetBeta(T=298.):
    k_au = 3.16681534222374e-06
    au_per_kcal = 1.59360145069066e-03
    k_kcal = ( k_au / au_per_kcal )
    #T = 298.
    return 1. / ( k_kcal * T );



def CptMeanAndStderr(xs):
    import numpy as np
    err = 0
    N = xs.shape[0]
    mu = 0
    if N > 1:
        err = np.sqrt( np.var(xs,ddof=1) / N )
    if N > 0:
        mu = np.mean(xs)
    return mu,err



def CptMeanAndVar(xs):
    import numpy as np
    err = 0
    N = xs.shape[0]
    if N > 1:
        err = np.var(xs,ddof=1)
    mu=0
    if N > 0:
        mu = np.mean(xs)
    return mu,err



def Ttest(a, b):
    import scipy.stats
    t,p_value = scipy.stats.ttest_ind(a,b,equal_var=False)
    return t,p_value



def Ttest_from_stats( na, mua, stderra, nb, mub, stderrb ):
    import numpy as np
    import scipy.stats
    stda = stderra*np.sqrt(na)
    stdb = stderrb*np.sqrt(nb)
    t,p = scipy.stats.ttest_ind_from_stats(mua,stda,na,mub,stdb,nb,equal_var=False)
    return t,p



def Ftest(a, b):
    import numpy as np
    import scipy.stats
    var1 = np.var(a, ddof=1)
    var2 = np.var(b, ddof=1)
    if var1 > var2:
        f = var1/var2
        p_value = 2*(1-scipy.stats.f.cdf(f, a.shape[0]-1, b.shape[0]-1))
    else:
        f = var2/var1
        p_value = 2*(1-scipy.stats.f.cdf(f, b.shape[0]-1, a.shape[0]-1))
    if p_value > 1.:
        p_value = 2-p_value
    return f, p_value



def Ftest_from_stats(na,stderra,nb,stderrb):
    import numpy as np
    import scipy.stats
    var1 = stderra*stderra*na
    var2 = stderrb*stderrb*nb
    if var1 > var2:
        f = var1/var2
        p_value = 2*(1-scipy.stats.f.cdf(f, na-1, nb-1))
    else:
        f = var2/var1
        p_value = 2*(1-scipy.stats.f.cdf(f, nb-1, na-1))
    if p_value > 1.:
        p_value = 2-p_value
    return f, p_value




def KSTestProb( alam ):
    import numpy as np
    EPS1 = 0.001
    EPS2 = 1.e-8
    a2 = -2.*alam*alam
    fac = 2.
    probks = 0.
    termbf = 0.
    for j in range(100):
        term = fac*np.exp(a2*(j+1)*(j+1))
        probks += term
        if abs(term) <= EPS1*termbf or abs(term) <= EPS2*probks:
            return probks
        fac = -fac
        termbf = abs(term)
    return 1.

def KSTestPValue( n1, n2, ks ):
    import numpy as np
    en = np.sqrt( (n1*n2)/(n1+n2) )
    return KSTestProb( (en+0.12+0.11/en)*ks )



def HaveTheSameMean(na,mua,stderra,nb,mub,stderrb,tol):
    import numpy as np
    res = True
    p = 1
    if na > 0 and nb > 0:
        err = np.sqrt( stderra**2+stderrb**2 )
        if err > 1.e-8:
            f,p = Ttest_from_stats(na,mua,stderra,nb,mub,stderrb)
            if tol > 0:
                res = p > tol
            else:
                res = abs(mua-mub) < np.sqrt( stderra**2+stderrb**2+1.e-8 )
    return res,p



def HaveTheSameVar(na,stderra,nb,stderrb,tol):
    import numpy as np
    res = True
    p = 1
    if na > 0 and nb > 0:
        err = np.sqrt( stderra**2+stderrb**2 )
        if err > 1.e-8:
            f,p = Ftest_from_stats(na,stderra,nb,stderrb)
            res = p > tol
    return res, p



def FromSameDist(x,y,tol):
    from scipy.stats import kstest
    ks_same = True
    ks_p = 1.0
    if len(x) > 0 and len(y) > 0:
        ksres = kstest(x,y)
        ks = ksres.statistic
        #ks_p = ksres.pvalue
        ks_p =  KSTestPValue( len(x), len(y), ks )
        ks_same = ks_p > tol
    return ks_same, ks_p


def StatIneff(arr):
    import numpy as np    
    A = np.copy( arr )
    N = A.shape[0]
    g=1
    if N > 1:
        mu = np.mean(A)
        dA = A.astype(np.float64) - mu
        s2 = np.mean(dA**2)
        if s2 > 0:
            mintime=3
            t = 1
            inc = 1
            while(t<N-1):
                C = np.sum( dA[0:(N - t)] * dA[t:N] ) / (float(N - t) * s2)
                if (C <= 0.0) and (t > mintime):
                    break
                g += 2.0 * C * (1.0 - float(t) / float(N)) * float(inc)
                t += inc

        g = int(round(max(g,1.0)))
        #g = max(int(g),1)
    return g



def GetSampleStride( xs ):
    import numpy as np
    N = xs.shape[0]
    g = StatIneff(xs)
    #gold = g
    #s = min(g,2)
    s = max(g//2,1)
    #print("  g INIT",g)
    while g > 1:
        if s >= N//2:
            break
        else:
            g = StatIneff( xs[::s] )
            #print("s,g     ",s,g)
            #if g == gold:
            #    break
            #gold = g
            if g > 1:
                s += max(g//2,1)
    return s



def AreTheSame(a,b,tol):
    import numpy as np
    #return np.abs(a.avg-b.avg) < np.sqrt(a.err**2+b.err**2 + 1.e-8)
    return HaveTheSameMean(a.un,a.cavg,a.cerr,b.un,b.cavg,b.cerr,tol)








def CalcWeightLinearRegression(xs,ys,sigma=None):
    import numpy as np
    import scipy
    import scipy.stats
    
    xs = np.array(xs)
    ys = np.array(ys)
    n  = xs.shape[0]
    
    X = np.zeros( (n,2) )
    X[:,1] = 1.
    X[:,0] = xs[:]

    
    
    if sigma is None:
        #
        # y = X.p
        #
        # y-X.p = e
        # (y-X.p)^T . (y-X.p) = e^2
        # y^T.t - 2 * y^T.X.p + p^T.X^T.X.p = e^2
        #
        # -2 * y^T.X + 2 * p^T.X^T.X = 0
        # p^T.X^T.X = y^T.X
        # X^T.X.p = X^T.y
        #
        # p = (X^T.X)^{-1}.X^T.y
        #
        p   = np.linalg.inv( X.T @ X ) @ X.T @ ys

        yp  = X @ p
        SSE = np.sum( (ys-yp)**2 )
        if n > 2:
            ResidualSE = np.sqrt( SSE / (n-2) )
        else:
            ResidualSE = np.sqrt( SSE )

        mx  = np.mean(xs)
        den = np.sum( (xs-mx)**2 )
        if den > 1.e-16:
            sb  = ResidualSE / np.sqrt( den )
        else:
            sb = 0.
        t = p[0] / max(sb,1.e-16)
        my  = np.mean(ys)
        wyy = np.dot( ys-my, ys-my )
        wxx = np.dot( xs-mx, xs-mx )
        wxy = np.dot( xs-mx, ys-my )
        den = wxx*wyy
        if den > 1.e-16:
            cor = wxy/np.sqrt(den)
        else:
            cor = 0.
    else:
        #
        # (y-X.p)^T . W . (y-X.p) = e^2
        # y^T.W.y - 2 * y^T.W.X.p + p^T.X^T.W.X.p = e^2
        #
        # -2 * y^T.W.X + 2 * p^T.X^T.W.X = 0
        # p^T.X^T.W.X = y^T.W.X
        # X^T.W.X.p = X^T.W.y
        #
        # p = (X^T.W.X)^{-1}.X^T.W.y
        #

        S = np.array( [1/s for s in sigma] )
        W = S*S

        SX = S.reshape(len(S),1) * X
        Sy = S * ys

        p = np.linalg.inv( SX.T @ SX ) @ SX.T @ Sy
        yp  = X @ p

        Syp = S * yp
        dy = ys-yp
        SSE = sum( W*dy*dy )
        if n > 2:
            ResidualSE = np.sqrt( SSE / (n-2) )
        else:
            ResidualSE = np.sqrt( SSE )
        mx  = np.mean(xs)
        dx = xs-mx
        den = sum( W*dx*dx )
        if den > 1.e-16:
            sb = ResidualSE / np.sqrt( den )
        else:
            sb = 0.        
        t = p[0] / max(sb,1.e-16)
        
    
        #print("%15.10f %15.10f %15.10f %15.10f\n"%(SSE,ResidualSE,sb,t))
        wnorm = sum(W)
        W /= wnorm
        mx = sum(W*xs)
        my = sum(W*ys)
        dy = ys-my
        dx = xs-mx
        wyy = sum( W*dy*dy )
        wxx = sum( W*dx*dx )
        wxy = sum( W*dx*dy )
        den = wxx*wyy
        if den > 1.e-16:
            cor = wxy/np.sqrt(den)
        else:
            cor = 0.

    pval = scipy.stats.t.sf(np.abs(t), n-2)*2

    return p[0],p[1],cor,pval













class TimeseriesSegment(object):
    def __init__( self, istart, istop, xs ):
        import numpy as np
        self.istart = istart
        self.istop = istop

        c = xs[istart:istop]
        self.s = GetSampleStride(c)
        t = xs[istart:istop:self.s]
        
        self.cn = len(c)
        self.un = len(t)

        self.cavg = 0
        self.uavg = 0
        self.uvar = 0
        self.ustd = 0
        self.cvar = 0
        self.cstd = 0
        self.uerr = 0
        self.cerr = 0
        
        if self.cn > 0:
            dof=0
            if self.cn > 1:
                dof=1
            self.cavg = np.mean(c)
            self.cvar = np.var(c,ddof=dof)
            self.cstd = np.sqrt(self.cvar)
            
        if self.un > 0:
            dof=0
            if self.un > 1:
                dof=1
            self.uavg = np.mean(t)
            self.uvar = np.var(t,ddof=dof)
            self.ustd = np.sqrt( self.uvar )
            self.uerr = np.sqrt( self.uvar / self.un )
            self.cerr = np.sqrt( self.cvar / self.un )

                
        

        
class AnalysisSegment(object):
    def __init__( self, iblk, blks, xs, tol ):
        import numpy as np
        
        self.ptol = tol
        self.absptol = abs(tol)

        do_ks = True
        
        nblk = len(blks)
        N = xs.shape[0]
        fwd_start = 0
        fwd_stop  = blks[iblk][-1] + 1
        rev_start = blks[nblk-iblk-1][0]
        rev_stop  = blks[nblk-1][-1] + 1
        self.fwd = TimeseriesSegment( fwd_start, fwd_stop, xs )
        self.rev = TimeseriesSegment( rev_start, rev_stop, xs )
        prod_start = blks[iblk][0]
        self.prod = TimeseriesSegment( prod_start, N, xs )
        #s = self.prod.s
        #halves = np.array_split( range(prod_start,N,s), 2 )
        imid = (prod_start + N)//2 + 1
        self.first = TimeseriesSegment( prod_start, imid, xs )
        self.last  = TimeseriesSegment( imid, N, xs )
        #self.first.n = halves[0].shape[0]
        #self.first.avg, self.first.err = CptMeanAndStderr( xs[halves[0]] )
        #self.last.n = halves[1].shape[0]
        #self.last.avg, self.last.err = CptMeanAndStderr( xs[halves[1]] )
        
        self.fwdrev_mean, self.fwdrev_mean_p = \
            AreTheSame( self.fwd, self.rev, tol )

        self.fwdrev_dist = True
        self.fwdrev_dist_p = 1
        if do_ks:
            self.fwdrev_dist, self.fwdrev_dist_p \
                = FromSameDist( xs[fwd_start:fwd_stop],
                                xs[rev_start:rev_stop], tol )
            
        self.halves_mean, self.halves_mean_p = \
            AreTheSame( self.first, self.last, tol )
        
        self.halves_dist = True
        self.halves_dist_p = 1
        if do_ks:
            self.halves_dist, self.halves_dist_p = \
                FromSameDist( xs[self.first.istart:self.first.istop],
                              xs[self.last.istart:self.last.istop], tol )
            
        self.fwdrev = self.fwdrev_mean and self.fwdrev_dist
        self.halves = self.halves_mean and self.halves_dist

        self.sec=None
        self.seg=None
        self.segsec = None
        self.segsec_mean = None
        self.segsec_mean_p = None
        self.segsec_dist = None
        self.segsec_dist_p = None
        self.segsec_prod_n = None
        mblk = int(nblk/2+0.5)
        #for b in range(len(blks)):
        #    print(f"{b:2} {blks[b][0]:6}  {blks[b][-1]:6}")
        if iblk < mblk and nblk > 1:
            sec_start = blks[mblk][0]
            sec_stop = blks[nblk-1][-1] + 1
            #print(nblk,mblk,sec_start,sec_stop)
            self.sec = TimeseriesSegment( sec_start, sec_stop, xs )
            seg_start = blks[iblk][0]
            seg_stop = blks[mblk-1][-1] + 1
            self.seg = TimeseriesSegment( seg_start, seg_stop, xs )

            #print(seg_start,seg_stop,sec_start,sec_stop)
            
            self.segsec_mean, self.segsec_mean_p = \
                AreTheSame( self.seg, self.sec, tol )
            
            self.segsec_dist = True
            self.segsec_dist_p = 1
            if do_ks:
                self.segsec_dist, self.segsec_dist_p = \
                    FromSameDist( xs[seg_start:seg_stop],
                                  xs[sec_start:sec_stop], tol )
            self.segsec = self.segsec_mean and self.segsec_dist

            proposed_prod = TimeseriesSegment( seg_start, sec_stop, xs )
            self.segsec_prod_n =  proposed_prod.un

            
        

def MakeChunks( istart, istop, nchunks ):
    import numpy as np
    nchunks = min(istop-istart,nchunks)
    return np.array_split( range(istart,istop), nchunks )



def ChunkAnalysis( fstart, fstop, nchunks, xs, tol ):
    N = xs.shape[0]
    istart = max(0,int( fstart * N ))
    istop = min(N,int( fstop * N ))
    blks = MakeChunks(istart,istop,nchunks)
    segs = [ AnalysisSegment(iblk,blks,xs,tol)
             for iblk in range(len(blks)) ]
    return segs


def AutoEquil( fstart, fstop, nchunks, data, tol, maxeq=0.75 ):
    return AutoEquil_v5( fstart, fstop, nchunks, data, tol, maxeq )


def AutoEquil_v2( fstart, fstop, nchunks, data, tol, maxeq=0.75 ):
    import numpy as np
    ana = ChunkAnalysis( fstart, fstop, nchunks, data, tol )
    equil = False
    seg = None
    lev = 0
    for iblk in range(nchunks):
        if lev == 0 and (ana[iblk].fwdrev or iblk > nchunks//2):
            lev = 1
        if lev == 1 and ana[iblk].halves:
            lev = 2
            seg = ana[iblk]
            equil = True
            break
        if iblk == int(nchunks*maxeq+0.5):
            equil = False
            seg = ana[iblk]
            break
    if seg is None and nchunks == 1:
        seg = ana[0]
    return equil,seg


def AutoEquil_v3( fstart, fstop, nchunks, data, tol, maxeq=0.75 ):
    import numpy as np
    ana = ChunkAnalysis( fstart, fstop, nchunks, data, tol )
    equil = False
    seg = None
    nmid = int(nchunks/2+0.5)
    pblk = nmid
    for iblk in range(nmid-1,-1,-1):
        if ana[iblk].segsec_dist:
            pblk = iblk
        else:
            break
    for iblk in range(pblk,nchunks):
        if ana[iblk].halves:
            seg = ana[iblk]
            equil = True
            break
        if iblk == int(nchunks*maxeq+0.5):
            equil = False
            seg = ana[iblk]
            break
    if seg is None and nchunks == 1:
        seg = ana[0]
    return equil,seg
    

def AutoEquil_v4( fstart, fstop, nchunks, data, tol, maxeq=0.75 ):
    import numpy as np
    ana = ChunkAnalysis( fstart, fstop, nchunks, data, tol )
    equil = False
    seg = None
    qblk = int(nchunks*0.25+0.5)
    mblk = int(nchunks*0.50+0.5)
    pblk = mblk
    for iblk in range(mblk-1,-1,-1):
        if ((ana[iblk].segsec_dist or ana[iblk].segsec_mean) and iblk >= qblk) \
           or (ana[iblk].segsec_dist and ana[iblk].segsec_mean):
            pblk = iblk
        elif iblk < qblk:
            break
    for iblk in range(pblk,nchunks):
        if ana[iblk].halves_mean:
            seg = ana[iblk]
            equil = True
            break
        if iblk == int(nchunks*maxeq+0.5):
            # if ana[iblk].prod passes t-test against ana[pblk].prod, then
            # accept ana[pblk] as the production segment; otherwise we are
            # not converged
            imax = int(len(data)*maxeq)
            blks = [ range(imax,len(data)) ]
            last = AnalysisSegment(0,[ range(imax,len(data)) ],data,tol)
            equil,p = AreTheSame( last.prod, ana[pblk].prod, tol )
            if equil:
                seg = ana[pblk]
            else:
                seg = last
            break
    if seg is None and nchunks == 1:
        seg = ana[0]
    return equil,seg,ana
    

def AutoEquil_v5( fstart, fstop, nchunks, data, tol, maxeq=0.75 ):
    import numpy as np
    ana = ChunkAnalysis( fstart, fstop, nchunks, data, tol )
    equil = False
    seg = None
    qblk = int(nchunks*0.25+0.5)
    mblk = min(int(nchunks*0.50+0.5),nchunks-1)
    fblk = int(nchunks*maxeq+0.5)
    pblk = mblk

    ntarget = ana[mblk].prod.un
    for iblk in range(mblk-1,-1,-1):
        isdiff = not ana[iblk].segsec_dist and not ana[iblk].segsec_mean
        
        morepts = ana[iblk].segsec_prod_n >= ntarget
        #print("morepts",iblk,morepts,ana[iblk].segsec_prod_n,ntarget)

        if iblk >= qblk:
            match = (ana[iblk].segsec_dist or ana[iblk].segsec_mean)
        else:
            match = ana[iblk].segsec_dist and ana[iblk].segsec_mean
            
        #print(f"{iblk:3} {ana[iblk].seg.istart:5} {ana[iblk].seg.istop:6} {ana[iblk].seg.s:4} {ana[iblk].seg.un:6} {ana[iblk].seg.cavg:9.3f} {ana[iblk].seg.cerr:7.3f} {ana[iblk].sec.istart:5} {ana[iblk].sec.istop:6} {ana[iblk].sec.s:4} {ana[iblk].sec.un:6} {ana[iblk].sec.cavg:9.3f} {ana[iblk].sec.cerr:7.3f}  {ana[iblk].segsec_mean_p:7.3f} {ana[iblk].segsec_dist_p:7.3f} {match:1} {morepts:1}")
        
        if match and morepts:
            pblk = iblk
            ntarget = ana[iblk].segsec_prod_n
        elif iblk < qblk:
            break
        
    #print(f"Final pblk: {pblk:2}")
    #f"{qblk:3} {ana[qblk].segsec_mean:1} {ana[qblk].segsec_dist:1}")
    # pblk = mblk

    
    # if ana[qblk].segsec_mean:
    #     pblk = qblk
    #     for iblk in range(qblk-1,-1,-1):
    #         if ana[iblk].segsec_dist and ana[iblk].segsec_mean:
    #             pblk = iblk
    #         else:
    #             break
    # else:
    #     for iblk in range(qblk+1,mblk):
    #         if ana[iblk].segsec_mean:
    #             pblk=iblk
    #             break

    ntarget = 0
    for iblk in range(min(pblk,fblk),nchunks):
        #print(f"halves iblk: {iblk} {ana[iblk].halves_mean:2}")
        if ana[iblk].halves_mean:
            #print("size",iblk,ana[iblk].prod.n)
            #if ana[iblk].prod.n >= ntarget or not equil:
            seg = ana[iblk]
            equil = True
            #ntarget = ana[iblk].prod.n
            #continue
            break
            
        if iblk == fblk and not equil:
            # if ana[iblk].prod passes t-test against ana[pblk].prod, then
            # accept ana[pblk] as the production segment; otherwise we are
            # not converged
            
            imax = int(len(data)*maxeq)
            blks = [ range(imax,len(data)) ]
            last = AnalysisSegment(0,blks,data,tol)
            #print("blks",blks)
            #print(last.prod.istart,last.prod.istop)
            equil,p = AreTheSame( last.prod, ana[pblk].prod, tol )
            # print(f"not conv same mean? {equil} {p:7.3f} "
            #       f"{ana[pblk].prod.un} {last.prod.un} {imax}")
            # print(f"{ana[pblk].prod.cavg:13.4e} +- {ana[pblk].prod.cerr:13.4e} "
            #       f"{last.prod.cavg:13.4e} +- {last.prod.cerr:13.4e}")
            #if equil:
            #    print("Are the same ",ana[pblk].prod.istart)
            #    seg = ana[pblk]
            #else:
            seg = last
            break
    if seg is None and nchunks == 1:
        seg = ana[0]
    #print(f"final result: {seg.prod.istart:4} {seg.prod.s:1} {equil}")
    return equil,seg,ana
    



def AutoSubsample_orig( seg, data, tol, minsamples=50, maxsamples=10000, dbg=False ):
    import numpy as np
    from scipy.stats import kstest

    
    s = seg.prod.s
    istart = seg.prod.istart
    istop = seg.prod.istop
    nprop = data.shape[1]

    prod = data[istart:istop:s,:]
    refn = prod.shape[0]

    if refn <= minsamples:
        return istart, istop, s
    
    refmus = []
    referrs = []
    for i in range(prod.shape[1]):
        mu,err = CptMeanAndStderr(prod[:,i])
        refmus.append(mu)
        referrs.append(err)

    sok = s
    for g in range(s+1,(istop-istart)//2):
        
        sample = data[istart:istop:g,:]
        n = sample.shape[0]
        if n > maxsamples:
            continue
        if n < minsamples:
            break
        
        nprop_with_both_same = 0
        nprop_with_both_diff = 0
        nprop_with_same_ks = 0

        if dbg:
            print("s: %3i n: %6i sref: %3i nref %6i"%(g,n,s,refn))

        maxstat = 0
        for i in range(prod.shape[1]):
            stat = StatIneff( sample[:,i] )
            maxstat = max(maxstat,stat)

        if maxstat > 1:
            if dbg:
                print("skipping because max stat ineff > 1",maxstat)
            continue
            
        for i in range(prod.shape[1]):
            mu,err = CptMeanAndStderr(sample[:,i])
            mu_same, mu_p = HaveTheSameMean(refn,refmus[i],referrs[i],
                                            n,mu,err,tol)
            var_same, var_p = HaveTheSameVar(refn,referrs[i],
                                             n,err,tol)
            
            ks_same = True
            ks_p = 1
            if np.sqrt( err*err + referrs[i]*referrs[i] ) > 0:
                ksres = kstest(prod[:,i],sample[:,i])
                ks_same = ksres.pvalue > tol
                ks_p = ksres.pvalue
            
            if (not mu_same) and (not var_same) and (not ks_same):
                nprop_with_both_diff += 1
            if mu_same and var_same and ks_same:
                nprop_with_both_same += 1
            if ks_same:
                nprop_with_same_ks += 1

            if dbg:
                print("%5i %9.3f +- %7.3f"%(i,mu,err*np.sqrt(n)),
                      "   %9.3f +- %7.3f"%(refmus[i],referrs[i]*np.sqrt(refn)),
                      "   %5.2f %5.2f %5.2f"%(mu_p,var_p,ks_p),
                      " %6s %6s %6s"%(mu_same,var_same,ks_same))
            
        if nprop_with_both_diff == 0:
            if nprop_with_both_same > 0 and nprop_with_same_ks == nprop:
                if dbg:
                    print("New best s: %3i"%(g))
                sok = g
        else:
            break
        
    return istart, istop, sok



def AutoSubsample( seg, data, tol, aux=None, minsamples=50, maxsamples=10000, dbg=False ):
    import numpy as np
    from scipy.stats import kstest

    naux = 0
    if aux is not None:
        naux = aux.shape[1]
        if aux.shape[0] != data.shape[0]:
            raise Exception(("Size mismatch:"
                             f"data.shape[0] = {data.shape[0]} but "
                             f"aux.shape[0] = {aux.shape[0]}"))
    
    s = seg.prod.s
    istart = seg.prod.istart
    istop = seg.prod.istop

    pdata = data[istart:istop]
    prod = AnalysisSegment(0,[range(istart,istop)],data,tol)
    #prod = data[istart:istop:s]
    refn = prod.prod.un
    refmu = prod.prod.cavg
    referr = prod.prod.cerr
    #refmu,referr = CptMeanAndStderr(prod)

    max_start = int(istop*0.75+0.5)
    
    if refn <= minsamples:
        return istart, istop, s
    
    auxmus = []
    auxerrs = []
    if naux > 0:
        auxprod = aux[istart:istop,:]
        for i in range(naux):
            #mu,err = CptMeanAndStderr(auxprod[:,i])
            mu = np.mean(auxprod[:,i])
            std = np.std(auxprod[:,i],ddof=1)
            auxmus.append(mu)
            auxerrs.append( std / np.sqrt(refn) )

    sok = None
    # big_s = None
    # big_istart = None
    # big_n = None

    first_n = refn
    first_istart = istart
    first_s = s

    #print("AutoSample",max_start)
    
    while sok is None:

        if istart > max_start:
            #print("Exit because ",istart,max_start)
            break
        
        for g in range(s+1,(istop-istart)//2):
        
            sample = data[istart:istop:g]
            n = sample.shape[0]
            if n > maxsamples:
                continue
            if n < minsamples:
                break
        
            seg = ChunkAnalysis(0,1,1,sample,tol)[0]
            #if seg.prod.s > 1:
            #    continue
        
            halves_same, halves_p = HaveTheSameMean\
                ( seg.first.un, seg.first.cavg, seg.first.cerr,
                  seg.last.un, seg.last.cavg, seg.last.cerr, tol )

            full_same, full_p = HaveTheSameMean\
                ( seg.prod.un, seg.prod.cavg, seg.prod.cerr,
                  refn, refmu, referr, tol )
        
            var_same, var_p = HaveTheSameVar\
                ( seg.prod.un, seg.prod.cerr,
                  refn, referr, tol )
        
            ks_same, ks_p = True, 1
            if referr > 0:
                ks_same, ks_p = FromSameDist(pdata,sample,tol)

            aux_same = True
            for i in range(naux):
                same,p = FromSameDist(aux[istart:istop,i],
                                      aux[istart:istop:g,i],tol)
                if not same:
                    aux_same = False
                    break
        
            if dbg:
                print(f"s: {g:3} n: {n:6} sref: {s:3} nref {refn:6} "
                      f"{full_same:1} "
                      f"{halves_same:1} "
                      f"{ks_same:1} "
                      f"{var_same:1} "
                      f"{aux_same:1} "
                      f"fh: {seg.first.cavg:7.2f} +- {seg.first.cerr:5.2f} "
                      f"lh: {seg.last.cavg:7.2f} +- {seg.last.cerr:5.2f} "
                      f"seg: {seg.prod.cavg:7.2f} +- {seg.prod.cerr:5.2f} "
                      f"ref: {refmu:7.2f} +- {referr:5.2f}")

            # if n > big_n and istart <= max_start:
            #     big_n = n
            #     big_s = g
            #     big_istart = istart
                
            if full_same and halves_same and ks_same and aux_same: # and var_same:
                if dbg:
                    print("New best s: %3i"%(g))
                sok = g
            elif not full_same and not halves_same and not ks_same:
                break

        if sok is None:
            n = len(data[istart:istop:s])
            if n <= maxsamples:
                sok = s
            else:
                # (istop-istart)/s = maxsamples
                # istop-istart = s*maxsamples
                # istop-s*maxsamples = istart
                #nprime = (maxsamples + n)//2
                #istart = istop-s*nprime
                
                istart += max(1,s//2)
                if istart > max_start:
                    sok = first_s
                    istart = first_istart
                    break
                #print("RESTART")

    if istart > max_start:
        #print("Set first sok,istart",first_s,first_istart)
        istart = first_istart
        sok = first_s
        
    return istart, istop, sok




def SimAnalysis( fstart, fstop, nchunks, sim_efep, fwd_efep, rev_efep, tol ):
    import numpy as np
    from pathlib import Path
    import sys

    #beta = GetBeta()
    beta = 1
    
    sim_efep = Path( sim_efep )
    if sim_efep.is_file():
        sim_data = np.loadtxt(str(sim_efep))[:,1]
        #sim_data -= np.mean(sim_data)
    else:
        raise Exception(f"File not found: {sim_efep}")
    
    fwd_ana = None
    if fwd_efep is not None:
        fwd_efep = Path( fwd_efep )
        if fwd_efep.is_file():
            fwd_data = np.loadtxt(str(fwd_efep))[:,1]
            #fwd_data -= np.mean(fwd_data)
        else:
            raise Exception(f"File not found: {fwd_efep}")
        fwd_ana = ChunkAnalysis( fstart, fstop, nchunks,
                                   beta * (fwd_data-sim_data), tol )

    rev_ana = None
    if rev_efep is not None:
        rev_efep = Path( rev_efep )
        if rev_efep.is_file():
            rev_data = np.loadtxt(str(rev_efep))[:,1]
            #rev_data -= np.mean(rev_data)
        else:
            raise Exception(f"File not found: {rev_efep}")
        rev_ana = ChunkAnalysis( fstart, fstop, nchunks,
                                 beta * (rev_data-sim_data), ptol )
        
    nblk = 0
    istarts = None
    strides = None
    if rev_ana is not None:
        nblk = len(rev_ana)
        istarts = [ s.prod.istart for s in rev_ana ]
        strides = [ s.prod.s for s in rev_ana ]
    if fwd_ana is not None:
        nblk = len(fwd_ana)
        istarts = [ s.prod.istart for s in fwd_ana ]
        if strides is not None:
            strides = [ max(s.prod.s,stride)
                        for s,stride in zip(fwd_ana,strides) ]
        else:
            strides = [ s.prod.s for s in fwd_ana ]

    fwd_conv = 0
    rev_conv = 0
    fwd_conv_blk = -1
    rev_conv_blk = -1
    for i in range(nblk):
        plo = i / nblk
        phi = (i+1) / nblk
        ts = "%.2f %.2f %5i %3i "%(plo,phi,istarts[i],strides[i])
        
        fwd = ""
        if fwd_ana is not None:
            a = fwd_ana[i]
            if fwd_conv == 0 and a.fwdrev:
                fwd_conv = 1
            if fwd_conv == 1 and a.halves:
                fwd_conv = 2
                fwd_conv_blk = i
            fwd = (f"{a.fwd.avg:8.3f} {a.fwd.err:8.3f} "
                   f"{a.rev.avg:8.3f} {a.rev.err:8.3f} "
                   f"{a.fwdrev:3} "
                   f"{a.first.avg:8.3f} {a.first.err:8.3f} "
                   f"{a.last.avg:8.3f} {a.last.err:8.3f} "
                   f"{a.halves:3}  "
                   f"{fwd_conv:3}  ")
            
        rev = ""
        if rev_ana is not None:
            a = rev_ana[i]
            if rev_conv == 0 and a.fwdrev:
                rev_conv = 1
            if rev_conv == 1 and a.halves:
                rev_conv = 2
                rev_conv_blk = i
            rev = (f"{a.fwd.avg:8.3f} {a.fwd.err:8.3f} "
                   f"{a.rev.avg:8.3f} {a.rev.err:8.3f} "
                   f"{a.fwdrev:3} "
                   f"{a.first.avg:8.3f} {a.first.err:8.3f} "
                   f"{a.last.avg:8.3f} {a.last.err:8.3f} "
                   f"{a.halves:3}  "
                   f"{rev_conv:3}  ")
            
        sys.stdout.write(f"{ts} {fwd} {rev}\n")
    conv_blk = max(rev_conv_blk,fwd_conv_blk)
    if fwd_ana is not None:
        sys.stdout.write(f"Forward-dU feq: {fwd_conv_blk/nblk:5.2f}  g: {fwd_ana[conv_blk].prod.s}\n")
    if rev_ana is not None:
        sys.stdout.write(f"Reverse-dU feq: {rev_conv_blk/nblk:5.2f}  g: {rev_ana[conv_blk].prod.s}\n")
    sys.stdout.write(f"dU feq: {conv_blk/nblk:5.2f}  g: {strides[conv_blk]}\n")





class SliceResult(object):
    def __init__(self):

        self.g = 1
        self.n = 0
        self.offset = 0
        
        self.mean_test=False
        self.mean_p = 0
        self.mean_fhalf = 0
        self.mean_lhalf = 0
        self.stde_fhalf = 0
        self.stde_lhalf = 0

        self.delta_test=False
        self.delta_tol=0
        self.delta=0
        
        self.linreg_test=False
        self.linreg_p = 0
        self.linreg_m = 0
        self.linreg_b = 0

        self.seg_mean = 0
        self.seg_stde = 0
        
        self.test = False

        
def AnalyzeSlice(fwdxs,ptol,dtol,offset=0):
    import numpy as np
    from scipy.stats import linregress
    
    tres = SliceResult()
    tres.n = len(fwdxs)
    tres.offset = offset
    fwdxs = np.array(fwdxs,copy=True)
    
    g = StatIneff(fwdxs)
    g = max(g,1)
    #print(g,fwdxs)
    uxs = fwdxs[::g]
    imid = 1+len(uxs)//2
    m1,e1 = CptMeanAndStderr(uxs[:imid])
    m2,e2 = CptMeanAndStderr(uxs[imid:])
    tres.mean_test,tres.mean_p = HaveTheSameMean(imid,m1,e1,len(uxs)-imid,m2,e2,ptol)
    tres.g = g
    tres.mean_fhalf = m1
    tres.stde_fhalf = e1
    tres.mean_lhalf = m2
    tres.stde_lhalf = e2

    tres.delta_tol = dtol
    tres.delta = abs(m1-m2)
    tres.delta_test = tres.delta < tres.delta_tol    
    
    ts = np.linspace(0,len(fwdxs)-1,len(fwdxs))
    res = linregress(ts,fwdxs)
    tres.linreg_m = res.slope
    tres.linreg_b = res.intercept
    tres.linreg_p = res.pvalue
    tres.linreg_test = tres.linreg_p > ptol
    #if (tres.mean_test or tres.delta_test) and tres.linreg_test:
    npass = int(tres.mean_test) + int(tres.delta_test) + int(tres.linreg_test)
    tres.test = npass > 1
    return tres


def SliceAnalysis( fstart, fstop, fmaxeq, fdelta, xs, ptol, dtol ):
    import numpy as np
    xs = np.array(xs,copy=True)
    N = xs.shape[0]
    istart  = max(0,int( fstart * N ))
    istop   = min(N,int( fstop * N ))
    imax    = int(istart + fmaxeq*(istop-istart))

    idelta = int((istop-istart)*fdelta + 0.5)
    idelta = max(idelta,1)
    blkstarts = []
    for i in range(istart,imax+1,idelta):
        blkstarts.append(i)
    if blkstarts[-1] < imax:
        blkstarts.append(imax)

    nb = len(blkstarts)
    if nb > 2:
        if blkstarts[nb-1]-blkstarts[nb-2] <= 0.5*(blkstarts[nb-2]-blkstarts[nb-3]):
            blkstarts[nb-2] = blkstarts[nb-1]
            blkstarts = blkstarts[:-1]

    #print(blkstarts)
    #print([(b-istart)/(istop-istart) for b in blkstarts])
         
    blks = []
    for i in blkstarts:
        blks.append( AnalyzeSlice(xs[i:istop],ptol,dtol,offset=i) )
        #if blks[-1].test:
        #    break

    blkstarts.append(N)
    for i in range(len(blkstarts)-1):
        ilo = blkstarts[i]
        ihi = blkstarts[i+1]
        blks[i].seg_mean = np.mean(xs[ilo:ihi])
        blks[i].seg_stde = np.sqrt( (1./(ihi-ilo)) * np.var(xs[ilo:ihi]) )
        
    return blks
