#!/usr/bin/env python3

class PathSpl(object):
    """Class that defines a parametric curve, which could be
    an Akima, Linear, or potentially other curve type.

    Attributes
    ----------
    stype : str
        The spline type. Either : "akima", "linear"

    smooth : bool
        If False, then the spline control points are the
        same thing as the input points. If True, then the
        spline control points are obtained upon smoothing
        the input points

    ipts : numpy.ndarray, shape=(npts,ndim)
        The input points

    spl : ndfes.PCurve 
        The spline object

    Methods
    -------
    """
    def __init__(self,stype,smooth,ipts,ts=None):
        """
        Parameters
        ----------
        stype : string
            Either 'akima' or 'linear'
        
        smooth : bool
            If true, then the input points must be smoothed before constructing
            the parametric spline

        ipts : numpy.ndarray, shape=(npts,ndim)
            The input points. If smooth=False, then these points are the
            control points defining the parametric curve. If smooth=True,
            then the smoothed points are the control points.

        ts : optional, numpy.ndarray, shape=(npts,)
            If present, then smooth is ignored and these are assumed to be the
            spline progress variables
        """
        import numpy as np
        from . PathUtils import PCurve
        from . SmoothCurve import SmoothCurve_IterReflectedAvg
        
        self.stype = stype.lower()
        if ts is None:
            self.smooth = smooth
        else:
            self.smooth = False
        self.ipts = np.array(ipts,copy=True)
        
        linear = False
        if self.stype == "linear":
            linear = True

        cpts = np.array(ipts,copy=True)
        if self.smooth:
            cpts = SmoothCurve_IterReflectedAvg(cpts,3,11,1)

        self.spl = PCurve(cpts,fixt=False,linear=linear,t=ts)


    def __str__(self):
        return f"PathSpl(stype={self.stype},smooth={self.smooth},npts={self.ipts.shape[0]},ndim={self.ipts.shape[1]})"

    
    @classmethod
    def from_xml(cls,node):
        """Construct from an xml node. The node is expected to have
        the following children:

        <smooth> 0 or 1 </smooth>

        <type> 0 or 1 </type> (0 = linear, 1 = akima)

        <pt idx="ipt">
            <rc dim="idim"> val </rc>
            ...
        </pt>
        ...

        
        Parameters
        ----------
        node : ElementTree.Element
            The xml node to read from
        """
        import numpy as np
        import xml.etree.ElementTree as ET

        npts = 0
        ndim = 0
        nt = 0
        for cnode in node.findall('pt'):
            npts += 1
            if cnode.find('t') is not None:
                nt += 1
            if npts == 1:
                ndim = 0
                for dnode in cnode.findall('rc'):
                    ndim += 1

        ipts = np.zeros( (npts,ndim) )
        ts = None
        if nt == npts:
            ts = np.zeros( (npts,) )
    
        for cnode in node.findall('pt'):
            i = int(cnode.get('idx'))
            if ts is not None:
                tnode = cnode.find('t')
                ts[i] = float(tnode.text)
            for dnode in cnode.findall('rc'):
                dim = int(dnode.get('dim'))
                val = float(dnode.text)
                ipts[i,dim] = val
                
        stype = int(node.find('type').text)
        if stype == 0:
            stype = "linear"
        else:
            stype = "akima"
        smooth = int(node.find('smooth').text)
        if smooth == 0:
            smooth = False
        else:
            smooth = True

        return cls(stype,smooth,ipts,ts=ts)

    
    def GetXml(self):
        """Returns an xml node

        Returns
        -------
        node : ElementTree.Element
            The xml node
        """
        import xml.etree.ElementTree as ET

        node = ET.Element("path")
        if self.stype == "linear":
            ET.SubElement(node,"type").text = "0"
        elif self.stype == "akima":
            ET.SubElement(node,"type").text = "1"
        else:
            raise Exception(f"Invalid stype '{self.stype}'")
        #if self.smooth:
        #    ET.SubElement(node,"smooth").text = "1"
        #else:
        #    ET.SubElement(node,"smooth").text = "0"
        ET.SubElement(node,"smooth").text = "0"
        spl = self.spl
        npts = spl.x.shape[0]
        ndim = spl.x.shape[1]
        for i in range(npts):
            cnode = ET.SubElement(node,"pt")
            cnode.attrib["idx"] = "%i"%(i)
            tnode = ET.SubElement(cnode,"t")
            tnode.text = "%23.14e"%(spl.t[i])
            for dim in range(ndim):
                dnode = ET.SubElement(cnode,"rc")
                dnode.attrib["dim"] = "%i"%(dim)
                #dnode.text = "%21.12e"%(self.ipts[i,dim])
                dnode.text = "%21.12e"%(spl.x[i,dim])
        return node

        
    def GetValue(self,t):
        """Evaluate the parametric curve at the specified t-value.

        Parameters
        ----------
        t : float
            The parametric coordinate

        Returns
        -------
        vals : numpy.ndarray, shape=(ndim,)
            The coordinate at the specified t-value
        """
        return self.spl.GetValue(t)


    def GetControlPts(self):
        """Return the spline control points

        Returns
        -------
        vals : numpy.ndarray, shape=(npt,ndim)
            Spline control points
        """
        import numpy as np
        return np.array( self.spl.x, copy=True )

    
    def GetProgressValues(self):
        """Return the control point progress values

        Returns
        -------
        vals : numpy.ndarray, shape=(npt,)
            Spline control points
        """
        import numpy as np
        return np.array( self.spl.t, copy=True )

    
    def GetInputPts(self):
        """Return the spline (pre-smoothed) input points

        Returns
        -------
        vals : numpy.ndarray, shape=(npt,ndim)
            Spline control points
        """
        import numpy as np
        return np.array( self.ipts, copy=True )

    
    

class PathSims(object):
    """A class that holds the simulated reaction coordinates and force
    constants

    Attributes
    ----------
    rcs : numpy.ndarray, shape=(nsim,ndim)
        The reaction coordinates of each simulation

    fcs : numpy.ndarray, shape=(nsim,ndim)
        The force constants of each simulation

    Methods
    -------
    """
    def __init__(self,rcs,fcs):
        """Constructor

        Parameters
        ----------
        rcs : numpy.ndarray, shape=(nsim,ndim)
            The reaction coordinates of each simulation

        fcs : numpy.ndarray, shape=(nsim,ndim)
            The force constants of each simulation
        """
        import numpy as np
        self.rcs = np.array(rcs,copy=True)
        self.fcs = np.array(fcs,copy=True)


    def __str__(self):
        if self.rcs is None:
            return f"PathSims(npts=0,ndim=0)"
        else:
            return f"PathSims(npts={self.rcs.shape[0]},ndim={self.rcs.shape[1]})"
        
    @classmethod
    def from_xml(cls,node):
        """Construct from xml"""
        import numpy as np
        simrcs = None
        simfcs = None
        if node:
            npts = 0
            for tnode in node.findall("pt"):
                npts += 1
                if npts == 1:
                    ndim = 0
                    for qnode in tnode.findall("rc"):
                        ndim += 1
            simrcs = np.zeros( (npts,ndim) )
            simfcs = np.zeros( (npts,ndim) )
        
            for tnode in node.findall("pt"):
                i = int( tnode.get("idx") )
                for qnode in tnode.findall("rc"):
                    dim = int( qnode.get("dim") )
                    val = float( qnode.text )
                    simrcs[i,dim] = val
                for qnode in tnode.findall("fc"):
                    dim = int( qnode.get("dim") )
                    val = float( qnode.text )
                    simfcs[i,dim] = val
        return cls(simrcs,simfcs)

    
    def GetXml(self):
        """Returns an xml node

        Returns
        -------
        node : ElementTree.Element
            The xml node
        """
        import xml.etree.ElementTree as ET
        node = ET.Element("sims")
        npts = self.rcs.shape[0]
        ndim = self.rcs.shape[1]
        for i in range(npts):
            tnode = ET.SubElement(node,"pt")
            tnode.attrib["idx"] = "%i"%(i)
            for dim in range(ndim):
                qnode = ET.SubElement(tnode,"rc")
                qnode.attrib["dim"] = "%i"%(dim)
                qnode.text = "%21.12e"%(self.rcs[i,dim])
            for dim in range(ndim):
                qnode = ET.SubElement(tnode,"fc")
                qnode.attrib["dim"] = "%i"%(dim)
                qnode.text = "%21.12e"%(self.fcs[i,dim])
        return node
        

class PathIter(object):
    """Class that holds the spline and simulation data for an optimization
    iteration. The data is the INPUT path to the iteration. The output
    path is the the input of the next iteration. For iteration 0, one would
    write the input path of iteration 0 and the output path from the
    optimization. All future iterations would only write their output paths.

    Attributes
    ----------
    path : PathSpl
        The spline definition

    sims : PathSims
        The actual simulations. If this is iteration 0, then these are
        the simulations performed as the initial guess. When writing
        the data for all other iterations, these are the proposed simulations
        to be performed.  The number of simulations is not necessarily the
        same at each iteration (the initial guess may have a different
        number for example).  Nor are the number of simulations necessarily
        the same as the number of control points defining the path spline.

    Methods
    -------
    """
    def __init__(self,path,sims):
        """Constructor

        Parameters
        ----------
        path : PathSpl
            The spline definition
        
        sims : PathSims
            The latest set of simulations that were performed. It is the
            analysis of these simulations that yield the next guess.
        """
        import numpy as np
        from copy import deepcopy
        self.path = deepcopy( path )
        self.sims = deepcopy( sims )


    def __str__(self):
        psims = "None"
        if self.sims is not None:
            psims = str(self.sims)
        return f"PathIter({str(self.path)},{psims})"
    
        
    @classmethod
    def from_xml(cls,node):
        """Construct from xml
        
        Parameters
        ----------
        node : ElementTree.Element
            The xml node to read from
        """
        inode = node.find("path")
        if not inode:
            raise Exception("Could not find \"path\"")

        path = PathSpl.from_xml(inode)

        inode = node.find("sims")
        if inode:
            sims = PathSims.from_xml(inode)
        else:
            sims = None

        return cls(path,sims)

    
    def GetXml(self):
        """Returns an xml node

        Returns
        -------
        node : ElementTree.Element
            The xml node
        """
        import xml.etree.ElementTree as ET
        node = ET.Element("iter")
        node.append( self.path.GetXml() )
        if self.sims is not None:
            node.append( self.sims.GetXml() )
        return node

    
    def GetValue(self,t):
        """Evaluate the parametric curve at the specified t-value.

        Parameters
        ----------
        t : float
            The parametric coordinate

        Returns
        -------
        vals : numpy.ndarray, shape=(ndim,)
            The coordinate at the specified t-value
        """
        return self.path.GetValue(t)


    def GetControlPts(self):
        """Return the spline control points

        Returns
        -------
        vals : numpy.ndarray, shape=(npt,ndim)
            Spline control points
        """
        return self.path.GetControlPts()

    
    def GetProgressValues(self):
        """Return the control point progress values

        Returns
        -------
        vals : numpy.ndarray, shape=(npt,)
            Spline control points
        """
        return self.path.GetProgressValues()

    
    def GetInputPts(self):
        """Return the spline (pre-smoothed) input points

        Returns
        -------
        vals : numpy.ndarray, shape=(npt,ndim)
            Spline control points
        """
        return self.path.GetInputPts()

    
    
class PathOpt(object):
    """Stores a collection of path iterations

    Attributes
    ----------
    iters : list of PathIter
        The input paths of each iteration
    """
    def __init__(self,iters):
        """
        Parameters
        ----------
        paths : list of PathIter
        """
        from copy import deepcopy
        self.iters = deepcopy( iters )

    def __len__(self):
        return len(self.iters)

    def __getitem__(self,i):
        return self.iters[i]

    def __iter__(self):
        return iter(self.iters)


    def __str__(self):
        return f"PathOpt(len={len(self.iters)})"

    
    @classmethod
    def from_xml(cls,node,onlylast=False):
        """Construct from xml node

        Parameters
        ----------
        node : ElementTree.Element
            The xml node to read from
        """
        iters = []
        if not onlylast:
            for pnode in node.findall("iter"):
                iters.append( PathIter.from_xml(pnode) )
        else:
            last = None
            for pnode in node.findall("iter"):
                last = pnode
            iters.append( PathIter.from_xml(last) )
        return cls(iters)

    
    @classmethod
    def from_file(cls,fname,onlylast=False):
        """Construct from xml file

        fname : str
            The xml filename to read
        """
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(fname)
            root = tree.getroot()
            return cls.from_xml(root,onlylast)
        except Exception as xmlmsg:
            import ndfes.FTSM
            import sys
            import os
            import pathlib
            import glob
            from . amber import Disang

            
            opt = ndfes.FTSM.FTSMOpt.load(fname)
            absfname = os.path.abspath(fname)
            stype = "akima"
            if "linear" in absfname:
                stype = "linear"
            fpath = pathlib.Path(absfname)
            topdir = fpath.parent.parent
            
            iters = []
            for ip,p in enumerate(opt.paths):
                pspl = PathSpl(stype,False,p.splpts,ts=p.splts)
                ndim = p.splpts.shape[1]
                
                if ip == 0:
                    cdir = topdir / "init"
                else:
                    cdir = topdir / ("it%02i"%(ip))

                rcs = []
                fcs = []
                for iimg in range(200):
                    dfile = cdir / ("img%02i.disang"%(iimg+1))
                    if os.path.exists(dfile):
                        disang = Disang(dfile)
                        rc = [ disang.restraints[ires].r2 for ires in range(ndim) ]
                        fc = [ disang.restraints[ires].rk2 for ires in range(ndim) ]
                        rcs.append(rc)
                        fcs.append(fc)
                    else:
                        break
                sims = None
                if len(rcs) > 0 and len(fcs) > 0:
                    sims = PathSims( rcs, fcs )
                iters.append( PathIter(pspl,sims) )

            o = cls(iters)
            sys.stderr.write(f"Detected version 2 path pkl file named {fname}\n")
            nname = pathlib.Path(fname).with_suffix(".xml")
            if os.path.exists(nname):
                sys.stderr.write(f"Not writing {nname} because it already exists\n")
            else:
                sys.stderr.write(f"Writing version 3 file named {nname}\n")
                o.SaveXml(nname)
            if onlylast:
                iters = [iters[-1]]
            return cls(iters)

        
    def GetXml(self):
        """Returns an xml node

        Returns
        -------
        node : ElementTree.Element
            The xml node
        """
        import xml.etree.ElementTree as ET
        node = ET.Element("opt")
        for path in self.iters:
            node.append( path.GetXml() )
        return node

    
    def SaveXml(self,fname):
        """Write xml file

        Parameters
        ----------
        fname : str
            The xml filename to write
        """
        import xml.etree.ElementTree as ET
        import xml.dom.minidom as md
        import os
        
        root = self.GetXml()
        xmlstr = ET.tostring(root,encoding="unicode")
        dom = md.parseString( xmlstr )     
        # To parse string instead use: dom = md.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="  ")
        # remove the weird newline issue:
        pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines()
                                      if s.strip()])
        fh = open(fname,"w")
        fh.write(pretty_xml)
        fh.close()



def ReadPaths(fname,ndim,onlylast=False):
    """Read one-or-more paths from a file

    It will first try to load the file as a PathOpt xml file.
    If that fails, it will interpret it as a text file.
    If that fails, it will try to interpret it as a Metafile.

    If it is interpretted as a text file, then columns 3 to
    2+ndim are assumed to be the reaction coordinate values,
    and column 2 is assumed to be the progress value.
    The value of ndim is not used otherwise.

    If the file could not be read as xml, then the path splines
    are constructed using akima splines rather than linear
    interpolation.

    Parameters
    ----------
    fname : str
        Name of file

    ndim : int
        Dimensionality of the paths.

    onlylast : bool, default=False
        If True, then only return the last path (if there was
        more than 1 path).

    Returns
    -------
    pathopt : ndfes.PathOpt
        The container of path iterations.
    """
    import numpy as np
    try:
        return PathOpt.from_file(fname,onlylast=onlylast)
    except Exception as xmlerr:
        try:
            data = np.loadtxt(fname)[:,1:2+ndim]
            ts = data[:,0]
            rcs = data[:,1:]
            pspl = PathSpl( "akima", False, rcs )
            psim = None
            return PathOpt( [PathIter( pspl, psim )] )
        except Exception as txterr:
            from . Metafile import Metafile
            mfile = Metafile(fname)
            rcs = np.array([ t.xs for t in mfile.trajs ])
            fcs = np.array([ t.ks for t in mfile.trajs ])
            pspl = PathSpl( "akima", False, rcs )
            psim = PathSims( rcs, fcs )
            return PathOpt( [PathIter( pspl, psim )] )
