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
    
    parser = argparse.ArgumentParser \
        ( formatter_class=argparse.RawDescriptionHelpFormatter,
          description="""
          Reads dumpave (or netcdf trajectory) files and writes input trace
          files for ndfes.  The active collective variables are selected with
          the --rxn option.  If a multiple-Hamiltonian wTP or gwTP analysis
          is desired, then one use --ene to read the potential energies from
          a series of mdout files.

          Example 1
          ---------
              A 1D FES umbrella window for vFEP or MBAR analysis
              There is only 1 collective variable (the first variable in the
              disang file).  All other restraints are ignored.

              ndfes-PrepareAmberData.py -d rc_0.00.disang -i rc_0.00.dumpave \\
                  -o dumpaves/rc_0.00.dumpave -r 1

              The output file will contain 2 columns:
                 1. The simulation step
                 2. The value of the first collective variable

              One would analyze the resulting files with:
              "ndfes --mbar" or "ndfes --vfep"

          Example 2
          ---------
              A 2D FES umbrella window for vFEP or MBAR analysis
              There are 2 collective variable (the first two variables in the
              disang file).  All other restraints are ignored.

              ndfes-PrepareAmberData.py -d rc_0.00_0.00.disang \\
                  -i rc_0.00_0.00.dumpave \\
                  -o dumpaves/rc_0.00_0.00.dumpave -r 1 2

              The output file will contain 3 columns:
                 1. The simulation step
                 2. The value of the first collective variable
                 3. The value of the second collective variable

              One would analyze the resulting files with:
              "ndfes --mbar" or "ndfes --vfep"

          Example 3
          ---------
              A 1D FES umbrella window for wTP analysis, in which the effect
              of a second biasing potential is removed.

              ndfes-PrepareAmberData.py -d rc_0.00.disang -i rc_0.00.dumpave \\
                  -o dumpaves/rc_0.00.dumpave -r 1 -b 2

              The output file will contain 4 columns:
                 1. The simulation step
                 2. The value of the first collective variable
                 3. The bias energy (kcal/mol) caused by the 2nd CV
                 4. The potential energy without the bias (which is safely
                    chosen to be 0.0

              One would analyze the resulting files with:
              ndfes --mbar --nham=2
              The biased FES would correspond to "model 0" and the
              unbiased FES would be "model 1"

          Example 4
          ---------
              A 1D FES umbrella window for wTP analysis, in which a low
              level Hamiltonian is transformed to a high level Hamiltonian

              If the simulation was performed with the low level Hamiltonian,
              then --hamidx is set to 0 to indicate that the corresponding
              low level energies are stored in the first instance of --ene

              ndfes-PrepareAmberData.py -d rc_0.00.disang \\
                  --hamidx 0 -i LL_0.00.nc \\
                  -o dumpaves/rc_0.00.dumpave -r 1 \\
                  --ene LL_0.00.mdout --ene HL_0.00.mdout

              whereas, if the high-level Hamiltonian produced the trajectory,
              then --hamidx=1 because the high level energies are stored in
              the second instance of --ene

              ndfes-PrepareAmberData.py -d rc_0.00.disang \\
                  --hamidx 1 -i HL_0.00.nc \\
                  -o dumpaves/rc_0.00.dumpave -r 1 \\
                  --ene LL_0.00.mdout --ene HL_0.00.mdout

              The output file will contain 4 columns:
                 1. The simulation step
                 2. The value of the first collective variable
                 3. The low level potential energy
                 4. The high level potential energy

              One would analyze the resulting files with:
              ndfes --mbar --nham=2
              The low level FES would correspond to "model 0" and the
              high level FES would be "model 1"

          Example 5
          ---------
              This is the same as Example 4; however, the high-level
              simulations were restart several times to yield several
              trajectory and reanalysis files

              ndfes-PrepareAmberData.py -d rc_0.00.disang \\
                  --hamidx 1 -i HL_0.00.nc HL_0.00_rst1.nc HL_0.00_rst2.nc \\
                  -o dumpaves/rc_0.00.dumpave -r 1 \\
                  --ene LL_0.00.mdout LL_0.00_rst1.mdout LL_0.00_rst2.mdout \\
                  --ene HL_0.00.mdout HL_0.00_rst1.mdout HL_0.00_rst2.mdout

              The output file will contain 4 columns:
                 1. The simulation step
                 2. The value of the first collective variable
                 3. The low level potential energy
                 4. The high level potential energy

              One would analyze the resulting files with:
              ndfes --mbar --nham=2
              The low level FES would correspond to "model 0" and the
              high level FES would be "model 1"

          Example 6
          ---------
              This is the same as Example 4; however, an additional bias
              potential is removed from the 1D FES

              ndfes-PrepareAmberData.py -d rc_0.00.disang \\
                  --hamidx 1 -i HL_0.00.nc \\
                  -o dumpaves/rc_0.00.dumpave -r 1 -b 2 \\
                  --ene LL_0.00.mdout --ene HL_0.00.mdout

              The output file will contain 6 columns:
                 1. The simulation step
                 2. The value of the first collective variable
                 3. The biased low level potential energy
                 4. The biased high level potential energy
                 5. The unbiased low level potential energy
                 6. The unbiased high level potential energy

              One would analyze the resulting files with:
              ndfes --mbar --nham=4
              The biased low level FES would correspond to "model 0".
              The biased high level FES would be "model 1"
              The unbiased low level FES would be "model 2"
              The unbiased high level FES would be "model 3"
          """ )
    
    parser.add_argument \
        ("-d","--disang",
         help="disang file defining the restraint energies",
         type=str,
         required=True )
    
    parser.add_argument \
        ("-T","--temp",
         help="temperature, default=298.",
         type=float,
         default=298,
         required=False )
    
    parser.add_argument \
        ("-i","--inp",
         help="input dumpave file(s) or netcdf trajectory files. Multiple files can be listed for each instance of --inp, which are interpretted as a series of restarts",
         type=str,
         nargs='+',
         action='append',
         required=True )
    
    parser.add_argument \
        ("-o","--out",
         help="output dumpave file",
         type=str,
         required=True )

    parser.add_argument \
        ("-r","--rxn",
         help="column indexes of the desired reaction coordinates",
         type=int,
         action='append',
         nargs='+',
         required=True )

    parser.add_argument \
        ("-b","--bias",
         help="column indexes of the biased coordinates",
         type=int,
         action='append',
         nargs='+',
         required=False )


    parser.add_argument \
        ("-e","--ene",
         help="mdout file(s) containing the potential energy for each frame. Multiple files can be listed for each instance of --ene, which are interpretted as a series of restarts.  Each instance of --ene begins a list of mdout files for a new Hamiltonian.  The ordering of the mdouts must be consistent with the ordering of the --inp files",
         type=str,
         action='append',
         nargs='+',
         required=False )

    
    parser.add_argument \
        ("-H","--hamidx",
         help="the index of the Hamiltonian that produced the trajectory, default: 0",
         type=int,
         default=0,
         required=False )


    parser.add_argument \
        ("-s","--sym",
         help="negate the observed samples of the specified reaction coordinate",
         type=int,
         required=False )

    parser.add_argument \
        ("-w","--width",
         help="The histogram bin width. Use this option multiple times for multiple dimensions. If used only used once, then it assumes each dimension uses the same width. If used multiple times, it must be used the same number of times as the --rxn option. If this option is used, then the output samples will be shifted by +1.e-6 if it would lie exactly on the border of two bins. This is only useful when creating dumpave files for systems that will use the --sym option, because negating a sample precisely on a border does not round the bin-index 'away from zero' in a manner that required to perfectly enforce the desired symmetry.",
         type=float,
         action='append',
         nargs='+',
         required=False )

    

    parser.add_argument \
        ("-P","--prefix",
         help="remove the leading string from the output dumpave filename when writing the metafile",
         type=str,
         default="",
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


    out_path = pathlib.Path(args.out)
    if not out_path.parents[0].is_dir():
        raise Exception("Directory does not exist: %s"%(out_path.parents[0]))
    if len(args.prefix) > 0:
        pre_path = pathlib.Path(args.prefix)
        out_path = out_path.relative_to(*pre_path.parts)

    
    
    # the list of column indexes for the active collective variables
    rxncols  = [item for sublist in args.rxn for item in sublist]

    # the list of column indexes for the extra bias to be removes
    biascols = []
    if args.bias is not None:
        biascols  = [item for sublist in args.bias for item in sublist]

    # the list of bin widths for each column
    widths = None
    if args.width is not None:
        widths = [item for sublist in args.width for item in sublist]
        if len(widths) == 1:
            widths = [widths[0]]*len(rxncols)
        elif len(widths) != len(rxncols):
            raise Exception(f"Expected to read {len(rxncols)} values "
                            f"of --width, but only {len(widths)} were "
                            "provided")
        
    # if a column is not in rxncols nor biascols, then it is ignored


    if args.ene is not None:
        for hamfiles in args.ene:
            for hamfile in hamfiles:
                if not pathlib.Path(hamfile).exists():
                    raise Exception("File not found: %s"%(hamfile))
    

    
    # the restraint definitions
    disang = ndfes.amber.Disang( args.disang )

    
    
    # the list of dumpaves to read
    idumps = [item for sublist in args.inp for item in sublist]
    if args.out in idumps:
        raise Exception("Output dumpave cannot be one of the input dumpaves")


    
    # read the dumpave (or netcdf trajectory) files
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
        else:
            data = []
            rawdata = np.loadtxt(idump)
            tprev = -1
            for i in range(rawdata.shape[0]):
                t = rawdata[i,0]
                if t == tprev:
                    data[-1] = rawdata[i,:]
                else:
                    data.append(rawdata[i,:])
                tprev = t
            data = np.array(data)
        datas.append(data)
    data = np.concatenate( datas )


    if widths is not None:
        for c,w in zip(rxncols,widths):
            for i in range(data.shape[0]):
                frep = data[i,c] / w
                irep = int(round(frep))
                if abs(frep-irep) < 1.e-6:
                    data[i,c] += 1.e-6
    
    # reverse a collective variable and sampling, if requested
    
    if args.sym is not None:
        disang.restraints[args.sym-1].Reverse()
        data[:,args.sym] *= -1
        # for i in range(data.shape[0]):
        #     if data[i,args.sym] == 0.0:
        #         #print(f"{i} {data[i,args.sym]}")
        #         data[i,args.sym] = -0.0001
        
    
    # compute the bias energy, if necessary
    
    biasenes = []
    if len(biascols) > 0:
        bias = disang.Subset(biascols)
        for i in range(data.shape[0]):
            biasenes.append( bias.CptBiasEnergy( data[i,biascols] ) )
        biasenes = np.array(biasenes)


            
    # create the matrix of potential energies
    nham = 0
    if args.ene is not None:
        nham = len(args.ene)
    if nham > 0:
        ntotham = nham
        if len(biascols) > 0:
            ntotham = nham * 2
        eptots = np.zeros( (data.shape[0],ntotham) )
        for iham,ham in enumerate(args.ene):
            i0 = 0
            for mdout in ham:
                enes = ndfes.amber.ReadEnergies( mdout )
                n = len(enes)
                if i0+n > eptots.shape[0]:
                    raise Exception("Read too many energies "
                                    +"(found %i but expected %i) "%(i0+n+1,data.shape[0])
                                    +"for Hamiltonian %i upon reading: %s"%(iham,str(ham)))
                eptots[i0:i0+n,iham] = enes
                i0 += n
            if i0 != data.shape[0]:
                raise Exception("Did not read enough energies "
                                +"(read %i energies but expected %i) "%(i0,data.shape[0])
                                +"for Hamiltonian %i upon reading: %s"%(iham,str(ham)))
        if ntotham > nham:
            for iham in range(nham):
                eptots[:,iham+nham] = eptots[:,iham]
                eptots[:,iham] += biasenes[:]
    elif len(biascols) > 0:
        eptots = np.zeros( (data.shape[0],2) )
        eptots[:,0] = biasenes[:]
            
    # write the new dumpave
    
    fh = open(args.out,"w")
    for i in range(data.shape[0]):
        fh.write("%8i"%(int(data[i,0])))
        for j in rxncols:
            fh.write(" %15.6f"%(data[i,j]))
        if len(biascols) > 0 or nham > 0:
            for iham in range(eptots.shape[1]):
                fh.write(" %23.14e"%(eptots[i,iham]))
        fh.write("\n")
    fh.close()



    # write the line for the metafile
    
    sys.stdout.write("%i %6.2f %s"%(args.hamidx,args.temp,out_path))
    for col in rxncols:
        r = disang.restraints[col-1]
        k = r.rk2
        x0 = r.r2
        sys.stdout.write("%12.6f %23.14e"%(x0,k))
    sys.stdout.write("\n");

