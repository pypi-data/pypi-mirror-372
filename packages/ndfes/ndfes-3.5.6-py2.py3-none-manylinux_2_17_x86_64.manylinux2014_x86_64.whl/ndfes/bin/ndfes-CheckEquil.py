#!/usr/bin/env python3


from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    

    
if __name__ == "__main__":

    import argparse
    import numpy as np
    import ndfes
    import ndfes.amber
    import pathlib
    import sys
    import subprocess as subp
    #from ndfes import AutoEquil
    #from ndfes import AutoSubsample
    #from ndfes import ChunkAnalysis
    from ndfes import SliceAnalysis

    
    parser = argparse.ArgumentParser \
        ( formatter_class=argparse.RawDescriptionHelpFormatter,
          description="""
Use forward and reverse analysis of the biasing potential to automatically
detect the equilibrated region of an Amber trajectory. Optionally uses
cpptraj to write a new trajectory containing the statistically independent 
samples from the equilibrated region.

     EXAMPLES THAT ANALYZE NETCDF TRAJECTORY FILES
     ---------------------------------------------

     To exclude the first 25% of a simulation and keep all remaining samples:

     ndfes-CheckEquil.py -p sys.parm7 -i inp.nc -o out.nc \\
                         --start=0.25 --skipg --skipsearch \\
                         -d inp.disang -r 1

     To automatically detect equilibration from forward and reverse analysis,
     but keep all remaining samples:

     ndfes-CheckEquil.py -p sys.parm7 -i inp.nc -o out.nc \\
                         --skipg -d inp.disang -r 1

     To automatically detect equilibration from forward and reverse analysis,
     and keep only the statistically independent samples:

     ndfes-CheckEquil.py -p sys.parm7 -i inp.nc -o out.nc \\
                         -d inp.disang -r 1

     To automatically detect equilibration but skip the writing of a new
     trajectory:

     ndfes-CheckEquil.py -i inp.nc -d inp.disang -r 1


     If the trajectory time series was restart several times, then one can
     specify multiple input trajectories: -i init.nc rst1.nc rst2.nc [...]



     EXAMPLES THAT ANALYZE DUMPAVE FILES
     -----------------------------------

     A dumpave consists of several columns. The first column (column 0)
     is the step number (or simulation time).  The remaining columns are
     assumed to be values of the reaction coordinates (in principle they
     can be anything, but this script makes that assumption).  The
     bias energy is computed from the columns specified with the -r flag.
     For example -r 1 2 means that the 2nd and 3rd columns in the dumpave
     file correspond to the 2nd and 3rd restraints specified in the 
     disang file, and the bias energy is computed from these 2 coordinates.
     If the above assumption does not hold, one would need to modify
     the disang file appropriately.

     To exclude the first 25% of a simulation and keep all remaining samples:

     ndfes-CheckEquil.py -i inp.dumpave -o out.dumpave \\
                         --start=0.25 --skipg --skipsearch \\
                         -d inp.disang -r 1

     To automatically detect equilibration from forward and reverse analysis,
     but keep all remaining samples:

     ndfes-CheckEquil.py -i inp.dumpave -o out.dumpave \\
                         --skipg -d inp.disang -r 1

     To automatically detect equilibration from forward and reverse analysis,
     and keep only the statistically independent samples:

     ndfes-CheckEquil.py -i inp.dumpave -o out.dumpave \\
                         -d inp.disang -r 1

     To automatically detect equilibration but skip the writing of a new
     trajectory:

     ndfes-CheckEquil.py -i inp.dumpave -d inp.disang -r 1


     If the trajectory time series was restart several times, then one can
     specify multiple input trajectories: -i init.dumpave rst1.dumpave [...]



     The following line will print to standard output:

Ninp=<N> Nout=<Nind> Teq=<Teq> i0=<i0> s=<s> g=<g> fst= <Wf> +- <dWf> lst= <Wl> +- <dWl>

     Ninp:  The number of input samples
     Nout:  The number of output samples
     Teq:   The percentage of samples excluded as equilibration
     i0:    The 1-based index of the first frame to write (the "start" value 
            when using cpptraj)
     s:     The stride through the data (the "offset" value when using cpptraj)
     g:     The statistical inefficiency of the correlated samples
     Wf:    The mean value of the bias potential from the first half of 
            statistically independent samples after excluding the first 
            i0-1 samples as equilibration
     dWf:   The standard error of Wf
     Wl:    The mean value of the bias potential from the last half of 
            statistically independent samples after excluding the first 
            i0-1 samples as equilibration
     dWl:   The standard error of Wl

        
""" )
    
    parser.add_argument \
        ("-d","--disang",
         help="disang file defining the restraint energies",
         type=str,
         required=True )
    
    parser.add_argument \
        ("-i","--inp",
         help="input netcdf trajectory (or disang) files."+
         " Multiple files can be listed for each instance of"+
         " --inp, which are interpretted as a series of restarts",
         type=str,
         nargs='+',
         action='append',
         required=True )
    
    parser.add_argument \
        ("-p","--parm",
         help="Amber parm7 (only needed if --out is a netcdf file)",
         type=str,
         required=False )
    
    parser.add_argument \
        ("-o","--out",
         help="output trajectory (or disang) file",
         type=str,
         required=False )

    parser.add_argument \
        ("-r","--rxn",
         help="column indexes of the desired reaction coordinates",
         type=int,
         action='append',
         nargs='+',
         required=True )

    parser.add_argument \
        ("--start",
         help="exclude the first percentage of samples (Default: 0.0)",
         type=float,
         default=0.0,
         required=False )

    parser.add_argument \
        ("--stop",
         help="ignore the last fraction of samples (Default: 1.0)",
         type=float,
         default=1.0,
         required=False )

    
    parser.add_argument \
        ("-s","--sym",
         help="negate the restraint definition for the specified reaction coordinate. This is only useful if one is processing a dumpave file that was already generated with ndfes-PrepareAmberData.py with the same -s option. It is very rare that this option would ever be used.",
         type=int,
         required=False )
    
    parser.add_argument \
        ("-m","--maxeq",
         help="maximum fraction of samples to exclude as equilibration (Default: 0.5)",
         type=float,
         default=0.5,
         required=False )

    parser.add_argument \
        ("-g","--skipg",
         help="keep all samples after identifying the equilibrated region (assume g=1, where g is the statistical inefficiency)",
         action='store_true' )

    parser.add_argument \
        ("-S","--skipsearch",
         help="skip the auto-detection of the equilibration region",
         action='store_true' )
    
    # parser.add_argument \
    #     ("-C","--chunks",
    #      help="number of chunks to split the data into to perform time series analysis (default: 20)",
    #      type=int,
    #      default=20,
    #      required=False )
    
    parser.add_argument \
        ("--ptol",
         help=("The p-value threshold when performing statistical "
               "tests. Default is 0.05. Larger values exclude more samples. "
               "Some useful values to note:\n"
               "  0.21135667595 (79%% confidence, 1.25 sigma)\n"
               "  0.31729526862 (68%% confidence, 1.00 sigma, default)\n"
               "  0.45310971043 (55%% confidence, 0.75 sigma)\n"
               "  0.61678615958 (38%% confidence, 0.50 sigma)\n"
         ),
         type=float,
         #default=0.31729526862,
         default=0.05,
         required=False )

    parser.add_argument \
        ("--dtol",
         help=("If the first and last half means are less than dtol, "
               "then it passes the delta test (Default: 0.1 kcal/mol)"),
         type=float,
         default=0.1,
         required=False )

    
    
    parser.add_argument \
        ("--prune",
         help=("Use a minimal number of samples to represent the "
               "production region. Only available if -S is not used."),
         action='store_true' )
    
    
    parser.add_argument \
        ("--maxsize",
         help=("The maximum number of samples after pruning. "
               "Default: 125"),
         type=int,
         default=125,
         required=False)
    
    

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


    if args.prune and args.skipg:
        raise Exception("Cannot use --prune and --skipg at the same time.")
    
    # the list of dumpaves to read
    idumps = [item for sublist in args.inp for item in sublist]
    if args.out in idumps:
        raise Exception("Output dumpave cannot be one of the input dumpaves")

    
    out_path = None
    if args.out is not None:
        out_path = pathlib.Path(args.out)
        if not out_path.parents[0].is_dir():
            raise Exception("Directory does not exist: %s"%(out_path.parents[0]))
        if pathlib.Path(out_path).suffix == ".nc":
            if args.parm is None:
                raise Exception("--parm must be specified if --out is used")
            parm_path = pathlib.Path(args.parm)
            if not parm_path.exists():
                raise Exception("File not found: %s"%(parm_path))
            for idump in idumps:
                if pathlib.Path(idump).suffix != ".nc":
                    raise Exception("Output is a netcdf trajectory but the input is not: %i"%(idump))
        elif pathlib.Path(out_path).suffix == ".dumpave":
            for idump in idumps:
                if pathlib.Path(idump).suffix != ".dumpave":
                    raise Exception("Output is a dumpave but the input is not: %i"%(idump))
        else:
            raise Exception(f"Output suffix must either be .nc or .dumpave not '{pathlib.Path(out_path).suffix}'")

    
    
    # the list of column indexes for the active collective variables
    rxncols  = [item for sublist in args.rxn for item in sublist]

    # the restraint definitions
    disang = ndfes.amber.Disang( args.disang )

    
    

    
    # read the dumpave (or netcdf trajectory) files
    dumplines=[]
    datas = []
    for idump in idumps:
        if pathlib.Path(idump).suffix == ".nc":
            crds = ndfes.amber.ReadCrds( idump )
            data = []
            for i in range(crds.shape[0]):
                row = np.zeros( (1+len(disang.restraints),) )
                row[0] = i
                row[1:] = disang.CptCrds( crds[i,:,:] )
                data.append(row)
            data = np.array(data)
        elif pathlib.Path(idump).suffix == ".dumpave":
            data=[]
            fh=open(idump,"r")
            prevt=None
            for line in fh:
                line = line.strip()
                cs = [float(c) for c in line.split()]
                if len(cs) > 1:
                    if prevt is not None:
                        if abs(prevt-cs[0]) < 1.e-4:
                            data[-1] = cs
                            dumplines[-1] = line
                            continue
                    prevt=cs[0]
                    dumplines.append(line)
                    data.append( cs )
            fh.close()
            data = np.array(data)
        #    data = np.loadtxt(idump)
        datas.append(data)
    data = np.concatenate( datas )


    # reverse a collective variable and sampling, if requested
    
    if args.sym is not None:
        disang.restraints[args.sym-1].Reverse()

        
    
    # compute the bias energy, if necessary
    
    biasenes = []
    if len(rxncols) > 0:
        bias = disang.Subset(rxncols)
        for i in range(data.shape[0]):
            biasenes.append( bias.CptBiasEnergy( data[i,rxncols] ) )
        biasenes = np.array(biasenes)
    else:
        raise Exception("reaction coordinates are undefined")

    N = biasenes.shape[0]

    # if args.chunks < 2:
    #     raise Exception(f"--chunks too small {args.chunks}, should be > 2")
    
    
    if True:
        convblk = None
        if not args.skipsearch:
            # conv,trial,chunks = AutoEquil(args.start,args.stop,args.chunks,
            #                               biasenes,args.ptol,maxeq=args.maxeq)
            blks = SliceAnalysis( args.start, args.stop, args.maxeq, 0.05, biasenes, args.ptol, args.dtol )
            
            #print("search blks",blks)
            
            for blk in blks:
                if blk.test:
                    convblk = blk
                    break
            if convblk is None:
                convblk = blks[-1]
                #print("%6s %6s %6s"%(blk.mean_test,blk.linreg_test,blk.test))
            
        else:
            blks = SliceAnalysis( args.fstart, args.fstop, 1, 1, biasenes, args.ptol, args.dtol )
            convblk = blks[-1]
            #print("nosearch blks",blks)

        conv = convblk.test
        

        #kstart = trial.prod.istart
        #kstop = trial.prod.istop
        #kstride = trial.prod.s
        kstart = convblk.offset
        kstop = kstart + convblk.n
        kstride = convblk.g
        
        # if args.prune:
        #     nprop = len(rxncols)
        #     props = data[:,rxncols]
        #     kstart,kstop,stride = AutoSubsample\
        #         ( trial, biasenes, args.ptol, aux=props,
        #           minsamples=args.minsize, maxsamples=args.maxsize, dbg=True )
        #     if stride != kstride:
        #         trial = ChunkAnalysis(0,1,1, biasenes[kstart:kstop:stride],args.ptol)[0]
        #     kstride = stride

        if args.prune:

            refmean = np.mean(data[kstart:kstop:kstride,rxncols],axis=0)
            kstride = 0
            xstride = 0
            while True:
                xstride += 1
                n = len(range(kstart,kstop,xstride))
                print(xstride,n,args.maxsize)
                if n > args.maxsize:
                    continue
                elif n < args.maxsize:
                    xstride = max(1,xstride-1)
                    break
                else:
                    break
            valid_xstarts = []
            xstart = -1
            while True:
                xstart += 1
                n = len(range(kstart+xstart,kstop,xstride))
                if n == args.maxsize:
                    valid_xstarts.append(xstart)
                elif n < args.maxsize:
                    xstart = max(0,xstart-1)
                    break
            if len(valid_xstarts) > 0:
                xmin=0
                dmin=1.e+30
                for x in valid_xstarts:
                    d = np.linalg.norm( np.mean(data[kstart+x:kstop:xstride,rxncols],axis=0) - refmean )
                    if d < dmin:
                        dmin = d
                        xmin = x
                xstart = xmin
            
            kstride = xstride
            kstart = kstart + xstart
        
        
        nout = len( range(kstart,kstop,kstride) )
        if args.skipg:
            kstride = 1
            nout = len( range(kstart,kstop,kstride) )
            
        warns=[]
        if not conv:
            warns.append( "UNCONVERGED!" )
        if kstart/(N-1) > 0.7:
            warns.append( "Teq > 70!" )
        if nout < 50:
            warns.append( " N<50!" )
        warn=" ".join(warns)
            
        print("%60s Ninp=%5i Nout=%5i Teq=%4.0f i0=%5i s=%3i fst=%6.2f +- %4.2f lst=%6.2f +- %4.2f %s"%(\
                idumps[0],
                N,
                nout,
                100*kstart/(N-1),
                kstart+1,kstride,
                convblk.mean_fhalf,convblk.stde_fhalf,
                convblk.mean_lhalf,convblk.stde_lhalf,
                warn))
                  
            
    if out_path is not None:

        if pathlib.Path(out_path).suffix == ".nc":
            inp = str(out_path) + ".cpptraj"
            out = inp + ".out"
            fh=open(inp,"w")
            fh.write("parm %s\n"%(args.parm))
            for idump in idumps:
                fh.write("trajin %s\n"%(idump))
            fh.write("trajout %s start %i offset %i\n"%(out_path,kstart+1,kstride))
            fh.write("run\nexit\n")
            fh.close()

            subp.run(["cpptraj","-i",inp,"-o",out])

        elif pathlib.Path(out_path).suffix == ".dumpave":
            fh=open(out_path,"w")
            for idx in range(kstart,kstop,kstride):
                fh.write("%s\n"%(dumplines[idx]))
            fh.close()

            
