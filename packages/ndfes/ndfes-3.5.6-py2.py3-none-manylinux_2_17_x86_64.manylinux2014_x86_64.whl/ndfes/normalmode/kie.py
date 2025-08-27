#!/usr/bin/env python3

def BigeleisenMayerKIE( rslight, rsheavy, tslight, tsheavy, temperature=298.15 ):
    """
    Calculates a KIE using the Bigeleisen-Mayer equation.
    The input arguments are lists of Vibrator objects, which contain
    the results of normal mode analysis.  They are lists because
    the reaction may involve more than one molecule, although the
    transition state usually corresponds to a single "molecule".

    Parameters
    ----------
    rslight : list of Vibrator
        The normal mode analysis of the reactant state performed
        with the light isotopes

    rsheavy : list of Vibrator
        The normal mode analysis of the reactant state performed
        with the heavy isotopes

    tslight : list of Vibrator
        The normal mode analysis of the transition state performed
        with the light isotopes

    tsheavy : list of Vibrator
        The normal mode analysis of the transition state performed
        with the heavy isotopes

    temperature : float, default=298.15
        The temperature in Kelvin

    Returns
    -------
    kie : float
        The kinetic isotope effect

    Example
    -------
    from ndfes.normalmode import *
    from ndfes.gaussian import GaussianOutput
    rs = GaussianOutput("reactant/min.out").FirstStepWithHessian()
    ts = GaussianOutput("ts/tssearch.out").FirstStepWithHessian()
    rslight = Vibrator.from_gaussian_archive(rs,None)
    tslight = Vibrator.from_gaussian_archive(ts,None)
    rsO2 = Vibrator.from_gaussian_archive(rs,[11])
    tsO2 = Vibrator.from_gaussian_archive(ts,[11])
    kieO2 = BigeleisenMayerKIE( [rslight], [rsO2], [tslight], [tsO2], 298.15 )
    print("KIE O2' %.3f"%(kieO2))
    """
    import numpy as np
    from .. constants.Conversions import BOLTZMANN_CONSTANT_AU
    ufact = 0.5 / ( BOLTZMANN_CONSTANT_AU() * temperature )

    if len(rslight) != len(rsheavy):
        raise Exception("len(rslight) != len(rsheavy) : "
                        f"{len(rslight)} vs {len(rsheavy)}")
    
    if len(tslight) != len(tsheavy):
        raise Exception("len(tslight) != len(tsheavy) : "
                        f"{len(tslight)} vs {len(tsheavy)}")
    
    kie = 1.0
    for s in range(len(rslight)):
        wls = rslight[s].GetFreqs_AU()
        whs = rsheavy[s].GetFreqs_AU()
        for wl,wh in zip(wls,whs):
            if wl > 0 and wh > 0:
                kie *= ( np.sinh(ufact*wl) / np.sinh(ufact*wh) )
            if abs(wl) > 0 and abs(wh) > 0:
                kie *= (wh/wl)
                
    for s in range(len(tslight)):
        wls = tslight[s].GetFreqs_AU()
        whs = tsheavy[s].GetFreqs_AU()
        for wl,wh in zip(wls,whs):
            if wl > 0 and wh > 0:
                kie *= ( np.sinh(ufact*wh) / np.sinh(ufact*wl) )
            if abs(wl) > 0 and abs(wh) > 0:
                kie *= (wl/wh)
    return kie


def KIETunnelingFactor( tslight, tsheavy, temperature=298.15 ):
    import numpy as np
    from .. constants.Conversions import BOLTZMANN_CONSTANT_AU
    ufact = 0.5 / ( BOLTZMANN_CONSTANT_AU() * temperature )

    tfact = 1.
    for s in range(len(tslight)):
        wls = tslight[s].GetFreqs_AU()
        whs = tsheavy[s].GetFreqs_AU()
        for wl,wh in zip(wls,whs):
            if wl < 0 and wh < 0:
                tfact *= (wl/np.sin(ufact*wl)) / (wh/np.sin(ufact*wh))
                break
    return tfact

