#!/usr/bin/env python3

class PCV(object):
    """A class that stores the path collective variable definition

    Attributes
    ----------
    pts : numpy.ndarray, shape=(nsim,ndim)
        The points that define the path

    wts : numpy.ndarray, shape=(nsim,ndim)
        The weight associated with each point, such that
        a (squared) distance is measured with:
            D_i(x) = \sum_{d} wts[i,d] * (x[d]-pts[i,d])**2

    lam : float
        The PCV lambda parameter, such that the progress
        along the path is:
            p = (S(x)-1)/(nsim-1)
            S(x) = \sum_i i * exp(-lam*D_i(x)) / \sum_i exp(-lam*D_i(x))

    isangle : list of int, len=ndim
        Flags a dimension is an angle coordinate

    isper : list of int, len=ndim
        Flags a dimension is a periodic coordinate


    Methods
    -------
    """
    def __init__(self,pts,wts,isangle,isper,lam=None):
        import numpy as np
        import copy
        from . GridUtils import WrapAngleRelativeToRef
        self.pts = np.array(pts,copy=True)
        self.wts = np.array(wts,copy=True)
        self.isangle = copy.deepcopy(isangle)
        self.isper = copy.deepcopy(isper)
        nsim,ndim = self.pts.shape
        if len(self.isangle) != ndim:
            raise Exception(f"shape mismatch isangle {ndim} {len(isangle)}")
        if len(self.isper) != ndim:
            raise Exception(f"shape mismatch isper {ndim} {len(isper)}")
        if self.wts.shape[0] != nsim:
            raise Exception(f"shape mismatch nsim {nsim} {self.wts.shape[0]}")
        if self.wts.shape[1] != ndim:
            raise Exception(f"shape mismatch ndim {ndim} {self.wts.shape[1]}")
        if lam is None:
            Ds = []
            for i in range(nsim-1):
                D = 0
                for d in range(ndim):
                    w = 0.5*(self.wts[i+1,d]+self.wts[i,d])
                    dx = self.pts[i+1,d]-self.pts[i,d]
                    if self.isper[d]:
                        dx = WrapAngleRelativeToRef(dx,0)
                    D += w * dx * dx
                Ds.append(D)
            lam = 1. / np.mean(Ds)
        self.lam = lam


    def __call__(self,xs):
        """Evaluate the s and v values from an array of primitive collectives

        Parameters
        ----------
        xs : numpy.ndarray, shape=(n,ndim)
            A time series of primitive collective variables

        Returns
        -------
        sv : numpy.ndarray, shape=(n,2)
            The s and v values of each sample
        """
        import numpy as np
        from . GridUtils import WrapAngleRelativeToRef
        xs = np.array(xs)
        if len(xs.shape) == 1:
            xs = np.array([xs])
        n,ndim = xs.shape
        nref = self.pts.shape[0]
        sz = np.zeros( (n,2) )
        lspc = np.linspace(0,1,self.pts.shape[0])
        for i in range(n):
            ds = np.zeros( (nref,) )
            for j in range(nref):
                D = 0
                for k in range(ndim):
                    w = self.wts[j,k]
                    dx = xs[i,k]-self.pts[j,k]
                    if self.isper[k]:
                        dx = WrapAngleRelativeToRef(dx,0)
                    D += w * dx * dx
                ds[j] = D
            #ds = np.dot( self.wts, (xs[i,:]-self.pts)**2, dim=1 )
            es = np.exp(-self.lam*ds)
            sumes = es.sum()
            sz[i,0] = np.dot(lspc,es)/sumes
            sz[i,1] = -np.log(sumes)/self.lam
        return sz
    

    @classmethod
    def from_plumed(cls,fname):
        """Read the last PATH command from the plumed input file to
        create the PCV object

        Parameters
        ----------
        fname : str
            The name of the plumed input file
        """
        import os
        from pathlib import Path
        from collections import defaultdict as ddict
        
        class VarT(object):
            def __init__(self,line):
                self.line = line.strip()
                self.name,self.cmd = self.line.split(":",1)
                self.isper = None
                self.isangle = None
                self.args = []
                if "PERIODIC=NO" in self.cmd:
                    self.isper = False
                elif "PERIODIC=" in self.cmd:
                    self.isper = True
                    self.isangle = True
                    cs = self.cmd.split()
                    ele = [ e for e in cs
                            if "PERIODIC=" in e ][0]
                    res = ele.split("=")[-1]
                    vals = [float(x) for x in res.split(",")]
                    if vals[0] != -180 or vals[1] != 180:
                        raise Exception("Periodic coordinate does not range "
                                        +f"from -180 to +180 on line: {line}")
                elif "DISTANCE" in self.cmd:
                    self.isper = False
                    self.isangle = False
                elif "ANGLE" in self.cmd:
                    self.isper = False
                    self.isangle = True
                elif "TORSION" in self.cmd:
                    self.isper = True
                    self.isangle = True
                if "ARG=" in self.cmd:
                    cs = self.cmd.split()
                    ele = [ e for e in cs
                            if "ARG=" in e ][0]
                    res = ele.split("=")[-1]
                    self.args = res.split(",")
                    
                    
        fh=open(fname,"r")
        ref=None
        lam=None
        path=None

        uvars = ddict(str)
        
        for line in fh:
            line = line.split("#",1)[0]
            if ":" in line and "RESTRAINT" not in line:
                uvar = VarT(line)
                uvars[uvar.name] = uvar
                
            if "PATH" in line:
                path=True
                cs = line.strip().split()
                for i in range(len(cs)):
                    if "REFERENCE" in cs[i]:
                        if "=" in cs[i]:
                            k,v = cs[i].split("=")
                            ref=v
                        else:
                            ref = cs[i+1]
                    if "LAMBDA" in cs[i]:
                        if "=" in cs[i]:
                            k,v = cs[i].split("=")
                            lam = float(v)
                        else:
                            lam = float(v)


        for v in uvars:
            if uvars[v].isangle is None and len(uvars[v].args)>0:
                for u in uvars[v].args:
                    if u in uvars:
                        if uvars[u].isangle is not None:
                            uvars[v].isangle = uvars[u].isangle
                            break

        isangle = []
        isper = []
        for i in range(200):
            name = f"rc{i+1}"
            if name in uvars:
                isangle.append(uvars[name].isangle)
                isper.append(uvars[name].isper)
            else:
                break
                            
        if path is None:
            raise Exception(f"Could not find PATH command in {fname}")
        if ref is None:
            raise Exception(f"Missing REFERENCE in PATH-command in {fname}")
        if lam is None:
            raise Exception(f"Missing LAMBDA in PATH-command in {fname}")
        pinp = Path(fname)
        pref = Path(ref)
        tname = pref
        tried_names = [str(tname)]
        if not os.path.exists(str(tname)):
            tname = pinp.absolute().parents[0] / pref
            tried_names.append(str(tname))
        if not os.path.exists(str(tname)):
            tname = pinp.absolute().parents[0] / pref.name
            tried_names.append(str(tname))
        if not os.path.exists(str(tname)):
            raise Exception(f"Ref PDB in {fname} is {ref}, but could "
                            +f"not find any of: {tried_names}")
        return cls.from_pdb(str(tname),lam=lam,isangle=isangle,isper=isper)

    
    @classmethod
    def from_pdb(cls,fname,lam=None,isangle=None,isper=None):
        """Read the PCV path from a plumed-style PDB file
        The reference PDB file should look something like:

        DESCRIPTION: a reference point.
        REMARK WEIGHT=1.0
        REMARK ARG=rc1,rc2
        REMARK rc1=-1.4 rc2=-2.5
        REMARK sigma_rc1=1.
        REMARK sigma_rc2=1.
        END
        DESCRIPTION: a reference point.
        REMARK WEIGHT=1.0
        REMARK ARG=rc1,rc2
        REMARK rc1=1.4 rc2=2.5
        REMARK sigma_rc1=1.
        REMARK sigma_rc2=1.
        END

        Parameters
        ----------
        fname : str
            The name of the pdb file
        
        lam : float, optional
            The PCV lambda parameter. If None (default), then calculate
            lam = 1 / <D>, where <D> is the average distance metric 
            between adjacent images. D is defined as follows:
            D_i(x) = \sum_d w_{id} (x_d-xref_{id})**2
        """
        import numpy as np
        import os

        fact = (np.pi/180)**2
        
        if not os.path.exists(fname):
            raise Exception(f"File not found {fname}")
        
        fh=open(fname,"r")
        wts=[]
        rcs=[]
        ndim=0
        myrc=[]
        myw=[]
        iline=0
        for line in fh:
            iline += 1
            if "END" in line:
                if ndim > 0:
                    if len(myrc)!=ndim:
                        raise Exception(f"ndim mismatch {len(myrc)} expected "
                                        +f"{ndim} on line {iline} in file {pdb}")
                ndim = len(myrc)
                if len(myw) != ndim:
                    myw = [1]*ndim
                wts.append(myw)
                rcs.append(myrc)
                myw=[]
                myrc=[]
            elif "WEIGHT" in line:
                #myw = float(line.strip().split("=")[-1])
                pass
            elif "sigma" in line:
                cs = line.replace("REMARK","").strip().replace("="," ").split()
                if "sigma_rc" not in cs[0]:
                    raise Exception(f"Expected sigma_rc in {cs[0]} on line {iline} "
                                    +f"in file {pdb}")
                i = int(cs[0].replace("sigma_rc",""))
                while len(myw) < i:
                    myw.append(1.)
                myw[i-1] = float(cs[1])
            
            elif "REMARK" in line and "ARG" not in line and "sigma" not in line:
                cs = line.replace("REMARK","").strip().replace("="," ").split()
                if len(cs) % 2 != 0:
                    raise Exception(f"Expected key/value pairs on line {iline} "
                                    +f"in file {pdb} but saw:\n{line}")
                if ndim > 0:
                    if len(cs)//2 != ndim:
                        raise Exception(f"ndim mismatch {len(cs)//2} expected "
                                        +f"{ndim} on line {iline} in file {pdb}:\n"
                                        +f"{line}")
                n = len(cs)//2
                for i in range(n):
                    var = "rc%i"%(i+1)
                    if cs[0+i*2] != var:
                        raise Exception(f"variable {cs[0+i*2]} found "
                                        +f"expected {var} on line {iline} "
                                        +f"in file {pdb}:\n"
                                        +f"{line}")
                for i in range(n):
                    myrc.append( float( cs[1+i*2] ) )

        rcs = np.array(rcs)
        nsim,ndim = rcs.shape
        myisangle = [0]*ndim
        myisper   = [0]*ndim
        if isangle is not None:
            for k in range(ndim):
                myisangle[k] = isangle[k]
        else:
            for k in range(ndim):
                if abs(wts[0,k]-fact) < 1.e-6:
                    isangle[k]=1
        if isper is not None:
            for k in range(ndim):
                myisper[k] = isper[k]

        return cls(rcs,wts,myisangle,myisper,lam=lam)

    
    @classmethod
    def from_pts(cls,pts,isangle,isper,lam=None):
        import numpy as np
        pts = np.array(pts)
        wts = np.zeros( pts.shape )
        wts[:,:] = 1
        if len(isangle) != pts.shape[1]:
            raise Exception(f"Size mismatch {len(isangle)} vs {pts.shape[1]}")
        if len(isper) != pts.shape[1]:
            raise Exception(f"Size mismatch {len(isper)} vs {pts.shape[1]}")
        for k in range(len(isangle)):
            if isangle[k]:
                wts[:,k] = (np.pi/180)**2
        return cls(pts,wts,isangle,isper,lam=lam)

    
    @classmethod
    def from_disangs(cls,disangs,lam=None):
        import numpy as np
        nsim = len(disangs)
        ndim = len(disangs[0].restraints)
        for i in range(nsim):
            if len(disangs[i].restraints) != ndim:
                raise Exception(f"Disang has {len(disangs[i].restraints)} "
                                +f" restraints; expected {ndim}")
        pts=np.zeros( (nsim,ndim) )
        isangle = [0]*ndim
        isper = [0]*ndim
        for i in range(nsim):
            for k in range(ndim):
                res = disangs[i].restraints[k]
                pts[i,k] = res.r2
                isangle[k] = res.angle
                isper[k] = res.dihed
        return cls.from_pts(pts,isangle,isper,lam=lam)
    
    
    def SavePDB(self,fname):
        fh = open(fname,"w")
        nsim,ndim = self.pts.shape
        for isim in range(nsim):
            fh.write("DESCRIPTION: a reference point.\n")
            fh.write("REMARK WEIGHT=1.0\n")
            args = ",".join( [ "rc%i"%(k+1) for k in range(ndim) ] )
            fh.write(f"REMARK ARG={args}\n")
            fh.write("REMARK")
            for k in range(ndim):
                fh.write(" rc%i=%.13e"%(k+1,self.pts[isim,k]))
            fh.write("\n")
            for k in range(ndim):
                fh.write("REMARK sigma_rc%i=%.13e\n"%(k+1,self.wts[isim,k]))
            fh.write("END\n")
            
