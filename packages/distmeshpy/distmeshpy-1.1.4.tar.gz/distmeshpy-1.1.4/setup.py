import numpy
import pybind11
from setuptools import Extension, setup


def create_extension(name: str, sources: list[str]) -> None:
    return Extension(
        name,
        sources=sources,
        include_dirs=["distmeshpy/core/src", pybind11.get_include(), numpy.get_include()],
        language="c++",
        extra_compile_args=["-O3", "-march=native", "-std=c++11"],
    )


ext_modules = [
    create_extension(
        "distmeshpy.core._triangle_utils", ["distmeshpy/core/src/triangle_utils.cpp"]
    ),
    create_extension(
        "distmeshpy.core._tetrahedron_utils", ["distmeshpy/core/src/tetrahedron_utils.cpp", "distmeshpy/core/src/triangle_utils.cpp"]
    ),
    create_extension("distmeshpy.core._internal", ["distmeshpy/core/src/internal.cpp"]),
]

setup(ext_modules=ext_modules)
