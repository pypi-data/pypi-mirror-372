#!/usr/bin/env python3

from . FES import FES

    
class MBAR(FES):
    """
    A class used to store and retrieve free energy results from an MBAR 
    calculation.  Specifically, the stored data consists of the unbiased free
    energies of each occupied bin, their standard errors, and reweighting
    entropies.  This class does not contain the biased state free energies, nor
    the unbiased Hamiltonian free energies.
 
    Attributes
    ----------
    grid : VirtualGrid
        The range and size information of each dimension

    bins : dict (key : int, value : SpatialBin)
        A dictionary of occupied bins.  The key values are the global bin
        index, and the values are SpatialBin objects containing the free
        energy, standard error, and reweighting entropy values

    nearestbin : scipy.interpolate.RegularGridInterpolator
        Returns the index of the nearest occupied bin to any point,
        without considering periodicity.  Note that this attribute
        is None by default. One should not manually access this
        attribute. Instead use the GetClosestBinIdx method, which will
        create the interpolator object, if necessary.

    gpr : ndfes.GPR
        Interpolates the free energy surface using a Gaussian Process
        Regression fit. Note that this attribute is None by default.
        One should instead use the UseGPRInterp to initialize the
        interpolator and then use the CptInterp method to perform 
        interpolations using the stored object

    Methods
    -------
    """
    
    def __init__(self, grid, bins, kb=None):
        """
        Parameters
        ----------
        grid : VirtualGrid
            The range and size information of each dimension

        bins : dict (key : int, value : SpatialBin)
            A dictionary of occupied bins.

        kb : float, optional
            The value of Boltzmann's constant in the desired
            energy units. Default is None, which will produce
            an error if it is used mathematically.
        """
        
        super().__init__(grid,bins,kb=kb)


    
    # def _makerbf(self,eps=None):
    #     import numpy as np
    #     import scipy.interpolate.RBFInterpolator as MakeRBF
    #     xobs = []
    #     yobs = []
    #     for gidx in self.bins:
    #         b = self.bins[gidx]
    #         y = b.value
    #         if y is not None:
    #             yobs.append( y )
    #             xobs.append( b.center )
    #     self.rbf = None
    #     if len(yobs) > 0:
    #         self.rbf = MakeRBF(xobs,yobs,kernel='multiquadric',epsilon=eps)

            
    # def GetRBFValue(self,xs,eps=None):
    #     y = None
    #     gidx = self.grid.GetGlbBinIdx(x)
    #     if gidx in self.bins:
    #         if self.rbf is None:
    #             self._makerbf(eps=eps)
    #         y = self.rbf(self.grid.Wrap(xs))
    #     return y

    


    def ResizeGrid(self,newgrid):
        """Returns a new MBAR object using the provided grid.  The grid
        dimensions and periodicity must be the same as the original
        grid.

        Parameters
        ----------        
        newgrid : VirtualGrid
            The new grid

        Returns
        -------
        newinstance : vFEP
            A new vFEP object
        """
        
        from collections import defaultdict as ddict
        from . SpatialBin import SpatialBin
        from . GridUtils import LinearPtsToMeshPts

        if self.grid.ndim != newgrid.ndim:
            raise Exception("Can't resize grid because dims are different")
        
        for dim in range(self.grid.ndim):
            if abs(self.grid.dims[dim].width-newgrid.dims[dim].width) > 1.e-8:
                raise Exception("Can't resize grid because widths are "
                                +"different")
        for dim in range(self.grid.ndim):
            if self.grid.dims[dim].xmin < newgrid.dims[dim].xmin or \
               self.grid.dims[dim].xmax > newgrid.dims[dim].xmax:
                raise Exception("Can't resize grid because new grid is smaller")

        for dim in range(self.grid.ndim):
            if self.grid.dims[dim].isper != newgrid.dims[dim].isper:
                raise Exception("Can't resize grid because periodic mismatch")

            
        ndim=self.grid.ndim
        offs = [0]*ndim

        for dim in range(ndim):
            dx = self.grid.dims[dim].xmin - newgrid.dims[dim].xmin
            #print(dx/self.grid.dims[dim].width)
            db =  dx/self.grid.dims[dim].width
            if db > 0:
                dn = int( db + 0.5 )
            else:
                dn = int( db - 0.5 )

            if abs(db-dn) > 1.e-6:
                raise Exception("Can't resize grid because the new range "
                                +"is shifted from the original grid")
                
            offs[dim] = dn


        bins = ddict( int )
        for gidx in self.bins:
            sbin = self.bins[gidx]
            newbidx=[ sbin.bidx[dim] + offs[dim]
                      for dim in range(ndim) ]
            is_valid=True
            for dim in range(ndim):
                if newbidx[dim] < 0 or newbidx[dim] >= newgrid.dims[dim].size:
                    is_valid=False
            if is_valid:
                newgidx=0
                for dim in reversed(range(ndim)):
                    newgidx = newbidx[dim] + newgidx*newgrid.dims[dim].size
                bins[newgidx] = SpatialBin( newbidx,
                                            sbin.value,
                                            sbin.stderr,
                                            sbin.entropy,
                                            sbin.size )

        return MBAR(newgrid, bins)

    
    
    def GetXml(self):
        import xml.etree.ElementTree as ET
        mnode = ET.Element("model")
        ET.SubElement(mnode,"type").text = "MBAR"
        if self.kb is not None:
            ET.SubElement(mnode,"kb").text = "%23.14e"%(self.kb)
        mnode.append( self.grid.GetXml() )
        bnodes = self.GetBinXml(binvals=True)
        for bnode in bnodes:
            mnode.append( bnode )
        return mnode
    
