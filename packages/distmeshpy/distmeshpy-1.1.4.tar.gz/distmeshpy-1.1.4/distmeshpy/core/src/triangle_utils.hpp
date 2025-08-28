#ifndef TRIANGLE_UTILS_HPP
#define TRIANGLE_UTILS_HPP

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <array>
#include <unordered_map>

namespace py = pybind11;

double _triangle_area(py::array_t<double>, py::array_t<double>,
                      py::array_t<double>);
py::array_t<double> _triangle_area_all(py::array_t<double>, py::array_t<double>,
                                       py::array_t<double>);

py::array_t<double> _triangle_normal(py::array_t<double>, py::array_t<double>,
                                     py::array_t<double>);
py::array_t<double> _triangle_normal_all(py::array_t<double>,
                                         py::array_t<double>,
                                         py::array_t<double>);

double _triangle_quality(py::array_t<double>, py::array_t<double>,
                         py::array_t<double>);
py::array_t<double> _triangle_quality_all(py::array_t<double>,
                                          py::array_t<double>,
                                          py::array_t<double>);

void _triangle_connectivity(py::array_t<int>, py::array_t<int>,
                            py::array_t<int>);

void _triangle_update(py::array_t<double>, py::array_t<int>, py::array_t<int>,
                      py::array_t<int>);

py::array_t<int> _triangle_find_edges(py::array_t<int>);

struct pair_hash {
    using pair_t = typename std::pair<unsigned int, unsigned int>;
    std::size_t operator()(const pair_t &pair) const noexcept;
};
class _TriangleConnectivity {
   private:
    using pair_t = typename std::pair<unsigned int, unsigned int>;
    std::unordered_map<pair_t, pair_t, pair_hash> connectivity_;

   public:
    _TriangleConnectivity(py::array_t<int>);
    void _update_connectivity(py::array_t<double>, py::array_t<int>);
};

#endif  // !TRIANGLE_UTILS_HPP