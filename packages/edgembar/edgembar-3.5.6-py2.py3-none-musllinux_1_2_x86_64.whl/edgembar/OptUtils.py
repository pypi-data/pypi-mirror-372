#!/usr/bin/env python3

import numpy as np


# class DummyEqCon(object):
#     def __init__(self):
#         self.ncon = 0
#         pass

#     def SetupTransform(self):
#         pass

#     def GetGenParams(self,fullparams):
#         return fullparams

#     def GetGenGradients(self,fullgrad):
#         return fullgrad

#     def GetFullParams(self,genparams):
#         return genparams

#     def GetLagrangeMultipliers(self,dChidFull):
#         return np.array([])

#     def GetLinearConstraint(self):
#         return None

    

# class LinearEqCon(object):

#     def __init__(self,Cmat,Cvals):
#         self.Cmat = np.array(Cmat,copy=True)
#         self.Cvals = np.array(Cvals,copy=True)
#         self.ncon = self.Cmat.shape[0]
#         self.npar = self.Cmat.shape[1]
#         self.nfree = self.npar-self.ncon
#         if self.Cvals.shape[0] != self.ncon:
#             raise Exception((f"{self.Cvals.shape} constraint values provided"
#                              f" but {self.ncon} expected"))
#         if self.nfree < 0:
#             raise Exception((f"There are more constraints {self.ncon}"
#                              f" than parameters {self.npar}"))
#         self.T = None
#         self.Cinv = None
#         self.x0 = None

#     def SetupTransform(self,tol=1.e-8):
#         from scipy.linalg import svd
#         m,n = self.Cmat.shape
#         U,s,VT = svd(self.Cmat,full_matrices=True)
#         sigma = np.zeros( (m,n) )
#         n = self.npar
#         i = n - self.nfree
#         self.T = VT[i:n,:]
#         for i in range(min(m,n)):
#             if abs(s[i]) > tol:
#                 sigma[i] = 1./s[i]
#             else:
#                 sigma[i] = 0.
#         self.Cinv = np.dot(VT.T,np.dot(sigma.T,U.T))
#         self.x0 = np.dot(self.Cinv,self.Cvals)

#     def GetFullParams(self,genparams):
#         return self.x0 + np.dot(genparams,self.T)

#     def GetGenGradients(self,fullgrad):
#         return np.dot(self.T,fullgrad)

#     def GetGenParams(self,fullparams):
#         return np.dot(self.T,fullparams)

#     def GetLagrangeMultipliers(self,dChidFull):
#         print(dChidFull)
#         return np.dot(dChidFull,self.Cinv)

#     def GetLinearConstraint(self):
#         from scipy.optimize import LinearConstraint
#         return LinearConstraint(self.Cmat,self.Cvals,self.Cvals)


# def LinearEqConFactory(nparam,xidxs,xvalues):
#         from collections import OrderedDict
#         seen_idxs = OrderedDict()
#         if xidxs is not None and xvalues is not None:
#             for xidx,val in zip(xidxs,xvalues):
#                 t = tuple(xidx[::-1])
#                 if t in seen_idxs:
#                     seen_idxs[t] = -val
#                 else:
#                     seen_idxs[tuple(xidx)] = val
        
#         ncon = len(seen_idxs)
#         if ncon > 0:
#             Cmat = np.zeros( (ncon,nparam) )
#             Cvals = np.array( xvalues )
#             for icon,idx in enumerate(seen_idxs):
#                 if idx[0] > 0:
#                     Cmat[icon,idx[0]-1] = -1
#                 if idx[1] > 0:
#                     Cmat[icon,idx[1]-1] =  1
#             return LinearEqCon(Cmat,Cvals)
#         else:
#             return DummyEqCon()
    


        
def GraphObjective( pfree, node_idxs, pcenter, pc2, pc3 ):
    chisq = 0.
    p = np.concatenate( ([0.], pfree ) )
    g = np.zeros( (p.shape[0],) )
    f0 = p[node_idxs[0,:]]
    f1 = p[node_idxs[1,:]]
    df = f1-f0
    dq = df-pcenter
    dq2 = dq**2
    chisq = np.dot( pc2, dq2 ) + np.dot( pc3, dq**3 )
    dpen = 2*pc2*dq + 3*pc3*dq2
    for i in range(dpen.shape[0]):
        g[node_idxs[0,i]] -= dpen[i]
        g[node_idxs[1,i]] += dpen[i]
    return chisq,g[1:]
        

# def GraphObjective( pgen, lincon, node_idxs, pcenter, pc2, pc3 ):
#     chisq, g = GraphPenalty( lincon.GetFullParams(pgen),
#                              node_idxs, pcenter, pc2, pc3 )
#     return chisq, lincon.GetGenGradients(g)




