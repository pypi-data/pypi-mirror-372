#!/usr/bin/env python3

from . Trajectory import Trajectory
from pathlib import Path


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    

class Metafile(object):
    """A class that reads a metafile and stores a list of Trajectory objects

    Attributes
    ----------
    filename : str
        The name of the metafile

    ndim : int, optional
        If present, then it sets the number of dimensions. This is only useful
        if the metafile is used to specify a generalized bias rather than a
        harmonic bias. When a harmonic bias is used, the number of dimensions
        can be inferred from the number of columns in the metafile, but one
        must manually specify the number of dimensions when using a generalized
        bias.

    trajs : list of Trajectory
        The list of trajectories listed in the metafile. Each element of
        the list stores the Hamiltonian index, temperature, dumpave filename,
        and umbrella window locations and force constants

    Methods
    -------
    """
    def __init__(self,fname,ndim=None):
        """
        Parameters
        ----------
        fname : str
            The filename of the metafile
        """
        
        self.filename = fname
        self.trajs = []
        self.isharmonic = True
        self.ndim = ndim
        
        path = Path(self.filename)
        if not path.is_file():
            raise Exception("File not found: %s"%(self.filename))
        parent = path.parent

        fh = open(self.filename,"r")
        for line in fh:
            cs = line.strip().split()
            biasidx = None
            if len(cs) > 1:
                if len(cs) == 4:
                    self.isharmonic = False
                    xs = None
                    ks = None
                elif len(cs) < 5 or (len(cs)-3)%2 == 1:
                    raise Exception("Incorrect number of columns in "+
                                    "%s on line:\n%s"%(self.filename,line))
                hamidx = int(cs[0])
                temp = float(cs[1])
                dumpave = cs[2]
                if self.isharmonic:
                    xs = [ float(x) for x in cs[3::2] ]
                    ks = [ float(x) for x in cs[4::2] ]
                    self.ndim = len(xs)
                else:
                    biasidx = int(cs[3])

                if is_number(dumpave):
                    raise Exception(f"{dumpave} should be a filename, not a number")
                
                self.trajs.append( Trajectory(hamidx,temp,
                                              dumpave,xs,ks,
                                              prefix=parent,
                                              biasidx=biasidx,
                                              ndim=self.ndim) )

    def RelativeTo(self,newdir):
        """Returns a copy of the metafile object, but the dumpave
        locations are relative to a new location

        Parameters
        ----------
        newdir : str
            The directory where the new metafile will be written

        Returns
        -------
        m : ndfes.Metafile
            A new metafile whose path are relative to newdir
        """
        import pathlib
        import copy
        import os
        m = copy.deepcopy(self)
        p2meta = pathlib.Path(newdir).resolve()
        if not p2meta.is_dir():
            raise Exception("Directory not found: %s"%(p2meta))
        for t in m.trajs:
            dumpname = t.path.name
            p2dump = t.path.resolve().parent
            meta2dump = pathlib.Path(os.path.relpath(p2dump,start=p2meta)) / dumpname
            t.dumpave = "%s"%(meta2dump)
            t.path = meta2dump
            t.prefix = ""
        return m

    
    def write(self,fh,seen=[]):
        """Write the metafile to a file handle

        Parameters
        ----------
        fh : file handle
            The handle to which to write the contents

        seen : list of str, optional
            The list of seen dumpaves. A dumpave is only written
            if it has not already been seen.

        Returns
        -------
        seen : list of str
            The new list of seen dumpaves
        """
        for t in self.trajs:
            name = "%s"%(t.path)
            if name not in seen:
                fh.write("%i %6.2f %s"%(t.hamidx,t.temperature,t.path))
                if self.isharmonic:
                    s = " ".join( ["%12.6f %23.14e"%(x,k)
                                   for x,k in zip(t.xs,t.ks)] )
                else:
                    s = "%i"%(t.biasidx)
                fh.write(" %s\n"%(s))
                seen.append(name)
        return seen
            
                
    def GetTrajsFromHamIdx(self,hamidx):
        """Return a list of Trajectory objects for a given Hamiltonian
        index
        
        Parameters
        ----------
        hamidx : int
            The Hamiltonian index
            
        Returns
        -------
        trajs : list of Trajectory
            All trajectories generated from hamidx
        """
        return [ traj for traj in self.trajs
                     if traj.hamidx == hamidx ]

    def GetDumpavesFromHamidx(self,hamidx):
        """Return a list of dumpave filenames for a given Hamiltonian
        index

        Parameters
        ----------
        hamidx : int
            The Hamiltonian index
            
        Returns
        -------
        dumpaves : list of str
            All dumpave filenames generated from hamidx
        """
        return [ traj.dumpave for traj in self.GetTrajsFromHamIdx(hamidx) ]

        
            
                
        
