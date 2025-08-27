#!/usr/bin/env python3

import ndfes
import numpy as np
from collections import defaultdict as ddict


from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    

# def ReadModel(fesdict,fname):
#     try:
#         mdl = int(fesdict[fname])
#     except:
#         raise Exception("Could not interpret %s as model "+
#                         "index"%(fesdict[fname]))
#     my_models = ndfes.GetModelsFromFile(fname)
#     if mdl >= 0 and mdl < len(my_models):
#         model = my_models[mdl]
#     else:
#         raise Exception("Model %i not found in %s"%(mdl,fname))
#     return model


def ArgToNameAndIdx(arg):
    if "=" in arg:
        name,idx = arg.split("=")
        idx = int(idx)
    else:
        name = arg
        idx = 0
    return name,idx


def ReadModel(arg):
    fname,mdl = ArgToNameAndIdx(arg)
    my_models = ndfes.GetModelsFromFile(fname)
    if mdl >= 0 and mdl < len(my_models):
        model = my_models[mdl]
        #print(fname,mdl)
    else:
        raise Exception("Model %i not found in %s"%(mdl,fname))
    return model



class AvgFES(object):
    def __init__(self,models,ref=None,use_ref_ene=False):
        self.models = models
        self.ref = ref
        self.use_ref_ene = use_ref_ene
        ms = [ m for m in self.models ]
        if self.ref is not None:
            ms = ms + [self.ref]
        self.grid = self.MakeGrid(ms)
        #print([ dim.size for dim in self.grid.dims ])  
        self.binidxs,self.occbins = self.GetOccBins(refmodel=self.ref)
        self.offsets = self.GetOffsets()
        #print(self.offsets)

    def MakeGrid(self,models):
        
        ndim = None
        xmins = None
        xmaxs = None
        widths = None
        ispers = None
        for ifes,m in enumerate(models):
            if ndim is None:
                ndim = m.grid.ndim
                xmins = [ dim.xmin for dim in m.grid.dims ]
                xmaxs = [ dim.xmax for dim in m.grid.dims ]
                widths = [ dim.width for dim in m.grid.dims ]
                ispers = [ dim.isper for dim in m.grid.dims ]
            elif m.grid.ndim != ndim:
                raise Exception("Grid dimensionality mismatch in FES %i"%(ifes))
            else:
                for idim in range(ndim):
                    xmins[idim] = min(xmins[idim],m.grid.dims[idim].xmin)
                    xmaxs[idim] = max(xmaxs[idim],m.grid.dims[idim].xmax)
                    if abs(m.grid.dims[idim].width - widths[idim]) > 1.e-8:
                        raise Exception("Grid width mismatch in " +
                                        "dim %i "%(idim) +
                                        "of FES %i"%(ifes))
                    if m.grid.dims[idim].isper != ispers[idim]:
                        raise Exception("Periodic mismatch in " +
                                        "dim %i "%(idim) +
                                        "of FES %i"%(ifes))
                
        sizes = [ int(round((xmax-xmin)/w))
                  for xmin,xmax,w in zip(xmins,xmaxs,widths) ]
    
        new_widths = [ (xmax-xmin)/size
                       for xmin,xmax,size in zip(xmins,xmaxs,sizes) ]
        for idim in range(ndim):
            if abs(widths[idim]-new_widths[idim]) > 1.e-8:
                raise Exception("Width mismatch in dim %i"%(idim))

        dims = []
        for idim in range(ndim):
            dims.append( ndfes.SpatialDim(xmins[idim], \
                                          xmaxs[idim],sizes[idim],ispers[idim]) )
        return ndfes.VirtualGrid( dims )

    
    def GetOccBins(self,refmodel=None):
        binidxs = ddict(list)
        bindict = ddict(list)
        nmodel = len(self.models)
        for imdl,model in enumerate(self.models):
            for gidx,sbin in sorted(model.bins.items()):
                bidx = self.grid.GetBinIdx( sbin.center )
                newgidx = self.grid.CptGlbIdxFromBinIdx( bidx )
                if newgidx not in binidxs:
                    binidxs[newgidx] = bidx
                if newgidx not in bindict:
                    bindict[newgidx] = [None]*nmodel
                bindict[newgidx][imdl] = sbin
        if refmodel is not None:
            for gidx,sbin in sorted(refmodel.bins.items()):
                bidx = self.grid.GetBinIdx( sbin.center )
                newgidx = self.grid.CptGlbIdxFromBinIdx( bidx )
                if newgidx not in binidxs:
                    binidxs[newgidx] = bidx
                if newgidx not in bindict:
                    bindict[newgidx] = [None]*nmodel
                #bindict[newgidx][imdl] = sbin
        return binidxs,bindict

    def GetBinValue(self,gidx):
        value = None
        stderr = None
        entropy = None
        size = None
        enes = []
        errs = []
        ents = []
        sizes = []
        for imdl in range(len(self.models)):
            if self.occbins[gidx][imdl] is not None:
                enes.append( self.occbins[gidx][imdl].value + self.offsets[imdl] )
                errs.append( self.occbins[gidx][imdl].stderr )
                ents.append( self.occbins[gidx][imdl].entropy )
                sizes.append( self.occbins[gidx][imdl].size )
        if len(enes) > 0:
            enes = np.array(enes)
            errs = np.array(errs)
            ents = np.array(ents)
            sizes = np.array(sizes)
            ddof=1
            if len(enes) < 2:
                ddof=0
            var_of_means = np.var(enes,ddof=ddof)
            mean_of_vars = np.mean( errs**2 )
            value = np.mean(enes)
            stderr = np.sqrt( (mean_of_vars+var_of_means)/len(enes) )
            entropy = np.mean(ents)
            size = int(round(np.mean(sizes)))

        return value,stderr,entropy,size

    def GetBinString(self,gidx,value,stderr,entropy,size):
        bidx = self.binidxs[gidx]
        bstr = ",".join(["%5i"%(b) for b in bidx])
        return "%7i : ndfes.SpatialBin([ %s ],"%(gidx,bstr) + \
            "%23.14e,%23.14e,%23.14e,%i )"%(value,stderr,entropy,size)
    
    def GetOffsets(self):
        nmodels = len(self.models)
        avgerrs = [0]*nmodels
        for imdl,model in enumerate(self.models):
            avgerrs[imdl] = np.mean( [ model.bins[sbin].stderr for sbin in model.bins ] )
        avgerr = np.mean( avgerrs )
        if avgerr < 1.e-8:
            avgerr = 1
        for imdl in range(nmodels):
            if avgerrs[imdl] < 1.e-8:
                avgerrs[imdl] = avgerr

        ref = self.ref
        if ref is None:
            ref = self.models[0]
                
        offsets = np.zeros( (nmodels,) )
        for imdl in range(nmodels):
            wsum = 0
            for ridx,sbin in sorted(ref.bins.items()):
                bidx = self.grid.GetBinIdx( sbin.center )
                gidx = self.grid.CptGlbIdxFromBinIdx( bidx )
                if self.occbins[gidx][imdl] is not None:
                    e0 = sbin.stderr
                    if e0 == 0:
                        e0 = 0.25
                    e1 = self.occbins[gidx][imdl].stderr
                    if e1 == 0:
                        e1 = 0.25
                    f0 = sbin.value
                    f1 = self.occbins[gidx][imdl].value
                    #print( sbin.value, [ self.occbins[gidx][uu].value for uu in range(len(self.occbins[gidx])) ] )
                    w = 1. / ( e0**2 + e1**2 )
                    #w = 1
                    df = f0-f1
                    wsum += w
                    offsets[imdl] += w*df
            #print(imdl,wsum,offsets[imdl])
            if wsum > 0:
                offsets[imdl] /= wsum
        return offsets

    def GetAvgModel(self):
        from ndfes import SpatialBin
        from ndfes import MBAR
        bins = {}
        if self.ref is None:
            for gidx in sorted(self.occbins):
                bidx = self.binidxs[gidx]
                value,stderr,entropy,size = self.GetBinValue(gidx)
                if value is None:
                    continue
                bins[gidx] = SpatialBin(bidx,value=value,stderr=stderr,entropy=entropy,size=size)
        else:
            for ridx,sbin in sorted(self.ref.bins.items()):
                bidx = self.grid.GetBinIdx( sbin.center )
                gidx = self.grid.CptGlbIdxFromBinIdx( bidx )
                value,stderr,entropy,size = self.GetBinValue(gidx)
                if value is None:
                    continue
                if self.use_ref_ene:
                    value = sbin.value
                    entropy = sbin.entropy
                    size = sbin.size
                bins[gidx] = SpatialBin(bidx,value=value,stderr=stderr,entropy=entropy,size=size)
        return MBAR(self.grid,bins)

    def Write(self,fh):
        ndim = len(self.grid.dims)
        fh.write("#!/usr/bin/env python3\n")
        fh.write("import ndfes\n")
        for idim in range(ndim):
            fh.write("dim%i = ndfes.SpatialDim( %23.13f, %23.14f, %6i, %s )\n"%(\
                        idim+1,self.grid.dims[idim].xmin,
                        self.grid.dims[idim].xmax,
                        self.grid.dims[idim].size,
                        self.grid.dims[idim].isper))
        fh.write("grid = ndfes.VirtualGrid([%s])\n"%(\
                    ",".join(["dim%i"%(i+1) for i in range(ndim)])))

        for omodel in range( 1 + len(self.models) ):
            imodel = omodel-1
            fh.write("model%i = ndfes.MBAR(grid,\n"%(omodel))
            fh.write("    {")

            binstrs = []

            if omodel == 0:
                if self.ref is None:
                    for gidx in sorted(self.occbins):
                        bidx = self.binidxs[gidx]
                        value,stderr,entropy,size = self.GetBinValue(gidx)
                        #entropy = 0
                        binstrs.append( self.GetBinString(gidx,value,stderr,entropy,size) )
                else:
                    for ridx,sbin in sorted(self.ref.bins.items()):
                        bidx = self.grid.GetBinIdx( sbin.center )
                        gidx = self.grid.CptGlbIdxFromBinIdx( bidx )
                        value,stderr,entropy,size = self.GetBinValue(gidx)
                        #entropy = 0
                        #print("use_ref_ene = ",use_ref_ene)
                        if self.use_ref_ene:
                            value = sbin.value
                            entropy = sbin.entropy
                            size = sbin.size
                        binstrs.append( self.GetBinString(gidx,value,stderr,entropy,size) )
            else:
                for gidx in sorted(self.occbins):
                    bidx = self.binidxs[gidx]
                    sbin = self.occbins[gidx][imodel]
                    if sbin is not None:
                        value,stderr = sbin.value + self.offsets[imodel],sbin.stderr
                        entropy = sbin.entropy
                        binstrs.append( self.GetBinString(gidx,value,stderr,entropy) )

            binstr = ",\n     ".join(binstrs) + " })\n\n"
            fh.write(binstr)
        modelstr = ",".join(["model%i"%(omodel) for omodel in range(1+len(self.models))])
        fh.write("models = [%s]\n\n"%(modelstr))

    

if __name__ == "__main__":

    import ndfes
    import numpy as np
    import argparse
    import sys
    from collections import defaultdict as ddict
    
    # create a keyvalue class
    class keyvalue(argparse.Action):
        # Constructor calling
        def __call__( self , parser, namespace,
                      values, option_string = None):
            if getattr(namespace,self.dest) is None:
                setattr(namespace, self.dest, ddict(list))
            for value in values:
                # split it into key and value
                if '=' in value:
                    key, value = value.split('=')
                else:
                    key, value = value,'0'
                    #raise Exception("--fes option expected filename=index,"+
                    #                " but received '%s'"%(value))
                    # assign into dictionary
                getattr(namespace, self.dest)[key].append(value)
                
    parser = argparse.ArgumentParser \
    ( formatter_class=argparse.RawDescriptionHelpFormatter,
      description="Averaged 1-or-more models from checkpoint file(s) "+
      "and writes a new checkpoint file")

    parser.add_argument \
        ("--fes",
         nargs='+',
         action='append',
         help="One or more models to average. E.g., chkptfile=0 will "+
         "read model 0 from the checkpoint file names 'chkptfile'."+
         "If the trailing '=idx' is missing, then '=0' is assumed.",
         required=True )


    parser.add_argument \
        ("--ene",
         help="If present, then read the energies from this checkpoint "+
         "file and use the --fes surfaces only to estimate the error. "+
         "The only difference between this option and --ref is: this "+
         "option reports the reference energy rather than the average "+
         "energy; i.e., the output model with --ene only modifies the "+
         "standard errors. "
         "This option also uses the chkptfile=i syntax.",
         required=False )

    parser.add_argument \
        ("--ref",
         help="If present, then shift the --fes surfaces to minimize "+
         "the error with respect to this reference surface, but "+
         "report the average energy instead of the reference energy. "+
         "This option also uses the chkptfile=i syntax.",
         required=False )

    
    parser.add_argument \
        ("-o","--out",
         help="output checkpoint file name",
         type=str,
         required=True )


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

    fesargs  = [item for sublist in args.fes for item in sublist]

    models=[]
    for fname in fesargs:
        #print("fname from args:",fname)
        models.append( ReadModel(fname) )
    use_ref_ene = False
    refmodel = None
    if args.ene is not None and args.ref is not None:
        raise Exception("Cannot simultaneously use --ene and --ref")
    if args.ene is not None:
        fname = args.ene
        refmodel = ReadModel(fname)
        #print(fname,refmodel)
        use_ref_ene = True
    elif args.ref is not None:
        fname = args.ref
        refmodel = ReadModel(fname)

    avg = AvgFES(models,ref=refmodel,use_ref_ene=use_ref_ene)

    if False:
        if refmodel is None and args.out is not None:
            for it in range(3):
                fh = open(args.out,"w")
                avg.Write(fh)
                fh.close()
                fesdict = { args.out : "0" }
                #print("reading",args.out)
                refmodel = ReadModel(args.out)
                #print("refmodel",str(refmodel))
                #exit(0)
                avg = AvgFES(models,ref=refmodel,use_ref_ene=False)
    
    # if args.out:
    #     fh = open(args.out,"w")
    # else:
    #     fh = sys.stdout
        
    # avg.Write(fh)

    models = [ avg.GetAvgModel() ] + avg.models
    
    for im,m in enumerate(avg.models):
        m.ShiftBinValues( -avg.offsets[im] )
    
    
    ndfes.SaveXml( args.out, models )
    
            
