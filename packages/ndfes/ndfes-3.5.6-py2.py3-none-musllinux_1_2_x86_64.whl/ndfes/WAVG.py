#!/usr/bin/env python3

class WAVG(object):
    """
    A class that calculates a weighted average free energy
    interpolation

    Attributes
    ----------
    fes : ndfes.FES
        The free energy histogram

    order : int
        The B-spline order of the average

    y0 : float
        The y0 value is subtracted from the interpolated values 

    Methods
    -------
    """
    def __init__(self,fes,minsize,order,niter):
        self.order = order
        self.nbspl = order + (order%2)
        #self.fes = fes.AddPenaltyBuffers(self.nbspl)
        self.fes = fes.AddPenaltyBuffers(minsize,self.nbspl//2)
        self.y0 = 0
        self.IterativeCorrection(niter)

        
    def IterativeCorrection(self,nit):
        import numpy as np
        from collections import defaultdict as ddict
        from . Bspline import CptBsplineValues
        from . GridUtils import LinearPtsToMeshPts
        from . GridUtils import LinearWtsToMeshWts
        
        occgidxs = [ gidx for gidx in self.fes.GetOccBins() ]
        occgidxs.sort()
        tvals = np.array([ self.fes.bins[gidx].value for gidx in occgidxs ])
        tcens = np.array([ self.fes.bins[gidx].center for gidx in occgidxs ])

        tidx = self.nbspl//2 - 1
        
        ndim = self.fes.grid.ndim

        if nit > 0:
            for it in range(nit+1):
                ovals = self.GetValues(tcens).values            
                dvals = tvals - ovals
                print("wavg iter %4i  MAE %10.2e  MaxE %10.2e"%\
                      ( it, np.mean(np.abs(dvals)), np.max(np.abs(dvals)) ) )
                if it < nit:
                    for i,gidx in enumerate(occgidxs):
                        self.fes.bins[gidx].value += dvals[i]

        # if True:


        #     for it in range(nit):
        #         #dwts  = ddict(list)
        #         #dvals = ddict(list)
                
        #         #ovals = np.zeros( tvals.shape )
        #         ovals = self.GetValues(tcens).values
        #         dvals = tvals-ovals
        #         avgs = np.zeros(ovals.shape)
        #         print("%3i %13.4e %13.4e"%( it, np.mean(np.abs(dvals)), np.max(np.abs(dvals)) ) )

        #         for ipt in range(tcens.shape[0]):
        #             pt = tcens[ipt,:]
        #             cidxs = [0]*ndim
        #             cpt = [0]*ndim
        #             for idim,dim in enumerate(self.fes.grid.dims):
        #                 w = dim.width
        #                 h = w / 2
        #                 xp = dim.xmin + h
        #                 idelta = int(max(0,(pt[idim]-xp)/w))
        #                 cidxs[idim] = idelta
        #                 cpt[idim] = xp + (idelta+0.5)*w

        #             lwts = []
        #             lidx = []
        #             for idim,dim in enumerate(self.fes.grid.dims):
        #                 w = (self.nbspl-1)*dim.width
        #                 c = w/2.
        #                 dx = c + (pt[idim]-cpt[idim])
        #                 bs,ws = CptBsplineValues(dx,0,dim.width,self.order)

        #                 obs = []
        #                 for b in bs:
        #                     idx = b + cidxs[idim] - (self.nbspl//2-1)
        #                     if dim.isper:
        #                         idx = INTWRAP(idx,dim.size)
        #                     obs.append(idx)
        #                 bs = obs
                    
        #                 lwts.append(ws)
        #                 lidx.append(bs)
                        
        #             midxs = LinearPtsToMeshPts(lidx)
        #             gidxs = [ self.fes.grid.CptGlbIdxFromBinIdx(midx)
        #                       for midx in midxs ]
        
        #             lwts = np.array(lwts)
        #             mwts = LinearWtsToMeshWts(lwts)
        #             #den = np.linalg.norm( mwts )**2

        #             serr = 0
        #             w = 0
        #             for i,gidx in enumerate(gidxs):
        #                 if gidx in occgidxs:
        #                     serr += mwts[i] * dvals[ occgidxs.index(gidx) ]
        #                     w += mwts[i]
        #             avgs[ipt] = serr/w
                    
        #             #val = 0
        #             #for i,gidx in enumerate(gidxs):
        #             #    val += mwts[i] * self.fes.bins[gidx].value
        #             #ovals[ipt] = val
        #             #dval = tvals[ipt]-ovals[ipt]
        #             #for i,gidx in enumerate(gidxs):
        #             #    w = mwts[i] / den
        #             #    dwts[gidx].append( w * mwts[i] )
        #             #    dvals[gidx].append( w * dval )
                        
        #         #d = tvals - ovals

        #         # for gidx in dwts:
        #         #     ws = np.array(dwts[gidx])
        #         #     ws /= np.sum(ws)
        #         #     ds = np.array(dvals[gidx])
        #         #     self.fes.bins[gidx].value += np.dot(ds,ws)
                    
        #         for ipt,gidx in enumerate(occgidxs):
        #             self.fes.bins[gidx].value += avgs[ipt]

                    
        
    def GetValues(self,pts,return_std=False,return_deriv=False):
        """Computes the weighted average values (and optionally the 
        standard errors and function gradients) at arbitrary points

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
        from . Bspline import CptBsplineValues
        from . Bspline import CptBsplineValuesAndDerivs
        from . GridUtils import LinearPtsToMeshPts
        from . GridUtils import LinearWtsToMeshWts

        def INTWRAP(i,n):
            return (i%n+n)%n
        
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

            pt = pts[ipt]
            cidxs = [0]*ndim
            cpt = [0]*ndim
            for idim,dim in enumerate(self.fes.grid.dims):
                w = dim.width
                h = w / 2
                xp = dim.xmin + h
                if dim.isper:
                    idelta = int(np.floor((pt[idim]-xp)/w))
                else:
                    idelta = int(max(0,(pt[idim]-xp)/w))
                cidxs[idim] = idelta
                cpt[idim] = xp + (idelta+0.5)*w

            lwts = []
            lidx = []
            lder = []
            for idim,dim in enumerate(self.fes.grid.dims):
                w = (self.nbspl-1)*dim.width
                c = w/2.
                dx = c + (pt[idim]-cpt[idim])
                if return_deriv:
                    bs,ws,ds = CptBsplineValuesAndDerivs(dx,0,dim.width,self.order)
                else:
                    bs,ws = CptBsplineValues(dx,0,dim.width,self.order)
                    ds = None

                obs = []
                for b in bs:
                    idx = b + cidxs[idim] - (self.nbspl//2-1)
                    if dim.isper:
                        idx = INTWRAP(idx,dim.size)
                    obs.append(idx)
                bs = obs
                    
                for b in bs:
                    if b < 0 or b >= dim.size:
                        raise Exception(f"WAVG out of bounds {idim} {dim.size} {str(bs)}")
                lidx.append(bs)
                lwts.append(ws)
                lder.append(ds)
                
            lwts=np.array(lwts)
            if return_deriv:
                lder=np.array(lder)
            else:
                lder=None
                
            midxs = LinearPtsToMeshPts(lidx)
            gidxs = [ self.fes.grid.CptGlbIdxFromBinIdx(midx)
                      for midx in midxs ]
            cwts = LinearWtsToMeshWts(lwts)

            vals[ipt] = 0
            for ii,gidx in enumerate(gidxs):
                wt = cwts[ii]
                v = 0
                e = 0
                if gidx in self.fes.bins:
                    v = self.fes.bins[gidx].value
                    e = self.fes.bins[gidx].stderr
                else:
                    print(lidx)
                    print(cidxs)
                    print(cpt)
                    print([ g for g in sorted(self.fes.bins) ])
                    raise Exception(f"gidx {gidx} not in bins")
                vals[ipt] += wt * v
                if return_std:
                    errs[ipt] += (wt*e)**2
                    
            if return_std:
                errs[ipt] = np.sqrt(errs[ipt])

            if return_deriv:
                for idim in range(ndim):
                    twts = np.array(lwts,copy=True)
                    twts[idim,:] = lder[idim,:]
                    dwts = LinearWtsToMeshWts(twts)
                    for ii,gidx in enumerate(gidxs):
                        dwt = dwts[ii]
                        v = self.fes.bins[gidx].value
                        ders[ipt,idim] += dwt * v

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
