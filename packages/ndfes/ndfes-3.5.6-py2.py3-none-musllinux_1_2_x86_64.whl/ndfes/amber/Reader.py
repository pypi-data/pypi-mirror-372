#!/usr/bin/env python3


def ReadCrds( trajfile ):
    """Reads coordinates from a NetCDF trajectory file

    Parameters
    ----------
    trajfile : str
        Filename of the Amber NetCDF trajectory file

    Returns
    -------
    crds : numpy.array, shape=(nframe,natom,3)
        The coordinates of each atom in each frame
    """
    import numpy
    try:
        from scipy.io import netcdf
        nc = netcdf.NetCDFFile(trajfile,'r',mmap=False)
    except:
        from scipy.io import netcdf_file
        nc = netcdf_file(trajfile,'r',mmap=False)

    fvar = nc.variables['coordinates'] # angstrom
    nframe,nat,xyzidx = fvar.shape
    data = numpy.zeros( (nframe,nat,xyzidx) )
    data[:,:,:] = fvar[:,:,:]
    fvar = None
    nc.close()
    return data


def ReadFrcs( trajfile ):
    """Reads forces from a NetCDF trajectory file

    Parameters
    ----------
    trajfile : str
        Filename of the Amber NetCDF trajectory file

    Returns
    -------
    frcs : numpy.array, shape=(nframe,natom,3)
        The forces of each atom in each frame
    """
    import numpy
    try:
        from scipy.io import netcdf
        nc = netcdf.NetCDFFile(trajfile,'r',mmap=False)
    except:
        from scipy.io import netcdf_file
        nc = netcdf_file(trajfile,'r',mmap=False)
        
    fvar = nc.variables['forces'] # kcal/mol/angstrom
    nframe,nat,xyzidx = fvar.shape
    data = numpy.zeros( (nframe,nat,xyzidx) )
    data[:,:,:] = fvar[:,:,:]
    fvar = None
    nc.close()
    return data



def ReadEnergies(mdout):
    """Reads an Amber mdout file and returns the total potential energy
    of each output frame.

    Parameters
    ----------
    mdout : str
        The mdout filename

    Returns
    -------
    ene : numpy.array, shape=(nframe,)
        The EPtot energies encountered in the file, excluding the summaries
        of averages and RMS fluctuations
    """
    import numpy
    es=[]
    fh=open(mdout,"r")
    skip=False
    for line in fh:
        if "A V E R A G E S" in line or "R M S  F L U C" in line:
            skip=True
        if "EPtot      =" in line:
            if skip:
                skip=False
            else:
                cs=line.strip().split()
                es.append( float(cs[-1]) )
    return numpy.array(es)



def ReadCrdsAndBox( trajfile ):
    """Reads coordinates and unit cell from a NetCDF trajectory file

    Parameters
    ----------
    trajfile : str
        Filename of the Amber NetCDF trajectory file

    Returns
    -------
    crds : numpy.array, shape=(nframe,natom,3)
        The coordinates of each atom in each frame

    box : numpy.array, shape=(nframe,6)
        The unit cell
    """
    
    import numpy
    try:
        from scipy.io import netcdf
        nc = netcdf.NetCDFFile(trajfile,'r',mmap=False)
    except:
        from scipy.io import netcdf_file
        nc = netcdf_file(trajfile,'r',mmap=False)
        
        

    #for key in nc.variables:
    #    print(key,nc.variables[key].shape)
    #    if "cell" in key:
    #        print(nc.variables[key][:])

    fvar = nc.variables['coordinates'] # angstrom
    nframe,nat,xyzidx = fvar.shape
    data = numpy.zeros( (nframe,nat,xyzidx) )
    data[:,:,:] = fvar[:,:,:]
    fvar = None

    box = numpy.zeros( (nframe,6) )
    box[:,0:3] = nc.variables['cell_lengths'][:,:]
    box[:,3:6] = nc.variables['cell_angles'][:,:]
    
    nc.close()
    return data, box



def ReadCrdsFrcsAndBox( trajfile ):
    """Reads coordinates, forces, and unit cell from a NetCDF trajectory file

    Parameters
    ----------
    trajfile : str
        Filename of the Amber NetCDF trajectory file

    Returns
    -------
    crds : numpy.array, shape=(nframe,natom,3)
        The coordinates of each atom in each frame

    frcs : numpy.array, shape=(nframe,natom,3)
        The forces of each atom in each frame

    box : numpy.array, shape=(nframe,6)
        The unit cell
    """
    import numpy

    try:
        from scipy.io import netcdf
        nc = netcdf.NetCDFFile(trajfile,'r',mmap=False)
    except:
        from scipy.io import netcdf_file
        nc = netcdf_file(trajfile,'r',mmap=False)
        
    crds = None
    if 'coordinates' in nc.variables:
        fvar = nc.variables['coordinates'] # angstrom
        nframe,nat,xyzidx = fvar.shape
        crds = numpy.zeros( (nframe,nat,xyzidx) )
        crds[:,:,:] = fvar[:,:,:]
        fvar = None

    frcs = None
    if 'forces' in nc.variables:
        fvar = nc.variables['forces'] # kcal/mol/angstrom
        nframe,nat,xyzidx = fvar.shape
        frcs = numpy.zeros( (nframe,nat,xyzidx) )
        frcs[:,:,:] = fvar[:,:,:]
        fvar = None

    box = None
    if 'cell_lengths' in nc.variables and \
       'cell_angles' in nc.variables:
        box = numpy.zeros( (nframe,6) )
        box[:,0:3] = nc.variables['cell_lengths'][:,:]
        box[:,3:6] = nc.variables['cell_angles'][:,:]

    nc.close()
    return crds,frcs,box




def ReadAvgCrds(tfiles,aidxs,masses,ref=None,callback=None):
    """Returns the time-averaged coordinates from 1-or-more trajectory
    files after root-mean-squared fitting the coordinates to the
    specified list of atoms

    Parameters
    ----------
    tfiles : list of str
        The list of netcdf trajectory filenames (more than one if the
        trajectory was restarted several times)

    aidxs : list of int
        The 0-based indexes of the atoms involved in the RMS fit.
        The coordinates are first translated to move the first atom in
        aidxs to the origin

    masses : list of float
        The mass of each atom in the aidxs

    ref : optional, numpy.array, shape=(len(aidxs),3)
        The reference coordinates used to perform RMS overlays
        If None, then the first frame from the trajectory is used

    Returns
    -------
    crds : numpy.array, shape=(len(aidxs),3)
        The average coordinates after RMS fitting
    """
    import numpy as np
    from . Geometry import PerformRmsOverlay
    from . Geometry import RemoveCoM
    from pathlib import Path
    
    wts = np.array(masses)
    allcrds = []
    if ref is not None:
        if ref.shape[0] != len(aidxs) or ref.shape[1] != 3:
            raise Exception(f"ref has shape {ref.shape}, but expected "
                            "({len(aidxs),3})")
    #ref = None
    for tfile in tfiles:
        pf = Path(tfile)
        if not pf.is_file():
            raise Exception("File not found %s"%(pf))
        inpcrds = ReadCrds(tfile)
        if callback is not None:
            inpcrds = callback(inpcrds)
        crds = inpcrds[:,aidxs,:]
        inpcrds = None
        if ref is None:
            ref = crds[0,:,:]
        for frame in range(crds.shape[0]):
            rms,rmscrd = PerformRmsOverlay(crds[frame,:,:],ref,wts)
            allcrds.append(rmscrd)
    if len(allcrds) == 0:
        raise Exception("No coordinates read from %s"%(str(tfiles)))
    allcrds = np.array(allcrds)
    avgcrds = np.mean(allcrds,axis=0)
    avg = RemoveCoM( avgcrds, wts )
    
    return avg
    
    # import pytraj as pt

    # alltraj = pt.Trajectory(top=pfile)
    # for tfile in tfiles:
    #     crd,box = ReadCrdsAndBox(tfile)
    #     alltraj.append(crd)
    #     alltraj._append_unitcells( box )

    # sele = "@" + ",".join(["%i"%(i+1) for i in aidxs])
    # alltraj.center('@%i origin'%(aidx[0]))
    # alltraj.rmsfit(ref=0,mask=sele,masses=True)
    # if strip:
    #     alltraj.strip("!(%s)"%(sele))
    # return np.mean( alltraj.xyz, axis=0 )



def ReadAvgCrdsAndFrcs(tfiles,ffiles,aidxs,masses):
    """Returns the time-averaged coordinates from 1-or-more trajectory
    files after root-mean-squared fitting the coordinates to the
    specified list of atoms

    Parameters
    ----------
    tfiles : list of str
        The list of netcdf trajectory filenames (more than one if the
        trajectory was restarted several times) containing the coordinates

    ffiles : list of str
        The list of netcdf trajectory filenames (more than one if the
        trajectory was restarted several times) containing the forces

    aidxs : list of int
        The 0-based indexes of the atoms involved in the RMS fit.
        The coordinates are first translated to move the first atom in
        aidxs to the origin

    masses : list of float
        The mass of each atom in the aidxs

    Returns
    -------
    crds : numpy.array, shape=(len(aidxs),3)
        The average coordinates after RMS fitting

    frcs : numpy.array, shape=(len(aidxs),3)
        The average force after RMS fitting
    """
    import numpy as np
    from . Geometry import CptRmsTransform
    from . Geometry import RemoveCoM

    wts = np.array(masses)
    allcrds = []
    allfrcs = []
    ref = None
    for tfile,ffile in zip(tfiles,ffiles):
        crds = ReadCrds(tfile)[:,aidxs,:]
        frcs = ReadFrcs(ffile)[:,aidxs,:]
        
        if crds.shape[0] != frcs.shape[0]:
            raise Exception("Nframe (%i vs %i) "%(crds.shape[0],
                                                  frcs.shape[0]) +
                            " mismatch between %s and %s"%(tfile,ffile))
        
        if ref is None:
            ref = crds[0,:,:]
        for frame in range(crds.shape[0]):
            rms,rot,com,refcom = CptRmsTransform(crds[frame,:,:],ref,wts)
            rmscrd = np.dot(crds[frame,:,:]-com,rot) + refcom
            rmsfrc = np.dot(frcs[frame,:,:],rot)
            allcrds.append(rmscrd)
            allfrcs.append(rmsfrc)
    allcrds = np.array(allcrds)
    allfrcs = np.array(allfrcs)
    avg = RemoveCoM( np.mean(allcrds,axis=0), wts )
    avgfrc = np.mean(allfrcs,axis=0)
    return avg,avgfrc

    


def CalcFrameRMSValues(tfiles,aidxs,masses,ref=None):
    """For each frame in the trajectory file(s), perform a RMS
    fit to a reference structure and return the list of RMS
    values.

    Parameters
    ----------
    tfiles : list of str
        The list of netcdf trajectory filenames (more than one if the
        trajectory was restarted several times)

    aidxs : list of int
        The 0-based indexes of the atoms involved in the RMS fit.
        The coordinates are first translated to move the first atom in
        aidxs to the origin

    masses : list of float
        The mass of each atom in the aidxs

    ref : optional, numpy.array, shape=(len(aidxs),3)
        The reference coordinates used to perform RMS overlays
        If None, then the first frame from the trajectory is used

    Returns
    -------
    rmsvals : numpy.array, shape=(nframe,)
        The RMS values

    crds : numpy.array, shape=(nframe,len(aidxs),3)
        The RMS fitted coordinates
    """
    import numpy as np
    from . Geometry import PerformRmsOverlay
    from . Geometry import RemoveCoM
    from pathlib import Path

    rmsvals = []
    wts = np.array(masses)
    allcrds = []
    if ref is not None:
        if ref.shape[0] != len(aidxs) or ref.shape[1] != 3:
            raise Exception(f"ref has shape {ref.shape}, but expected "
                            "({len(aidxs),3})")
    #ref = None
    for tfile in tfiles:
        pf = Path(tfile)
        if not pf.is_file():
            raise Exception("File not found %s"%(pf))
        inpcrds = ReadCrds(tfile)
        crds = inpcrds[:,aidxs,:]
        inpcrds = None
        if ref is None:
            ref = crds[0,:,:]
        for frame in range(crds.shape[0]):
            rms,rmscrd = PerformRmsOverlay(crds[frame,:,:],ref,wts)
            allcrds.append(rmscrd)
            rmsvals.append(rms)
    if len(allcrds) == 0:
        raise Exception("No coordinates read from %s"%(str(tfiles)))
    allcrds = np.array(allcrds)
    rmsvals = np.array(rmsvals)
    #avgcrds = np.mean(allcrds,axis=0)
    #avg = RemoveCoM( avgcrds, wts )
    
    return rmsvals,allcrds
    
