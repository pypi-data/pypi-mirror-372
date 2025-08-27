#!/usr/bin/env python3

import edgembar as embar
import numpy as np

class CenteredCubic(object):
    """Evaluates the polynomial a cubic polnomial centered about q0
    and which has no slope; i.e., f0 + c2*(q-q0)**2 + c3*(q-q0)**3

    Parameters
    ----------
    q0 : float
        The location of the minimum

    f0 : float
        Function value at the minimum

    c2 : float
        Quadratic coefficient

    c3 : float
        Cubic coefficient

    R : float
        Pearson correlation coefficient

    Methods
    -------
    """
    def __init__(self,q0,f0,c2,c3,Rcub=1,Rquad=1):
        self.q0=q0
        self.f0=f0
        self.c2=c2
        self.c3=c3
        self.Rcub = Rcub
        self.Rquad = Rquad

    def __call__(self,qs):
        """Evaluates the polynomial and returns the value

        Parameters
        ----------
        qs : float or numpy.ndarray, shape=(N,)
            The value(s) at which to evaluate the polynomial
        
        Returns
        -------
        fs : float or numpy.ndarray, shape=(N,)
            The polynomial value(s)
        """
        return self.f0 + self.c2*(qs-self.q0)**2 + self.c3*(qs-self.q0)**3

    def GetValueAndGrad(self,qs):
        """Evaluates the polynomial and returns the value and derivative

        Parameters
        ----------
        qs : float or numpy.ndarray, shape=(N,)
            The value(s) at which to evaluate the polynomial
        
        Returns
        -------
        fs : float or numpy.ndarray, shape=(N,)
            The polynomial value(s)

        gs : float or numpy.ndarray, shape=(N,)
            The gradients of the polynomial
        """
        dq = qs-self.q0
        dq2 = dq**2
        dq3 = dq**3
        ys = self.f0 + self.c2*dq2 + self.c3*dq3
        gs = 2*self.c2*dq + 3*self.c3*dq2
        return ys,gs

    def GetShiftedValueAndGrad(self,qs):
        """Evaluates the polynomial (excluding the leading constant)
        and returns the value and derivative

        Parameters
        ----------
        qs : float or numpy.ndarray, shape=(N,)
            The value(s) at which to evaluate the polynomial
        
        Returns
        -------
        fs : float or numpy.ndarray, shape=(N,)
            The polynomial value(s)

        gs : float or numpy.ndarray, shape=(N,)
            The gradients of the polynomial
        """
        dq = qs-self.q0
        dq2 = dq**2
        dq3 = dq**3
        ys = self.c2*dq2 + self.c3*dq3
        gs = 2*self.c2*dq + 3*self.c3*dq2
        return ys,gs

    @classmethod
    def from_lsq(cls,xs,ys):
        """Constructs a polynomial by performing a least squares fit
        to observed values

        Parameters
        ----------
        xs : numpy.ndarray, shape=(N,)
            The observed locations

        ys : numpy.ndarray, shape=(N,)
            The observed values
        
        Returns
        -------
        obj : CenteredCubic
            The least squares fit
        """
        import scipy.stats
        qs = np.array(xs)
        fs = np.array(ys)
        imin = np.argmin(fs)
        n = qs.shape[0]
        q0 = qs[imin]
        f0 = fs[imin]
        A = np.zeros( (n,2) )
        for i in range(n):
            A[i,0] = (qs[i]-q0)**2
            A[i,1] = (qs[i]-q0)**3
        cs,residuals,rank,singvals = np.linalg.lstsq(A,fs-f0,rcond=None)
        ys = f0 + cs[0]*(qs-q0)**2 + cs[1]*(qs-q0)**3
        try:
            m,b,Rcub,P,stderr = scipy.stats.linregress(fs,ys)
        except:
            Rcub=1
            
        ys = f0 + cs[0]*(qs-q0)**2
        try:
            m,b,Rquad,P,stderr = scipy.stats.linregress(fs,ys)
        except:
            Rquad=1
        return cls(q0,f0,cs[0],cs[1],Rcub=Rcub,Rquad=Rquad)
        

# def runit(self):
#     for e in self.edges:
#         qs = np.array([ c.conval for c in e.results.con ])
#         fs = np.array([ c.chisq for c in e.results.con ])
#         n = qs.shape[0]
#         imin = np.argmin(fs)
#         q0 = qs[imin]
#         f0 = fs[imin]
#         A = np.zeros( (n,2) )
#         for i in range(n):
#             A[i,0] = (qs[i]-q0)**2
#             A[i,1] = (qs[i]-q0)**3
#         cs = np.linalg.lstsq(A,fs-f0)


# g = embar.Graph.from_glob("analysis/*~*.py")

# runit(g)
