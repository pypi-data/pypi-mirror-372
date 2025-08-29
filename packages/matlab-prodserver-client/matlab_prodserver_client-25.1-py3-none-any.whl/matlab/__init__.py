# Copyright 2014-2022 MathWorks, Inc.
"""
Array interface between Python and MATLAB

This package defines classes and exceptions that create and manage
multidimensional arrays in Python that are passed between Python and MATLAB.

Modules
-------
    * mcpyarray - type-specific multidimensional array classes for working
    with MATLAB, implemented in C++
"""

import os
import platform
import sys
from pkgutil import extend_path
__path__ = extend_path(__path__, '__name__')

_package_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_package_folder)

platform_name = platform.system()
if platform_name == 'Windows':
    arch = 'win64'
elif platform_name == 'Linux':
    arch = 'glnxa64'
elif platform_name == 'Darwin':
    platform_arch = platform.machine()
    if platform_arch == 'x86_64':
        arch = 'maci64'
    elif platform_arch == 'arm64':
        arch = 'maca64'
    else:
        raise RuntimeError('MacOS architecture {0} is not supported.'.format(platform_arch))
else:
    raise RuntimeError('Operating system {0} is not supported.'.format(platform_name))

_mcpyarray_folder = os.path.join(_package_folder, 'extern', 'bin', arch)
sys.path.insert(0, _mcpyarray_folder)

from matlabmultidimarrayforpython import double, single, uint8, int8, uint16, \
    int16, uint32, int32, uint64, int64, logical, ShapeError, SizeError
