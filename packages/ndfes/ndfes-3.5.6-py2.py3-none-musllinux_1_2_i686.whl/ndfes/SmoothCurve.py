#!/usr/bin/env python3


def SmoothCurve_IterWinAvg(x0,nmin,nmax,smoothness,endpt_error_damping):
    """Smoothes a sequence of parametric points by iterative window averaging.
    One would generally prefer to use SmoothCurve_IterReflectedAvg over this
    routine.

    Parameters
    ----------
    x0 : numpy.ndarray, shape=(npt,ndim)
        The points along a parametric curve. These points may contain some
        numerical noise.

    nmin : int
        The minimum length of the windowed average. This must be an odd number
        greater than or equal to 3. Recommended: 3.

    nmax : int
        The maximum length of the windowed average. This must be an odd number
        greater than or equal to 3. If wlen=3, then the result is a windowed
        average that will "cut corners".  Setting wlen=5 or larger will help
        to alleviate the corner cutting. Recommended 7, 9, or 11.

    smoothness : float
        Smoothing percentage. If the value is 0, then the windowed average
        is performed with weights equal to zero except the central point
        which has a weight of 1.  If the value is 1, then the weights are
        uniform.  Intermediate values linearly switch between these limits.

    endpt_error_damping : bool
        If True, then the error of the first and last (n-1)/2 points are
        assumed to be zero as n increases from nmin to nmax.

    Returns
    -------
    xnew : numpy.ndarray, shape=(npt,ndim)
        The points after smoothing as been applied.
    """
    import numpy as np
    
    N = x0.shape[0]
    if nmin % 2 == 0:
        nmin -= 1
    if nmin < 3:
        nmin = 3
    nmax = max(min(N,nmax),nmin)
    if nmax%2 == 0:
        nmax -= 1
    nmax = max(nmin,nmax)
    xnew = np.zeros( x0.shape )
    it0 = (nmin-1)//2
    itN = (nmax-1)//2
    
    for it,ii in enumerate(range(it0,itN+1)):
        wlen = 2*ii+1
        err = x0-xnew
        #if it > 0:
        #    err *= wlen/nmax
        #print(f"it {it} {wlen} {smoothness}")

        
        if it > 0 and endpt_error_damping:
            for k in range(ii):
                err[k] = 0
                err[N-1-k] = 0
        
        dx = SmoothCurve_WinAvg( err, wlen, smoothness )
        
        # if it > 0:
        #     for k in range(ii):
        #         print(it,wlen,k)
        #         dx[k] = 0
        #         dx[N-1-k] = 0
                
        xnew += dx
    return xnew



def ReflectCurve(x):
    import numpy as np
    N = x.shape[0]
    ndim = x.shape[1]
    nmid = N-2
    mid = np.flip( x[1:-1,:], 0 )
    o = np.zeros( (nmid+N+nmid,ndim) )
    F = x[0,:]
    L = x[-1,:]
    o[:nmid,:] = F - (mid-F)
    o[nmid:nmid+N,:] = x[:,:]
    o[nmid+N:,:] = L - (mid-L)
    return o


def SmoothCurve_IterReflectedAvg(x0,nmin,nmax,smoothness):
    """Smoothes a sequence of parametric points by iterative window averaging
    upon reflecting the data around the endpoints. This is the preferred
    routine for smoothing data.

    Parameters
    ----------
    x0 : numpy.ndarray, shape=(npt,ndim)
        The points along a parametric curve. These points may contain some
        numerical noise.

    nmin : int
        The minimum length of the windowed average. This must be an odd number
        greater than or equal to 3. Recommended: 3.

    nmax : int
        The maximum length of the windowed average. This must be an odd number
        greater than or equal to 3. If wlen=3, then the result is a windowed
        average that will "cut corners".  Setting wlen=5 or larger will help
        to alleviate the corner cutting. Recommended 7, 9, or 11.

    smoothness : float
        Smoothing percentage. If the value is 0, then the windowed average
        is performed with weights equal to zero except the central point
        which has a weight of 1.  If the value is 1, then the weights are
        uniform.  Intermediate values linearly switch between these limits.

    Returns
    -------
    xnew : numpy.ndarray, shape=(npt,ndim)
        The points after smoothing as been applied.
    """
    import numpy as np
    
    N = x0.shape[0]
    Ndim = x0.shape[1]
    nmid = N-2
    if nmin % 2 == 0:
        nmin -= 1
    if nmin < 3:
        nmin = 3
    nmax = max(min(N,nmax),nmin)
    if nmax%2 == 0:
        nmax -= 1
    nmax = max(nmin,nmax)
    it0 = (nmin-1)//2
    itN = (nmax-1)//2


    X0 = ReflectCurve( x0 )
    xnew = np.zeros( x0.shape )


    # fh = open("refl.dat","w")
    # for i in range(X0.shape[0]):
    #     fh.write("%3i %s\n"%( i-nmid, " ".join(["%14.5e"%(z) for z in X0[i,:]])))
    # fh.write("\n")
    # for i in range(x0.shape[0]):
    #     fh.write("%3i %s\n"%( i, " ".join(["%14.5e"%(z) for z in x0[i,:]])))
    # fh.close()
    # exit(0)
    
    frac = 1
    for it,ii in enumerate(range(it0,itN+1)):
        wlen = 2*ii+1
        Xnew = ReflectCurve( xnew )
        err = X0-Xnew
        dX = SmoothCurve_WinAvg( frac * err, wlen, smoothness )
        dx = dX[nmid:nmid+N,:]
        #print(" ".join(["%11.2e,%11.2e"%(y[0],y[1]) for y in dx]))
        xnew += dx
        xnew[0,:] = x0[0,:]
        xnew[-1,:] = x0[-1,:]
        if it > 1:
            frac *= 0.5
    return xnew



def SmoothCurve_WinAvg(x0,wlen,smoothness):
    """Smoothes a sequence of parametric points by a single windowed average.

    Parameters
    ----------
    x0 : numpy.ndarray, shape=(npt,ndim)
        The points along a parametric curve. These points may contain some
        numerical noise.

    wlen : int
        The length of the windowed average. This must be an odd number
        greater than or equal to 3.

    smoothness : float
        Smoothing percentage. If the value is 0, then the windowed average
        is performed with weights equal to zero except the central point
        which has a weight of 1.  If the value is 1, then the weights are
        uniform.  Intermediate values linearly switch between these limits.

    Returns
    -------
    xnew : numpy.ndarray, shape=(npt,ndim)
        The points after smoothing as been applied.
    """
    import numpy as np
    
    N = x0.shape[0]
    sidxs, sfact = GetSmoothingIdxs( N, wlen, smoothness )
    #for i in range(N):
    #    print("idx %2i %s"%(i," ".join(["%5i"%(x) for x in sidxs[i]])))
    #    print("wts %2i %s"%(i," ".join(["%5.2f"%(x) for x in sfact[i]])))
    return ApplySmoothing( x0, sidxs, sfact )



def GetSmoothingIdxs( N, wlen, smoothness=1 ):
    """Determines the weights and indexes of the points to perform a 
    windowed average.

    Parameters
    ----------
    N : int
        The number of points in the parametric curve

    wlen : int
        The length of the windowed average. This must be an odd number
        greater than or equal to 3.

    smoothness : float, default=1.
        Smoothing percentage. If the value is 0, then the windowed average
        is performed with weights equal to zero except the central point
        which has a weight of 1.  If the value is 1, then the weights are
        uniform.  Intermediate values linearly switch between these limits.
        
    Returns
    -------
    sidxs : list of list of int
        The indexes of points contributing to each average. The slow-index
        is the number points in the parametric curve, len(sidxs) = N.
        The fast index includes the petite set of point indexes that
        contribute to the weighted average.

    sfact : list of list of float
        The weights of each point contributing to each average. The
        slow-index is the number points in the parametric curve, 
        len(sidxs) = N. The fast index is the contribution of a point
        to the average.
    """
    import numpy as np
    
    if wlen%2 == 0:
        raise Exception("length of window average must be odd")
    
    smoothness = min(1,max(0,smoothness))

    #N = xs.shape[0]
    sidxs = [ [] for i in range(N) ]
    sfact = [ [] for i in range(N) ]

    for i in range(N):
        small = i < wlen // 2
        big = (N-1)-i < wlen // 2
        if small:
            mlen = 2*i+1
        elif big:
            mlen = 2*((N-1)-i) + 1
        else:
            mlen = wlen
        mwidth = (mlen-1)//2
        pN = 0
        if mlen > 1:
            wt = smoothness
            myp = (wt)*(1/mlen) + (1-wt)*(1)
            pN = (1-myp)/(mlen-1)
            for j in range(i-mwidth,i+mwidth+1):
                p = pN
                if j == i:
                    p = 1-(mlen-1)*pN
                sidxs[i].append(j)
                sfact[i].append(p)
        else:
            sidxs[i].append(i)
            sfact[i].append(1)

    return sidxs,sfact


def ApplySmoothing( xs, sidxs, sfact ):
    """Performs a windowed average of points along a parametric curve.

    Parameters
    ----------
    xs : numpy.ndarray, shape=(npt,ndim)
        The points of the parametric curve to be smoothed

    sidxs : list of list of int
        The indexes of the points contributing to each windowed average.
        This is the first return value from GetSmoothingIdxs

    sfact : list of list of float
        The coefficients of each windowed average.
        This is the second return value from GetSmoothingIdxs.

    Returns
    -------
    ys : numpy.ndarray, shape=(npt,ndim)
        The smoothed points
    """
    import numpy as np
    ys = np.array(xs,copy=True)
    for i in range(xs.shape[0]):
        ys[i,:] = 0
        for k in range(len(sidxs[i])):
            j = sidxs[i][k]
            c = sfact[i][k]
            ys[i,:] += c * xs[j,:]
    return ys
