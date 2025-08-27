#!/usr/bin/env python3


def SwitchOff(r,rlo,rhi):
    s = 1
    if r >= rhi:
        s = 0
    elif r <= rlo:
        s = 1
    else:
        u = (rhi-r)/(rhi-rlo)
        u3 = u*u*u
        u4 = u3*u
        u5 = u4*u
        s = 10. * u3 - 15. * u4 + 6. * u5
    return s


def SwitchOn(rab,rlo,rhi):
    return 1. - SwitchOff(rab,rlo,rhi)


class DensityEst(object):
    """
    A class used to calculate the probability density of biased
    free energy surfaces. The unbiased free energy surface is
    read upon construction and intermediate values are internally
    stored to optimize performance when later querying the
    density for many different biasing potentials.

    Attributes
    ----------
    fes : ndfes.FES or derived-class
        The object defining the free energy surface

    nquad : int
        The number of quadrature points in each dimension to integrate
        a single bin

    qwts : numpy.array, dtype=float, shape=(nquad**ndim,)
        The quadrature weights of a single bin

    qpts : numpy.array, dtype=float, shape=(nquad**ndim,ndim)
        The quadrature points of a single bin centered at the origin

    fvals : dict of numpy.array, dtype=float, shape=(nquad**ndim,)
        The free energy values (kcal/mol) at each quadrature point
        for each bin (the global bin index is the key to the dict)

    relo : float
        The lower bound on acceptable reweighting entropies.
        Bins with a entropy less than relo will be ignored, effectively
        treating it as if its free energy is +inf

    rehi : float
        The upper bound on acceptable reweighting entropies.
        Bins with a entropy greater than rehi will be trusted.
        Bins with entropies above relo and below rehi will
        be smoothly scaled.

    Methods
    -------
    """

    def __init__(self,fes,T,nquad,relo=0.3,rehi=0.5):
        """
        Parameters
        ----------
        fes : ndfes.FES or derived-class
            The object defining the free energy surface

        T : float
            The temperature (K) of the FES

        nquad : int
            The number of quadrature points in each dimension to integrate
            a single bin

        relo : float, default=0.3
            The lower bound on acceptable reweighting entropies.
            Bins with a entropy less than relo will be ignored, effectively
            treating it as if its free energy is +inf

        rehi : float, default=0.5
            The upper bound on acceptable reweighting entropies.
            Bins with a entropy greater than rehi will be trusted.
            Bins with entropies above relo and below rehi will
            be smoothly scaled.
        """
        from collections import defaultdict as ddict
        import numpy as np
        
        self.fes=fes
        self.T = T
        self.nquad=nquad
        self.relo=relo
        self.rehi=rehi
        self.qpts,self.qwts = self.fes.grid.GetQuadMesh(self.nquad)

        try:
            for gidx,sbin in sorted(self.fes.bins.items()):
                c = np.array(sbin.center)
                break
            v = self.fes.CptInterp( [c] )
            has_interp = True
        except Exception as e:
            has_interp = False
            
        self.fvals = ddict(int)

        if has_interp:
            for gidx,sbin in sorted(self.fes.bins.items()):
                qpts = np.array(sbin.center) + self.qpts
                self.fvals[gidx] = self.fes.CptInterp(qpts).values
        else:
            for gidx,sbin in sorted(self.fes.bins.items()):
                self.fvals[gidx] = np.array([ sbin.value ]*self.qpts.shape[0])


                
    def GetBeta(self,T):
        """Returns 1/kT which converts energies in kcal/mol to reduced
        energy units

        Parameters
        ----------
        T : float
            Temperature (K)

        Returns
        -------
        beta : float
            1/kT in (kcal/mol)^{-1}
        """
        
        import scipy.constants
        Jperkcal = scipy.constants.calorie * 1000 / scipy.constants.Avogadro
        boltz = scipy.constants.Boltzmann / Jperkcal
        return 1./(boltz*T)
    

    
    def GetDensity(self,fcs=None,rcs=None):
        """Returns the probability density of each bin
        
        Parameters
        ----------
        fcs : numpy.array, dtype=float, shape=(ndim,), default=None
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcs : numpy.array, dtype=float, shape=(ndim,), default=None
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        rho : dict of float
            The dictionary keys are the global index of each bin and the
            values are the densities
        """

        import numpy as np
        from collections import defaultdict as ddict
        from . MBAR import MBAR

        if fcs is not None and rcs is not None:
            rcs=np.array(rcs)
            fcs=np.array(fcs)
        beta = self.GetBeta(self.T)
        rho=ddict(int)
        Q=0.0
        for gidx,sbin in sorted(self.fes.bins.items()):
            
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)

            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                v = np.dot(self.qwts,np.exp(-beta*(F+W)))
            else:
                v = np.dot(self.qwts,np.exp(-beta*F))
            v *= re
            Q += v
            rho[gidx] = v
        for gidx in rho:
            rho[gidx] /= Q
        return rho



    
    def GetContinuousDensity(self,fcs=None,rcs=None):
        """Returns the probability density of each bin
        
        Parameters
        ----------
        fcs : numpy.array, dtype=float, shape=(ndim,), default=None
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcs : numpy.array, dtype=float, shape=(ndim,), default=None
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        rho : dict of numpy.ndarray of size nquad**ndim
            The dictionary keys are the global index of each bin and the
            values are the densities at each quadrature point in the
            bin
        """

        import numpy as np
        from collections import defaultdict as ddict
        from . MBAR import MBAR

        if fcs is not None and rcs is not None:
            rcs=np.array(rcs)
            fcs=np.array(fcs)
        beta = self.GetBeta(self.T)
        rho=ddict(int)
        Q=0.0
        for gidx,sbin in sorted(self.fes.bins.items()):
            
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)

            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                rho[gidx] = re * np.exp(-beta*(F+W))
                v = np.dot(self.qwts,rho[gidx])
            else:
                rho[gidx] = re * np.exp(-beta*F)
                v = np.dot(self.qwts,rho[gidx])
            Q += v
        for gidx in rho:
            rho[gidx] /= Q
        return rho


    # def GetDensityAndWrappedCenters(self,fcs,rcs):
    #     """Returns the probability density of each bin and the position
    #     of each bin center with consideration of the periodicity relative
    #     to the umbrella potential
        
    #     Parameters
    #     ----------
    #     fcs : numpy.array, dtype=float, shape=(ndim,)
    #         Calculate the density from the FES biased with an additional
    #         umbrella potential with these force constants in each dimension

    #     rcs : numpy.array, dtype=float, shape=(ndim,)
    #         Calculate the density from the FES biased with an additional
    #         umbrella potential located at this position

    #     Returns
    #     -------
    #     rho : dict of float
    #         The dictionary keys are the global index of each bin and the
    #         values are the densities

    #     binpos : dict of numpy.array, shape=(ndim,)
    #         The wrapped position of each bin center
    #     """

    #     import numpy as np
    #     from collections import defaultdict as ddict
    #     from . MBAR import MBAR

    #     rcs=np.array(rcs)
    #     fcs=np.array(fcs)
    #     beta = self.GetBeta(self.T)
    #     rho=ddict(int)
    #     binpos=ddict(int)
    #     Q=0.0
    #     for gidx,sbin in sorted(self.fes.bins.items()):
            
    #         re = 1.0
    #         if isinstance(self.fes,MBAR):
    #             re = sbin.entropy
    #         re = SwitchOn(re,self.relo,self.rehi)

    #         F = self.fvals[gidx]
    #         wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
    #         qpts = wc + self.qpts
    #         W = np.dot( (qpts-rcs)**2, fcs )
    #         v = np.dot(self.qwts,np.exp(-beta*(F+W)))
    #         v *= re
    #         Q += v
    #         rho[gidx] = v
    #         binpos[gidx] = wc
    #     for gidx in rho:
    #         rho[gidx] /= Q
    #     return rho,binpos

    
    def GetAvgPos(self,fcs,rcs):
        """Estimate the mean position of the reaction coordinates from
        a biased simulation

        Parameters
        ----------
        fcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        avg : numpy.array, dtype=float, shape=(ndim,)
            The expected position of the reaction coordinates
        """

        import numpy as np
        from . MBAR import MBAR
        
        # rho = self.GetDensity(T,fcs=fcs,rcs=rcs)
        # avg=np.zeros( (self.fes.grid.ndim,) )
        # for gidx,sbin in sorted(self.fes.bins.items()):
        #     avg += rho[gidx] * sbin.center
        
        if fcs is not None and rcs is not None:
            rcs=np.array(rcs)
            fcs=np.array(fcs)
            
        beta = self.GetBeta(self.T)
        avg=np.zeros( (self.fes.grid.ndim,) )
        Q=0.0
        for gidx,sbin in sorted(self.fes.bins.items()):
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)
            

            
            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                es = self.qwts*np.exp(-beta*(F+W))
            else:
                qpts = np.array(sbin.center) + self.qpts
                es = self.qwts*np.exp(-beta*F)
            es *= re
            avg += np.dot(es,qpts)
            v = np.sum(es)
            Q += v
        avg = avg/Q
        #print(rcs,avg)

        return avg



    def GetAvgEne(self,fcs,rcs):
        """Estimate the mean energy from a biased simulation

        Parameters
        ----------
        fcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        avg : float
            The density-weighted free energy
        """

        import numpy as np
        from . MBAR import MBAR
        
        if fcs is not None and rcs is not None:
            rcs=np.array(rcs)
            fcs=np.array(fcs)
            
        beta = self.GetBeta(self.T)
        avg=0
        Q=0.0
        for gidx,sbin in sorted(self.fes.bins.items()):
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)
            

            
            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                es = re * self.qwts*np.exp(-beta*(F+W))
            else:
                qpts = np.array(sbin.center) + self.qpts
                es = re * self.qwts*np.exp(-beta*F)
            avg += np.dot(es,F)
            Q += np.sum(es)
        avg = avg/Q

        return avg
    

    def GetAvgEneAndGrd(self,fcs,rcs):
        """Estimate the mean energy from a biased simulation

        Parameters
        ----------
        fcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        avg : float
            The density-weighted free energy
       
        grd : np.array, dtype=float, shape=(ndim,)
            The gradient of the energy with respect to rcs
        """

        import numpy as np
        from . MBAR import MBAR

        ndim = self.fes.grid.ndim
        avg = 0.
        grd=np.zeros( (ndim,) )
        beta = self.GetBeta(self.T)

        if fcs is not None and rcs is not None:
            rcs=np.array(rcs)
            fcs=np.array(fcs)
            
        Q=0.0
        dQ = np.zeros( (ndim,) )
        des = np.zeros( (self.qwts.shape[0],ndim,) )
        for gidx,sbin in sorted(self.fes.bins.items()):
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)
            
            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                es = re * self.qwts*np.exp(-beta*(F+W))
                tmp = 2*beta*fcs*(qpts-rcs) 
                des = es[:,np.newaxis] * tmp
                #print(tmp.shape,es.shape,des.shape,F.shape)
            else:
                qpts = np.array(sbin.center) + self.qpts
                es = re * self.qwts*np.exp(-beta*F)
            v = np.sum(es)
            avg += np.dot(F,es)
            Q += v
            grd += np.dot(F,des)
            dQ += np.sum(des,axis=0)
            
        grd = grd/Q - (avg/(Q*Q))*dQ
        avg = avg/Q

        return avg,grd
    


    def GetAvgFromBinDensity(self,rho):
        """Estimate the mean position of the reaction coordinates from
        a histogram density

        Parameters
        ----------
        rho : dict (key : int, the global index of the bin)
            The integrated value of the density in each histogram bin

        Returns
        -------
        avg : numpy.array, dtype=float, shape=(ndim,)
            The expected position of the reaction coordinates
        """
        avg=np.zeros( (self.fes.grid.ndim,) )
        for gidx,sbin in sorted(self.fes.bins.items()):
            avg += rho[gidx] * sbin.center
        return avg

    
    def GetOverlapPercent(self,fcsa,rcsa,fcsb,rcsb):
        """Calculate the overlap percent of two biased simulations

        Parameters
        ----------
        fcsa : numpy.array, dtype=float, shape=(ndim,)
            Simulation "a"
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcsa : numpy.array, dtype=float, shape=(ndim,)
            Simulation "a"
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        fcsb : numpy.array, dtype=float, shape=(ndim,)
            Simulation "b"
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcsb : numpy.array, dtype=float, shape=(ndim,)
            Simulation "b"
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        Sab : numpy.array, dtype=float, shape=(ndim,)
            The percent overlap between the 2 simulations
        """
        rhoa = self.GetDensity(fcsa,rcsa)
        rhob = self.GetDensity(fcsb,rcsb)
        return self.GetOverlapPercentFromBinDensities(rhoa,rhob)

    
    def GetOverlapPercentFromBinDensities(self,rhoa,rhob):
        """

        Parameters
        ----------
        rho : dict (key : int, the global index of the bin)
            The integrated value of the density in each histogram bin

        Returns
        -------
        avg : numpy.array, dtype=float, shape=(ndim,)
            The expected position of the reaction coordinates
        """
        Saa = 0.
        Sab = 0.
        Sbb = 0.
        for gidx,sbin in sorted(self.fes.bins.items()):
            Saa += rhoa[gidx] * rhoa[gidx]
            Sab += rhoa[gidx] * rhob[gidx]
            Sbb += rhob[gidx] * rhob[gidx]
        return Sab / max(Saa,Sbb)


    def GetAvgPosAndStd(self,fcs,rcs):
        """Estimate the mean position of the reaction coordinates from
        a biased simulation and the standard deviation of the estimate

        Parameters
        ----------
        fcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential with these force constants in each dimension

        rcs : numpy.array, dtype=float, shape=(ndim,)
            Calculate the density from the FES biased with an additional
            umbrella potential located at this position

        Returns
        -------
        avg : numpy.array, dtype=float, shape=(ndim,)
            The expected position of the reaction coordinates
        """

        import numpy as np
        from . MBAR import MBAR
        
        # rho = self.GetDensity(T,fcs=fcs,rcs=rcs)
        # avg=np.zeros( (self.fes.grid.ndim,) )
        # for gidx,sbin in sorted(self.fes.bins.items()):
        #     avg += rho[gidx] * sbin.center
        
        if fcs is not None and rcs is not None:
            rcs=np.array(rcs)
            fcs=np.array(fcs)
            
        beta = self.GetBeta(self.T)
        avg=np.zeros( (self.fes.grid.ndim,) )
        var=np.zeros( (self.fes.grid.ndim,) )
        Q=0.0
        for gidx,sbin in sorted(self.fes.bins.items()):
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)

            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                es = self.qwts*np.exp(-beta*(F+W))
            else:
                qpts = np.array(sbin.center) + self.qpts
                es = self.qwts*np.exp(-beta*F)
            es *= re
            avg += np.dot(es,qpts)
            v = np.sum(es)
            Q += v
        avg = avg/Q
        
        for gidx,sbin in sorted(self.fes.bins.items()):
            re = 1.0
            if isinstance(self.fes,MBAR):
                re = sbin.entropy
            re = SwitchOn(re,self.relo,self.rehi)

            F = self.fvals[gidx]
            if fcs is not None and rcs is not None:
                wc = self.fes.grid.DiffCrd(sbin.center,rcs) + rcs
                qpts = wc + self.qpts
                W = np.dot( (qpts-rcs)**2, fcs )
                es = self.qwts*np.exp(-beta*(F+W))/Q
            else:
                qpts = np.array(sbin.center) + self.qpts
                es = self.qwts*np.exp(-beta*F)/Q
            es *= re
            var += np.dot(es,(qpts-avg)**2)
            
        return avg,np.sqrt(var)


