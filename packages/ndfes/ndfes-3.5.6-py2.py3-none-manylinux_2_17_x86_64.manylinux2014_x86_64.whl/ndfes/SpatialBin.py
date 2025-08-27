#!/usr/bin/env python3


    
class SpatialBin(object):
    """
    A class that stores the free energy value, standard error, and reweighting
    entropy of a bin

    Attributes
    ----------
    bidx : list of int
        The bin index in each dimension

    value : float
        The free energy value

    stderr : float
        The standard error of the free energy value.

    entropy : float
        The reweighting entropy

    size : int
        The number of observed samples in this bin

    center : list of float
        The coordinates of the bin center.  By default, the list of coordinates
        are all 'None'. The MBAR or VFEP classes will replace the list with
        appropriate values when they are constructed.

    Methods
    -------
    """
    
    def __init__(self,bidx,value=None,stderr=None,entropy=None,size=1):
        """
        Parameters
        ----------
        bidx : list of int
            The bin index in each dimension

        value : float, optional
            The free energy value

        stderr : float, optional
            The standard error of the free energy value.

        entropy : float, optional
            The reweighting entropy

        size : int, default=1
            The number of samples in this bin

        """
        
        self.bidx    = bidx
        self.value   = value
        self.stderr  = stderr
        self.entropy = entropy
        self.size    = size
        self.center  = [None]*len(bidx)

        
    def __call__(self):
        """
        Returns
        -------
        tuple (float,float,float)
            The value, standard error, and entropy as a tuple
        """
        
        return (self.value,self.stderr,self.entropy)

    
    def __str__(self):
        """
        Returns
        -------
        str
            The bin center, value, standard error, and entropy
            as a string
        """
        return "%s %15.6e %12.3e %8.3f"%(
            " ".join(["%14.8f"%(c) for c in self.center]),
            self.value,
            self.stderr,
            self.entropy)
    

