#!/usr/bin/env python3

# def Orthogonalize(Xin,Ein):
#     import numpy as np
#     Xfree = np.array(Xin,copy=True)
#     Elim = np.array(Ein,copy=True)
#     for i in range(Elim.shape[1]):
#         Elim[:,i] /= np.linalg.norm(Elim[:,i])**2
#     for i in range(Xfree.shape[1]):
#         proj = np.dot(Xfree[:,i],Elim)
#         Xfree[:,i] -= np.dot(Elim,proj)
#         proj2 = np.dot(Xfree[:,i],Elim)
#         print(i,np.linalg.norm(proj),np.linalg.norm(proj2))
#     return Xfree

def AddConstraint(Cmat,Cvec):
    import numpy as np
    nm = Cmat.shape[1]
    X = SvdFillCols(Cmat)
    Xfree = X[:,nm:]
    Cproj = np.dot(Cvec,Xfree)
    Cfree = np.dot(Xfree,Cproj)
    Cmat2 = np.concatenate((Cmat,Cfree.reshape(Cfree.shape[0],1)),1)
    #print(Cmat.shape,Cmat2.shape)
    return Cmat2


def CenterOfMass(m,crds):
    import numpy as np
    return np.dot(m,crds)/np.sum(m)


def MoveCenterOfMassToOrigin(m,crds):
    #print(CenterOfMass(m,crds))
    #print(crds - CenterOfMass(m,crds))
    #print(crds)
    return crds - CenterOfMass(m,crds)

def CptInertiaTensor(m,crds):
    import numpy as np

    n = len(m)
    I = np.zeros( (3,3) )
    #print(crds.shape,n)
    #print(m)
    for i in range(n):
        I[0,0] += m[i] * ( crds[i,1]*crds[i,1] + crds[i,2]*crds[i,2] )
        I[1,1] += m[i] * ( crds[i,0]*crds[i,0] + crds[i,2]*crds[i,2] )
        I[2,2] += m[i] * ( crds[i,1]*crds[i,1] + crds[i,0]*crds[i,0] )
        I[1,0] -= m[i] * crds[i,1]*crds[i,0]
        I[2,0] -= m[i] * crds[i,2]*crds[i,0]
        I[2,1] -= m[i] * crds[i,2]*crds[i,1]
    I[0,1]=I[1,0]
    I[0,2]=I[2,0]
    I[1,2]=I[2,1]
    return I


def CptPrincipleMomentsOfInertia(m,crds):
    from numpy.linalg import eigh
    
    comcrd = MoveCenterOfMassToOrigin(m,crds)
    I = CptInertiaTensor(m,comcrd)
    moments_of_intertia,principle_moment_vectors = eigh(I)
    return moments_of_intertia,principle_moment_vectors


def CptRotationalInfo(m,crds):
    moments,vectors = CptPrincipleMomentsOfInertia(m,crds)
    numRotModes = 0
    for k in range(3):
        if abs(moments[k]) > 1.e-6:
            numRotModes += 1
    return numRotModes,moments




def GaussianMass(z):
    data = { 1: 1.0078250,
             6: 12.0,
             7: 14.0030740,
             8: 15.9949146,
             15: 30.9737634 }
    return data[z]


def CorrectMass(M):
    import numpy as np
    from .. constants import AU_PER_ATOMIC_MASS_UNIT
    MASS_TOL = 0.1 * AU_PER_ATOMIC_MASS_UNIT()
    o = np.array(M,copy=True)
    for i in range(len(o)):
        if o[i] < MASS_TOL:
            o[i] = 0
    return o




def TranslationConstraints(Min):
    #
    # The center of mass in each direction is conserved.
    # q(r) = Rc = \sum_a ma * ra
    #
    # sa = sqma * ra
    # 
    # ra = sa/sqma
    #
    # so,
    #
    # q(s) = \sum_a ma * ( sa/sqma )
    #      = \sum_a sqma * sa
    #
    # dq/dsa = sqma 
    #
    #
    import numpy as np
    M = np.sqrt(CorrectMass(Min))
    nat = len(M)
    n = 3*nat
    C = np.zeros( (n,3) )
    for i in range(nat):
        for k in range(3):
            C[k+i*3,k] = M[i]
    return C


def RotationalConstraints(Min,Crd):
    #
    # This preserves the moments of inertia. The moments
    # are expressed in terms of mass-scaled coordinates, s,
    # and the columns are the derivatives dq/ds
    # 
    import numpy as np
    
    M = CorrectMass(Min)
    nat = len(M)
    n = 3*nat

    if Crd.shape[0] != nat:
        raise Exception(f"Crd nat {Crd.shape[0]} != {nat}")
    if Crd.shape[1] != 3:
        raise Exception(f"Crd size {Crd.shape[1]} != 3")

    com = np.dot( M,Crd ) / np.sum(M)
    ComCrd = Crd - com
        
    I = np.zeros( (3,3) )
    for i in range(nat):
        I[0,0] += M[i]*(ComCrd[i,1]*ComCrd[i,1] + ComCrd[i,2]*ComCrd[i,2])
        I[0,1] -= M[i]*ComCrd[i,0]*ComCrd[i,1]
        I[1,1] += M[i]*(ComCrd[i,0]*ComCrd[i,0] + ComCrd[i,2]*ComCrd[i,2])
        I[0,2] -= M[i]*ComCrd[i,0]*ComCrd[i,2]
        I[1,2] -= M[i]*ComCrd[i,1]*ComCrd[i,2]
        I[2,2] += M[i]*(ComCrd[i,1]*ComCrd[i,1] + ComCrd[i,0]*ComCrd[i,0])
    I[1,0] = I[0,1]
    I[2,0] = I[0,2]
    I[2,1] = I[1,2]

    E, U = np.linalg.eigh( I )
    idx = E.argsort()
    E = E[idx]
    U = U[:,idx]
    E[0],E[2] = E[2],E[0]
    t = np.array(U[:,0],copy=True)
    U[:,0] = U[:,2]
    U[:,2] = t


    PmiCrd = np.dot(ComCrd,U)
    
    C = np.zeros( (n,3) )
    for i in range(nat):
        mi = np.sqrt(M[i])
        for k in range(3):
            C[k+i*3,0] = mi*(PmiCrd[i,1]*U[k,2] - PmiCrd[i,2]*U[k,1])
            C[k+i*3,1] = mi*(PmiCrd[i,2]*U[k,0] - PmiCrd[i,0]*U[k,2])
            C[k+i*3,2] = mi*(PmiCrd[i,0]*U[k,1] - PmiCrd[i,1]*U[k,0])
    nmodes = 0
    for i in range(3):
        if abs(E[i]) > 1.e-6:
            nmodes += 1
    return C[:,:nmodes]



def BondConstraints(Min,crd,bondpairs):
    #
    # This preserves bond lengths. The bond length is expressed
    # in terms of mass-scaled coordinates, s, and the columns are
    # the derivatives dq/ds
    #
    # q(r) = |ri-rj|
    #
    # si = sqmi * ri
    #
    # ri = si/sqmi
    #
    # q(s) = | si/sqmi - sj/sqmj |
    #
    # dq/dsi = (1/sqmi) * (si/sqmi - sj/sqmj)/| si/sqmi - sj/sqmj |
    #        = (1/sqmi) * (ri-rj)/|ri-rj|
    #
    import numpy as np
    nbond = len(bondpairs)//2
    M = CorrectMass(Min)
    nat = M.shape[0]
    C = np.zeros( (3*nat,nbond) )
    for ib in range(nbond):
        i = bondpairs[0+ib*2]-1
        j = bondpairs[1+ib*2]-1
        mi = np.sqrt(M[i]) # sqmi
        mj = np.sqrt(M[j]) # sqmj
        rij = crd[i,:]-crd[j,:]
        nrm = np.linalg.norm(rij)
        uij = rij/nrm
        for k in range(3):
            C[k+i*3,ib] =  uij[k] / ( mi )
            C[k+j*3,ib] = -uij[k] / ( mj )
            
    return C



def ExtraConstraints(Min,crd,conmat):
    import numpy as np
    from .. amber.Geometry import CptDistAndGrd
    from .. amber.Geometry import CptAngleAndGrd
    from .. amber.Geometry import CptDihedAndGrd
    
    #print("conmat.shape=",conmat.shape)
    
    ncon = conmat.shape[0]
    M = CorrectMass(Min)
    nat = M.shape[0]
    C = np.zeros( (3*nat,ncon) )
    for icon in range(ncon):
        if conmat[icon,0] == 1:
            i = conmat[icon,1]-1
            j = conmat[icon,2]-1
            mi = np.sqrt(M[i]) # sqmi
            mj = np.sqrt(M[j]) # sqmj
            q,di,dj = CptDistAndGrd(crd[i,:],crd[j,:])
            C[i*3:i*3+3,icon] += di/mi
            C[j*3:j*3+3,icon] += dj/mj
        elif conmat[icon,0] == 2:
            i = conmat[icon,1]-1
            j = conmat[icon,2]-1
            k = conmat[icon,3]-1
            mi = np.sqrt(M[i]) # sqmi
            mj = np.sqrt(M[j]) # sqmj
            mk = np.sqrt(M[k]) # sqmk
            q,di,dj,dk = CptAngleAndGrd(crd[i,:],crd[j,:],crd[k,:])
            C[i*3:i*3+3,icon] += di/mi
            C[j*3:j*3+3,icon] += dj/mj
            C[k*3:k*3+3,icon] += dk/mk
        elif conmat[icon,0] == 3:
            i = conmat[icon,1]-1
            j = conmat[icon,2]-1
            k = conmat[icon,3]-1
            l = conmat[icon,4]-1
            mi = np.sqrt(M[i]) # sqmi
            mj = np.sqrt(M[j]) # sqmj
            mk = np.sqrt(M[k]) # sqmk
            ml = np.sqrt(M[l]) # sqml
            q,di,dj,dk,dl = CptDihedAndGrd(crd[i,:],crd[j,:],crd[k,:],crd[l,:])
            C[i*3:i*3+3,icon] += di/mi
            C[j*3:j*3+3,icon] += dj/mj
            C[k*3:k*3+3,icon] += dk/mk
            C[k*3:k*3+3,icon] += dl/ml
        else:
            raise Exception(f"Invalid constraint type: {conmat[icon,:]}")
            
    return C



def NaturalConstraints(Min,Crd,norm=True):
    import numpy as np
    TrnVec = TranslationConstraints(Min)
    RotVec = RotationalConstraints(Min,Crd)
    ntrn = TrnVec.shape[1]
    nrot = RotVec.shape[1]
    nfix = ntrn+nrot
    X = np.zeros( (TrnVec.shape[0],nfix) )
    X[:,:ntrn] = TrnVec
    X[:,ntrn:] = RotVec
    if norm:
        for i in range(nfix):
            X[:,i] /= np.linalg.norm( X[:,i] )
    return X


def SvdFillCols(M):
    import numpy as np
    n = M.shape[0]
    nm = M.shape[1]
    X = np.zeros( (n,n) )
    X[:,:nm] = M[:,:nm]
    U,w,VT = np.linalg.svd(X)
    SVD_TOL = 1.e-10
    ic = 0
    for i in range(n):
        if w[i] < SVD_TOL:
            X[:,ic+nm] = U[:,i]
            ic += 1
    return X


def InternalCrdTransformationMatrix(Min,ConVec):
    import numpy as np
    
    M = CorrectMass(Min)
    nat = len(M)
    n = 3*nat
    nfix = ConVec.shape[1]
    NumVibModes = n-nfix
    
    X = np.zeros( (n,n) )
    X[:,:nfix] = ConVec
    for i in range(nfix):
        X[:,i] /= np.linalg.norm(X[:,i])

    U,w,VT = np.linalg.svd(X)
    #w = np.diag(w)
    X = np.zeros( (n,NumVibModes) )
    SVD_TOL = 1.e-10
    ic = 0
    for i in range(n):
        if w[i] < SVD_TOL:
            X[:,ic] = U[:,i]
            ic += 1
    return X


def FullInternalCrdTransformationMatrix(Min,ConVec):
    import numpy as np
    
    M = CorrectMass(Min)
    nat = len(M)
    n = 3*nat
    nfix = ConVec.shape[1]
    NumVibModes = n-nfix
    
    X = np.zeros( (n,n) )
    X[:,:nfix] = ConVec
    for i in range(nfix):
        X[:,i] /= np.linalg.norm(X[:,i])

    U,w,VT = np.linalg.svd(X)
    #w = np.diag(w)
    #X = np.zeros( (n,NumVibModes) )
    SVD_TOL = 1.e-10
    ic = 0
    for i in range(n):
        if w[i] < SVD_TOL:
            X[:,nfix+ic] = U[:,i]
            ic += 1
    return X


def GetMmat(Min):
    M = CorrectMass(Min)
    nat = len(M)
    n = 3*nat
    mmat = np.zeros( (n,n) )
    for i in range(nat):
        for k in range(3):
            mmat[k+i*3,k+i*3] = M[i]
    return mmat

            
def FreqSolver(Min,X,H):
    import numpy as np
    
    M = CorrectMass(Min)
    nat = len(M)
    n = 3*nat
    nm = X.shape[1]
    
    X_over_sqrt_M = np.array(X,copy=True)
    for i in range(nat):
        oo_sqrt_m = 0.
        if M[i] > 1.e-40:
            oo_sqrt_m = 1. / np.sqrt(M[i])
        for im in range(nm):
            for k in range(3):
                X_over_sqrt_M[k+i*3,im] *= oo_sqrt_m

    T = np.dot(H,X_over_sqrt_M)
    IQH = np.dot(X_over_sqrt_M.T,T)
    freqs, U = np.linalg.eigh(IQH)
    idxs = freqs.argsort()
    freqs = freqs[idxs]
    U = U[:,idxs]
    for i in range(nm):
        if freqs[i] < 0:
            freqs[i] = -np.sqrt(-freqs[i])
        else:
            freqs[i] = np.sqrt(freqs[i])

    dispmat = np.dot( X_over_sqrt_M, U )
    redmass = np.array( [ 1./np.linalg.norm(dispmat[:,im])**2
                          for im in range(nm) ] )
    
    return freqs,redmass,dispmat


def AltFreqSolver(Min,X,H,approx=True):
    import numpy as np
    import scipy.linalg
    
    M = CorrectMass(Min)
    nat = len(M)
    n = 3*nat
    nm = X.shape[1]

    Mmat = np.zeros( (n) )
    for i in range(nat):
        for k in range(3):
            Mmat[k+i*3] = M[i]
            
    if True:
        #
        # GOOD
        #
        ngen = X.shape[1]
        if approx:
            Z = np.array(X,copy=True)
        else:
            Z = SvdFillCols(X)
            
        ZMZ = np.dot( Z.T, np.dot( np.diag(Mmat), Z ) )
        vvals,vvecs = np.linalg.eigh( ZMZ )
        vvals_mhalf = np.where( vvals > 1.e-12, 1./np.sqrt(vvals), 0 )
        ZMZ_mhalf = np.dot( vvecs, np.dot( np.diag(vvals_mhalf), vvecs.T ) )

        #print(np.allclose(np.dot(X,X.T),np.identity(X.shape[0])))
        #print(np.allclose(np.dot(X.T,X),np.identity(X.shape[1])))
        #print(np.allclose(np.linalg.pinv(X),X.T))
        #print(np.allclose(np.linalg.pinv(X.T),X))
        #XMX = np.dot( X.T, np.dot( np.diag(Mmat), X ) )
        #vvals,vvecs = np.linalg.eigh( XMX )
        #vvals_mhalf = np.where( vvals > 1.e-12, 1./np.sqrt(vvals), 0 )
        #XMX_mhalf = np.dot( vvecs, np.dot( np.diag(vvals_mhalf), vvecs.T ) )
        #V_mhalf = 0.5*(ZMZ_mhalf[:ngen,:ngen] + XMX_mhalf)
        
        ZVred = np.dot(Z,ZMZ_mhalf[:,:ngen])
        redIQH = np.dot(ZVred.T, np.dot(H,ZVred))
        freqs, U = np.linalg.eigh(redIQH)

        # sort the eigenvalues
        idxs = freqs.argsort()
        freqs = freqs[idxs]
        U = U[:,idxs]

        # convert to frequencies
        for i in range(ngen):
            if freqs[i] < 0:
                freqs[i] = -np.sqrt(-freqs[i])
            else:
                freqs[i] = np.sqrt(freqs[i])
                
        # calculate displacements and reduced masses
        dispmat = np.dot( ZVred, U )
        redmass = np.array( [ 1./np.linalg.norm(dispmat[:,im])**2
                              for im in range(ngen) ] )

    return freqs,redmass,dispmat




class Vibrator(object):


    @classmethod
    def from_file(cls,fname,isosub,idxfromparm,save=True):
        from .. gaussian import GaussianOutput
        try:
            gau = GaussianOutput(fname)
            arc = gau.FirstStepWithHessian()
            return cls.from_gaussian_archive(arc,isosub)
        except:
            return cls.from_netcdf(fname,isosub,idxfromparm,save=save)
    
    @classmethod
    def from_gaussian_archive(cls,arc,isosub,solve=True):
        from .. constants import GetAtomicNumber
        from .. constants import AU_PER_ANGSTROM
        
        isosub = [ i for i in isosub ]
        ele = arc.GetElements()
        atnums = [ GetAtomicNumber(e) for e in ele ]
        crd = arc.GetCrd() * AU_PER_ANGSTROM()
        hess = arc.GetHessian()

        for i in range(len(isosub)):
            nat = len(atnums)
            if isosub[i] < 1 or isosub[i] > nat:
                raise Exception(f"Invalid isosub index {idx} (range: 1,{nat})")
            else:
                isosub[i] -= 1
        
        return cls(atnums,crd,hess,isosub,
                   solve=solve,
                   symnum=arc.GetSymNum(),
                   multiplicity=arc.GetMultiplicity(),
                   E=arc.GetHF() )

    @classmethod
    def from_netcdf(cls,fname,isosub,idxfromparm,save=True):
        from netCDF4 import Dataset
        import numpy as np
        import sys
        
        
        src = Dataset(fname,"r",format="NETCDF3_64BIT_OFFSET")
        atnum = np.array(src.variables["atnums"][:],dtype=int,copy=True)
        crds = np.array(src.variables["coordinates"][:,:],copy=True)
        nat = crds.shape[0]
        nhess = 3*nat

        isosub = [ i for i in isosub ]
        if len(isosub) > 0:
            if idxfromparm:
                atidxs = np.array(src.variables["atidxs"][:],dtype=int,copy=True)
                myiso = []
                for idx in isosub:
                    if idx in atidxs:
                        myiso.append( np.where( atidxs == idx )[0][0] )
                        #print(myiso)
                    else:
                        raise Exception(f"Could not find atom index {idx} in {atidxs}")
                isosub = myiso
            else:
                myiso = []
                for idx in isosub:
                    cidx = idx-1
                    if cidx >= 0 and cidx < nat:
                        myiso.append(cidx)
                    else:
                        raise Exception(f"Invalid isosub index {idx} (range: 1,{nat})")
                isosub = myiso
            isosub.sort()

        
        #ncol = src.dimensions["hesscols"].size
        #if ncol != nhess:
        #    raise Exception(f"Expected {nhess} columns in {fname}; found {ncol}")
        ncol = int(src.variables["nsavedcols"][0])
        
        niso = src.dimensions["niso"].size
        match = None
        if niso > 0:
            keys = [ i+1 for i in range(nat) ]
            for iiso in range(niso):
                mask = src.variables["isomask"][iiso,:nat]
                myiso = [ key-1 for key,val in zip(keys,mask)
                          if val == 1 ]
                myiso.sort()
                if np.array_equal(isosub,myiso):
                    match = iiso
                    break

        if not save:
            match = None
                
        H = np.zeros( (nhess,nhess) )
        hascol = [False]*nhess
        colidxs = np.array(src.variables["colidx"][:ncol],dtype=int,copy=True)
        for i,idx in enumerate(colidxs):
            cidx = idx-1
            hascol[cidx]=True
            H[cidx,:] = src.variables["colvals"][i,:]

                
        missing = []
        for i,x in enumerate(hascol):
            if not x:
                missing.append(i+1)
        if len(missing) > 0:
            raise Exception(f"Missing Hessian columns: {missing}")



        abserrs=[]
        relerrs=[]
        ijs=[]
        for i in range(H.shape[0]):
            for j in range(i+1):
                a = H[i,j]
                b = H[j,i]
                c = 0.5*(a+b)
                #H[i,j] = H[j,i] = c
                abserrs.append(a-b)
                relerrs.append(abs(a-b)/abs(c))
                ijs.append( (i,j) )

        argmax = np.argmax(abserrs)
        i,j = ijs[argmax]
        sys.stderr.write("Max  Abs Err %12.3e %5i %5i %12.3e %12.3e\n"%(abserrs[argmax],i,j,H[i,j],H[j,i]))
        sys.stderr.write("Mean Abs Err %12.3e\n"%(np.mean(abserrs)))

        argmax = np.argmax(relerrs)
        i,j = ijs[argmax]
        sys.stderr.write("Max  Rel Err %12.3e %5i %5i %12.3e %12.3e\n"%(relerrs[argmax],i,j,H[i,j],H[j,i]))
        sys.stderr.write("Mean Rel Err %12.3e\n"%(np.mean(relerrs)))

        
        H = 0.5*(H + H.T)

        conmat=None
        if "ncon" in src.dimensions:
            ncon = src.dimensions["ncon"].size
            conmat = np.zeros( (ncon,5), dtype=int )
            #print("conmat shape = ",src.variables["conmat"].shape)
            conmat[:,:] = src.variables["conmat"][:,:]

        
        res = cls(atnum,crds,H,isosub,solve=(match is None),
                  conmat=conmat)

        if match is not None:
            # overwrite mass
            res.mass = np.array(src.variables["atmass"][match,:],copy=True)
            nvib = src.variables["nvib"][match]
            res.freqs = np.array(src.variables["freqs"][match,:nvib],copy=True)
            res.X = np.array(src.variables["xmat"][match,:,:nvib],copy=True)
            res.redmass = np.array(src.variables["redmass"][match,:nvib],copy=True)
            res.dispmat = np.array(src.variables["dispmat"][match,:,:nvib],copy=True)
        src.close()

        if match is None and save:
            dst = Dataset(fname,"a",format="NETCDF3_64BIT_OFFSET")
            isomask = [0]*nat
            for i in isosub:
                isomask[i]=1
            nvib = res.freqs.shape[0]
            dst.variables["atmass"][niso,:nat] = res.mass[:nat]
            dst.variables["nvib"][niso] = nvib
            dst.variables["isomask"][niso,:] = isomask
            dst.variables["freqs"][niso,:nvib] = res.freqs
            dst.variables["xmat"][niso,:,:nvib] = res.X
            dst.variables["redmass"][niso,:nvib] = res.redmass
            dst.variables["dispmat"][niso,:,:nvib] = res.dispmat
            dst.close()
        return res
                
    
    def __init__(self,atnum,crd,hess,isosub,
                 solve=True,symnum=1,multiplicity=1,E=0,
                 conmat=None):
        import numpy as np
        import copy
        from .. constants import GetStdIsotopeMass, GetSecondIsotopeMass
        from .. constants import AU_PER_ATOMIC_MASS_UNIT

        self.E = E
        self.multiplicity = multiplicity
        self.symnum = symnum
        if len(isosub) > 0:
            self.symnum = 1
            
        self.atnum = atnum
        self.crd = np.array(crd,copy=True)
        self.hess = np.array(hess,copy=True)
        self.isosub = [ i for i in isosub ]
        self.mass = np.array( [ GetStdIsotopeMass(z) for z in self.atnum ] )
        #self.mass = np.array( [ GaussianMass(z) for z in self.atnum ] )
        if self.isosub is not None:
            for i in self.isosub:
                self.mass[i] = GetSecondIsotopeMass(self.atnum[i])
        self.mass *= AU_PER_ATOMIC_MASS_UNIT()
        self.conmat = copy.deepcopy(conmat)
        
        if solve:
            #print(len(self.atnum))
            #print(self.crd.shape)
            #print(self.hess.shape)
            #print(self.mass.shape)
            self.Solve(conmat=conmat)

            
    def GetIsosubElements(self):
        from .. constants import GetAtomicSymbol
        return [ GetAtomicSymbol(self.atnum[i]) for i in self.isosub ]
            
            
    def ExtractAtomSubset(self,atoms):
        import numpy as np
        if self.conmat is not None:
            raise Exception("Currently cannot call ExtractAtomSubset when"+
                            " constrained coordinates have been specified (TODO)")
        icrds = [ j+i*3 for i in atoms for j in range(3) ]
        isosub = None
        if self.isosub is not None:
            isosub=[]
            for a in self.isosub:
                if a in atoms:
                    isosub.append( atoms.index(a) )
        
        return Vibrator( [self.atnum[a] for a in atoms],
                         self.crd[atoms,:],
                         self.hess[np.array(icrds)[:,np.newaxis],
                                   np.array(icrds)[np.newaxis,:]],
                         isosub, solve=True )

    def Solve(self,conmat=None):
        import numpy as np
        MWCon = NaturalConstraints(self.mass,self.crd)

        
        if conmat is not None:
            ncon = conmat.shape[0]
            CMat = np.array(MWCon,copy=True)
            sqM = np.sqrt(CorrectMass(self.mass))
            BondCs = ExtraConstraints(self.mass,self.crd,conmat)
            CMat = np.concatenate( (CMat,BondCs) , axis=1 )
            #
            # We can either multiply my sqrt(mass) before calling
            # InternalCrdTransformationMatrix, ... or ...
            #
            for a in range(len(sqM)):
                for k in range(3):
                    CMat[k+a*3,:] *= sqM[a]
            self.X = InternalCrdTransformationMatrix(self.mass,CMat)
            #
            # ... or ... we can divide X by 1/sqrt(mass)
            #
            #for a in range(len(sqM)):
            #    for k in range(3):
            #        self.X[k+a*3,:] /= sqM[a]
            #
            # ... Both yield the same result. We divide X by 1/sqrt(mass)
            # because the mass weighting is explicitly treated in the
            # GenCrdSolve routine, whereas the FreqSolver routine
            # assumes X is mass-weighted.
            
            self.GenCrdSolve(self.X,approx=True)
            
        else:
            self.X = InternalCrdTransformationMatrix(self.mass,MWCon)
            self.freqs,self.redmass,self.dispmat = \
                FreqSolver(self.mass,self.X,self.hess)

        
    def GenCrdSolve(self,X,approx=True):
        self.X = X
        self.freqs,self.redmass,self.dispmat = \
            AltFreqSolver(self.mass,self.X,self.hess,approx=approx)

        
    def GetMassMatrix3N(self):
        import numpy as np
        n = len(self.mass)
        n3 = 3*n
        m = CorrectMass(self.mass)
        o = np.zeros( (n3,n3) )
        for i in range(n):
            for j in range(3):
                o[j+i*3,j+i*3] = m[i]
        return o

    
    def GetReducedMasses_AU(self):
        import numpy as np
        return np.array(self.redmass,copy=True)

    
    def GetReducedMasses_AMU(self):
        from .. constants import AU_PER_ATOMIC_MASS_UNIT
        return self.redmass / AU_PER_ATOMIC_MASS_UNIT()

    
    def GetForceConsts_AU(self):
        x = self.redmass * self.freqs * self.freqs
        for i in range(self.freqs.shape[0]):
            if self.freqs[i] < 0:
                x[i] *= -1
        return x

    
    def GetForceConsts_mDynePerAng(self):
        from .. constants import AU_PER_DYNE_PER_CM
        AU_PER_MDYNE_PER_ANGSTROM = AU_PER_DYNE_PER_CM() * 1.e+5
        return self.GetForceConsts_AU() / AU_PER_MDYNE_PER_ANGSTROM


    def GetNumModes(self):
        return self.freqs.shape[0]
    
    def GetFreqs_AU(self):
        import numpy as np
        return np.array(self.freqs,copy=True)

    
    def GetFreqs_InvCM(self):
        from .. constants import AU_PER_INVERSE_CM
        return self.freqs / AU_PER_INVERSE_CM()

    
    def GetNormalizedDisplacementVector_AU(self,imode):
        import numpy as np
        c = np.array(self.dispmat[:,imode],copy=True)
        c /= np.linalg.norm(c)
        return c.reshape( (len(self.mass),3) )

    
    def GetScaledDisplacedCrds_AU(self,imode,delta):
        return self.crd + delta * self.GetNormalizedDisplacementVector_AU(imode)

    
    def GetScaledDisplacedCrds_Ang(self,imode,delta):
        from .. constants import AU_PER_ANGSTROM
        return self.GetScaledDisplacedCrds_AU(imode,delta) / AU_PER_ANGSTROM()


    def GetElectronicEnergy_AU(self):
        return self.E

    
    def GetZeroPointEnergy_AU(self):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        #from .. constants import FOUR_PI
        
        h = PLANCK_CONSTANT_AU()
        #pi4 = FOUR_PI()
        pi4 = np.pi * 4

        ZPE = 0.
        for F in self.freqs:
            if F > 0:
                ZPE += h * F / pi4
        return ZPE

    
    def GetVibrationalPartitionFunctionFromBottom_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU
        #from .. constants import PI

        h  = PLANCK_CONSTANT_AU();
        k  = BOLTZMANN_CONSTANT_AU();
        PI = np.pi;

        qbot = 1.
        for F in self.freqs:
            if F < 0.:
                continue
            Tvib = h * F / k / (2.*PI)
            emT = 0.
            TvibT = 0.
            if T > 0.:
                TvibT = Tvib / T
                emT = np.exp(-TvibT)
            if emT > 0.:
                qbot *= np.sqrt(emT)/(1.-emT)
            else:
                qbot /= (1.-emT)
        return qbot

    
    def GetVibrationalPartitionFunctionFromV0_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU
        
        h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        PI = np.pi

        q = 1.
        for F in self.freqs:
            if F < 0.:
                continue
            Tvib = h * F / k / (2.*PI)
            emT = 0.
            TvibT = 0.
            if T > 0.:
                TvibT = Tvib/T
                emT = np.exp(-TvibT)
            q /= (1.-emT)
        return q


    def GetVibrationalEntropy_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU

        h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        PI = np.pi

        S = 0.
        for F in self.freqs:
            if F < 0.:
                continue
            Tvib = h * F / k / (2.*PI)
            emT = 0.
            TvibT = 0.
            if T > 0.:
                TvibT = Tvib/T
                emT = np.exp(-TvibT)
            if emT > 0.:
                eT = 1./emT
                S += TvibT/(eT-1.) - np.log(1.-emT)
        return S*k

    
    def GetVibrationalInternalThermalEnergy_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU

        h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        PI = np.pi

        E = 0.
        for F in self.freqs:
            if F < 0:
                continue
            Tvib = h * F / k / (2.*PI)
            emT = 0.
            TvibT = 0.
            if T > 0.:
                TvibT = Tvib/T
                emT = np.exp(-TvibT)
            if emT > 0.:
                E += Tvib * (0.5 + emT/(1.-emT))
            else:
                E += Tvib/2.
        return E*k


    
    def GetVibrationalHeatCapacity_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU

        h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        PI = np.pi

        C = 0.
        for F in self.freqs:
            if F < 0:
                continue
            Tvib = h * F / k / (2.*PI)
            emT = 0.
            TvibT = 0.
            if T > 0.:
                TvibT = Tvib/T
                emT = np.exp(-TvibT)
            if emT > 0.:
                x = (TvibT/(1.-emT))
                C += emT * x * x

        return C*k


    def GetTranslationalPartitionFunction_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU
        from .. constants import AU_PER_ATMOSPHERE
        
        h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        PI = np.pi
        P = 1. * AU_PER_ATMOSPHERE()
        kT = k*T
        m = sum(self.mass)
        q = pow(2.*PI*m*kT/(h*h), 1.5 ) * kT/P
        return q

    
    def GetTranslationalEntropy_AU(self, T):
        import numpy as np
        from .. constants import BOLTZMANN_CONSTANT_AU
        
        k  = BOLTZMANN_CONSTANT_AU()
        q = self.GetTranslationalPartitionFunction_AU(T)
        S = 0.
        if q > 0.:
            S = k * ( np.log(q) + 2.5 )
        return S

    
    def GetTranslationalInternalThermalEnergy_AU(self, T):
        from .. constants import BOLTZMANN_CONSTANT_AU
        k  = BOLTZMANN_CONSTANT_AU()
        kT = k*T
        q = self.GetTranslationalPartitionFunction_AU(T)
        E = 0.
        if q > 0:
            E = 1.5 * kT
        return E

    
    def GetTranslationalHeatCapacity_AU(self):
        from .. constants import BOLTZMANN_CONSTANT_AU
        return 1.5 * BOLTZMANN_CONSTANT_AU()


    def GetElectronicPartitionFunction_AU(self):
        return self.multiplicity


    def GetElectronicEntropy_AU(self):
        import numpy as np
        from .. constants import BOLTZMANN_CONSTANT_AU

        q = self.GetElectronicPartitionFunction_AU()
        return BOLTZMANN_CONSTANT_AU() * np.log( q )


    def GetElectronicInternalThermalEnergy_AU(self):
        return 0

    
    def GetElectronicHeatCapacity_AU(self):
        return 0


    def GetRotationalPartitionFunction_AU(self, T):
        import numpy as np
        from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU

        if self.symnum < 1:
            raise Exception(f"Symmetry number must be >= 1, received {self.symnum}")
        
        h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        PI = np.pi

        pref = h*h/(8.*PI*PI*k)

        nat = len(self.atnum)
        if nat == 1:
            q = 1.
        else:
            numRotModes, moments = CptRotationalInfo(self.mass,self.crd)
            if numRotModes < 3:
                theta = pref / moments[1]
                q = (T/theta)/self.symnum
            else:
                theta = pref / moments
                q = np.sqrt( PI*T*T*T/(theta[0]*theta[1]*theta[2]) ) / self.symnum
        return q


    
    def GetRotationalEntropy_AU(self, T):
        import numpy as np
        #from .. constants import PLANCK_CONSTANT_AU
        from .. constants import BOLTZMANN_CONSTANT_AU

        if self.symnum < 1:
            raise Exception(f"Symmetry number must be >= 1, received {self.symnum}")
        
        #h  = PLANCK_CONSTANT_AU()
        k  = BOLTZMANN_CONSTANT_AU()
        #PI = np.pi

        #pref = h*h/(8.*PI*PI*k)

        nat = len(self.atnum)
        if nat == 1:
            S = 0.
        else:
            numRotModes, moments = CptRotationalInfo(self.mass,self.crd)
            q = self.GetRotationalPartitionFunction_AU(T)
            
            if numRotModes < 3:
                if q > 0:
                    S = k*( np.log(q) + 1 )
                else:
                    S = k
            else:
                if q > 0.:
                    S = k*( np.log(q) + 1.5 )
                else:
                    S = 1.5 * k
        return S




    def GetRotationalInternalThermalEnergy_AU(self, T):
        import numpy as np
        from .. constants import BOLTZMANN_CONSTANT_AU

        k  = BOLTZMANN_CONSTANT_AU()
        kT = k*T

        nat = len(self.atnum)
        if nat == 1:
            E = 0.
        else:
            numRotModes, moments = CptRotationalInfo(self.mass,self.crd)
            q = self.GetRotationalPartitionFunction_AU(T)
            
            if numRotModes < 3:
                E = kT
            else:
                E = 1.5*kT
        return E



    def GetRotationalHeatCapacity_AU(self):
        import numpy as np
        from .. constants import BOLTZMANN_CONSTANT_AU

        k  = BOLTZMANN_CONSTANT_AU()

        nat = len(self.atnum)
        if nat == 1:
            C = 0.
        else:
            numRotModes, moments = CptRotationalInfo(self.mass,self.crd)
            q = self.GetRotationalPartitionFunction_AU(T)
            
            if numRotModes < 3:
                C = k
            else:
                C = 1.5 * k
        return C


    def GetThermalCorrectionToEnergy_AU(self,T):
        Evib = self.GetVibrationalInternalThermalEnergy_AU(T)
        Erot = self.GetRotationalInternalThermalEnergy_AU(T)
        Etrn = self.GetTranslationalInternalThermalEnergy_AU(T)
        Eele = self.GetElectronicInternalThermalEnergy_AU()
        return Evib+Erot+Etrn+Eele


    def GetThermalCorrectionToEnthalpy_AU(self,T):
        from .. constants import BOLTZMANN_CONSTANT_AU
        k = BOLTZMANN_CONSTANT_AU()
        Ecorr = self.GetThermalCorrectionToEnergy_AU(T)
        return Ecorr + k*T

    
    def GetThermalCorrectionToGibbsFreeEnergy_AU(self,T):
        Hcorr = self.GetThermalCorrectionToEnthalpy_AU(T)
        S = self.GetEntropy_AU(T)
        return Hcorr - T*S

    
    def GetEntropy_AU(self,T):
        Svib = self.GetVibrationalEntropy_AU(T)
        Srot = self.GetRotationalEntropy_AU(T)
        Strn = self.GetTranslationalEntropy_AU(T)
        Sele = self.GetElectronicEntropy_AU()
        return Svib+Srot+Strn+Sele;



    def GetHeatCapacity_AU(self,T):
        Cvib = self.GetVibrationalHeatCapacity_AU(T);
        Crot = self.GetRotationalHeatCapacity_AU();
        Ctrn = self.GetTranslationalHeatCapacity_AU();
        Cele = self.GetElectronicHeatCapacity_AU();
        return Cvib+Crot+Ctrn+Cele;


    def GetPartitionFunctionFromBottom_AU(self,T):
        Qvib = self.GetVibrationalPartitionFunctionFromBottom_AU(T);
        Qrot = self.GetRotationalPartitionFunction_AU(T);
        Qtrn = self.GetTranslationalPartitionFunction_AU(T);
        Qele = self.GetElectronicPartitionFunction_AU();
        return Qvib*Qrot*Qtrn*Qele


    def GetPartitionFunctionFromV0_AU(self,T):
        Qvib = self.GetVibrationalPartitionFunctionFromV0_AU(T);
        Qrot = self.GetRotationalPartitionFunction_AU(T);
        Qtrn = self.GetTranslationalPartitionFunction_AU(T);
        Qele = self.GetElectronicPartitionFunction_AU();
        return Qvib*Qrot*Qtrn*Qele;

    
    def GetSumOfElectronicAndZeroPointEnergy_AU(self):
        return self.GetElectronicEnergy_AU() + self.GetZeroPointEnergy_AU();

    
    def GetSumOfElectronicAndThermalEnergy_AU(self,T):
        return self.GetElectronicEnergy_AU() + self.GetThermalCorrectionToEnergy_AU(T);

    
    def GetSumOfElectronicAndThermalEnthalpy_AU(self,T):
        return self.GetElectronicEnergy_AU() + self.GetThermalCorrectionToEnthalpy_AU(T);

    
    def GetSumOfElectronicAndThermalFreeEnergy_AU(self,T):
        return self.GetElectronicEnergy_AU() + self.GetThermalCorrectionToGibbsFreeEnergy_AU(T);

    
    def PrintThermochemistryReport(self,fh,T):

        fh.write("Thermochemistry (au)\n")
        fh.write("Temperature (K) = %12.5f\n"%(T))
        fh.write("Presure   (atm) = %12.5f\n"%( 1. ))
 
        fh.write("Adiabatic electronic energy                =%15.8f\n"%( self.GetElectronicEnergy_AU() ))
        fh.write("Zero-point correction                      =%15.8f\n"%( self.GetZeroPointEnergy_AU() ))
        fh.write("Thermal correction to Energy               =%15.8f\n"%( self.GetThermalCorrectionToEnergy_AU(T) ))
        fh.write("Thermal correction to Enthalpy             =%15.8f\n"%( self.GetThermalCorrectionToEnthalpy_AU(T) ))
        fh.write("Thermal correction to Gibbs Free Energy    =%15.8f\n"%( self.GetThermalCorrectionToGibbsFreeEnergy_AU(T) ))
        fh.write("Sum of electronic and zero-point Energies  =%15.8f\n"%( self.GetSumOfElectronicAndZeroPointEnergy_AU() ))
        fh.write("Sum of electronic and thermal Energies     =%15.8f\n"%( self.GetSumOfElectronicAndThermalEnergy_AU(T) ))
        fh.write("Sum of electronic and thermal Enthalpies   =%15.8f\n"%( self.GetSumOfElectronicAndThermalEnthalpy_AU(T) ))
        fh.write("Sum of electronic and thermal Free Energies=%15.8f\n"%( self.GetSumOfElectronicAndThermalFreeEnergy_AU(T) ))
        
        
        fh.write("Vibrational partition function (V=0)       =%15.6e\n"%( self.GetVibrationalPartitionFunctionFromV0_AU(T) ))
        fh.write("Vibrational partition function (Bot)       =%15.6e\n"%( self.GetVibrationalPartitionFunctionFromBottom_AU(T) ))
        fh.write("Rotational partition function              =%15.6e\n"%( self.GetRotationalPartitionFunction_AU(T) ))
        fh.write("Translational partition function           =%15.6e\n"%( self.GetTranslationalPartitionFunction_AU(T) ))
        fh.write("Electronic partition function              =%15.6e\n"%( self.GetElectronicPartitionFunction_AU() ))
        fh.write("Total partition function (V=0)             =%15.6e\n"%( self.GetPartitionFunctionFromV0_AU(T) ))
        fh.write("Total partition function (Bot)             =%15.6e\n"%( self.GetPartitionFunctionFromBottom_AU(T) ))


    def PrintFullReport(self,fh,T):
        import numpy as np
        from .. constants import GetAtomicSymbol
        from .. constants import AU_PER_ANGSTROM
        from .. constants import AU_PER_ATOMIC_MASS_UNIT
        from .. amber.Geometry import CptAngle, CptDihed
        
        fh.write("%i\n"%(len(self.atnum)))
        #isosub = ",".join(["%i"%(i) for i in self.isosub])
        #fh.write("%20.10e\n"%(AU_PER_ATOMIC_MASS_UNIT()))
        fh.write(" E=%.8f multiplicity=%i symnum=%i\n"%\
                 (self.E,self.multiplicity,self.symnum))
        for i in range(len(self.atnum)):
            if i in self.isosub:
                c="YES"
            else:
                c="no"
            m = self.mass[i] / AU_PER_ATOMIC_MASS_UNIT()
            fh.write("%2s %13.7f %13.7f %13.7f   %3s  %10.5f\n"%\
                     (GetAtomicSymbol(self.atnum[i]),
                      self.crd[i,0] / AU_PER_ANGSTROM(),
                      self.crd[i,1] / AU_PER_ANGSTROM(),
                      self.crd[i,2] / AU_PER_ANGSTROM(),
                      c, m))
        fh.write("\n")

        ncon = 0
        if self.conmat is not None:
            ncon = self.conmat.shape[0]
        fh.write(f"There are {ncon} constraints applied to the vibrational modes\n")
        if ncon > 0:
            fh.write("%6s %6s %6s %6s %6s %14s\n"%("Type","i","j","k","l","q (A or deg)"))
            for ib in range(ncon):
                t = self.conmat[ib,0]
                i = self.conmat[ib,1]-1
                j = self.conmat[ib,2]-1
                k = self.conmat[ib,3]-1
                l = self.conmat[ib,4]-1
                if t == 1:
                    q = np.linalg.norm( self.crd[i,:]-self.crd[j,:] ) / AU_PER_ANGSTROM()
                elif t == 2:
                    q = CptAngle( self.crd[i,:], self.crd[j,:], self.crd[k,:] )
                elif t == 3:
                    q = CptDihed( self.crd[i,:], self.crd[j,:], self.crd[k,:], self.crd[l,:] )
                else:
                    q = 0
                fh.write("%6i %6i %6i %6i %6i %12.5f\n"%(t,i+1,j+1,k+1,l+1,q))
        fh.write("\n")

        
        fh.write("%7s %12s %12s %12s\n"%("Mode","Freq.","Frc.Const.","Red.Mass."))
        fh.write("%7s %12s %12s %12s\n"%("","1/cm","mDyne/A","amu"))
        f = self.GetFreqs_InvCM()
        k = self.GetForceConsts_mDynePerAng()
        m = self.GetReducedMasses_AMU()
        for i in range(len(f)):
            fh.write("%7i %12.5f %12.5f %12.5f\n"%(i+1,f[i],k[i],m[i]))
        fh.write("\n")
        self.PrintThermochemistryReport(fh,T)

        
    def PrintVibrations(self,fh,vibs):
        
        from .. constants import GetAtomicSymbol
        from .. constants import AU_PER_ANGSTROM

        if vibs is None:
            return
        
        if len(vibs) < 1:
            return
        
        nat = len(self.mass)
        lines = []
        for i in range(nat):
            lines.append( "%2s %12.7f %12.7f %12.7f"%\
                          ( GetAtomicSymbol(self.atnum[i]),
                            self.crd[i,0] / AU_PER_ANGSTROM(),
                            self.crd[i,1] / AU_PER_ANGSTROM(),
                            self.crd[i,2] / AU_PER_ANGSTROM() ) )
        freqs = self.GetFreqs_InvCM()
        for imode in vibs:
            if imode < 0 or imode > len(freqs)-1:
                continue
            d = self.GetNormalizedDisplacementVector_AU(imode)
            fh.write("%i\nmode %i freq %.2f 1/cm\n"%(nat,imode+1,freqs[imode]))
            for i in range(nat):
                fh.write("%s  %10.5f %10.5f %10.5f\n"%\
                         (lines[i],
                          d[i,0] / AU_PER_ANGSTROM(),
                          d[i,1] / AU_PER_ANGSTROM(),
                          d[i,2] / AU_PER_ANGSTROM()))


        
    
    # def GetNormalizedDisplacementVector_Ang(self,imode):
    #     from .. constants import AU_PER_ANGSTROM
    #     return self.GetNormalizedDisplacementVector_AU(imode) / AU_PER_ANGSTROM()

    

    # def GetMassScaledDisplacementVector_AU(self,imode):
    #     import numpy as np
    #     c = np.array( self.dispmat[:,imode], copy=True )
    #     c = c.reshape( (len(self.mass),3) )
    #     M = np.sqrt( CorrectMass( self.mass ) )
    #     for i in range(len(M)):
    #         c[i,:] *= M[i]
    #     return c
    
    # def GetMassScaledDisplacementVector_Ang(self,imode):
    #     from .. constants import AU_PER_ANGSTROM
    #     return self.GetMassScaledDisplacementVector_AU(imode)/AU_PER_ANGSTROM()

    
    # def GetMassScaledDisplacedCrds_AU(self,imode,delta):
    #     return self.crd + delta * \
    #         self.GetMassScaledDisplacementVector_AU(imode)

    
    # def GetMassScaledDisplacedCrds_Ang(self,imode,delta):
    #     from .. constants import AU_PER_ANGSTROM
    #     return self.GetMassScaledDisplacedCrds_AU(imode,delta)/AU_PER_ANGSTROM()



if __name__ == "__main__":
    from ndfes.gaussian import GaussianOutput
    import numpy as np
    import sys
    import copy


    template = """#!/bin/bash
#SBATCH --job-name="example"
#SBATCH --output="example.slurmout"
#SBATCH --error="example.slurmerr"
#SBATCH --partition=main
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=20G
##SBATCH --account=rut149
##SBATCH --no-requeue
#SBATCH --export=ALL
#SBATCH -t 5:00:00
#SBATCH --exclude=slepner[009-045,048,054-061,079-081]
export GAUSS_SCRDIR=${PWD}
"""
    
    g = GaussianOutput(sys.argv[1])
    s = g.FirstStepWithHessian()
    nma = Vibrator.from_gaussian_archive(s,None)
    gcnma = copy.deepcopy(nma)

    #x = np.dot( np.linalg.inv(np.sqrt( GetMmat( nma.mass )) ), nma.X )
    
    gcnma.GenCrdSolve( nma.dispmat[:,:1] )
    
    #print(nma.dispmat)
    #print(gcnma.dispmat)
    #print( np.allclose(nma.dispmat,gcnma.dispmat) )
    
    exact = nma.GetFreqs_InvCM()
    approx = gcnma.GetFreqs_InvCM()
    nmode = min(exact.shape[0],approx.shape[0])
    exact = exact[:nmode]
    approx= approx[:nmode]

    
    #mass = nma.GetReducedMasses_AMU()
    #for a,b,m in zip(exact,approx,mass):
    #    print("%9.2f %9.2f"%(a,b))
    allerr = abs(exact-approx)
    allperc = 100*abs(allerr / exact)
    err = [ e for a,e in zip(exact,allerr) if a < 500 ]
    errperc = [ 100*abs(e/a) for a,e in zip(exact,allerr) if a < 500 ]
    if abs(exact[0]) < 500:
        print( "%9.2f %9.2f  ts: %8.2f (%5.1f)  w<500: %6.2f (%5.1f, %3i)  w: %6.2f (%5.1f, %3i)  %s"%( exact[0], approx[0],
                exact[0]-approx[0],
                100*abs((exact[0]-approx[0])/exact[0]),
                np.mean( err ), np.mean( errperc ), len(err),
                np.mean( allerr ), np.mean(allperc), len(allerr), sys.argv[1] ) )
    exit(0)
    
    #print(nma.GetForceConsts_AU()[0])
    #print(nma.GetForceConsts_mDynePerAng()[0])
    #print(nma.GetFreqs_InvCM()[0])
    #print(nma.GetReducedMasses_AMU()[0])

    
    
    #crd = nma.GetMassScaledDisplacementVector_AU(0)
    ele = nma.atnum
    crd = nma.GetNormalizedDisplacementVector_AU(0)
    for e,c in zip(ele,crd):
        print("%2i %12.5f %12.5f %12.5f"%(e,c[0],c[1],c[2]))
    #exit(0)
    masses = nma.mass

    
    for disp in [-0.1, -0.05, -0.02, -0.01, 0.00, 0.01, 0.02, 0.05, 0.1]:
        #crd = nma.GetMassScaledDisplacedCrds_Ang(0,disp)
        #crd = nma.crd + disp * nma.GetNormalizedDisplacementVector_AU(0)
        crd = nma.GetScaledDisplacedCrds_Ang(0,disp)

        print( np.dot(masses,crd)/np.sum(masses)) 
        
        base = "disp.%.2f"%(disp)
        inp = base+".inp"
        out = base+".out"
        slurm = base+".slurm"
        
        fh = open(inp, "w")
        fh.write("%NPROC=8\n%MEM=16GB\n")
        fh.write(s.GetInput(singlepoint=True,crd=crd))
        fh.close()

        fh = open(slurm,"w")
        fh.write(template)
        fh.write("g16 < %s > %s\n"%(inp,out))
        fh.close()
        
