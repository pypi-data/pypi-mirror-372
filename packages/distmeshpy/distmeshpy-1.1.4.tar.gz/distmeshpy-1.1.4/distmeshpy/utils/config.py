"""
Configuration class containing mesh parameters for distmesh.

Recommended sets of default parameters generated via the provided
factory functions. These parameters suffice for most use cases.
Custom parameters, such as maximum number of iterations, should be
specified by creating a new instance of DistMeshConfig.
"""

from dataclasses import dataclass

import numpy as np

from distmeshpy._typing import Float, Int

MACHINE_EPS_SQRT = np.sqrt(np.finfo(np.float64).eps)


@dataclass
class DistMeshConfig:
    """
    Configuration class for DistMesh.

    This class holds parameters used for mesh generation, such as tolerances,
    step sizes, and machine precision.
    """

    internal_pressure: Float = 1.2
    step_tol: Float = 1e-3
    mesh_tol: Float = 0.1
    euler_step: Float = 0.2
    machine_eps: Float = MACHINE_EPS_SQRT
    density_ctrl_freq: Int = 30
    max_iter: Int = 4000
    geometry_eps: Float = 1e-3


def default_2d_config() -> DistMeshConfig:
    """
    Generate default configuration for 2D meshes.

    :return: Default configuration object for 2D meshes.
    :rtype: DistMeshConfig
    """
    return DistMeshConfig()


def default_surface_config() -> DistMeshConfig:
    """
    Generate default configuration for 3D surface meshes.

    :return: Default configuration object for 3D surface meshes.
    :rtype: DistMeshConfig
    """
    return DistMeshConfig(step_tol=np.float64(1e-4))


def default_3d_config() -> DistMeshConfig:
    """
    Generate default configuration for 3D meshes.

    :return: Default configuration object for 3D meshes.
    :rtype: DistMeshConfig
    """
    return DistMeshConfig(
        internal_pressure=np.float64(1.1),
        geometry_eps=np.float64(0.1),
        euler_step=np.float64(0.1),
    )
