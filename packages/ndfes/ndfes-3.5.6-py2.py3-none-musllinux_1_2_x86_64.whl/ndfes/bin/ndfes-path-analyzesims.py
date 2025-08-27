#!/usr/bin/env python3

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    
def GetDirName(it,pad):
    name = None
    if it == 0:
        name = "init"
    elif it > 0:
        name = f"it%0{pad}i"%(it)
    return name

def MetafileCurrent(prefix):
    m = "metafile.current"
    if prefix is not None:
        if prefix != "":
            m += "." + prefix
    return m
            
def MetafileAll(prefix):
    m = "metafile.all"
    if prefix is not None:
        if prefix != "":
            m += "." + prefix
    return m


if __name__ == "__main__":

    
    import argparse
    import numpy as np
    import pathlib
    import glob
    import sys
    import os
    import shutil
    import ndfes
    from subprocess import check_output

    parser = argparse.ArgumentParser \
        ( formatter_class=argparse.RawDescriptionHelpFormatter,
          description="""
          This script is used during the finite temperature string method to 
          prepare the lastest set of simulations for analysis. A typical string
          iteration involves the following steps:

          1. Perform the simulations.

          2. Prepare the sampling for analysis using ndfes-path-analyzesims.py.
          This effectively acts as a convenience wrapper to ndfes-CheckEquil.py,
          ndfes-PrepareAmberData.py, and ndfes-CombineMetafiles.py.

          3. Run ndfes to obtain the current estimate of the free energy 
          surface from the aggregate sampling obtained from the current and 
          previous string iterations.

          4. Run ndfes-path to optimize a minimum free energy path on the 
          current estimate of the free energy surface and write a new directory
          of simulation inputs.
          """ )


    parser.add_argument \
        ("-d","--disang",
         help="template disang",
         type=str,
         required=True)

    parser.add_argument \
        ("--prefix",
         help="The subdirectory within the iteration directory "
         +"containing the simulation data. The default prefix is '', "
         +"which will search for itXXX/img*.dumpave. If prefix is set, "
         +"then it will search for itXXX/PREFIX/img*.dumpave.",
         default=None,
         type=str,
         required=False)

    parser.add_argument \
        ("--curit",
         type=int,
         required=True,
         help="Index of the current iteration. The current directory is "
         +"assumed to be itXXX, where XXX is a zero-padded integer, "
         +"specified by --curit.  If --curit=0, then the directory name "
         +"is assumed to be init")

    parser.add_argument \
        ("--pad",
         type=int,
         required=False,
         default=3,
         help="Length of the directory name zero-padding. Default: 3")
    
    parser.add_argument \
        ("--nprev",
         type=int,
         default=1000,
         help="The number of previous iterations to include in the "
         +"estimation of the free energy surface. A value of 0 means "
         +"only the sampling from the current iteration contributes "
         +"the calculation of the free energy surface. A value of 1000 "
         +"will include all previous iterations. A value of 10 likely "
         +"strikes a good balance between performance and accuracy. "
         +"The default is 1000.")
    
    # parser.add_argument \
    #     ("--curdir",
    #      help="Directory containing the current iteration."+
    #      " The simulations in this directory must have already been run."+
    #      " The ${curdir}/img*.dumpave are expected to exist.",
    #      type=str,
    #      required=True)

    
    # parser.add_argument \
    #      ("--extrameta",
    #       help="One-or-more extra metafile's used to estimate the free energy."+
    #       " Typically this is ${olddir}/analysis/metafile.all, but other"+
    #       " additional metafile's can be specified by using this option"+
    #       " more than once.  If this option is not used, then only the"+
    #       " dumpave's in ${curdir} are analyzed.",
    #       nargs='+',
    #       action='append',
    #       type=str,
    #       required=False)

    # parser.add_argument \
    #     ("-D","--dumpaves",
    #      help="List of additional dumpave files to include in the analysis.  "
    #      +"That is, the current iteration of umbrella simulations",
    #      type=str,
    #      action='append',
    #      nargs='+',
    #      required=True )

    # parser.add_argument \
    #     ("--oldmeta",
    #      help="The metafile used to analyze the previous string iterations",
    #      type=str,
    #      required=False)

    parser.add_argument \
        ("-T","--temp",
         help="Temperature, K (default: 298.)",
         type=float,
         default=298.,
         required=False )

    parser.add_argument \
        ("-s","--start",
         help="exclude the first percentage of samples (default: 0.0)",
         type=float,
         default=0.0,
         required=False )

    parser.add_argument \
        ("--stop",
         help="ignore the samples after this percentage (default: 1.0)",
         type=float,
         default=1.0,
         required=False )

    parser.add_argument \
        ("-m","--maxeq",
         help="maximum fraction of samples to exclude as equilibration "
         +" (default: 0.7)",
         type=float,
         default=0.7,
         required=False )
    
    parser.add_argument \
        ("-g","--skipg",
         help="keep all samples after identifying the equilibrated "
         +"region (assume g=1, where g is the statistical "
         +"inefficiency)",
         action='store_true' )
    
    parser.add_argument \
        ("-S","--skipsearch",
         help="skip the forward/reverse analysis",
         action='store_true' )
    
    # parser.add_argument \
    #     ("--refine-restart",
    #      help="restart the aggregate sampling if the previous iteration was marked as the first refinement, as determined from the isrefinement.txt file",
    #      action='store_true')
   
    parser.add_argument \
        ("--neqit",
         type=int,
         default=-1,
         help="phase-out the first neqit iterations from the sampling when generating metafile.all as curit increases")


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

    if args.prefix is not None:
        if "/" in args.prefix:
            raise Exception("prefix cannot have a slash")
        if " " in args.prefix:
            raise Exception("prefix cannot have a space")
    
    
    curdir = GetDirName( args.curit, args.pad )
    if curdir is not None:
        cdir = pathlib.Path( curdir )
        if not cdir.is_dir():
            raise Exception("Directory does not exist for iteration %s"%(curdir))
    else:
        raise Exception("Invalid index given to --curit: %i"%(args.curit))
    
    
    tdisangfile = pathlib.Path( args.disang )
    
    if not tdisangfile.is_file():
        raise Exception("Template disang %s does not exist"%(tdisangfile))

    tdisang = ndfes.amber.Disang(tdisangfile)
    tdisang.ValidateTemplate()
    idxs = tdisang.GetTemplateIdxs()


    firstit = None
    # if args.curit > 0 and args.refine_restart:
    #     first_refinement = -2
    #     for it in range(args.curit):
    #         if it == 0:
    #             fname = "init/isrefinement.txt"
    #         else:
    #             fname = "it%02i/isrefinement.txt"%(it)
    #         if os.path.exists(fname):
    #             fh = open(fname,"r")
    #             line = fh.readline().strip()
    #             if len(line) > 0:
    #                if int(line) == 1:
    #                   first_refinement = it
    #                   break
    #     firstit = max( 0, first_refinement+1 )
    if args.neqit >= 0:
        firstit = 0
        if args.curit > args.neqit:
            firstit = min(args.neqit+1,args.curit-args.neqit)
                                        


    #idumps = [item for sublist in args.dumpaves for item in sublist]

    idumps = []
    simdir = cdir
    if args.prefix is not None:
        simdir = simdir / args.prefix
        
    for idump in sorted(glob.glob( str(simdir / "img*.dumpave") )):
        idumps.append(idump)

    
    ana_dir  = cdir / "analysis"
    ana_dump_dir = ana_dir / "dumpaves"
    ana_cur_dir = ana_dir / "current"
    ana_dump_cur_dir = ana_dump_dir / cdir
    if args.prefix is not None:
        ana_dump_cur_dir = ana_dump_cur_dir / args.prefix
        ana_cur_dir = ana_cur_dir / args.prefix


    os.makedirs(ana_dump_cur_dir,exist_ok=True)
    os.makedirs(ana_cur_dir,exist_ok=True)


    
    print("Pruning data from %s "%(cdir)
          +"and storing dumpaves in %s"%(ana_cur_dir))
    
    for idump in idumps:
        dump = pathlib.Path(idump)
        dis = dump.with_suffix(".disang")
        if not dis.is_file():
            raise Exception("Disang %s does not exist"%(dis))
        odump = ana_cur_dir / dump.name
        cmd = ["ndfes-CheckEquil.py",
               "--disang","%s"%(dis),
               "--inp","%s"%(dump),
               "--out","%s"%(odump),
               "--start","%.3f"%(args.start),
               "--stop","%.3f"%(args.stop),
               "--maxeq","%.3f"%(args.maxeq),
               "--rxn"] + ["%i"%(idxs[i]+1) for i in range(len(idxs))]
        if args.skipg:
            cmd.append("--skipg")
        if args.skipsearch:
            cmd.append("--skipsearch")
        #print(cmd)
        out = check_output(cmd).decode("utf-8") 
        sys.stdout.write(out)

    
    print("Extracting data from %s "%(ana_cur_dir)
          +"and storing dumpaves in %s"%(ana_dump_cur_dir))
    
    metafile = ana_dir / MetafileCurrent(args.prefix)
    
    print("Writing %s"%(metafile))


    
    metafh = open(metafile,"w")
    
    for idump in idumps:
        dump = pathlib.Path(idump)
        dis = dump.with_suffix(".disang")
        if not dis.is_file():
            raise Exception("Disang %s does not exist"%(dis))
        idump = ana_cur_dir / dump.name
        odump = ana_dump_cur_dir / dump.name
        
        cmd = ["ndfes-PrepareAmberData.py",
               "-d","%s"%(dis),
               "-i","%s"%(idump),
               "-o","%s"%(odump),
               "-T","%.3f"%(args.temp),
               "--prefix","%s"%(ana_dir),
               "-r"] + ["%i"%(idxs[i]+1) for i in range(len(idxs))]

        #print(" ".join(cmd))
        out = check_output(cmd).decode("utf-8") 
        metafh.write(out)
        
    metafh.close()
    

    
    metaall = ana_dir / MetafileAll(args.prefix)
    fh = open(metaall,"w")
    seen = []
    print("Writing %s"%(metaall))        


    metas = []
    if firstit is None:

        for previt in range(1,args.curit-args.nprev):
            prevdir = GetDirName(previt,args.pad)
            if prevdir is not None:
                mpath = pathlib.Path(prevdir) / "analysis/" / MetafileCurrent(args.prefix)
                if mpath.is_file():
                    m = ndfes.Metafile(mpath)
                    p =  m.RelativeTo(ana_dir)
                    if len(p.trajs) > 1:
                        print("Including endstates from %s"%(mpath))
                        p.trajs = [ p.trajs[0], p.trajs[-1] ]
                        seen = p.write(fh,seen=seen)

        for previt in range( args.curit - args.nprev, args.curit ):
            prevdir = GetDirName(previt,args.pad)
            if prevdir is not None:
                mpath = pathlib.Path(prevdir) / "analysis/" / MetafileCurrent(args.prefix)
                if not mpath.is_file():
                    raise Exception("Previous metafile %s "%(mpath)
                                    +"does not exist")
                print("Including previous metafile: %s"%(mpath))
                metas.append( mpath )
    else:

        for previt in range( firstit, args.curit ):
            prevdir = GetDirName(previt,args.pad)
            if prevdir is not None:
                mpath = pathlib.Path(prevdir) / "analysis/" / MetafileCurrent(args.prefix)
                if not mpath.is_file():
                    raise Exception("Previous metafile %s "%(mpath)
                                    +"does not exist")
                print("Including previous metafile: %s"%(mpath))
                metas.append( mpath )



    for oldmetafile in metas:
        #print(oldmetafile)
        m = ndfes.Metafile(oldmetafile)
        p = m.RelativeTo(ana_dir)
        seen = p.write(fh,seen=seen)

    m = ndfes.Metafile(metafile)
    p = m.RelativeTo(ana_dir)
    p.write(fh,seen=seen)


    fh.close()


    
    if args.prefix is not None:
        if args.prefix != "":
            allmetas = []
            #print("pattern: %s"%(str(ana_dir / "metafile.all.*")))
            for meta in glob.glob( str(ana_dir / "metafile.all.*") ):
                #print("glob found",meta)
                if ".chk" not in meta and \
                   ".path" not in meta and \
                   ".dat" not in meta and \
                   ".txt" not in meta and \
                   ".pkl" not in meta:
                    allmetas.append(meta)
            
            metafile = str(ana_dir / "metafile.all")

            print("Writing %s from %s"%(metafile," ".join(allmetas)))
            
            fh = open(metafile,"w")
            seen = []
            for oldmetafile in allmetas:
                m = ndfes.Metafile(oldmetafile)
                p = m.RelativeTo(ana_dir)
                seen = p.write(fh,seen=seen)
            fh.close()

            
