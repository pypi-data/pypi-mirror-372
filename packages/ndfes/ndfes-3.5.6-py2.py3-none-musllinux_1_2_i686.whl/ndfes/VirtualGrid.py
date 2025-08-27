#!/usr/bin/env python3


class VirtualGrid(object):
    """
    A class used to bin samples in multiple dimensions

    Attributes
    ----------
    dims : list of SpatialDim
        The range and size information of each dimension

    ndim : int
        The number of dimensions

    Methods
    -------
    """
    
    def __init__(self,dims):
        """
        Parameters
        ----------
        dims : list of SpatialDim
            The range and size information of each dimension

        """

        self.dims = dims
        self.ndim = len(self.dims)


        
    def Wrap(self,xs,range180=False):
        """Wraps a multidimensional sample within the range of each dimension,
        for those dimensions that are periodic

        Parameters
        ----------
        xs : list of float
            The multidimensional coordinate of the sample 

        range180 : bool, default=False
            If True, then wrap periodic coordinate around the origin
            [-180,180) rather than [0,360).

        Returns
        -------
        list of float
            The wrapped coordinate
        """
        
        return [self.dims[i].Wrap(xs[i],range180=range180)
                for i in range(self.ndim)]

    
    def DiffCrd(self,a,b):
        """Returns a difference vector using the minimum image convention

        Parameters
        ----------
        a : list of float
            The multidimensional coordinate of the sample 

        b : list of float
            The multidimensional coordinate of the sample 

        Returns
        -------
        ab : numpy.array, dtype=float, size=(ndim,)
            The wrapped difference a-b
        """
        import numpy as np
        ab = np.array(a)-np.array(b)
        for i in range(self.ndim):
            if self.dims[i].isper:
                w = self.dims[i].xmax - self.dims[i].xmin
                h = 0.5*w
                ab[i] = (ab[i]-h)%w-h
        return ab
        
    
    def GetBinIdx(self,xs):
        """Returns an array of integers that describe the bin containing the
        sample

        Parameters
        ----------
        xs : list of float
            The multidimensional coordinate of the sample 

        Returns
        -------
        list of int
            The bin index in each dimension containing the sample
        """
        
        return [self.dims[i].GetIdx(xs[i]) for i in range(self.ndim)]

    
    def CptGlbIdxFromBinIdx(self,bidx):
        """Converts the multidimensional bin indexes into a single, global
        index for the bin

        Parameters
        ----------
        bidx : list of int
            The bin index in each dimension

        Returns
        -------
        int
            The global bin index
        """
        
        gidx = 0
        for i in range(self.ndim-1,-1,-1):
            if bidx[i] is None:
                gidx = None
                break
            else:
                gidx = bidx[i] + gidx*self.dims[i].size
        return gidx

    
    def GetGlbBinIdx(self,xs):
        """Returns the global bin index of a sample

        Parameters
        ----------
        xs : list of float
            The multidimensional coordinate of the sample

        Returns
        -------
        int
            The global bin index
        """
        
        return self.CptGlbIdxFromBinIdx( self.GetBinIdx(xs) )

    
    def GetBinCenter(self,bidx):
        """Returns the spatial coordinates of a bin center

        Parameters
        ----------
        bidx : list of int
            The bin index in each dimension

        Returns
        -------
        list of float
            The multidimensional coordinate of the bin center
        """
        
        return [ (bidx[i]+0.5)*self.dims[i].width + self.dims[i].xmin
                 for i in range(self.ndim) ]

    
    def GetRegGridCenters(self):
        """Return a N-dimensional regular grid of bin centers as a numpy 
        meshgrid.

        Returns
        -------
        numpy.ndarray (dtype=float,shape=see below)
            The numpy meshgrid of bin centers

            - For 1-dimensional systems, the ndarray has shape=(1,n0), where n0
              is the number of bin centers in the first dimension
            - For 2-dimensions: shape=(2,n0,n1)
            - For 3-dimensions: shape=(3,n0,n1,n2)
            Higher dimensionality follows a similar trend.

            Examples of using the meshgrid in a loop structure follows:
            - 1-dimension:
               for ix in range(mgrid.shape[1]):
                   print("x=",mgrid[0,ix])
                   center = mgrid[:,ix]
            - 2-dimensions:
               for ix in range(mgrid.shape[1]):
                   for iy in range(mgrid.shape[2]):
                       print("x=",mgrid[0,iy,ix],"y=",mgrid[1,iy,ix])
                       center = mgrid[:,iy,ix]
            - 3-dimensions:
               for ix in range(mgrid.shape[2]):
                   for iy in range(mgrid.shape[3]):
                       for iz in range(mgrid.shape[4]):
                           print("x=",mgrid[0,ix,iy,iz],
                                 "y=",mgrid[1,ix,iy,iz],
                                 "z=",mgrid[2,ix,iy,iz])
                           center = mgrid[:,ix,iy,iz]
        """

        import numpy as np
        grids = []
        for dim in self.dims:
            grids.append( dim.GetRegGridCenters() )
            #print(grids[-1].shape)
        mgrid = np.array( np.meshgrid(*grids,indexing='ij') )
        #print(mgrid.shape)
        return mgrid
        

    def GetRegGridEdges(self):
        """Return a N-dimensional regular grid of bin edges as a numpy 
        meshgrid.

        Returns
        -------
        mgrid : numpy.array, shape=(ndim,nx,ny,nz,...)
        """
        import numpy as np
        grids = []
        for dim in self.dims:
            grids.append( dim.GetRegGridEdges() )
        mgrid = np.array( np.meshgrid(*grids,indexing='ij') )
        return mgrid

    
    def GetRegGridCenterPts(self):
        """Return a list of N-dimensional points that form a regular grid of 
        bin centers

        Returns
        -------
        numpy.ndarray (dtype=float, shape=(npts,ndim))
            The slow (left) index is the number of points in the regular grid
            (the product of sizes from each dimension).  The fast (right) index
            is the number of dimensions.

            Examples of using the points:
            - 1-dimension:
                for ipt in range(pts.shape[0]):
                    print("x=",pts[ipt,0])
                    center = pts[ipt,:]
            - 2-dimensions:
                for ipt in range(pts.shape[0]):
                    print("x=",pts[ipt,0],"y=",pts[ipt,1])
                    center = pts[ipt,:]
            - 3-dimensions:
                for ipt in range(pts,shape[0]):
                    print("x=",pts[ipt,0],"y=",pts[ipt,1],"z=",pts[ipt,2])
                    center = pts[ipt,:]
        """

        from . GridUtils import GetPtsFromRegGrid
        return GetPtsFromRegGrid( self.GetRegGridCenters() )



    def GetRegGridEdgePts(self):
        """Return a list of N-dimensional points that form a regular grid of 
        bin edges

        Returns
        -------
        numpy.ndarray (dtype=float, shape=(npts,ndim))
            The slow (left) index is the number of points in the regular grid
            (the product of sizes from each dimension).  The fast (right) index
            is the number of dimensions.
        """

        from . GridUtils import GetPtsFromRegGrid
        return GetPtsFromRegGrid( self.GetRegGridEdges() )

        
    def GetQuadMesh(self,nquad):
        """Return a multidimensional Gauss-Legendre quadrature roots and
        weights that integrate a single histogram bin centered at the origin

        Parameters
        ----------
        nquad : int
            The quadrature rule used in each dimension

        Returns
        -------
        numpy.ndarray (dtype=float, shape=(nquad**ndim,ndim))
            The positions of the quadrature mesh. The first index 
            represents points on the mesh and the second index
            is the coordinate dimension

        numpy.array (dtype=float, shape=(nquad**ndim,)
            The quadrature weight of each point in the mesh
        """

        from scipy.special import roots_legendre
        from . GridUtils import LinearPtsToMeshPts
        from . GridUtils import LinearWtsToMeshWts
        pts=[]
        wts=[]
        xs,ws = roots_legendre(nquad)
        for dim in self.dims:
            dx = 0.5*dim.width
            qxs = xs*dx
            qws = ws*dx
            pts.append(qxs)
            wts.append(qws)
        pts = LinearPtsToMeshPts(pts)
        wts = LinearWtsToMeshWts(wts)
        return pts,wts

    def MakeBufferedGrid(self,nlayers):
        """Returns a new VirtualGrid object that extends the dimensions
        in all directions by including extra layers of bins
        
        Parameters
        ----------
        nlayers : int
            The number of extra bin layers

        Returns
        -------
        vgrid : VirtualGrid
            Extended grid
        """
        from . SpatialDim import SpatialDim
        dims = []
        for dim in self.dims:
            xmin  = dim.xmin
            xmax  = dim.xmax
            size  = dim.size
            isper = dim.isper
            width = dim.width
            if not isper:
                xmin -= nlayers*width
                xmax += nlayers*width
                size += 2*nlayers
            newdim=SpatialDim(xmin,xmax,size,isper)
            dims.append(newdim)
        return VirtualGrid(dims)
        
        
    def GetMeshIdxs(self,bidxs,nlayers,strict):
        from . GridUtils import LinearPtsToMeshPts
        
        def INTWRAP(i,n):
            return (i%n+n)%n
        
        didx = nlayers
        #nd = 2*didx+1
        alllidxs = []
        for idim,dim in enumerate(self.dims):
            dimsize = dim.size
            bidx = bidxs[idim]
            if dim.isper:
                lidxs = [ INTWRAP(bidx+idel,dimsize)
                          for idel in range(-didx,didx+1) ]
            else:
                lidxs = [ bidx+idel
                          for idel in range(-didx,didx+1) ]
                if strict:
                    for i,lidx in enumerate(lidxs):
                        if lidx < 0 or lidx >= dimsize:
                            raise Exception\
                                ("Programming error getting "+
                                 f"extended region dim={idim} "+
                                 f" i={i} k={lidx} dimsize={dimsize}")
            alllidxs.append(lidxs)
        return LinearPtsToMeshPts(alllidxs)

    def GetXml(self):
        import xml.etree.ElementTree as ET

        grid = ET.Element("grid")
        for idim in range(self.ndim):
            dim = self.dims[idim]
            
            dnode = ET.SubElement(grid,"dim")
            dnode.attrib["idx"]=str(idim)
            
            tnode = ET.SubElement(dnode,"xmin")
            tnode.text = "%.8f"%(dim.xmin)
            
            tnode = ET.SubElement(dnode,"xmax")
            tnode.text = "%.8f"%(dim.xmax)
            
            tnode = ET.SubElement(dnode,"size")
            tnode.text = str(dim.size)
            
            tnode = ET.SubElement(dnode,"isper")
            if dim.isper:
                tnode.text = "1"
            else:
                tnode.text = "0"
        return grid
            
    def WrapPath(self,pts,range180=False):
        """Wrap the first point to the periodic range, and then
        subsequent points are wrapped to the previous point using
        the minimum image convention

        Parameters
        ----------
        pts : numpy.ndarray, shape=(npt,ndim)
            The path points

        range180 : bool, default=False
            The first point is wrapped to the range [0,360).
            If range180=True, then it is wrapped to [-180,180).

        Returns
        -------
        opts : numpy.ndarray, shape=(npt,ndim)
            The wrapped points
        """
        import numpy as np
        ndim = self.ndim
        opts = [ self.Wrap( pts[0,:], range180=range180 ) ]
        for i in range(1,pts.shape[0]):
            d = opts[-1] + self.DiffCrd( pts[i,:], opts[-1] )
            opts.append( d )
        return np.array( opts )

    def WrapPathSegments(self,pts,range180=False):
        """Returns a path as a series of line segments such
        that all points in the path are within the periodic
        range.  This is usually only used for plotting
        purposes.

        Parameters
        ----------
        pts : numpy.ndarray, shape=(npt,ndim)
            The path points

        range180 : bool, default=False
            The points are wrapped to the range [0,360).
            If range180=True, then it is wrapped to [-180,180).

        Returns
        -------
        segs : list of numpy.ndarray(nsegpts,ndim)
            Each segment is wrapped to the periodic range
        """
        import numpy as np
        import copy
        opts = self.WrapPath(pts,range180=range180)
        
        segs = []
        cseg = [ opts[0,:] ]
        for i in range(1,opts.shape[0]):
            ppt = cseg[-1]
            wc = self.Wrap( opts[i,:], range180=range180 )
            dc = ppt + self.DiffCrd(opts[i,:],ppt)
            if np.linalg.norm( wc-dc ) < 1.e-8:
                cseg.append(wc)
            else:
                segs.append( copy.deepcopy(cseg) )
                cseg = [ wc ]
        if len(cseg) > 0:
            segs.append( copy.deepcopy(cseg) )
        for i in range(len(segs)):
            segs[i] = np.array(segs[i])
            #print(i,segs[i])
        return segs
        
