#!/usr/bin/env python3



class SpatialDim(object):
    """
    A class used to store range and histogram information along one dimension

    Attributes
    ----------
    xmin : float
        The lowest value of the coordinate

    xmax : float
        The largest value of the coordinate

    size : int
        The number of histogram bins along the coordinate

    isper : bool
        Indicates if the dimension is periodic

    width : float
        The width of each bin (max-min)/size

    Methods
    -------
    """
    
    def __init__(self,xmin,xmax,size,isper):
        """
        Parameters
        ----------
        xmin : float
            The lowest value of the coordinate

        xmax : float
            The largest value of the coordinate

        size : int
            The number of histogram bins along the coordinate

        isper : bool
            Indicates if the dimension is periodic
        """
        
        self.xmin=xmin
        self.xmax=xmax
        self.size=size
        self.isper=isper
        self.width=(xmax-xmin)/size

        
    def Wrap(self,x,range180=False):
        """If the coordinate is periodic, wrap the value into range; return the
        unaltered value, otherwise

        Parameters
        ----------
        x : float
            The value to wrap

        range180 : bool, default=False
            If the dimension is periodic, then x is wrapped to [0,360), but
            if range180=True, then it is wrapped to [-180,180).

        Returns
        -------
        float
            The wrapped value of x
        """

        from . GridUtils import BasicWrap
        
        xp = x
        if self.isper:
            mid = 0.5*( self.xmin + self.xmax )
            if range180:
                mid = 0
            xp = BasicWrap( x-mid, self.xmax-self.xmin )+mid
            if xp == self.xmax:
                xp = self.xmin
        return xp

    
    def GetIdx(self,x):
        """Return the bin index containing the sample
        
        Parameters
        ----------
        x : float
            The sample to bin
        
        Returns
        -------
        int
            The bin index
        """

        xp = self.Wrap(x)
        idx = int( (xp-self.xmin)/self.width )
        if idx < 0 or idx >= self.size:
            idx = None
        return idx


    def GetRegGridCenters(self):
        """Return a regular grid of bin centers

        Returns
        -------
        numpy.array dims=(size,), dtype=float
            The location of the bin centers
        """

        import numpy as np
        return (np.arange(self.size)+0.5)*self.width + self.xmin

    
    def GetRegGridEdges(self):
        """Return a regular grid of bin edges

        Returns
        -------
        numpy.array dims=(size,), dtype=float
            The location of the bin edges
        """

        import numpy as np
        return (np.arange(self.size+1))*self.width + self.xmin

    
