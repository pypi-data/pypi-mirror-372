#!/usr/bin/env python3

from . GridUtils import GetPtsFromRegGrid

    
class FES(object):
    """
    A base class used to store and retrieve free energy results from MBAR or 
    vFEP calculations.  Specifically, the base class stores data the unbiased
    free energies of each occupied bin, their standard errors, and reweighting
    entropies.  For vFEP, the these quantities are "None"; the base class 
    primarily acts to indicate which bins are occupied with data. This class
    does not contain the biased state free energies, nor the unbiased 
    Hamiltonian free energies.
 
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
        from . ReadCheckpoint import InferEnergyUnitsFromBoltzmannConstant
        self.grid = grid
        self.bins = bins
        self.kb   = kb
        self.EneUnits = InferEnergyUnitsFromBoltzmannConstant(self.kb)
        for gidx in self.bins:
            self.bins[gidx].center = self.grid.GetBinCenter(
                self.bins[gidx].bidx )
        self.nearestbin = None
        self.gpr = None
        self.rbf = None
        self.wavg = None


    def ResizeDims(self,mins,maxs):
        from . SpatialDim import SpatialDim
        from . VirtualGrid import VirtualGrid
        from . SpatialBin import SpatialBin
        from . MBAR import MBAR
        
        ndim = self.grid.ndim
        if len(mins) != ndim:
            raise Exception(f"size of mins {len(mins)} does not match ndim {ndim}")
        if len(maxs) != ndim:
            raise Exception(f"size of mins {len(maxs)} does not match ndim {ndim}")
        dims = []
        for i in range(ndim):
            w = self.grid.dims[i].width
            minx = round( mins[i] / w ) * w
            maxx = round( maxs[i] / w ) * w
            n = int(round( (maxx-minx)/w ))
            if self.grid.dims[i].isper:
                minx = self.grid.dims[i].xmin
                maxx = self.grid.dims[i].xmax
                n = self.grid.dims[i].size
            
            if abs( minx + n*w - maxx ) >= w/2:
                raise Exception(f"Failed to reset dim {i} min={minx} max={maxx} w={w} n={n}")
            dims.append(SpatialDim(minx,maxx,n,self.grid.dims[i].isper))
        grid = VirtualGrid(dims)
        bins = {}
        for gidx,sbin in sorted(self.bins.items()):
            inrange=True
            for dim in range(ndim):
                if sbin.center[dim] < grid.dims[dim].xmin \
                   or sbin.center[dim] > grid.dims[dim].xmax:
                    inrange=False
            if inrange:
                bidx = grid.GetBinIdx( sbin.center )
                c = grid.GetBinCenter( bidx )
                newgidx = grid.CptGlbIdxFromBinIdx( bidx )
                match = True
                for dim in range(ndim):
                    if abs(c[dim]-sbin.center[dim]) > w/100:
                        match=False
                if not match:
                    raise Exception(f"bin center mismatch {c} vs {sbin.center}")
                b = SpatialBin(bidx,
                               value=sbin.value,
                               stderr=sbin.stderr,
                               entropy=sbin.entropy,
                               size=sbin.size)
                b.center = c

                bins[newgidx] = b
        return MBAR(grid,bins)
    
            
        
    def GetOccBins(self):
        obins = {}
        for gidx,sbin in sorted(self.bins.items()):
            if sbin.size > 0:
                obins[gidx] = sbin
        return obins
        

    def __CreateNearestGridInterpolator(self):
        """Creates a RegularGridInterpolator that accepts a position
        in space and returns the global bin index of the nearest bin

        Note that this method doesn't properly consider periodicity
        because it uses NearestNDInterpolator and RegularGridInterpolator
        to find the closest occupied bin, and these classes do not
        allow the user to override the Eucleidean distance operation.
        One would need to reimplement these algorithms from scratch.

        Returns
        -------
        nearestbin : scipy.interpolate.RegularGridInterpolator
            Accepts a point in space and returns the index of the 
            nearest bin 
        """
        
        import numpy as np
        from scipy.interpolate import NearestNDInterpolator
        from scipy.interpolate import RegularGridInterpolator
        
        #
        # crds : np.array, shape=(NoccBins,ndim)
        #    The coordinates of each occupied bin
        #
        # idxs : np.array, shape=(NoccBins,), dtype=int
        #    The global bin index of each occupied bin
        #

        occbins = self.GetOccBins()
        
        crds = np.array([ sbin.center
                          for gidx,sbin in sorted(occbins.items()) ])
        
        idxs = np.array([ gidx
                          for gidx,sbin in sorted(occbins.items()) ],
                        dtype=int )
        
        #
        # Use NearestNDInterpolator to find the nearest occupied
        # bin for each unoccupied bin
        #
    
        nearestbin = NearestNDInterpolator(crds,idxs)

        #
        # We could use the NearestNDInterpolator object to always
        # find the nearest occupied bin, but now that we used it
        # to form a regular grid of values, we can use a
        # RegularGridInterpolator henceforth, which is less costly
        # to evaluate.
        #
        # The grid centers need to be input as a list of 1D arrays,
        # and the values as a meshgrid... seems like an odd convention,
        # but ok.
        #
        # grids : list of np.array
        #     The 1D list of grid points for each dimension
        #
        # mgrid : np.array, shape=(ndim,nx,ny,...)
        #     The collection of meshgrid coordinates
        #
        # idxs : np.array, shape=(nx,ny,...)
        #     The collection of meshgrid values
        #     The values are the nearest occupied bin index
        #
        
        grids = [sdim.GetRegGridCenters() for sdim in self.grid.dims]
        mgrid = np.meshgrid(*grids,indexing='ij')
        idxs = nearestbin(*mgrid).reshape( mgrid[0].shape )

        nearestbin = RegularGridInterpolator(\
                        grids,idxs,method="nearest",
                        bounds_error=False,fill_value=None)
        return nearestbin


    def GetClosestBinIdx(self,pt):
        """Returns the index of the closest occupied bin to pt, without
        considering the periodicity of the system. If you want to
        consider periodicity, then wrap the pt before calling this
        routine; however, this would only give the closest occupied
        center within the unit cell, rather than calculating the distances
        with the minimum image convention. To obtain proper return values,
        one would need to rewrite the NearestNDInterpolator and
        RegularGridInterpolator classes provided by scipy

        Parameters
        ----------
        pt : np.array, shape=(ndim,)
            The coordinates of the point to query

        Returns
        -------
        gidx : int
            The global bin index of the closest occupied bin
        """
        if self.nearestbin is None:
            self.nearestbin = self.__CreateNearestGridInterpolator()
        return self.nearestbin([pt])[0]
    
    
    def GetInterpCrd(self,pt,k=100):
        """Checks to see if pt is within an occupied bin. If it is not,
        then it returns the coordinates of the nearest grid center, a
        harmonic penalty (k*dx**2) and the penalty gradient (2*k*dx).
        If it is, then it returns the pt, and 0.0 penalty and [0,0,0]
        gradient

        Parameters
        ----------
        pt : np.array, shape=(ndim,)
            The input evaluation point

        k : float, default=100
            The harmonic penalty force constant if pt is out of bounds

        Returns
        -------
        x : np.array, shape=(ndim,)
            The wrapped coordinates, or the location of the nearest bin
            center

        ene : float
            The out-of-bounds harmonic penalty value

        grd : np.array, shape=(ndim,)
            The out-of-bounds harmonic penalty gradient

        """
        import numpy as np

        wp = [ self.grid.dims[i].Wrap(pt[i]) for i in range(self.grid.ndim) ]
        ibin = self.grid.GetGlbBinIdx(pt)
        occbins = self.GetOccBins()
        
        if ibin in occbins:
            c = np.array(wp)
            ene = 0.
            grd = np.zeros( c.shape )
        else:
            ibin = self.GetClosestBinIdx(wp)
            c = np.array([x for x in self.bins[ibin].center])
            dx = np.array([ x-y for x,y in zip(wp,self.bins[ibin].center)])
            ene = k * np.dot(dx,dx)
            grd = 2 * k * dx
        return c,ene,grd

    
    def GetRegGridCenters(self,full=False,bounds=None):
        """Returns a meshgrid defining a minimal regular grid of bin centers
        that span the range of occupied bins

        Parameters
        ----------
        full : bool, default=False
            If full=False, then the grid covers the smallest possible range
            of occupied bins. Otherwise, it covers the full range of
            the virtual grid

        bounds : numpy.array, shape=(ndim,2), optional
            If bounds is not None, then bounds is the range
            of each dimension, and the value of full is ignored

        Results
        -------
        numpy.array, shape=(ndim,nx,ny,nz,...)
            A mesh grid. The first index is the dimension, the remaining indexes
            (1 index for each dimension) are the number of points in the 
            dimension
        """
        
        import numpy as np
        if bounds is not None:
            if len(bounds.shape) != 2:
                raise Exception("bounds array expected to be 2d")
            if bounds.shape[0] != len(self.grid.dims):
                raise Exception(f"Incorrect bounds dimensions "
                                f"{bounds.shape[0]} expected "
                                f"{len(self.grid.dims)}")
            if bounds.shape[1] != 2:
                raise Exception(f"Expected lower and upper bounds"
                                f" but received {bounds.shape[1]}")
            grids = []
            ndim=self.grid.ndim
            for d in range(ndim):
                dim = self.grid.dims[d]
                #ilo = int(np.floor((bounds[d,0]-dim.xmin) / dim.width))
                #ihi = int(np.ceil((bounds[d,1]-dim.xmin) / dim.width))
                ilo = int(round((bounds[d,0]-dim.xmin) / dim.width))
                ihi = int(round((bounds[d,1]-dim.xmin) / dim.width))
                grids.append( [ (i+0.5)*dim.width + dim.xmin
                                for i in range(ilo,ihi) ] )
                #print(grids[-1][0],grids[-1][-1],ilo,ihi,dim.width,bounds[d,0] / dim.width,bounds[d,1] / dim.width)
            mgrid = np.array( np.meshgrid(*grids,indexing='ij') )
        elif not full:
            ndim = self.grid.ndim
            imins = [ 10000000]*ndim
            imaxs = [-10000000]*ndim
            occbins = self.GetOccBins()
            for gidx in occbins:
                b = occbins[gidx]
                for d in range(ndim):
                    imins[d] = min(imins[d],b.bidx[d])
                    imaxs[d] = max(imaxs[d],b.bidx[d])
            grids = []
            for d in range(ndim):
                dim = self.grid.dims[d]
                grids.append( [ (i+0.5)*dim.width + dim.xmin
                                for i in range(imins[d],imaxs[d]+1) ] )
                #print(len(grids[-1]))
            mgrid = np.array( np.meshgrid(*grids,indexing='ij') )
        else:
            #mgrid = self.grid.GetRegGridCenters()
            grids = []
            ndim=self.grid.ndim
            for d in range(ndim):
                dim = self.grid.dims[d]
                grids.append( [ (i+0.5)*dim.width + dim.xmin
                                for i in range(0,dim.size) ] )
                #print(len(grids[-1]))
            mgrid = np.array( np.meshgrid(*grids,indexing='ij') )
        return mgrid

    
    def GetRegGridCenterPts(self,full=False,bounds=None):
        """Returns an array of points defining a minimal regular grid of bin
        centers that span the range of occupied bins

        Parameters
        ----------
        full : bool, default=False
            If full=False, then the grid covers the smallest possible range
            of occupied bins. Otherwise, it covers the full range of
            the virtual grid

        bounds : numpy.array, shape=(ndim,2), optional
            If bounds is not None, then bounds is the range
            of each dimension, and the value of full is ignored

        Results
        -------
        numpy.array, shape=(npts,ndim)
            The array of grid points, where npts = nx*ny*nz*... is the number
            of points in the grid, and the fast index loops over dimension
        """
        
        return GetPtsFromRegGrid(self.GetRegGridCenters(full=full,bounds=bounds))


    def GetRegGridExtent(self,full=False,bounds=None):
        """Returns a flat list of ranges for each dimension. The ranges cover
        the space spanned by the occupied bins. The ranges go from bin edge
        to bin edge, rather than bin centers.

        Parameters
        ----------
        full : bool, default=False
            If full=False, then the grid covers the smallest possible range
            of occupied bins. Otherwise, it covers the full range of
            the virtual grid

        bounds : numpy.array, shape=(ndim,2), optional
            If bounds is not None, then bounds is the range
            of each dimension, and the value of full is ignored

        Results
        -------
        list, shape=(2*ndim,)
            The first element is the lower bound of the first dimension. The
            second element is the maximum bound of the first dimension. The
            remaining elements follow an analogous pattern for the remaining
            dimensions
        """
        
        import numpy as np
        if bounds is not None:
            if len(bounds.shape) != 2:
                raise Exception("bounds array expected to be 2d")
            if bounds.shape[0] != len(self.grid.dims):
                raise Exception(f"Incorrect bounds dimensions "
                                f"{bounds.shape[0]} expected "
                                f"{len(self.grid.dims)}")
            if bounds.shape[1] != 2:
                raise Exception(f"Expected lower and upper bounds"
                                f" but received {bounds.shape[1]}")
            extents=[]
            ndim=self.grid.ndim
            for d in range(ndim):
                dim = self.grid.dims[d]
                #ilo = int(np.floor((bounds[d,0]-dim.xmin) / dim.width))
                #ihi = int(np.ceil((bounds[d,1]-dim.xmin) / dim.width))
                ilo = int(round((bounds[d,0]-dim.xmin) / dim.width))
                ihi = int(round((bounds[d,1]-dim.xmin) / dim.width))
                extents.append( (ilo)*dim.width + dim.xmin )
                extents.append( (ihi)*dim.width + dim.xmin )
        elif not full:
            ndim = self.grid.ndim
            imins = [ 10000000]*ndim
            imaxs = [-10000000]*ndim
            occbins = self.GetOccBins()
            for gidx in occbins:
                b = occbins[gidx]
                for d in range(ndim):
                    imins[d] = min(imins[d],b.bidx[d])
                    imaxs[d] = max(imaxs[d],b.bidx[d]+1)
            extents = []
            for d in range(ndim):
                dim = self.grid.dims[d]
                extents.append( imins[d]*dim.width + dim.xmin )
                extents.append( imaxs[d]*dim.width + dim.xmin )
        else:
            ndim = self.grid.ndim
            extents = []
            for d in range(ndim):
                dim = self.grid.dims[d]
                extents.append( dim.xmin )
                extents.append( dim.xmax )
        return extents
    
    
    def GetBinCenters(self,pts=None):
        """Returns a list of occupied bin centers. The list does not necessarily
        form a complete regular grid, because not all bins may be occupied with
        samples. The bins are ordered by global index.

        Parameters
        ----------
        pts : list of list, optional
            If present, then for each point, find the histogram bin containing
            the point, and return the bin center.  If not present, then return
            the bin center from all bins

        Returns
        -------
        list of lists
            The each element of the list contains the N-dimensional coordinates
            of a bin center; that is, the size of element is the number of
            dimensions
        """

        vs=[]
        occbins = self.GetOccBins()
        if pts is None:
            vs = [ sbin.center for gidx,sbin in sorted(occbins.items) ]
        else:
            for pt in pts:
                gidx = self.grid.GetGlbBinIdx(pt)
                if gidx in occbins:
                    vs.append( occbins[gidx].center )
                else:
                    vs.append( None )
        return vs


    def GetBinValues(self,pts=None):
        """Returns the list of free energy values. The bins are ordered by
        global index.

        Parameters
        ----------
        pts : list of list, optional
            If present, then for each point, find the histogram bin containing
            the point, and return the bin value.  If not present, then return
            the bin value from all bins

        Returns
        -------
        list of float
            The free energy at the bin center
        """

        vs = []
        occbins = self.GetOccBins()
        if pts is None:
            vs = [ sbin.value for gidx,sbin in sorted(occbins.items()) ]
        else:
            for pt in pts:
                gidx = self.grid.GetGlbBinIdx(pt)
                if gidx in occbins:
                    vs.append( occbins[gidx].value )
                else:
                    vs.append( None )
        return vs

    
    def GetBinSizes(self,pts=None):
        """Returns the list of bin samples. The bins are ordered by
        global index.

        Parameters
        ----------
        pts : list of list, optional
            If present, then for each point, find the histogram bin containing
            the point, and return the bin value.  If not present, then return
            the bin value from all bins

        Returns
        -------
        list of float
            The number of samples at the bin center
        """

        vs = []
        occbins = self.GetOccBins()
        if pts is None:
            vs = [ sbin.size for gidx,sbin in sorted(occbins.items()) ]
        else:
            for pt in pts:
                gidx = self.grid.GetGlbBinIdx(pt)
                if gidx in occbins:
                    vs.append( occbins[gidx].size )
                else:
                    vs.append( None )
        return vs
    

    
    def GetBinErrors(self,pts=None):
        """Returns the list of free energy standard errors. The bins are
        ordered by global index.

        Parameters
        ----------
        pts : list of list, optional
            If present, then for each point, find the histogram bin containing
            the point, and return the bin error.  If not present, then return
            the bin error from all bins

        Returns
        -------
        list of float
            The free energy standard error at the bin center
        """

        vs = []
        occbins = self.GetOccBins()
        if pts is None:
            vs = [ sbin.stderr for gidx,sbin in sorted(occbins.items()) ]
        else:
            for pt in pts:
                gidx = self.grid.GetGlbBinIdx(pt)
                if gidx in occbins:
                    vs.append( occbins[gidx].stderr )
                else:
                    vs.append( None )
        return vs

    
    def GetBinEntropies(self,pts=None):
        """Returns the list of reweighting entropies. The bins are ordered by
        global index.

        Parameters
        ----------
        pts : list of list, optional
            If present, then for each point, find the histogram bin containing
            the point, and return the bin entropy.  If not present, then return
            the bin entropy from all bins

        Returns
        -------
        list of float
            The reweighting entropy of the bin
        """

        vs = []
        occbins = self.GetOccBins()
        if pts is None:
            vs = [ sbin.entropy for gidx,sbin in sorted(occbins.items()) ]
        else:
            for pt in pts:
                gidx = self.grid.GetGlbBinIdx(pt)
                if gidx in occbins:
                    vs.append( occbins[gidx].entropy )
                else:
                    vs.append( None )
        return vs

    
    def GetBinIdxs(self,pts=None):
        """Returns the list of bin indexs. The bins are ordered by global index.

        Parameters
        ----------
        pts : list of list, optional
            If present, then for each point, find the histogram bin containing
            the point, and return the bin index.  If not present, then return
            the bin value from all bin indices

        Returns
        -------
        list of list of int
            The N-dimensional bin index for each bin
        """

        vs = []
        if pts is None:
            vs = [ sbin.bidx for gidx,sbin in sorted(self.GetOccBins().items()) ]
        else:
            vs = [ self.grid.GetBinIdx(pt) for pt in pts ]
        return vs


    def GetOccMask(self,pts):
        """Returns a bool for each point that indicates if it resides in an
        occupied bin

        Parameters
        ----------
        pts : list of lists
            The points to check

        Returns
        -------
        list of bool
            There is one element per point, and it is True if the point lies
            within an occupied bin
        """
        mask=[]
        occbins = self.GetOccBins()
        for gidx in [ self.grid.GetGlbBinIdx(pt) for pt in pts ]:
            if gidx in occbins:
                mask.append(True)
            else:
                mask.append(False)
        return mask
    

    def GetInterpolationGrid(self,sizes,full=False,bounds=None):
        """Create a regular grid that covers the space spanned by the extent
        of the grid enclosing the occupied samples. There are two differences
        between this method and GetRegGridCenters. The grid created by this 
        method goes from bin edge to bin edge (rather than bin centers). 
        Second, the input sizes are provided as input, so the grid mesh can 
        be much finer grained than the underlying histogram bin.

        Parameters
        ----------
        sizes : list of int
           The desired uniform grid size for each dimension

        full : bool, default=False
            If full=False, then the grid covers the smallest possible range
            of occupied bins. Otherwise, it covers the full range of
            the virtual grid

        bounds : numpy.array, shape=(ndim,2), optional
            If bounds is not None, then bounds is the range
            of each dimension, and the value of full is ignored

        Returns
        -------
        np.array, shape=(ndim,nx,ny,nz,...)
           The collection of uniform grid meshes
        
        """

        import numpy as np
        
        ndim = self.grid.ndim
        extents = np.array(self.GetRegGridExtent(full=full,bounds=bounds))
        extents.resize(ndim,2)
        grids=[ np.linspace(extents[i,0],extents[i,1],sizes[i])
                for i in range(ndim) ]
        return np.array( np.meshgrid(*grids,indexing='ij') )


    def ShiftBinValues(self,e):
        """Sets a new zero of free energy. The input value is subtracted from
        from all bin values.  This does not shift the interpolated free
        energy values if the interpolator has already been created.
        See: ShiftInterpolatedValues

        Parameters
        ----------
        e : float
            The value to subtract

        """

        for gidx in self.bins:
            self.bins[gidx].value -= e


    def __CreateGPR(self,
                    filename=None,
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
        """Creates a Gaussian Process Regression object that fits to the bin
        values and standard errors. The object is internally stored as
        self.gpr

        Parameters
        ----------
        filename : str, optional
            If the file exists, then read the file as a serialized pickle
            of the GPR object. If the file does not exist, construct the
            GPR object and save it to file. If None, then construct the
            GPR object without any file operations.

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
        gpr : ndfes.GPR
            The GPR interpolation object
            
        """

        #The sklearn GPR object. Example usage of the gpr object:
        #    y_pred,sigma = gpr.predict(list_of_pts, return_std=True)
        #    upper_95_confidence = y_pred + 1.96 * sigma
        #    lower_95_confidence = y_pred + 1.96 * sigma

        import os.path
        import numpy as np
        
        try:
            import joblib
            HAS_JOBLIB = True
        except:
            HAS_JOBLIB = False

        from . GPR import GPR
        
        gpr = None
        if HAS_JOBLIB:
            if filename is not None:
                if os.path.isfile(filename):
                    gpr = joblib.load(filename)

        if gpr is None:
            x  = np.array( self.GetBinCenters() )
            y  = np.array( self.GetBinValues() )
            dy = np.array( self.GetBinErrors() )

            gpr = GPR(x,y,dy,
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

            if HAS_JOBLIB:
                if filename is not None:
                    joblib.dump(gpr,filename)

        return gpr

    
    def UseGPRInterp(self,
                     filename=None,
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
        """Creates a Gaussian Process Regression object that fits to the bin
        values and standard errors. The object is internally stored as
        self.gpr

        Parameters
        ----------
        filename : str, optional
            If the file exists, then read the file as a serialized pickle
            of the GPR object. If the file does not exist, construct the
            GPR object and save it to file. If None, then construct the
            GPR object without any file operations.

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
        gpr : ndfes.GPR
            The GPR interpolation object
            
        """
        
        self.gpr = self.__CreateGPR(\
                    filename=filename,
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


    def UseRBFInterp(self,
                     filename=None,
                     epsilon=100.,
                     minsize=0,
                     maxerr=0.5):
        """Creates a multiquadrtic radial basis function interpolator
        and stores it in self.rbf

        Parameters
        ----------
        filename : str, default=None
            If filename is present and exists, then read the RBF object from 
            the pickled file.  Otherwise, the RBF will be constructed and
            saved to the file, if present

        epsilon : float, default=100
            The RBF shape parameter

        minsize : int, default=0
            If a bin has fewer than minsize samples, then it is not included
            as part of the RBF fit.

        maxerr : float, default=0.5 (kcal/mol)
            If a bin was excluded from the RBF fit, and the resulting
            interpolated free energy disagrees with the bin value by more 
            than this tolerance, then the bin is entirely removed from the
            free energy surface.

        Returns
        -------
        None
            The object is stored as self.rbf
        """
        from . RBF import RBF
        import numpy as np
        import pickle
        import os

        if self.rbf is not None:
            return
        if filename is not None:
            if os.path.exists(filename):
                fh = open(filename,"rb")
                self.rbf = pickle.load(fh)
                fh.close()

        isnew=False
        if self.rbf is None:
            isnew=True
            dimisper = [ dim.isper for dim in self.grid.dims ]
            #dimisper = [ False for dim in self.grid.dims ]
            cpts = []
            cvals = []
            cerrs = []
            if minsize <= 1:
                for sbin in self.bins:
                    cpts.append( self.bins[sbin].center )
                    cvals.append( self.bins[sbin].value )
                    cerrs.append( self.bins[sbin].stderr )
            else:
                gidxs = self.BinsWithAtLeastMinSamples(minsize)
                for gidx in gidxs:
                    cpts.append( self.bins[gidx].center )
                    cvals.append( self.bins[gidx].value )
                    cerrs.append( self.bins[gidx].stderr )
            cpts = np.array(cpts)
            cvals = np.array(cvals)
            cerrs = np.array(cerrs)
            self.rbf = RBF(cpts,cvals,cerrs,epsilon,dimisper,dimrange=360)

            if minsize > 1:
                gidxs = self.BinsWithFewerThanMinSamples(minsize)
                if len(gidxs) > 0:
                    cpts = []
                    cvals = []
                    for gidx in gidxs:
                        cpts.append( self.bins[gidx].center )
                        cvals.append( self.bins[gidx].value )
                    cpts = np.array(cpts)
                    cvals = np.array(cvals)
                    res = self.rbf.GetValues(cpts,return_std=False,
                                             return_deriv=False)
                    for i in range(len(gidxs)):
                        if abs(cvals[i]-res.values[i]) > maxerr:
                            del self.bins[gidxs[i]]
                        

        if isnew and filename is not None:
            fh = open(filename,"wb")
            pickle.dump(self.rbf,fh)
            fh.close()

        if self.gpr is not None:
            self.gpr = None


    def StripBins(self,nmin):
        from . MBAR import MBAR
        gidxs = self.BinsWithAtLeastMinSamples(nmin)
        bins = {}
        for gidx in gidxs:
            bins[gidx] = self.bins[gidx]
        return MBAR(self.grid,bins)
    
            
    def BinsWithAtLeastMinSamples(self,nmin):
        gidxs = [ gidx for gidx,sbin in sorted(self.bins.items()) if sbin.size >= nmin ]
        return gidxs
        
    def BinsWithFewerThanMinSamples(self,nmin):
        gidxs = [ gidx for gidx,sbin in sorted(self.bins.items()) if sbin.size < nmin ]
        return gidxs
        
    def UseARBFInterp(self,
                      delta,
                      epsilon=100.):
        """Creates an approximate multiquadrtic radial basis 
        function interpolator and stores it in self.rbf

        Parameters
        ----------
        epsilon : float, default=100
            The RBF shape parameter
        """
        from . RBF import ARBF
        if delta > 0:
            self.rbf = ARBF(delta,self.bins,self.grid,epsilon,dimrange=360)
        else:
            self.UseRBFInterp(epsilon=epsilon)

            
    def UseWAVGInterp(self,minsize,order,niter):
        from . WAVG import WAVG
        self.wavg = WAVG(self,minsize,order,niter)

        
    def CptInterp(self,xpts,return_std=False,return_deriv=False,k=100):
        """Computes the RBF or GPR fit values (and optionally the standard 
        errors and function gradients) at arbitrary points

        Parameters
        ----------        
        xpts : list of lists or numpy.ndarray shape=(npts,ndim)
            A list of evaluation points

        return_std : bool, default=False
            If True, then return the standard error at the evaluation points

        return_deriv : bool, default=False
            If True, then return the feature gradients at the evalution points

        k : float, default=100
            Umbrella potential penalty applied to points that are not
            located within an occupied bin

        Returns
        -------
        ndfes.EvalT
            A container holding the values, errors, and feature derivatives.
            The EvalT.values, EvalT.errors are numpy.array's shape=(npts,).
            EvalT.derivs is a (npts,ndim) array.  The EvalT.errors and 
            EvalT.derivs elements can be None, depending on the values of
            return_std and return_deriv
        """
        import numpy as np
        from . EvalT import EvalT
        
        # if not self.gpr and not self.rbf:
        #     raise Exception("Attempted to call ndfes.FES.CptInterp without "+
        #                     "first calling ndfes.FES.UseGPRInterp or "+
        #                     "ndfes.FES.UseRBFInterp")
        
        xpts  = np.array(xpts)
        cs    = np.zeros( xpts.shape )
        pens  = np.zeros( (xpts.shape[0],) )
        dpens = np.zeros( xpts.shape )
        for i,x in enumerate(xpts):
            cs[i,:],pens[i],dpens[i,:] = self.GetInterpCrd(x,k=k)

        if self.rbf is not None:
            res = self.rbf.GetValues(cs,return_std=return_std,
                                     return_deriv=return_deriv)
        elif self.gpr is not None:
            res = self.gpr.GetValues(cs,return_std=return_std,
                                     return_deriv=return_deriv)
        elif self.wavg is not None:
            res = self.wavg.GetValues(cs,return_std=return_std,
                                      return_deriv=return_deriv)
        else:
            #raise Exception("CptInterp called, but no interpolation object"+
            #                " has been initialized")
            vals = np.array(self.GetBinValues(pts=cs))
            errs = np.array(self.GetBinErrors(pts=cs))
            ders = np.zeros( (vals.shape[0],self.grid.ndim) )
            res = EvalT(vals,ders,errs)
        res.values += pens
        if return_deriv:
            res.derivs += dpens
        return res
    

    def ShiftInterpolatedValues(self,e):
        """Sets the y0 attribute, which is subtracted from all interpolated
        values

        Parameters
        ----------
        e : float
            The value to be subtracted from all interpolated values
        """

        if self.rbf is not None:
            self.rbf.ShiftInterpolatedValues(e)
        if self.gpr is not None:
            self.gpr.ShiftInterpolatedValues(e)
        if self.wavg is not None:
            self.wavg.ShiftInterpolatedValues(e)
            

    def ShiftFES(self,path_pts,
                 zerobyhist=False,
                 zerobypath0=False,
                 zerobypath1=False,
                 interp=None,
                 oobk=100):
        """Shift the bin values and interpolations by choosing a zero
        of energy. If path_pts is None or zerobyhist=True, then the
        zero of energy is the minimum bin free energy value. If
        path_pts is not None, then the free energy is evaluated along
        the path. If zerobypath0 or zerobypath1 are True, then the
        free energy at one of the end points is chosen; if both are
        False, then the minimum free energy along the path is chosen.
        If the free energy is evaluated along the path, then the interp
        argument decides how the free energy is interpolated.

        Parameters
        ----------
        path_pts : numpy.ndarray, shape=(npts,ndim), optional
            Coordinates along the path. This can be None.

        zerobyhist: bool, default=False
            Ignore the path and choose the zero of energy to be the lowest
            bin free energy

        zerobypath0: bool, default=False
            The start of the path defines the zero of energy
            If zerobypath0 == zerobypath1 == False and path_pts != None,
            then the minimum energy along the path defines the zero

        zerobypath1: bool, default=False
            The end of the path defines the zero if energy
            If zerobypath0 == zerobypath1 == False and path_pts != None,
            then the minimum energy along the path defines the zero

        interp: str, optional
            If None, then the interpolator is automatically detected.
            If 'none', then an interpolator is not used

        oobk: float, default=100
            Force constant penalty added to the free energy when interpolated
            in an out-of-bounds area
        """
        
        import numpy as np
        
        has_path = False
        if path_pts is not None:
            path_pts = np.array(path_pts)
            if path_pts.shape[0] > 1:
                has_path = True

        if interp is None:
            interp = 'none'
            if self.rbf is not None:
                interp = 'rbf'
            if self.gpr is not None:
                interp = 'gpr'
            if self.wavg is not None:
                interp = 'wavg'
        else:
            if interp != "none" and interp != "rbf" \
               and interp != "gpr" and interp != "wavg" \
                   and interp != "bspl" and interp != "arbf":
                raise Exception(f"Invalid interp {interp}")
        
        minval = 0
        if zerobyhist or not has_path:
            vals = [ x for x in self.GetBinValues()
                     if x is not None ]
            if len(vals) > 0:
                minval = min(vals)
        elif has_path:
            if interp == 'none':
                vals = [x for x in self.GetBinValues(pts=path_pts)
                        if x is not None]
            else:
                vals = self.CptInterp(path_pts,k=oobk).values
            if zerobypath0:
                minval = vals[0]
            elif zerobypath1:
                minval = vals[-1]
            else:
                minval = min(vals)
        self.ShiftBinValues( minval )
        self.ShiftInterpolatedValues( minval )

                
    def GetPenalizedBorderFES(self,Penalty):
        import copy
        from . GridUtils import BasicWrap
        from . GridUtils import LinearPtsToMeshPts
        import numpy as np
        from . MBAR import MBAR
        
        ndim = self.grid.ndim
        obins = copy.deepcopy(self.bins)
        dsizes = [ self.grid.dims[dim].size for dim in range(ndim) ]

        def INTWRAP(i,n):
            return (i%n+n)%n
        
        for gidx in self.bins:
            bidx = self.bins[gidx].bidx
            loffs = []
            for dim in range(ndim):
                off = []
                if self.grid.dims[dim].isper:
                    off = [ INTWRAP(bidx[dim]-1,dsizes[dim]),
                            bidx[dim],
                            INTWRAP(bidx[dim]+1,dsizes[dim]) ]
                else:
                    for d in [-1,0,1]:
                        b = bidx[dim]+d
                        if b >= 0 and b < dsizes[dim]:
                            off.append(b)
                loffs.append(off)
            pts = LinearPtsToMeshPts(loffs)
            gpts = [ self.grid.CptGlbIdxFromBinIdx(pt) for pt in pts ]
            nmissing = 0
            maxfe = -1.e+10
            for g in gpts:
                if not g in self.bins:
                    nmissing += 1
                else:
                    maxfe = max(maxfe,self.bins[g].value)
            #print(nmissing,obins[gidx].value,obins[gidx].value+nmissing * 5)
            #obins[gidx].value += (nmissing/(len(gpts)-1)) * Penalty
            if nmissing > 0:
                wmiss = (nmissing/(len(gpts)-1))
                whave = 1-wmiss
                obins[gidx].value = whave * obins[gidx].value \
                    + wmiss * (maxfe + Penalty)
        return MBAR( self.grid, obins )

    
    def GetBootstrapFES(self,stderr=None):
        import copy
        from numpy.random import normal
        from . MBAR import MBAR
        obins = copy.deepcopy(self.bins)            
        for gidx in obins:
            if stderr is not None:
                disp = normal(0.0,scale=stderr)
            else:
                disp = normal(0.0,scale=obins[gidx].stderr)
            obins[gidx].value += disp
        return MBAR( self.grid, obins )


    def AddPenaltyBuffers(self,minsize,nlayers):
        xgrid = self.grid
        xFES = self.AddPenaltyBuffer(minsize)
        for i in range(1,nlayers):
            dbg = (i == (nlayers-1))
            xFES = xFES.AddPenaltyBuffer(0,dbg=dbg)

        return xFES

    
    def AddPenaltyBuffer(self,minsize,dbg=False):
        from . MBAR import MBAR
        from . SpatialBin import SpatialBin
        import copy
        
        class TripleT(object):
            def __init__(self,gidx,bidx,fevalue):
                import copy
                self.gidx = gidx
                self.bidx = copy.deepcopy(bidx)
                self.fevalue = fevalue

        DELTAV = 0.5
                
        ndim = self.grid.ndim
        xgrid = self.grid.MakeBufferedGrid(1)

        occgidxs =  self.BinsWithAtLeastMinSamples(minsize)
        bins = {}
        for ibin,ogidx in enumerate(occgidxs):
            sbin = self.bins[ogidx]
            bidxs = xgrid.GetBinIdx( sbin.center )
            ngidx = xgrid.CptGlbIdxFromBinIdx(bidxs)
            bins[ngidx] = SpatialBin(bidxs,sbin.value,sbin.stderr,sbin.entropy,sbin.size)
            bins[ngidx].center = sbin.center
        #oldgidxs = [ idx for idx in bins ]
            
        xFES = MBAR( xgrid, bins )

        newidxs = {}
        
        for gidx,sbin in sorted(xFES.bins.items()):
            fevalue = sbin.value
            midxs = xFES.grid.GetMeshIdxs( sbin.bidx, 1, True )
            for mbidx in midxs:
                mgidx = xFES.grid.CptGlbIdxFromBinIdx(mbidx)
                if mgidx not in xFES.bins:
                    if mgidx in newidxs:
                        newidxs[mgidx].fevalue = max(newidxs[mgidx].fevalue,fevalue)
                    else:
                        newidxs[mgidx] = TripleT( mgidx, mbidx, fevalue )
        
        for gidx in newidxs:
            if gidx in xFES.bins:
                raise Exception(f"gidx {gidx} already in xFES.bins")
            bidx = newidxs[gidx].bidx
            fevalue = newidxs[gidx].fevalue
            sbin = SpatialBin(bidx,fevalue+DELTAV,0,0,0)
            sbin.center = xFES.grid.GetBinCenter(bidx)
            xFES.bins[gidx] = sbin
            
        return xFES
    
    
    # def GetDensity(self,nquad=3,T=298,k=None,req=None):
    #     """Returns the integrated probability density within each bin
        
    #     Parameters
    #     ----------
    #     nquad : int, default=3
    #         The number of quadature points to use in each dimension

    #     T : float, default=298
    #         The temperature (K) of the target distribution

    #     k : numpy.array, dtype=float, shape=(ndim,)
    #         The umbrella potential force constant (kcal/mol)

    #     req : numpy.array, dtype=float, shape=(ndim,)
    #         The umbrella potential location (kcal/mol)

    #     Returns
    #     -------
    #     rho : numpy.array, dtype=float, shape=(nbins,)
    #         The density of each spatial bin, accessed via
    #         for idx,gidx,sbin in enumerate(sorted(self.bins.items())):
    #               p = rho[idx]
    #               center = sbin.center
    #     """
        
    #     import scipy.constants
    #     import numpy as np
        
    #     Jperkcal = scipy.constants.calorie * 1000 / scipy.constants.Avogadro
    #     boltz = scipy.constants.Boltzmann / Jperkcal
    #     beta = 1./(boltz*T)
    #     cpts,qwts = self.grid.GetQuadMesh(nquad)
    #     Q=0.
    #     rho=[]
    #     for gidx,sbin in sorted(self.bins.items()):
    #         cbin = np.array(sbin.center)
    #         qpts = cbin + cpts
    #         #print(cbin,cpts,qpts)
    #         F = self.CptInterp(qpts).values
    #         if k is not None and req is not None:
    #             W = np.dot( qwts, np.sum( (qpts-req)**2, axis=1) )
    #             es = np.exp(-beta*(F+W))
    #         else:
    #             es = np.exp(-beta*F)
    #         rho.append(np.dot(es,qwts))
    #     rho = np.array(rho)
    #     return rho/np.sum(rho)

    

    # def GetAvgPosition(self,k,req,nquad=3,T=298):
    #     """Returns the expected average position of the reaction
    #     coordinates if a biased sampling was performed with an
    #     umbrella potential with force constant k and position req
    #     and a temperature T.
        
    #     Parameters
    #     ----------
    #     k : numpy.array, dtype=float, shape=(ndim,)
    #         The umbrella potential force constant (kcal/mol)

    #     req : numpy.array, dtype=float, shape=(ndim,)
    #         The umbrella potential location (kcal/mol)

    #     nquad : int, default=3
    #         The number of quadature points to use in each dimension

    #     T : float, default=298
    #         The temperature (K) of the target distribution

    #     Returns
    #     -------
    #     avg : numpy.array, dtype=float, shape=(ndim,)
    #         The Boltzmann-weighted mean position
    #     """

    #     rho = GetDensity(nquad=nquad,T=T,k=k,req=req)
    #     avg=np.zeros( (self.grid.ndim,) )
    #     for idx,gidx,sbin in enumerate(sorted(self.bins.items())):
    #         for dim in range(self.grid.ndim):
    #             avg[dim] += rho[idx]*sbin.center[dim]
    #     return avg
    

    def GetBinXml(self,binvals=True):
        import xml.etree.ElementTree as ET
        bins = self.GetOccBins()
        nodes = []
        ndim = self.grid.ndim
        for gidx in sorted(bins):
            tnode = ET.Element("bin")
            tnode.attrib["idx"] = str(gidx)
            for idim in range(ndim):
                bnode = ET.SubElement(tnode,"bidx")
                bnode.attrib["idx"] = str(idim)
                bnode.text = str(bins[gidx].bidx[idim])
            if binvals:
                v = "%23.14e"%(bins[gidx].value)
                e = "%23.14e"%(bins[gidx].stderr)
                s = "%24.14e"%(bins[gidx].entropy)
                ET.SubElement(tnode,"val").text = v
                ET.SubElement(tnode,"err").text = e
                ET.SubElement(tnode,"re").text = s
            n = str(bins[gidx].size)
            ET.SubElement(tnode,"size").text = n
            nodes.append(tnode)
        return nodes
        
