#!/usr/bin/env python3


class RBF(object):
    """
    A class that calculates multiquadrtic radial basis function
    interpolation

    Attributes
    ----------
    op : GridUtils.MinImg
        Calculates minimum image distances

    cpts : numpy.array, shape=(npts,ndim)
        The control points that the spline passes through
    
    cerrs : numpy.array, shape=(npts,)
        The uncertainty in the control values used to propagate
        the uncertainty in the interpolated values

    epsilon : float
        The multiquadrtic shape parameter

    Ainv : numpy.array, shape=(npts,npts)
        The least squares spline fit

    wts : numpy.array, shape=(npts,)
        The spline interpolation weights

    y0 : float
        The y0 value is subtracted from the interpolated values 

    Methods
    -------
    """
    def __init__(self,cpts,cvals,cerrs,epsilon,dimisper,dimrange=360):
        """
        Parameters
        ----------
        cpts : numpy.array, shape=(npts,ndim)
            The control points that the spline passes through

        cvals : numpy.array, shape=(npts,)
            The control values that the spline should have at the control
            points

        cerrs : numpy.array, shape=(npts,)
            The uncertainty in the control values

        dimisper : numpy.array, shape=(ndim,), dtype=bool
            Flag for each dimension indicating if it is periodic

        dimrange : float, default=360.
            The range of periodicity
        """
        import numpy as np
        import scipy.linalg
        from scipy.spatial.distance import pdist, squareform
        from . GridUtils import MinImg
        import sys

        #
        # periodicity hack: include replicated copies of any data within
        # 7 percent of a periodic boundary... no time to work on this
        # and the rbf kernel isn't directly amenable to non-euclidean
        # distance metrics.
        #
        for d in range(len(dimisper)):
            if dimisper[d]:
                pidxs=[]
                midxs=[]
                for i in range(cpts.shape[0]):
                    # wrap the input control data
                    cpts[i,d] = (cpts[i,d]-dimrange/2)%dimrange
                    if cpts[i,d] < 0.07*dimrange:
                        pidxs.append(i)
                    if cpts[i,d] > 0.93*dimrange:
                        midxs.append(i)
                cp = cpts[pidxs,:]
                cm = cpts[midxs,:]
                cp[:,d] += dimrange
                cm[:,d] -= dimrange
                cpts = np.concatenate( (cpts,cp,cm), axis=0 )
                cerrs = np.concatenate( (cerrs,cerrs[pidxs],cerrs[midxs]),
                                        axis=0 )
                cvals = np.concatenate( (cvals,cvals[pidxs],cvals[midxs]),
                                        axis=0 )


        #print(cpts.shape)
        self.op = MinImg([False]*len(dimisper),dimrange)
        self.cpts = cpts
        self.cerrs = cerrs
        self.epsilon = epsilon

        if False:
            seps     = pdist(cpts,lambda x,y: self.op.diffsep(x,y))
            rbfs     = np.sqrt( 1 + epsilon * seps**2 )
            A        = squareform(rbfs)
            for i in range(A.shape[0]):
                A[i,i]=1.
        else:
            A = np.zeros( (cpts.shape[0],cpts.shape[0]) )
            for i in range(A.shape[0]):
                for j in range(i):
                    dist = np.linalg.norm( cpts[i,:]-cpts[j,:] )
                    f = np.sqrt( 1 + epsilon * dist*dist )
                    A[i,j] = f
                    A[j,i] = f
                A[i,i] = 1
            
        #Ainv     = scipy.linalg.inv(A)
        Ainv     = np.linalg.inv(A)
        self.Ainv = Ainv
        self.wts = np.dot(Ainv,cvals)
        self.y0 = 0
        vs = self.GetValues(self.cpts).values
        maxerr = max( abs(vs-cvals) )
        if maxerr > 1.e-4:
            sys.stderr.write("RBF construction failed. "
                             +"Ill-conditioned matrix? "
                             +"Retrying with cipy.linalg.solve ...\n")
            sys.stderr.write("maxerr = %13.4e\n"%(maxerr))
            self.wts = scipy.linalg.solve(A,cvals,assume_a='sym')
            vs = self.GetValues(self.cpts).values
            maxerr = max( abs(vs-cvals) )
            if maxerr > 1.e-4:
                sys.stderr.write("RBF results are still wrong."
                                 +" This is a problem!\n")
                sys.stderr.write("maxerr = %13.4e\n"%(maxerr))
            else:
                sys.stderr.write("RBF results seem ok now\n")
                
        self.op = MinImg(dimisper,dimrange)
                

        
    def GetValues(self,pts,return_std=False,return_deriv=False):
        """Computes the RBF fit values (and optionally the standard errors and
        function gradients) at arbitrary points

        Parameters
        ----------        
        pts : list of lists or numpy.ndarray shape=(npts,ndim)
            A list of evaluation points

        return_std : bool, default=False
            If True, then return the standard error at the evaluation points

        return_deriv : bool, default=False
            If True, then return the feature gradients at the evalution points

        Returns
        -------
        ndfes.EvalT
            A container holding the values, errors, and feature derivatives.
            The EvalT.values, EvalT.errors are numpy.array's shape=(npts,).
            EvalT.derivs is a (npts,ndim) array.  The EvalT.errors and 
            EvalT.derivs elements can be None, depending on the values of
            return_std and return_deriv
        """

        import numpy as np
        from . EvalT import EvalT

        pts = np.array(pts)
        npt = pts.shape[0]
        ndim = pts.shape[1]
        vals = np.zeros( (npt,) )
        errs = None
        if return_std:
            errs = np.zeros( (npt,) )
            sqerrs = self.cerrs**2
        ders = None
        if return_deriv:
            ders = np.zeros( pts.shape )
        for ipt in range(npt):
            pt = np.where(self.op.dimisper,
                          self.op.wrap(pts[ipt,:])+180,
                          pts[ipt,:])
            crds = pt-self.cpts
            #crds = self.op.diffcrd(pts[ipt,:],self.cpts)
            sqseps = np.sum(crds**2,axis=1)
            rbfs = np.sqrt( 1 + self.epsilon * sqseps )
            vals[ipt] = np.dot(rbfs,self.wts)
            if return_std:
                errs[ipt] = np.sqrt(np.dot(np.dot(rbfs,self.Ainv)**2,sqerrs))
            if return_deriv:
                ders[ipt,:] = np.dot(self.epsilon*self.wts/rbfs,crds)


        return EvalT(vals-self.y0,ders,errs)

    
    def ShiftInterpolatedValues(self,e):
        """Sets the y0 attribute, which is subtracted from all interpolated
        values

        Parameters
        ----------
        e : float
            The value to be subtracted from all interpolated values
        """
        
        self.y0 += e



class ARBFBin(object):
    def __init__(self,delta,ibin,bins,grid,epsilon,dimrange=360):
        from . GridUtils import LinearPtsToMeshPts
        from . GridUtils import MinImg
        import numpy as np

        def INTWRAP(i,n):
            return (i%n+n)%n

        #delta = 2
        bidx = bins[ibin].bidx

        dimsizes = [ dim.size for dim in grid.dims ]
        dimisper = [ dim.isper for dim in grid.dims ]
        ndim = len(dimsizes)
        
        didxs = [i for i in range(-delta,delta+1)]
        ndidx = len(didxs)
        
        lidxs = []
        for dim in range(ndim):
            off = []
            if dimisper[dim]:
                for idel,d in enumerate(didxs):
                    off.append( INTWRAP(bidx[dim]+d,dimsizes[dim]) )
            else:
                for idel,d in enumerate(didxs):
                    b = bidx[dim]+d
                    if b >= 0 and b < dimsizes[dim]:
                        off.append(b)
            lidxs.append(off)
        midxs = LinearPtsToMeshPts(lidxs)
        gidxs = [ grid.CptGlbIdxFromBinIdx(idx) for idx in midxs ]
        gidxs = [ idx for idx in gidxs if idx in bins ]

        N = len(gidxs)
        mimg = MinImg(dimisper,dimrange)
        A = np.zeros( (N,N) )
        cvals = np.array( [ bins[ g ].value for g in gidxs ] )

        self.epsilon = epsilon
        
        c0 = np.array(bins[ibin].center)
        self.c0 = np.array(c0,copy=True)
        self.cpts = np.array( [ c0 + mimg.diffcrd(np.array(bins[g].center),c0)
                                for g in gidxs ] )
        self.cvals = np.array( [ bins[g].value for g in gidxs ] )
        self.cerrs = np.array( [ bins[g].stderr for g in gidxs ] )
        
        for i in range(N):
            A[i,i] = 1
            for j in range(i):
                r = np.linalg.norm( self.cpts[i,:]-self.cpts[j,:] )
                x = np.sqrt( 1 + self.epsilon * r*r )
                A[i,j] = x
                A[j,i] = x
                
        Ainv = np.linalg.inv(A)
        self.Ainv = Ainv
        self.wts = np.dot(Ainv,self.cvals)
        self.y0 = 0
        self.op = mimg



    def GetValues(self,pts,return_std=False,return_deriv=False):
        """Computes the RBF fit values (and optionally the standard errors and
        function gradients) at arbitrary points

        Parameters
        ----------        
        pts : list of lists or numpy.ndarray shape=(npts,ndim)
            A list of evaluation points

        return_std : bool, default=False
            If True, then return the standard error at the evaluation points

        return_deriv : bool, default=False
            If True, then return the feature gradients at the evalution points

        Returns
        -------
        ndfes.EvalT
            A container holding the values, errors, and feature derivatives.
            The EvalT.values, EvalT.errors are numpy.array's shape=(npts,).
            EvalT.derivs is a (npts,ndim) array.  The EvalT.errors and 
            EvalT.derivs elements can be None, depending on the values of
            return_std and return_deriv
        """

        import numpy as np
        from . EvalT import EvalT

        pts = np.array(pts)
        npt = pts.shape[0]
        ndim = pts.shape[1]
        vals = np.zeros( (npt,) )
        errs = None
        if return_std:
            errs = np.zeros( (npt,) )
            sqerrs = self.cerrs**2
        ders = None
        if return_deriv:
            ders = np.zeros( pts.shape )
        for ipt in range(npt):
            wpt = self.op.diffcrd(pts[ipt,:],self.c0) + self.c0
            crds = wpt - self.cpts
                
            #pt = np.where(self.op.dimisper,
            #              self.op.wrap(pts[ipt,:])+180,
            #              pts[ipt,:])
            #crds = pt-self.cpts
            #print(np.linalg.norm(crds,axis=1),np.linalg.norm(wcrds,axis=1))
            #crds = self.op.diffcrd(pts[ipt,:],self.cpts)
            sqseps = np.sum(crds**2,axis=1)
            rbfs = np.sqrt( 1 + self.epsilon * sqseps )
            vals[ipt] = np.dot(rbfs,self.wts)
            if return_std:
                errs[ipt] = np.sqrt(np.dot(np.dot(rbfs,self.Ainv)**2,sqerrs))
            if return_deriv:
                ders[ipt,:] = np.dot(self.epsilon*self.wts/rbfs,crds)

        return EvalT(vals-self.y0,ders,errs)

    
    def ShiftInterpolatedValues(self,e):
        """Sets the y0 attribute, which is subtracted from all interpolated
        values

        Parameters
        ----------
        e : float
            The value to be subtracted from all interpolated values
        """
        
        self.y0 += e

        
        
class ARBF(object):
    def __init__(self,delta,bins,grid,epsilon,dimrange=360):
        from collections import defaultdict as ddict
        self.bins = ddict(int)
        self.grid = grid
        for gidx in bins:
            self.bins[gidx] = ARBFBin(delta,gidx,bins,grid,epsilon,dimrange)

            

    def GetValues(self,pts,return_std=False,return_deriv=False):
        """Computes the RBF fit values (and optionally the standard errors and
        function gradients) at arbitrary points

        Parameters
        ----------        
        pts : list of lists or numpy.ndarray shape=(npts,ndim)
            A list of evaluation points

        return_std : bool, default=False
            If True, then return the standard error at the evaluation points

        return_deriv : bool, default=False
            If True, then return the feature gradients at the evalution points

        Returns
        -------
        ndfes.EvalT
            A container holding the values, errors, and feature derivatives.
            The EvalT.values, EvalT.errors are numpy.array's shape=(npts,).
            EvalT.derivs is a (npts,ndim) array.  The EvalT.errors and 
            EvalT.derivs elements can be None, depending on the values of
            return_std and return_deriv
        """

        import numpy as np
        from . EvalT import EvalT
        
        pts = np.array(pts)
        npt = pts.shape[0]
        ndim = pts.shape[1]
        vals = np.zeros( (npt,) )
        errs = None
        if return_std:
            errs = np.zeros( (npt,) )
        ders = None
        if return_deriv:
            ders = np.zeros( pts.shape )
        for ipt in range(npt):
            gidx = self.grid.GetGlbBinIdx( pts[ipt,:] )
            if gidx in self.bins:
                ret = self.bins[gidx].GetValues([pts[ipt]],return_std,return_deriv)
                vals[ipt] = ret.values[0]
                if return_deriv:
                    ders[ipt] = ret.derivs[0]
                if return_std:
                    errs[ipt] = ret.errors[0]
            else:
                vals[ipt] = None
                if return_deriv:
                    ders[ipt] = None
                if return_std:
                    errs[ipt] = None

        return EvalT(vals,ders,errs)

    
    def ShiftInterpolatedValues(self,e):
        """Sets the y0 attribute, which is subtracted from all interpolated
        values

        Parameters
        ----------
        e : float
            The value to be subtracted from all interpolated values
        """

        for ibin in self.bins:
            self.bins[ibin].ShiftInterpolatedValues(e)

