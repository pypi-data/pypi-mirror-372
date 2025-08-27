#!/usr/bin/env python3

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    

# def FindT(pt,refpts,refts):
#     rs = np.linalg.norm( pt-refpts, axis=1 )
#     return refts[np.argmin(rs)]


# def ReadPathFromDisangs(idxs,disangs):
#     import numpy as np
#     import ndfes
    
#     vals = []
#     for i in range(len(disangs)):
#         dis = ndfes.amber.Disang(disangs[i])
#         qs = [ 0.5*(dis.restraints[idx].r2+dis.restraints[idx].r3)
#                for idx in idxs ]
#         vals.append( qs )
#     return np.array(vals)


# def ReadFCsFromDisangs(idxs,disangs):
#     import numpy as np
#     import ndfes
    
#     fcs = []
#     for i in range(len(disangs)):
#         dis = ndfes.amber.Disang(disangs[i])
#         fc = [ 0.5*(dis.restraints[idx].rk2+dis.restraints[idx].rk3)
#                for idx in idxs ]
#         fcs.append( fc )
#     return np.array(fcs)




def GetSims(nsim,rcs):
    import numpy as np
    
    # number of paths
    npath = rcs.shape[0]-1

    # path lengths
    plens = np.array([ np.linalg.norm(rcs[i+1,:]-rcs[i,:])
                       for i in range(npath) ])
    
    # total length
    totlen = np.sum(plens)
    tlens = np.cumsum(plens) / totlen
    tlens[-1] = 1
    wins = []
    for i in range(nsim):
        if i == 0:
            wins.append( rcs[0,:] )
        elif i == nsim-1:
            wins.append( rcs[-1,:] )
        else:
            t = i/(nsim-1)
            #print("t=",t)
            pmin = 0
            tmin = 0
            tmax = 1
            for p in range(npath):
                if tlens[p] > t:
                    pmin = p
                    tmax = tlens[p]
                    if p == 0:
                        tmin = 0
                    else:
                        tmin = tlens[p-1]
                    break
            #print(tmin,tmax)
            w = (t-tmin)/(tmax-tmin)
            wins.append( (1-w) * rcs[pmin,:] + w * rcs[pmin+1,:] )

    wins = np.array(wins)
    return wins


def FindClosestWin(rc,wins):
    import numpy as np
    return np.linalg.norm( wins-rc, axis=1 ).argmin()
    
    

def WriteMdinFromTemplate(tmdin,fname):
    import pathlib
    import re
    
    fname = pathlib.Path(fname)
    disang = fname.with_suffix(".disang").name
    dumpave = fname.with_suffix(".dumpave").name
    
    fh = open(fname,"w")
    found_disang = False
    found_dumpave = False
    for line in tmdin:
        if "DISANG" in line:
            m = re.match(r"DISANG *=.*",line)
            if m:
                line = re.sub(r"DISANG *=.*",
                              "DISANG=%s"%(disang),
                              line)
                found_disang=True
        if "DUMPAVE" in line:
            m = re.match(r"DUMPAVE *=.*",line)
            if m:
                line = re.sub(r"DUMPAVE *=.*",
                              "DUMPAVE=%s"%(dumpave),
                              line)
                found_dumpave=True
        fh.write(line+"\n")
    fh.close()
    
    if not found_disang:
        raise Exception("DISANG field was not found in "
                        +"%s"%(fname))
    if not found_dumpave:
        raise Exception("DUMPAVE field was not found in "
                        +"%s"%(fname))
        


def WriteEquilScript(fname,init,first,last,rev,pad):
    import pathlib

    mmin = min(first,last)
    mmax = max(first,last)
    idxs = [ i for i in range(mmin,mmax) ]
    #print(idxs)
    if rev:
        idxs.reverse()

    if len(idxs) == 0:
        return
    
    fh = open(fname,"w")
    p = pathlib.Path(fname)
    name = p.name
    fh.write("""#!/bin/bash
set -e
set -u

#
# You can create a slurm script and run these
# commands in the following way:
#
# export LAUNCH="srun sander.MPI"
# export PARM="path/to/parm7"
# bash %s
#

if [ "${LAUNCH}" == "" ]; then
    echo 'bash variable LAUNCH is undefined. Defaulting to: export LAUNCH="sander"'
    export LAUNCH="sander"
fi

if [ "${PARM}" == "" ]; then
    echo 'bash variable PARM is undefined. Please: export PARM="/path/to/parm7"'
    exit 1
else
   if [ ! -e "${PARM}" ]; then
       echo "File not found: ${PARM}"
       exit 1
   fi
fi

if [ ! -e "%s.rst7" ]; then
    echo "File not found: %s.rst7"
    exit 1
fi

"""%(name,init,init))

    for idx in idxs:
        b = f"img%0{pad}i"%(idx)
        #print(f"${{LAUNCH}} -O -p ${{PARM}} -i {b}.mdin -o {b}.mdout -c {init}.rst7 -r {b}.rst7 -x {b}.nc -inf {b}.mdinfo\n")
        fh.write(f"${{LAUNCH}} -O -p ${{PARM}} -i {b}.mdin -o {b}.mdout -c {init}.rst7 -r {b}.rst7 -x {b}.nc -inf {b}.mdinfo\n")

        init = b
    

    

if __name__ == "__main__":

    import ndfes
    import ndfes.amber
    import argparse
    import numpy as np
    import pathlib
    import sys
    import re
    import shutil
    import os


    parser = argparse.ArgumentParser \
        ( formatter_class=argparse.RawDescriptionHelpFormatter,
          description="""
          This script helps to create an initial guess from which one can start
          the finite temperature string method. It is presumed that the user 
          has prepared and equilibrated one-or-more structures that approximate
          stationary point(s) on the reduced dimensional free energy surface.
          One needs to have prepared at least one structure (typically either
          the reactant or product structure). By "reactant" and "product" we 
          mean the two ends of a minimum free energy pathway. Furthermore, it 
          is presumed that the user has prepared two-or-more disang files that
          the initial path should pass through. One needs at least 2 disang 
          files to represent the two ends of the path. Given these disang and
          restart files, the script writes a series of NSIM output mdin and 
          output disang files that connect the input disang files via linear 
          interpolation. Furthermore, one-or-more shell scripts will be created
          that can be used to generate initial starting configurations for each
          of the NSIM states via a sequential series of short simulations from
          the nearest input restart file.
          """ )


    parser.add_argument \
        ("-d","--disang",
         help="template disang file",
         type=str,
        required=True )

    parser.add_argument \
        ("-i","--mdin",
         help="template mdin file",
         type=str,
         required=True )

    
    parser.add_argument \
        ("--min",
         help="Either a disang or coordinate restart (with velocities) "+
         "defining a proposed stationary point on the free energy surface. "+
         "If it is a disang file, then the script will check to see if "+
         "there is a corresponding restart file by replacing the '.disang' "
         "suffix with a '.rst7' suffix.  This option must be used at least "+
         "twice (once for the reactant and product, repsectively).",
         type=str,
         nargs='+',
         action='append',
         required=True )

    
    parser.add_argument \
        ("-n","--nsim",
         help="Number of windows in the string.",
         type=int,
         required=True )
    

    parser.add_argument \
        ("--pad",
         help="Length of the filename padding. Default: 3",
         type=int,
         default=3,
         required=False )


    
    parser.add_argument \
        ("-q","--dry-run",
         help="Don't prepare the outputs; only show what would be done",
         action='store_true',
         required=False )

    
    parser.add_argument \
        ("-o","--odir",
         help="Output directory",
         type=str,
         default="init",
         required=False )


    # try:
    #     import pkg_resources
    #     version = pkg_resources.require("ndfes")[0].version
    # except:
    #     version = "unknown"
    
    version = get_package_version("ndfes")

    
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format\
                        (version=version))


    args = parser.parse_args()
    args.pad = max(args.pad,1)

    tdisfile = pathlib.Path(args.disang)
    if not tdisfile.is_file():
        raise Exception("Template disang not found: %s"%(tdisfile))

    
    tmdinfile = pathlib.Path(args.mdin)
    if not tdisfile.is_file():
        raise Exception("Template mdin not found: %s"%(tmdinfile))


    
    disfiles = [pathlib.Path(item) for sublist in args.min for item in sublist]
    rstfiles = [None]*len(disfiles)
    for i in range(len(disfiles)):
        disfile = disfiles[i]
        rstfile = disfile.with_suffix(".rst7")
        
        if not disfile.is_file():
            raise Exception("File not found: %s"%(disfile))
        
        if disfile.suffix != ".disang":
            if rstfile.suffix == ".rst7":
                rstfiles[i] = disfile
                disfiles[i] = None
            else:
                raise Exception("Unrecognized file suffix: %s"%(disfile))
        elif rstfile.is_file():
            rstfiles[i] = rstfile

    nrst = 0
    for rst in rstfiles:
        if rst is not None:
            nrst += 1
    if nrst == 0:
        raise Exception("No restart files were found. You need at least one.")


    nsims = args.nsim

    if nsims < 2:
        raise Exception("--nsim must be >= 2")

    if nrst > nsims:
        raise Exception("--nsim must be at least as large as the number of restarts")

    if not args.dry_run:
        fh = open(tmdinfile,"r")
        tmdin = fh.read().split("\n")
        fh.close()


    tdisang = ndfes.amber.Disang( tdisfile )
    tdisang.ValidateTemplate()
    idxs = tdisang.GetTemplateIdxs()

    rcs = []
    fcs = []
    for i in range(len(disfiles)):
        if disfiles[i] is not None:
            d = ndfes.amber.Disang(disfiles[i])
            #print(idxs)
            #print(len(d.restraints))
            rcs.append( [ d.restraints[idx].r2 for idx in idxs ] )
        elif rstfiles[i] is not None:
            import parmed
            rst = parmed.load_file( str(rstfiles[i]) )
            crd = rst.coordinates[0,:,:]
            qs = tdisang.CptCrds(crd)
            rcs.append( [ qs[idx] for idx in idxs ] )

    rcs = np.array(rcs)
    fcs = np.array( [ tdisang.restraints[idx].rk2 for idx in idxs ] )

    wins = GetSims(nsims,rcs)
    rstgidxs = [None] * len(rstfiles)
    for i in range(len(rstfiles)):
        if rstfiles[i] is not None:
            rstgidxs[i] = FindClosestWin(rcs[i,:],wins)
    
    
    if not args.dry_run:
        name = pathlib.Path(args.odir)
        odir = name
        if not odir.is_dir():
            os.makedirs(odir,exist_ok=True)
        for gidx,rst in zip(rstgidxs,rstfiles):
            if gidx is not None:
                src = rst
                dst = odir / (f"init%0{args.pad}i.rst7"%(gidx+1))
                shutil.copyfile(src,dst)
                print(f"cp {src} {dst}")


        ursts = []
        for idx in rstgidxs:
            if idx is not None:
                ursts.append(idx+1)
        for i in range(len(ursts)):
            #print(i,ursts[i],nsims)
            init = f"init%0{args.pad}i"%(ursts[i])
            if i < len(ursts)-1:
                mid = (ursts[i]+ursts[i+1])//2
                WriteEquilScript(odir / ("eq%02ifwd.sh"%(i+1)),
                                 init,ursts[i],mid+1,False,args.pad)
            else:
                if ursts[i] < nsims:
                    WriteEquilScript(odir / ("eq%02ifwd.sh"%(i+1)),
                                     init,ursts[i],nsims+1,False,args.pad)
            if i > 0:
                mid = (ursts[i]+ursts[i-1])//2
                hi = ursts[i]
                if hi == nsims:
                    hi += 1
                WriteEquilScript(odir / ("eq%02irev.sh"%(i+1)),
                                 init,mid+1,hi,True,args.pad)
            else:
                WriteEquilScript(odir / ("eq%02irev.sh"%(i+1)),
                                 init,1,ursts[i],True,args.pad)

    maxgap = np.zeros( wins.shape[1] )
    for gidx in range(nsims):
        name = pathlib.Path(args.odir)
        odir = name 
        disname = odir / (f"img%0{args.pad}i.disang"%(gidx+1))
        rcstr = " ".join( ["%9.3f"%(x) for x in wins[gidx,:]] )
        print("%4i %s   %s"%(gidx+1,rcstr,disname))

        if not args.dry_run:
            odisang = tdisang.SetTemplateValues(wins[gidx,:],ks=fcs)
            fh = open(disname,"w")
            odisang.Write(fh)
            fh.close()
            WriteMdinFromTemplate(tmdin,disname.with_suffix(".mdin"))
            
        if gidx > 0:
            gap = abs(wins[gidx,:] - wins[gidx-1,:])
            for d in range(maxgap.shape[0]):
                maxgap[d] = max(maxgap[d],gap[d])
    rcstr = " ".join( ["%9.3f"%(x) for x in maxgap] )
    print("%4s %s"%("dmax",rcstr))

    exit(0)
        
