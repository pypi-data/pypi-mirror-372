#!/usr/bin/env python3


class Disang(object):
    """A collection of restraints

    Attributes
    ----------
    restraints : list of Restraint
        The restraint definitions

    Methods
    -------
    """
    
    def __init__(self,fname):
        """
        Parameters
        ----------
        fname : str
            The name of the Amber restraint file (disang file)
        """
        from . Restraint import Restraint
        self.restraints=[]
        if fname is not None:
            rline=""
            fh = open(fname,"r")
            for line in fh:
                line = line.split("!")[0].strip()
                if "&rst" in line:
                    rline=line
                    if not ( "/" in line or "&end" in line ):
                        for line in fh:
                            line = line.split("!")[0].strip()
                            if "/" in line or "&end" in line:
                                rline += " " + line
                                break
                            else:
                                rline += " " + line
                    rline = rline.replace("/"," /")
                    self.restraints.append( Restraint(rline) )
                    rline=""
            fh.close()

            

    def Save(self,fname):
        """Writes restraint definitions to file

        Parameters
        ----------
        fname : str
            The name of the file to write
        """
        fh = open(fname,"w")
        self.Write(fh)
        fh.close()

        
    def Write(self,fh):
        """Writes restraint definitions to an opened file

        Parameters
        ----------
        fname : str
            The file object to write to
        """
        for rst in self.restraints:
            fh.write("%s\n"%( str(rst) ))

            
    def CptBiasEnergy(self,rcrds):
        """Computes the restraint bias energy in kcal/mol, given the
        collective variable values

        Parameters
        ----------
        rcrds : list of float
            The values of the collective variables. If it is an angle restraint,
            then it should be in units of degrees, not radians

        Returns
        -------
        e : float
            The bias potential energy in kcal/mol
        """

        e = 0
        n = len(rcrds)
        if n != len(self.restraints):
            raise Exception("len(rcrds) != len(self.restraints) (%i,%i)"%(n,len(self.restraints)))
        for i in range(n):
            e += self.restraints[i].CptBiasEnergy(rcrds[i])
        return e

    
    def CptCrds(self,crds,aidxs=None):
        """Evaluates the collective variable values from the atomic coordinates

        Parameters
        ----------
        crds : numpy.array, shape=(natom,3)
            The atomic coordinates

        aidxs : list of int, default=None
            If present, the crds is presumed to be a petite list of
            coordinates, and aidxs is a corresponding list of
            0-based indexes to the atoms for the full system

        Returns
        -------
        qs : numpt.array, shape=(nrestraint,)
            The values of the collective variable
        """

        import numpy as np
        n = len(self.restraints)
        qs = np.zeros( (n,) )
        for i in range(n):
            qs[i] = self.restraints[i].CptCrd(crds,aidxs=aidxs)
        return qs

    
    def ValidateTemplate(self):
        """Raises exception if the disang is not a properly formatted 
        template"""
        
        tvars = self._GetTemplateKeys()
        invalid = [ name for idx in tvars for name in tvars[idx]  ]
        valid = []
        for i in range(99):
            #v = "K%i"%(i+1)
            #valid.append(v)
            #while v in invalid: invalid.remove(v)
            v = "RC%i"%(i+1)
            valid.append(v)
            while v in invalid: invalid.remove(v)

        if len(invalid) > 0:
            raise Exception("Template disang contains invalid keys: "
                            +"%s\n"%(" ".join(invalid))
                            +"Expected one-or-more of: "
                            +"%s\n"%(" ".join(valid)))

        if len(tvars) == 0:
            raise Exception("Template disang does not have variables\n"
                            +"Expected one-or-more of: "
                            +"%s\n"%(" ".join(valid)))
 
        idxs = [ idx for idx in tvars ]
        idxs.sort()
        for i in range(len(idxs)):
    
            if len(tvars[idxs[i]]) > 1:
                raise Exception("Disang restraint contains multiple "
                                +"template variables: "
                                +"%i (%s)"%(idxs[i],str(tvars[idxs[i]])))
    
            for j in range(i+1,len(idxs)):
                for name in tvars[idxs[i]]:
                    if name in tvars[idxs[j]]:
                        raise Exception("Disang template variable %s "%(name)
                                        +"found in multiple restraints: "
                                        +"%i and %i\n"%(idxs[i],idxs[j])
                                        +"%s"%(str(tvars)))

            for i in range(len(idxs)):
                expected_name = "RC%i"%(i+1)
                if tvars[idxs[i]][0] != expected_name:
                    raise Exception("Disang restraint %i "%(idxs[i])
                                    +"contains name %s "%(tvars[idxs[i]][0])
                                    +"but the expected name is "
                                    +"%s"%(expected_name))

                
    def GetTemplateIdxs(self):
        """Return a list of restraint indexes that contain template
        variables

        Returns
        -------
        idx : list of int
            The sorted list of restraint indexes
        """
        tvars = self._GetTemplateKeys()
        idxs = [ idx for idx in tvars ]
        idxs.sort()
        return idxs

    
    def SetTemplateValues(self,rcs,ks=None):
        """Return a new disang object whose template variables are
        replaced by values

        Parameters
        ----------
        rcs : list of float
            The restraint values for each templated restraint
            The length of the list corresponds to the list of
            indexes provided by GetTemplateIdxs

        ks : list of float, default=None
            If provided, it is a corresponding list of force
            constants (kcal/mol/A^2 or kcal/mol/deg^2)

        Returns
        -------
        odis : Disang
            A copy of the disang object with replaced values
        """

        idxs = self.GetTemplateIdxs()
        if len(rcs) != len(idxs):
            raise Exception("Size mismatch in the number of "
                            +"restraints while trying to fill "
                            +"template disang: "
                            +"Expected %i but received %i"%(len(idxs),len(rcs)))
        valdict = {}
        for i in range(len(idxs)):
            name = "RC%i"%(i+1)
            valdict[name] = rcs[i]
            
        odis = self._FillTemplateFromDict(valdict)
        
        if ks is not None:
            if len(ks) != len(idxs):
                raise Exception("Size mismatch in the number of "
                                +"restraints while trying to fill "
                                +"force constants: "
                                +"Expected %i but received "%(len(idxs))
                                +"%i"%(len(ks)))
            for i in range(len(idxs)):
                odis.restraints[idxs[i]].rk2 = ks[i]
                odis.restraints[idxs[i]].rk3 = ks[i]
        return odis
        
        
    def _GetTemplateKeys(self):
        """Return a dict of template keys

        Returns
        -------
        ret : dict (key: int, value: list of str)
            The template variable names for each restraint
            The key is the index of the restraint, and the
            list is the variable names found in that restraint
            definition
        """
        keys = {}
        for i in range(len(self.restraints)):
            hs = self.restraints[i].GetTemplateKeys()
            if len(hs) > 0:
                keys[i] = hs
        return keys
    
            
    def _FillTemplateFromDict(self,valdict,warn=False):
        """Return a new instance of a disang object that replaces
        the template variables with numeric values

        Parameters
        ----------
        valdict : dict (keys: str, values: float)
            The variables to replace with values

        warn : bool, default=False
            Notify if the disang continues to have undefined keys

        Returns
        -------
        result : Disang
            A new instance with replaced values
        """
        import copy
        import sys
        result = copy.deepcopy(self)
        for i in range(len(result.restraints)):
            result.restraints[i] = result.restraints[i].FillTemplate(valdict)
        if warn:
            ks = result._GetTemplateKeys()
            if len(ks) > 0:
                sys.stderr.write("Undefined restraint values "
                                 +"remain after calling Disang.FillTemplate: "
                                 +"%s\n"%(str(ks)))
        return result
    
    
    def Subset(self,acols):
        """Returns a Disang object, whose restraints are the columns
        provided as input (1-based indexing)

        Attributes
        ----------
        acols : list of int
            The columns of the first Disang (1-based)

        Returns
        -------
        a : Disang
            The first Disang
        """
        a = Disang(None)
        a.restraints = [ self.restraints[i-1] for i in acols ]
        return a

    def GetUniqueAtomIdxs(self):
        """Returns a list of unique atom indexes used to define
        retraints

        Returns
        -------
        aidxs : list of int
            The sorted list of 0-based atom indexes
        """
        import numpy as np
        aidxs = []
        for res in self.restraints:
            aidxs.extend( [i-1 for i in res.iat] )
        
        return np.unique(aidxs)

    
    def GetWilsonB_FromCrds(self,crds,aidxs):
        import numpy as np
        nres = len(self.restraints)
        
        # uidxs = {}
        # for uidx, aidx in enumerate(aidxs):
        #     uidxs[aidx] = uidx
        
        nat = len(aidxs)
        B = np.zeros( (nres,3*nat) )

        if crds.shape[0] != nat:
            raise Exception("Expected %i atoms, but received %i\n"%(nat,crds.shape[0]))
        
        qs = np.zeros( (nres,) )
        for ires in range(nres):
            q,col = self.restraints[ires].GetWilsonElements(crds,aidxs)
            qs[ires] = q
            B[ires,:] = col[:]
        
        return qs,B
        

    # def GetWilsonB_FromTrajs(self,parm,tfiles):
    #     from . import ReadAvgCrds
        
    #     #aidxs = []
    #     #for res in self.restraints:
    #     #    aidxs.append( [i-1 for i in res.iat] )
    #     #aidxs = list(set(aidxs))

    #     aidxs = self.GetUniqueAtomIdxs()
    #     masses = np.array([ parm.atoms[i].mass for i in aidxs ])
        
    #     crds = ReadAvgCrds(tfiles,aidxs)
    #     qs,B,aidx = self.GetWilsonB_FromCrds(crds)
    #     return qs,B,aidx,crds


    def Split(self,acols):
        """Returns 2 disang objects, the first contains the
        restraints listed in acols, and the second contains
        all other restraints

        Parameters
        ----------
        acols : list of int
           The 1-based indexes of the restraints

        Returns
        -------
        disA : Disang
            The disang object containing the acol restraints
        
        disB : Disang
            The disang object containing the bcol restraints
        """
        bcols = []
        for i in range(len(self.restraints)):
            if i+1 in acols:
                pass
            else:
                bcols.append(i+1)
        return self.Subset(acols),self.Subset(bcols)
    

    def SavePlumed(self,fname,
                   stride=1,
                   pcv=None,
                   pcvs0=0,pcvz0=0,
                   pcvks=0,pcvkz=0):
        """Write a Plumed restraint file for use in sander

        Parameters
        ----------
        fname : str
            The plumed filename to write. It must end in '.plumed'

        stride: int, default=1
            The output stride to write the dumpave
            If stride < 1, then no output is written

        pcv: ndfes.PCV
            The path collective variable object. If None, then
            the biasing potentials are for the individual reaction
            coordinates. If pcv is present, then only the s and z
            PCV-coordinates will be biased.

        pcvs0: float, default=1.0
            The equilibrium position of the harmonic restraint on the PCV
            S-coordinate (this coordinate goes from 1 to N, which are the
            2 ends of the path). This is only used if pcv is not None.

        pcvz0: float, default=0.0
            The equilibrium position of the harmonic restraint on the PCV
            Z-coordinate (this coordinate goes from -inf to +inf, and a
            value of 0 means the point is located on the path).  This is 
            only used if pcv is not None.

        pcvks : float, default=0
            The force constant applied to the PCV S-coordinate in units
            of kcal/mol.  This is only used if pcv is not None.

        pcvkz : float, default=0
            The force constant applied to the PCV Z-coordinate in units
            of kcal/mol.  This is only used if pcv is not None.

        Returns
        -------
        xtra : Disang
            The extra restraints that were not written to the plumed
            file. These will include all half-harmonics, flat-well
            potentials, etc.
        """
        import numpy as np
        from pathlib import Path
        import copy
        
        fpath = Path(fname)
        if fpath.suffix != ".plumed":
            raise Exception(f"filename must end in '.plumed' but {fname} "
                            +f"ends in '{fpath.suffix}'")
        
        deg2rad = (np.pi/180.)
        rad2deg = 1/deg2rad
        kdeg2krad = (np.pi/180.)**2
        krad2kdeg = 1/kdeg2krad
        fh = open(fname,"w")

        xtra = Disang(None)

        ncv = 0
        rcs = []
        fcs = []
        isangle = []
        isper = []
        for ires,res in enumerate(self.restraints):
            if (res.r2 != res.r3) or \
               (res.rk2 != res.rk3):
                xtra.restraints.append(res)
                continue
            ncv += 1
            rcs.append(res.r2)
            fcs.append(res.rk2)
            if res.angle:
                isangle.append(1)
            else:
                isangle.append(0)
            if res.dihed:
                isper.append(1)
            else:
                isper.append(0)

        cvisangle = copy.deepcopy(isangle)
        cvisper = copy.deepcopy(isper)
        
        if pcv is not None:
            rcs = [pcvs0,pcvz0]
            fcs = [pcvks,pcvkz]
            isangle=[0,0]
            isper=[0,0]
            if pcv.pts.shape[1] != ncv:
                raise Exception(f"Disang defines {ncv} primitive CVs, "
                                +"but the PCV reference path is "
                                +f"{pcv.pts.shape[1]}-dimensional")
            
        
        fh.write("#NDFES PCV %i\n"%( pcv is not None ))
        pdbname = "none"
        pcvlam = 1
        if pcv is not None:
            pdbname = fpath.name + ".pcv.pdb"
            pdbpath = str(fpath) + ".pcv.pdb"
            pcvlam = pcv.lam
        fh.write("#NDFES PCVPDB %s\n"%( pdbname ))
        fh.write("#NDFES PCVLAM %.14e\n"%( pcvlam ))
        fh.write("#NDFES PCVDIM %i\n"%( ncv ))
        fh.write("#NDFES PCVISANGLE %s\n"%(" ".join(["%i"%(x) for x in cvisangle])))
        fh.write("#NDFES PCVISPER %s\n"%(" ".join(["%i"%(x) for x in cvisper])))
        fh.write("#NDFES NDIM %i\n"%(len(rcs)))
        fh.write("#NDFES RCS %s\n"%( " ".join(["%.14e"%(x) for x in rcs]) ) )
        fh.write("#NDFES FCS %s\n"%( " ".join(["%.14e"%(x) for x in fcs]) ) )
        fh.write("#NDFES ISANGLE %s\n"%(" ".join(["%i"%(x) for x in isangle])))
        fh.write("#NDFES ISPER %s\n"%(" ".join(["%i"%(x) for x in isper])))
        fh.write("\n")

        
        fh.write("UNITS LENGTH=A TIME=ps ENERGY=kcal/mol\n\n")
        rcnt=0
        acnt=0
        tcnt=0
        args=[]
        for ires,res in enumerate(self.restraints):
            
            if (res.r2 != res.r3) or \
               (res.rk2 != res.rk3):
                continue

            if isinstance(res.r2,float):
                if res.dihed or res.angle:
                    AT="%.13e"%(res.r2) #*deg2rad)
                else:
                    AT="%.13e"%(res.r2)
            else:
                AT=res.r2
            
            if res.dihed:
                tcnt += 1
                fh.write(f"t{tcnt}: TORSION ATOMS={res.iat[0]},"
                         +f"{res.iat[1]},{res.iat[2]},{res.iat[3]}\n")
                fh.write(f"rc{ires+1}: CUSTOM ARG=t{tcnt} "
                         +"FUNC=%.14e*x PERIODIC=%.14e,%.14e\n"\
                         %(rad2deg,-180,180))
                args.append(f"rc{ires+1}")
                if pcv is None:
                    fh.write(f"erc{ires+1}: RESTRAINT ARG=rc{ires+1} AT={AT} "
                             +"KAPPA=%.13e\n"%(2*res.rk2))
            elif res.angle:
                acnt += 1
                fh.write(f"a{acnt}: ANGLE ATOMS={res.iat[0]},"
                         +f"{res.iat[1]},{res.iat[2]}\n")
                fh.write(f"rc{ires+1}: CUSTOM ARG=a{acnt} "
                         +"FUNC=%.14e*x PERIODIC=NO\n"%(rad2deg))
                args.append(f"rc{ires+1}")
                if pcv is None:
                    fh.write(f"erc{ires+1}: RESTRAINT ARG=rc{ires+1} AT={AT} "
                             +"KAPPA=%.13e\n"%(2*res.rk2))
            elif res.r12:
                fh.write(f"r{rcnt+1}: DISTANCE ATOMS={res.iat[0]},"
                         +f"{res.iat[1]}\n")
                fh.write(f"r{rcnt+2}: DISTANCE ATOMS={res.iat[2]},"
                         +f"{res.iat[3]}\n")
                
                fh.write(f"rc{ires+1}: CUSTOM ARG=r{rcnt+1},r{rcnt+2}")
                if res.rstwt[0] == 1 and res.rstwt[1] == -1:
                    fh.write(" FUNC=x-y PERIODIC=NO\n")
                elif res.rstwt[0] == -1 and res.rstwt[1] == 1:
                    fh.write(" FUNC=y-x PERIODIC=NO\n")
                else:
                    fh.write(" FUNC=(%.5f)*x+(%.5f)*y PERIODIC=NO\n")
                args.append(f"rc{ires+1}")
                if pcv is None:
                    fh.write(f"erc{ires+1}: RESTRAINT ARG=rc{ires+1} AT={AT} "
                             +"KAPPA=%.13e\n"%(2*res.rk2))
                rcnt += 2
            else:
                fh.write(f"rc{rcnt+1}: DISTANCE ATOMS={res.iat[0]},"
                         +f"{res.iat[1]}\n")
                args.append(f"rc{ires+1}")
                if pcv is None:
                    fh.write(f"erc{ires+1}: RESTRAINT ARG=rc{ires+1} AT={AT} "
                             +"KAPPA=%.13e\n"%(2*res.rk2))
                rcnt += 1
            fh.write("\n")

        if stride > 0:
            fh.write("PRINT ARG=%s STRIDE=%i "%(",".join(args),stride)
                     +f"FILE={fpath.name}.dumpave FMT=%11.3f\n")

                    
        if pcv is not None:
            pcv.SavePDB(pdbpath)
            fh.write("\n")
            fh.write("pcv: PATH TYPE=NORM-EUCLIDEAN LAMBDA=%.14e "%(pcv.lam)
                     +f"REFERENCE={pdbname}\n")
            fh.write("spath: CUSTOM ARG=pcv.spath "
                     +f"FUNC=(x-1)/{pcv.pts.shape[0]-1} "
                     +"PERIODIC=NO\n");
            fh.write("epcv1: RESTRAINT ARG=spath "
                     +"AT=%.14e "%(pcvs0)
                     +"KAPPA=%.14e\n"%(pcvks))
            fh.write("epcv2: RESTRAINT ARG=pcv.zpath "
                     +"AT=%.14e "%(pcvz0)
                     +"KAPPA=%.14e\n"%(pcvkz))
            fh.write("\n")
            if stride > 0:
                fh.write(f"PRINT ARG=spath,pcv.zpath STRIDE={stride} "
                         +f"FILE={fpath.name}.pcv.dumpave FMT=%14.6f\n")
            
        fh.write("\n")

        return xtra
