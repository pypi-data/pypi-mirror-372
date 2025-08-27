#!/usr/bin/env python3

from importlib.metadata import version, PackageNotFoundError

def get_package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Unknown"
    
if __name__ == "__main__":

    
    import argparse
    import ndfes
    import sys
    import os
    import pathlib

    
    parser = argparse.ArgumentParser \
        ( formatter_class=argparse.RawDescriptionHelpFormatter,
          description="""
          Combine metafiles and write a new metafile whose dumpave
          locations are relative to the current working directory
          (by default) or relative to the directory to which the
          new metafile is written.  If only 1 input metafile is
          provided, then this script effectively copies the metafile
          and shifts the dumpave paths accordingly""" )


    parser.add_argument \
        ("-o","--out",
         help="The output metafile to write",
         type=str,
         required=True)
          
    
    parser.add_argument \
         ('metafiles',
          help="One-or-more input metafiles",
          nargs='+',
          action='append',
          type=str)

    
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

    imetas  = [pathlib.Path(item) for sublist in args.metafiles for item in sublist]

    for imeta in imetas:
        if not imeta.is_file():
            raise Exception("Metafile not found: %s"%(imeta))

    ometa = pathlib.Path(args.out)

        
    metas = [ ndfes.Metafile(m) for m in imetas ]
    fh = open(ometa,"w")
    seen=[]
    for m in metas:
        p = m.RelativeTo(ometa.parent)
        seen = p.write(fh,seen=seen)
    fh.close()
