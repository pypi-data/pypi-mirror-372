#!/usr/bin/env python3


def bspline_one_pass( c, w, n ):
    """Cardinal B-spline utility function that evaluates
    the recursion coefficients

    Parameters
    ----------
    c : numpy.array, shape=(n,), dtype=float
        The input array values are modified on output

    w : float
        The B-spline progress variable [0,1]

    n : int
        The B-spline order

    Returns
    -------
    None
        Note that the c array values are modified
    """
    
    import numpy as np
    nm1 = n-1
    div = 1. / nm1
    c[nm1] = div * w * c[nm1 - 1]
    for j in range(1,nm1):
        c[nm1-j] = div * ((w + j) * c[nm1 - j - 1] + (n - j - w) * c[nm1 - j])
    c[0] =  div * (1 - w) * c[0]

    
def bspline_eval( w, order, array ):
    """Evaluates the Cardinal B-spline values
    
    Parameters
    ----------
    w : float
        B-spline progress variable [0,1]

    order : int
        The number of B-spline values

    array : numpy.ndarray, shape=(order,), dtype=float
        The B-spline values. The array elements are modfied
        on output

    Returns
    -------
    None
        Note that the array elements are modified on output
    """
    
    array[0] = 1. - w
    array[1] = w
    if order > 2:
      # One pass to order 3:
        array[2] = 0.5 * w * array[1]
        array[1] = 0.5 * ((w + 1.) * array[0] + (2. - w) * array[1])
        array[0] = 0.5 * (1. - w) * array[0]
        if order > 3:
            # One pass to order 4:         
            div = 1./3.
            array[3] = div * w * array[2]
            array[2] = div * ((w + 1.) * array[1] + (3. - w) * array[2])
            array[1] = div * ((w + 2.) * array[0] + (2. - w) * array[1])
            array[0] = div * (1. - w) * array[0]
            # and the rest
            for k in range(5,order+1):
                bspline_one_pass(array,w,k)


def bspline_diff( order, array, diff ):
    """Cardinal B-spline utility function that calculates the derivative
    recurrence from the B-spline values

    Parameters
    ----------
    order : int
        B-spline order

    array : numpy.array, shape=(order,), dtype=float
        B-spline values
    
    diff : numpy.array, shape=(order,), dtype=float
        B-spline derivatives. The diff elements are changed on output

    Returns
    -------
    None
        Note that the diff array elements are changed on output
    """
    
    nm1 = order-1
    diff[0] = -array[0]
    for j in range(1,nm1):
        diff[j] = array[j-1] - array[j]
    diff[nm1] = array[nm1-1]



    
def bspline_eval_deriv( w, order, array, darray ):
    """Evaluated the 1D Cardinal B-spline values and derivatives, given
    the B-spline progress variable

    Parameters
    ----------
    w : float
        B-spline progress variable

    order : int
        B-spline order

    array : numpy.array, shape=(order,), dtype=float
        B-spline values. The array elements are changes on output
    
    darray : numpy.array, shape=(order,), dtype=float
        B-spline derivatives. The diff elements are changed on output

    Returns
    -------
    None
        Note that the array elements are changed on output
        Note that the darray elements are changed on output
    """
    
    if order < 3:
        raise Exception("B-spline derivatives available only for order >= 3")
    
    div = 1./3.;

    array[0] = 1. - w;
    array[1] = w;

    if order == 4:
        # One pass to order 3:
        array[2] = 0.5 * w * array[1];
        array[1] = 0.5 * ((w + 1.) * array[0] + (2. - w) * array[1]);
        array[0] = 0.5 * (1. - w) * array[0];
      
        darray[0] = -array[0];
        darray[1] = array[0]-array[1];
        darray[2] = array[1]-array[2];
        darray[3] = array[2];

        # One pass to order 4:     
        array[3] = div * w * array[2];
        array[2] = div * ((w + 1.) * array[1] + (3. - w) * array[2]);
        array[1] = div * ((w + 2.) * array[0] + (2. - w) * array[1]);
        array[0] = div * (1. - w) * array[0];
      
    elif order > 4:
        array[2] = 0.5 * w * array[1];
        array[1] = 0.5 * ((w + 1.) * array[0] + (2. - w) * array[1]);
        array[0] = 0.5 * (1. - w) * array[0];
        
        array[3] = div * w * array[2];
        array[2] = div * ((w + 1.) * array[1] + (3. - w) * array[2]);
        array[1] = div * ((w + 2.) * array[0] + (2. - w) * array[1]);
        array[0] = div * (1. - w) * array[0];

        # and the rest
        for k in range(5,order): # don't do k==order
            bspline_one_pass(array, w, k);

        bspline_diff(order,array,darray);

        # One more recursion: // do the k==order
        bspline_one_pass(array, w, order);

    else: # order == 3
        darray[0] = -array[0];
        darray[1] = array[0]-array[1];
        darray[2] = array[1];

        # One pass to order 3:
        array[2] = 0.5 * w * array[1];
        array[1] = 0.5 * ((w + 1.) * array[0] + (2. - w) * array[1]);
        array[0] = 0.5 * (1. - w) * array[0];
    




def CptBsplineValues(x,xmin,binwidth,order):
    """Computes the Cardinal B-spline values of a point

    Parameters
    ----------
    x : float
        The coordinate of the point

    xmin : float
        The left-most bin edge of the grid. If one desires
        the output edge indexes to be >= 0, then xmin must
        be less than all possible evaluation points and
        be further padded by (nbspl//2-1)*binwidth, where
        nbspl = order + order%2

    binwidth : float
        The width of each bin

    order : int
        The B-spline order

    Returns
    -------
    bs : numpy.array, shape=(order,), dtype=int
        The corner indexes of the nonzero B-spline weights

    ws : numpy.array, shape=(order,), dtype=float
        The B-spline weights
    """
    
    import numpy as np
    
    # even = 0, odd = 1
    isodd = order%2
    
    # The number of possible corners that may be nonzero
    # Only "order" of them will actually be nonzero, but
    # which of them will depend on the value of x
    # (if order is odd)
    nbspl=order+isodd

    # The nonzero b-spline weights
    ws = np.zeros( (order,) )
    
    # The number of bins traversed to reach the sample
    # The 0.5*isodd is due to the bins appearing to be shifted
    # by 1/2 bin width when odd orders are used.  That is,
    # when x=xmin, then it will appear to have passed 1/2 way
    # through the first bin, from the B-spline's perspective
    bidx_float = (x - xmin)/binwidth + 0.5*isodd

    # The number of bins traversed to reach the sample's bin
    bidx = int(np.floor(bidx_float))

    # The fraction traversed through the sample's bin
    # bfrac is a number between 0 and 1
    bfrac = bidx_float - bidx
    #print("prebfrac %i %30.20e %30.20e %s"%(bidx,bidx_float,bfrac,str(bfrac<0.5)))

    # The left-most edge accessible by the sample's b-spline
    lidx = bidx-(nbspl//2-1)

    # The edge indices of the b-spline weights
    bs = np.array([ tidx for tidx in range(lidx,lidx+order) ],dtype=int)

    #print("bspline frac %20.10e %i %20.10e"%(bfrac,bidx,bidx_float))
    
    if order == 1:
        ws[0] = 1.
    else:
        bspline_eval(bfrac,order,ws)

    
    #print("%s"%(" ".join(["%13i"%(x) for x in bs ])))
    #print("%s"%(" ".join(["%13.4e"%(x) for x in ws ])))

    return bs,ws



def CptBsplineValuesAndDerivs(x,xmin,binwidth,order):
    """Computes the Cardinal B-spline values and derivatives of a point

    Parameters
    ----------
    x : float
        The coordinate of the point

    xmin : float
        The left-most bin edge of the grid. If one desires
        the output edge indexes to be >= 0, then xmin must
        be less than all possible evaluation points and
        be further padded by (nbspl//2-1)*binwidth, where
        nbspl = order + order%2

    binwidth : float
        The width of each bin

    order : int
        The B-spline order

    Returns
    -------
    bs : numpy.array, shape=(order,), dtype=int
        The corner indexes of the nonzero B-spline weights

    ws : numpy.array, shape=(order,), dtype=float
        The B-spline weights

    ds : numpy.array, shape=(order,), dtype=float
        The B-spline derivatives
    """
    
    import numpy as np
    
    # even = 0, odd = 1
    isodd = order%2
    
    # The number of possible corners that may be nonzero
    # Only "order" of them will actually be nonzero, but
    # which of them will depend on the value of x
    # (if order is odd)
    nbspl=order+isodd

    # The nonzero b-spline weights
    ws = np.zeros( (order,) )

    # The nonzero b-spline derivs
    ds = np.zeros( (order,) )

    # The number of bins traversed to reach the sample
    # The 0.5*isodd is due to the bins appearing to be shifted
    # by 1/2 bin width when odd orders are used.  That is,
    # when x=xmin, then it will appear to have passed 1/2 way
    # through the first bin, from the B-spline's perspective
    bidx_float = (x - xmin)/binwidth + 0.5*isodd

    # The number of bins traversed to reach the sample's bin
    bidx = int(bidx_float)

    # The fraction traversed through the sample's bin
    # bfrac is a number between 0 and 1
    bfrac = bidx_float - bidx

    # The left-most edge accessible by the sample's b-spline
    lidx = bidx-(nbspl//2-1)

    # The edge indices of the b-spline weights
    bs = np.array([ tidx for tidx in range(lidx,lidx+order) ],dtype=int)
    
    if order == 1:
        ws[0] = 1.
    else:
        bspline_eval_deriv(bfrac,order,ws,ds)
        ds /= binwidth

    return bs,ws,ds
