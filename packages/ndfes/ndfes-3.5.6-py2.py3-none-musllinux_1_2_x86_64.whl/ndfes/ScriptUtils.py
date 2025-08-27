#!/usr/bin/env python3


def AddStdOptsToCLI(parser):
    """Adds typical arguments to an argparse paser.

    --model
    --gpr
    --rbf
    --arbf
    --hist
    --bspl
    --wavg
    --wavg-niter
    --minsize
    --shape
    --rbfmaxerr
    --extraerr
    --sigmatol
    --grid

    Parameters
    ----------
    parser : argparse.ArgumentParser

    """
    
    parser.add_argument \
        ('chkpt',
         metavar='chkpt',
         type=str,
         help='ndfes checkpoint file')
    
    parser.add_argument \
        ("-m","--model",
         help="zero-based index of the model to print. Default: 0",
         type=int,
         default=0,
         required=False )

    parser.add_argument \
        ("--gpr",
         help="Gaussian Process Regression interpolation. "+
         "Valid for both vFEP and MBAR",
         action='store_true',
         required=False)
    
    parser.add_argument \
        ("--rbf",
         help="Radial Basis Function interpolation. "+
         "Valid for both vFEP and MBAR",
         action='store_true',
         required=False)
    
    parser.add_argument \
        ("--bspl",
         help="Cardinal B-spline interpolation. "+
         "Valid only for vFEP",
         action='store_true',
         required=False)

    parser.add_argument \
        ("--wavg",
         help="Weighted average B-spline interpolation. Argument is the B-spline order.",
         type=int,
         default=-1,
         required=False)

    parser.add_argument \
        ("--wavg-niter",
         help="The number of iterations used to correct the weighted average. Using too many corrections will cause it to reproduce the noise in the data. Default: 0. Recommended: 4",
         type=int,
         default=0,
         required=False)


    parser.add_argument \
        ("--hist",
         help="No interpolation; only use histogram values",
         action='store_true',
         required=False)

    
    parser.add_argument \
        ("--arbf",
         help="Approximate Radial Basis Function interpolation. "+
         "Valid for both vFEP and MBAR. This option is not "+
         "recommended for general use. It exists only for testing purposes. "+
         "The integer value refers to the number of layers of "+
         "neighbors used to generate a local RBF interpolator. "+
         "The default value of -1 (default) disables the ARBF. "+
         "A value of 1 is very fast but produces noticable artifacts "+
         "in the free energy surface. A value of 2 reduces the "+
         "artifacts, such that one would not notice them on a heatmap, "+
         "but one can still see some wiggles in a 1D path projection. "+
         "A value of 3 would likely be so slow that one would prefer "+
         "to use the --rbf option instead.",
         type=int,
         default=-1,
         required=False)
    
    parser.add_argument \
        ("--shape",
         help="RBF shape parameter used when --rbf is specified. "+
         "small values tend to yield larger oscillations. Default=100",
         type=float,
         default=100,
         required=False )

    parser.add_argument \
        ("--minsize",
         type=int,
         default=0,
         required=False,
         help="Exclude bins with fewer "+
         "than minsize samples. Default: 0 (which includes all bins)")

    parser.add_argument \
        ("--rbfmaxerr",
         type=float,
         default=1.0,
         required=False,
         help="If a bin was excluded from the RBF solution, and the "+
         "interpolated free energy differs from the histogram value "+
         "by more than rbfmaxerr, then eliminate the bin entirely -- "+
         "effectively treating the free energy as positive infinity. "+
         "Default: 1.0 kcal/mol (or energy unit defined within the checkpoint file)")
    
    
    parser.add_argument \
        ("--extraerr",
         help="add extra standard deviation to each point to increase the "+
         "amount of GPR smoothing. Only used if --gpr is specified. Default: 0",
         type=float,
         default=0,
         required=False )

    parser.add_argument \
        ("--sigmatol",
         help="refit GPR until the interpolated free energies are within "+
         "sigmatol standard deviations of the training values. Only used "+
         "if --gpr is specified. Default: 1.e+5",
         type=float,
         default=1.96,
         required=False )
    
    
    parser.add_argument \
        ("--grid",
         help="extract grid from the specified checkpoint file. Can be used multiple times to expand the grid.",
         type=str,
         action='append',
         nargs='+',
         required=False )


def SetupModelFromCLI(args):
    """Reads a model, resizes the grid, and sets up the interpolator

    Parameters
    ----------
    args : ArgumentParser.Namespace
        The result of ArgumentParser.parse_args()

    Returns
    -------
    model : ndfes.MBAR or ndfes.vFEP
        The FES object

    oprefix : str
        A string that is suggested to be used as a filename prefix
        for any files that are written

    interp : str
       A string indicating the type of interpolation
    """

    from . ReadCheckpoint import GetModelsFromFile
    
    if args.grid is not None:
        args.grid = [item for sublist in args.grid
                     for item in sublist]

    #
    # Read the first model from the ndfes checkpoint file
    #
    print("Reading ndfes checkpoint file")
    model = GetModelsFromFile(args.chkpt)[args.model]

    if args.minsize > 0:
        model = model.StripBins(args.minsize)

    if args.grid is not None:
        xmins=[dim.xmin for dim in model.grid.dims]
        xmaxs=[dim.xmax for dim in model.grid.dims]
        print("original grid xmins:",xmins)
        print("original grid xmaxs:",xmaxs)
        for grid in args.grid:
            gmodel = GetModelsFromFile(grid)[0]
            for idim,dim in enumerate(gmodel.grid.dims):
                xmins[idim] = min(xmins[idim],dim.xmin)
                xmaxs[idim] = max(xmaxs[idim],dim.xmax)
        print("extended grid xmins:",xmins)
        print("extended grid xmaxs:",xmaxs)
        model = model.ResizeDims(xmins,xmaxs)

    oprefix,interp = SetupInterpFromCLI(args,model)
    
    return model,oprefix,interp


def SetupInterpFromCLI(args,model,iofile_interp=None):
    """Setup FES interpolation based on command-line options

    Parameters
    ----------
    args : ArgumentParser.Namespace
        The result of ArgumentParser.parse_args()

    mode : ndfes.MBAR or ndfes.vFEP
        The free energy surface to manipulate

    iofile_interp : str, default=None (DEPRECATED)
        This was used to store intermediate calculations in a pkl file
        which could be re-read if the script was run more than once to
        change the aesthetics, because a GPR or RBF interpolation can
        be expensive to calculate.  However, this often led to confusion
        because people forgot to delete the pkl file when they wanted
        to recalculate the interpolation.

    Returns
    -------
    oprefix : str
        Output string used to prefix filenames

    interp : str
        String indicating the type of interpolation
    """
    from . MBAR import MBAR
    from . vFEP import vFEP
    
    #
    # Valid choices of interp for vFEP are:
    # 'bspl' : use B-spline interpolation
    # 'rbf'  : use RBF interpolation
    # 'gpr'  : use GPR interpolation
    #
    # Valid choices of interp for MBAR are:
    # 'rbf'  : use RBF interpolation
    # 'gpr'  : use GPR interpolation

    if isinstance(model,MBAR):
        interp = 'rbf'
    elif isinstance(model,vFEP):
        interp = 'bspl'
        
    if args.arbf > 0:
        interp = 'arbf'
    elif args.rbf:
        interp = 'rbf'
    elif args.wavg > 1:
        interp = 'wavg'
    elif args.gpr:
        interp = 'gpr'
    elif args.bspl:
        interp = 'bspl'
    elif args.hist:
        interp = 'none'
        
    if interp == "bspl" and not isinstance(model,vFEP):
        raise Exception("bspl interpolation is only available for vFEP")
            
    oprefix = args.chkpt + "." + interp + ".%i"%(args.model)

    
    if iofile_interp is not None:
        if os.path.isfile(iofile_interp):
            ifile = os.path.getmtime(iofile_interp)
            mfile = os.path.getmtime(args.chkpt)
            if mfile > ifile:
                print("Removing",iofile_interp,
                      "because",args.chkpt,"is newer")
                os.remove(iofile_interp)
            
    if interp == 'gpr':
        print("Creating GPR interpolator")
        model.UseGPRInterp( filename=iofile_interp,
                            extra_error=args.extraerr,
                            sigma_fit_tol=args.sigmatol )
    elif interp == 'rbf':
        print("Creating RBF interpolator")
        nexcl = len(model.BinsWithFewerThanMinSamples(args.minsize))
        print("There are %i occupied bins,"%(len(model.bins)) +
              " %i of which are excluded "%(nexcl) +
              "because they have fewer than %i samples"%(args.minsize))

        model.UseRBFInterp( filename=iofile_interp,
                            epsilon=args.shape,
                            minsize=args.minsize,
                            maxerr=args.rbfmaxerr )
            
        print("There are %i remaining bins "%(len(model.bins)) +
              "that agree with the RBF "+
              "within %.1f kcal/mol (or energy unit defined within the checkpoint file)"%(args.rbfmaxerr))

    elif interp == 'arbf':
        print("Creating ARBF interpolator")

        model.UseARBFInterp( args.arbf, epsilon=args.shape )
            
    elif interp == 'wavg':
        print(f"Creating WAVG interpolator (order: {args.wavg})")
        model.UseWAVGInterp( args.minsize, args.wavg,
                             args.wavg_niter )

    elif interp == 'none':
        print("Not using interpolator")
    else:
        print("Using B-spline basis")
    print("Finished creating interpolator")

    return oprefix,interp



def WritePathProjection(ts,pcrds,model,interp,pfile):
    """Writes the 1D projection of a path to a file

    Parameters
    ----------
    ts : numpy.ndarray, shape=(n,)
        The spline progress values

    pcrds : numpy,ndarray, shape=(n,ndim)
        The path coordinates

    model : ndfes.FES
        The free energy surface

    interp : str
        The string indicating the type of interpolation

    pfile : str
        Name of the file to write
    """
    
    import numpy as np
    from . EvalT import EvalT

    
    if interp == 'none':
        vals = np.array(model.GetBinValues(pts=pcrds))
        errs = np.array(model.GetBinErrors(pts=pcrds))
        ders = np.zeros( (vals.shape[0],model.grid.ndim) )
        res = EvalT(vals,ders,errs)
    else:
        res = model.CptInterp(pcrds,return_std=True)
    sizes = np.array(model.GetBinSizes(pts=pcrds))
                
    print(f"Writing path to {pfile}")
    
    fh = open(pfile,"w")
    for i in range(ts.shape[0]):
        if res.values[i] is None:
            v = 0
            e = 0
            s = 0
        else:
            v = res.values[i]
            e = 1.96*res.errors[i]
            s = sizes[i]
        if s is None:
            s = 0
        fh.write("%3i %22.14f"%(i+1,ts[i]))
        for x in pcrds[i,:]:
            fh.write(" %19.10e"%(x))
        fh.write(" %19.10e"%(v) +
                 " %13.4e %5i\n"%(e,s))
    fh.close()

    
