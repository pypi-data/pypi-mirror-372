#!/usr/bin/env python3

class DensitySim(object):
    
    def __init__(self,rcs,fcs,size,denest,dampfactor,t=0):
        
        import numpy as np
        
        self.rcs = np.array(rcs,copy=True)
        self.fcs = np.array(fcs,copy=True)
        self.size = size
        self.t = t
        self.UpdateDensity(denest,dampfactor)

        
    def UpdateDensity(self,denest,dampfactor):
        
        import numpy as np
        
        #self.denest = denest
        #self.hdf = None
        self.mean = np.array(self.rcs,copy=True)
        self.std = np.zeros( self.rcs.shape )
        #self.hdf_eff = None
        self.size_eff = 0
        self.mean_eff = np.array(self.rcs,copy=True)
        self.err_eff = np.zeros( self.rcs.shape )

        if denest is not None:
            hdf = denest.GetDensity(self.fcs,self.rcs)
            self.mean,self.std = self.CptCentroidAndError(hdf,1,denest)

            if self.size > 0:
                hdf_eff,self.size_eff = self.CptEffectiveHDF(hdf,denest,dampfactor)
                self.mean_eff,self.err_eff = \
                    self.CptCentroidAndError( hdf_eff, self.size_eff, denest )
            else:
                self.size_eff = 0
                #self.hdf_eff = self.hdf
                self.mean_eff = self.mean
                self.err_eff = self.std


    def CptEffectiveHDF(self,hdf,denest,dampfactor):
        
        from collections import defaultdict as ddict
        import numpy as np
        
        hdf_eff = ddict(int)
        
        fes = denest.fes

        w1 = min(1,max(0,dampfactor))
        w2 = 1-w1

        size_eff = 0
        for gidx,sbin in sorted(fes.bins.items()):
            n = min(sbin.size,self.size*hdf[gidx])
            hdf_eff[gidx] = n
            size_eff += n

        for gidx,sbin in sorted(fes.bins.items()):
            hdf_eff[gidx] /= size_eff
            hdf_eff[gidx] = w1 * hdf_eff[gidx] + w2 * hdf[gidx]
            
        return hdf_eff,size_eff
    
        
    def CptCentroidAndError(self,hdf,size,denest):
        
        import numpy as np
        
        mu  = np.zeros( self.rcs.shape )
        err = np.zeros( self.rcs.shape )
        fes = denest.fes
        
        for gidx,sbin in sorted(fes.bins.items()):
            wc = fes.grid.DiffCrd(sbin.center,self.rcs)+self.rcs
            mu += hdf[gidx] * wc

        for gidx,sbin in sorted(fes.bins.items()):
            wc = fes.grid.DiffCrd(sbin.center,self.rcs)+self.rcs
            err += hdf[gidx] * (wc-mu)**2

        err = np.sqrt( err/size )

        return mu,err

        
        
        
class DensityString(object):

    def __init__( self,
                  denest,
                  inp_pts,
                  path_npts,
                  path_fcs,
                  sim_size,
                  dampfactor,
                  first_path=None,
                  prev_path=None,
                  method=None):
        
        from . PathUtils import PCurve
        import numpy as np

        self.denest     = denest
        self.first_path = first_path
        self.prev_path  = prev_path
        self.method     = method
        self.dampfactor = dampfactor
        
        if self.method is None:
            self.uniform=True
        elif self.method == "min":
            self.uniform=False
        elif self.method == "ts":
            self.uniform=False
        else:
            raise Exception("Unrecognized update method %s"%(str(self.method)))

        self.inp_pts    = np.array( inp_pts, copy=True )

        if not self.uniform:
            if path_npts != self.inp_pts.shape[0]:
                raise Exception("Uniform division of the parametric curve"+
                                " was requested, but the number of path "+
                                "pts (%i) "%(path_npts) +
                                "differs from the number of input points "+
                                " (%i)"%(self.inp_pts.shape[0]))
            
            

        if self.inp_pts.shape[0] > 1 and self.uniform:
            self.inp_pc = PCurve( self.inp_pts, fixt=False )
        else:
            self.inp_pc = None

        self.sim_size   = sim_size
        self.path_npts  = path_npts
        self.path_fcs   = np.array( path_fcs, copy=True )

        if self.path_npts == 1 and self.inp_pts.shape[0] > 1:
            raise Exception("Too many input points "+
                            "(%i) "%(self.inp_pts.shape[0])+
                            "for a path containing 1 point")
        
        if self.path_npts == 1:
            ts = np.zeros( (1,) )
        else:
            ts = np.linspace(0,1,self.path_npts)

        self.path = []
        for i in range(self.path_npts):
            t = ts[i]
            if self.uniform:
                if self.inp_pc is not None:
                    rc = self.inp_pc.GetValue(t)
                else:
                    rc = self.inp_pts[0,:]
            else:
                rc = self.inp_pts[i,:]
                if self.inp_pc is not None:
                    t = self.inp_pc.t[i]
            fc = self.path_fcs
            n = self.sim_size
            self.path.append( DensitySim(rc,fc,n,denest,dampfactor,t=t) )

        #self.out_pts = np.array( [ p.mean_eff for p in self.path ] )


    @classmethod
    def from_sims(cls,denest,
                  inp_pts,
                  path_fcs,
                  sim_size,
                  dampfactor,
                  sims,
                  method=None):
        
        import numpy as np
        from . PathUtils import PCurve

        self = cls(None,[],0,[],0,dampfactor,method=method)
        
        self.denest     = denest
        self.first_path = None
        self.prev_path  = None
        
        self.inp_pts    = np.array( inp_pts, copy=True )
        if self.inp_pts.shape[0] > 1:
            self.inp_pc = PCurve( self.inp_pts, fixt=False )

        self.sim_size   = sim_size
        self.path_npts  = self.inp_pts.shape[0]
        self.path_fcs   = np.array( path_fcs, copy=True )
        self.path       = sims
        return self

    
    @classmethod
    def from_disangs_and_dumpaves(cls,disangs,dumpaves,idxs,dampfactor,method=None):
        
        import numpy as np
        from . PathUtils import PCurve
        from . amber.Disang import Disang
        #from scipy.stats import circmean
        from . GridUtils import MeanAngleAndStdRelativeToRef
        
        self = cls(None,[],0,[],0,dampfactor,method=method)
        
        self.denest     = None
        self.first_path = None
        self.prev_path  = None

        if len(disangs) != len(dumpaves):
            raise Exception("Inconsistent number of files "+
                            "%i vs %i"%(len(disangs),len(dumpaves)))


        isper = []
        rcs = []
        fcs = []
        for f in disangs:
            dis = Disang(f)
            if len(isper) == 0:
                for idx in idxs:
                    if dis.restraints[idx].dihed:
                        isper.append(True)
                    else:
                        isper.append(False)
            rc = [ 0.5*(dis.restraints[idx].r2 + dis.restraints[idx].r3)
                   for idx in idxs ]
            fc = [ 0.5*(dis.restraints[idx].rk2 + dis.restraints[idx].rk3)
                   for idx in idxs ]
            rcs.append(rc)
            fcs.append(fc)

        
            
        fcs = np.array(fcs)
        self.inp_pts   = np.array(rcs)
        self.path_npts = self.inp_pts.shape[0]
        if self.inp_pts.shape[0] > 1:
            self.inp_pc = PCurve( self.inp_pts, fixt=False )
        self.path_fcs  = np.mean(fcs,axis=0)
        
        mus  = []
        ns   = []
        sigs = []
        for idump,f in enumerate(dumpaves):
            data = np.loadtxt(f)[:,1:]
            data = data[:,idxs]
            ns.append( data.shape[0] )
            mymus = []
            mysigs = []
            for i in range(data.shape[1]):
                if isper[i]:
                    mu,sig = MeanAngleAndStdRelativeToRef(data[:,i],self.inp_pts[idump,i])
                    mymus.append(mu)
                    mysigs.append(sig)
                else:
                    mymus.append( np.mean(data[:,i]) )
                    mysigs.append( np.std(data[:,i]) )
            mus.append(mymus)
            sigs.append(mysigs)
            #mus.append( np.mean(data,axis=0) )
            #sigs.append( np.std(data,axis=0) )

        mus = np.array(mus)
        ns = np.array(ns)
        sigs = np.array(sigs)

        self.sim_size   = np.mean(ns)
        self.path = []
        for i in range(self.path_npts):
            s = DensitySim(self.inp_pts[i,:],fcs[i,:],ns[i],
                           self.denest,dampfactor,t=self.inp_pc.t[i])
            s.mean = mus[i]
            s.std = sigs[i]
            s.mean_eff = mus[i]
            s.err_eff = s.std
            if ns[i] > 0:
                s.err_eff = sigs[i] / np.sqrt(ns[i])
            self.path.append(s)
            
        return self

        
    def query_convergence(self,tol,fh=None):
        
        import numpy as np

        cps = np.array( [1]*self.path_npts )
        ops = np.array( [1]*self.path_npts )
        if self.inp_pc is not None:
            cps = self.GetPathProjection(self)
            ops = np.array(cps,copy=True)
            if self.first_path is not None:
                ops = self.GetPathProjection(self.first_path)
        
        conv = True
        if self.prev_path is not None:
            for i in range(self.path_npts):
                p = self.path[i]
                q = self.prev_path.path[i]
                #drc = abs(p.mean_eff - q.mean_eff)
                drc = abs(p.rcs - q.rcs)
                err = np.sqrt(p.err_eff**2 + q.err_eff**2)
                
                if self.sim_size > 0:
                    err *= tol
                    big = np.any( drc > err )
                else:
                    err[:] = tol
                    big = np.any( drc > err )
                if fh is not None:
                    fh.write("img %2i"%(i+1)+
                             " %6.2f %6.2f"%(cps[i],ops[i])+
                             " ".join(["  %9.2e +- %9.2e"%(v,e)
                                       for v,e in zip(drc,err)])+
                             "  %s\n"%(not big))

                if big:
                    conv = False
        else:
            conv = False
            if fh is not None:
                fh.write("String method not converged because it is"+
                         " the first step\n")

        if conv and fh is not None:
            fh.write("String method CONVERGED!\n")
            
        return conv


    
    def next(self,fix0,fix1,method=None):
        
        import numpy as np
        
        if method is None:
            method = self.method

        if self.first_path is None:
            first_path = self
        else:
            first_path = self.first_path

        out_pts = np.array( [ p.mean_eff for p in self.path ] )

        
        if method == "ts":
            for i in range(len(self.path)):
                if False:
                    s = self.path[i]
                    w0 = s.rcs
                    c0 = s.mean_eff
                    wc = w0-c0
                    cwt = 1
                    tc = (1-cwt) * w0 + cwt*c0
                    sim = DensitySim(tc,s.fcs,s.size,
                                     self.denest,self.dampfactor)
                    c1 = sim.mean_eff
                    c01 = w0-c1
                    #c01 = 0.5*( (w0-c1) + (c0-c1) )
                    u01 = c01/np.linalg.norm(c01)
                    d = c0 + np.dot(wc,u01) * u01
                    out_pts[i,:] = d
                elif False:
                    s = self.path[i]
                    w0 = s.rcs
                    c0 = s.mean_eff
                    cw = c0-w0
                    ucw = cw/np.linalg.norm(cw)
                    sim = DensitySim(c0,s.fcs,s.size,
                                     self.denest,self.dampfactor)
                    c1 = sim.mean_eff
                    p = w0 + (c0-c1)
                    sim = DensitySim(p,s.fcs,s.size,
                                     self.denest,self.dampfactor)
                    c2 = sim.mean_eff
                    c2w = c2 - w0
                    out_pts[i,:] = w0 + (c2w - np.dot(c2w,ucw)*ucw)
                elif True:
                    s = self.path[i]
                    w0 = s.rcs
                    c0 = s.mean_eff
                    wc = w0-c0
                    uwc = wc/np.linalg.norm(wc)
                    sim = DensitySim(c0,s.fcs,s.size,
                                     self.denest,self.dampfactor)
                    c1 = sim.mean_eff
                    p = c0 - 2*( (c1-c0) - np.dot( (c1-c0) , uwc ) * uwc )
                    out_pts[i,:] = p




        if fix0:
            out_pts[0,:] = self.inp_pts[0,:]
        if fix1:
            out_pts[-1,:] = self.inp_pts[-1,:]

        return DensityString( self.denest,
                              out_pts,
                              self.path_npts,
                              self.path_fcs,
                              self.sim_size,
                              self.dampfactor,
                              first_path=first_path,
                              prev_path=self,
                              method=method )

    
    def GetSmoothedPath(self,sfact,nmin,nmax):
        #from . SmoothCurve import SmoothCurve_IterWinAvg
        from . SmoothCurve import SmoothCurve_IterReflectedAvg
        if nmin < 3:
            return self
        nmax = max(nmax,nmin)
        if nmin % 2 == 0:
            raise Exception(f"nmin is {nmin} but an odd integer is required")
        if nmax % 2 == 0:
            raise Exception(f"nmax is {nmax} but an odd integer is required")
        
        #out_pts = SmoothCurve_IterWinAvg(self.inp_pts,nmin,nmax,sfact)
        out_pts = SmoothCurve_IterReflectedAvg(self.inp_pts,nmin,nmax,sfact)
        if self.first_path is None:
            first_path = self
        else:
            first_path = self.first_path

        return DensityString( self.denest,
                              out_pts,
                              self.path_npts,
                              self.path_fcs,
                              self.sim_size,
                              self.dampfactor,
                              first_path=first_path,
                              prev_path=self,
                              method=self.method )

        
    
    def UpdateDensity(self,denest,dampfactor=None):
        self.denest=denest
        if dampfactor is not None:
            self.dampfactor=dampfactor
        for sim in self.path:
            sim.UpdateDensity(self.denest,self.dampfactor)
            
    def GetCenters(self):
        import numpy as np
        return np.array([ s.rcs for s in self.path])
    
    def GetMeans(self):
        import numpy as np
        return np.array([ s.mean_eff for s in self.path])

    def GetStdErrs(self):
        import numpy as np
        return np.array([ s.err_eff for s in self.path])

    def GetForceConstants(self):
        import numpy as np
        return np.array([ s.fcs for s in self.path])

    
    def GetPathWidths(self,nsim):

        import numpy as np

        if self.inp_pc is None:
            raise Exception("Can't GetPathWidths without a parametric spline")
        
        ts = np.linspace(0,1,nsim)
        dws = []
        for i in range(nsim):
            if i == 0:
                dw = self.inp_pc.GetValue(ts[i+1]) \
                    - self.inp_pc.GetValue(ts[i])
            elif i == nsim-1:
                dw = self.inp_pc.GetValue(ts[i]) \
                    - self.inp_pc.GetValue(ts[i-1])
            else:
                dw = 0.5*( self.inp_pc.GetValue(ts[i+1]) \
                           - self.inp_pc.GetValue(ts[i-1]) )
            dws.append(dw)
        return np.array(dws)


    def GetPathProjection(self,refpath):
        import numpy as np
        
        if self.inp_pc is None:
            raise Exception("Can't GetPathProjection without a parametric spline")
        
        nsim = len(self.path)
        dws = refpath.GetPathWidths(nsim)
        projs = np.zeros( (nsim,) )
        for i in range(nsim):
            dw = dws[i,:]
            lw = np.linalg.norm(dw)
            uw = dw/lw

            dx = self.path[i].mean_eff - refpath.path[i].rcs
            lx = np.linalg.norm(dx)
            proj = 0
            if lx > 0.001:
                ux = dx/lx
                proj = np.dot(uw,ux)
            projs[i] = proj
        return projs
    

    def GetUniformSims(self,nsim,limits=None):
        
        import numpy as np
        
        if self.inp_pc is None:
            raise Exception("Can't GetUniformSims without a parametric spline")
        
        if limits is None:
            limits = DensityStringSimLimits(self.denest.fes.grid)

        tdisp = limits.tdisp
        maxfcs = limits.maxfcs
        minfcs = limits.minfcs
        
        dws = self.GetPathWidths(nsim)
        ts = np.linspace(0,1,nsim)
        sims = []
        ndim = dws.shape[1]
        
        for i in range(nsim):
            t  = ts[i]
            dw = dws[i,:]
            lw = np.linalg.norm(dw)
            uw = dw/lw
            rc = self.inp_pc.GetValue(t)
            fc = np.array(self.path_fcs,copy=True)
            
            conv = False
            
            for it in range(20):
                sim = DensitySim(rc,fc,self.sim_size,
                                 self.denest,self.dampfactor,t=t)

                dx = sim.mean_eff - sim.rcs
                lx = np.linalg.norm(dx)
                
                if lx > 0.001:
                    ux = dx/lx
                    proj = np.dot(uw,ux)
 
                    # perc is the percentage of the displacement
                    # through the gap
                    perc = np.dot(uw,dx)/lw
                    
                    oldfc = np.array(fc,copy=True)
                    scale = abs(perc)/tdisp
                    fc[:] *= scale
                    
                    for d in range(ndim):
                        fc[d] = max(minfcs[d],min(maxfcs[d],fc[d]))
                        
                    if scale < 1:
                        fc = 0.5*(fc+oldfc)

                    for d in range(ndim):
                        fc[d] = max(minfcs[d],min(maxfcs[d],fc[d]))
                        
                        
                    dfc = np.linalg.norm(fc-oldfc)

                    
                    print("Update fc %2i iter %3i dfc %5.1f "%(i,it,dfc)+
                          " ".join(["%8.2f"%(x) for x in fc]))
                    
                    if dfc < 0.5:
                        sims.append(sim)
                        conv = True
                        break
                else:
                    sims.append(sim)
                    conv = True
                    break

            if not conv:
                sims.append(sim)

        return sims 


    def MakeSimsNonuniform(self,sims,newfrac=1,limits=None):

        import numpy as np
        from . PathUtils import PCurve
        from scipy.interpolate import interp1d

        if self.inp_pc is None:
            raise Exception("Can't MakeSimsNonuniform without a parametric spline")
        
        if limits is None:
            limits = DensityStringSimLimits(self.denest.fes.grid)

        tdisp = limits.tdisp
        maxfcs = limits.maxfcs
        minfcs = limits.minfcs
        
        nsim = len(sims)

        sim_ts = np.linspace(0,1,nsim)
        sim_ks = np.array( [ s.fcs for s in sims ] )
        kspl = PCurve( sim_ks, t=sim_ts )

        uts = np.linspace(0,1,self.path_npts)
        means = []
        for t in uts:
            fc = kspl.GetValue(t)
            for d in range(len(fc)):
                fc[d] = min(maxfcs[d],max(minfcs[d],fc[d]))
            rc = self.inp_pc.GetValue(t)
            s = DensitySim(rc,fc,self.sim_size,
                           self.denest,self.dampfactor,t=t)
            means.append( s.mean_eff )

        cspl = PCurve( means, fixt=False )
            
        spl = interp1d(cspl.t,uts,kind='linear')
        ux = np.linspace(0,1,nsim)
        params = spl( ux[1:-1] )
        params = np.array( [ 0 ] + params.tolist() + [ 1 ] )
        params = newfrac * params + (1-newfrac) * sim_ts
        params.sort()

        osims = []
        for i in range(nsim):
            t = params[i]
            fc = kspl.GetValue(t)
            for d in range(len(fc)):
                fc[d] = min(maxfcs[d],max(minfcs[d],fc[d]))
            rc = self.inp_pc.GetValue(t)
            s = DensitySim(rc,fc,self.sim_size,
                           self.denest,self.dampfactor,t=t)
            osims.append(s)

        return osims

    
    def PredictSims(self,nsim,varyfc,limits=None):

        import numpy as np
        from . DensityEst import SwitchOn

        if self.inp_pc is None:
            if nsim == self.path_npts:
                sims = []
                for i in range(nsim):
                    rc = self.path[i].rcs
                    fc = self.path[i].fcs
                    t = self.path[i].t
                    sims.append( DensitySim(rc,fc,self.sim_size,
                                            self.denest,self.dampfactor,t=t) )
                    
                return DensityString.from_sims \
                    ( self.denest, self.inp_pts,
                      self.path_fcs, self.sim_size,
                      self.dampfactor, sims )
            else:
                raise Exception("Can't MakeSimsNonuniform without a parametric spline")
        

        if varyfc is not None:
            if varyfc:
                sims = self.GetUniformSims(nsim,limits=limits)
            else:
                sims = []
                ts = np.linspace(0,1,nsim)
                for t in ts:
                    fc = np.array( self.path_fcs, copy=True )
                    rc = self.inp_pc.GetValue(t)
                    sims.append( DensitySim(rc,fc,self.sim_size,
                                            self.denest,self.dampfactor,t=t) )
            sims = self.MakeSimsNonuniform(sims,limits=limits)
        else:
            cps = self.GetPathProjection(self)
            ops = np.array(cps,copy=True)
            if self.first_path is not None:
                ops = self.GetPathProjection(self.first_path)

            cavg = np.mean(abs(cps[1:-1]))
            oavg = np.mean(abs(ops[1:-1]))
            wfc  = SwitchOn(oavg,0.5,0.95)
            wlin = SwitchOn(0.5*(oavg+cavg),0.25,0.90)

            #print("wfc,wlin %.3f (%.3f)  %.3f (%.3f)"%(wfc,oavg,
            #                                           wlin,0.5*(oavg+cavg)))
            #print("wfc",wfc)
            if wfc > 0:
                sims = self.GetUniformSims(nsim,limits=limits)
                newsims = []
                for i in range(nsim):
                    rc = sims[i].rcs
                    fc = wfc * sims[i].fcs + (1-wfc) * self.path[i].fcs
                    newsims.append(DensitySim(rc,fc,self.sim_size,
                                              self.denest,self.dampfactor,sims[i].t))
                
            else:
                newsims = [ DensitySim(s.rcs,s.fcs,
                                       self.sim_size,self.denest,
                                       self.dampfactor,t=s.t)
                            for s in self.path ]

            #print("wlin:",wlin)
            #print("cps",cps)
            #print("cavg",cavg,oavg)
            #sims = self.MakeSimsNonuniform(newsims,newfrac=wlin,limits=limits)
            sims = self.MakeSimsNonuniform(newsims,newfrac=1,limits=limits)
            #sims = newsims

            # print("Predicted sims:")
            # for i in range(nsim):
            #    print("%12.9f "%(i/(nsim-1))+
            #          " ".join(["%12.8f"%(x) for x in sims[i].rcs])+
            #          #" "+
            #          #" ".join(["%7.2f"%(x) for x in sims[i].fcs])+
            #          " ".join(["%12.8f"%(x) for x in self.path[i].rcs])+
            #          " ".join(["%12.8f"%(x) for x in self.inp_pc.x[i,:]]))

        return DensityString.from_sims \
            ( self.denest, self.inp_pts,
              self.path_fcs, self.sim_size,
              self.dampfactor, sims )




def CheckDensityStringConv(opath,cpath,
                           sfact,smooth_nmin,smooth_nmax,
                           ptol,fh=None):
    import numpy as np
    from scipy.stats import ttest_ind_from_stats
    
    npts = cpath.path_npts
    cps = np.array( [1]*npts )
    if cpath.inp_pc is not None:
        cps = cpath.GetPathProjection(cpath)

    curpath = cpath.GetSmoothedPath(sfact,smooth_nmin,smooth_nmax)
    oldpath = None
    if opath is not None:
        oldpath = opath.GetSmoothedPath(sfact,smooth_nmin,smooth_nmax)
    
        
    conv = True
    if oldpath is not None:
        for i in range(npts):
            p = curpath.path[i]
            q = oldpath.path[i]
            ndim = p.rcs.shape[0]
            pstd = p.err_eff
            qstd = q.err_eff
            psize = p.size_eff
            qsize = q.size_eff
            if psize <= 0:
                psize = 100
            else:
                pstd *= np.sqrt(psize)
            if qsize <= 0:
                qsize = 100
            else:
                qstd *= np.sqrt(qsize)
            psize = p.size
            qsize = q.size
            if psize <= 0:
                psize = 100
            if qsize <= 0:
                qsize = 100
            psizes = np.array([psize]*ndim)
            qsizes = np.array([qsize]*ndim)
            diff = abs(p.mean_eff - q.mean_eff)
            tvals,pvals = ttest_ind_from_stats( p.mean_eff, pstd, psizes,
                                                q.mean_eff, qstd, qsizes,
                                                equal_var=False,
                                                alternative='two-sided' )
            #notsame = np.any( pvals < ptol )
            #if notsame:
            #    conv = False
            for dim in range(ndim):
                if pvals[dim] < ptol:
                    conv=False

            if fh is not None:
                allconv = "T"
                convs = []
                for dim in range(ndim):
                    if pvals[dim] < ptol:
                        convs.append("F")
                        allconv="F"
                    else:
                        convs.append("T")
                    
                fh.write("img %2i %s "%(i+1,allconv)+
                         " cos: %5.2f "%(cps[i])+
                         " ".join(["[d:%9.2e p: %5.3f>%5.3f ? %s]"%(d,p,ptol,c)
                                   for d,p,c in zip(diff,pvals,convs)])+
                         "%9.3f %9.3f"%(qsizes[0],psizes[0])+
                         "\n")

    else:
        conv = False
        if fh is not None:
            fh.write("String method not converged because it is"+
                     " the first step\n")

    if conv and fh is not None:
        fh.write("String method CONVERGED!\n")
            
    return conv

    

class DensityStringOpt(object):


    def __init__(self,
                 denest,
                 inp_pts, path_npts, path_fcs,
                 sim_size,
                 dampfactor,
                 tol, maxit,
                 smooth_fact,smooth_nmin,smooth_nmax,
                 fix0=False,fix1=False,
                 method=None):
        import sys

        self.path_npts = path_npts
        self.path_fcs = path_fcs
        self.sim_size = sim_size
        self.tol = tol
        self.maxit = maxit
        self.smooth_fact = smooth_fact
        self.smooth_nmin = smooth_nmin
        self.smooth_nmax = smooth_nmax
        self.fix0 = fix0
        self.fix1 = fix1
        self.method = method
        self.dampfactor = dampfactor
        self.strings = []

        if denest is not None:
            s = DensityString(denest,inp_pts,path_npts,
                              path_fcs,sim_size,
                              dampfactor,
                              method=method)
            for it in range(self.maxit):
                opath = None
                if len(self.strings) > 0:
                    opath = self.strings[-1]
                self.strings.append(s)
                sys.stdout.write("Testing convergence for iteration %i\n"%(it))
                #if s.query_convergence(tol,sys.stdout):
                if CheckDensityStringConv( opath, s,
                                           self.smooth_fact,
                                           self.smooth_nmin,
                                           self.smooth_nmax,
                                           tol, fh=sys.stdout ):
                    break
                else:
                    s = s.next(fix0,fix1)
                

    def SmoothPath(self,sfact,nmin,nmax):
        self.strings.append( self.strings[-1].GetSmoothedPath(sfact,nmin,nmax) )
        

    @classmethod
    def from_string(cls,s,
                    tol,maxit,
                    smooth_fact,smooth_nmin,smooth_nmax,
                    fix0=False,fix1=False):
        import sys
        
        self = DensityStringOpt(s.denest,s.inp_pts,
                                s.path_npts,s.path_fcs,
                                s.sim_size,
                                s.dampfactor,
                                tol, maxit,
                                smooth_fact,smooth_nmin,smooth_nmax,
                                fix0=fix0,fix1=fix1,
                                method=s.method)
        if s.denest is None:
            for it in range(self.maxit):
                opath = None
                if len(self.strings) > 0:
                    opath = self.strings[-1]
                self.strings.append(s)
                sys.stdout.write("Testing convergence for iteration %i\n"%(it))
                if CheckDensityStringConv( opath, s,
                                           self.smooth_fact,
                                           self.smooth_nmin,
                                           self.smooth_nmax,
                                           tol, fh=sys.stdout ):
                    break
                else:
                    s = s.next(fix0,fix1)
        return self
        
                    
    def __getitem__(self,i):
        return self.strings[i]

    def __len__(self):
        return len(self.strings)
                
    def restart(self,denest,
                path_npts=None,
                path_fcs=None,
                sim_size=None,
                dampfactor=None,
                tol=None,maxit=None,
                smooth_fact=None,smooth_nmin=None,smooth_nmax=None,
                fix0=None,fix1=None,
                method=None):
        if path_npts is None:
            path_npts = self.path_npts
        if path_fcs is None:
            path_fcs = self.path_fcs
        if sim_size is None:
            sim_size = self.sim_size
        if tol is None:
            tol = self.tol
        if maxit is None:
            maxit = self.maxit
        if smooth_fact is None:
            smooth_fact = self.smooth_fact
        if smooth_nmin is None:
            smooth_nmin = self.smooth_nmin
        if smooth_nmax is None:
            smooth_nmax = self.smooth_nmax
        if fix0 is None:
            fix0 = self.fix0
        if fix1 is None:
            fix1 = self.fix1
        if method is None:
            method = self.method
        if dampfactor is None:
            dampfactor = self.dampfactor
            
        return DensityStringOpt(denest,
                                self.strings[-1].inp_pts,
                                path_npts,path_fcs,
                                sim_size,
                                dampfactor,
                                tol,maxit,
                                smooth_fact,smooth_nmin,smooth_nmax,
                                fix0=fix0,fix1=fix1,
                                method=method)

    
    @classmethod
    def load(cls,fname):
        import os
        import pickle
        s=None
        if os.path.exists(fname):
            fh=open(fname,"rb")
            s = pickle.load(fh)
            fh.close()
        else:
            raise Exception("File not found: %s"%(fname))
        return s
    

    def save(self,fname):
        import pickle
        import copy

        try:
            if True:
                ####
                tmp = copy.deepcopy(self)
                for i in range(len(tmp.strings)):
                    tmp.strings[i].denest = None
                    #for j in range(len(tmp.strings[i].path)):
                        #tmp.strings[i].path[j].hdf = None
                        #tmp.strings[i].path[j].hdf_eff = None

                #####
                fh=open(fname,"wb")
                pickle.dump(tmp,fh)
                fh.close()
            else:
                fh=open(fname,"wb")
                pickle.dump(self,fh)
                fh.close()
        except Exception as e:
            raise Exception("Could not write %s because: %s"%(fname,str(e)))

        
class DensityStringSimLimits(object):
    def __init__(self,grid):
        import copy
        self.grid = copy.deepcopy(grid)
        self.maxfcs=[0]*self.grid.ndim
        self.minfcs=[0]*self.grid.ndim
        self.tdisp=0.75
        self.SetLimits( 50, 300, 0.4, 2.0 )
        
    def SetLimits(self, nonper_min, nonper_max, per_min, per_max):
        for d in range(self.grid.ndim):
            if self.grid.dims[d].isper:
                self.maxfcs[d] = per_max
                self.minfcs[d] = per_min
            else:
                self.maxfcs[d] = nonper_max
                self.minfcs[d] = nonper_min
                

        
        
