# -*- coding: utf-8 -*-
import os
import subprocess
import sys


ROOT_DIR = os.path.join(os.path.dirname(__file__), "bin")

def _program(name, args):
    return subprocess.call([os.path.join(ROOT_DIR, name)] + args, close_fds=False)


def ndfes():
    suffix = '.exe' if os.name == 'nt' else ''
    raise SystemExit(_program('ndfes' + suffix, sys.argv[1:]))


def ndfes_omp():
    suffix = '.exe' if os.name == 'nt' else ''
    raise SystemExit(_program('ndfes_omp' + suffix, sys.argv[1:]))


def ndfes_path():
    suffix = '.exe' if os.name == 'nt' else ''
    raise SystemExit(_program('ndfes-path' + suffix, sys.argv[1:]))


def ndfes_path_omp():
    suffix = '.exe' if os.name == 'nt' else ''
    raise SystemExit(_program('ndfes-path_omp' + suffix, sys.argv[1:]))


def ndfes_AvgFESs():
    raise SystemExit(_program('ndfes-AvgFESs.py', sys.argv[1:]))


def ndfes_CheckEquil():
    raise SystemExit(_program('ndfes-CheckEquil.py', sys.argv[1:]))


def ndfes_CombineMetafiles():
    raise SystemExit(_program('ndfes-CombineMetafiles.py', sys.argv[1:]))


def ndfes_path_analyzesims():
    raise SystemExit(_program('ndfes-path-analyzesims.py', sys.argv[1:]))


def ndfes_path_prepguess():
    raise SystemExit(_program('ndfes-path-prepguess.py', sys.argv[1:]))


def ndfes_PrepareAmberData():
    raise SystemExit(_program('ndfes-PrepareAmberData.py', sys.argv[1:]))


def ndfes_PrintFES():
    raise SystemExit(_program('ndfes-PrintFES.py', sys.argv[1:]))


# def ndfes_nma_MergeHessianNetCDFs():
#     raise SystemExit(_program('ndfes-nma-MergeHessianNetCDFs.py', sys.argv[1:]))


# def ndfes_nma_Thermochem():
#     raise SystemExit(_program('ndfes-nma-Thermochem.py', sys.argv[1:]))


# def ndfes_nma_KIE():
#     raise SystemExit(_program('ndfes-nma-KIE.py', sys.argv[1:]))


