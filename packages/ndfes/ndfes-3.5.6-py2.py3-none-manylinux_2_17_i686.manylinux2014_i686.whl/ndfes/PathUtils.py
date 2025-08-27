#!/usr/bin/env python3


def ApproxTFromPts(xs):
    import numpy as np
    npt = xs.shape[0]
    ndim = xs.shape[1]
    ts = np.zeros( (npt,) )
    for i in range(1,npt):
        ts[i] = ts[i-1] + np.linalg.norm( xs[i,:] - xs[i-1,:] )
    ts[:] /= ts[-1]
    return ts

def ApproxTFromSpl(spls,nseg):
    import numpy as np
    ndim = len(spls)
    uts = np.linspace(0,1,nseg)
    xs = np.array( [ [ spl(t) for spl in spls ] for t in uts ] )
    return ApproxTFromPts(xs)


def CptNewTs(ts,xs,nseg):
    import numpy as np
    from scipy.interpolate import Akima1DInterpolator as akima
    from scipy.interpolate import interp1d
    
    SplCtor = lambda t,x: akima(t,x) if x.shape[0]>2 else interp1d(t,x,kind='linear')
    
    ndim = xs.shape[1]
    spls = [ SplCtor(ts,xs[:,dim]) for dim in range(ndim) ]
    
    tin = np.linspace(0,1,nseg)
    tout = ApproxTFromSpl(spls,nseg)
    tspl = interp1d(tin,tout,kind='linear')
    newts = np.array( [ tspl(t) for t in ts ] )
    newts[0] = 0
    newts[-1] = 1
    return newts




class PCurve(object):
    """Defines a parametric curve using Akima splines for each dimension

    Attributes
    ----------
    spls : list of scipy.interpolate.Akima1DInterpolator
        A spline for each dimension that covers t=0 to 1

    x : np.array, shape=(npts,ndim)
        The points that were used to define the splines on a regular grid of
        t-values. These are the points that evenly divide the length of the
        curve, as determined from iterative refinement

    t : np.array, shape=(npts,)
        The progress variable (t=0 to 1) through the parametric curve  

    Methods
    -------
    """
    
    def __init__(self, x, t=None, fixt=False, tol=1.e-8, maxit=100, nseg=1000, linear=False):
        """
        Parameters
        ----------
        x : list of list
             A list of n-dimensional points used to define the parametric
             curve.  These points are used to begin a process of iterative
             refinement, that resamples the parametric curve to find a new
             set of points that evenly divide the length of the curve.

        t : list of float, optional
            If present, then the parametric curve is fully defined by the
            input x and t.  Otherwise, the parametric curve will undergo
            a self-consistent procedure either by updating the input points
            (while fixing the t's to a uniform distribution), or optimizing
            the t-values for a fixed set of points.

        fixt : bool, default=False
            If the t-values are not input, then fixt=False will self-
            consistently choose the t-values for the fixed set of x-values.
            If fixt=True, then the self-consistent procedure will update
            the x-values for a regular grid of t-values. If fixt=False,
            then the parametric curve will pass through the input points;
            however, uniform resampling of the curve and subsequent creation
            of another parametric curve from the sampled points will yield
            a different curve.  Alternatively, if fixt=True, then the
            parametric curve will not pass through the input points, but
            uniform sampling of the parametric curve and subsequent creation
            of another parametric curve from the sampled points will yield
            the same curve.  If you know the proper t-values, then you
            should specify them.  If you don't, then you should use 
            fixt=False.  If you then want a set of uniformly spaced points,
            then uniformly sample from that curve, and create a new curve
            with fixt=True.
        
        tol : double, default=1.e-4
            The stopping tolerance on the iterative refinement. If the norm
            between the new and old set of t-values is less than tol, then 
            the iterative refinement terminates.

        maxit : int, default=50
            The maximum number of iterations in the iterative refinement.

        nseg : int, default=1000
            The number of linear segments used to approximate the length
            of the parametric curve.

        linear : bool, default=False
            If True, use a piecewise linear path. Default is Akima
        """
        
        import numpy as np
        from scipy.interpolate import Akima1DInterpolator as akima
        from scipy.interpolate import interp1d

        
        x_fixed = np.array(x)
        ndim = x_fixed.shape[1]

        
        SplCtor = lambda t,x: akima(t,x) if (x.shape[0]>2 and not linear) else interp1d(t,x,kind='linear')
        

        if t is not None:
            t_fixed = np.array(t)
            spls = [ SplCtor(t_fixed,x_fixed[:,i]) for i in range(ndim) ]
        else:

            if not fixt and linear:

                ts = ApproxTFromPts( x_fixed )
                spls = [ SplCtor(ts,x_fixed[:,i]) for i in range(ndim) ]
                t_fixed = np.array(ts,copy=True)

            elif not fixt:

                mynseg = nseg
                maxnseg = 16*nseg
                npts = x_fixed.shape[0]
                ts = ApproxTFromPts( x_fixed )
                tnew = np.array(ts,copy=True)

                
                
                #print(ts)
                #print(ts[1:]-ts[:-1])
                spls = [ SplCtor(ts,x_fixed[:,i]) for i in range(ndim) ]
                
                for it in range(maxit):
                    tnew = CptNewTs(ts,x_fixed,mynseg)
                    bad=False
                    for i in range(1,npts):
                        #print(i,tnew[i]-tnew[i-1])
                        if abs(tnew[i]-tnew[i-1]) < 1.e-6:
                            bad=True
                    if bad:
                        if mynseg < maxnseg:
                            mynseg *= 2
                            tnew = CptNewTs(ts,x_fixed,mynseg)
                            bad=False
                            for i in range(1,npts):
                                if abs(tnew[i]-tnew[i-1]) < 1.e-8:
                                    bad=True
                            if bad:
                                break
                    err = np.linalg.norm(ts-tnew)
                    #print("it=%5i nseg=%5i"%(it,mynseg),)
                    #for i in range(1,npts):
                    #    print(
                    ts[:] = tnew[:]
                    spls = [ SplCtor(ts,x_fixed[:,i]) for i in range(ndim) ]
                    #print(it,err,mynseg)
                    if err < tol:
                        break
                t_fixed = np.array(ts,copy=True)
                spls = [ SplCtor(ts,x_fixed[:,i]) for i in range(ndim) ]

                # print("\n")
                # for i,t in enumerate(t_fixed):
                #     print("%4i %17.8e %s"%(i,t," ".join(["%17.8f"%(x) for x in x_fixed[i,:]])))
                # print("\n")


            else:
                
                t_fixed = np.linspace(0,1,x_fixed.shape[0])
                spls = [ SplCtor(t_fixed,x_fixed[:,i]) for i in range(ndim) ]
        
                t_seg = np.linspace(0,1,nseg)
                l_seg = np.zeros( (nseg,) )
        
                for it in range(maxit):

                    x_seg = np.array([ [spl(t) for spl in spls] for t in t_seg ])
                    x_seg[0] = x_fixed[0]
                    x_seg[-1] = x_fixed[-1]
                    
                    l_seg[:] = 0.
                    for i in range(1,nseg):
                        dx = np.linalg.norm(x_seg[i]-x_seg[i-1])
                        l_seg[i] = l_seg[i-1] + dx

                        l_seg /= l_seg[-1]
                        #tspl = akima( t_seg, l_seg )                
                        #t_fixed_new = tspl( t_fixed )

                
                        tspl = SplCtor( l_seg, t_seg )                
                        t_fixed_new = tspl( t_fixed )
                        t_fixed_new[0] = 0
                        t_fixed_new[-1] = 1
                        
                        ihis = np.searchsorted( l_seg, t_fixed, side='right' )
                        for i,t in enumerate(t_fixed):
                            ihi=min(max(ihis[i],1),nseg-1)
                            ilo=ihi-1
                            lhi=l_seg[ihi]
                            llo=l_seg[ilo]
                            w = (t - llo)/(lhi-llo)
                            l = (1-w)*t_seg[ilo] + w*t_seg[ihi]
                            t_fixed_new[i] = l
                        t_fixed_new[0] = 0
                        t_fixed_new[-1] = 1
                    
                        dt = np.linalg.norm(t_fixed_new-t_fixed)
                    
                        x0 = x_fixed[0]
                        x1 = x_fixed[-1]
                        x_fixed = np.array([ [spl(t) for spl in spls] for t in t_fixed_new ])
                        x_fixed[0] = x0
                        x_fixed[-1] = x1
                        spls = [ SplCtor(t_fixed,x_fixed[:,i])
                                 for i in range(ndim) ]

                    if dt < tol:
                        break

        self.x = x_fixed
        self.t = t_fixed
        self.spls = spls
            
            
    def GetValue(self,t,nu=0,extrapolate=False):
        """
        Evaluate the parametric curve at the specified t-value. Values
        outside of the range t=[0,1] will return values at the boundary,
        as it is presumbed that this will only occur due to numerical
        precision errors.

        Parameters
        ----------
        t : float
            The parametric coordinate

        nu : int, default=0
            The order of the derivative

        extrapolate : bool, default=False
            Whether to extrapolate past the ends

        Returns
        -------
        vals : numpy.ndarray, shape=(ndim,)
            The coordinate at the specified t-value
        """

        import numpy as np
        tval = t
        if not extrapolate:
            tval = min(max(t,self.t[0]),self.t[-1])
            
        if nu == 0:
            if extrapolate and len(self.t) > 2:
                return np.array( [ spl(tval,extrapolate=extrapolate) for spl in self.spls ] )
            else:
                return np.array( [ spl(tval) for spl in self.spls ] )
        elif len(self.t) > 2:
            return np.array( [ spl(tval,nu=nu,extrapolate=extrapolate) for spl in self.spls ] )
        elif nu == 1:
            return (self.x[1,:]-self.x[0,:]) / (self.t[1]-self.t[0])
        elif nu > 1:
            return np.zeros( (len(self.spls),) )
        else:
            raise Exception("Antiderivatives of linear spline not implemented")

    def GetError(self,t):
        import numpy as np
        return np.zeros( (self.x.shape[1],) )

    def MakeLinear(self):
        return PCurve( self.x, fixt=False, linear=True )
    
    
    
class PGPRCurve(object):
    """Defines a parametric curve using Gaussian Process Regression for each
    dimension

    Attributes
    ----------
    spls : list of ndfes.GPR objects
        A spline for each dimension that covers t=0 to 1

    x : np.array, shape=(npts,ndim)
        The points that were used to define the splines on a regular grid of
        t-values. These are the points that evenly divide the length of the
        curve, as determined from iterative refinement

    dx : np.array, shape=(npts,ndim) or None
        The error of each point in each dimension 

    t : np.array, shape=(npts,)
        The progress variable (t=0 to 1) through the parametric curve  

    Methods
    -------
    """
    
    def __init__(self, x, dx=None, t=None,
                 n_restarts_optimizer=30,
                 normalize_y=True,
                 extra_error=0,
                 sigma_fit_tol=1000,
                 rbf_val=1.0,
                 rbf_val_min=1.e-3,
                 rbf_val_max=1.e+5,
                 const_val=1.0,
                 const_val_min=1.e-4,
                 const_val_max=1.e+4 ):
        """
        Parameters
        ----------
        x : numpy.array, shape=(npts,ndim)
            The sampled data used to perform the fit
    
        dx : numpy.array, shape=(npts,dim), optional
            The sample standard deviations in each direction

        t : numpy.array, shape=(npts,), optional
            The parametric curve percentages of each point. If unspecified,
            the t-values are calculated from a ndfes.PCurve with fixt=False;
            that is, the t-values are estimated by iteratively updating them
            until they are consistent with the length percentage of the curve
            for the fixed set of x-values

        n_restarts_optimizer : int, default=30
            The number of restarts of the optimizer for finding the kernel’s
            parameters which maximize the log-marginal likelihood.

        normalize_y : bool, default=True
            Whether or not to normalized the target values y by removing the
            mean and scaling to unit-variance. This is recommended for cases
            where zero-mean, unit-variance priors are used.

        extra_error : float, default=0
            Value added to the diagonal of the kernel matrix during fitting. 
            This can prevent a potential numerical issue during fitting, by 
            ensuring that the calculated values form a positive definite 
            matrix. It can also be interpreted as the variance of additional
            Gaussian measurement noise on the training observations.  Setting
            alpha to a nonzero number is the same as adding sqrt(alpha) to each
            element of the dy array.

        sigma_fit_tol : float, default=1000
            If the GPR fit does not match the points to within 
            y +/- (dy * sigma_fit_tol), then reperform the GPR fit with
            reduced errors for those points that were too far away from
            the input. This is an iterative procedure, so it can potentially
            be very expensive.  The default value was chosen such that
            the first iteration would be necessary under normal circumstances

        rbf_val : float or numpy.array with shape=(ndim,), default=1.0
            Initial value of the RBF length_scale parameter. If a float, 
            an isotropic kernel is used. If an array, an anisotropic kernel
            is used where each dimension of l defines the length-scale of 
            the respective feature dimension

        rbf_val_min : float, default=1.e-3
            Lower bound of the RBF length_scale parameter

        rbf_val_max : float, default=1.e+5
            Upper bound of the RBF length_scale parameter

        const_val : float, default=1.0
            Initial value of the constant kernel parameter

        const_val_min : float, default=1.e-4
            Lower bound of the constant kernel parameter

        const_val_max : float, default=1.e+4
            Upper bound of the constant kernel parameter

        """

        import numpy as np
        from . GPR import GPR
        
        x = np.array(x)
        ndim = x.shape[1]
        
        if t is None:
            pc = PCurve(x,fixt=False)
            t = pc.t
        else:
            t = np.array(t)

        if dx is not None:
            dx = np.array(dx)
            
        spls = [ GPR( t, x[:,i], dy=dx[:,i],
                      n_restarts_optimizer=n_restarts_optimizer,
                      normalize_y=normalize_y,
                      extra_error=extra_error,
                      sigma_fit_tol=sigma_fit_tol,
                      rbf_val=rbf_val,
                      rbf_val_min=rbf_val_min,
                      rbf_val_max=rbf_val_max,
                      const_val=const_val,
                      const_val_min=const_val_min,
                      const_val_max=const_val_max )
                 for i in range(ndim) ]

        self.x=x
        self.t=t
        self.dx=dx
        self.spls = spls


    def GetValue(self,t):
        """
        Evaluate the parametric curve at the specified t-value. 

        Parameters
        ----------
        t : float
            The parametric coordinate

        Returns
        -------
        list
            The coordinate at the specified t-value
        """

        import numpy as np
        return np.array( [ spl.GetValues([t],
                                         return_std=False,
                                         return_deriv=False).values[0]
                           for spl in self.spls ] )

    
    def GetError(self,t):
        """
        Evaluate the GPR errors at the specified t-value.

        Parameters
        ----------
        t : float
            The parametric coordinate

        Returns
        -------
        list
            The coordinate at the specified t-value
        """

        import numpy as np
        return np.array( [ spl.GetValues([t],
                                         return_std=True,
                                         return_deriv=False).errors[0]
                           for spl in self.spls ] )
    
    

def AkimaStringMethodUpdate( num_output_pts, input_pts,
                             scf=False, tol=1.e-8, maxit=100, nseg=1000 ):
    """
    Given a set of input points, return a set of output points that
    uniformly sample an Akima spline parametric curve

    Parameters
    ----------
    num_output_pts : int
        The number of uniformly sampled points

    inputs_pts : list of list
        The list of N-dimensional points used to construct the parametric
        spine.  The output points will not pass through the input points
        even when num_output_pts = len(input_pts) unless the input points
        are already uniformly spaced or scf=True
        
    scf : bool, default=False
        If True, then self-consistently solve for the uniform set of points,
        otherwise, uniformly sample the curve that passes through the input
        set of points.  If the input set of points are uniformly spaced, then
        the result is self-consistent without the need for performing a 
        self-consistent procedure

    tol : double, default=1.e-4
        The stopping tolerance on the iterative refinement. If the norm
        between the new and old set of t-values is less than tol, then 
        the iterative refinement terminates.

    maxit : int, default=50
        The maximum number of iterations in the iterative refinement.

    nseg : int, default=1000
        The number of linear segments used to approximate the length
        of the parametric curve.
    """

    import numpy as np
    
    #
    # Determine the self-consistent set of t-values for these points
    #
    pc = PCurve( input_pts, fixt = False,
                 tol=tol, maxit=maxit, nseg=nseg )

    #
    # Uniformly sample the parametric curve
    #
    uniform_pts = [ pc.GetValue(t) for t in np.linspace(0,1,num_output_pts) ]
    #print(uniform_pts)
    if scf:
        #
        # Determine the self-consistent set of pts for uniform t-values
        #
        pc = PCurve( uniform_pts, fixt = True,
                     tol=tol, maxit=maxit, nseg=nseg )
        
        #
        # Return the self-consistent pts
        #
        uniform_pts = pc.x
        
    return np.array(uniform_pts)



def PGPRStringMethodUpdate( num_output_pts, input_pts,
                            dx=None,
                            n_restarts_optimizer=30,
                            normalize_y=True,
                            extra_error=0,
                            sigma_fit_tol=1000,
                            rbf_val=1.0,
                            rbf_val_min=1.e-3,
                            rbf_val_max=1.e+5,
                            const_val=1.0,
                            const_val_min=1.e-4,
                            const_val_max=1.e+4 ):
    """
    Given a set of input points, return a set of output points that
    uniformly sample an Akima spline parametric curve

    Parameters
    ----------
    num_output_pts : int
        The number of uniformly sampled points

    inputs_pts : list of list
        The list of N-dimensional points used to construct the parametric
        spine.  The output points will not pass through the input points
        even when num_output_pts = len(input_pts) unless the input points
        are already uniformly spaced or scf=True

    dx : numpy.array, shape=(npts,dim), optional
        The sample standard deviations in each direction

    n_restarts_optimizer : int, default=30
        The number of restarts of the optimizer for finding the kernel’s
        parameters which maximize the log-marginal likelihood.

    normalize_y : bool, default=True
        Whether or not to normalized the target values y by removing the
        mean and scaling to unit-variance. This is recommended for cases
        where zero-mean, unit-variance priors are used.

    extra_error : float, default=0
        Value added to the diagonal of the kernel matrix during fitting. 
        This can prevent a potential numerical issue during fitting, by 
        ensuring that the calculated values form a positive definite 
        matrix. It can also be interpreted as the variance of additional
        Gaussian measurement noise on the training observations.  Setting
        alpha to a nonzero number is the same as adding sqrt(alpha) to each
        element of the dy array.

    sigma_fit_tol : float, default=1000
        If the GPR fit does not match the points to within 
        y +/- (dy * sigma_fit_tol), then reperform the GPR fit with
        reduced errors for those points that were too far away from
        the input. This is an iterative procedure, so it can potentially
        be very expensive.  The default value was chosen such that
        the first iteration would be necessary under normal circumstances

    rbf_val : float or numpy.array with shape=(ndim,), default=1.0
        Initial value of the RBF length_scale parameter. If a float, 
        an isotropic kernel is used. If an array, an anisotropic kernel
        is used where each dimension of l defines the length-scale of 
        the respective feature dimension

    rbf_val_min : float, default=1.e-3
        Lower bound of the RBF length_scale parameter

    rbf_val_max : float, default=1.e+5
        Upper bound of the RBF length_scale parameter
    
    const_val : float, default=1.0
        Initial value of the constant kernel parameter

    const_val_min : float, default=1.e-4
        Lower bound of the constant kernel parameter

    const_val_max : float, default=1.e+4
        Upper bound of the constant kernel parameter

    """

    import numpy as np
    
    #
    # Determine the self-consistent set of t-values for these points
    #
    pc = PGPRCurve( input_pts, dx=dx,
                    n_restarts_optimizer=n_restarts_optimizer,
                    normalize_y=normalize_y,
                    extra_error=extra_error,
                    sigma_fit_tol=sigma_fit_tol,
                    rbf_val=rbf_val,
                    rbf_val_min=rbf_val_min,
                    rbf_val_max=rbf_val_max,
                    const_val=const_val,
                    const_val_min=const_val_min,
                    const_val_max=const_val_max )

    #
    # Uniformly sample the parametric curve
    #
    uniform_pts = [ pc.GetValue(t) for t in np.linspace(0,1,num_output_pts) ]

    return np.array(uniform_pts)





def statisticalInefficiency(A_n, B_n=None, fast=False, mintime=3, fft=False):
    """Compute the (cross) statistical inefficiency of (two) timeseries.

    Parameters
    ----------
    A_n : np.ndarray, float
        A_n[n] is nth value of timeseries A.  Length is deduced from vector.

    B_n : np.ndarray, float, optional, default=None
        B_n[n] is nth value of timeseries B.  Length is deduced from vector.
        If supplied, the cross-correlation of timeseries A and B will be 
        estimated instead of the autocorrelation of timeseries A.  

    fast : bool, optional, default=False
        If True, will use faster (but less accurate) method to estimate 
        correlation time, described in Ref. [1] (default: False).  This is 
        ignored when B_n=None and fft=True.

    mintime : int, optional, default=3
        minimum amount of correlation function to compute (default: 3)
        The algorithm terminates after computing the correlation time out to 
        mintime when the correlation function first goes negative.  Note that
        this time may need to be increased if there is a strong initial 
        negative peak in the correlation function.

    fft : bool, optional, default=False
        If fft=True and B_n=None, then use the fft based approach, as
        implemented in statisticalInefficiency_fft().

    Returns
    -------
    g : np.ndarray,
        g is the estimated statistical inefficiency (equal to 1 + 2 tau, 
        where tau is the correlation time). We enforce g >= 1.0.

    Notes
    -----
    The same timeseries can be used for both A_n and B_n to get the 
    autocorrelation statistical inefficiency. The fast method described 
    in Ref [1] is used to compute g.

    References
    ----------
    [1] J. D. Chodera, W. C. Swope, J. W. Pitera, C. Seok, and K. A. Dill. 
        Use of the weighted histogram analysis method for the analysis of 
        simulated and parallel tempering simulations. JCTC 3(1):26-41, 2007.

    Examples
    --------

    Compute statistical inefficiency of timeseries data with known correlation
    time.  

    >>> from pymbar.testsystems import correlated_timeseries_example
    >>> A_n = correlated_timeseries_example(N=100000, tau=5.0)
    >>> g = statisticalInefficiency(A_n, fast=True)

    """

    import numpy as np
    
    # Create numpy copies of input arguments.
    A_n = np.array(A_n)

    if fft and B_n is None:
        raise Exception("fft version not implemented")

    if B_n is not None:
        B_n = np.array(B_n)
    else:
        B_n = np.array(A_n)

    # Get the length of the timeseries.
    N = A_n.size

    # Be sure A_n and B_n have the same dimensions.
    if(A_n.shape != B_n.shape):
        raise Exception('A_n and B_n must have same dimensions.')

    # Initialize statistical inefficiency estimate with uncorrelated value.
    g = 1.0

    # Compute mean of each timeseries.
    mu_A = A_n.mean()
    mu_B = B_n.mean()

    # Make temporary copies of fluctuation from mean.
    dA_n = A_n.astype(np.float64) - mu_A
    dB_n = B_n.astype(np.float64) - mu_B

    # Compute estimator of covariance of (A,B) using estimator that will
    # ensure C(0) = 1.
    sigma2_AB = (dA_n * dB_n).mean()  # standard estimator to ensure C(0) = 1

    #print("N,sig2",N,sigma2_AB)
    
    # Trap the case where this covariance is zero, and we cannot proceed.
    if(sigma2_AB == 0):
        raise Exception('Sample covariance sigma_AB^2 = 0 -- cannot compute statistical inefficiency')

    # Accumulate the integrated correlation time by computing the normalized
    # correlation time at increasing values of t.  Stop accumulating if the
    # correlation function goes negative, since this is unlikely to occur
    # unless the correlation function has decayed to the point where it is
    # dominated by noise and indistinguishable from zero.
    t = 1
    increment = 1
    while (t < N - 1):

        # compute normalized fluctuation correlation function at time t
        C = np.sum(dA_n[0:(N - t)] * dB_n[t:N] +
                   dB_n[0:(N - t)] * dA_n[t:N]) / (2.0 * float(N - t) * sigma2_AB)
        # Terminate if the correlation function has crossed zero and we've
        # computed the correlation function at least out to 'mintime'.
        if (C <= 0.0) and (t > mintime):
            break

        # Accumulate contribution to the statistical inefficiency.
        g += 2.0 * C * (1.0 - float(t) / float(N)) * float(increment)

        # Increment t and the amount by which we increment t.
        t += increment

        # Increase the interval if "fast mode" is on.
        if fast:
            increment += 1

    # g must be at least unity
    if (g < 1.0):
        g = 1.0

    # Return the computed statistical inefficiency.
    return g



def CptMeanAndError(v):
    """Computes the mean and standard error of a vector with consideration of
    correlation. The standard error is approximated as sqrt( s^2 / Neff ),
    where Neff = N/g, N is the number of samples, g is the statistical
    inefficiency, and s^2 is the variance of the sample; e.g.,
    s^2 = (1/(N-1)) * \sum_i^N (v[i]-mean)^2 

    Parameters
    ----------
    v : numpy.array, shape=(N,)
        Array of samples

    Returns
    -------
    avg : float
        The mean of the samples

    err : float
        The standard error of the mean
    """
    
    import numpy as np

    # if False:
    #     g = statisticalInefficiency(v)
    #     inc = int(g+0.5)
    #     avg = np.mean(v)
    #     vsig = v[::inc]
    #     err = np.sqrt(np.var(vsig,ddof=1)/vsig.shape[0])
    # elif False:
    #     avg = np.mean(v)
    #     err = GetBlockBootstrapErr(v)
    # else:
    
    g = statisticalInefficiency(v)
    n = v.shape[0]
    avg = np.mean(v)
    err = np.sqrt( np.var(v,ddof=1) * (g/n) )
        
    return avg,err



def CptCrdMeanAndError(crd):
    """Computes the mean and standard error of each dimension in a time-series
    of coordinates with consideration of correlation.  The standard error of
    each dimension is sqrt( s^2 / Neff ), where s^2 is the variance of the
    samples in the dimension and Neff = N/g, where N is the number of samples
    and g is the maximum statistical inefficiency of any dimension.

    Parameters
    ----------
    crd : numpy.array, shape=(N,ndim)
        Array of samples

    Returns
    -------
    avg : numpy.array, shape=(ndim,)
        The mean of the samples for each dimension

    err : numpy.array, shape=(ndim,)
        The standard error of the mean for each dimension
    """
    
    import numpy as np

    crd = np.array(crd)
    ndim = crd.shape[1]

    # if False:
    #     g = max( [statisticalInefficiency(crd[:,idim])
    #               for idim in range(ndim)] )
    #     if g > crd.shape[0]/2:
    #         g = crd.shape[0]/4
    #     inc = int(g+0.5)
    #     crdsig = crd[::inc,:]
    #     n = crdsig.shape[0]
    #     avg = np.array( [np.mean(crd[:,idim])
    #                      for idim in range(ndim)] )
    #     err = np.array( [np.sqrt(np.var(crdsig[:,idim],ddof=1)/n)
    #                      for idim in range(ndim)] )
    # elif False:
    #     avg = np.array( [np.mean(crd[:,idim])
    #                      for idim in range(ndim)] )
    #     err = GetCrdBlockBootstrapErr(crd)
    # else:
    
    n = crd.shape[0]
        
    g = max( [statisticalInefficiency(crd[:,idim])
              for idim in range(ndim)] )
        
    avg = np.array( [np.mean(crd[:,idim])
                     for idim in range(ndim)] )

    err = np.array( [np.sqrt(np.var(crd[:,idim],ddof=1) * (g/n))
                     for idim in range(ndim)] )
    
    return avg,err



def GetCrdMeanAndErrorFromFile(fname,cols):
    """Reads the selected columns from a text file and returns the mean and
    standard error of each column.

    Parameters
    ----------
    fname : str
        filename of a tabular text file

    cols : list of int
        The column indexes to be extracted from the table. The length of the
        list is ndim, which defines the sizes of the output arrays.  The 
        indexes are zero-based; e.g., column 0 is the first column.

    Results
    -------
    avgs : numpy.array, shape=(ndim,)
        The column averages

    errs : numpy.array, shape=(ndim,)
        The standard error of the means
    """
    
    import numpy as np
    return CptCrdMeanAndError( np.loadtxt(fname)[:,cols] )

    

def ReadDumpavesAsPGPR( dumpaves, cols,
                        n_restarts_optimizer=30,
                        normalize_y=True,
                        extra_error=0,
                        sigma_fit_tol=1000,
                        rbf_val=1.0,
                        rbf_val_min=1.e-3,
                        rbf_val_max=1.e+5,
                        const_val=1.0,
                        const_val_min=1.e-4,
                        const_val_max=1.e+4 ):
    """Reads selected columns from a series of files and uses the column means
    and standard errors to construct a parametric gaussian process regression
    curve.

    Parameters
    ----------
    dumpaves : list of str
        The filenames that contain the umbrella window simulations along the
        path.  The first file in the list corresponds to t=0 and the last
        file is t=1.

    cols : list of int
        The columns corresponding to the collective variables of interest. The
        length of the cols array is the dimensionality of the FES. The indexes
        are zero-based; e.g., the first column in the file is index 0.

    
    n_restarts_optimizer : int, default=30
        The number of restarts of the optimizer for finding the kernel’s
        parameters which maximize the log-marginal likelihood.

    normalize_y : bool, default=True
        Whether or not to normalized the target values y by removing the
        mean and scaling to unit-variance. This is recommended for cases
        where zero-mean, unit-variance priors are used.

    extra_error : float, default=0
        Value added to the diagonal of the kernel matrix during fitting. 
        This can prevent a potential numerical issue during fitting, by 
        ensuring that the calculated values form a positive definite 
        matrix. It can also be interpreted as the variance of additional
        Gaussian measurement noise on the training observations.  Setting
        alpha to a nonzero number is the same as adding sqrt(alpha) to each
        element of the dy array.

    sigma_fit_tol : float, default=1000
        If the GPR fit does not match the points to within 
        y +/- (dy * sigma_fit_tol), then reperform the GPR fit with
        reduced errors for those points that were too far away from
        the input. This is an iterative procedure, so it can potentially
        be very expensive.  The default value was chosen such that
        the first iteration would be necessary under normal circumstances

    rbf_val : float or numpy.array with shape=(ndim,), default=1.0
        Initial value of the RBF length_scale parameter. If a float, 
        an isotropic kernel is used. If an array, an anisotropic kernel
        is used where each dimension of l defines the length-scale of 
        the respective feature dimension

    rbf_val_min : float, default=1.e-3
        Lower bound of the RBF length_scale parameter

    rbf_val_max : float, default=1.e+5
        Upper bound of the RBF length_scale parameter

    const_val : float, default=1.0
        Initial value of the constant kernel parameter

    const_val_min : float, default=1.e-4
        Lower bound of the constant kernel parameter

    const_val_max : float, default=1.e+4
        Upper bound of the constant kernel parameter

    Returns
    -------
    pc : PGPRCurve
        The parametric spline of the path

    """
    
    import numpy as np
    
    xs=[]
    es=[]
    for dumpave in dumpaves:
        avg,err = GetCrdMeanAndErrorFromFile(dumpave,cols)
        #err[:] = 0.
        xs.append(avg)
        es.append(err)

        
    xs=np.array(xs)
    es=np.array(es)

    pc = PGPRCurve( xs,dx=es, 
                    n_restarts_optimizer=n_restarts_optimizer,
                    normalize_y=normalize_y,
                    extra_error=extra_error,
                    sigma_fit_tol=sigma_fit_tol,
                    rbf_val=rbf_val,
                    rbf_val_min=rbf_val_min,
                    rbf_val_max=rbf_val_max,
                    const_val=const_val,
                    const_val_min=const_val_min,
                    const_val_max=const_val_max )
    
    return pc


def ReadDumpavesAsPCurve( dumpaves, cols, fixt=False ):
    """Reads selected columns from a series of files and uses the column means
    ato construct a parametric Akima spline of the path.

    Parameters
    ----------
    dumpaves : list of str
        The filenames that contain the umbrella window simulations along the
        path.  The first file in the list corresponds to t=0 and the last
        file is t=1.

    cols : list of int
        The columns corresponding to the collective variables of interest. The
        length of the cols array is the dimensionality of the FES. The indexes
        are zero-based; e.g., the first column in the file is index 0.

    fixt : bool, default=False
        If fixt=False, then the spline t-values are optimized while fixing
        the input positions. If it is true, then the t-values are fixed to
        a uniform spacing and the spline positions are optimized to self
        consistency.
    
    Returns
    -------
    pc : PCurve
        A parametric Akima spline of the path

    """
    
    xs=[]
    for dumpave in dumpaves:
        avg,err = GetCrdMeanAndErrorFromFile(dumpave,cols)
        xs.append(avg)
        
    pc = PCurve( xs, fixt=fixt )
    
    return pc


