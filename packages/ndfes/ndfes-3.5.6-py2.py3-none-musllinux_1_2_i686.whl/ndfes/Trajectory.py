#!/usr/bin/env python3

import numpy as np
from pathlib import Path

class Trajectory(object):
    """A class that describes a trajectory

    Attributes
    ----------
    hamidx : int
        The index of the Hamiltonian that produced the trajectory.
        
    temperature : float
        The temperature (Kelvin) the trajectory was simulated at

    dumpave : str
        The filename containing the timeseries of collective variables
        and possibly potential energies of the Hamiltonians

    xs : list, len=(ndim,)
        The umbrella window center for each dimension

    ks : list, len=(ndim,)
        The umbrella window "force constants". Technically, these are
        twice the forcs constants, such that the bias potential is:
        Ubias(x) = np.dot( ks[:], ( x-xs[:] )**2 )

    prefix : str
        The directory containing the dumpave, such that the file is
        located at prefix + "/" + dumpave

    biasidx : int
        If this dumpave file is in a "general bias" format rather than
        a harmonic bias format, then the biasidx is the column of
        bias energies for this simulation.

    _means : np.array, shape=(ndim,) [private]
        Use self.GetMeanAndStd() to access this quantity
        This is the array of reaction coordinate means

    _stds : np.array, shape=(ndim,) [private]
        Use self.GetMeanAndStd() to access this quantity
        This is the array of standard deviations for each reaction coordinate

    _size : int [private]
        Use self.GetSampleSize to access this quantity
        This is the number of samples

    Methods
    -------
    """
    def __init__(self,hamidx,temp,dumpave,xs,ks,prefix=".",biasidx=None,ndim=None):
        self.hamidx = hamidx
        self.temperature = temp
        self.dumpave = dumpave
        self.prefix = prefix
        self.xs = None
        self.ks = None
        self.biasidx = biasidx
        self.ndim = ndim
        if xs is not None and ks is not None:
            self.xs = np.array(xs,copy=True)
            self.ks = np.array(ks,copy=True)
            self.ndim = self.xs.shape[0]

        self._means = None
        self._stds = None
        self._size = None

        self.path = self.prefix / Path(self.dumpave)
        if not self.path.is_file():
            self.path = Path(self.dumpave)


    def _ReadDumpave(self):
        """Private method to read the dumpave and store the
        sample size, mean, and standard deviation

        Sets self._means, self._stds, self._size
        """
        import numpy as np
        #path = self.prefix / Path(self.dumpave)

        if not self.path.is_file():
            raise Exception("File not found: %s"%(self.path))
        
        data = np.loadtxt( self.path )
        self._size = data.shape[0]
        if self.ndim is not None:
            self._means = np.array( [ np.mean(data[:,i+1])
                                      for i in range(self.ndim) ] )
            self._stds = np.array( [ np.std(data[:,i+1],ddof=1)
                                     for i in range(self.ndim) ] )
        else:
            # This isn't actually the number of dimensions because
            # it includes all bias potentials and potential energies
            ndim = data.shape[1] - 1
            self._means = np.array( [ np.mean(data[:,i+1])
                                      for i in range(ndim) ] )
            self._stds = np.array( [ np.std(data[:,i+1],ddof=1)
                                     for i in range(ndim) ] )

            
    def GetMeanAndStd(self):
        """Returns the mean and standard deviation of the reaction
        coordinates.

        Returns
        -------
        means : numpy.array, shape=(ndim,)
            The average values

        stds : numpy.array, shape=(ndim,)
            The standard deviations
        """
        
        if self._means is None:
            self._ReadDumpave()
        return self._means,self._stds

        
    def GetSampleSize(self):
        """Returns the number of samples

        Returns
        -------
        size : int
            The number of rows in the dumpave file

        """
        
        if self._means is None:
            self._ReadDumpave()
        return self._size
