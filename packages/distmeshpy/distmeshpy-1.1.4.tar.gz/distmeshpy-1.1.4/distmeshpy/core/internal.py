"""Internal utility wrapper functions implemented in C++."""

from distmeshpy._typing import Array, Triangulation

from ._internal import _apply_force_2d, _apply_force_3d


def apply_force_2d(
    force_on_bar: Array, force_vector: Array, bar_index: Triangulation
) -> None:
    """
    Assemble the force vector on the trusses in 2D.

    :param force_on_bar: (Ne, 2) The force vector to assemble.
    :type force_on_bar: np.typing.NDArray[np.float64]
    :param force_vector: (Nb, 2) Force vector on each individual truss.
        Each row corresponds to the row in bar_index.
    :type force_vector: np.typing.NDArray[np.float64]
    :param bar_index: (Nb, 2) The nodal index of each individual truss.
    :type p3: np.typing.NDArray[np.int32]
    """
    _apply_force_2d(force_on_bar, force_vector, bar_index)


def apply_force_3d(
    force_on_bar: Array, force_vector: Array, bar_index: Triangulation
) -> None:
    """
    Assemble the force vector on the trusses in 3D.

    :param force_on_bar: (Ne, 3) The force vector to assemble.
    :type force_on_bar: np.typing.NDArray[np.float64]
    :param force_vector: (Nb, 3) Force vector on each individual truss.
        Each row corresponds to the row in bar_index.
    :type force_vector: np.typing.NDArray[np.float64]
    :param bar_index: (Nb, 2) The nodal index of each individual truss.
    :type p3: np.typing.NDArray[np.int32]
    """
    _apply_force_3d(force_on_bar, force_vector, bar_index)
