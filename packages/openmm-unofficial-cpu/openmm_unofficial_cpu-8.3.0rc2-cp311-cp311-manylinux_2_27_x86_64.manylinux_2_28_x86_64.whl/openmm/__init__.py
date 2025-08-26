"""OpenMM is a toolkit for molecular simulation. It can be used either as a
stand-alone application for running simulations, or as a library you call
from your own code. It provides a combination of extreme flexibility
(through custom forces and integrators), openness, and high performance
(especially on recent GPUs) that make it truly unique among simulation codes.
"""
from __future__ import absolute_import
__author__ = "Peter Eastman"

import os, os.path
import sys


openmm_library_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
if not os.path.exists(openmm_library_path):
    # The conda package installs all the libraries in the env/lib directory
    import site

    openmm_library_path = os.path.abspath(os.path.join(site.getsitepackages()[0], '..', '..'))
    if sys.platform == 'win32':
        # Don't move this in the next if below. it should only happen on conda packages where
        # lib is not under the package root.
        openmm_library_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Library', 'lib')

if sys.platform == 'win32':
    _path = os.environ['PATH']
    os.environ['PATH'] = r'%(lib)s;%(lib)s\plugins;%(path)s' % {
        'lib': openmm_library_path, 'path': _path}
    try:
        with os.add_dll_directory(openmm_library_path):
            from . import _openmm
    except:
        pass

from openmm.openmm import *
from openmm.vec3 import Vec3
from openmm.mtsintegrator import MTSIntegrator, MTSLangevinIntegrator
from openmm.amd import AMDIntegrator, AMDForceGroupIntegrator, DualAMDIntegrator

if os.getenv('OPENMM_PLUGIN_DIR') is None and os.path.isdir(openmm_library_path):
    pluginLoadedLibNames = Platform.loadPluginsFromDirectory(os.path.join(openmm_library_path, 'plugins'))
else:
    pluginLoadedLibNames = Platform.loadPluginsFromDirectory(Platform.getDefaultPluginsDirectory())

if sys.platform == 'win32':
    os.environ['PATH'] = _path
    del _path
__version__ = Platform.getOpenMMVersion()

class OpenMMException(Exception):
    """This is the class used for all exceptions thrown by the C++ library."""
    pass

from . import version
