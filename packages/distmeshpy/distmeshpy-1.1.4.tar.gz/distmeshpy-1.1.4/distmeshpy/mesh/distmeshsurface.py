"""Implementation of distmesh algorithm for surfaces in 3D space."""

from __future__ import annotations

from typing import Any

import numpy as np
from mcubes import marching_cubes  # type: ignore

from distmeshpy._typing import Array, Float, Function, Triangulation
from distmeshpy.core import TriangleConnectivity, apply_force_3d, triangle_find_edges
from distmeshpy.utils.config import DistMeshConfig, default_surface_config


def distmeshsurface(
    dist_func: Function,
    size_func: Function,
    edge_size: Float,
    bounding_box: tuple[tuple[Float, Float], tuple[Float, Float], tuple[Float, Float]],
    config: DistMeshConfig | None = None,
    **kwargs: dict[str, Any],
) -> tuple[Array, Triangulation]:
    """
    Generate 3D surface mesh.

    Mirror function of ``distmeshsurface.m`` in the original MATLAB code. From original
    author: "Doesn't work too well for nonuniform size functions. Need a better initial
    grid or density control. Also no support for fixed points, again because of the
    initial grid."

    :param dist_func: Distance function.
    :type dist_func: Function
    :param size_func: Scaled edge length function.
    :type size_func: Function
    :param edge_size: Initial edge size.
    :type edge_size: Float
    :param bounding_box: Bounding box for the mesh in the form
        ((x_min, x_max), (y_min, y_max), (z_min, z_max)).
    :type bounding_box: tuple[tuple[Float, Float], tuple[Float, Float], tuple[Float, Float]]
    :param config: Configuration object for DistMesh. Defaulted to default_surface_config().
    :type config: DistMeshConfig, None
    :param kwargs: Additional arguments to be passed to the distance and size functions.
    :type kwargs: dict[str, Any]
    :return: Mesh points and triangulation
    """
    # 0. Define config and tolerance parameters
    if config is None:
        config = default_surface_config()
    eps = config.machine_eps * edge_size
    step_tol = config.step_tol * edge_size
    mesh_tol = config.mesh_tol * edge_size

    # 1. Initialize the points
    grid_x, grid_y, grid_z = np.meshgrid(
        np.arange(bounding_box[0][0], bounding_box[0][1] + eps, edge_size),
        np.arange(bounding_box[1][0], bounding_box[1][1] + eps, edge_size),
        np.arange(bounding_box[2][0], bounding_box[2][1] + eps, edge_size),
    )
    ny, nx, nz = grid_x.shape
    grid_x = np.transpose(grid_x, (1, 0, 2))
    grid_y = np.transpose(grid_y, (1, 0, 2))
    grid_z = np.transpose(grid_z, (1, 0, 2))
    points = np.vstack((grid_x.ravel(), grid_y.ravel(), grid_z.ravel())).T

    # iso-surface is found by the marching-cubes algorithm.
    # The code below is equivalent to the MATLAB isosurface function
    points, triangulation = marching_cubes(
        dist_func(points, **kwargs).reshape((nx, ny, nz)), 0.0
    )
    triangulation = triangulation.astype(np.int32, copy=False)
    points = points.astype(np.float64, copy=False)

    points *= edge_size
    points += np.array(
        [bounding_box[0][0], bounding_box[1][0], bounding_box[2][0]], dtype=np.float64
    )
    tri_conn = TriangleConnectivity(triangulation)

    # Main loop (time steps)
    count = 0
    d_count = 0
    step_change = config.step_tol + 1.0
    mesh_points = np.inf

    bars: Triangulation = np.zeros((2,), dtype=np.int32)

    while step_change > step_tol and count < config.max_iter:
        if np.isnan(points).any():
            message = "NaN detected in points"
            raise ValueError(message)

        count += 1
        step_points = points.copy()  # type: ignore

        # 3. Re-triangulation by the Delaunay algorithm
        if np.amax(np.linalg.norm(points - mesh_points, axis=1)) >= mesh_tol:
            d_count += 1
            mesh_points = points.copy()  # type: ignore
            tri_conn.update_connectivity(points.view(), triangulation.view())

            # 4. Describe each bar by a unique pair of nodes
            bars = triangle_find_edges(triangulation)

        # 5. Move mesh points based on bar lengths L and forces F
        bar_vec = points[bars[:, 0], :] - points[bars[:, 1], :]
        bar_lengths = np.linalg.norm(bar_vec, axis=1).reshape((-1, 1))
        bar_size_vals = size_func(
            0.5 * (points[bars[:, 0], :] + points[bars[:, 1], :]), **kwargs
        )
        desired_lengths = (
            config.internal_pressure
            * bar_size_vals
            * np.sqrt(np.sum(bar_lengths**2) / np.sum(bar_size_vals**2))
        ).reshape((-1, 1))
        force_vectors = (
            np.maximum(desired_lengths - bar_lengths, 0.0) / bar_lengths
        ) * bar_vec
        force_on_bars = np.zeros_like(points)
        apply_force_3d(force_on_bars, force_vectors, bars)
        points += config.euler_step * force_on_bars

        # 6. Bring outside points back to the boundary
        dist = dist_func(points, **kwargs)
        tmp = (
            np.vstack(
                (
                    points[:, 0] + eps,
                    points[:, 1],
                    points[:, 2],
                )
            ).T
        ).astype(np.float64)
        dist_grad_x = (dist_func(tmp, **kwargs) - dist) / eps
        tmp = (
            np.vstack(
                (
                    points[:, 0],
                    points[:, 1] + eps,
                    points[:, 2],
                )
            ).T
        ).astype(np.float64)
        dist_grad_y = (dist_func(tmp, **kwargs) - dist) / eps
        tmp = (
            np.vstack(
                (
                    points[:, 0],
                    points[:, 1],
                    points[:, 2] + eps,
                )
            ).T
        ).astype(np.float64)
        dist_grad_z = (dist_func(tmp, **kwargs) - dist) / eps
        dist_grad = np.vstack((dist_grad_x, dist_grad_y, dist_grad_z)) / (
            dist_grad_x**2 + dist_grad_y**2 + dist_grad_z**2
        )
        points -= (dist * dist_grad).T

        step_change = np.amax(np.linalg.norm(points - step_points, axis=1))

    return points, triangulation
