#!/usr/bin/env python3



def LoadModule(pyfilename):
    """
    Loads a python file as a python module

    Parameters
    ----------
    pyfilename : str
        filename of the python module

    Returns
    ----------
    module
        a reference to the loaded module
    """
    
    import importlib.machinery
    import importlib.util
    import importlib
    import os
    import errno
    import sys
    sys.dont_write_bytecode = True

    if not os.path.isfile(pyfilename):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), pyfilename)
    
    modname = pyfilename.replace(".","d").replace("-","h")
    modname = modname.replace("_","u")
    modname = modname.replace("/","s").replace("\\","b")
    modname = modname.replace("~","t").replace("#","o")
    modname = modname.replace("@","a").replace("%","p")
    #spec = importlib.util.spec_from_file_location(modname, pyfilename)
    #usermod = importlib.util.module_from_spec(spec)
    #spec.loader.exec_module(usermod)
    #print("Reading",pyfilename,"as",modname)
    
    importlib.invalidate_caches()
    loader = importlib.machinery.SourceFileLoader(modname,pyfilename)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    usermod = importlib.util.module_from_spec(spec)
    loader.exec_module(usermod)
    #print(usermod)
    #exit(0)
    return usermod


def SaveXml(fname,models):
    """Saves a list of models to a file in XML format

    Parameters
    ----------
    fname : str
        Filename to write

    models : list of ndfes.MBAR or ndfes.vFEP objects
        The models to write
    """
    import xml.etree.ElementTree as ET
    #import html as HTML
    import xml.dom.minidom as md
    import os
    
    root = ET.Element("ndfes")
    for imodel,model in enumerate(models):
        ele = model.GetXml()
        ele.attrib["idx"] = str(imodel)
        root.append(ele)
    xmlstr = ET.tostring(root,encoding="unicode") #,method="html")
    dom = md.parseString( xmlstr )     
    # To parse string instead use: dom = md.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")
    # remove the weird newline issue:
    pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines()
                                  if s.strip()])
    fh = open(fname,"w")
    fh.write(pretty_xml)
    fh.close()
    

def GetModelsFromFile(filename):
    """Loads a ndfes checkpoint file as ndfes.MBAR or ndfes.vFEP
    objects and returns the list of objects.

    Parameters
    ----------
    filename : str
        Checkpoint filename

    Returns
    ----------
    list of ndfes.MBAR or ndfes.vFEP objects
        The free energy surfaces
    """
    from . SpatialDim import SpatialDim
    from . SpatialBin import SpatialBin
    from . VirtualGrid import VirtualGrid
    from . MBAR import MBAR
    from . vFEP import vFEP
    
    try:
        mdict = {}
        import xml.etree.ElementTree as ET
        tree = ET.parse(filename)
        root = tree.getroot()
        for mnode in root.findall('model'):
            #
            # model index
            #
            midx = int(mnode.get('idx'))
            #
            # model type
            #
            mtype = mnode.find('type').text.upper()

            kb = 0.0019872066135803628
            knode = mnode.find('kb')
            if knode is not None:
                kb = float(knode.text)
                
            #
            # bspl order
            #
            order = None
            tnode = mnode.find('order')
            if tnode is not None:
                order = int(tnode.text)

            #
            # grid definition
            #
            gnode = mnode.find('grid')
            dims = {}
            for dnode in gnode.findall('dim'):
                didx = int(dnode.get('idx'))
                xmin = float(dnode.find('xmin').text)
                xmax = float(dnode.find('xmax').text)
                size = int(dnode.find('size').text)
                isper = int(dnode.find('isper').text)
                if isper <= 0:
                    isper = False
                else:
                    isper = True
                dims[didx] = SpatialDim(xmin,xmax,size,isper)
                #print(didx,xmin,xmax,size,isper)
            dimlist = [None]*len(dims)
            for didx in sorted(dims):
                dimlist[didx] = dims[didx]
            grid = VirtualGrid( dimlist )
            
            ndim = grid.ndim

            #
            # occupied bins
            #
            bins = {}
            for bnode in mnode.findall('bin'):
                gidx = int(bnode.get('idx'))
                
                bidxs = [0]*ndim
                for cnode in bnode.findall('bidx'):
                    bidxs[ int(cnode.get('idx')) ] = int(cnode.text)
                    
                val = None
                tnode = bnode.find('val')
                if tnode is not None:
                    val = float(tnode.text)
                    
                err = None
                tnode = bnode.find('err')
                if tnode is not None:
                    err = float(tnode.text)
                
                rew = None
                tnode = bnode.find('re')
                if tnode is not None:
                    rew = float(tnode.text)
                
                size = None
                tnode = bnode.find('size')
                if tnode is not None:
                    size = int(tnode.text)

                bins[gidx] = SpatialBin(bidxs,value=val,stderr=err,
                                        entropy=rew,size=size)
            # 
            # vFEP corner parameters
            #
            corners = {}
            for cnode in mnode.findall('corner'):
                cidx = int(cnode.get('idx'))
                val = float( cnode.find('val').text )
                err = float( cnode.find('err').text )
                corners[cidx] = (val,err)
            
            if mtype == "MBAR":
                mdict[midx] = MBAR(grid,bins,kb=kb)
            elif mtype == "VFEP":
                mdict[midx] = vFEP(grid,bins,order,corners,kb=kb)
            else:
                raise Exception(f"Unknown model type {mtype}")
            
        models = [None]*len(mdict)
        for midx in sorted(mdict):
            models[midx] = mdict[midx]
        
            
    except Exception as xmlmsg:
        try:
            models = LoadModule(filename).models
            import os
            import sys
            import shutil
            sys.stderr.write("Read a checkpoint file generated "
                             +"from ndfes version 2. This format is "
                             +"deprecated in favor of xml format.\n")

            sys.stderr.write(f"Copying {filename} -> {filename}.bak\n")
            shutil.copyfile(filename,filename+".bak")
            #if os.path.exists(filename + ".xml"):
            #    sys.stderr.write(f"Not writing {filename}.xml because "
            #                     +"it already exists\n")
            #else:
            sys.stderr.write(f"Overwriting {filename} in XML format\n")
            SaveXml(filename,models)
                
        except Exception as pymsg:
            models = None
            raise Exception(f"Could not load {filename} as an xml "
                            +"file nor python module. "
                            +f"Received msgs:\n{xmlmsg}\n{pymsg}")

    return models


def InferEnergyUnitsFromBoltzmannConstant(kb):
    from . constants import AU_PER_ELECTRON_VOLT
    from . constants import AU_PER_KCAL_PER_MOL
    from . constants import AU_PER_CAL_PER_MOL
    from . constants import AU_PER_JOULE_PER_MOL
    from . constants import AU_PER_KJOULE_PER_MOL
    from . constants import BOLTZMANN_CONSTANT_AU

    vals = {
        #
        # 8.617342790900664e-05
        "eV"       : BOLTZMANN_CONSTANT_AU() / AU_PER_ELECTRON_VOLT(),
        #
        # 0.001987206613580358
        "kcal/mol" : BOLTZMANN_CONSTANT_AU() / AU_PER_KCAL_PER_MOL(),
        #
        # 1.9872066135803579
        "cal/mol"  : BOLTZMANN_CONSTANT_AU() / AU_PER_CAL_PER_MOL(),
        #
        # 8.314472471220217
        "J/mol"    : BOLTZMANN_CONSTANT_AU() / AU_PER_JOULE_PER_MOL(),
        #
        # 0.008314472471220217
        "kJ/mol"   : BOLTZMANN_CONSTANT_AU() / AU_PER_KJOULE_PER_MOL() }


    if kb is None:
        label = "kcal/mol"
    else:
        label = "Unknown Units"
        bestdiff = 1.e+30
        bestkey = None
        for key in vals:
            x = vals[key]
            d = abs(kb-x)
            if d < bestdiff:
                bestdiff = d
                bestkey = key
        x = vals[bestkey]
        if kb > 0.99*x and kb < 1.01*x:
            label = bestkey
    return label

