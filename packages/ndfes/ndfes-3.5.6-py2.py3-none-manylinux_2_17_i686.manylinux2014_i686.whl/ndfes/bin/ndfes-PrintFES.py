#!/usr/bin/env python3

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    

if __name__ == "__main__":

    import ndfes
    import argparse

    parser = argparse.ArgumentParser \
    ( formatter_class=argparse.RawDescriptionHelpFormatter,
      description="Prints free energy from ndfes checkpoint file")

    parser.add_argument \
        ("-m","--model",
         help="zero-based index of the model to print. Default: -1, which "+
         "causes all models to be printed",
         type=int,
         default=-1,
         required=False )

    
    parser.add_argument \
        ("-c","--ci",
         help="if present, write the confidence intervals rather than "+
         "standard errors",
         action='store_true',
         required=False )

    
    # parser.add_argument \
    #     ("-g","--gpr",
    #      help="perform Gaussian Process Regression before outputting values.",
    #      action='store_true',
    #      required=False )
    
    # parser.add_argument \
    #     ("-e","--extraerr",
    #      help="add extra standard deviation to each point to increase the "+
    #      "amount of GPR smoothing. Only used if --gpr is specified. Default: 0",
    #      type=float,
    #      default=0,
    #      required=False )

    # parser.add_argument \
    #     ("-s","--sigmatol",
    #      help="refit GPR until the interpolated free energies are within "+
    #      "sigmatol standard deviations of the training values. Only used "+
    #      "if --gpr is specified. Default: 1.e+5",
    #      type=float,
    #      default=1.e+5,
    #      required=False )

    parser.add_argument \
        ('chkpt',
         metavar='chkpt',
         type=str,
         help='ndfes checkpoint file')

    
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

    models = ndfes.GetModelsFromFile(args.chkpt)

    if args.model >= 0:
        if args.model < len(models):
            models = [ models[args.model] ]
        else:
            raise Exception("--model=%i is out of range "%(args.model) +
                            "(there are only %i models)"%(len(models)))

        
    for i,model in enumerate(models):
        if i > 0:
            print("")
        # if args.gpr:            
        #     idxs = model.GetBinIdxs()
        #     pts  = model.GetBinCenters()
        #     rws  = model.GetBinEntropies()
        #     model.UseGPRInterp(extra_error=args.extraerr,
        #                        sigma_fit_tol=args.sigmatol)
        #     res  = model.CptInterp(pts,return_std=True)
        #     vals = res.values
        #     errs = res.errors
        #     for i in range(len(vals)):
        #         sbin = ndfes.SpatialBin(idxs[i],vals[i],errs[i],rws[i])
        #         sbin.center = pts[i]
        #         print(sbin)
        # else:
        if True:
            fact = 1.0
            if args.ci:
                fact = 1.96
            for gidx,sbin in sorted(model.bins.items()):
                try:
                    print("%s %15.6e %12.3e %8.3f %6i"%(
                        " ".join(["%14.8f"%(c) for c in sbin.center]),
                        sbin.value,
                        fact * sbin.stderr,
                        sbin.entropy,sbin.size))
                except:
                    pass
    

