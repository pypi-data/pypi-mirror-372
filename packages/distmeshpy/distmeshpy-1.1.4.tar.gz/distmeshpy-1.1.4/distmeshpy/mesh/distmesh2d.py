"""Implementation of the 2D DistMesh algorithm."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial import Delaunay  # type: ignore

from distmeshpy._typing import Array, Float, Function, Triangulation
from distmeshpy.core import apply_force_2d, triangle_find_edges
from distmeshpy.utils.config import DistMeshConfig, default_2d_config


# TODO: add loggers
def distmesh2d(
    dist_func: Function,
    size_func: Function,
    edge_size: Float,
    bounding_box: tuple[tuple[Float, Float], tuple[Float, Float]],
    fixed_points: Array | None = None,
    config: DistMeshConfig | None = None,
    **kwargs: dict[str, Any],
) -> tuple[Array, Triangulation]:
    """
    Generate a 2D triangular mesh using the DistMesh algorithm.

    Mirror function of ``distmesh2d.m`` in the original MATLAB code.

    :param dist_func: Distance function.
    :type dist_func: Function
    :param size_func: Scaled edge length function.
    :type size_func: Function
    :param edge_size: Initial edge size.
    :type edge_size: Float
    :param bounding_box: Bounding box for the mesh in the form
        ((x_min, x_max), (y_min, y_max), (z_min, z_max)).
    :type bounding_box: tuple[tuple[Float, Float], tuple[Float, Float], tuple[Float, Float]]
    :param config: Configuration object for DistMesh. Defaulted to default_2d_config().
    :type config: DistMeshConfig | None
    :param kwargs: Additional arguments to be passed to the distance and size functions.
    :type kwargs: dict[str, Any]
    :return: Mesh points and triangulation
    """
    # 0. Define config and tolerance parameters
    if config is None:
        config = default_2d_config()
    eps = config.machine_eps * edge_size
    geo_eps = config.geometry_eps * edge_size
    step_tol = config.step_tol * edge_size
    mesh_tol = config.mesh_tol * edge_size

    # 1. Initialize the points
    grid_x, grid_y = np.meshgrid(
        np.arange(bounding_box[0][0], bounding_box[0][1] + eps, edge_size),
        np.arange(
            bounding_box[1][0], bounding_box[1][1] + eps, 0.5 * np.sqrt(3) * edge_size
        ),
    )
    grid_x[1::2, :] += 0.5 * edge_size
    points: Array = np.vstack((grid_x.ravel(), grid_y.ravel())).T

    # 2. Remove points outside the boundary
    points = points[np.where(dist_func(points, **kwargs) < geo_eps)[0], :]
    r0 = 1 / size_func(points, **kwargs) ** 2
    rng = np.random.default_rng(seed=kwargs.get("seed"))
    points = points[np.where(rng.uniform(size=points.shape[0]) < r0 / np.max(r0))[0], :]
    n_fix = 0
    if fixed_points is not None:
        fixed_pts = np.unique(fixed_points, axis=0)
        n_fix = fixed_pts.shape[0]
        to_remove = []
        for i in range(fixed_points.shape[0]):
            to_remove += np.where(
                np.all(np.isclose(points, fixed_points[i, :]), axis=1)
            )[0].tolist()
        points = np.delete(points, to_remove, axis=0)
        points = np.vstack((fixed_pts, points))

    # Main loop (time steps)
    count = 0
    d_count = 0
    step_change = config.step_tol + 1.0
    previous_points = np.inf

    bars: Triangulation = np.zeros((2,), dtype=np.int32)
    triangulation: Triangulation = np.zeros((3,), dtype=np.int32)

    while step_change > step_tol and count < config.max_iter:
        count += 1

        # 3. Re-triangulation by the Delaunay algorithm
        if np.amax(np.linalg.norm(points - previous_points, axis=1)) >= mesh_tol:
            d_count += 1
            previous_points = points.copy()  # type: ignore
            tri = Delaunay(points)
            triangulation = tri.simplices.astype(np.int32, copy=False)
            mid_points = np.mean(points[triangulation], axis=1)
            triangulation = triangulation[
                np.where(dist_func(mid_points, **kwargs) < -geo_eps)[0], :
            ]

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

        # Density control. Remove points that are too close to each other
        if count % config.density_ctrl_freq == 0:
            close_bars = desired_lengths > 2 * bar_lengths
            if np.any(close_bars):
                points_to_remove = np.setdiff1d(
                    bars[np.where(close_bars)[0], :].ravel(), np.arange(0, n_fix)
                )
                points = np.delete(points, np.unique(points_to_remove), axis=0)
                previous_points = np.inf  # type: ignore
                continue

        force_vectors = (
            np.maximum(desired_lengths - bar_lengths, 0.0) / bar_lengths
        ) * bar_vec
        force_on_bars = np.zeros_like(points)

        apply_force_2d(force_on_bars, force_vectors, bars)

        force_on_bars[:n_fix, :] = 0.0
        points += config.euler_step * force_on_bars

        # 6. Bring outside points back to the boundary
        dist = dist_func(points, **kwargs)
        out_points = dist > 0
        out_points[:n_fix] = False
        if np.any(out_points):
            tmp = (
                np.vstack(
                    (
                        points[out_points, 0] + eps,
                        points[out_points, 1],
                    )
                ).T
            ).astype(np.float64)
            dist_grad_x = (dist_func(tmp, **kwargs) - dist[out_points]) / eps
            tmp = (
                np.vstack(
                    (
                        points[out_points, 0],
                        points[out_points, 1] + eps,
                    )
                ).T
            ).astype(np.float64)
            dist_grad_y = (dist_func(tmp, **kwargs) - dist[out_points]) / eps
            dist_grad = np.vstack((dist_grad_x, dist_grad_y)) / (
                dist_grad_x**2 + dist_grad_y**2
            )
            points[out_points, :] -= (dist[out_points] * dist_grad).T

        step_change = np.sqrt(config.euler_step) * np.amax(
            np.linalg.norm(force_on_bars[dist < -geo_eps, :], axis=1)
        )

    return points, triangulation
