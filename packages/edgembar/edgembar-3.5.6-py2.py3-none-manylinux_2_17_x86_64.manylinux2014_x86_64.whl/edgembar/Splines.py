#!/usr/bin/env python3

import numpy as np

class LinearSplineWithErrorProp(object):
    """Performs linear interpolation and trapezoidal integration
    with analytic error propagation

    Attributes
    ----------
    x : numpy.ndarray, shape=(n,)
        The input x-values. These must be in ascending order.

    Methods
    -------
    """
    
    def __init__(self, x):
        """Constructor
        
        Parameters
        ----------
        x : numpy.ndarray, shape=(n,)
            The input x-values. These must be in ascending order.
        """
        n = len(x)
        self.x = np.array(x,copy=True)

        
    def GetValues(self,y,xnew):
        """Returns the interpolated values at xnew, given the input y-values
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        xnew : numpy.ndarray, shape=(m,)
            The output x-values

        Returns
        -------
        ynew : numpy.ndarray, shape=(m,)
            The output y-values of the linear spline
        """
        
        m = len(self.x)
        N = len(self.x)

        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
           
        n = len(xnew)
        ynew = np.zeros( (n,) )
        for i in range(n):
            j = max(0,min(len(self.x)-2,np.searchsorted(self.x, xnew[i]) - 1))
            lamw = xnew[i] - self.x[j]
            lodx = lamw / (self.x[j+1]-self.x[j])
            c1 = 1 - lodx
            c2 = lodx
            ynew[i] = c1 * y[j] + c2 * y[j+1]
            
        return ynew

    
    def GetValuesAndErrors(self,y,dy,xnew):
        """Returns the interpolated values and propagated errors
        at xnew, given the input y-values and input error values
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        dy : numpy.ndarray, shape=(n,)
            The input error values. This must be the same shape as the 
            input x-values.  These should correspond to standard
            deviations (or standard errors) rather than variances.

        xnew : numpy.ndarray, shape=(m,)
            The output x-values

        Returns
        -------
        ynew : numpy.ndarray, shape=(m,)
            The output y-values of the linear spline

        dynew : numpy.ndarray, shape=(m,)
            The propagated uncertainty of the output values
        """
        m = len(self.x)
        N = len(self.x)

        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
        if dy is not None:
            if N != len(dy):
                raise Exception(f"expected dy size {N} but received {len(dy)}")
                
        n = len(xnew)
        ynew = np.zeros( (n,) )
        dynew = np.zeros( (n,) )
        for i in range(n):
            j = max(0,min(len(self.x)-2,np.searchsorted(self.x, xnew[i]) - 1))
            lamw = xnew[i] - self.x[j]
            lodx = lamw / (self.x[j+1]-self.x[j])
            c1 = 1 - lodx
            c2 = lodx
            ynew[i] = c1*y[j] + c2*y[j+1]
            dynew[i] = np.sqrt(c1**2*dy[j]**2 + c2**2*dy[j+1]**2 )
        return ynew,dynew

    
    def Integrate(self,y,dy):
        """Returns integral of the linear spline over the range
        of input x-values.
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        dy : numpy.ndarray, shape=(n,)
            The input error values. This must be the same shape as the 
            input x-values.  These should correspond to standard
            deviations (or standard errors) rather than variances.
            This parameter is allowed to be None, in which case
            the uncertainty of the integral is reported as None

        Returns
        -------
        IntF : float
            The integral of the linear spline from x=self.x[0] to self.x[-1]

        dIntF : float
            The propagated uncertainty of the integral. Returns None
            value if dy was None
        """

        m = len(self.x)
        N = len(self.x)

        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
        if dy is not None:
            if N != len(dy):
                raise Exception(f"expected dy size {N} but received {len(dy)}")
                
        inty = 0
        wts = np.zeros( (m,) )
        for i in range(m-1):
            dx = self.x[i+1]-self.x[i]
            w = dx/2
            wts[i] += w
            wts[i+1] += w
        inty = np.dot(wts,y)
        if dy is not None:
            dinty = np.sqrt( np.dot(wts**2,dy**2) )
        return inty,dinty

    
    def RunningIntegral(self,y,dy):
        """Returns the running integral of the linear spline over the range
        of input x-values.
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        dy : numpy.ndarray, shape=(n,)
            The input error values. This must be the same shape as the 
            input x-values.  These should correspond to standard
            deviations (or standard errors) rather than variances.
            This parameter is allowed to be None, in which case
            the uncertainty of the integral is reported as None

        Returns
        -------
        IntF : numpy.ndarray, shape=(n,)
            The running integral from x=self.x[0] to self.x[i] for each
            input x-value. The first element is 0.0, by definition

        dIntF : numpy.ndarray, shape=(n,)
            The propagated uncertainty in the running integral values
        """

        m = len(self.x)
        N = len(self.x)

        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
        if dy is not None:
            if N != len(dy):
                raise Exception(f"expected dy size {N} but received {len(dy)}")
                
        Inty = np.zeros( (m,) )
        dInty = np.zeros( (m,) )
        wts = np.zeros( (m,) )
        for i in range(m-1):
            dx = self.x[i+1]-self.x[i]
            w = dx/2
            wts[i] += w
            wts[i+1] += w
            Inty[i+1] = np.dot(wts,y)
            if dy is not None:
                dInty[i+1] = np.sqrt( np.dot(wts**2,dy**2) )
        return Inty,dInty
    
    

    
class CubicSplineWithErrorProp(object):
    """Performs cubic spline interpolation and integration
    with analytic error propagation.
 
    Both natural (zero 2nd derivative) and clamped (specified
    slopes) end-point conditiions are supported.

    One can write the cubic spline in the following way:
        f_i(x) = a_i + b_i*(x-x_i) + c_i*(x-x_i)^2 + d_i*(c-c_i)^3
    where
        a_i = dot( AW, y )
        b_i = dot( BW, y ) + BV
        c_i = dot( CW, y ) + CV
        d_i = dot( DW, y ) + DV
    such that the AW, BW, CS, and DW matrices and the BV, CV, and
    DV vectors are independent of y (they only depend on the
    input x-values).

    Attributes
    ----------
    x : numpy.ndarray, shape=(n,)
        The input x-values. These must be in ascending order.

    h : numpy.ndarray, shape=(n-1,)
        The gaps between consecutive x-values

    AW : numpy.ndarray, shape=(n,n)
        Unit matrix

    BW,CW,DW : numpy.ndarray, shape=(n,n)
        The matrices used to evaluate the spline coefficients

    BV,CV,DV : numpy.ndarray, shape=(n,)
        The vectors used to evaluate the spline coefficients

    Methods
    -------
    """
    
    def __init__(self, x, dleft, dright):
        """Constructor

        Parameters
        ----------
        x : numpy.ndarray, shape=(n,)
            The input x-values

        dleft : float
            The slope of the spline at the left end-point.
            If dleft=None, then it uses a natural cubic
            spline condition (zero 2nd derivative)

        dright : float
            The slope of the spline at the right end-point.
            If dright=None, then it uses a natural cubic
            spline condition (zero 2nd derivative)
        """
        # define some space
        L = len(x)
        H = np.zeros((L,L))
        M = np.zeros((L,L))
        CV = np.zeros((L,))

        x = np.array(x)
        h = x[1:L]-x[0:L-1]
        self.x  = x.copy()
        self.h = h
        ih = 1.0/h
        
        if dleft is None:
            H[0,0] = 1
        else: # clamped
            H[0,0] = 2*h[0]
            H[0,1] = h[0]
            
        if dright is None:
            H[L-1,L-1] = 1
        else: # clamped
            H[L-1,L-1] = 2*h[L-2]
            H[L-1,L-2] = h[L-2]

        # same for clamped or natural
        for i in range(1,L-1):
            H[i,i] = 2*(h[i-1]+h[i])
            H[i,i-1] = h[i-1]
            H[i,i+1] = h[i]
            
            M[i,i]  = -3*(ih[i-1]+ih[i])
            M[i,i-1] = 3*(ih[i-1])
            M[i,i+1] = 3*(ih[i])

        if dleft is not None:
            M[0,0] = -3*ih[0]
            M[0,1] =  3*ih[0]
            CV[0] = -3*dleft
        if dright is not None:
            M[L-1,L-1] = -3*ih[L-2]
            M[L-1,L-2] =  3*ih[L-2]
            CV[-1] = 3*dright
        
        Hinv = np.linalg.inv(H)
        self.CW = np.dot(Hinv,M)
        self.CV = np.dot(Hinv,CV)
        self.AW = np.eye( L )
        self.BW = np.zeros( (L,L) )
        self.BV = np.zeros( (L,) )
        self.DW = np.zeros( (L,L) )
        self.DV = np.zeros( (L,) )

        for i in range(L-1):
            h = self.h[i]
            ho3 = h / 3
            ht3 = h * 3
            
            self.BW[i,i]   -= 1/h
            self.BW[i,i+1] += 1/h
            self.BW[i,:]   -= ho3 * (self.CW[i+1,:]+2*self.CW[i,:])
            self.BV[i] = -ho3*(self.CV[i+1]+2*self.CV[i])

            self.DW[i,:] = (1/ht3) * (self.CW[i+1,:]-self.CW[i,:])
            self.DV[i] = (self.CV[i+1]-self.CV[i])/ht3
            
        
    def GetValues(self,y,xnew):
        """Returns the interpolated values at xnew, given the input y-values
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        xnew : numpy.ndarray, shape=(m,)
            The output x-values

        Returns
        -------
        ynew : numpy.ndarray, shape=(m,)
            The output y-values of the cubic spline
        """
        
        N = len(self.x)
        
        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
                
        a = np.dot(self.AW,y)
        b = np.dot(self.BW,y) + self.BV
        c = np.dot(self.CW,y) + self.CV
        d = np.dot(self.DW,y) + self.DV

        N = len(xnew)
        ynew = np.zeros((N,))
        for i in range(N):
            j = max(0,min(len(self.x)-2,np.searchsorted(self.x, xnew[i]) - 1))
            lamw = xnew[i] - self.x[j]
            ynew[i] = d[j]*lamw**3 + c[j]*lamw**2 + b[j]*lamw + a[j]

        return ynew



    def GetValuesAndErrors(self,y,dy,xnew):
        """Returns the interpolated values and propagated errors
        at xnew, given the input y-values and input error values
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        dy : numpy.ndarray, shape=(n,)
            The input error values. This must be the same shape as the 
            input x-values.  These should correspond to standard
            deviations (or standard errors) rather than variances.

        xnew : numpy.ndarray, shape=(m,)
            The output x-values

        Returns
        -------
        ynew : numpy.ndarray, shape=(m,)
            The output y-values of the cubic spline

        dynew : numpy.ndarray, shape=(m,)
            The propagated uncertainty of the output values
        """
        
        N = len(self.x)

        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
        if dy is not None:
            if N != len(dy):
                raise Exception(f"expected dy size {N} but received {len(dy)}")
                
        a = np.dot(self.AW,y)
        b = np.dot(self.BW,y) + self.BV
        c = np.dot(self.CW,y) + self.CV
        d = np.dot(self.DW,y) + self.DV

        M = len(self.x)
        N = len(xnew)
        ynew = np.zeros((N,))
        dynew = np.zeros((N,))
        for i in range(N):
            j = max(0,min(len(self.x)-2,np.searchsorted(self.x, xnew[i]) - 1))
            dx = xnew[i] - self.x[j]
            dx2 = dx*dx
            dx3 = dx2*dx
            dx4 = dx2*dx2
            dx6 = dx3*dx3
            ynew[i] = d[j]*dx3 + c[j]*dx2 + b[j]*dx + a[j]
            for k in range(M):
                dynew[i] += (dx3*self.DW[j,k]+dx2*self.CW[j,k]+dx*self.BW[j,k]+self.AW[j,k])**2 * dy[k]**2
            dynew[i] = np.sqrt(dynew[i])
        return ynew,dynew


    
    
    def Integrate(self,y,dy):
        """Returns integral of the cubic spline over the range
        of input x-values.
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        dy : numpy.ndarray, shape=(n,)
            The input error values. This must be the same shape as the 
            input x-values.  These should correspond to standard
            deviations (or standard errors) rather than variances.
            This parameter is allowed to be None, in which case
            the uncertainty of the integral is reported as None

        Returns
        -------
        IntF : float
            The integral of the linear spline from x=self.x[0] to self.x[-1]

        dIntF : float
            The propagated uncertainty of the integral. Returns None
            value if dy was None
        """
        
        N = len(self.x)

        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
        if dy is not None:
            if N != len(dy):
                raise Exception(f"expected dy size {N} but received {len(dy)}")
                
        avec = np.zeros( [N], float )
        bvec = np.zeros( [N], float )
        cvec = np.zeros( [N], float )
        dvec = np.zeros( [N], float )
        for j in range(N-1):
            delx = self.x[j+1]-self.x[j]
            c4=(delx**4)/4.
            c3=(delx**3)/3.
            c2=(delx**2)/2.
            c1=delx
            avec[j] = c1
            bvec[j] = c2
            cvec[j] = c3
            dvec[j] = c4
        aw = np.dot(avec,self.AW)
        bw = np.dot(bvec,self.BW)
        cw = np.dot(cvec,self.CW)
        dw = np.dot(dvec,self.DW)
        bv = np.dot(bvec,self.BV)
        cv = np.dot(cvec,self.CV)
        dv = np.dot(dvec,self.DV)

        wvec = aw+bw+cw+dw
        wext = bv+cv+dv
        inty   = np.dot( wvec, y ) + wext
        intdy = None
        if dy is not None:
            intdy = np.sqrt( np.dot( wvec**2, dy**2 ) )

        return inty,intdy


    def RunningIntegral(self,y,dy):
        """Returns the running integral of the cubic spline over the range
        of input x-values.
        
        Parameters
        ----------
        y : numpy.ndarray, shape=(n,)
            The input y-values. This must be the same shape as the 
            input x-values

        dy : numpy.ndarray, shape=(n,)
            The input error values. This must be the same shape as the 
            input x-values.  These should correspond to standard
            deviations (or standard errors) rather than variances.
            This parameter is allowed to be None, in which case
            the uncertainty of the integral is reported as None

        Returns
        -------
        IntF : numpy.ndarray, shape=(n,)
            The running integral from x=self.x[0] to self.x[i] for each
            input x-value. The first element is 0.0, by definition

        dIntF : numpy.ndarray, shape=(n,)
            The propagated uncertainty in the running integral values
        """

        N = len(self.x)
        if N != len(y):
            raise Exception(f"expected y size {N} but received {len(y)}")
        if dy is not None:
            if N != len(dy):
                raise Exception(f"expected dy size {N} but received {len(dy)}")
                
        Ivals = np.zeros( (N,) )
        Dvals = np.zeros( (N,) )

        asum = np.zeros( [N], float )
        bsum = np.zeros( [N], float )
        csum = np.zeros( [N], float )
        dsum = np.zeros( [N], float )
        for j in range(N-1):
            delx = self.x[j+1]-self.x[j]
            c4=(delx**4)/4.
            c3=(delx**3)/3.
            c2=(delx**2)/2.
            c1=delx
            asum[j] += c1
            bsum[j] += c2
            csum[j] += c3
            dsum[j] += c4
            aw = np.dot(asum,self.AW)
            bw = np.dot(bsum,self.BW)
            cw = np.dot(csum,self.CW)
            dw = np.dot(dsum,self.DW)
            bv = np.dot(bsum,self.BV)
            cv = np.dot(csum,self.CV)
            dv = np.dot(dsum,self.DV)

            wvec = aw+bw+cw+dw
            wext = bv+cv+dv
            Ivals[j+1] = np.dot( wvec, y ) + wext
            if dy is not None:
                Dvals[j+1] = np.sqrt( np.dot( wvec**2, dy**2 ) )
        return Ivals,Dvals



###########################################################################
###########################################################################





def GeneralizedSSCSched(N,alpha0,alpha1=None):
    """Returns a N-point schedule that based on a generalized SSC function.
    The SSC(alpha) function uses a fixed value of alpha to obtain construct
    a symmetric schedule. The generalized form calculated here uses a
    lambda-dependent alpha; e.g., SSC(alpha(lambda)), which scales from
    alpha(0) = alpha0 to alpha(1) = alpha1

    If alpha == 0, then a SSC(0) schedule is returned.
    If alpha == 1, then a SSC(1) schedule is returned.
    If alpha == 2, then a SSC(2) schedule is returned.
    If 0 < alpha < 1, the schedule is a mixture of SSC(0) and SSC(1).
    If 1 < alpha < 2, the schedule is a mixture of SSC(1) and SSC(2).
    
    The schedule is determined by finding all unique real roots of the
    the N polynomials, where i = [0,N-1].

    SSC(x;alpha_i,i) = c_{5}(alpha_i) x^5 + c_{4}(alpha_i) x^4 
                     + c_{3}(alpha_i) x^3 
                     + c_{2}(alpha_i) x^2 + c_{1}(alpha_i) x - i/(N-1)
    
    where alpha_i = alpha0 + (alpha1-alpha0) * i / (N-1), and the
    coefficients are:

    c_{1}(alpha) = { 1,             if alpha = 0
                     1-alpha,       if 0 < alpha < 1
                     0,             if 1 < alpha }

    c_{2}(alpha) = { 0,             if alpha = 0
                     3 alpha,       if 0 < alpha < 1
                     3 (2-alpha),   if 1 < alpha }

    c_{3}(alpha) = { 0,             if alpha = 0
                     -2 alpha,      if 0 < alpha < 1
                     10 (alpha-1) - 2 (2-alpha), if 1 < alpha }

    c_{4}(alpha) = { 0,             if alpha <= 1
                     -15 (alpha-1), if 1 < alpha }

    c_{5}(alpha) = { 0,             if alpha <= 1
                     6 (alpha-1),   if 1 < alpha }

    Parameters
    ----------
    N : int
        The size of the schedule. N >= 2

    alpha0 : float
        The schedule type at lambda=0. 0 <= alpha <= 2

    alpha1 : float, default=None
        The schedule type at lambda=1. 0 <= alpha <= 2
        If unused, it is set to alpha0

    Returns
    -------
    lams : numpy.ndarray, shape=(N,), dtype=float
        The sorted list of lambda values
    """

    import numpy as np

    if alpha1 is None:
        alpha1 = alpha0
    
    if N < 2:
        raise Exception(f"Expected N>=2, but received {N}")
    if alpha0 < 0 or alpha0 > 2:
        raise Exception(f"Expected 0 <= alpha <= 2, but received {alpha}")
    if alpha1 < 0 or alpha1 > 2:
        raise Exception(f"Expected 0 <= alpha <= 2, but received {alpha}")

    x = np.linspace(0,1,N)
    alphas = np.linspace(alpha0,alpha1,N)
    lams = [0.]
    for i in range(1,N-1):
        alpha = alphas[i]
        if alpha <= 1.:
            a_uniform = np.array([  0., 0., 1., -x[i] ])
            a_ssc1 =    np.array([ -2., 3., 0., -x[i] ])
            a = alpha * a_ssc1 + (1.-alpha) * a_uniform
        else:
            a_ssc1 =    np.array([ 0.,   0., -2., 3., 0., -x[i] ])
            a_ssc2 =    np.array([ 6., -15., 10., 0., 0., -x[i] ])
            a = (alpha-1.) * a_ssc2 + (2.-alpha) * a_ssc1
        r = np.roots(a)
        for j in range(len(r)):
            if (np.iscomplex(r[j]) == 0) & ((r[j] in lams) == 0):
                val = np.real(r[j])
                if val >= 0 and val <= 1:
                    lams.append(val)
                    break
        lams[i] = round(lams[i],6)
    lams.append(1.)
    
    lams = np.array(lams)
    lams.sort()
    lams[0] = 0.
    lams[-1] = 1.
    if len(lams) != N:
        raise Exception(f"Failed to obtain a {N}-point schedule."+
                        f" Produced {len(lams)} values")

    return lams



class MapObjective(object):
    def __init__(self,lams):
        import numpy as np
        self.lams = np.array(lams)

    def CptValue(self,x):
        import numpy as np
        n = len(self.lams)
        us = GeneralizedSSCSched(n,x[0],x[1])
        return np.linalg.norm(us-self.lams)**2
    


def EvalMapObjective(x,self):
    return self.CptValue(x)
    
def MapOptimize(lams):
    from scipy.optimize import minimize
    obj = MapObjective(lams)
    x0 = [1.4,1.4]
    res = minimize( EvalMapObjective,x0,
                    args=(obj,),
                    method='L-BFGS-B',
                    jac=False,
                    bounds=[(0.,2.),(0.,2.)],
                    options={
                        "maxiter":10000,
                        "disp":False,
                        "ftol":1.e-12,
                        "gtol":1.e-9,
                        "eps":1.e-4
                    } )
    return res.x



def OptSfcn(lams,size=2001):
    import numpy as np
    from scipy.interpolate import PchipInterpolator
    #from fetkutils import CptGeneralizedSSCSched

    n = len(lams)
    ps = MapOptimize(lams)

    m=size
    us = np.linspace(0,1,m)
    xs = GeneralizedSSCSched(m,ps[0],ps[1])
    Sfcn = PchipInterpolator(xs,us)
    Sinv = PchipInterpolator(us,xs)
    return Sfcn,Sinv


###########################################################################
###########################################################################
    

class USubSplineWithErrorProp(object):
    def __init__(self,x,y,dy):
        import numpy as np
        self.x=np.array(x,copy=True)
        self.y=np.array(y,copy=True)
        self.dy = None
        if dy is not None:
            self.dy = np.array(dy,copy=True)
            
        self.S,self.Sinv = OptSfcn(self.x)
        self.dSinv  = self.Sinv.derivative()
        self.nspl = CubicSplineWithErrorProp( self.S(self.x), None, None )

    def GetValues(self,xnew):
        return self.nspl.GetValues(self.y,self.S(xnew))

    def GetValuesAndErrors(self,xnew):
        return self.nspl.GetValuesAndErrors(self.y,self.dy,self.S(xnew))

    def Integrate(self,nboot=0,size=2001):
        import numpy as np
        from scipy.interpolate import CubicSpline
        #from edgembar.Splines import CubicSplineWithErrorProp

        m = size
        mx  = np.linspace(0,1,m)
        
        if self.dy is None:
            
            return self.nspl.Integrate(self.y,self.dy)
            
        elif nboot < 1:
            
            my,dmy  = self.nspl.GetValuesAndErrors(self.y,self.dy,mx)
            dsy = self.dSinv(mx)
            
            wN = 1/(len(self.x)-1)
            wM = 1/(m-1)
            
            dmy = dmy * abs(dsy) * np.sqrt( 1.15 * wN/wM  )
            my = my * dsy
            
            tmp = CubicSplineWithErrorProp( mx, None, None )
            Gdu,dGdu = tmp.Integrate(my,dmy)
            
        else:
            
            ds = self.dSinv(mx)
            xx = self.S(self.x)
            bvals=[]
            for i in range(1+nboot):
                if i == 0:
                    yy = self.y
                else:
                    yy = self.y + np.random.normal(loc=0, scale=self.dy)
                # Natural cubic splines
                spl = CubicSpline(xx,yy,bc_type=((2, 0.0), (2, 0.0)))
                tmp = CubicSpline(mx,spl(mx) * ds,bc_type=((2, 0.0), (2, 0.0)))
                bvals.append(tmp.integrate(0,1))
            bvals = np.array(bvals)
            Gdu = bvals[0]
            dGdu = np.std(bvals[1:])
        return Gdu,dGdu
