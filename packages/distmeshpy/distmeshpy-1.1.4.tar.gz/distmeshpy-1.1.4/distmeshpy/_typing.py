from typing import Any, Protocol

from numpy import float32, float64, int32
from numpy.typing import NDArray
from typing_extensions import TypeAlias

Float: TypeAlias = "float | float32 | float64"
Int: TypeAlias = "int | int32"
Array: TypeAlias = NDArray[float64]
Triangulation: TypeAlias = NDArray[int32]


class Function(Protocol):
    def __call__(self, array: Array, **kwargs: dict[str, Any]) -> Array: ...
