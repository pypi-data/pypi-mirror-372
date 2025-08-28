"""Predefined distance functions."""

import numpy as np

from distmeshpy._typing import Array, Float


def drectangle(p: Array, x1: Float, x2: Float, y1: Float, y2: Float) -> Array:
    """
    Evaluate the signed distance from a rectangle.

    :param p: (N, 2) The points to evaluate the signed distance at.
    :type p: Array
    :param x1: The x-coordinate of the left edge of the rectangle.
    :type x1: Float
    :param x2: The x-coordinate of the right edge of the rectangle.
    :type x2: Float
    :param y1: The y-coordinate of the bottom edge of the rectangle.
    :type y1: Float
    :param y2: The y-coordinate of the top edge of the rectangle.
    :type y2: Float
    :return: The signed distance from the rectangle.
    :rtype: Array
    """
    return -np.min(
        np.vstack((-y1 + p[:, 1], y2 - p[:, 1], -x1 + p[:, 0], x2 - p[:, 0])), axis=0
    )


def dcircle(p: Array, x0: Float, y0: Float, r: Float) -> Array:
    """
    Evaluate the signed distance from a circle.

    :param p: (N, 2) The points to evaluate the signed distance at.
    :type p: Array
    :param x0: The x-coordinate of the center of the circle.
    :type x0: Float
    :param y0: The y-coordinate of the center of the circle.
    :type y0: Float
    :param r: The radius of the circle.
    :type r: Float
    :return: The signed distance from the circle.
    :rtype: Array
    """
    return np.sqrt((p[:, 0] - x0) ** 2 + (p[:, 1] - y0) ** 2) - r


def ddiff(d1: Array, d2: Array) -> Array:
    """
    Evaluate the signed distance from the difference of two shapes.

    :param d1: The signed distance from the first shape (removed from).
    :type d1: Array
    :param d2: The signed distance from the second shape (to remove).
    :type d2: Array
    :return: The signed distance from the difference of the two shapes.
    :rtype: Array
    """
    return np.maximum(d1, -d2)


def dunion(d1: Array, d2: Array) -> Array:
    """
    Evaluate the signed distance from the union of two shapes.

    :param d1: The signed distance from the first shape.
    :type d1: Array
    :param d2: The signed distance from the second shape.
    :type d2: Array
    :return: The signed distance from the union of the two shapes.
    :rtype: Array
    """
    return np.minimum(d1, d2)


def dintersect(d1: Array, d2: Array) -> Array:
    """
    Evaluate the signed distance from the intersection of two shapes.

    :param d1: The signed distance from the first shape.
    :type d1: Array
    :param d2: The signed distance from the second shape.
    :type d2: Array
    :return: The signed distance from the intersection of the two shapes.
    :rtype: Array
    """
    return np.maximum(d1, d2)


def dsphere(p: Array, xc: Float, yc: Float, zc: Float, r: Float) -> Array:
    """
    Evaluate the signed distance from a sphere.

    :param p: (N, 3) The points to evaluate the signed distance at.
    :type p: Array
    :param xc: The x-coordinate of the center of the sphere.
    :type xc: Float
    :param yc: The y-coordinate of the center of the sphere.
    :type yc: Float
    :param zc: The z-coordinate of the center of the sphere.
    :type zc: Float
    :param r: The radius of the sphere.
    :type r: Float
    :return: The signed distance from the sphere.
    :rtype: Array
    """
    return np.sqrt((p[:, 0] - xc) ** 2 + (p[:, 1] - yc) ** 2 + (p[:, 2] - zc) ** 2) - r
