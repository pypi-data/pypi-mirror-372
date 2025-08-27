#!/usr/bin/env python3




class Restraint(object):
    """Stores restraint definition

    Attributes
    ----------
    line : str
        The fortran namelist string used to define the restraint

    angle : bool
        Indicates if the restraint is a 3-atom angle definition

    dihed : bool
        Indicates if the restraint is a 4-atom dihedral angle definition

    r12 : bool
        Indicates if the restraint is a 4-atom R12 definition

    iat : list of int
        The indexes of the atoms involved in the restraint (1-based indexing)

    rstwt : list of float
        The coefficients of the linear combination of distances used in the
        R12 distance definition

    r1 : float
        The lower bound of the restraint, below which the penalty is linear

    r2 : float or str
        The lower center of the flat harmonic. If string, then this is a
        template definition
    
    r3 : float or str
        The upper center of the flat harmonic. If string, then this is a
        template definition

    r4 : float
        The upper bound of the restraint, above which the penalty is linear

    rk2 : float or str
        The quadratic penalty between r1 and r2
        Note that angle and dihedral restraints list this value in units of
        (kcal/mol) * radian**(-2); however, it is immediately converted to
        (kcal/mol) * degree**(-2) because the angles are assumed to be in
        degrees -- as per Amber convention.
        If string, then this is a template definition

    rk3 : float or str
        The quadratic penalty between r3 and r4
        Note that angle and dihedral restraints list this value in units of
        (kcal/mol) * radian**(-2); however, it is immediately converted to
        (kcal/mol) * degree**(-2) because the angles are assumed to be in
        degrees -- as per Amber convention.
        If string, then this is a template definition

    Methods
    -------
    """
    
    def __init__(self,line):
        """
        Parameters
        ----------
        line : str
            The fortran namelist definition of the restraint.
            The namelist should begin with &rst and end with / or &end
        """
        
        import re
        import numpy as np
        
        self.line = line
        self.angle = False
        self.dihed = False
        self.r12 = False
        self.iat = []
        self.rstwt = []
        self.r1 = -1000.
        self.r2 = 0
        self.r3 = 0
        self.r4 = 1000.
        self.rk2 = 0
        self.rk3 = 0

        line = line.replace(","," ")
        cols = line.split()
        cols.remove("&rst")
        if "/" in cols:
            cols.remove("/")
        if "&end" in cols:
            cols.remove("&end")
        line = " ".join(cols)
        
        
        keyvals = re.findall(r"(.*?)=([^=]+)",line)
        for i in range(len(keyvals)):
            k,v = keyvals[i]
            keyvals[i] = (k.strip(),v.strip())
        for i in range(len(keyvals)):
            k,v = keyvals[i]
            if len(k) == 0:
                pk,pv = keyvals[i-1]
                cols = pv.split()
                k = cols.pop()
                pv = " ".join(cols)
                keyvals[i-1] = pk,pv
                keyvals[i] = k,v
                
        
        for k,v in keyvals:
            if k == "iat":
                self.iat = [ int(x) for x in v.split() ]
                self.angle=False
                if len(self.iat) == 3:
                    self.angle = True
                elif len(self.iat) == 4:
                    if "rstwt" in [ k for k,v in keyvals ]:
                        self.angle = False
                        self.r12 = True
                    else:
                        self.angle = True
                        self.dihed = True
            elif k == "rk2":
                try:
                    self.rk2 = float(v)
                except Exception as e:
                    self.rk2 = v
            elif k == "rk3":
                try:
                    self.rk3 = float(v)
                except Exception as e:
                    self.rk3 = v
            elif k == "r1":
                self.r1 = float(v)
            elif k == "r2":
                try:
                    self.r2 = float(v)
                except Exception as e:
                    self.r2 = v
            elif k == "r3":
                try:
                    self.r3 = float(v)
                except Exception as e:
                    self.r3 = v
            elif k == "r4":
                self.r4 = float(v)
            elif k == "rstwt":
                self.rstwt = [ float(x) for x in v.split() ]
                
        if self.angle:
            f = (np.pi/180.)**2
            if isinstance(self.rk2, float):
                self.rk2 *= f
            if isinstance(self.rk3, float):
                self.rk3 *= f

                
    def is_template(self):
        """Return True if this is a template definition of a restraint"""
        return (not isinstance(self.r2,float)) \
            or (not isinstance(self.r3,float)) \
            or (not isinstance(self.rk2,float)) \
            or (not isinstance(self.rk2,float))

                
    def __str__(self):
        """Returns a fortran namelist that defines the restraint

        Returns
        -------
        s : str
            The fortran namelist string
        """
        
        import numpy as np
        s  = "&rst\n"
        s += "  iat = %s\n"%( ", ".join(["%i"%(x) for x in self.iat]) )
        if self.r12:
            s += "  rstwt = %s\n"%( ", ".join(["%.2f"%(x) for x in self.rstwt]))
        if isinstance(self.r2,float):
            s +=  "  r2  = %18.13f,"%(self.r2)
        else:
            s +=  "  r2  = %s,"%(self.r2)
        if isinstance(self.r3,float):
            s += "  r3 = %18.13f\n"%(self.r3)
        else:
            s += "  r3 = %s\n"%(self.r3)

        s += "  r1  = %18.13f,  r4 = %18.13f\n"%(self.r1,self.r4)
        rk2 = self.rk2
        rk3 = self.rk3
        f = (np.pi/180.)**2
        if self.angle:
            if isinstance(rk2,float):
                rk2 /= f
            if isinstance(rk3,float):
                rk3 /= f
                
        if isinstance(rk2,float):
            s += "  rk2 = %18.13f,"%(rk2)
        else:
            s += "  rk2 = %s,"%(rk2)
            
        if isinstance(rk3,float):
            s += " rk3 = %18.13f\n"%(rk3)
        else:
            s += " rk3 = %s\n"%(rk3)

        s += "&end\n"
        return s
            
    def CptBiasEnergy(self,r):
        """Computes the restraint bias energy in kcal/mol, given a
        collective variable value

        Parameters
        ----------
        r : float
            The value of the collective variable. If it is an angle restraint,
            then it should be in units of degrees, not radians

        Returns
        -------
        e : float
            The bias potential energy in kcal/mol
        """

        if self.is_template():
            e=None
        else:
            e = 0
            if r < self.r1:
                h = self.rk2 * (self.r1-self.r2)**2
                m = 2 * self.rk2 * (self.r1-self.r2)
                e = h + m*(r-self.r1)
            elif r < self.r2:
                e = self.rk2 * (r-self.r2)**2
            elif r < self.r3:
                e = 0
            elif r < self.r4:
                e = self.rk3 * (r-self.r3)**2
            else:
                h = self.rk3 * (self.r4-self.r3)**2
                m = 2 * self.rk3 * (self.r4-self.r3)
                e = h + m*(r-self.r4)
        return e


    def Reverse(self):
        """Reverses the ordering of the atoms and positions defining
        the bias. This is typically only useful for easily symmetrizing
        free energy surfaces of symmetric R12 reactions"""
        if self.is_template():
            raise Exception("Cannot reverse the atom ordering of a "
                            +"template restraint definition")
        self.r1,self.r4 = -self.r4,-self.r1
        self.r2,self.r3 = -self.r3,-self.r2
        self.rk2,self.rk3 = self.rk3,self.rk2
        self.iat.reverse()
        self.rstwt = [ -x for x in self.rstwt ]

        
    def CptCrd(self,crds,aidxs=None):
        """Evaluates the collective variable value from the atomic coordinates

        Parameters
        ----------
        crds : numpy.array, shape=(natom,3)
            The atomic coordinates

        aidxs : list of int, default=None
            If present, then crds is presumed to be a petite list of
            coordinates (rather than the full system), and aidxs 
            provides the 0-based index of the atom in the full list
            of coordinates.

        Returns
        -------
        q : float
            The value of the collective variable
        """

        umap=None
        if aidxs is not None:
            umap = {}
            for u,a in enumerate(aidxs):
                umap[a] = u
        
        q=None
        if len(self.iat) == 2:
            from . Geometry import CptDist
            if umap is None:
                a = crds[ self.iat[0] - 1, : ]
                b = crds[ self.iat[1] - 1, : ]
            else:
                a = crds[ umap[self.iat[0] - 1], : ]
                b = crds[ umap[self.iat[1] - 1], : ]
                #x = np.sqrt( parmed.geometry.distance2(a,b) )
            q = CptDist(a,b)
        elif self.dihed:
            from . Geometry import CptDihed
            if umap is None:
                a = crds[ self.iat[0] - 1, : ]
                b = crds[ self.iat[1] - 1, : ]
                c = crds[ self.iat[2] - 1, : ]
                d = crds[ self.iat[3] - 1, : ]
            else:
                a = crds[ umap[self.iat[0] - 1], : ]
                b = crds[ umap[self.iat[1] - 1], : ]
                c = crds[ umap[self.iat[2] - 1], : ]
                d = crds[ umap[self.iat[3] - 1], : ]
            q = CptDihed(a,b,c,d)
        elif self.angle:
            from . Geometry import CptAngle
            if umap is None:
                a = crds[ self.iat[0] - 1, : ]
                b = crds[ self.iat[1] - 1, : ]
                c = crds[ self.iat[2] - 1, : ]
            else:
                a = crds[ umap[self.iat[0] - 1], : ]
                b = crds[ umap[self.iat[1] - 1], : ]
                c = crds[ umap[self.iat[2] - 1], : ]
            q = CptAngle(a,b,c)
        elif len(self.iat) == 4:
            from . Geometry import CptR12
            if umap is None:
                a = crds[ self.iat[0] - 1, : ]
                b = crds[ self.iat[1] - 1, : ]
                c = crds[ self.iat[2] - 1, : ]
                d = crds[ self.iat[3] - 1, : ]
            else:
                a = crds[ umap[self.iat[0] - 1], : ]
                b = crds[ umap[self.iat[1] - 1], : ]
                c = crds[ umap[self.iat[2] - 1], : ]
                d = crds[ umap[self.iat[3] - 1], : ]
            q = CptR12(a,b,c,d,self.rstwt)
        return q

    
    def GetTemplateKeys(self):
        """Return a list of template variable names

        Returns
        -------

        vars : list of str
            The name of each variable within the restraint file
            Returns an empty list of this is not a template definition
        """
        vs = []
        if not isinstance(self.r2,float):
            vs.append(self.r2)
        if not isinstance(self.r3,float):
            vs.append(self.r3)
        if not isinstance(self.rk2,float):
            vs.append(self.rk2)
        if not isinstance(self.rk3,float):
            vs.append(self.rk3)
        return list(set(vs))

    
    def FillTemplate(self,valdict,warn=False):
        """Return a new instance of a restraint that replaces
        template variable names with numerical values

        Parameters
        ----------
        valdict : dict (keys: str, values: float)
            The keys are the variable names and the values are the
            numerical values to be inserted

        warn : bool, default=False
            Print a warning to stderr if the template did not contain
            a named variable or if the resulting restraint object
            still contains non-numeric entries

        Returns
        -------
        res : Restraint object
        """
        import copy
        import sys
        res = copy.deepcopy(self)
        for k in valdict:
            found=False
            if res.r2 == k:
                res.r2 = valdict[k]
                found=True
            if res.r3 == k:
                res.r3 = valdict[k]
                found=True
            if res.rk2 == k:
                res.rk2 = valdict[k]
                found=True
            if res.rk3 == k:
                res.rk3 = valdict[k]
                found=True
            if warn and not found:
                sys.stderr.write("Restraint.FillTemplate could "
                                 +"not find variable %s\n"%(k))
        if res.is_template():
            sys.stderr.write("Not all variables filled in "
                             +"Restraint.FillTemplate "
                             +"%s"%(res.GetTemplateKeys()))
        return res


    def GetWilsonElements(self,crds,aidxs):
        """Return a column of the Wilson B matrix, the elements
        of which are dq/dx, where q is the restraint coordinate
        and x is a Cartesian coordinate.  The length of the output
        array is 3 * len(aidxs).

        Parameters
        ----------
        crds : numpy.array, shape=(nat,3)
            The coordinates of the system

        aidxs : list of int
            Each element is the 0-based index of the atom in
            the full system.  In contrast, crds may be a 
            petite list of coordinates, where the petite list
            is len(aidxs)
        
        Returns
        -------
        q : float
            The restraint coordinate value

        B : numpy.array, shape=3*len(aidxs)
            The values of dq/dx for this restraint        
        """
        
        import numpy as np

        q=None
        dqdx = np.zeros( (3*len(aidxs)) )
        
        umap = {}
        for u,a in enumerate(aidxs):
            umap[a] = u
        
        if len(self.iat) == 2:
            from . Geometry import CptDistAndGrd
            ia = self.iat[0] - 1
            if ia in umap:
                ia = umap[ia]
            else:
                raise Exception("Missing %i in aidxs"%(ia))
            
            ib = self.iat[1] - 1
            if ib in umap:
                ib = umap[ib]
            else:
                raise Exception("Missing %i in aidxs"%(ib))
                                
                
            q,dqda,dqdb = CptDistAndGrd(crds[ia,:],crds[ib,:])

            for k in range(3):
                dqdx[ k + ia*3 ] =  dqda[k]
                dqdx[ k + ib*3 ] += dqdb[k]
                
        elif self.dihed:
            
            #import parmed.geometry
            from . Geometry import CptDihedAndGrd

            ia = self.iat[0] - 1
            if ia in umap:
                ia = umap[ia]
            else:
                raise Exception("Missing %i in aidxs"%(ia))
            
            ib = self.iat[1] - 1
            if ib in umap:
                ib = umap[ib]
            else:
                raise Exception("Missing %i in aidxs"%(ib))
                       
            ic = self.iat[2] - 1
            if ic in umap:
                ic = umap[ic]
            else:
                raise Exception("Missing %i in aidxs"%(ic))
       
            ie = self.iat[3] - 1
            if ie in umap:
                ie = umap[ie]
            else:
                raise Exception("Missing %i in aidxs"%(ie))
            
            #q = parmed.geometry.dihedral(crds[ia,:],crds[ib,:],crds[ic,:],crds[ie,:]) #* np.pi / 180.
            #raise Exception("Dihedrals not implemented")
            
            q,dqda,dqdb,dqdc,dqde = CptDihedAndGrd(crds[ia,:],crds[ib,:],crds[ic,:],crds[ie,:])
            
            for k in range(3):
                dqdx[ k + ia*3 ]  = dqda[k]
                dqdx[ k + ib*3 ] += dqdb[k]
                dqdx[ k + ic*3 ] += dqdc[k]
                dqdx[ k + ie*3 ] += dqde[k]
        
        elif self.angle:
            from . Geometry import CptAngleAndGrd

            ia = self.iat[0] - 1
            if ia in umap:
                ia = umap[ia]
            else:
                raise Exception("Missing %i in aidxs"%(ia))
            
            ib = self.iat[1] - 1
            if ib in umap:
                ib = umap[ib]
            else:
                raise Exception("Missing %i in aidxs"%(ib))
                       
            ic = self.iat[2] - 1
            if ic in umap:
                ic = umap[ic]
            else:
                raise Exception("Missing %i in aidxs"%(ic))
       
            
            q,dqda,dqdb,dqdc = CptAngleAndGrd(crds[ia,:],crds[ib,:],crds[ic,:])
            
            for k in range(3):
                dqdx[ k + ia*3 ]  = dqda[k]
                dqdx[ k + ib*3 ] += dqdb[k]
                dqdx[ k + ic*3 ] += dqdc[k]

        elif len(self.iat) == 4:
            from . Geometry import CptR12AndGrd

            ia = self.iat[0] - 1
            if ia in umap:
                ia = umap[ia]
            else:
                raise Exception("Missing %i in aidxs"%(ia))
            
            ib = self.iat[1] - 1
            if ib in umap:
                ib = umap[ib]
            else:
                raise Exception("Missing %i in aidxs"%(ib))
                       
            ic = self.iat[2] - 1
            if ic in umap:
                ic = umap[ic]
            else:
                raise Exception("Missing %i in aidxs"%(ic))
       
            ie = self.iat[3] - 1
            if ie in umap:
                ie = umap[ie]
            else:
                raise Exception("Missing %i in aidxs"%(ie))
            
            q,dqda,dqdb,dqdc,dqde = CptR12AndGrd(self.rstwt[0],
                                                 self.rstwt[1],
                                                 crds[ia,:],crds[ib,:],
                                                 crds[ic,:],crds[ie,:])
            

            for k in range(3):
                dqdx[ k + ia*3 ]  = dqda[k]
                dqdx[ k + ib*3 ] += dqdb[k]
                dqdx[ k + ic*3 ] += dqdc[k]
                dqdx[ k + ie*3 ] += dqde[k]
        return q,dqdx
        
