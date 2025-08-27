#!usr/bin/env python3



def GetPtsFromRegGrid(mgrid):
    """Converts a meshgrid to a list of points

    Parameters
    ----------
    mgrid : numpy.array, shape=(ndim,nz,ny,nx,...)
        A mesh grid. The first index is the dimension, the remaining 
        indexes (1 index for each dimension) are the number of points 
        in the dimension

    Returns
    -------
    numpy.ndarray, shape=(npts,ndim)
        Reshaped array, where npts = nx*ny*nz*... is the number of 
        points in the grid, and the fast index loops over dimension
    """
    
    import numpy as np
    ncrd = mgrid.shape[0]
    npts = np.prod(mgrid.shape[1:])
    # moveaxis changes the dim axis from being the slow index to the fast index
    return np.moveaxis(mgrid,0,-1).reshape((npts,ncrd))



def LinearPtsToMeshPts(lpts):
    """Converts a list (corresponding to each dimension) of lists 
    (corresponding to 1D spatial locations) into a list of N-dimensional
    spatial coordinates of the mesh.  The returned array's fast index is 
    the dimension and whose slow index refers to a point on the meshgrid

    Parameters
    ----------
    lpts : list of lists
        A linear representation a mesh grid. The first index is the 
        dimension, and the second index is a value for each grid point 
        along the dimension

    Returns
    -------
    numpy.ndarray, shape=(npts,ndim)
        Reshaped array, where npts = nx*ny*nz*... is the number of 
        points in the grid, and the fast index loops over dimension
    """
    
    import numpy as np
    mgrid = np.array(np.meshgrid( *lpts, indexing='ij' ))
    return GetPtsFromRegGrid(mgrid)



def LinearWtsToMeshWts(lwts):
    """Converts a list (corresponding to each dimension) of lists 
    (corresponding to 1D weight values) into a flat list of values, 
    whose size is the total number of points on the grid and whose 
    values are the product of the 1D grid values

    Parameters
    ----------
    lwts : list of lists
        A list of 1D weight values for each dimension

    Returns
    -------
    numpy.ndarray, shape=(npts,)
        npts = nx*ny*nz*... is the number of points in the grid
    """
    
    import numpy as np
    
    lwts = np.array(lwts)
    ndim = lwts.shape[0]
    wts = lwts[0,:]
    for dim in range(1,ndim):
        wts = np.outer( wts, lwts[dim,:] ).flatten()
    return wts
    


def BasicWrap(x,l):
    """Places x within the range [0,l)

    Parameters
    ----------
    x : float
        The variable to be wrapped

    l : float
        The length of periodic range

    Returns
    -------
    float
        The wrapped value of x
    """
    return x - l * round(x/l)



def WrapAngleRelativeToRef(angle,ref):
    """Places angle within +/- 180 of ref. The return value is not
    guaranteed to be within the range [0,360].

    Parameters
    ----------
    angle : float
        The angle to wrap in degrees

    ref : float
        The reference angle acting as the center in degrees

    Returns
    -------
    float
        The wrapped angle in degrees
    """
    # d is the difference
    d = angle-ref
    halfrange = 180.
    dimrange = 360.
    # wd is the wrapped difference in the range [-halfrange,halfrange)
    # i.e., it is the min.img. displacement of angle from ref
    wd = (d-halfrange)%dimrange-halfrange
    return wd+ref


def MeanAngleRelativeToRef(angles,ref):
    """Calculates the mean value of an angle and then translates
    the mean to places it within +/- 180 of ref. The return value is not
    guaranteed to be within the range [0,360].

    Parameters
    ----------
    angles : np.array, shape=(n,), dtype=float
        The angle to wrap in degrees

    ref : float
        The reference angle acting as the center in degrees

    Returns
    -------
    float
        The wrapped mean angle in degrees
    """
    import numpy as np
    from scipy.stats import circmean
    angles = np.array(angles)
    if len(angles.shape) != 1:
        raise Exception(f"Expected a 1d array of angles, but "
                        f"received a matrix with shape {angles.shape}")
    mu = circmean(angles,high=360,low=0)
    return WrapAngleRelativeToRef(mu,ref)


def MeanAngleAndStdRelativeToRef(angles,ref):
    """Calculates the mean value of an angle and its standard
    deviation. The mean is translated to places it within 
    +/- 180 of ref. The return value is not guaranteed to be 
    within the range [0,360].

    Parameters
    ----------
    angles : np.array, shape=(n,), dtype=float
        The angle to wrap in degrees

    ref : float
        The reference angle acting as the center in degrees

    Returns
    -------
    float
        The wrapped mean angle in degrees
    """
    import numpy as np
    from scipy.stats import circmean
    angles = np.array(angles)
    if len(angles.shape) != 1:
        raise Exception(f"Expected a 1d array of angles, but "
                        f"received a matrix with shape {angles.shape}")
    mu = circmean(angles,high=360,low=0)
    mu = WrapAngleRelativeToRef(mu,ref)
    nang = len(angles)
    rangs = np.deg2rad(angles)
    cangs = np.cos(rangs)
    sangs = np.sin(rangs)
    R = np.sqrt(np.mean(sangs)**2 + np.mean(cangs)**2)
    std = np.rad2deg( np.sqrt(-2*np.log(R)) )
    return mu,std



class MinImg(object):
    """Class that stores the periodic information and provides
    methods for calculating Euclidean distances while considering
    the periodicity of each dimension; e.g., the minimum image
    convention

    Attributes
    ----------
    dimisper: numpy.array, shape=(ndim,), dtype=bool
        Flag indicating if the dimension is periodic

    dimrange: float
        The range of periodicity

    halfrange: float
        dimrange/2

    wrap: univariate lambda function
        Wraps a coordinate value to the range [-halfrange,halfrange)
    
    Methods
    -------
    """
    def __init__(self,dimisper,dimrange=360):
        """
        Parameters
        ----------
        dimisper: numpy.array, shape=(ndim,), dtype=bool
            Flag indicating if the dimension is periodic

        dimrange: float, default=360
            The range of periodicity
        """
        import numpy as np
        self.dimisper = dimisper
        self.dimrange = dimrange
        self.halfrange = dimrange/2

    def wrap(self,x):
        """Wraps a coordinate value to the range [-halfrange,halfrange)
        
        Parameters
        ----------
        x : float
            1D coordinate value

        Returns
        -------
        float
        """
        return (x-self.halfrange)%self.dimrange-self.halfrange
        
    def diffsep(self,x,y):
        """Calculates the Euclidean distance between two points, 
        considering the periodicity of each dimension.

        Parameters
        ----------
        x : numpy.array, shape=(ndim,)
            A point in space
        
        y : numpy.array, shape=(ndim,)
            A point in space
        
        Returns
        -------
        float
            Distance |x-y| while considering the periodicity of each 
            dimension
        """
        import numpy as np
        return np.linalg.norm(self.diffcrd(x,y))

    def diffcrd(self,x,y):
        """Calculates the distance vector between two points,
        considering the periodicity of each dimension.

        Parameters
        ----------
        x : numpy.array, shape=(ndim,)
            A point in space
        
        y : numpy.array, shape=(ndim,)
            A point in space
        
        Returns
        -------
        numpy.array, shape=(ndim,)
            The difference vector x-y using the minimum image convention
            for each dimension
        """
        import numpy as np
        return np.where(self.dimisper,self.wrap(x-y),x-y)
