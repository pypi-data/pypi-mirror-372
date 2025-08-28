"""
Provides access to 2D, 3D, and surface mesh generation functions.

These functions mirror the functionality of the original DistMesh MATLAB
program at http://persson.berkeley.edu/distmesh/, with the exception of
`distmesh3d` which in the original code is generalized as `dishmeshnd`.
"""

from distmeshpy.mesh.distmesh2d import distmesh2d
from distmeshpy.mesh.distmesh3d import distmesh3d
from distmeshpy.mesh.distmeshsurface import distmeshsurface

__all__ = ["distmesh2d", "distmesh3d", "distmeshsurface"]
