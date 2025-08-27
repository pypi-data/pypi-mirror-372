#!/usr/bin/env python3

from . FES import FES


class vFEP(FES):
    """
    A class used to store and retrieve free energy results from a vFEP
    calculation.  Specifically, the stored data consists of the vFEP
    B-spline parameters at the grid point corners required to evaluate
    the potential within the bins occupied by observed samples.
 
    Attributes
    ----------
    grid : VirtualGrid
        The range and size information of each dimension

    bins : dict (key : int, value : SpatialBin)
        A dictionary of occupied bins.  The key values are the global bin
        index, and the values are SpatialBin objects containing the free
        energy and standard error

    bsplorder : int
        B-spline order

    nbspl : int
        The number of corners accessible to a bin along each dimension

    params : dict (key : int, value : tuple (float,float) )
        A dictionary of B-spline parameters. The key values are the
        global corner index, and the values are the parameter and bootstrap
        uncertainty of the parameter.

    y0 : float
        A value to subtract from all B-spline interpolated values

    findbin : scipy.interpolate.RegularGridInterpolator
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
        interpolations using the stored object.  The default behavior
        of CptInterp is to evaluate the free energies from the vFEP
        B-spline basis.

    rbf : ndfes.RBF
        Interpolates the free energy surface using a Radial Basis
        Function fit. Note that this attribute is None by default.
        One should instead use the UseRBFInterp to initialize the
        interpolator and then use the CptInterp method to perform 
        interpolations using the stored object.  The default behavior
        of CptInterp is to evaluate the free energies from the vFEP
        B-spline basis.

    Methods
    -------
    """
    
    def __init__(self, grid, bins, bsplorder, params, kb=None):
        """
        Parameters
        ----------
        grid : VirtualGrid
            The range and size information of each dimension

        bins : dict (key : int, value : SpatialBin)
            A dictionary of occupied bins.

        bsplorder : int
            B-spline order

        params : dict (key : int, value : tuple (float,float) )
            A dictionary of B-spline parameters

        kb : float, optional
            The value of Boltzmann's constant in the desired
            energy units. Default is None, which will produce
            an error if it is used mathematically.
        """

        import numpy as np

        
        super().__init__(grid,bins,kb=kb)
        self.bsplorder = bsplorder
        self.params = params
        self.nbspl = bsplorder + bsplorder%2
        self.y0 = 0

        #
        # Compute the bin free energy values from the vFEP
        # B-spline parameters
        #
        
        for bidx in self.bins:
            #print(bidx,self.bins[bidx].center)
            c = [self.bins[bidx].center]
            res = self.GetValues(c,return_std=True)
            self.bins[bidx].value = res.values[0]
            self.bins[bidx].stderr = res.errors[0]
            self.bins[bidx].entropy = 0

        if False: # Check vFEP gradients
            for bidx in self.bins:
                c = [self.bins[bidx].center]
                res = self.GetValues(c,return_std=True,return_deriv=True)
                TOL=1.e-5
                for dim in range(len(c)):
                    c[0][dim] += TOL
                    hi = self.GetValues(c)
                    c[0][dim] -= 2*TOL
                    lo = self.GetValues(c)
                    d = (hi.values[0]-lo.values[0])/(2.*TOL)
                    print("%13.4e %13.4e %13.4e"%(res.derivs[0,dim],
                                                  d,res.derivs[0,dim]-d))

            
            

    def GetValues(self,xpts,return_std=False,return_deriv=False):
        """Computes the B-spline values (and optionally the standard errors and
        function gradients) at points that lie within occupied bins. This
        method is meant to be analogous to the ndfes.GPR routine; however,
        one would likely not want to use this method. Instead, one would
        call CptInterp, which considers periodicity and which can handle
        points that lie outside the bounds of the occupied bins

        Parameters
        ----------
        xpts : list of lists or numpy.ndarray shape=(npts,ndim)
            A list of evaluation points

        return_std : bool, default=False
            If True, then return the standard error at the evaluation points

        return_deriv : bool, default=False
            If True, then return the feature gradients at the evalution points

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
        import copy
        from . EvalT import EvalT
        from . Bspline import CptBsplineValues
        from . Bspline import CptBsplineValuesAndDerivs
        from . GridUtils import LinearPtsToMeshPts
        from . GridUtils import LinearWtsToMeshWts

        xs = np.array(xpts)
        
        if len(xs.shape) == 1:
            xs = np.atleast_2d(xs).T

        nvals = xs.shape[0]
        ndim = self.grid.ndim

        #print("eval @ %s"%("".join( ["%8.3f"%(c) for c in xs[0,:]] )) )
        
        values = np.zeros( (nvals,) )
        
        if return_deriv:
            derivs = np.zeros( (nvals,ndim) )
        else:
            derivs = None
            
        if return_std:
            errors = np.zeros( (nvals,) )
        else:
            errors = None

        for ix,pt in enumerate(xs):
            
            lidx=[]
            lwts=[]
            lder=[]
            if return_deriv:
                for dim in range(ndim):
                    bs,ws,ds = CptBsplineValuesAndDerivs(
                        pt[dim],self.grid.dims[dim].xmin,
                        self.grid.dims[dim].width,self.bsplorder)
                    if self.grid.dims[dim].isper:
                        for i in range(self.bsplorder):
                            bs[i]=bs[i]%self.grid.dims[dim].size
                    lidx.append(bs)
                    lwts.append(ws)
                    lder.append(ds)
                lwts = np.array(lwts)
                lder = np.array(lder)
            else:
                for dim in range(ndim):
                    bs,ws = CptBsplineValues(
                        pt[dim],self.grid.dims[dim].xmin,
                        self.grid.dims[dim].width,self.bsplorder)
                    if self.grid.dims[dim].isper:
                        for i in range(self.bsplorder):
                            bs[i]=bs[i]%self.grid.dims[dim].size
                    #print("dim %3i %s"%(dim,"".join(["%5i"%(h) for h in bs])))
                    lidx.append(bs)
                    lwts.append(ws)
                lwts = np.array(lwts)

            # Create a (order**ndim,ndim) array of corner indexes
            cidxs = LinearPtsToMeshPts(lidx)
            
            # Create a (npts,) array of global corner indexes
            npts = cidxs.shape[0]
            gcidxs = np.zeros( (npts,), dtype=int )
            #gcidxs = [0]*npts
            for ipt in range(npts):
                gidx = 0
                for dim in reversed(range(ndim)):
                    if self.grid.dims[dim].isper:
                        gidx = cidxs[ipt,dim] + \
                            gidx*self.grid.dims[dim].size
                    else:
                        gidx = cidxs[ipt,dim] + \
                            gidx*(self.grid.dims[dim].size+1)
                gcidxs[ipt] = gidx
                if gidx not in self.params:
                    spt = ",".join(["%8.3f"%(c) for c in pt])
                    sidx = ",".join(["%i"%(c) for c in cidxs[ipt,:]])
                    print("ndfes.vFEP.GetValues missing global corner index",
                          gidx)
                    print("Point %s => %s"%(spt,sidx))
                    

            #print(gcidxs.shape,type(gcidxs))
            # The vFEP B-spline parameters at the corner indexes
            fs = np.array( [self.params[idx][0] for idx in gcidxs ] )
            # The vFEP B-spline parameters uncertainties
            es = np.array( [self.params[idx][1] for idx in gcidxs ] )
            
            mwts = LinearWtsToMeshWts(lwts)

            #for ipt in range(len(gcidxs)):
            #    print("gidx %6i %s %20.10e %20.10e"%(gcidxs[ipt],",".join(["%5i"%(u) for u in cidxs[ipt,:]]),fs[ipt],mwts[ipt]))
            
            values[ix] = np.dot(mwts,fs) - self.y0
            if return_std:
                errors[ix] = np.sqrt(np.dot(mwts**2,es**2))
            if return_deriv:
                for dim in range(ndim):
                    twts = copy.deepcopy(lwts)
                    twts[dim] = lder[dim]
                    derivs[ix,dim] = np.dot(fs,LinearWtsToMeshWts(twts))

            #print("FES %12.4f\n"%(values[ix]))
        return EvalT(values,derivs,errors)

    
    def ShiftInterpolatedValues(self,e):
        """Sets the y0 attribute, which is subtracted from all interpolated
        values.

        Parameters
        ----------
        e : float
            The value to be subtracted from all interpolated values
        """
        
        self.y0 += e
        if self.rbf is not None:
            self.rbf.ShiftInterpolatedValues(e)
        if self.gpr is not None:
            self.gpr.ShiftInterpolatedValues(e)
        if self.wavg is not None:
            self.wavg.ShiftInterpolatedValues(e)


    def CptInterp(self,xpts,return_std=False,return_deriv=False,k=100):
        """Computes the interpolated values (and optionally the standard 
        errors and function gradients) at arbitrary points.  The default
        behavior is to evaluate the B-spline representation, unless the
        UseGPRInterp method has been called, in which case this evaluates
        the GPR fit interpolator

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
            res = self.GetValues(cs,return_std=return_std,
                                 return_deriv=return_deriv)
            
        res.values += pens
        if return_deriv:
            res.derivs += dpens
        return res


    def ResizeGrid(self,newgrid):
        """Returns a new vFEP object using the provided grid.  The grid
        dimensions and periodicity must be the same as the original
        grid. Furthermore, the new grid can only extend the ranges of
        the existing grid.

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
                raise Exception("Can't resize grid because widths are different")

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

        #print(offs)
        #exit(0)
            
        params = ddict( int )
        
        lcidx = []
        for dim in range(ndim):
            n=self.grid.dims[dim].size
            if self.grid.dims[dim].isper:
                lcidx.append( [ i for i in range(n) ] )
            else:
                lcidx.append( [ i for i in range(n+1) ] )
                
        cidxs = LinearPtsToMeshPts(lcidx)
        npts = cidxs.shape[0]
        for ipt in range(npts):
            oldgidx = 0
            newgidx = 0
            for dim in reversed(range(ndim)):
                if self.grid.dims[dim].isper:
                    oldgidx = cidxs[ipt,dim] + \
                        oldgidx*self.grid.dims[dim].size
                    newgidx = (cidxs[ipt,dim]+offs[dim]) + \
                        oldgidx*newgrid.dims[dim].size
                else:
                    oldgidx = cidxs[ipt,dim] + \
                        oldgidx*(self.grid.dims[dim].size+1)
                    newgidx = (cidxs[ipt,dim]+offs[dim]) + \
                        newgidx*(newgrid.dims[dim].size+1)
                    
            if oldgidx in self.params:
                params[ newgidx ] = self.params[ oldgidx ]

        bins = ddict( int )
        for gidx in self.bins:
            sbin = self.bins[gidx]
            newbidx=[ sbin.bidx[dim] + offs[dim]
                      for dim in range(ndim) ]
            newgidx=0
            for dim in reversed(range(ndim)):
                newgidx = newbidx[dim] + newgidx*newgrid.dims[dim].size
            bins[newgidx] = SpatialBin( newbidx,
                                        sbin.value,
                                        sbin.stderr,
                                        sbin.entropy,
                                        sbin.size )

        return vFEP(newgrid, bins, self.bsplorder, params)

    
    
    def GetXml(self):
        import xml.etree.ElementTree as ET
        mnode = ET.Element("model")
        ET.SubElement(mnode,"type").text = "VFEP"
        ET.SubElement(mnode,"order").text = str(self.bsplorder)
        if self.kb is not None:
            ET.SubElement(mnode,"kb").text = "%23.14e"%(self.kb)

        mnode.append( self.grid.GetXml() )
        bnodes = self.GetBinXml(binvals=True)
        for bnode in bnodes:
            mnode.append( bnode )

        for cidx in sorted(self.params):
            tnode = ET.SubElement(mnode,"corner")
            tnode.attrib["idx"] = str(cidx)
            v,e = self.params[cidx]
            v = "%23.14e"%(v)
            e = "%23.14e"%(e)
            ET.SubElement(tnode,"val").text = v
            ET.SubElement(tnode,"err").text = e
        
        return mnode
    
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
            interp = 'bspl'
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
