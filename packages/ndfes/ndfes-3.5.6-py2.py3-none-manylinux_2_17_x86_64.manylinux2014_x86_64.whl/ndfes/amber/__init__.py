#!/usr/bin/env python3

"""
Utilities for reading Amber-style restraint information and trajectory files

Brief summary of functions
--------------------------
CptDist(a,b) -> q
    Computes interatomic distance

CptR12(a,b,c,d,rstwt) -> q
    Computes a linear combination of distances

CptAngle(a,b,c) -> q
    Computes the angle between 3 points

CptDihed(a,b,c,d) -> q
    Computes the dihedral angle between 4 points

CptDistAndGrd(a,b) -> q,dqda,dqdb
    Computes interatomic distance and gradient

CptR12AndGrd(a,b,c,d,rstwt) -> q,dqda,dqdb,dqdc,dqdd
    Computes a linear combination of distances and gradient

CptAngleAndGrd(a,b,c) -> q,dqda,dqdb,dqdc
    Computes the angle between 3 points and gradient

ReadEnergies(filename) -> numpy.array
    Reads a mdout file and returns the potential energy time series

ReadCrds(filename) -> numpy.array
    Returns the coordinates of each frame in a netcdf trajectory file

ReadFrcs(filename) -> numpy.array
    Returns the forces of each frame in a netcdf trajectory file

ReadCrdsFrcsAndBox(filename) -> numpy.array
    Returns the coordinates, forces, and unit cell of each frame in a 
    netcdf trajectory file

ReadCrdsAndBox(filename) -> numpy.array, numpy.array
    Returns the coordinates and unit cell of each frame in a 
    netcdf trajectory file

ReadAvgCrds(tfiles,aidxs,masses) -> numpy.array
    Reads one-or-more netcdf trajectory files, RMS fits the
    coordinates of the specified atoms, and returns the average coordinates

ReadAvgCrdsAndFrcs(tfiles,ffiles,aidxs,masses) -> numpy.array
    Reads one-or-more netcdf trajectory files of coordinates and forces, 
    RMS fits the coordinates of the specified atoms, and returns the 
    average coordinates

CptCoM(crd,wts) ->  numpy.array
    Get center of mass coordinates

RemoveCoM(crd,wts) ->  numpy.array
    Remove center of mass

CptRmsTransform(crd,rcrd,wts) -> float,numpy.array,numpy.array,numpy.array
    Compute the rotation and translation vectors needed to perform a
    RMS overlay

PerformRmsOverlay(crd,rcrd,wts) -> float,numpy.array
    Compute coordinate RMSD and return the rotated/translated coordinates

Brief summary of classes
------------------------
Restraint
    Stores the definition of one restraint

Disang
    Stores the definition of multiple restraints

"""

from . Geometry import CptDist
from . Geometry import CptR12
from . Geometry import CptAngle
from . Geometry import CptDihed
from . Geometry import CptDistAndGrd
from . Geometry import CptR12AndGrd
from . Geometry import CptAngleAndGrd
from . Geometry import CptCoM
from . Geometry import RemoveCoM
from . Geometry import CptRmsTransform
from . Geometry import PerformRmsOverlay

from . Reader import ReadEnergies
from . Reader import ReadCrds
from . Reader import ReadFrcs
from . Reader import ReadCrdsFrcsAndBox
from . Reader import ReadCrdsAndBox
from . Reader import ReadAvgCrds
from . Reader import ReadAvgCrdsAndFrcs

from . Restraint import Restraint
from . Disang import Disang


__all__ = ['CptDist',
           'CptR12',
           'CptAngle',
           'CptDihed',
           'CptDistAndGrd',
           'CptR12AndGrd',
           'CptAngleAndGrd',
           'CptCoM',
           'RemoveCoM',
           'CptRmsTransform',
           'PerformRmsOverlay',
           'ReadEnergies',
           'ReadCrds',
           'ReadFrds',
           'ReadCrdsFrcsAndBox',
           'ReadCrdsAndBox',
           'ReadAvgCrds',
           'ReadAvgCrdsAndFrcs',
           'Restraint',
           'Disang']

