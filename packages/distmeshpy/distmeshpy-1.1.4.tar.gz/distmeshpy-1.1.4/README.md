# DistMeshPy

DistMeshPy is a Python implementation of the [DistMesh](http://persson.berkeley.edu/distmesh/) algorithm based on the original MATLAB implementation. 

## Features

- Generate 2D, 3D, and surface meshes with a simple interface.
- Flexible distance functions for custom geometries.
- Robust mesh size control through a size function.
- Backend utility compiled via C++ code.

## Installation

```bash
pip install distmeshpy
```

#### Note: A working C++11 order higher compiler is required. 

## Usage

Here's a quick example of how to generate a 2D mesh:

```python
from distmeshpy import distmesh2d
from distmeshpy.utils import dcircle, huniform

p, t = distmesh2d(
    lambda p: dcircle(p, 0.0, 0.0, 1.0),  # Distance function
    huniform,  # Uniform size function
    0.2,  # Initial edge size
    ((-1.1, 1.1), (-1.1, 1.1)),  # Bounding box
)
```
and the mesh can be plotted via `matplotlib`:
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.triplot(p[:, 0], p[:, 1], t)
ax.set_aspect("equal")
plt.show()
```

For more examples, see the [examples](examples/) directory. 

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

## License

Following the original work, this project is licensed under the GNU General Public License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

DistMeshPy is inspired by the original MATLAB DistMesh implementation by Per-Olof Persson and Gilbert Strang.
