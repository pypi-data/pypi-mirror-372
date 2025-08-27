#!/usr/binenv python3


class EvalT(object):
    """A class for storing interpolation results. This class is typically used
    as a return type from several methods that optionally compute some of the
    values. This alleviates the need to return a variable number of return
    arguments

    Attributes
    ----------
    values : numpy.array, shape=(npts,)
        The free energy value at each evaluation point

    derivs : numpy.array, shape=(npts,ndim)
        The gradient of the free energy with respect to each dimension for
        each evaluation point

    errors : numpy.array, shape=(npts,)
        The (standard) error or error estimate of the free energy for each
        evaluation point

    Methods
    -------
"""
    
    def __init__(self,values,derivs,errors):
        """
        Parameters
        ----------
        values : numpy.array, shape=(npts,)
            The free energy value at each evaluation point

        derivs : numpy.array, shape=(npts,ndim)
            The gradient of the free energy with respect to each dimension for
            each evaluation point

        errors : numpy.array, shape=(npts,)
            The (standard) error or error estimate of the free energy for each
            evaluation point

        """
        
        self.values=values
        self.derivs=derivs
        self.errors=errors

        
