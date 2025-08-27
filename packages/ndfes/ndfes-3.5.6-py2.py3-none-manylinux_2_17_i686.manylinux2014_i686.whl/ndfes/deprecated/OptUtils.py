#!/usr/bin/env python3


def UnbiasedInterp(x,interp,scale,oobk):
    res = interp.CptInterp([x],return_deriv=True,k=oobk)
    return scale * res.values[0], scale * res.derivs[0]


def BiasedInterp(x,interp,scale,k,x0,oobk):
    res = interp.CptInterp([x],return_deriv=True,k=oobk)
    val = scale * res.values[0]
    grd = scale * res.derivs[0]
    for i in range(len(x)):
        dx = x[i]-x0[i]
        val += k[i]*dx*dx
        grd[i] += 2*k[i]*dx
    return val,grd


def UnbiasedMinimize(interp,x,oobk):
    """
    Optimizes the position x for a local minimum on the free energy surface
    
    Parameters
    ----------
    interp : ndfes.GPR or ndfes.VFEP
        The free energy surface interpolation object. It must provide a
        GetValues method, analogous to ndfes.GPR

    x : list
        The initial guess

    oobk : float
        The harmonic force constant penalty for out-of-bounds interpolations

    Results
    -------
    numpy.array, shape=(ndim,)
        The optimized point

    bool
        True if optimization was successful
    """
    
    from scipy.optimize import minimize
    res = minimize( UnbiasedInterp, x,
                    args=(interp,1,oobk),
                    jac=True, method='L-BFGS-B')
    return res.x,res.success


def BiasedMinimize(interp,x,k,x0,oobk):
    """
    Optimizes the position x for a local minimum on a biased free energy 
    surface
    
    Parameters
    ----------
    interp : ndfes.GPR or ndfes.VFEP
        The free energy surface interpolation object. It must provide a
        GetValues method, analogous to ndfes.GPR

    x : list
        The initial guess

    k : list
        The bias prefactor for each dimension; \sum_i k[i]*(x[i]-x0[i])**2

    x0 : list
        The bias window positions in each dimension

    oobk : float
        The harmonic force constant penalty for out-of-bounds interpolations

    Results
    -------
    numpy.array, shape=(ndim,)
        The optimized point

    bool
        True if optimization was successful
    """
    
    from scipy.optimize import minimize
    res = minimize( BiasedInterp, x,
                    args=(interp,1,k,x0,oobk),
                    jac=True, method='L-BFGS-B')
    return res.x,res.success


def UnbiasedMaximize(interp,x,oobk):
    """
    Optimizes the position x for a local maximum on the free energy surface
    
    Parameters
    ----------
    interp : ndfes.GPR or ndfes.VFEP
        The free energy surface interpolation object. It must provide a
        GetValues method, analogous to ndfes.GPR

    x : list
        The initial guess

    oobk : float
        The harmonic force constant penalty for out-of-bounds interpolations

    Results
    -------
    numpy.array, shape=(ndim,)
        The optimized point

    bool
        True if optimization was successful
    """
    
    from scipy.optimize import minimize
    res = minimize( UnbiasedInterp, x,
                    args=(interp,-1,oobk),
                    jac=True, method='L-BFGS-B')
    return res.x,res.success


def BiasedMaximize(interp,x,k,x0,oobk):
    """
    Optimizes the position x for a local maximum on a biased free energy 
    surface
    
    Parameters
    ----------
    interp : ndfes.GPR or ndfes.VFEP
        The free energy surface interpolation object. It must provide a
        GetValues method, analogous to ndfes.GPR

    x : list
        The initial guess

    k : list
        The bias prefactor for each dimension; \sum_i k[i]*(x[i]-x0[i])**2

    x0 : list
        The bias window positions in each dimension

    oobk : float
        The harmonic force constant penalty for out-of-bounds interpolations

    Results
    -------
    numpy.array, shape=(ndim,)
        The optimized point

    bool
        True if optimization was successful
    """
    
    from scipy.optimize import minimize
    res = minimize( BiasedInterp, x,
                    args=(interp,-1,k,x0,oobk),
                    jac=True, method='L-BFGS-B')
    return res.x,res.success




def AkimaDensityStringMethod_OLD( denest, xs, npts, ks, grid,
                              tol=1.e-4, maxit=300,
                              fix0=True, fix1=True,
                              T=298., varyks=False,
                              minks=None,maxks=None,
                              verbose=True):
    """Uses the string method to locate a minimum free energy pathway
    represented by a parametric Akima spline

    Parameters
    ----------
    denest : ndfes.DensityEst
        FES density estimator used to predict the expected locations
        of the reaction coordinates from a biased simulation

    xs : list of list
        The points defining the intial guess at the pathway. The number of
        points does not need to be the same as the number of output points

    npts : int
        The number of output points

    ks : numpy.array, dtype=float, shape=(ndim,) or shape(npts,ndim)
        The biasing potential force constants used in the minimizations
        If len(ks.shape) == 2 (that is, if ks is a matrix), then it 
        defines the force constants for each window in the path.
        If len(ks.shape) == 1 (that is, if vs is a vector), then it
        defines the force costants of each dimension and each window
        uses the same force constants

    grid : numpy.VirtualGrid.VirtualGrid
        The grid defining the range and periodicity of the dimensions

    tol : float, default=1.e-4
        Stopping tolerance to terminate the string method. If the maximum
        displacement is smaller than the tolerance, then the method stops

    maxit : int, default=300
        Stop the string method even if the tolerance is not met

    fix0 : bool, default=True
        Allow the t=0 endpoint to move

    fix1 : bool, default=True
        Allow the t=1 endpoint to move
    
    T : float, default=298.
        Simulation temperature

    varyks : bool, default=False
        If true, then allow the umbrella window force constants to
        change during the path optimization.

    minks : numpy.array, dtype=float, shape=(ndim,)
        The minimum allowable force constant value in each direction
        If not provided, it defaults to 50 kcal/mol/A^2 in each direction
        For periodic dimensions, it defaults to 0.4 kcal/mol/degree

    maxks : numpy.array, dtype=float, shape=(ndim,)
        The maximum allowable force constant value in each direction
        If not provided, it defaults to 300 kcal/mol/A^2 in each direction
        For periodic dimensions, it defaults to 2 kcal/mol/degree

    verbose : bool, default=True
        Print path finding progress to stdout

    Returns
    -------
    pcurve : ndfes.PCurve
        The final parametric spline

    kmat : numpy.array, shape=(npts,ndim)
        The final force constants (note that the spline points can be
        found in pcurve.x)

    paths : list of numpy.array
        The points from each iteration of optimization.
        The size of the list is the number of iterations.
        Each element of the list is a numpy matrix of shape (npts,ndim)
        corresponding to the path points defining a parametric curve.

    means : list of numpy.array
        The centroids of each simulation performed along the path

    stddevs : list of numpy.array
        The centroid standard deviations for each simulation performed
        along the path

    """

    import numpy as np
    from . PathUtils import AkimaStringMethodUpdate
    from . PathUtils import PCurve

    ix = np.array(xs)

    paths = []
    means = []
    stddevs = []
    

    # if not fix0:
    #     ox = np.array(ix[0],copy=True)
    #     dx = 1.e+10
    #     for it in range(maxit):
    #         ix[0] = denest.GetAvgPos(T,ks,ix[0])
    #         dx = np.linalg.norm( ix[0]-ox )
    #         ox = np.array(ix[0],copy=True)
    #         if dx < tol:
    #             break        
    # if not fix1:
    #     ox = np.array(ix[-1],copy=True)
    #     dx = 1.e+10
    #     for it in range(maxit):
    #         ix[-1] = denest.GetAvgPos(T,ks,ix[-1])
    #         dx = np.linalg.norm( ix[-1]-ox )
    #         ox = np.array(ix[-1],copy=True)
    #         if dx < tol:
    #             break      

    kmat = np.zeros( (npts,grid.ndim) )
    ks = np.array(ks)
    if len(ks.shape) == 2:
        if ks.shape[0] == npts and ks.shape[1] == grid.ndim:
            kmat[:,:] = ks[:,:]
        else:
            raise Exception("number of force constants does not "
                            +"match the number of windows "
                            +"%i "%(ks.shape[0])
                            +"%i"%(ix.shape[0]))
    elif ks.shape[0] == kmat.shape[1]:
        for i in range(npts):
            kmat[i,:] = ks[:]
    else:
        raise Exception("number of force constants does not match "
                        +"the number of windows nor the dimensionality")

    if maxks is None:
        maxks = np.array( [300.]*grid.ndim )
        for d in range(grid.ndim):
            if grid.dims[d].isper:
                minks[d] = 2.
    elif len(maxks.shape) != 1:
        raise Exception("maxks should be a vector, but a matrix was provided")
    elif maxks.shape[0] != grid.ndim:
        raise Exception("size of maxks does not match dimensionality")

    if minks is None:
        minks = np.array( [50.]*grid.ndim )
        for d in range(grid.ndim):
            if grid.dims[d].isper:
                minks[d] = 0.4
    elif len(minks.shape) != 1:
        raise Exception("minks should be a vector, but a matrix was provided")
    elif minks.shape[0] != grid.ndim:
        raise Exception("size of minks does not match dimensionality")

    
        
    kmat_orig = np.array(kmat,copy=True)
    isoptk = False
    isfirstoptk = False

    if varyks:
        optimizations = [False,True]
    else:
        optimizations = [False]


#    fh = open("pathiters.dat","w")
        
    for isoptk in optimizations:
    
        for it in range(maxit):
            ix = AkimaStringMethodUpdate(npts,ix,scf=False)

            paths.append(np.array(ix,copy=True))

            mean = np.array( ix, copy=True )
            std = np.zeros( (npts,grid.ndim) )

            ilo=0
            ihi=npts
            if fix0:
                ilo += 1
            if fix1:
                ihi -= 1
                
            for i in range(ilo,ihi):
                m,v = denest.GetAvgPosAndStd(T,kmat[i,:],ix[i])
                mean[i,:] = m[:]
                std[i,:] = v[:]
            means.append(mean)
            stddevs.append(std)
            
            #fh.write("# it %i\n"%(it))
            #for i in range(ix.shape[0]):
            #    t = i/(ix.shape[0]-1)
            #    fh.write("%12.6f %s\n"%(t," ".join(["%12.6f"%(u) for u in ix[i,:]])))
            #fh.write("\n")
            
            if it > 0:
                dx = max([np.linalg.norm(ix_prev[i]-ix[i])
                          for i in range(npts)])
                print(it,dx,ix[0],ix[-1])

                if dx < tol:
                    break

                ix_prev[:,:]=ix[:,:]
            else:
                ix_prev = np.array(ix,copy=True)

            for i in range(ilo,ihi):
                ix[i] = means[-1][i,:]

                
            if verbose:
                rhos = []
                for k in range(npts):
                    rhos.append( denest.GetDensity(T, fcs=kmat[k,:],
                                                   rcs=ix_prev[k,:]) )
                Ss = []
                for k in range(npts):
                    if k < npts-1:
                        s = denest.GetOverlapPercentFromBinDensities\
                            ( rhos[k], rhos[k+1] )
                        Ss.append(s)
                    else:
                        Ss.append( Ss[-1] )
            
                ii=0       
                for x,y,z,s in zip(ix,kmat,ix_prev,Ss):
                    frac = ii/(npts-1)
                    ii += 1
                    print("%9.6f s: %.2f x:"%(frac,s)
                          +" ".join(["%9.3f"%(d) for d in x])
                          +" disp:"
                          +" ".join(["%7.3f"%(x[i]-z[i])
                                     for i in range(len(x))])
                          +" k:"
                          +" ".join(["%6.1f"%(d) for d in y]))


            if True and isoptk:
                new_kmat = np.array(kmat,copy=True)
                for i in range(ilo,ihi):
                    if i == 0:
                        dw = ix_prev[i+1,:]-ix_prev[i]
                    elif i == npts-1:
                        dw = ix_prev[i,:]-ix_prev[i-1]
                    else:
                        dw = 0.5*(ix_prev[i+1,:]-ix_prev[i-1])

                    lw = np.linalg.norm(dw)
                    uw = dw/lw
                    
                    dx = ix[i,:]-ix_prev[i,:]
                    lx = np.linalg.norm(dx)
                    if lx < 0.001:
                        # if there's no displacement, then do nothing
                        new_kmat[i,:] = kmat[i,:]
                    else:
                        ux = dx/lx
                        proj = np.dot(uw,ux)
                            
                        # perc is the percentage of the displacement
                        # through the gap between points
                        perc = np.dot(uw,dx)/lw
                        if verbose:
                            print("%3i gap: %8.3f "%(i,perc)
                                  +"uT.v: %7.3f"%(proj))


                        new_kmat[i,:] = kmat[i,:] * abs(perc)/0.5 
                        for d in range(grid.ndim):
                            new_kmat[i,d] = max(minks[d],min(new_kmat[i,d],maxks[d]))                        
                        
                    kmat[i,:] = new_kmat[i,:]

                wo=0.25
                wi=1-2*wo
                for d in range(grid.ndim):
                    for i in range(npts):
                        if i == 0:
                            k=(wi+wo)*kmat[i,d]+wo*kmat[i+1,d]
                        elif i == npts-1:
                            k=(wi+wo)*kmat[i,d]+wo*kmat[i-1,d]
                        else:
                            k=wo*(kmat[i+1,d]+kmat[i-1,d])+wi*kmat[i,d]
                        kmat[i,d]=max(kmat[i,d],k)

                    

            if False:
                if isoptk:
                    new_kmat = np.array(kmat,copy=True)
                    for i in range(ilo,ihi):
                        #
                        # dw = the vector tangent to the path at point i
                        # lw = the length of dw
                        # uw = the unit vector
                        #
                        if i == 0:
                            dw = ix_prev[i+1,:]-ix_prev[i]
                        elif i == npts-1:
                            dw = ix_prev[i,:]-ix_prev[i-1]
                        else:
                            dw = 0.5*(ix_prev[i+1,:]-ix_prev[i-1])

                        lw = np.linalg.norm(dw)
                        uw = dw/lw

                        #
                        # dx = the expected displacement of the centroid
                        # lx = the displacement length
                        # ux = the unit vector
                        #
                        dx = ix[i,:]-ix_prev[i,:]
                        lx = np.linalg.norm(dx)
                        if lx < 0.001:
                            # if there's no displacement, then do nothing
                            new_kmat[i,:] = kmat[i,:]
                        else:
                            ux = dx/lx

                            # uu[k] = uw[k]*ux[k]
                            # uu[k] = 1 if uw and ux are colinear
                            #         along direction k
                            uu=abs(uw*ux)**2
                            #fuu = uu / np.linalg.norm(uu)
                            #fuu = uu/sum(uu)
                            fuu = uu/max(uu)
                        
                            #avgfuu = np.mean(fuu)
                            # proj = uw^T . ux 
                            proj = np.dot(uw,ux)
                            
                            # perc is the percentage of the displacement
                            # through the gap between points
                            perc = np.dot(uw,dx)/lw
                            if verbose:
                                print("%3i gap: %8.3f "%(i,perc)
                                      +"uT.v: %7.3f"%(proj)
                                      +" (u*v)^2: %s"%(" ".join(["%5.2f"%(h)
                                                                 for h in uu]))
                                      +" (u*v)^2/max((u*v)^2): "
                                      +"%s"%(" ".join(["%5.2f"%(h)
                                                       for h in fuu])))
                                  
                        
                            # Estimate the force constants that would
                            # yield a centroid displacement of dw/2
                            # in each direction.  Call that khalf.
                            # If the centroid is moving perpendicular
                            # to the path, then we lower the force constant
                            # by an amount uu[k] so it is free to
                            # find a better path.
                            k = kmat[i,:]

                            w1=abs(proj)
                            w2=1.-w1

                            scale = abs(perc)/0.5 * ( fuu*w2 + w1 )

                            new_kmat[i,:] = kmat[i,:] * scale
                            for d in range(grid.ndim):
                                new_kmat[i,d] = max(minks[d],min(new_kmat[i,d],maxks[d]))
                        
                        
                        kmat[i,:] = new_kmat[i,:]
                    
                        
                
    return PCurve(ix,fixt=False),kmat,paths,means,stddevs





def OverlapChisq(p,rbf):
    import numpy as np
    x = [0]
    x.extend( [ u for u in p ] )
    x.extend( [1] )
    x.sort()
    x = np.array(x)
    pts = np.array([ [ x[i], x[i+1] ] for i in range(len(x)-1) ])
    
    ret = rbf.GetValues(pts,return_deriv=True)
    ns = pts.shape[0]
    nx = x.shape[0]
    
    if True:
        avg = np.sum(ret.values/ns)
        davgdx = np.zeros( (nx,) )
        for ipt in range(ns):
            davgdx[ipt]   += ret.derivs[ipt,0]/ns
            davgdx[ipt+1] += ret.derivs[ipt,1]/ns

        dvdx = np.zeros( (nx,) )
        v = 0
        for ipt in range(ns):
            u = ret.values[ipt]-avg
            v += u**2/(ns-1)
            dvdu = 2*u/(ns-1)
            #v += u
            #dvdu = 1
            dudval = 1
            #dudavg = -ns/2
            dvaldx = ret.derivs[ipt,:]
            #dvdx[ipt]   += c*(ret.derivs[ipt,0]-davgdx[ipt])
            #dvdx[ipt+1] += c*(ret.derivs[ipt,1]-davgdx[ipt])
            #dvdx[ipt]   += c*(ret.derivs[ipt,0]-ret.derivs[ipt,0]/ns)
            #dvdx[ipt+1] += c*(ret.derivs[ipt,1]-ret.derivs[ipt,1]/ns)
            dvdx[ipt]   += dvdu*dudval*dvaldx[0] #+ dvdu*dudavg*davgdx[ipt]
            dvdx[ipt+1] += dvdu*dudval*dvaldx[1] #+ dvdu*dudavg*davgdx[ipt+1]


            
    dv = dvdx[1:-1]
    
    #for pt,val in zip(pts,ret.values):
    #    print("%s %12.4f"%(" ".join(["%8.3f"%(u) for u in pt]),val))
    #print("%12.4f"%(v))

    # for ip in range(len(p)):
    #     ipts = [ ip, ip + 1 ]
    #     idim = [ 1, 0 ]
    #     for i,d in zip(ipts,idim):
    #         davg[ip] += ret.derivs[i,d]/n
    #     for i,d in zip(ipts,idim):
    #         c = 2*(ret.values[i]-avg)/(n-1)
    #         dv[ip] += c * ( ret.derivs[i,d] - ret.derivs[i,d]/n )
    #return avg,davgdx[1:-1]
    print("var(S): %12.6f S: "%(v)
          + " ".join(["%4.2f"%(s) for s in ret.values]))
    return v,dv




def OverlapChisq4(p,rbf):
    import numpy as np
    x = [0]
    x.extend( [ u for u in p ] )
    x.extend( [1] )
    x.sort()
    x = np.array(x)
    pts = np.array([ [ x[i], x[i+1] ] for i in range(len(x)-1) ])
    
    ret = rbf.GetValues(pts,return_deriv=True)
    ns = pts.shape[0]
    nx = x.shape[0]
    
    if True:
        avg = np.sum(ret.values/ns)
        davgdx = np.zeros( (nx,) )
        for ipt in range(ns):
            davgdx[ipt]   += ret.derivs[ipt,0]/ns
            davgdx[ipt+1] += ret.derivs[ipt,1]/ns

        dvdx = np.zeros( (nx,) )
        v = 0
        for ipt in range(ns):
            u = ret.values[ipt]-avg
            v += u**2/(ns-1)
            dvdu = 2*u/(ns-1)

            dudval = 1
            dvaldx = ret.derivs[ipt,:]

            dvdx[ipt]   += dvdu*dudval*dvaldx[0]
            dvdx[ipt+1] += dvdu*dudval*dvaldx[1]

    dv = dvdx[1:-1]
    
    print("var(S): %12.6f S: "%(v)
          + " ".join(["%4.2f"%(s) for s in ret.values]))
    
    return v**2,2*v*dv



def OverlapChisq2(p,rbf,self,kspl):
    import numpy as np
    x = [0]
    x.extend( [ u for u in p ] )
    x.extend( [1] )
    x.sort()
    x = np.array(x)
    pts = np.array([ [ x[i], x[i+1] ] for i in range(len(x)-1) ])
    
    ret = rbf.GetValues(pts,return_deriv=True)
    ns = pts.shape[0]
    nx = x.shape[0]


    
    if True:
        avg = np.sum(ret.values/ns)
        davgdx = np.zeros( (nx,) )
        for ipt in range(ns):
            davgdx[ipt]   += ret.derivs[ipt,0]/ns
            davgdx[ipt+1] += ret.derivs[ipt,1]/ns

        dvdx = np.zeros( (nx,) )
        v = 0
        for ipt in range(ns):
            u = ret.values[ipt]-avg
            v += u**2/(ns-1)
            dvdu = 2*u/(ns-1)
            dudval = 1
            dvaldx = ret.derivs[ipt,:]
            dvdx[ipt]   += dvdu*dudval*dvaldx[0]
            dvdx[ipt+1] += dvdu*dudval*dvaldx[1]


            
    dv = dvdx[1:-1]

    rs = []
    for i in range(len(x)):
        t = x[i]
        c = self.pc.GetValue(t)
        k = kspl.GetValue(t)
        rs.append( self.denest.GetDensity(k,c) )

    Sref = []
    for i in range(len(x)-1):
        s = self.denest.GetOverlapPercentFromBinDensities( rs[i],rs[i+1] )
        Sref.append(s)
    
    print("var(S): %12.6f S: "%(v)
          + " ".join(["%4.2f"%(s) for s in ret.values]))

    myv = np.var(Sref,ddof=1)
    
    print("ref(S): %12.6f S: "%(myv)
          + " ".join(["%4.2f"%(s) for s in Sref]))
    
    print("")

    
    return v,dv


def FindTValue(allts,allcrds,crd):
    import numpy as np
    from scipy.interpolate import Akima1DInterpolator as akima
    
    rsqs = np.array( [ np.linalg.norm(crd[:]-allcrds[i,:])**2
                       for i in range(allcrds.shape[0])] )
    imin = np.argmin(rsqs)
    tmin = allts[imin]

    roots = akima(allts,rsqs).derivative().roots()
    t = tmin
    if len(roots) > 0:
        t=roots[0]
        for r in roots[1:]:
            if abs(r-tmin) < abs(t-tmin):
                t=r

    return t
    

def ParamConstraint(p,lbs,ubs):
    pen=0
    for i in range(len(p)):
        if p[i] < lbs[i]:
            pen += (p[i]-lbs[i])**2
        if p[i] > ubs[i]:
            pen += (p[i]-ubs[i])**2
    return -pen

def OverlapExplicit(p,self,kspl):
    import numpy as np
    x = [0]
    x.extend( [ u for u in p ] )
    x.extend( [1] )
    x.sort()
    x = np.array(x)
    pts = np.array([ [ x[i], x[i+1] ] for i in range(len(x)-1) ])
    
    rs = []
    for i in range(len(x)):
        t = x[i]
        c = self.pc.GetValue(t)
        k = kspl.GetValue(t)
        rs.append( self.denest.GetDensity(k,c) )

    Sref = []
    for i in range(len(x)-1):
        s = self.denest.GetOverlapPercentFromBinDensities( rs[i],rs[i+1] )
        Sref.append(s)
    
    #v = np.var(Sref,ddof=1)
    v = 0.
    mu = np.mean(Sref)
    for s in Sref:
        v += (s-mu)**4
            
    print("X: "
          + " ".join(["%4.2f"%(s) for s in x]))
    print("ref(S): %12.6f S: "%(v)
          + " ".join(["%4.2f"%(s) for s in Sref]))
    
    return v


class PathProps(object):
    def __init__(self,inppts,npathpts,
                 nsimpts,pathks,
                 denest, 
                 maxks=None,minks=None,
                 simks=None,
                 fix0=False,fix1=False,
                 vary_simks=False,
                 vary_pathks=False,
                 pathts=None,
                 simts=None,
                 target_disp=0.75,
                 nsamples=1):
        import numpy as np
        import copy
        from . PathUtils import PCurve

        self.denest     = denest
        self.fix0       = fix0
        self.fix1       = fix1
        self.target_disp= target_disp
        self.vary_simks = vary_simks
        self.vary_pathks= vary_pathks
        self.path_npts  = npathpts
        self.sim_npts   = nsimpts
        self.ndim       = inppts.shape[1]
        self.path_shape = (self.path_npts,self.ndim)
        self.sim_shape  = (self.sim_npts,self.ndim)
        self.inp_pts    = np.array(inppts,copy=True)
        self.pc         = PCurve(self.inp_pts,fixt=False)

        self.nsamples = nsamples


            
        if pathts is not None:
            self.path_ts = np.array(pathts,copy=True)
            if self.path_ts.shape[0] != self.path_npts:
                self.path_ts = np.linspace(0,1,self.path_npts)
        else:
            self.path_ts = np.linspace(0,1,self.path_npts)

        if simts is not None:
            self.sim_ts = np.array(simts,copy=True)
            if self.sim_ts.shape[0] != self.sim_npts:
                self.sim_ts = np.linspace(0,1,self.sim_npts)
        else:
            self.sim_ts = np.linspace(0,1,self.sim_npts)

        
        self.path_ks  = np.zeros( self.path_shape )

        pathks = np.array(pathks)
        if len(pathks.shape) == 2:
            if pathks.shape[0] == self.path_npts and pathks.shape[1] == self.ndim:
                self.path_ks[:,:] = pathks[:,:]
            else:
                raise Exception("number of force constants does not "
                                +"match the number of windows "
                                +"%i "%(pathks.shape[0])
                                +"%i"%(self.path_npts))
        elif pathks.shape[0] == self.ndim:
            for i in range(self.path_npts):
                self.path_ks[i,:] = pathks[:]
        else:
            raise Exception("number of force constants does not match "
                            +"the number of windows nor the dimensionality")

        if maxks is None:
            maxks = np.array( [300.]*self.ndim )
            for d in range(self.ndim):
                if self.denest.fes.grid.dims[d].isper:
                    minks[d] = 2.
        elif len(maxks.shape) != 1:
            raise Exception("maxks should be a vector, but a matrix was provided")
        elif maxks.shape[0] != self.ndim:
            raise Exception("size of maxks does not match dimensionality")

        self.maxks = np.array(maxks)
        
        if minks is None:
            minks = np.array( [50.]*self.ndim )
            for d in range(self.ndim):
                if self.denest.fes.grid.dims[d].isper:
                    minks[d] = 0.4
        elif len(minks.shape) != 1:
            raise Exception("minks should be a vector, but a matrix was provided")
        elif minks.shape[0] != self.ndim:
            raise Exception("size of minks does not match dimensionality")

        self.minks = np.array(minks)

        if simks is not None:
            simks = np.array(simks)
            if len(simks.shape) == 2:
                if simks.shape[0] != self.sim_npts:
                    raise Exception("simks.shape[0] does not match sim_npts"
                                    +" %i versus %i"%(simks.shape[0],self.sim_npts))
                elif simks.shape[1] != self.ndim:
                    raise Exception("simks.shape[1] does not match ndim"
                                    +" %i versus %i"%(simks.shape[1],self.ndim))
                else:
                    self.sim_ks = np.array( simks, copy=True )
            elif len(simks.shape) == 1:
                if simks.shape[0] != self.ndim:
                    raise Exception("simks.shape[0] does not match ndim"
                                    +" %i versus %i"%(simks.shape[0],self.ndim))
                self.sim_ks = np.zeros( self.sim_shape )
                for i in range(self.sim_npts):
                    self.sim_ks[i,:] = simks[:]

        else:
            self.sim_ks = np.zeros( self.sim_shape )
            splk = PCurve( self.path_ks, t=self.path_ts )
            for i in range(self.sim_npts):
                kp = splk.GetValue( self.sim_ts[i] )
                for d in range(self.ndim):
                    self.sim_ks[i,d] = min(self.maxks[d],max(self.minks[d],kp[d]))
        
                
        self.path_pts = np.array([self.pc.GetValue(t)
                                  for t in self.path_ts])

        self.sim_pts = np.array([self.pc.GetValue(t)
                                  for t in self.sim_ts])

        self.path_means = np.zeros( self.path_shape )
        self.path_stds = np.zeros( self.path_shape )

        self.SetPathMeans()
        
        if self.vary_simks:
            self.SetSimForceConsts()
        if self.vary_pathks:
            self.SetPathForceConsts()

    
            
    def SetPathMeans(self):            
        for i in range(self.path_npts):
            self.path_means[i,:],self.path_stds[i,:] = \
                self.denest.GetAvgPosAndStd(self.path_ks[i,:],
                                            self.path_pts[i,:])
        if self.fix0:
            self.path_means[0,:] = self.path_pts[0,:]
        if self.fix1:
            self.path_means[-1,:] = self.path_pts[-1,:]

            
    def GetSimMeans(self,std=False):
        import numpy as np

        sim_means = np.zeros( self.sim_shape )
        sim_stds = None
        if std is False:
            for i in range(self.sim_npts):
                sim_means[i,:] = \
                    self.denest.GetAvgPos(self.sim_ks[i,:],
                                          self.sim_pts[i,:])
        else:
            sim_stds = np.zeros( self.sim_shape )
            for i in range(self.sim_npts):
                sim_means[i,:],sim_stds[i,:] = \
                    self.denest.GetAvgPosAndStd(self.sim_ks[i,:],
                                                self.sim_pts[i,:])
        if self.fix0:
            sim_means[0,:] = self.sim_pts[0,:]
        if self.fix1:
            sim_means[-1,:] = self.sim_pts[-1,:]
            
        return sim_means,sim_stds
    
    def SetForceConsts(self,verbose=True):
        self.SetPathForceConsts(verbose=verbose)
        self.SetSimForceConsts(verbose=verbose)

    def SetSimForceConsts(self,verbose=True):
        if verbose:
            print("Scaling simulation force constants")
            
        import numpy as np

        newks = np.array(self.sim_ks,copy=True)

        sim_means,sim_stds = self.GetSimMeans(std=False)
        
        
        for i in range(self.sim_npts):
            if i == 0:
                dw = self.sim_pts[i+1,:]-self.sim_pts[i]
            elif i == self.sim_npts-1:
                dw = self.sim_pts[i,:]-self.sim_pts[i-1]
            else:
                dw = 0.5*(self.sim_pts[i+1,:]-self.sim_pts[i-1])

            lw = np.linalg.norm(dw)
            uw = dw/lw
                    
            dx = sim_means[i,:]-self.sim_pts[i,:]
            lx = np.linalg.norm(dx)
            if lx < 0.001:
                # if there's no displacement, then do nothing
                newks[i,:] = self.sim_ks[i,:]
            else:
                ux = dx/lx
                proj = np.dot(uw,ux)
                            
                # perc is the percentage of the displacement
                # through the gap between points
                perc = np.dot(uw,dx)/lw
                
                newks[i,:] = self.sim_ks[i,:] * abs(perc)/self.target_disp
                for d in range(self.ndim):
                    newks[i,d] = max(self.minks[d],min(newks[i,d],self.maxks[d]))
                    
                if verbose:
                    print("%3i gap: %8.3f"%(i,perc)
                          +" uT.v: %7.3f"%(proj)
                          +" k: %s"%(" ".join(["%9.3f"%(k) for k in newks[i,:]])))

        wo=0.25
        wi=1-2*wo
        for d in range(self.ndim):
            for i in range(self.sim_npts):
                if i == 0:
                    k=(wi+wo)*newks[i,d]+wo*newks[i+1,d]
                elif i == self.sim_npts-1:
                    k=(wi+wo)*newks[i,d]+wo*newks[i-1,d]
                else:
                    k=wo*(newks[i+1,d]+newks[i-1,d])+wi*newks[i,d]
                self.sim_ks[i,d]=max(newks[i,d],k)

        return sim_means
    

    def SetPathForceConsts(self,verbose=True):
        import numpy as np
        if verbose:
            print("Scaling path force constants")
    
        newks = np.array(self.path_ks,copy=True)

        
        
        for i in range(self.path_npts):
            if i == 0:
                dw = self.path_pts[i+1,:]-self.path_pts[i]
            elif i == self.path_npts-1:
                dw = self.path_pts[i,:]-self.path_pts[i-1]
            else:
                dw = 0.5*(self.path_pts[i+1,:]-self.path_pts[i-1])

            lw = np.linalg.norm(dw)
            uw = dw/lw
                    
            dx = self.path_means[i,:]-self.path_pts[i,:]
            lx = np.linalg.norm(dx)
            if lx < 0.001:
                # if there's no displacement, then do nothing
                newks[i,:] = self.path_ks[i,:]
            else:
                ux = dx/lx
                proj = np.dot(uw,ux)
                            
                # perc is the percentage of the displacement
                # through the gap between points
                perc = np.dot(uw,dx)/lw
                
                newks[i,:] = self.path_ks[i,:] * abs(perc)/1.0
                for d in range(self.ndim):
                    newks[i,d] = max(self.minks[d],min(newks[i,d],self.maxks[d]))
                    
                if verbose:
                    print("%3i gap: %8.3f"%(i,perc)
                          +" uT.v: %7.3f"%(proj)
                          +" k: %s"%(" ".join(["%9.3f"%(k) for k in newks[i,:]])))

        wo=0.25
        wi=1-2*wo
        for d in range(self.ndim):
            for i in range(self.path_npts):
                if i == 0:
                    k=(wi+wo)*newks[i,d]+wo*newks[i+1,d]
                elif i == self.path_npts-1:
                    k=(wi+wo)*newks[i,d]+wo*newks[i-1,d]
                else:
                    k=wo*(newks[i+1,d]+newks[i-1,d])+wi*newks[i,d]
                self.path_ks[i,d]=max(newks[i,d],k)
                


                
    def GetNewPath(self,vary_simks=None,vary_pathks=None):
        if vary_simks is None:
            vary_simks = self.vary_simks
        if vary_pathks is None:
            vary_pathks = self.vary_pathks
            
        return PathProps(self.path_means,self.path_npts,
                         self.sim_npts,self.path_ks,
                         self.denest,
                         simks=self.sim_ks,
                         maxks=self.maxks,minks=self.minks,
                         fix0=self.fix0,fix1=self.fix1,
                         vary_simks=vary_simks,
                         vary_pathks=vary_pathks,
                         pathts=self.path_ts,
                         simts=self.sim_ts,
                         target_disp=self.target_disp)

    

    def write(self,fh):
        for i in range(self.path_npts):
            fh.write("%9.6f"%(self.path_ts[i]) +
                     " x: %s"%(" ".join(["%9.3f"%(x)
                                         for x in self.path_pts[i,:]]))+
                     " k: %s"%(" ".join(["%9.3f"%(x)
                                         for x in self.path_ks[i,:]]))+
                     " d: %s"%(" ".join(["%9.3f"%(m-x)
                                         for m,x in zip(self.path_means[i,:],
                                                        self.path_pts[i,:])]))+
                     "\n")
            




            
    # def PredictSims_OLD(self,nsim=None):
    #     import numpy as np
    #     from . PathUtils import PCurve
    #     import scipy.optimize as opt
    #     #from scipy.interpolate import Akima1DInterpolator as akima
    #     from scipy.interpolate import interp1d

    #     if nsim is None:
    #         nsim = self.sim_npts
        
    #     kspl = PCurve( self.sim_ks, t=self.sim_ts )

    #     ndim = self.ndim
    #     allts = np.linspace(0,1,301)
    #     allcs = np.zeros( (allts.shape[0],ndim) )
    #     for i in range(allts.shape[0]):
    #         t = allts[i]
    #         allcs[i,:] = self.pc.GetValue(t)

    #     its = np.linspace( 0, 1, 2*(self.path_npts-1) + 1 )
    #     mts = np.zeros( its.shape )
    #     for i,t in enumerate(its):
    #         c = self.pc.GetValue(t)
    #         ks = kspl.GetValue(t)
    #         ks = np.array( [ min(self.maxks[d],max(self.minks[d],ks[d]))
    #                          for d in range(len(ks))] )
    #         m = self.denest.GetAvgPos(self.T,ks,c)
    #         mts[i] = FindTValue(allts,allcs,m)
    #     spl = interp1d(mts,its,kind='linear')
    #     ux = np.linspace(0,1,nsim)
    #     params = spl( ux[1:-1] )
    #     params = np.array( [ 0 ] + [ p for p in params ] + [ 1 ] )
    #     params.sort()

    #     ots = np.zeros( (nsim,) )
    #     oks = np.zeros( (nsim,ndim) )
    #     for i in range(nsim):
    #         t = params[i]
    #         ots[i] = t
    #         oks[i,:] = kspl.GetValue(t)

    #     return PathProps(self.inp_pts,self.path_npts,
    #                      nsim, oks,
    #                      self.denest,T=self.T,
    #                      maxks=self.maxks,minks=self.minks,
    #                      fix0=self.fix0,fix1=self.fix1,
    #                      vary_simks=False,
    #                      vary_pathks=False,
    #                      pathts=self.path_ts,
    #                      simts=ots,
    #                      target_disp=self.target_disp)




    def PredictSims(self):
        import numpy as np
        from . PathUtils import PCurve
        import scipy.optimize as opt
        #from scipy.interpolate import Akima1DInterpolator as akima
        from scipy.interpolate import interp1d

        nsim = self.sim_npts
        
        kspl = PCurve( self.sim_ks, t=self.sim_ts )

        ndim = self.ndim

        means = []
        uts = np.linspace(0,1,self.path_npts)
        for t in uts:
            k = kspl.GetValue(t)
            k = np.array( [ min(self.maxks[d],max(self.minks[d],k[d]))
                             for d in range(len(k))] )
            c = self.pc.GetValue(t)
            means.append( self.denest.GetAvgPos(k,c) )
        means = np.array(means)
        cspl = PCurve( means, fixt=False )
        
        spl = interp1d(cspl.t,uts,kind='linear')
        ux = np.linspace(0,1,nsim)
        params = spl( ux[1:-1] )
        params = np.array( [ 0 ] + params.tolist() + [ 1 ] )
        params.sort()

        ots = np.zeros( (nsim,) )
        oks = np.zeros( (nsim,ndim) )
        for i in range(nsim):
            t = params[i]
            ots[i] = t
            oks[i,:] = kspl.GetValue(t)

        self.sim_ks = oks
        self.sim_ts = ots
        self.vary_simks = False
        self.vary_pathks = False
        for i in range(self.sim_npts):
            self.sim_pts[i,:] = self.pc.GetValue(self.sim_ts[i])
        return self.GetSimMeans(std=True)

        # return PathProps(self.inp_pts,self.path_npts,
        #                  nsim, oks,
        #                  self.denest,T=self.T,
        #                  maxks=self.maxks,minks=self.minks,
        #                  fix0=self.fix0,fix1=self.fix1,
        #                  vary_simks=False,
        #                  vary_pathks=False,
        #                  pathts=self.path_ts,
        #                  simts=ots,
        #                  target_disp=self.target_disp)


    
    
    # def PredictUniformSimForceConsts(self,maxit=10):
    #     import numpy as np
    #     from . PathUtils import PCurve
        
    #     ks = np.array(self.sim_ks,copy=True)
        
    #     tuni = np.linspace(0,1,self.sim_npts)
    #     maxdt = 0.75*tuni[1]
    #     means = np.zeros( self.sim_shape )
    #     for it in range(maxit):
            
    #         for i in range(self.sim_npts):
    #             k = np.array( [ min(self.maxks[d],max(self.minks[d],ks[i,d]))
    #                             for d in range(self.ndim)] )
    #             c = self.pc.GetValue(tuni[i])
    #             means[i,:] = self.denest.GetAvgPos(self.T,k,c)
            
    #         cspl = PCurve(means,fixt=False)

    #         kold=np.array(ks,copy=True)
    #         for i in range(self.sim_npts):
    #             dt = abs( tuni[i] - cspl.t[i] )
    #             scale = dt/maxdt
    #             k = ks[i,:] * scale
    #             k = np.array( [ min(self.maxks[d],max(self.minks[d],k[d]))
    #                             for d in range(self.ndim)] )
    #             ks[i,:] = k[:]
    #             print("%3i  i=%3i tcspl=%7.4f dt=%7.4f maxdt=%7.4f"%(it,i,cspl.t[i],dt,maxdt)
    #                   +" scale=%7.3f"%(scale)
    #                   +" knew= %s"%( " ".join(["%7.2f"%(x) for x in ks[i,:]]))
    #                   +" dk= %s"%( " ".join(["%7.2f"%(x-y) for x,y in zip(ks[i,:],kold[i,:])])))
    #         print("")

    #         knew=np.array(ks,copy=True)
    #         if False:
    #             wo=0.25
    #             wi=1-2*wo
    #             for d in range(self.ndim):
    #                 for i in range(self.sim_npts):
    #                     if i == 0:
    #                         k=(wi+wo)*ks[i,d]+wo*ks[i+1,d]
    #                     elif i == self.path_npts-1:
    #                         k=(wi+wo)*ks[i,d]+wo*ks[i-1,d]
    #                     else:
    #                         k=wo*(ks[i+1,d]+ks[i-1,d])+wi*ks[i,d]
    #                     knew[i,d]=max(knew[i,d],k)

    #         maxdk = np.max( abs(knew-kold) )
    #         ks = knew
    #         if maxdk < 0.1:
    #             break
    #     return ks
    
        

def AkimaDensityStringMethod( denest,
                              path_pts,
                              path_npts,
                              sim_npts,
                              path_ks,
                              tol=1.e-4,
                              maxit=300,
                              fix0=True, fix1=True,
                              vary_pathks=False,
                              vary_simks=False,
                              minks=None, maxks=None,
                              verbose=True):
    """Uses the string method to locate a minimum free energy pathway
    represented by a parametric Akima spline

    Parameters
    ----------
    denest : ndfes.DensityEst
        FES density estimator used to predict the expected locations
        of the reaction coordinates from a biased simulation

    xs : list of list
        The points defining the intial guess at the pathway. The number of
        points does not need to be the same as the number of output points

    npts : int
        The number of output points

    path_ks : numpy.array, dtype=float, shape=(ndim,) or shape(npts,ndim)
        default=None
        The biasing potential force constants used in the minimizations
        If len(ks.shape) == 2 (that is, if ks is a matrix), then it 
        defines the force constants for each window in the path.
        If len(ks.shape) == 1 (that is, if vs is a vector), then it
        defines the force costants of each dimension and each window
        uses the same force constants
        If None is provided, then the path_ks values are spline
        interpolated from the sim_ks values

    tol : float, default=1.e-4
        Stopping tolerance to terminate the string method. If the maximum
        displacement is smaller than the tolerance, then the method stops

    maxit : int, default=300
        Stop the string method even if the tolerance is not met

    fix0 : bool, default=True
        Allow the t=0 endpoint to move

    fix1 : bool, default=True
        Allow the t=1 endpoint to move
    
    varyks : bool, default=False
        If true, then allow the umbrella window force constants to
        change during the path optimization.

    minks : numpy.array, dtype=float, shape=(ndim,)
        The minimum allowable force constant value in each direction
        If not provided, it defaults to 50 kcal/mol/A^2 in each direction
        For periodic dimensions, it defaults to 0.4 kcal/mol/degree

    maxks : numpy.array, dtype=float, shape=(ndim,)
        The maximum allowable force constant value in each direction
        If not provided, it defaults to 300 kcal/mol/A^2 in each direction
        For periodic dimensions, it defaults to 2 kcal/mol/degree

    verbose : bool, default=True
        Print path finding progress to stdout

    Returns
    -------
    pcurve : ndfes.PCurve
        The final parametric spline

    kmat : numpy.array, shape=(npts,ndim)
        The final force constants (note that the spline points can be
        found in pcurve.x)

    paths : list of numpy.array
        The points from each iteration of optimization.
        The size of the list is the number of iterations.
        Each element of the list is a numpy matrix of shape (npts,ndim)
        corresponding to the path points defining a parametric curve.

    means : list of numpy.array
        The centroids of each simulation performed along the path

    stddevs : list of numpy.array
        The centroid standard deviations for each simulation performed
        along the path

    """

    import sys
    import numpy as np
    from . PathUtils import AkimaStringMethodUpdate
    from . PathUtils import PCurve
    import pickle
    import os
    
    ix = np.array(path_pts)

    # paths = []
    # means = []
    # stddevs = []
    paths = []

    #if not os.path.exists("path.pkl"):
    if True:
    
        pprop = PathProps(ix,path_npts, sim_npts, path_ks, denest,
                          maxks=maxks, minks=minks,
                          fix0=fix0,fix1=fix1,
                          vary_simks=False,
                          vary_pathks=False)

        
        conv_path=False
        for it in range(maxit):

            
            vsimks=None
            vpathks=None
            if it > 0:
                dx = max( [ np.linalg.norm(paths[-1].path_pts[i,:]-pprop.path_pts[i,:])
                            for i in range(path_npts) ] )
                print("it: %4i  dx: %12.3e  tol: %12.3e"%(it,dx,tol))
                if dx < tol:
                    conv_path=True
                elif dx < 100*tol:
                    vsimks = vary_simks
                    vpathks = vary_pathks
                
            paths.append(pprop)
            # paths.append(np.array(pprop.path_pts,copy=True))
            # means.append(np.array(pprop.path_means,copy=True))
            # stddevs.append(np.array(pprop.path_stds,copy=True))

            pprop.write(sys.stdout)

            #pprop.PredictUniformSimForceConsts()
        
            if not conv_path:
                pprop = pprop.GetNewPath(vary_simks=vsimks,
                                         vary_pathks=vpathks)
            else:
                break

    #         fh=open("path.pkl","wb")
    #         pickle.dump(pprop,fh)
    #         fh.close()
            
    # else:
    #     fh=open("path.pkl","rb")
    #     pprop = pickle.load(fh)
    #     fh.close()


    return pprop.pc,paths

