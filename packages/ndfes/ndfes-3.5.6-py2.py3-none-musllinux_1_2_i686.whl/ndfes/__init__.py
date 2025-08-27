#!/usr/bin/env python3
"""
The ndfes C++ program will solve the vFEP or MBAR equations, and store the
final, multidimensional free energy surface to a checkpoint file. The 
checkpoint is formatted as a python module that contains a list of objects,
each element of which corresponds to a free energy surface of a target 
Hamiltonian.  The ndfes module provides functions to retreive the free energy
surfaces from the checkpoint file, and this module also defines the classes 
used to store the free energy surfaces within the checkpoint file.

Brief summary of functions
--------------------------
LoadModule(filename) -> python module reference
    Loads a text file as a python module

GetModelsFromFile(filename) -> list
    Reads a ndfes checkpoint file and returns the free energy surface objects

GetPtsFromRegGrid(np.array) -> np.array
    Converts a collection of numpy meshgrids (describing a regular grid) into
    a list of points shape=(npts,ndim)

LinearPtsToMeshPts(lpts) -> np.array
    Converts N lists of 1D coordinates into a matrix, interpreted as a 
    list of N-dimensional grid coordinates.  The difference between this
    function and GetPtsFromRegGrid is that this routine takes a list of
    lists instead of a 3-indexed meshgrid as input

LinearWtsToMeshWts(lwts) -> np.array
    Converts N lists of 1D weights into an array of weight products for
    the N-dimensional grid

GetContourLines(x,y,z,levels) ->  matplotlib.contour.QuadContourSet
    Computes contour lines from a 2d meshgrid

Plot2dHistogram(fig,ax,model,axlabels,csty,shift_fes=True) -> None
    Draw a 2d heatmap of the FES

Plot2dPath(fig,ax,path_crds,mgrid,model,fes,axlabels,csty,lsty) -> None
    Draw a 2d heatmap of the FES with a free energy pathway

ContourFmt(value) -> str
    Removes trailing zeros, e.g. "1.0" becomes "1". This function is passed to
    matplotlib's clabel method to inline contour values

CptBsplineValues(x,xmin,binwidth,order) -> np.array, np.array
    Evaluate 1D Cardinal B-spline weights and corner indexes about a point

CptBsplineValuesAndDerivs(x,xmin,binwidth,order) -> np.array, np.array
    Evaluate 1D Cardinal B-spline weights, derivatives, and corner indexes 
    about a point

SmoothCurve_WinAvg(x,wlen,smoothness) -> np.array
    Smooth a parametric curve by windowed averaging. The resulting curve will
    "cut corners".

SmoothCurve_IterWinAvg(x0,wlen_max,smoothness) -> np.array
    Smooth a parametric curve by an iterative windowed average. The iterative
    procedure will help avoid corner-cutting.

ReadPaths(fname,ndim) -> ndfes.PathOpt
    Read paths from a file

Brief summary of classes
------------------------
SpatialDim
    Stores the axis and histogram definition along an dimension

SpatialBin
    Stores the value, standard error, and reweighting entropy of a bin

VirtualGrid
    Stores the multidimensional histogram definition

MBAR
    Stores the MBAR free energy histogram information read from an ndfes
    checkpoint file

vFEP
    Stores the vFEP B-spline information read from an ndfes checkpoint file

GPR
    Performs Gaussian Process Regression, allowing one to smooth and 
    interpolate multidimensional free energy data

RBF
    Performs Radial Basis Function interpolation

MinImg
    Used to calculate minimum image distances

EvalT
    A common return type that stores interpolated free energy values,
    standard errors, and free energy gradients

PCurve
    A parametric curve interpolated with Akima splines for each dimension
 
Trajectory
    Stores the dumpave filename and umbrella window information of a
    trajectory (one of the lines in a metafile)

Metafile
    Reads and stores the trajectory information from a metafile. This is
    a collection of Trajectory objects.

ColorAndContours
    Contains information for assigning colors to free energy values and
    the contour levels to draw

LineStyle
    An object to store matplotlib line style parameters

SurfaceStyle
    An object to store matplotlib surface style parameters

AxesStyle
    A class that stores the matplotlib style parameters for an axes

AxesLabels
    A class that collects the axes styles for multiple axes

PathProj3D
    A class for drawing planes and lines of a free energy pathway in
    3 dimensions

PathCube
    A class that can draw: (1) a 3d cube, and (2) 2d projections
    of the 3d cube

PathSpl
    A class defining a parametric curve for a particular iteration

PathSims
    A class containing the simulations performed for a particular iteration

PathIter
    A class containing the input spline and input simulations for a 
    particular iteration

PathOpt
    A collection of path iterations defining a path optimization

PCV
    A class that defines path collective variables which can be
    read and written in a manner compatible with plumed
"""

from . ReadCheckpoint import LoadModule
from . ReadCheckpoint import GetModelsFromFile
from . ReadCheckpoint import SaveXml

from . GridUtils import GetPtsFromRegGrid
from . GridUtils import LinearPtsToMeshPts
from . GridUtils import LinearWtsToMeshWts
from . GridUtils import MinImg
from . GridUtils import WrapAngleRelativeToRef
from . GridUtils import MeanAngleRelativeToRef
from . GridUtils import MeanAngleAndStdRelativeToRef

from . SpatialDim import SpatialDim

from . SpatialBin import SpatialBin

from . VirtualGrid import VirtualGrid

from . EvalT import EvalT

from . FES import FES

from . MBAR import MBAR

from . vFEP import vFEP

from . GPR import GPR

from . RBF import RBF

from . Trajectory import Trajectory

from . Metafile import Metafile

#from . DensityEst import DensityEst

from . PathUtils import PCurve
#from . PathUtils import PGPRCurve
#from . PathUtils import PGPRStringMethodUpdate
#from . PathUtils import CptCrdMeanAndError
#from . PathUtils import GetCrdMeanAndErrorFromFile
#from . PathUtils import ReadDumpavesAsPGPR
#from . PathUtils import ReadDumpavesAsPCurve

from . PlotUtils import ContourFmt
from . PlotUtils import ColorAndContours
from . PlotUtils import GetContourLines
from . PlotUtils import LineStyle
from . PlotUtils import SurfaceStyle
from . PlotUtils import AxesStyle
from . PlotUtils import AxesLabels
from . PlotUtils import Plot2dHistogram
from . PlotUtils import Plot2dPath
from . PlotUtils import PathProj3D
from . PlotUtils import PathCube

# from . OptUtils import UnbiasedMinimize
# from . OptUtils import BiasedMinimize
# from . OptUtils import UnbiasedMaximize
# from . OptUtils import BiasedMaximize
# from . OptUtils import PathProps

from . Bspline import CptBsplineValues
from . Bspline import CptBsplineValuesAndDerivs


# from . DensityString import DensitySim
# from . DensityString import DensityString
# from . DensityString import DensityStringOpt
# from . DensityString import DensityStringSimLimits

#from . AutoEquil import AutoEquil
#from . AutoEquil import AutoSubsample
#from . AutoEquil import ChunkAnalysis
from . AutoEquil import SliceAnalysis

from . SmoothCurve import SmoothCurve_IterWinAvg
from . SmoothCurve import SmoothCurve_WinAvg
from . SmoothCurve import SmoothCurve_IterReflectedAvg
from . import amber
from . import constants
from . import gaussian
from . import normalmode

from . import deprecated
from . import FTSM

from . PathData import PathSpl
from . PathData import PathSims
from . PathData import PathIter
from . PathData import PathOpt
from . PathData import ReadPaths

from . ScriptUtils import AddStdOptsToCLI
from . ScriptUtils import SetupModelFromCLI
from . ScriptUtils import WritePathProjection

from . PCV import PCV

__all__ = ['deprecated',
           'FTSM',
           'amber',
           'constants',
           'gaussian',
           'normalmode',
           'AutoEquil',
           'AutoSubsample',
           'ChunkAnalysis',
           'LoadModule',
           'GetModelsFromFile',
           'GetPtsFromRegGrid',
           'LinearPtsToMeshPts',
           'LinearWtsToMeshWts',
           'MinImg',
           'WrapAngleRelativeToRef',
           'MeanAngleRelativeToRef',
           'MeanAngleAndStdRelativeToRef',
           'SpatialDim',
           'SpatialBin',
           'VirtualGrid',
           'EvalT',
           'FES',
           'MBAR',
           'vFEP',
           'GPR',
           'RBF',
           'Trajectory',
           'Metafile',
           'PCurve',
           'ContourFmt',
           'ColorAndContours',
           'GetContourLines',
           'LineStyle',
           'SurfaceStyle',
           'AxesStyle',
           'AxesLabel',
           'Plot2dHistogram',
           'Plot2dPath',
           'PathProj3D',
           'PathCube',
           'CptBsplineValues',
           'CptBsplineValuesAndDerivs',
           'SmoothCurve_IterWinAvg',
           'SmoothCurve_WinAvg',
           'SmoothCurve_IterReflectedAvg',
           'PathSpl',
           'PathSims',
           'PathIter',
           'PathOpt',
           'ReadPaths',
           'AddStdOptsToCLI',
           'SetupModelFromCLI',
           'WritePathProjection',
           'PCV']

