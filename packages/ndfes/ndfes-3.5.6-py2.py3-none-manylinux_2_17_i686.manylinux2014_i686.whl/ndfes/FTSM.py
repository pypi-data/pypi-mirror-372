#!/usr/bin/env python3


def StringDistObj(xs,pspl,refpt):
    """Utility function for GetMatchingTs"""
    import numpy as np
    #
    # dx^2 + dy^2
    #
    pt = pspl.GetValue(xs[0])
    dpt = pspl.GetValue(xs[0],nu=1)
    u = pt-refpt
    X2 = np.linalg.norm(u)**2
    g = np.array([2*np.dot(u,dpt)])
    #print("%9.5f %10.2e"%(xs[0],X2))
    return X2,g



def GetUniformPathDeltasFromPts(upts):
    """The vectors parallel to the path, whose lengths are the distance
    between adjacent, uniformly discretized points
    
    Parameters
    ----------
    upts : numpy.ndarray, shape=(Nsim,Ndim)
        The uniformly discretized points

    Returns
    -------
    dw : numpy.ndarray, shape=(Nsim,Ndim)
        The (non-unit) tangent vectors
    """
    import numpy as np
    nsim = upts.shape[0]

    dws = []
    for i in range(nsim):
        if i == 0:
            dw = upts[i+1,:] - upts[i,:]
            #dw = self.pspl.GetValue(ts[i+1])-self.pspl.GetValue(ts[i])
        elif i == nsim-1:
            dw = upts[i,:] - upts[i-1,:]
            #dw = self.pspl.GetValue(ts[i])-self.pspl.GetValue(ts[i-1])
        else:
            dw = 0.5*(upts[i+1,:] - upts[i-1,:])
            #dw = 0.5*( self.pspl.GetValue(ts[i+1]) \
            #           - self.pspl.GetValue(ts[i-1]) )
        dws.append(dw)
    return np.array(dws)



def GetUniformPathDeltasFromPCurve(pspl):
    """The vectors parallel to the path, whose lengths are the distance
    between adjacent, uniformly discretized points
    
    Parameters
    ----------
    pspl : ndfes.PCurve
        Parametric curve. The number of output points will be the
        same as the number of control points

    Returns
    -------
    dw : numpy.ndarray, shape=(Nsim,Ndim)
        The (non-unit) tangent vectors
    """
    import numpy as np
    nsim = pspl.x.shape[0]
    ndim = pspl.x.shape[1]
    ts = np.linspace(0,1,nsim)
    upts = np.zeros( (nsim,ndim) )
    for i in range(nsim):
        upts[i,:] = pspl.GetValue( ts[i] )
    return GetUniformPathDeltasFromPts(upts)



def GetMatchingTs(aspl,bspl):
    """Find the points on bspl that are closest to the 
    uniformly-spaced points on aspl.

    Parameters
    ----------
    aspl : ndfes.PathUtils.PCurve
        A parametric curve. This curve is uniformly discretized.
        The number of points is the same as the number of control points

    bspl : ndfes.PathUtils.PCurve
        t-values are optimized to find the points closest to aspl

    Returns
    -------
    bts : numpy.ndarray, shape=(Npts,)
        The t-values on bspl that minimize the Euclidean distance to
        aspl
    """
    import numpy as np
    from scipy.optimize import minimize
    
    n = len(aspl.t)
    uts = np.linspace(0,1,n)
    bts = np.linspace(0,1,n)
    for i in range(n):
        refpt = aspl.GetValue(uts[i])
        res = minimize( StringDistObj, [uts[i]],
                        args=(bspl,refpt),
                        jac=True,
                        method='L-BFGS-B',
                        bounds=[(0,1)],
                        tol=1.e-14)
        bts[i] = res.x[0]
        # pt = bspl.GetValue(bts[i])
        # d1 = np.linalg.norm(pt-refpt)
        # pt = bspl.GetValue(uts[i])
        # d2 = np.linalg.norm(pt-refpt)
        # print( "%9.4f %9.4f"%(d1,d2) )
    return bts




def GetSlopes(paths,closest):
    """
    For each dimension of each window, create a plot of position versus
    iteration, and calculate the slope.  All supplied paths are used
    in the regression. The values are the input splines, not the predicted
    centroids.

    Parameters
    ----------
    paths : list of ndfes.FTSM.FTSMString
        The string iterations to consider

    closest : bool
        If False, then uniformly discretize each string.
        If True, then uniformly discretize the last string, and find
        the closest points from the other strings

    Returns
    -------
    allms : numpy.array, shape=(Nsim,Ndim)
        The slope of each dimension for each window with respect to
        iteration
    """
    from scipy.stats import linregress
    import numpy as np

    allrcs = []
    for path in paths[:-1]:
        if closest:
            ts = GetMatchingTs(paths[-1].pspl,path.pspl)
            allrcs.append( np.array([path.pspl.GetValue(t) for t in ts]) )
        else:
            ts = np.linspace(0,1,len(paths[-1].sims))
            allrcs.append( np.array([path.pspl.GetValue(t) for t in ts]) )
            
    ts = np.linspace(0,1,len(paths[-1].sims))
    allrcs.append(np.array([paths[-1].pspl.GetValue(t) for t in ts]) )
    allrcs = np.array( allrcs )

    nobs = paths[-1][0].obs_n
    nit = allrcs.shape[0]
    nsim = allrcs.shape[1]
    ndim = allrcs.shape[2]
    allms = []
    for isim in range(nsim):
        ms = []
        for idim in range(ndim):
            xs = []
            ys = []
            xs = np.array([ i for i in range(nit) ])
            ys = allrcs[:,isim,idim]
            res = linregress(xs,ys)
            ms.append(res.slope)
        allms.append(ms)
        #print("%2i %s %s"%(isim,
        #                      " ".join(["%9.5f"%(p) for p in ps]),
        #                      " ".join(["%9.5f"%(m) for m in ms])
        #))
    allms = np.array(allms)
    return allms



def GenericMinSlopeTest(D,mlen,TOL):
    from scipy.stats import linregress

    minslope = 1.e+30
    for istart in range(len(D)-mlen+1):
        idxs = [ i for i in range(istart,len(D)) ]
        res = linregress(idxs,D[idxs])
        if abs(res.slope) < minslope:
            minslope = abs(res.slope)
    conv = False
    if minslope < TOL:
        conv = True
    return minslope,conv



def FTSMCptRMSD(paths):
    import numpy as np
    from scipy.stats import linregress
    from scipy.stats import ttest_ind

    nsim = len(paths[0].sims)
    #nsim = 100
    npath = len(paths)
    allrcs = []
    for path in paths:
        ts = np.linspace(0,1,nsim)
        allrcs.append( np.array([path.pspl.GetValue(t) for t in ts]) )

    allrcs = np.array( allrcs )
    ndim = allrcs.shape[2]

    #for i in range(nsim):
    #    print(allrcs[0,i,:])
        
    
    Ds = np.zeros( (npath,) )
    for i in range(npath):
        D = 0
        for j in range(nsim):
            d = np.linalg.norm( allrcs[i,j,:] - allrcs[0,j,:] )
            D += d*d
        Ds[i] = np.sqrt( D / ( nsim * ndim ) )

    # Ms = np.zeros( (npath,) )
    # for it in range(npath):
    #     if it == 0:
    #         continue
    #     istart = max(0,it-nvals+1)
    #     xs = [ i for i in range(istart,it+1) ]
    #     ys = Ds[xs]
    #     res = linregress(xs,ys)
    #     Ms[it] = res.slope
 
    # if npath > 1:
    #     Ms[0] = Ms[1]
        
    # Ts = np.zeros( (npath,) )
    # #nset = max(nvals,8)
    # #if nset % 2 == 1:
    # #    nset += 1
    # #nhalf = nset//2
    # nset = nvals
    # for it in range(npath):
    #     if it == 0:
    #         continue
    #     istart = it-nset+1
    #     #imid = istart + nhalf
    #     #istop = it+1
    #     #if istart < 0:
    #     #    continue
    #     istart = max(0,istart)
    #     xs = [ i for i in range(istart,it) ]
    #     ys = Ds[xs]
    #     mu = np.mean(ys)
    #     #sig = np.std(ys)
    #     #err = sig / np.sqrt( len(ys) )
    #     Ts[it] = Ds[it] - mu
    # Ts[0] = 1
    return Ds


def FTSMCheckRMSD(paths,nvals,fh):
    Ds = FTSMCptRMSD(paths)
    minslope,conv = GenericMinSlopeTest(Ds,nvals,1.e-3)
    if fh is not None:
        fh.write("\nCheck Path RMSD relative to initial guess\n")
        fh.write("%5s %12s\n"%("Iter","RMSD"))
        for it in range(Ds.shape[0]):
            fh.write("%5i %12.4f\n"%(it,Ds[it]))
        fh.write("\nMin slope in RMSD %12.3e"%(minslope))
        if conv:
            fh.write(" Path is effectively CONVERGED\n")
        else:
            fh.write(" Path NOT converged\n")

    

def FTSMCheckSlopes(opt,nvals,distol,angtol,isang,closest,fh=None):
    """Test if the optimization should be terminated because the
    strings stopped moving over a series of iterations.

    Parameters
    ----------
    opt : ndfes.FTSM.FTSMOpt
        The optimization object

    nvals : int
        The maximum number of iterations to use in the linear regressions

    distol : float
        The slope tolerance on distances

    angtol : float
        The slope tolerance on angles

    isang : list of bool, len=Ndim
        True if the dimension is an angle. False if it is a distance

    closest : bool
        If False, then uniformly discretize each string. If True, then
        uniformly discretize the final string, and find the closest
        points from the previous strings.

    fh : opened writable filehandle, default=None
        Print summary to file

    Returns
    -------
    conv : bool
        True if the slopes of each dimension of all windows is less than
        the appropriate tolerance
    
    dismax : float
        This is the value of distol that would be required to pass all tests

    angmax : float
        This is the value of angtol that would be required to pass all tests
    """
    n = len(opt)
    ifirst = max(0,n - nvals)
    allconv = True
    dismax = 0
    angmax = 0
    if n - ifirst > 1:
        ms = GetSlopes(opt.paths[ifirst:n],closest)
        nwin = ms.shape[0]
        ndim = ms.shape[1]
        for i in range(nwin):
            conv=True
            mstr = []
            for dim in range(ndim):
                m = ms[i,dim]
                mtol = distol
                if isang[dim]:
                    mtol = angtol
                if abs(m) > mtol:
                    conv = False
                    c="F"
                else:
                    c="T"
                if isang[dim]:
                    angmax = max(angmax,abs(m))
                else:
                    dismax = max(dismax,abs(m))
                mstr.append("[|m=%7.4f|<%6.4f ? %s]"%(m,mtol,c))
            if conv:
                c="T"
            else:
                allconv=False
                c="F"
            if fh is not None:
                fh.write("%2i %s %s\n"%(i+1,c," ".join(mstr)))
    else:
        allconv = False
    return allconv,dismax,angmax
    



def CptCentroidAndStddev(rcs,hdf,denest):
    """Computes the center and standard deviation of a biased density
    whose umbrella potential is located at rcs

    Parameters
    ----------
    rcs : numpy.ndarray, shape=(Ndim,)
        The location of the umbrella potential

    hdf : dict, keys = int, values = float or numpy.array 
          (shape=denest.quadwts.shape)
        The histogram density function generated from DensityEst.GetDensity
        or  DensityEst.GetContinuousDensity

    denest : ndfes.DensityEst.DensityEst
        The density calculator object

    Returns
    -------
    mu : numpy.ndarray, shape=(Ndim,)
        The center of the distribution

    err : numpy.ndarray, shape=(Ndim,)
        The standard deviation of the deviation (the square root of the
        covariance matrix diagonal elements)
    """
    
    import numpy as np
        
    fes = denest.fes
    ndim = fes.grid.ndim
    mu  = np.zeros( (ndim,) )
    err = np.zeros( (ndim,) )

    key = list(hdf.keys())[0]
    if isinstance( hdf[key], float ):

        for gidx,sbin in sorted(fes.bins.items()):
            wc = fes.grid.DiffCrd(sbin.center,rcs)+rcs
            mu += hdf[gidx] * wc

        for gidx,sbin in sorted(fes.bins.items()):
            wc = fes.grid.DiffCrd(sbin.center,rcs)+rcs
            err += hdf[gidx] * (wc-mu)**2
        
    else:
    
        for gidx,sbin in sorted(fes.bins.items()):
            wc = fes.grid.DiffCrd(sbin.center,rcs)+rcs
            qpts = wc + denest.qpts
            mu += np.dot( denest.qwts * hdf[gidx], qpts )

        for gidx,sbin in sorted(fes.bins.items()):
            wc = fes.grid.DiffCrd(sbin.center,rcs)+rcs
            qpts = wc + denest.qpts
            err += np.dot( denest.qwts * hdf[gidx] , (qpts-mu)**2 )

    err = np.sqrt( err )

    return mu,err



def CptEffectiveHDF(size,hdf,denest,dampfactor):
    """Damps the density to effectively increase the free energy in those
    areas that have not been sufficiently sampled.

    Given the expected number of samples, N, and the density function p(z),
    expected number of samples drawn from a bin is 
        Nexpect(i) = \int_Vi N p(z) dz, where
    the integral is over the volume of the bin i.

    We can count the number of samples that we have actually observed in
    the bin, Nobs, and derive a scale factor
        f(i) = 1, if Nobs >= Nexpect
          = Nobs(i)/Nexpect(i), otherwise

    We then scale the density in each bin peff(z \in i) = f(i) p(z \in i)
    and renormalize peff(z).

    Parameters
    ----------
    size : float
        The expected number of samples to draw from the biased simulation

    hdf : dict, keys = int, values = float or numpy.array 
          (shape=denest.quadwts.shape)
        The histogram density function generated from DensityEst.GetDensity
        or  DensityEst.GetContinuousDensity

    denest : ndfes.DensityEst.DensityEst
        The density calculator object

    dampfactor : float
        If dampfactor is 1, then the output density is the damped density.
        If it is 0, then the output density is the undamped density.
        Intermediate values return a linear combination of the 2 densities.

    Returns
    -------

    eff_hdf : dict, keys = int, values = float or numpy.array 
          (shape=denest.quadwts.shape)
        This is the same thing as the input density, but the values in
        each bin have been modified.
    """
    
    from collections import defaultdict as ddict
    import numpy as np
        
    hdf_eff = ddict(int)
    scalef = ddict(int)

    fes = denest.fes

    w1 = min(1,max(0,dampfactor))
    w2 = 1-w1

    size_eff = 0

    key = list(hdf.keys())[0]
    if isinstance( hdf[key], float ):

        for gidx,sbin in sorted(fes.bins.items()):
            rho = hdf[gidx]
            nrho = size*rho
            scalef[gidx] = 1
            if sbin.size < nrho:
                scalef[gidx] = sbin.size / nrho
            size_eff += scalef[gidx] * nrho

        Q = 0
        for gidx,sbin in sorted(fes.bins.items()):
            hdf_eff[gidx] = scalef[gidx] * hdf[gidx]
            Q += hdf_eff[gidx]

        for gidx,sbin in sorted(fes.bins.items()):
            hdf_eff[gidx] = w1 * hdf_eff[gidx]/Q + w2 * hdf[gidx]
        
        # tsum = 0
        # osum = 0
        # for gidx,sbin in sorted(fes.bins.items()):
        #     tsum += hdf_eff[gidx]
        #     osum += hdf[gidx]
        # print("TSUM : %20.10e %20.10e\n"%(tsum,osum))
        
    else:
    
        for gidx,sbin in sorted(fes.bins.items()):
            rho = np.dot( denest.qwts, hdf[gidx] )
            nrho = size*rho
            scalef[gidx] = 1
            if sbin.size < nrho:
                scalef[gidx] = sbin.size / nrho
            size_eff += scalef[gidx] * nrho

        Q = 0
        for gidx,sbin in sorted(fes.bins.items()):
            hdf_eff[gidx] = scalef[gidx] * hdf[gidx]
            Q += np.dot( denest.qwts, hdf_eff[gidx] )

        for gidx,sbin in sorted(fes.bins.items()):
            hdf_eff[gidx] = w1 * hdf_eff[gidx]/Q + w2 * hdf[gidx]

        # tsum = 0
        # osum = 0
        # for gidx,sbin in sorted(fes.bins.items()):
        #     tsum += np.dot( denest.qwts, hdf_eff[gidx] )
        #     osum += np.dot( denest.qwts, hdf[gidx] )
        # print("TSUM : %20.10e %20.10e"%(tsum,osum))
            
    size_eff = w1*size_eff + w2*size

    #exit(0)
    return hdf_eff,size_eff



def CalcUmbrellaSimDistrib(rcs,fcs,nobs,denest,dampfactor):
    """Computes the mean and standard deviation of the effective and
    undamped biased densities

    Parameters
    ----------
    rcs : numpy.ndarray, shape=(Ndim,)
        The location of the biasing potential

    fcs : numpy.ndarray, shape=(Ndim,)
        Twice the force constants (Ubias = k*(r-rcs)**2)

    nobs : float
        The expected number of samples to be drawn from the
        biased simulation

    denest : ndfes.DensityEst.DensityEst
        The density calculator

    dampfactor : float
        The linear combination of damped and undamped densities
        used to define the effective density. See CptEffectiveHDF

    Returns
    -------
    obs_mean : numpy.ndarray, shape=(Ndim,)
        The mean of the density, calculated from the undamped density

    obs_std : numpy.ndarray, shape=(Ndim,)
        The standard deviation of the undamped density in each dimension

    eff_n : float
        This should be ignored. It was, at one time, the effective number
        of samples drawn from the effective density, but it is no longer
        being calculated correctly. (TODO... although it's not used for
        anything)
    
    eff_mean : numpy.ndarray, shape=(Ndim,)
        The mean of the effective density

    eff_std : numpy.ndarray, shape=(Ndim,)
        The standard deviation of the effective density in each dimension
    
    """
    
    hdf = denest.GetContinuousDensity(fcs,rcs)
    #hdf = denest.GetDensity(fcs,rcs)
    obs_mean,obs_std = CptCentroidAndStddev(rcs,hdf,denest)
    eff_n = nobs
    eff_mean = obs_mean
    eff_std = obs_std
    if dampfactor > 0 and nobs > 0:
        eff_hdf, eff_n = CptEffectiveHDF(nobs,hdf,denest,dampfactor)
        eff_mean, eff_std = CptCentroidAndStddev(rcs,eff_hdf,denest)
        
    return obs_mean,obs_std,eff_n,eff_mean,eff_std



def CalcDisplacementPercentage(tdisp,dw,rc,fc,nobs,denest,dampfactor):
    """Represents the displacement of a centroid as a percentage of
    movement along the path, such that a percentage of 0.5 means that
    the centroid has moved half-way between the umbrella center and
    the neighboring umbrella center.
    
    Parameters
    ----------
    tdisp : float
        The "target" displacement percentage. If the centroid displacement
        is orthogonal to the path, then the output percentage is assumed
        to be the target percentage.

    dw : numpy.ndarray, shape=(Ndim,)
        The vector pointing from 1 umbrella center to a neighbor. Typically
        this is a vector pointing from 1 midpoint to another midpoint.

    rc : numpy.ndarray, shape=(Ndim,)
        The location of the biasing potential
    
    fc : numpy.ndarray, shape=(Ndim,)
        The biasing potential force constants (twice the force constants, 
        technically).

    nobs : float
        The expected number of samples to be drawn from the biased simulation

    denest : ndfes.DensityEst.DensityEst
        The density calculator

    dampfactor : float
        The percentage by which the density should be damped

    Returns
    -------
    perc : float
        The percent displacement of the centroid
    """
    import numpy as np
    lw = np.linalg.norm(dw)
    uw = dw/lw
    sim = FTSMSim.from_density(0,rc,fc,nobs,denest,dampfactor)
    dx = sim.eff_mean - sim.rcs
    lx = np.linalg.norm(dx)
    perc = tdisp
    cosa = 0
    if lx > 0.001:
        ux = dx/lx
        #proj = np.dot(uw,ux)
        #perc = abs(np.dot(uw,dx)/lw)
        cosa = np.dot(uw,ux)
        perc = abs(cosa) * (lx/lw)
        #scale = abs(perc)/tdisp

    return perc,cosa


def GetScaledForceConstants(minfcs,maxfcs,fc0,w):
    """Increases or decreases the force constants between allowable
    limits. If -1 < w < 0, then the result scales fc0 towards minfcs.
    If 0 < w < 1, then the result scales fc0 towards maxfcs.

    Parameters
    ----------
    minfcs : numpy.ndarray, shape=(Ndim,)
        The minimum allowable force constants

    maxfcs : numpy.ndarray, shape=(Ndim,)
        The maximum allowable force constants

    fc0 : numpy.ndarray, shape=(Ndim,)
        The unscaled force constants

    w : float from -1 to +1
        The scale factor

    Returns
    -------
    fcs : numpy.ndarray, shape=(Ndim,)
        The scaled force constants
    """
    
    import numpy as np
    w = min(1,max(-1,w))
    if w > 0:
        fcs = (1-w)*fc0 + w*maxfcs
    elif w < 0:
        fcs = (1-abs(w))*fc0 + abs(w)*minfcs
    else:
        fcs = np.array(fc0,copy=True)
    for d in range(len(fcs)):
        fcs[d] = min(maxfcs[d],max(minfcs[d],fcs[d]))
    return fcs


def MakeLinearInterpolator(xs,ys):
    """Sorts the x and y data by values of x and returns a
    linear interpolator

    Parameters
    ----------
    xs : numpy.ndarray, shape=(n,)
        The x-data
    
    ys : numpy.ndarray, shape=(n,)
        The y-data

    Returns
    -------
    interp1d : scipy.interpolate.interp1d
        The linear interpolator
    """
    from scipy.interpolate import interp1d
    xy = [ x for x in sorted(zip(xs,ys)) ]
    xs = [ x[0] for x in xy ]
    ys = [ x[1] for x in xy ]
    
    # for x,y in zip(xs,ys):
    #     print("%12.5f %12.5f"%(x,y))
    # print("")
    
    return interp1d(xs,ys,fill_value="extrapolate")
    

def FindIdealForceConstant(limits,dw,rc,fc,nobs,
                           denest,dampfactor,scale_fc):
    """Calculates the ideal force constant for a simulation. In doing so,
    it assumes that the simulations uniformly discretize the string.
    A force constant is considered "ideal" if the predicted centroid
    displacement along the path matches the desired limit, controlled
    by the tdisp attribute in the FTSMSimLimits class.
    If the predicted centroid does not exceed the target displacement,
    then the force constant is decreased. If it displaces by too much,
    then it is increased. This process is bounded by the maximum
    and minimum allowable force constants controlled by the maxfcs
    and minfcs attributes in the FTSMSimLimits class.

    Parameters
    ----------
    limits : ndfes.FTSM.FTSMSimLimits
        Defines the minimum & maximum allowable force constants and
        the target displacement percentage.

    dw : numpy.ndarray, shape=(Ndim,)
        The vector pointing from 1 umbrella center to a neighbor. Typically
        this is a vector pointing from 1 midpoint to another midpoint.

    rc : numpy.ndarray, shape=(Ndim,)
        The location of the biasing potential
    
    fc : numpy.ndarray, shape=(Ndim,)
        The biasing potential force constants (twice the force constants, 
        technically).

    nobs : float
        The expected number of samples to be drawn from the biased simulation

    denest : ndfes.DensityEst.DensityEst
        The density calculator

    dampfactor : float
        The percentage by which the density should be damped

    scale_fc : bool
        If True, then scale the force constant to the input value
        when the predicted centroid displacement is perpendicular
        to the predicted path

    Returns
    -------
    f : numpy.ndarray, shape=(Ndim,)
        The ideal force constants
    """
    
    import numpy as np
    
    minfcs = limits.minfcs
    maxfcs = limits.maxfcs
    tdisp = limits.tdisp
    
    for d in range(len(fc)):
        fc[d] = min(maxfcs[d],max(minfcs[d],fc[d]))
     
    fc0 = GetScaledForceConstants(minfcs,maxfcs,fc,0)
    p0,cos0 = CalcDisplacementPercentage\
        (tdisp,dw,rc,fc0,nobs,denest,dampfactor)
    print("Initial projection and cosine: %.4f %.4f"%(p0,cos0))
    if p0 < tdisp:
        whi = 0
        phi = p0
        coshi = cos0
        wlo = -1
        flo = GetScaledForceConstants(minfcs,maxfcs,fc,wlo)
        plo,coslo = CalcDisplacementPercentage\
            (tdisp,dw,rc,flo,nobs,denest,dampfactor)
    elif p0 > tdisp:
        whi = 1
        fhi = GetScaledForceConstants(minfcs,maxfcs,fc,whi)
        phi,coshi = CalcDisplacementPercentage\
            (tdisp,dw,rc,fhi,nobs,denest,dampfactor)
        wlo = 0
        plo = p0
        coslo = cos0
    else:
        return fc0

    ws = [wlo,whi]
    ps = [plo,phi]
    coss = [coslo,coshi]

    for it in range(10):
        interp = MakeLinearInterpolator(ps,ws)
        w = interp(tdisp)
        wp = min(1,max(-1,w))
        print("it %2i %.4f w: %s p: %s cos: %s"%(it,wp,
                                        " ".join(["%.4f"%(x) for x in ws]),
                                        " ".join(["%.4f"%(x) for x in ps]),
                                        " ".join(["%.4f"%(x) for x in coss])))

        if wp not in ws:
            f = GetScaledForceConstants(minfcs,maxfcs,fc,wp)
            p,cosp = CalcDisplacementPercentage\
                (tdisp,dw,rc,f,nobs,denest,dampfactor)
            #print("New w",w,wp,f,p,tdisp)
            ws.append(wp)
            ps.append(p)
            coss.append(cosp)
            print("fc: %s"%(" ".join(["%8.2f"%(x) for x in f])))
            if abs(p-tdisp) < 0.001:
                if scale_fc:
                    wnew = wp * abs(cosp)
                    print("Scaling wnew = w * abs(cosa) = %.4f"%(wnew))
                    f = GetScaledForceConstants(minfcs,maxfcs,fc,wnew)
                    print("fc: %s"%(" ".join(["%8.2f"%(x) for x in f])))
                break
        else:

            idx = 0
            mindp = 1.e+8
            for i,p in enumerate(ps):
                dp = abs(p-tdisp)
                if dp < mindp:
                    idx = i
                    mindp = dp

            w0idx = 0
            mindw = 1.e+8
            for i,w in enumerate(ws):
                aw = abs(w)
                if aw < mindw:
                    w0idx = i
                    mindw = aw

            
            if ps[idx] < tdisp \
               and ps[w0idx] < ps[idx] \
               and ws[w0idx] < ws[idx]:
                idx = w0idx
                
            wp = ws[idx]

            if scale_fc:
                #idx = ws.index(wp)
                cosp = coss[idx]
                wnew = wp * abs(cosp)
                print("Scaling wnew = w * abs(cosa) = %.4f"%(wnew))
                f = GetScaledForceConstants(minfcs,maxfcs,fc,wnew)
                print("fc: %s"%(" ".join(["%8.2f"%(x) for x in f])))
            else:
                f = GetScaledForceConstants(minfcs,maxfcs,fc,wp)
                print("fc: %s"%(" ".join(["%8.2f"%(x) for x in f])))
            break
    return f



def FTSMCheckSameMeans(opath,cpath,ptol,fh=None):
    """Checks if the centroids from two paths are statistically the same

    Parameters
    ----------
    opath : ndfes.FTSM.FTSMString
        The old path

    cpath : ndfes.FTSM.FTSMString
        The current path

    ptol : float
        The critical p-value used in Welch's t-test to determine if
        the two means are the same.  Larger values (values close to one)
        require greater agreement between the two means to satisfy the
        test.

    fh : opened file handle, default=None
        If not None, the tests are summarized by writing to the file

    Returns
    -------
    conv : bool
        Whether all windows passed the test

    pmin : float
        The value of ptol that would cause all tests to pass
    """

    import numpy as np
    from scipy.stats import ttest_ind_from_stats


    cps = None
    if fh is not None:
        cps = cpath.GetPathProjection(cpath)

    pmin = 2
    conv=True
    nsim = len(opath)
    ndim = opath[0].rcs.shape[0]
    for i in range(nsim):
        
        if opath[i].obs_n > 0:
            ons = np.array([opath[i].obs_n]*ndim)
        else:
            ons = np.array([100]*ndim)
            
        if cpath[i].obs_n > 0:
            cns = np.array([cpath[i].obs_n]*ndim)
        else:
            cns = np.array([100]*ndim)

        tvals,pvals = ttest_ind_from_stats\
            ( opath[i].eff_mean, opath[i].eff_std, ons,
              cpath[i].eff_mean, cpath[i].eff_std, cns,
              equal_var=False,
              alternative='two-sided' )
        
        diff = abs(opath[i].eff_mean - cpath[i].eff_mean)

        for dim in range(ndim):
            if pvals[dim] < pmin:
                pmin = pvals[dim]
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
                    
            fh.write("img %3i %s"%(i+1,allconv)+
                     " cos: %5.2f "%(cps[i])+
                     " ".join(["[d:%8.1e p: %5.3f>%5.3f ? %s]"%(d,p,ptol,c)
                               for d,p,c in zip(diff,pvals,convs)])+
                     "\n")
            #"%9.3f %9.3f %9.3f %9.3f"%(ons[0],cns[0],opath[i].eff_n,cpath[i].eff_n)+
    return conv,pmin



class NearbyBin(object):
    def __init__(self,gidx,bidxs,center,size,simidx):
        import copy
        import numpy as np
        self.gidx = gidx
        self.bidxs = copy.deepcopy(bidxs)
        self.center = np.array( center, copy=True )
        self.simidx = simidx
        self.size = size
        self.reserved = False
        

def GetMeshIdxs( xgrid, conv_layers, bidxs ):
    
    from . GridUtils import LinearPtsToMeshPts
    
    ndim = xgrid.ndim
    didx = conv_layers
    nd = 2*didx+1

    def INTWRAP(i,n):
        return (i%n+n)%n

    lidxs = []
    for dim in range(ndim):
        dimsize = xgrid.dims[dim].size
        bidx = bidxs[dim]
        if xgrid.dims[dim].isper:
            lidxs.append( [ INTWRAP(k,dimsize)
                            for k in range(bidx-didx, bidx+didx+1) ] )
        else:
            lidxs.append( [ k
                            for k in range(bidx-didx, bidx+didx+1) ] )
    midxs = LinearPtsToMeshPts( lidxs )
    return midxs

    

def CheckFESConv( rcs, fcs, nobs, minfc, maxfc, pspl, den, dampfactor, conv_layers, conv_samples, fh=None ):
    import numpy as np
    import sys
    import copy
    from collections import defaultdict as ddict
    from . SpatialDim import SpatialDim
    from . VirtualGrid import VirtualGrid
    from . GridUtils import LinearPtsToMeshPts

    def INTWRAP(i,n):
        return (i%n+n)%n

    DEF_FC_SIZE = 25
    
    rcs = np.array(rcs,copy=True)
    fcs = np.array(fcs,copy=True)
    
    didx = conv_layers
    nd = 2*didx+1

    nsim = rcs.shape[0]
    ndim = rcs.shape[1]

    simsizes = [0]*nsim
    
    xdims = []
    for dim in range(ndim):
        orig = den.fes.grid.dims[dim]
        if orig.isper:
            xdims.append( SpatialDim( orig.xmin, orig.xmax,
                                      orig.size, orig.isper ) )
        else:
            w = orig.width
            xdims.append( SpatialDim( orig.xmin - didx*w,
                                      orig.xmax + didx*w,
                                      orig.size + 2*didx,
                                      orig.isper ) )
    xgrid = VirtualGrid(xdims)
    newbidxs = ddict(list)
    newgidxs = ddict(int)
    newsizes = ddict(int)
    for gidx in den.fes.bins:
        xbidx = xgrid.GetBinIdx( den.fes.bins[gidx].center )
        xgidx = xgrid.CptGlbIdxFromBinIdx( xbidx )
        newgidxs[xgidx] = gidx
        newbidxs[xgidx] = xbidx
        newsizes[xgidx] = den.fes.bins[gidx].size

    nearbybins = ddict(int)

    prev_gidx=0
    npts = 2000
    dt = 1./(npts-1.)
    for ipt in range(npts):
        c = pspl.GetValue( ipt*dt )
        bidxs = xgrid.GetBinIdx( c )
        gidx = xgrid.CptGlbIdxFromBinIdx(bidxs)
        if ipt > 0 and gidx == prev_gidx:
            continue
        prev_gidx = gidx

        midxs = GetMeshIdxs( xgrid, conv_layers, bidxs )
        nmidxs = midxs.shape[0]
        for i in range(nmidxs):
            mbidxs = midxs[i,:]
            mgidx = xgrid.CptGlbIdxFromBinIdx( mbidxs )
            if mgidx not in nearbybins:
                center = xgrid.GetBinCenter( mbidxs )
                if mgidx in newsizes:
                    size = newsizes[mgidx]
                else:
                    size = 0
                #simidx = np.argmin( np.linalg.norm( rcs - center, axis=0 ) )
                simidx = 0
                rmin = 1.e+30
                for isim in range(nsim):
                    r = np.linalg.norm( rcs[isim,:] - center )
                    if r < rmin:
                        rmin=r
                        simidx=isim
                    
                nearbybins[mgidx] = NearbyBin(mgidx,mbidxs,center,size,simidx)

    simrcs = np.array( rcs, copy=True )
    simfcs = np.array( fcs, copy=True )
    simgidx = [0]*nsim

    for isim in range(nsim):
        bidxs = xgrid.GetBinIdx( rcs[isim,:] )
        ptarget = None
        mindist = 1.e+30
        minsize = 1.e+30
        for mgidx in nearbybins:
            if nearbybins[mgidx].simidx == isim and not nearbybins[mgidx].reserved:
                size = nearbybins[mgidx].size
                dist = np.linalg.norm( rcs[isim,:] - nearbybins[mgidx].center )
                if size < minsize or (size==minsize and dist<mindist):
                    minsize=size
                    mindist=dist
                    ptarget=mgidx
        if ptarget is None:
            midxs = GetMeshIdxs(xgrid,conv_layers,bidxs)
            nmidxs = midxs.shape[0]
            for i in range(nmidxs):
                mbidxs = midxs[i,:]
                mgidx = xgrid.CptGlbIdxFromBinIdx( mbidxs )
                if mgidx not in nearbybins:
                    raise Exception(f"Failed to locate gidx {mgidx} in nearbybins")
                elif not nearbybins[mgidx].reserved:
                    size = nearbybins[mgidx].size
                    dist = np.linalg.norm( rcs[isim,:] - nearbybins[mgidx].center )
                    if size < minsize or (size==minsize and dist<mindist):
                        minsize=size
                        mindist=dist
                        ptarget=mgidx
        if ptarget is None:
            raise Exception(f"Failed to locate a target bin for isim {isim}")

        nearbybins[ptarget].reserved = True
        simgidx[isim] = ptarget
        simsizes[isim] = nearbybins[ptarget].size
        w = min(1,simsizes[isim]/DEF_FC_SIZE)
        simfcs[isim,:] = (1-w)*minfc[:] + w*fcs[isim,:]
        simrcs[isim,:] = nearbybins[ptarget].center[:]


    fhs = [ sys.stdout ]
    if fh is not None:
        fhs.append(fh)

    for cout in fhs:
        cout.write(f"\nFES sampling check around the new path.\n"+
	           "What is the fewest number of bin samples within "+
	           f"{conv_layers} layers of each control point?\n"+
	           f"If each nearby bin contains at least {conv_samples}"+
	           " samples, then we assume the FES is converged.\n\n");
        cout.write("isim MinSamples Conv?\n")
        isconv = True
        num_not_enough = 0
        for isim in range(nsim):
            cout.write("%4i%11i"%(isim+1,simsizes[isim]))
            if simsizes[isim] < conv_samples:
                isconv = False
                num_not_enough += 1
                cout.write(" F\n")
            else:
                cout.write(" T\n")
        if isconv:
            cout.write("\nSampling appears to be converged\n")
        else:
            cout.write("\nSampling is NOT converged. Areas near the path need more samples.\n"+
                       f"There are {num_not_enough} simulations with insufficient sampling.\n")

    cout = sys.stdout


    cout.write("\n\nSTAGE 1: Check if centroids of target bins remains\n"+
               "         in the bin. If not, make a linear guess for\n"+
               "         a proposed umbrella center.\n\n")

    p0 = [ FTSMSim.from_density( 0, simrcs[isim,:], simfcs[isim,:],
                                 nobs[isim], den, dampfactor )
           for isim in range(nsim) ]

    isempty = [ size == 0 for size in simsizes ]
    proprcs = np.array( simrcs, copy=True )
    propgidx = [ x for x in simgidx ]
    donefc = [ False ]*nsim
    donerc = [ False ]*nsim

    for isim in range(nsim):
        mbin = nearbybins[propgidx[isim]]
        if isempty[isim]:
            donefc[isim] = True
            donerc[isim] = True
            cstr = "".join(["%10.4f"%(x) for x in mbin.center])
            cout.write("sim %3i %s not moving: empty\n"%(isim+1,cstr))
        else:
            cen_bidxs = xgrid.GetBinIdx( p0[isim].eff_mean )
            cen_gidx  = xgrid.CptGlbIdxFromBinIdx( cen_bidxs )
            sim_bidxs = xgrid.GetBinIdx( p0[isim].rcs )
            sim_gidx  = xgrid.CptGlbIdxFromBinIdx( sim_bidxs )
            if sim_gidx != cen_gidx:
                disp = p0[isim].eff_mean - p0[isim].rcs
                est  = p0[isim].rcs - disp
                for dim in range(ndim):
                    xmin = xgrid.dims[dim].xmin+1.e-10
                    xmax = xgrid.dims[dim].xmax-1.e-10
                    est[dim] = min(xmax,max(xmin,est[dim]))
                cen_bidxs = xgrid.GetBinIdx( est )
                cen_gidx  = xgrid.CptGlbIdxFromBinIdx( cen_bidxs )

            if sim_gidx == cen_gidx:
                donefc[isim] = True
                donerc[isim] = True
                cstr = "".join(["%10.4f"%(x) for x in mbin.center])
                cout.write("sim %3i %s not moving: centroid remains\n"%(isim+1,cstr))
            else:
                if cen_gidx not in nearbybins:
                    newsize = 0
                    if cen_gidx in newsizes:
                        newsize = newsizes[cen_gidx]
                    c = xgrid.GetBinCenter( cen_bidxs )
                    obin = NearbyBin(cen_gidx,cen_bidxs,c,newsize,isim)
                    obin.reserved = True
                    nearbybins[cen_gidx] = obin
                    donefc[isim]=False
                    donerc[isim]=False
                    if newsize == 0:
                        donefc[isim] = True
                    nearbybins[propgidx[isim]].reserved = False
                    propgidx[isim] = cen_gidx
                    proprcs[isim,:] = c[:]
                    cstr = "".join(["%10.4f"%(x) for x in mbin.center])
                    dstr = "".join(["%10.4f"%(x) for x in c])
                    cout.write("sim %3i %s moving to: %s (note: outside tube)\n"\
                               %(isim+1,cstr,dstr))
                else:
                    if nearbybins[cen_gidx].reserved:
                        donefc[isim]=False
                        donerc[isim]=True
                        cstr = "".join(["%10.4f"%(x) for x in mbin.center])
                        cout.write("sim %3i %s not moving: reserved\n"%(isim+1,cstr))
                    else:
                        donefc[isim]=False
                        donerc[isim]=False
                        c = nearbybins[cen_gidx].center
                        cstr = "".join(["%10.4f"%(x) for x in mbin.center])
                        dstr = "".join(["%10.4f"%(x) for x in c])
                        cout.write("sim %3i %s moving to: %s\n"\
                               %(isim+1,cstr,dstr))
                        nearbybins[propgidx[isim]].reserved = False
                        propgidx[isim] = cen_gidx
                        nearbybins[propgidx[isim]].reserved = True
                        proprcs[isim,:] = c[:]

    nres = 0
    for gidx in nearbybins:
        if nearbybins[gidx].reserved:
            nres += 1
    cout.write("Total reservations: %i\n"%(nres))


    cout.write("\n\nSTAGE 2: If the simulation center has changed, make\n")
    cout.write("         sure its centroid is closer to the target\n")
    cout.write("         bin than the simply placing the center at\n")
    cout.write("         the bin. If not, revert the linear guess.\n\n")


    p1 = [ FTSMSim.from_density( 0, proprcs[isim,:], simfcs[isim,:],
                                 nobs[isim], den, dampfactor )
           for isim in range(nsim) ]

    for isim in range(nsim):
        cstr = "".join(["%10.4f"%(x) for x in proprcs[isim,:]])
        dstr = "".join(["%10.4f"%(x) for x in simrcs[isim,:]])
        if donerc[isim]:
            cout.write("sim %3i %s untested\n"%(isim+1,cstr))
        else:
            r0 = np.linalg.norm( p0[isim].eff_mean - simrcs[isim,:] )
            r1 = np.linalg.norm( p1[isim].eff_mean - simrcs[isim,:] )
            if r1 > r0:
                if nearbybins[simgidx[isim]].reserved:
                    cout.write("sim %3i %s not reverting "%(isim+1,cstr) +
                               "to %s because it is reserved\n"%(dstr))
                else:
                    cout.write("sim %3i %s reverting to "%(isim+1,cstr) +
                               "%s because %10.2e >= %10.2e\n"%(dstr,r1,r0))
                    nearbybins[simgidx[isim]].reserved = True
                    nearbybins[propgidx[isim]].reserved = False
                    propgidx[isim] = simgidx[isim]
                    proprcs[isim,:] = simrcs[isim,:]
            else:
                cout.write("sim %3i %s validated "%(isim+1,cstr) +
                           "%10.2e <= %10.2e\n"%(r1,r0))

    nres = 0
    for gidx in nearbybins:
        if nearbybins[gidx].reserved:
            nres += 1
    cout.write("Total reservations: %i\n"%(nres))

    for isim in range(nsim):
        if nearbybins[propgidx[isim]].size == 0:
            donefc[isim] = True;


    cout.write("\n\nSTAGE 3: Adjust force constants, if necessary\n\n");

    ntry = 11
    ws = np.linspace(0,1,ntry)
    
    for itry in range(ntry):
        
        ncantry=0
        for isim in range(nsim):
            if not donefc[isim]:
                ncantry += 1
                
        cout.write("\nIteration %2i ncantry %3i scale %7.3f\n"%(itry+1,ncantry,ws[itry]));
        
        if ncantry == 0:
            break

        for isim in range(nsim):
            if donefc[isim]:
                cout.write("isim %2i fc not adjusted\n"%(isim+1))
            else:
                tryfcs = (1-ws[itry])*simfcs[isim,:] + ws[itry]*maxfc[:]
                sim = FTSMSim.from_density(0,proprcs[isim,:],tryfcs,nobs[isim],den,dampfactor)
                
                maxf = -1.e+10
                us = []
                for dim in range(ndim):
                    dx = abs(sim.eff_mean[dim] - simrcs[isim,dim])
                    u = dx / (0.5*xgrid.dims[dim].width) - 1.
                    maxf = max(maxf,u)
                    us.append(u)
 
                r0 = np.linalg.norm( sim.eff_mean - simrcs[isim,:] )
                r1 = np.linalg.norm( sim.eff_mean - proprcs[isim,:] )
                
                sc = "".join(["%10.4f"%(x) for x in tryfcs])
                su = "".join(["%8.4f"%(x) for x in us])
                cout.write("isim %2i fc %s u: %s r1: %10.2e r0: %10.2e"%(isim+1,sc,su,r1,r0))

                if maxf < 0 or itry == ntry-1:
                    cout.write(" FINAL\n")
                    donefc[isim] = True
                    simfcs[isim,:] = tryfcs
                elif r1 < r0:
                    donefc[isim] = True
                    cout.write(" reverting this iteration; moving away from target\n");
                    if itry > 0:
                        w = ws[itry-1]
                        simfcs[isim,:] = (1-w)*simfcs[isim,:] + w*maxfc[:]
                else:
                    cout.write("\n")
                    
    rcs[:,:] = proprcs[:,:]
    fcs[:,:] = simfcs[:,:]

    cout.write("\nFINAL RCS/FCS\n")
    for isim in range(nsim):
        sr = "".join(["%12.6f"%(x) for x in rcs[isim,:]])
        sf = "".join(["%12.6f"%(x) for x in fcs[isim,:]])
        cout.write("%2i %s%s\n"%(isim+1,sr,sf))

    return isconv,rcs,fcs

    

def CheckFESConv_OLD( rcs, fcs, nobs, minfc, maxfc, pspl, den, dampfactor, conv_layers, conv_samples, fh=None ):
    import numpy as np
    import sys
    import copy
    from collections import defaultdict as ddict
    from . SpatialDim import SpatialDim
    from . VirtualGrid import VirtualGrid
    from . GridUtils import LinearPtsToMeshPts

    def INTWRAP(i,n):
        return (i%n+n)%n

    DEF_FC_SIZE = 25
    
    rcs = np.array(rcs,copy=True)
    fcs = np.array(fcs,copy=True)
    
    didx = conv_layers
    nd = 2*didx+1

    nsim = rcs.shape[0]
    ndim = rcs.shape[1]

    simsizes = [0]*nsim
    
    xdims = []
    for dim in range(ndim):
        orig = den.fes.grid.dims[dim]
        if orig.isper:
            xdims.append( SpatialDim( orig.xmin, orig.xmax,
                                      orig.size, orig.isper ) )
        else:
            w = orig.width
            xdims.append( SpatialDim( orig.xmin - didx*w,
                                      orig.xmax + didx*w,
                                      orig.size + 2*didx,
                                      orig.isper ) )
    xgrid = VirtualGrid(xdims)
    newbidxs = ddict(list)
    newgidxs = ddict(int)
    newsizes = ddict(int)
    for gidx in den.fes.bins:
        xbidx = xgrid.GetBinIdx( den.fes.bins[gidx].center )
        xgidx = xgrid.CptGlbIdxFromBinIdx( xbidx )
        newgidxs[xgidx] = gidx
        newbidxs[xgidx] = xbidx
        newsizes[xgidx] = den.fes.bins[gidx].size

    reserved = []
        
    for isim in range(nsim):
        bidxs = xgrid.GetBinIdx( rcs[isim,:] )
        
        lidxs = []
        for dim in range(ndim):
            dimsize = xgrid.dims[dim].size
            bidx = bidxs[dim]
            if xgrid.dims[dim].isper:
                lidxs.append( [ INTWRAP(k,dimsize)
                                for k in range(bidx-didx, bidx+didx+1) ] )
            else:
                lidxs.append( [ k
                                for k in range(bidx-didx, bidx+didx+1) ] )
        midxs = LinearPtsToMeshPts( lidxs )
        
        MinBinSize=100000000
        MinXBinIdxs = []
        for ibin in range(midxs.shape[0]):
            xmeshidx = midxs[ibin,:]
            gidx = xgrid.CptGlbIdxFromBinIdx( xmeshidx )
            if gidx in reserved:
                continue
            samples = 0
            if gidx in newgidxs:
                samples = newsizes[gidx]
            if samples < MinBinSize:
                MinBinSize = samples
                MinXBinIdxs = [ xmeshidx ]
            elif samples == MinBinSize:
                MinXBinIdxs.append( xmeshidx )

        simsizes[isim] = MinBinSize


        mindist = 1.e+30
        mingidx = 0
        cmin = []
        for i in range(len(MinXBinIdxs)):
            b = MinXBinIdxs[i]
            c = xgrid.GetBinCenter(b)
            d = np.linalg.norm( c-rcs[isim,:] )**2
            if d < mindist:
                cmin = c
                mindist = d
                mingidx = xgrid.CptGlbIdxFromBinIdx( b )
                
        reserved.append( mingidx )

        if len(cmin) == ndim:
            rcs[isim,:] = np.array(cmin)
            w = min(1., simsizes[isim] / DEF_FC_SIZE)
            fcs[isim,:] = (1-w) * minfc + w * fcs[isim,:]
        else:
            raise Exception(f"isim={isim} did not find a nearby grid point")


    fhs = [ sys.stdout ]
    if fh is not None:
        fhs.append(fh)

    for cout in fhs:
        cout.write(f"\nFES sampling check around the new path.\n"+
	           "What is the fewest number of bin samples within "+
	           f"{conv_layers} layers of each control point?\n"+
	           f"If each nearby bin contains at least {conv_samples}"+
	           " samples, then we assume the FES is converged.\n\n");
        cout.write("isim MinSamples Conv?\n")
        isconv = True
        num_not_enough = 0
        for isim in range(nsim):
            cout.write("%4i%11i"%(isim+1,simsizes[isim]))
            if simsizes[isim] < conv_samples:
                isconv = False
                num_not_enough += 1
                cout.write(" F\n")
            else:
                cout.write(" T\n")
        if isconv:
            cout.write("\nSampling appears to be converged\n")
        else:
            cout.write("\nSampling is NOT converged. Areas near the path need more samples.\n"+
                       f"There are {num_not_enough} simulations with insufficient sampling.\n")


            
    cout = sys.stdout
            
    simrcs = np.array(rcs,copy=True)
    simfcs = np.array(fcs,copy=True)
   
    newreserved = copy.deepcopy( reserved )
    needsvalidation = [False]*nsim
    notmoving = [False]*nsim
    isocc = [True]*nsim
    isempty = []
    for isim in range(nsim):
        if simsizes[isim] == 0:
            isempty.append(True)
        else:
            isempty.append(False)

    cout.write("\n\nSTAGE 1: Check if centroids of target bins remains\n"+
               "         in the bin. If not, make a linear guess for\n"+
               "         a proposed umbrella center.\n\n")

    p0 = [ FTSMSim.from_density( 0, rcs[isim,:], simfcs[isim,:],
                                 nobs[isim], den, dampfactor )
           for isim in range(nsim) ]

    #for isim in range(nsim):
    #    print("%4i %s"%(isim+1,"".join(["%12.4f"%(x) for x in simfcs[isim,:]])))
    
    #newreserved = []
    for isim in range(nsim):
        if isempty[isim]:
            sim_bidxs = xgrid.GetBinIdx( rcs[isim,:] )
            sim_gidx = xgrid.CptGlbIdxFromBinIdx( sim_bidxs )
            #newreserved.append(sim_gidx)
            
            sc = "".join(["%10.4f"%(x) for x in rcs[isim]])
            cout.write("sim %3i %s not moving: empty\n"%(isim+1,sc))
        else:
            #sim = FTSMSim.from_density(0,rcs[isim,:],simfcs[isim,:],nobs[isim],den,dampfactor)
            sim = p0[isim]
            cen_bidxs = xgrid.GetBinIdx( sim.eff_mean )
            cen_gidx = xgrid.CptGlbIdxFromBinIdx( cen_bidxs )
            
            sim_bidxs = xgrid.GetBinIdx( sim.rcs )
            sim_gidx = xgrid.CptGlbIdxFromBinIdx( sim_bidxs )


            # print("".join(["%12.5f"%(x) for x in sim.rcs]),
            #       "".join(["%12.5f"%(x) for x in sim.eff_mean]),
            #       "".join(["%8i"%(x) for x in sim_bidxs]),
            #       "".join(["%8i"%(x) for x in cen_bidxs]))
            
            if sim_gidx != cen_gidx:
                
                disp = sim.eff_mean-sim.rcs
                est = sim.rcs - disp
                for dim in range(ndim):
                    est[dim] = min(xgrid.dims[dim].xmax-1.e-10,
                                   max(xgrid.dims[dim].xmin+1.e-10,est[dim]))
                cen_bidxs = xgrid.GetBinIdx( est )
                cen_gidx = xgrid.CptGlbIdxFromBinIdx( cen_bidxs )
                # print("".join(["%12.5f"%(x) for x in est]),
                #       "".join(["%8i"%(x) for x in cen_bidxs]))
                

            bidxs = copy.deepcopy(cen_bidxs)
            gidx = copy.deepcopy(cen_gidx)

            samples = 0
            if gidx in newsizes:
                samples = newsizes[gidx]

            if samples == 0:
                isocc[isim] = False
            else:
                isocc[isim] = True

            estc = xgrid.GetBinCenter(bidxs)
            sep = np.linalg.norm( rcs[isim,:] - estc )**2
            #print(isim,estc,sep)
            if sep < 1.e-10:
                notmoving[isim] = True
                sc = "".join(["%10.4f"%(x) for x in rcs[isim]])
                cout.write("sim %3i %s not moving: centroid remains\n"%(isim+1,sc))
                #newreserved.append( sim_gidx )
            else:
                notmoving[isim] = False
                if cen_gidx not in newreserved:
                    if sim_gidx not in newreserved:
                        sys.stderr.write(f"Failed to set isim {isim} in stage1\n")
                    else:
                        ii = newreserved.index(sim_gidx)
                        newreserved[ii] = cen_gidx
                        needsvalidation[isim] = True
                    #newreserved.append( cen_gidx )
                    simrcs[isim,:] = estc[:]
                    sr = "".join(["%10.4f"%(x) for x in rcs[isim]])
                    sc = "".join(["%10.4f"%(x) for x in simrcs[isim]])
                    cout.write("sim %3i %s moving to: %s\n"%(isim+1,sr,sc))
                else:
                    #newreserved.append( sim_gidx )
                    sr = "".join(["%10.4f"%(x) for x in rcs[isim]])
                    sc = "".join(["%10.4f"%(x) for x in estc])
                    cout.write("sim %3i %s not moved because %s is reserved\n"%(isim+1,sr,sc))
                    
    cout.write("Total reservations: %i\n"%(len(newreserved)))
    newreserved = list(set(newreserved))
    newreserved.sort()
    cout.write("Total unique reservations: %i\n"%(len(newreserved)))

    p1 = [ FTSMSim.from_density( 0, simrcs[isim,:], simfcs[isim,:],
                                 nobs[isim], den, dampfactor )
           for isim in range(nsim) ]
    
    cout.write("\n\nSTAGE 2: If the simulation center has changed, make\n")
    cout.write("         sure its centroid is closer to the target\n")
    cout.write("         bin than the simply placing the center at\n")
    cout.write("         the bin. If not, revert the linear guess.\n\n")

    for isim in range(nsim):
        if not needsvalidation[isim]:
            sr = "".join(["%10.4f"%(x) for x in rcs[isim]])
            cout.write("sim %3i %s untested\n"%(isim+1,sr))
        else:
            r0 = np.linalg.norm( p0[isim].eff_mean - rcs[isim,:] )
            r1 = np.linalg.norm( p1[isim].eff_mean - rcs[isim,:] )
            if r1 > r0:
                sim_bidxs = xgrid.GetBinIdx( p0[isim].rcs )
                sim_gidx = xgrid.CptGlbIdxFromBinIdx( sim_bidxs )
                cen_bidxs = xgrid.GetBinIdx( simrcs[isim,:] )
                cen_gidx = xgrid.CptGlbIdxFromBinIdx( cen_bidxs )
                if sim_gidx not in newreserved:
                    sc = "".join(["%10.4f"%(x) for x in simrcs[isim]])
                    sr = "".join(["%10.4f"%(x) for x in rcs[isim]])
                    cout.write("sim %3i %s reverting to %s because %10.2e >= %10.2e\n"%(isim+1,sc,sr,r1,r0))
                    simrcs[isim,:] = rcs[isim,:]
                    dp = newreserved.index(cen_gidx)
                    newreserved[dp]=sim_gidx
                else:
                    sc = "".join(["%10.4f"%(x) for x in simrcs[isim]])
                    sr = "".join(["%10.4f"%(x) for x in rcs[isim]])
                    cout.write("sim %3i %s not reverting to %s because it is reserved\n"%(isim+1,sc,sr)) 
            else:
                sc = "".join(["%10.4f"%(x) for x in simrcs[isim]])
                cout.write("sim %3i %s validated %10.2e <= %10.2e\n"%(isim+1,sc,r1,r0))

    cout.write("Total reservations: %i\n"%(len(newreserved)))
    newreserved = list(set(newreserved))
    newreserved.sort()
    cout.write("Total unique reservations: %i\n"%(len(newreserved)))


    canadjust = []
    for isim in range(nsim):
        if isempty[isim] or (not isocc[isim]) or notmoving[isim]:
            canadjust.append(False)
        else:
            canadjust.append(True)

    ntry = 11
    ws = np.linspace(0,1,ntry)

    cout.write("\n\nSTAGE 3: Adjust force constants, if necessary\n\n");

    for itry in range(ntry):
        ncantry=0
        for isim in range(nsim):
            if canadjust[isim]:
                ncantry += 1
        cout.write("\nIteration %2i ncantry %3i scale %7.3f\n"%(itry,ncantry,ws[itry]));
        if ncantry == 0:
            break

        for isim in range(nsim):
            if not canadjust[isim]:
                cout.write("isim %2i fc not adjusted\n"%(isim+1))
            else:
                tryfcs = (1-ws[itry])*simfcs[isim,:] + ws[itry]*maxfc[:]
                sim = FTSMSim.from_density(0,simrcs[isim,:],tryfcs,nobs[isim],den,dampfactor)
                
                maxf = -1.e+10
                us = []
                for dim in range(ndim):
                    dx = abs(sim.eff_mean[dim] - rcs[isim,dim])
                    u = dx / (0.5*xgrid.dims[dim].width) - 1.
                    maxf = max(maxf,u)
                    us.append(u)
 
                r0 = np.linalg.norm( sim.eff_mean - rcs[isim,:] )
                r1 = np.linalg.norm( sim.eff_mean - simrcs[isim,:] )
                
                sc = "".join(["%10.4f"%(x) for x in tryfcs])
                su = "".join(["%8.4f"%(x) for x in us])
                cout.write("isim %2i fc %s u: %s r1: %12.3e r0: %12.3e"%(isim+1,sc,su,r1,r0))

                if maxf < 0 or itry == ntry-1:
                    cout.write(" FINAL\n")
                    canadjust[isim] = False
                    simfcs[isim,:] = tryfcs
                elif r1 < r0:
                    canadjust[isim] = False
                    cout.write(" setting canadjust=false because we moving away from the target\n");
                    if itry > 0:
                        w = ws[itry-1]
                        simfcs[isim,:] = (1-w)*simfcs[isim,:] + w*maxfc[:]
                else:
                    cout.write("\n")
                    
    rcs[:,:] = simrcs[:,:]
    fcs[:,:] = simfcs[:,:]

    cout.write("\nFINAL RCS/FCS\n")
    for isim in range(nsim):
        sr = "".join(["%12.6f"%(x) for x in rcs[isim,:]])
        sf = "".join(["%12.6f"%(x) for x in fcs[isim,:]])
        cout.write("%2i %s%s\n"%(isim+1,sr,sf))

    
    return isconv,rcs,fcs




class FTSMSim(object):
    """Class that stores information about a simulation

    Attributes
    ----------
    splt : float
        The progress value of the window along the path

    rcs : numpy.ndarray, shape=(Ndim,)
        The location of the biasing potential

    fcs : numpy.ndarray, shape=(Ndim,)
        The biasing potential force constants (twice the force constants)

    obs_n : float
        The number of observed samples

    obs_mean : numpy.ndarray, shape=(Ndim,)
        The observed centroid location

    obs_std : numpy.ndarray, shape=(Ndim,)
        The observed standard deviations of the reaction coordinates

    eff_n : float
        The effective number of samples (this is not currently used
        anywhere and it is not currently calculated correctly)

    eff_mean :  numpy.ndarray, shape=(Ndim,)
        The centroid calculated from the effective density
        By default, this is the same as obs_mean

    obs_std : numpy.ndarray, shape=(Ndim,)
        The standard deviations calculated from the effective density
        By default, this is the same as obs_std

    Methods
    -------
    """
    def __init__(self,splt,rcs,fcs,nobs,obsmean,obsstd):
        """Constructed from provided values, except eff_mean and eff_std
           are copies of obs_mean and obs_std"""
        import numpy as np
        self.splt = splt
        self.rcs = np.array(rcs,copy=True)
        self.fcs = np.array(fcs,copy=True)
        self.obs_n = nobs
        self.obs_mean = np.array(obsmean,copy=True)
        self.obs_std  = np.array(obsstd,copy=True)
        self.eff_n = nobs
        self.eff_mean = np.array(obsmean,copy=True)
        self.eff_std  = np.array(obsstd,copy=True)

    @classmethod
    def from_density(cls,splt,rcs,fcs,nobs,denest,dampfactor):
        """Constructs an object by calculating the centroids from the
        density estimator

        Parameters
        ----------
        splt : float
            The progress value of the window along the path

        rcs : numpy.ndarray, shape=(Ndim,)
            The location of the biasing potential

        fcs : numpy.ndarray, shape=(Ndim,)
            The biasing potential force constants (twice the force constants)

        obs_n : float
            The number of observed samples

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped
        """

        obs_mean, obs_std, eff_n, eff_mean, eff_std = \
            CalcUmbrellaSimDistrib(rcs,fcs,nobs,denest,dampfactor)
        self = cls(splt,rcs,fcs,nobs,obs_mean,obs_std)
        self.eff_n = eff_n
        self.eff_mean = eff_mean
        self.eff_std = eff_std
        return self

    
    def UpdateDensity(self,denest,dampfactor):
        """Updates the centroid means and standard deviations from the
        provided density calculator

        Parameters
        ----------
        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        Returns
        -------
        None
        """

        if denest is not None:
            self.obs_mean, self.obs_std, self.eff_n, \
                self.eff_mean, self.eff_std = \
                    CalcUmbrellaSimDistrib(self.rcs,self.fcs,self.obs_n,
                                           denest,dampfactor)

    

class FTSMString(object):
    """A class that holds multiple FTSMSim objects representing a path.
    The spline of the path is the "input curve". To get the predicted
    "output curve", one needs to call the GetOutputSpline method.

    Attributes
    ----------
    splpts : numpy.ndarray, shape=(Nsim,Ndim)
        The control points defining the spline. These point are not
        necessarily uniformly discretized.

    splts : numpy.ndarray, shape=(Nsim,)
        The progress variables corresponding to the control points.

    pspl : ndfes.PathUtils.PCurve
        The parametric curve of reaction coordinates. This is the 
        input curve, not the output curve.

    sims : list of ndfes.FTSM.FTSMSim
        The simulations. These do not have to be performed at the
        control points, but the umbrella centers and splt attributes
        must coincide with the parameter spline. The constructor
        will check for consistency and throws an error if necessary.
    
    avgfc : numpy.ndarray, shape=(Ndim,)
        The simulation-average force constants

    Methods
    -------
    """

    def __init__(self,splpts,splts,sims,linear=False):
        """Constructs from the spline control points, progress values, and
        simulations.

        Parameters
        ----------
        splpts : numpy.ndarray, shape=(Nsim,Ndim)
            The spline control points

        splts : numpy.ndarray, shape(Nsim,)
            The spline progress variables

        sims : list of ndfes.FTSM.FTSMSim
            The simulations


        If splpts is None, then it assumes that the simulations
        define the control points and progress variables.
        If splpts is not None, but the progress variables are 
        None, then it calculates the the progress variables
        using ndfes.PathUtils.PCurve with fixt=False; that is,
        it iteratively solves for a parametric spline to reach
        self consistency between the progress variables and
        path arc lengths.
        """
        import numpy as np
        import sys
        from . PathUtils import PCurve

        self.splpts = splpts
        self.splts = splts
        self.sims = sims
        #pts = np.array([ sim.rcs for sim in self.sims ])
        
        if splpts is not None:
            if splts is not None:
                self.pspl = PCurve(self.splpts,t=self.splts,linear=linear)
            else:
                self.pspl = PCurve(self.splpts,fixt=False,linear=linear)
                self.splts = self.pspl.t
        else:
            self.splpts = np.array([ sim.rcs for sim in self.sims ])
            ts = [ sim.splt for sim in self.sims ]
            if len(set(ts)) == len(ts):
                self.pspl = PCurve(self.splpts,t=ts,linear=linear)
                self.splts = np.array(ts)
            else:
                self.pspl = PCurve(self.splpts,fixt=False,linear=linear)
                self.splts = self.pspl.t
            for i in range(len(self.sims)):
                self.sims[i].splt = self.splts[i]
                

        fcs =  np.array( [sim.fcs for sim in self.sims] )
        self.avgfc = np.mean(fcs,axis=0)


        for sim in self.sims:
            rc1 = sim.rcs
            rc2 = self.pspl.GetValue( sim.splt )
            if np.linalg.norm(rc1-rc2) > 1.e-3:
                rc1s = " ".join(["%.4f"%(x) for x in rc1])
                rc2s = " ".join(["%.4f"%(x) for x in rc2])
                raise Exception("Error: FTSMString sim @ %s"%(rc1s)
                                +" with t=%.3f"%(sim.splt)
                                +" does not match spline: "
                                +"%s\n"%(rc2s))
    

    def __getitem__(self,i):
        """Returns the indexed simulation"""
        return self.sims[i]

    def __len__(self):
        """Returns the number of simulations"""
        return len(self.sims)


    def MakeLinear(self):
        import numpy as np
        from . PathUtils import PCurve
        self.pspl = PCurve(self.splpts,fixt=False,linear=True)
        self.splts = np.array(self.pspl.t,copy=True)
        for i in range(len(self.sims)):
            self.sims[i].splt = self.splts[i]
    
    @classmethod
    def from_density(cls,splpts,splts,fcs,nobs,denest,dampfactor):
        """Constructs a path from a series of synthetic simulations,
        whose centroids are estimated from the free energy surface.

        Parameters
        ----------
        splpts : numpy.ndarray, shape=(Nsim,Ndim)
            The control points defining the spline. These point are not
            necessarily uniformly discretized. These are not where the
            synthetic simulations are performed; the synthetic simulations
            are performed on a uniformly discretized path.

        splts : numpy.ndarray, shape=(Nsim,)
            The progress variables corresponding to the control points.
            This can be None, in which case, the progress variables are
            calculated from ndfes.PathUtils.PCurve with fixt=False.
        
        fcs : numpy.ndarray, shape=(Ndim,) or (Nsim,Ndim)
            The force constants in each dimension. If separate force
            constants are provided for each simulation, then an average
            is used.

        nobs : list of float
            The expected number of samples drawn from each simulation.
            The length of this list is what controls the number of
            simulations.
        
        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        """
        import numpy as np
        from . PathUtils import PCurve
        
        nsim = len(nobs)
        if len(fcs.shape) == 1:
            avgfc = fcs
            fcs = np.array( [ avgfc ]*nsim )
        elif len(fcs.shape) == 2:
            avgfc = np.mean( fcs, axis=0 )
            fcs = np.array( [ avgfc ]*nsim )

        if splts is not None:
            pspl = PCurve(splpts,t=splts)
        else:
            pspl = PCurve(splpts,fixt=False)
            splts = pspl.t
            
        uts = np.linspace(0,1,nsim)
        rcs = np.array([ pspl.GetValue(t) for t in uts ])
        sims = [ FTSMSim.from_density(t,rc,fc,n,denest,dampfactor)
                 for t,rc,fc,n in zip(uts,rcs,fcs,nobs) ]
        return cls(splpts,splts,sims)

    @classmethod
    def from_simdata(cls,splpts,splts,ts,rcs,fcs,nobs,obsmean,obsstd,neff,effmean,effstd):
        import numpy as np
        #splpts = np.array(splpts)
        #splts = np.array(splts)
        #ts = np.array(ts)
        #rcs = np.array(rcs)
        #fcs = np.array(fcs)
        #nobs = np.array(nobs)
        #obsmean = np.array(obsmean)
        #obsstd = np.array(obsstd)
        #neff = np.array(neff)
        #effmean = np.array(effmean)
        #effstd = np.array(effstd)
        sims = []
        for i in range(len(ts)):
            s = FTSMSim(ts[i],np.array(rcs[i]),np.array(fcs[i]),
                        nobs[i],np.array(obsmean[i]),np.array(obsstd[i]))
            s.eff_n = neff[i]
            s.eff_mean = np.array( effmean[i] )
            s.eff_std = np.array( effstd[i] )
            sims.append(s)
        return cls(np.array(splpts),np.array(splts),sims)

    def GetSimData(self):
        splpts = self.splpts.tolist()
        splts = self.splts.tolist()
        ts=[ s.splt for s in self.sims ]
        rcs=[ s.rcs.tolist() for s in self.sims ]
        fcs=[ s.fcs.tolist() for s in self.sims ]
        nobs=[ s.obs_n for s in self.sims ]
        obsmean=[ s.obs_mean.tolist() for s in self.sims ]
        obsstd=[ s.obs_std.tolist() for s in self.sims ]
        neff=[ s.eff_n for s in self.sims ]
        effmean=[ s.eff_mean.tolist() for s in self.sims ]
        effstd=[ s.eff_std.tolist() for s in self.sims ]
        return splpts,splts,ts,rcs,fcs,nobs,obsmean,obsstd,neff,effmean,effstd
    
    def GetCenters(self):
        """The umbrella potential locations

        Returns
        -------
        rcs : numpy.ndarray, shape=(Nsim,Ndim)
            The centers
        """
        import numpy as np
        return np.array( [ sim.rcs for sim in self.sims ] )

    def GetMeans(self):
        """The effective centroid positions

        Returns
        -------
        means : numpy.ndarray, shape=(Nsim,Ndim)
            The centroids
        """
        import numpy as np
        return np.array( [ sim.eff_mean for sim in self.sims ] )

    def GetStdDevs(self):
        """The effective density standard deviations

        Returns
        -------
        means : numpy.ndarray, shape=(Nsim,Ndim)
            The standard deviations
        """
        import numpy as np
        return np.array( [ sim.eff_std for sim in self.sims ] )

    
    def UpdateDensity(self,denest,dampfactor):
        """Updates the centroid positions using the specified
        density estimator

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        Returns
        -------
        None
        """
        for sim in self.sims:
            sim.UpdateDensity(denest,dampfactor)

            
    def GetOutputSpline(self,fix0,fix1,smooth_fact,smooth_nmin,smooth_nmax,linear=False):
        """Returns a parametric spline passing through the centroids.

        Parameters
        ----------
        fix0 : bool
            If True, then do not update the position of the first window

        fix1 : bool
            If True, then do not update the position of the last window

        smooth_fact : float
            A number between 0 and 1. It controls the amount of smoothing
            by taking a linear combination of the smoothed and unsmoothed
            paths. One should probably always set this to 1.0

        smooth_nmin : int
            If this is 0, then no smoothing of the path is performed.
            If it is not zero, then it must be an odd integer.
            It is the width of a windowed average.  Larger window widths
            will increase smoothing, but it will also cut corners.
            I recommend setting this to 3. If you don't have sharp
            corners in your path, you could set it to 5.

        smooth_nmax : int
            This must be an odd integer >= 3.  One smoothing is applied
            with smooth_nmin, a series of additional corrects are performed
            by windowed averaging of the reference and smoothed paths
            to try and reduce the amount of corner cutting.  I recommend
            setting this to 11. Larger values will have only a minor
            impact on the final result.

        linear : bool, default=False
            Return the output as a piecewise linear curve

        Returns
        -------
        spl : ndfes.PathUtils.PCurve
            Parametric spline of the new path. The points are spl.x and
            progress variables are spl.t
        """
        import numpy as np
        from . SmoothCurve import SmoothCurve_IterReflectedAvg
        from . PathUtils import PCurve
        
        pts = np.array([ sim.eff_mean for sim in self.sims ])
        if fix0:
            pts[0,:] = self.pspl.x[0,:]
        if fix1:
            pts[-1,:] = self.pspl.x[-1,:]
        if smooth_fact > 0 and smooth_nmin >= 3 and smooth_nmax >= smooth_nmin:
            pts = SmoothCurve_IterReflectedAvg\
                (pts,smooth_nmin,smooth_nmax,smooth_fact)                

        return PCurve(pts,fixt=False,linear=linear)

    
    def Next(self,
             fix0, fix1,
             smooth_fact,smooth_nmin,smooth_nmax,
             denest,dampfactor):
        """Create a new FTSMString path passing through the centroids.

        Parameters
        ----------
        fix0 : bool
            If True, then do not update the position of the first window

        fix1 : bool
            If True, then do not update the position of the last window

        smooth_fact : float
            A number between 0 and 1. It controls the amount of smoothing
            by taking a linear combination of the smoothed and unsmoothed
            paths. One should probably always set this to 1.0

        smooth_nmin : int
            If this is 0, then no smoothing of the path is performed.
            If it is not zero, then it must be an odd integer.
            It is the width of a windowed average.  Larger window widths
            will increase smoothing, but it will also cut corners.
            I recommend setting this to 3. If you don't have sharp
            corners in your path, you could set it to 5.

        smooth_nmax : int
            This must be an odd integer >= 3.  One smoothing is applied
            with smooth_nmin, a series of additional corrects are performed
            by windowed averaging of the reference and smoothed paths
            to try and reduce the amount of corner cutting.  I recommend
            setting this to 11. Larger values will have only a minor
            impact on the final result.

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        Returns
        -------
        next : ndfes.FTSM.FTSMString
            The updated estimate of the path
        """
        import numpy as np
        from . SmoothCurve import SmoothCurve_IterReflectedAvg
        from . PathUtils import PCurve
        
        if denest is None:
            raise Exception("Cannot iterate a new string without a "+
                            "density estimator")
        
        pspl = self.GetOutputSpline(fix0,fix1,smooth_fact,
                                    smooth_nmin,smooth_nmax)
        #ts = np.linspace(0,1,pts.shape[0])
        #rcs = np.array( [ pspl.GetValue(t) for t in ts ] )
        nobs = np.array( [ sim.obs_n for sim in self.sims ] )

        return FTSMString.from_density( pspl.x, pspl.t, self.avgfc, nobs,
                                        denest, dampfactor )
            

    def GetUniformPathDeltas(self):
        """The vectors parallel to the path, whose lengths are the distance
        between adjacent, uniformly discretized points
        
        Returns
        -------
        dw : numpy.ndarray, shape=(Ndim,Ndim)
            The (non-unit) tangent vectors
        """
        return GetUniformPathDeltasFromPCurve( self.pspl )
        
        # import numpy as np
        # nsim = len(self.sims)
        # ndim = self.sims[0].rcs.shape[0]
        # ts = np.linspace(0,1,nsim)

        # upts = np.array( (nsim,ndim) )
        # for i in range(nsim):
        #     upts[i,:] = self.pspl.GetValue(ts[i])
        # return GetUniformPathDeltas(upts)
        
        # dws = []
        # for i in range(len(self.sims)):
        #     if i == 0:
        #         dw = self.pspl.GetValue(ts[i+1])-self.pspl.GetValue(ts[i])
        #     elif i == nsim-1:
        #         dw = self.pspl.GetValue(ts[i])-self.pspl.GetValue(ts[i-1])
        #     else:
        #         dw = 0.5*( self.pspl.GetValue(ts[i+1]) \
        #                    - self.pspl.GetValue(ts[i-1]) )
        #     dws.append(dw)
        # return np.array(dws)

    
    def GetPathDeltas(self):
        """The vectors parallel to the path, whose lengths are the distance
        between adjacent simulations
        
        Returns
        -------
        dw : numpy.ndarray, shape=(Ndim,Ndim)
            The (non-unit) tangent vectors
        """
        import numpy as np
        nsim = len(self.sims)
        dws = []
        for i in range(len(self.sims)):
            if i == 0:
                dw = self.sims[i+1].rcs-self.sims[i].rcs
            elif i == nsim-1:
                dw = self.sims[i].rcs-self.sims[i-1].rcs
            else:
                dw = 0.5*( self.sims[i+1].rcs-self.sims[i-1].rcs )
            dws.append(dw)
        return np.array(dws)

    
    def GetPathProjection(self,refpath):
        """The cosine angles of the centroid displacement relative to
        the tangents of a reference path

        Parameters
        ----------
        refpath : ndfes.FTSM.FTSMString
            The reference path (usually self)

        Returns
        -------
        projs: numpy.ndarray, shape=(Nsim,)
            The angle cosines. A value of +1 means the centroid
            moves parallel to the path in the +t direction. A value of
            -1 means the centroid moves in the -t direction. A value
            of 0 means the centroid is moving perpendicular to the path.
        """
        import numpy as np
        
        dws = refpath.GetUniformPathDeltas()
        nsim = dws.shape[0]
        projs = np.zeros( (nsim,) )
        for i in range(nsim):
            dw = dws[i,:]
            lw = np.linalg.norm(dw)
            uw = dw/lw

            dx = self.sims[i].eff_mean - refpath.sims[i].rcs
            lx = np.linalg.norm(dx)
            proj = 0
            if lx > 0.001:
                ux = dx/lx
                proj = np.dot(uw,ux)
            projs[i] = proj
        return projs


    
    def EstimateForceConstants(self,limits,denest,dampfactor,
                               fix0,fix1,
                               scale_fc,smooth_fc,smooth_fact,
                               smooth_nmin,smooth_nmax):
        """Predicts an ideal set of force constants, assuming the
        simulations uniformly discretize the path.  A force constant
        is "ideal" if the centroid displacement along the path matches
        a target displacement, measured as a percentage. The percentage
        is the distance between adjacent windows; e.g., a value of 0.5
        means the centroid moves halfway between two windows.

        Parameters
        ----------
        limits : ndfes.FTSM.FTSMSimLimits
            The tdisp, maxfcs, and minfcs attributes control the target
            displacement and maximum and minimum allowable force constants.

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped
        
        scale_fc : bool
            If True, then scale the force constant to the input value
            when the predicted centroid displacement is perpendicular
            to the predicted path

        smooth_fc : bool
            If True, apply smoothing to the force constants

        smooth_fact : float
            A number between 0 and 1. It controls the amount of smoothing
            by taking a linear combination of the smoothed and unsmoothed
            paths. One should probably always set this to 1.0

        smooth_nmin : int
            If this is 0, then no smoothing of the path is performed.
            If it is not zero, then it must be an odd integer.
            It is the width of a windowed average.  Larger window widths
            will increase smoothing, but it will also cut corners.
            I recommend setting this to 3. If you don't have sharp
            corners in your path, you could set it to 5.

        smooth_nmax : int
            This must be an odd integer >= 3.  One smoothing is applied
            with smooth_nmin, a series of additional corrects are performed
            by windowed averaging of the reference and smoothed paths
            to try and reduce the amount of corner cutting.  I recommend
            setting this to 11. Larger values will have only a minor
            impact on the final result.


        Returns
        -------
        fcs : numpy.ndarray, shape=(Ndim,Ndim)
            The predicted force constants
        """
        import numpy as np
        from . SmoothCurve import SmoothCurve_IterReflectedAvg

        if denest is None or limits is None or dampfactor is None:
            fcs = np.array([ self.avgfc ]*len(self.sims))
        else:
            tdisp = limits.tdisp
            maxfcs = limits.maxfcs
            minfcs = limits.minfcs

            ospl = self.GetOutputSpline(fix0,fix1,smooth_fact,
                                        smooth_nmin,smooth_nmax)
            
            dws = GetUniformPathDeltasFromPCurve(ospl)
            nsim = dws.shape[0]
            ndim = dws.shape[1]
            ts = np.linspace(0,1,nsim)
            fcs = []
            for i in range(nsim):
                print("\nEstimate FC for image %i"%(i+1))
                dw = dws[i,:]
                nobs = self.sims[i].obs_n
                rc = ospl.GetValue(ts[i])
                fc = np.array(self.avgfc,copy=True)
                fc = FindIdealForceConstant(limits,dw,rc,fc,nobs,
                                            denest,dampfactor,scale_fc)
                print("Final FC for image %i : %s\n"%\
                      (i+1," ".join(["%8.2f"%(x) for x in fc])))
                fcs.append(fc)
            fcs = np.array( fcs )
            print("Replacing end-point FCs with nearest neighbor values")
            fcs[0,:] = fcs[1,:]
            fcs[-1,:] = fcs[-2,:]
            print("\nPredicted force constants from uniform simulations")
            for i in range(nsim):
                print("%3i %s"%(i+1," ".join(["%8.2f"%(x) for x in fcs[i,:]])))
            print("")
            
            if smooth_fc:
                fcs = SmoothCurve_IterReflectedAvg(fcs,smooth_nmin,smooth_nmax,smooth_fact)
                for i in range(nsim):
                    for d in range(ndim):
                        fcs[i,d] = min(maxfcs[d],max(minfcs[d],fcs[i,d]))
            
                print("\nPredicted force constants from uniform simulations after smoothing")
                for i in range(nsim):
                    print("%3i %s"%(i+1," ".join(["%8.2f"%(x) for x in fcs[i,:]])))
                print("")
            
        return fcs

    
    def PredictUniformWindows(self,
                              varyfc,
                              fix0, fix1, scale_fc, smooth_fc,
                              smooth_fact,smooth_nmin,smooth_nmax,
                              limits,denest,dampfactor):
        """Predict the placement of the windows and force constants
        for a new set of real simulations such that the umbrella centers
        uniformly discretize the path.

        Parameters
        ----------
        varyfc : bool
            If True, predict an ideal set of force constants

        fix0 : bool
            If True, then do not update the position of the first window

        fix1 : bool
            If True, then do not update the position of the last window

        scale_fc : bool
            If True, then scale the force constant to the input value
            when the predicted centroid displacement is perpendicular
            to the predicted path

        smooth_fc : bool
            If True, apply smoothing to the force constants

        smooth_fact : float
            A number between 0 and 1. It controls the amount of smoothing
            by taking a linear combination of the smoothed and unsmoothed
            paths. One should probably always set this to 1.0

        smooth_nmin : int
            If this is 0, then no smoothing of the path is performed.
            If it is not zero, then it must be an odd integer.
            It is the width of a windowed average.  Larger window widths
            will increase smoothing, but it will also cut corners.
            I recommend setting this to 3. If you don't have sharp
            corners in your path, you could set it to 5.

        smooth_nmax : int
            This must be an odd integer >= 3.  One smoothing is applied
            with smooth_nmin, a series of additional corrects are performed
            by windowed averaging of the reference and smoothed paths
            to try and reduce the amount of corner cutting.  I recommend
            setting this to 11. Larger values will have only a minor
            impact on the final result.

        limits : ndfes.FTSM.FTSMSimLimits
            The tdisp, maxfcs, and minfcs attributes control the target
            displacement and maximum and minimum allowable force constants.

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        Returns
        -------
        rcs : numpy.ndarray, shape=(Nsim,Ndim)
            The predicted window locations

        fcs :  numpy.ndarray, shape=(Nsim,Ndim)
            The predicted window force constants
        """
        import numpy as np
        from . PathUtils import PCurve
        from . SmoothCurve import SmoothCurve_IterReflectedAvg

        pspl = self.GetOutputSpline(fix0,fix1,smooth_fact,
                                    smooth_nmin,smooth_nmax)
        nsim = len(self.sims)
        ts = np.linspace(0,1,nsim)
        rcs = np.array( [ pspl.GetValue(t) for t in ts ] )
        fcs = np.array( [ self.avgfc ]*nsim )
        if varyfc:
            if denest is None:
                raise Exception("Cannot use varyfc without a density estimator")
            fcs = self.EstimateForceConstants(limits,denest,dampfactor,
                                              fix0,fix1,
                                              scale_fc, smooth_fc, smooth_fact,
                                              smooth_nmin,smooth_nmax )
        return rcs,fcs


    
    def PredictUniformCentroids(self,
                                varyfc,
                                fix0, fix1,
                                scale_fc, smooth_fc,
                                smooth_fact,smooth_nmin,smooth_nmax,
                                limits,denest,dampfactor):
        """Predict the placement of the windows and force constants
        for a new set of real simulations such that predicted centroids
        uniformly discretize the path.

        Parameters
        ----------
        varyfc : bool
            If True, predict an ideal set of force constants

        fix0 : bool
            If True, then do not update the position of the first window

        fix1 : bool
            If True, then do not update the position of the last window

        scale_fc : bool
            If True, then scale the force constant to the input value
            when the predicted centroid displacement is perpendicular
            to the predicted path

        smooth_fc : bool
            If True, apply smoothing to the force constants

        smooth_fact : float
            A number between 0 and 1. It controls the amount of smoothing
            by taking a linear combination of the smoothed and unsmoothed
            paths. One should probably always set this to 1.0

        smooth_nmin : int
            If this is 0, then no smoothing of the path is performed.
            If it is not zero, then it must be an odd integer.
            It is the width of a windowed average.  Larger window widths
            will increase smoothing, but it will also cut corners.
            I recommend setting this to 3. If you don't have sharp
            corners in your path, you could set it to 5.

        smooth_nmax : int
            This must be an odd integer >= 3.  One smoothing is applied
            with smooth_nmin, a series of additional corrects are performed
            by windowed averaging of the reference and smoothed paths
            to try and reduce the amount of corner cutting.  I recommend
            setting this to 11. Larger values will have only a minor
            impact on the final result.

        limits : ndfes.FTSM.FTSMSimLimits
            The tdisp, maxfcs, and minfcs attributes control the target
            displacement and maximum and minimum allowable force constants.

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        Returns
        -------
        rcs : numpy.ndarray, shape=(Nsim,Ndim)
            The predicted window locations

        fcs :  numpy.ndarray, shape=(Nsim,Ndim)
            The predicted window force constants
        """
        import numpy as np
        from scipy.interpolate import interp1d
        from . PathUtils import PCurve
        from . SmoothCurve import SmoothCurve_IterReflectedAvg
        
        if denest is None:
            raise Exception("Cannot use PredictUniformCentroids without a density estimator")

        nsim = len(self.sims)
        ndim = self.avgfc.shape[0]
        nobs = np.array( [ sim.obs_n for sim in self.sims ] )

        ospl = self.GetOutputSpline(fix0, fix1, smooth_fact,
                                    smooth_nmin,smooth_nmax)
        
        rcs,fcs = self.PredictUniformWindows\
            ( varyfc, fix0, fix1, scale_fc, smooth_fc, smooth_fact,
              smooth_nmin, smooth_nmax, limits,
              denest, dampfactor)
        
        # uniform t values
        uts = np.linspace(0,1,nsim)
        
        pred = [ FTSMSim.from_density( t, rc, fc, n,
                                       denest, dampfactor )
                 for t,rc,fc,n in zip(uts,rcs,fcs,nobs) ]
        
        cpts = np.array( [ sim.eff_mean for sim in pred ] )
        #for i in range(cpts.shape[0]):
        #    print(i,cpts[i,:],rcs[i,:],fcs[i,:])
        # spline of centroids, fixt=False will calculate the
        # t-value of each centroid
        cspl = PCurve(cpts,fixt=False)


        # x-axis: centroid t-values
        # y-axis: uniform t-values
        ct2ut = interp1d(cspl.t,uts,kind='linear')

        # uniformly discretize the centroid t-values
        ucts = ct2ut( uts[1:-1] )
        ucts = np.array( [ 0 ] + ucts.tolist() + [ 1 ] )
        ucts.sort()
        #print(ucts)

        #
        # which one of these is correct?
        #
        fcspl = [ interp1d(uts,fcs[:,i],kind='linear')
                  for i in range(ndim) ]
        #
        #fcspl = [ interp1d(ospl.t,fcs[:,i],kind='linear')
        #          for i in range(ndim) ]

        orcs = []
        ofcs = []
        for i in range(nsim):
            t = ucts[i]
            rc = ospl.GetValue(t)
            fc = [ spl(t) for spl in fcspl ]
            orcs.append(rc)
            ofcs.append(fc)
        orcs = np.array(orcs)
        ofcs = np.array(ofcs)
        ofcs[0,:] = ofcs[1,:]
        ofcs[-1,:] = ofcs[-2,:]


        #===========================================================
        fpred = [ FTSMSim.from_density( t, rc, fc, n,
                                        denest, dampfactor )
                  for t,rc,fc,n in zip(uts,orcs,ofcs,nobs) ]
        
        fpts = np.array( [ sim.eff_mean for sim in fpred ] )
        fspl = PCurve(fpts,fixt=False)

        print("\nPredicted centroid distributions.")
        print("Col 1: uniform discretization")
        print("Col 2: predicted centroids from uniform window centers")
        print("Col 3: predicted centroids from uniform centroids")
        
        for i in range(nsim):
            print("%9.5f %9.5f %9.5f"%(uts[i],cspl.t[i],fspl.t[i]))
        print("")
        
        print("\nPredicted force constants from uniform centroids")
        for i in range(nsim):
            print("%3i %s"%(i+1," ".join(["%8.2f"%(x) for x in ofcs[i,:]])))
        print("")
        #===========================================================
        
        return orcs,ofcs



    
class FTSMSimLimits(object):
    """A class that stores various algorithmic values and limits

    Attributes
    ----------
    dimisangle : list of bool, len=Ndim
        The length of the list is the number of dimensions.
        Each element is a bool indicating if the dimension is an
        angle (True) or a distance (False)

    ndim : int
        The number of dimensions

    maxfcs : numpy.ndarray, shape=(Ndim,)
        The maximum allowable force constant in each dimension

    minfcs : numpy.ndarray, shape=(Ndim,)
        The minimum allowable force constant in each dimension

    tdisp : float
        The target percent displacement of the centroids used
        to estimate the ideal force constants

    Methods
    -------
    """
    def __init__(self,dimisangle):
        """
        Parameters
        ----------
        dimisangle : list of bool, len=Ndim
            The length of the list is the number of dimensions.
            Each element is a bool indicating if the dimension is an
            angle (True) or a distance (False)
        """
        import copy
        import numpy as np
        self.dimisangle = copy.deepcopy(dimisangle)
        self.ndim = len(self.dimisangle)
        self.maxfcs=np.array([0]*self.ndim)
        self.minfcs=np.array([0]*self.ndim)
        self.tdisp=0.75
        self.SetLimits( 50, 300, 0.4, 2.0 )
        
    def SetLimits(self, dismin, dismax, angmin, angmax):
        """Update the force constant limits

        Parameters
        ----------
        dismin : float
            The minimum allowable force constant for distance restraints.
            Units: kcal/mol/A**2

        dismax : float
            The maximum allowable force constant for distance restraints
            Units: kcal/mol/A**2

        angmin : float
            The minimum allowable force constant for angle restraints.
            Units: kcal/mol/deg**2

        angmax : float
            The maximum allowable force constant for angle restraints.
            Units: kcal/mol/deg**2

        Returns
        -------
        None
        """

        for d in range(self.ndim):
            if self.dimisangle[d]:
                self.maxfcs[d] = angmax
                self.minfcs[d] = angmin
            else:
                self.maxfcs[d] = dismax
                self.minfcs[d] = dismin



                
class FTSMOpt(object):
    """A class that holds a series of paths representing an sequence of
    optimization steps

    Attributes
    ----------
    paths : list of ndfes.FTSM.FTSMString
        The paths of each iteration

    Methods
    -------
    """
    def __init__(self,paths):
        """If this is not a restart, set paths=None"""
        import copy
        self.paths = []
        if paths is not None:
            self.paths = copy.deepcopy(paths)

    def MakeLinear(self):
        for i in range(len(self.paths)):
            self.paths[i].MakeLinear()
            
            
    def Optimize(self,
                 maxit,ptol,
                 fix0,fix1,
                 smooth_fact,smooth_nmin,smooth_nmax,
                 denest,dampfactor,fh=None):
        """
        Performs synthetic simulations to optimize a path.
        If a density estimator is not provided, then no optimization
        is performed.  The optimized parametric curve is the GetOutputPath of
        the last string (see the GetOutputPath method in FTSMString).

        Parameters
        ----------
        maxit : int
            The maximum number of iterations. A value of 0 does not perform
            any iterations.
        
        fix0 : bool
            If True, do not change the position of the first window

        fix1 : bool
            If True, do not change the position of the last window

        smooth_fact : float
            A number between 0 and 1. It controls the amount of smoothing
            by taking a linear combination of the smoothed and unsmoothed
            paths. One should probably always set this to 1.0

        smooth_nmin : int
            If this is 0, then no smoothing of the path is performed.
            If it is not zero, then it must be an odd integer.
            It is the width of a windowed average.  Larger window widths
            will increase smoothing, but it will also cut corners.
            I recommend setting this to 3. If you don't have sharp
            corners in your path, you could set it to 5.

        smooth_nmax : int
            This must be an odd integer >= 3.  One smoothing is applied
            with smooth_nmin, a series of additional corrects are performed
            by windowed averaging of the reference and smoothed paths
            to try and reduce the amount of corner cutting.  I recommend
            setting this to 11. Larger values will have only a minor
            impact on the final result.

        denest : ndfes.DensityEst.DensityEst
            The density calculator

        dampfactor : float
            The percentage by which the density should be damped

        fh : opened outout filehandle, default=None
            Write convergence information to file

        Returns
        -------
        None, but it changes the length of the self.paths attribute
        """
        if denest is not None:
            for it in range(maxit):

                if fh is not None:
                    fh.write("Synthetic iteration %i\n"%(it+1))
                
                npath = self.paths[-1].Next\
                    ( fix0, fix1, smooth_fact, smooth_nmin, smooth_nmax,
                      denest,dampfactor )
                
                samemeans,pmin = FTSMCheckSameMeans(npath,self.paths[-1],ptol,fh=fh)
                
                if samemeans:
                    if fh is not None:
                        fh.write("Converged because means are same\n")
                    break
                else:
                    self.paths.append(npath)
                    
                if fh is not None:
                    if it == maxit-1:
                        fh.write("Terminated because maxit reached\n")
                        fh.write("Convergence would be met if "
                                 +"ptol <= %.3f\n"%(pmin))
        else:
            if fh is not None:
                fh.write("No iterations because a density estimator"
                         +" was not supplied\n")
        

    def append(self,path):
        """Append a path"""
        self.paths.append(path)
                
    def __getitem__(self,i):
        """Get a path"""
        return self.paths[i]

    def __len__(self):
        """Get the number of paths"""
        return len(self.paths)

    def save(self,fname):
        """Write the optimization object to file in pickle format"""
        import pickle
        fh=open(fname,"wb")
        pickle.dump(self,fh)
        fh.close()

    @classmethod
    def load(cls,fname):
        """Create an optimization object by reading a pickle file"""
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


def CopyFiles(disang,mdin,curit,odir,prefix,extra_prefixes,
              cp_nearest,multidir,firstit,new_rcs,new_fcs):
    """Creates a directory of files for the next set of simulations

    Parameters
    ----------
    disang : str
        Filename, template disang
    
    mdin : str
        Filename, template mdin

    curit : int
        Current iteration. 0 is ./init, otherwise it is ./it%03i

    odir : str
        Output directory name

    prefix : str
        If non-empty, then the files are searched in itXX/prefix
        and written to odir/prefix

    extra_prefixes : list of str
       Search for rst files in itXX/extra

    cp_nearest : bool
        If true, copy the restart file from the closest previous
        window, as determined from the comparison between old_rcs
        and new_rcs

    multidir : bool
       If True, then all restart files from all previous iterations
       are examined and the closest restart is chosen. multidir is
       like cp_nearest, except cp_nearest only looks at the restarts
       in the current directory.

    new_rcs : list of list of float
        The umbrella centers written to the output directory

    new_fcs : list of list of float
        The umbrella force constants written to the output directory
    """

    import numpy as np
    from . amber import Disang
    import shutil
    from pathlib import Path
    import re
    import os
    import sys


    tdisang = Disang( disang )
    tdisang.ValidateTemplate()
    tidxs = tdisang.GetTemplateIdxs()
    
    new_rcs = np.array( new_rcs )
    new_fcs = np.array( new_fcs )
    nsim = new_rcs.shape[0]


    searches = None
    if prefix is not None:
        if prefix != "":
            searches = [prefix]
    if extra_prefixes is not None:
        prefs = list(set(extra_prefixes))
        searches.extend( [ sdir for sdir in prefs
                           if sdir != "" ] )

    if searches is None:
        searches = [None]
    else:
        if len(searches) == 0:
            searches = [None]
        
    old_files = []
    old_rcs = []
    if multidir or cp_nearest:
        for sdir in searches:
            for it in range(firstit,curit+1):
                if not multidir and cp_nearest and it != curit:
                    continue
                if it == 0:
                    idir = "init"
                else:
                    idir = "it%03i"%(it)

                if sdir is not None:
                    idir = "%s/%s"%(idir,sdir)
                
                for img in range(nsim):
                    base = "%s/img%03i"%(idir,img+1)
                    rst = base + ".rst7"
                    dis = base + ".disang"
                    if os.path.exists(rst) and os.path.exists(dis):
                        d = Disang(dis)
                        rc = [ d.restraints[idx].r2 for idx in tidxs ]
                        old_files.append( rst )
                        old_rcs.append( rc )
        old_files = old_files
        old_rcs = np.array( old_rcs )
        

        
    fh = open(mdin,"r")
    tmdin = fh.read().split("\n")
    fh.close()

    odir_path = Path(odir)
    mdin_path = Path(mdin)

    if prefix is not None:
        if prefix != "":
            odir_path = odir_path / prefix
    
    def relative_symlink(src, dst):
        d   = os.path.dirname(dst)
        Src = os.path.relpath(src, d)
        Dst = os.path.join(d, os.path.basename(dst))
        return os.symlink(Src, Dst)


    if curit == 0:
        cdir = "init"
    else:
        cdir = "it%03i"%(curit)

    if prefix is not None:
        if prefix != "":
            cdir = "%s/%s"%(cdir,prefix)
    
        
    fh = open(odir_path / "sims.txt","w")
    for i in range(nsim):
        xs = " ".join(["%15.8f"%(x) for x in new_rcs[i,:]])
        t = i/(nsim-1)
        fh.write("%3i %8.4f %s\n"%(i+1,t,xs))
    fh.close()
        
    for i in range(nsim):

        odisang = tdisang.SetTemplateValues(new_rcs[i,:],ks=new_fcs[i,:])

        if cp_nearest or multidir:
            iold = 0
            dmin = 1.e+30
            for k in range( old_rcs.shape[0] ):
                dc = np.linalg.norm( new_rcs[i,:]-old_rcs[k,:] )
                if dc <= dmin:
                    dmin = dc
                    iold = k
            old_rst = old_files[iold]
        else:
            old_rst = "%s/img%03i.rst7"%(cdir,i+1)

            
        fname = odir_path / ("img%03i.disang"%(i+1))
        print("   Writing %s"%(fname))
        fh = open(fname,"w")
        odisang.Write(fh)
        fh.close()

        fname = odir_path / ("img%03i.mdin"%(i+1))
        print("   Writing %s"%(fname))
        fh = open(fname,"w")
        found_disang = False
        found_dumpave = False
        for line in tmdin:
            if "DISANG" in line:
                m = re.match(r"DISANG *=.*",line)
                if m:
                    line = re.sub(r"DISANG *=.*",
                                  "DISANG=img%03i.disang"%(i+1),
                                  line)
                    found_disang=True
            if "DUMPAVE" in line:
                m = re.match(r"DUMPAVE *=.*",line)
                if m:
                    line = re.sub(r"DUMPAVE *=.*",
                                  "DUMPAVE=img%03i.dumpave"%(i+1),
                                  line)
                    found_dumpave=True
            fh.write(line+"\n")
        fh.close()
    
        if not found_disang:
            raise Exception("DISANG field was not found in "
                            +"%s"%(mdin_path))
        if not found_dumpave:
            raise Exception("DUMPAVE field was not found in "
                            +"%s"%(mdin_path))

        orst = odir_path / ("init%03i.rst7"%(i+1))
        
        print("   Copying file %s -> %s\n"%(old_rst,orst))
        
        #shutil.copyfile(old_rst, orst)
        
        if os.path.exists(orst):
            os.remove(orst)
        if os.path.islink(orst):
            os.unlink(orst)
            
        relative_symlink(old_rst,orst)

    sys.stdout.flush()

        
def CheckConvAndSavePathPickles( prevdir, curdir,
                                 mlen, distol, angtol, closest,
                                 isangle,
                                 paths, dryrun, tetris ):
    from pathlib import Path
    import os
    import sys

    curdir = Path(curdir)
    
    new_sims_path = FTSMOpt(None)
    
    if prevdir is not None:
        if len(prevdir) > 0:
            prevdir = Path(prevdir)
            prev_path = prevdir / "path.sims.pkl"
            if not prev_path.exists():
                raise Exception(f"{prev_path} not found. prevdir='{str(prevdir)}'")
            prev = FTSMOpt.load( prev_path )
            for i in range(len(prev)):
                new_sims_path.append( prev[i] )
            
    new_micro_path = FTSMOpt(None)
    for i in range(len(paths)):
        new_micro_path.append( paths[i] )
    if not dryrun:
        new_micro_path.save( curdir / "path.micro.pkl" )


    # This only works if the FTSM reads the means as the initial path when iter > 0
    # It currently does not work like that
    #if "init" not in str(curdir) and len(paths) > 1:
    #    paths = paths[1:]
    if tetris or (len(paths[0]) != len(paths[-1])):
        new_sims_path.append( paths[-1] )
    else:
        splpts0,splts0,ts0,rcs0,fcs0,nobs0,obsmean0,obsstd0,neff0,effmean0,effstd0 = paths[0].GetSimData()
        splptsN,spltsN,tsN,rcsN,fcsN,nobsN,obsmeanN,obsstdN,neffN,effmeanN,effstdN = paths[-1].GetSimData()
        modpath = FTSMString.from_simdata( splpts0,splts0,ts0,rcs0,fcs0,nobsN,obsmeanN,obsstdN,neffN,effmeanN,effstdN )
        new_sims_path.append( modpath )
    if not dryrun:
        new_sims_path.save( curdir / "path.sims.pkl" )




    print("\nChecking for convergence between the strings in",
          prevdir,"and",curdir,"\n... (the next iteration",
          " is created regardless of the outcome) ...")

    path_is_conv = False
    
    if True:
        fhs = [sys.stdout]
        if not dryrun:
            ofile = curdir / "pathconv.txt"
            ofh = open(ofile,"w")
            fhs.append( ofh )
        for fh in fhs:
            if len(new_sims_path) < 2:
                fh.write("Not converged because this is the first iteration\n")
            else:
                fh.write("="*80 + "\n")
                fh.write("SLOPE TEST\n\n")
                conv,dismax,angmax = \
                    FTSMCheckSlopes(new_sims_path,mlen,
                                    distol,angtol,
                                    isangle,closest,fh=fh)
                fh.write("Convergence would be met if "
                         +"distol >= %.2e and angtol >= %.2e\n"%(dismax,angmax))
                if conv:
                    fh.write("Slopes appears to be converged")
                else:
                    fh.write("Slopes are NOT converged")
                fh.write("\n\n")

                FTSMCheckRMSD(new_sims_path,mlen,fh)
                
                # fh.write("="*80 + "\n")
                # fh.write("CENTROID MEAN T-TESTS\n\n")
                # samemeans,pmin = FTSMCheckSameMeans(new_sims_path[-2],new_sims_path[-1],ptol,fh=fh)
                # fh.write("Convergence would be met if "
                #          +"ttol < %.3e\n"%(pmin))
                # if samemeans:
                #     fh.write("Means are statistically similar")
                # else:
                #     fh.write("Means are are NOT converged")

                # fh.write("\n\n")
                # fh.write("="*80 + "\n")
                # fh.write("OVERALL PATH TEST RESULT\n")
                # if conv and samemeans:
                #     fh.write("Path is converged, please check if the sampling has converged")
                #     path_is_conv = True
                # else:
                #     fh.write("Path has NOT converged")

    sys.stdout.flush()

    

# def SavePathPickles( fname, paths ):
#     new_sims_path = FTSMOpt(None)
#     new_sims_path
#     new_sims_path.save( fname )


def FTSMMin(interp, xs, npts, ks, obs_stds,
            tol, maxit,
            fix0, fix1,
            smooth_fact, smooth_nmin, smooth_nmax,
            oobk=100.):
    """Uses the string method to locate a minimum free energy pathway
    represented by a parametric Akima spline

    Parameters
    ----------
    interp : ndfes.GPR or ndfes.VFEP
        Free energy surface interpolation object

    xs : list of list
        The points defining the intial guess at the pathway. The number of
        points does not need to be the same as the number of output points

    npts : int
        The number of output points

    ks : list
        The biasing potential force constants used in the minimizations

    obs_stds : list of list
        The standard deviation of each simulation in each direction. This
        is only used for convergence testing. You can approximate these
        from the last set of simulations, or the width of each bin.

    tol : float
        Stopping tolerance to terminate the string method. If the norm of the
        displacements is smaller than the tolerance, then the method stops

    maxit : int
        Stop the string method even if the tolerance is not met

    fix0 : bool
        Allow the t=0 endpoint to move

    fix1 : bool
        Allow the t=1 endpoint to move

    smooth_fact : float
        A number between 0 and 1. It controls the amount of smoothing
        by taking a linear combination of the smoothed and unsmoothed
        paths. One should probably always set this to 1.0

    smooth_nmin : int
        If this is 0, then no smoothing of the path is performed.
        If it is not zero, then it must be an odd integer.
        It is the width of a windowed average.  Larger window widths
        will increase smoothing, but it will also cut corners.
        I recommend setting this to 3. If you don't have sharp
        corners in your path, you could set it to 5.

    smooth_nmax : int
        This must be an odd integer >= 3.  One smoothing is applied
        with smooth_nmin, a series of additional corrects are performed
        by windowed averaging of the reference and smoothed paths
        to try and reduce the amount of corner cutting.  I recommend
        setting this to 11. Larger values will have only a minor
        impact on the final result.

    oobk : float, default=100.
        The harmonic force constant penalty for out-of-bounds interpolations

    Returns
    -------
    ndfes.FTSMOpt
        The optimized pathway
    """

    import numpy as np
    from . PathUtils import PCurve
    from . SmoothCurve import SmoothCurve_IterReflectedAvg
    from . OptUtils import BiasedMinimize
    import sys
    
    ix = np.array(xs)

    # if not fix0:
    #     ix[0],ok = UnbiasedMinimize( interp, ix[0], oobk )
    # if not fix1:
    #     ix[-1],ok = UnbiasedMinimize( interp, ix[-1], oobk )

    paths = []
    
    ndim = ix.shape[1]
    
    obs_stds = np.array(obs_stds)
    if len(obs_stds.shape) == 1:
        std = np.array( [obs_stds]*npts )
    else:
        if obs_stds.shape[0] != npts:
            raise Exception(f"obs_stds has shape {obs_stds.shape} expected {(npts,ndim)}")
        elif obs_stds.shape[1] != ndim:
            raise Exception(f"obs_stds has shape {obs_stds.shape} expected {(npts,ndim)}")
        else:
            std = obs_stds

    pspl = PCurve(ix,fixt=False)
    uts = np.linspace(0,1,npts)
    for it in range(maxit+1):
        print("Minimization step %3i"%(it))
        ix = np.array( [ pspl.GetValue(t) for t in uts ] )
        ###
        ix_prev = np.array(ix,copy=True)
        ox = np.zeros( ix.shape )
        ilo=0
        ihi=npts
        if fix0:
            ox[0] = ix[0]
            ilo += 1
        if fix1:
            ox[-1] = ix[-1]
            ihi -= 1
        for i in range(ilo,ihi):
            ox[i],ok = BiasedMinimize( interp, ix[i], ks, ix[i], oobk )

        for i in range(npts):
            ibin = interp.grid.GetGlbBinIdx(ox[i])
            if ibin not in interp.bins:
                ibin = interp.GetClosestBinIdx(ox[i])
                ox[i] = np.array([x for x in interp.bins[ibin].center])
            
        if pspl.x.shape[0] == ix.shape[0]:
            path = FTSMString.from_simdata( pspl.x, pspl.t, uts, ix, [ks]*npts,
                                            [100]*npts, ox, std,
                                            [100]*npts, ox, std )
            paths.append(path)

        if len(paths) > 1:
            samemeans,pmin = FTSMCheckSameMeans(paths[-2],paths[-1],tol,fh=sys.stdout)
            if samemeans:
                print("Converged because means are same\n")
                break
            elif it == maxit:
                print("Terminated because maxit reached\n")
                print("Convergence would be met if "
                      +"ptol <= %.3f\n"%(pmin))
            
        if smooth_fact > 0 and smooth_nmin >= 3 and smooth_nmax >= smooth_nmin:
            ox = SmoothCurve_IterReflectedAvg(ox,smooth_nmin,smooth_nmax,smooth_fact)

        pspl = PCurve(ox,fixt=False)

    return FTSMOpt(paths)
