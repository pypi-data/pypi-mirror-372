
#include "basisSplines/basis.h"
#include "basisSplines/interpolate.h"
#include "basisSplines/spline.h"

#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace BasisSplines {
using namespace pybind11::literals;

PYBIND11_MODULE(_core, handle) {
  py::classh<Basis>(handle, "Basis", R"doc(
Basis of piecewise polynomial functions represented by truncated powers.

The basis is defined by its order and an increasing sequence of knots.
It provides properties that are derived from the knots and degree.
Allows the combination of two splines bases.
)doc")
      .def(py::init<>(), R"doc(Default constructor for an empty basis.)doc")
      .def(
          py::init<Eigen::ArrayXd, int, double>(), "knots"_a, "order"_a,
          "scale"_a = 1.0,
          R"doc(Construct a new basis for the given knots, order, and knot scale.

Args:
     knots (np.ndarray): Knot locations.
     order (int): Basis order.
     scale (float, optional): Knot scaling factor. Default is 1.0.
)doc")
      .def(
          "insertKnots", &Basis::insertKnots, "knotsIn"_a,
          R"doc(Create a new basis with knots including knotsIn and this basis knots.

Args:
     knotsIn (np.ndarray): Knots to insert to this basis' knots.
Returns:
     Basis: New basis including the given knots.
)doc")
      .def(
          "combine", &Basis::combine, "basis"_a, "order"_a, "accScale"_a = 1e-6,
          "accBps"_a = 1e-6,
          R"doc(Combine the knots of this and another basis to new basis of given order.

Args:
     basis (Basis): Other basis to combine with.
     order (int): Result basis order.
     accScale (float, optional): Accepted difference between this and other basis scaling.
     accBps (float, optional): Tolerance for assigning knots to breakpoint.
Returns:
     Basis: Combined basis.
)doc")
      .def("orderDecrease", &Basis::orderDecrease, "change"_a = 1,
           R"doc(Determine new basis with order decreased by change.

Args:
     change (int, optional): Order to decrease. Default is 1.
Returns:
     Basis: Basis with reduced order.
)doc")
      .def("orderIncrease", &Basis::orderIncrease, "change"_a = 1,
           R"doc(Determine new basis with order increased by change.

Args:
     change (int, optional): Order to increase. Default is 1.
Returns:
     Basis: Basis with increased order.
)doc")
      .def(
          "orderElevation", &Basis::orderElevation, "change"_a = 1,
          R"doc(Determine new basis with order increased by change, preserving breakpoint continuity.

Args:
     change (int, optional): Order to increase. Default is 1.
Returns:
     Basis: Basis with increased order.
)doc")
      .def(
          "derivative",
          py::overload_cast<Basis &, int>(&Basis::derivative, py::const_),
          "basis"_a, "orderDer"_a = 1,
          R"doc(Determines a matrix to transform the spline coefficients to derivative coefficients.

Args:
     basis (Basis): Basis of reduced order.
     orderDer (int, optional): Derivative order. Default is 1.
Returns:
     np.ndarray: Transformation matrix.
)doc")
      .def("derivative",
           py::overload_cast<Basis &, const Eigen::MatrixXd &, int>(
               &Basis::derivative, py::const_),
           "basis"_a, "values"_a, "orderDer"_a = 1,
           R"doc(Transforms the given values to the derivative of this basis.

Args:
     basis (Basis): Basis of reduced order.
     values (np.ndarray): Basis values or spline coefficients.
     orderDer (int, optional): Derivative order. Default is 1.
Returns:
     np.ndarray: Derivative values.
)doc")
      .def(
          "integral",
          py::overload_cast<Basis &, int>(&Basis::integral, py::const_),
          "basis"_a, "orderInt"_a = 1,
          R"doc(Determines a matrix to transform the spline coefficients to integral coefficients.

Args:
     basis (Basis): Basis spline.
     orderInt (int, optional): Integral order. Default is 1.
Returns:
     np.ndarray: Transformation matrix.
)doc")
      .def("integral",
           py::overload_cast<Basis &, const Eigen::MatrixXd &, int>(
               &Basis::integral, py::const_),
           "basis"_a, "values"_a, "orderInt"_a = 1,
           R"doc(Transforms the given values to the integral of this basis.

Args:
     basis (Basis): Basis of increased order.
     values (np.ndarray): Basis values or spline coefficients.
     orderInt (int, optional): Integral order. Default is 1.
Returns:
     np.ndarray: Integral values.
)doc")
      .def(
          "add", &Basis::add<Interpolate>, "basis"_a, "basisOut"_a,
          R"doc(Determine transformation matrices for left and right operand coefficients to get sum coefficients.

Args:
     basis (Basis): Right operand basis.
     basisOut (Basis): Sum basis.
Returns:
     Tuple[np.ndarray, np.ndarray]: Transformation matrices Tl and Tr.
)doc")
      .def(
          "prod", &Basis::prod<Interpolate>, "basis"_a, "basisOut"_a,
          R"doc(Determine transformation matrix for coefficients to get product coefficients.

Args:
     basis (Basis): Right operand basis.
     basisOut (Basis): Product basis.
Returns:
     np.ndarray: Transformation matrix T.
)doc")
      .def("dim", &Basis::dim,
           R"doc(Determine basis dimensionality.

Returns:
     int: Basis dimensionality.
)doc")
      .def("order", &Basis::order,
           R"doc(Determine basis order.

Returns:
     int: Basis order.
)doc")
      .def("knots", &Basis::knots, py::return_value_policy::reference_internal,
           R"doc(Determine basis knots.

Returns:
     np.ndarray: Basis knots.
)doc")
      .def("setBreakpoints", &Basis::setBreakpoints, "breakpointsNew"_a,
           "idcs"_a,
           R"doc(Set breakpoints at given breakpoint indices.

Args:
     breakpointsNew (np.ndarray): New breakpoints.
     idcs (np.ndarray): Breakpoint indices to set.
)doc")
      .def("getBreakpoints", &Basis::getBreakpoints, "accuracy"_a = 1e-6,
           R"doc(Determine basis breakpoints and continuities at breakpoints.

Args:
     accuracy (float, optional): Tolerance for assigning knots to breakpoint. Default is 1e-6.
Returns:
     Tuple[np.ndarray, np.ndarray]: Breakpoints and continuities.
)doc")
      .def("getScale", &Basis::getScale,
           R"doc(Get the basis scaling factor.

Returns:
     float: Scaling factor.
)doc")
      .def("setScale", &Basis::setScale, "scale"_a,
           R"doc(Set the basis scaling factor.

Args:
     scale (float): Scaling factor.
)doc")
      .def("__call__", &Basis::operator(), "points"_a, "accBps"_a = 1e-6,
           "accSegment"_a = 1e-6,
           R"doc(Evaluate the truncated power basis at the given points.

Args:
     points (np.ndarray): Evaluation points.
     accBps (float, optional): Minimum distance between breakpoints. Default is 1e-6.
     accSegment (float, optional): Accuracy point assignment to knot segment for order 1 basis values. Default is 1e-6.
Returns:
     np.ndarray: Values of truncated powers with points.size rows and self.dim columns.
)doc")
      .def("greville", &Basis::greville,
           R"doc(Determine the Greville sites representing the knot averages.

Returns:
     np.ndarray: Greville sites.
)doc")
      .def(
          "getSegment",
          py::overload_cast<int, int>(&Basis::getSegment, py::const_),
          R"doc(Determine a basis representing the first to the last segment of this basis.

Args:
     first (int): Index of the first segment.
     last (int): Index of the last segment.
Returns:
     Basis: Segment basis.
)doc")
      .def("getClamped", &Basis::getClamped,
           R"doc(Determine basis with knots clamped to basis segment.

Returns:
     Basis: Clamped basis.
)doc")
      .def_static(
          "toKnots",
          py::overload_cast<const Eigen::ArrayXd &, const Eigen::ArrayXi &,
                            int>(&Basis::toKnots),
          "breakpoints"_a, "continuities"_a, "order"_a,
          R"doc(Map breakpoints and continuities to knots.

Args:
     breakpoints (np.ndarray): Breakpoints mapped to knots.
     continuities (np.ndarray): Breakpoint continuities.
     order (int): Basis order.
Returns:
     np.ndarray: Knot representation of given breakpoints.
)doc")
      .def_static(
          "toKnots",
          py::overload_cast<const std::pair<Eigen::ArrayXd, Eigen::ArrayXi> &,
                            int>(&Basis::toKnots),
          "breakpoints"_a, "order"_a,
          R"doc(Map a pair of breakpoints and continuities to knots.

Args:
     breakpoints (Tuple[np.ndarray, np.ndarray]): Pair of breakpoints and continuities.
     order (int): Basis order.
Returns:
     np.ndarray: Knot representation.
)doc")
      .def_static("toBreakpoints", &Basis::toBreakpoints, "knots"_a, "order"_a,
                  "accuracy"_a = 1e-6,
                  R"doc(Map knots to breakpoints and their order of continuity.

Args:
     knots (np.ndarray): Query points mapped to breakpoints.
     order (int): Basis order.
     accuracy (float, optional): Tolerance for assigning knots to breakpoint. Default is 1e-6.
Returns:
     Tuple[np.ndarray, np.ndarray]: Breakpoints and their continuities.
)doc");

  py::classh<Spline>(handle, "Spline", R"doc(
Polynomial spline in basis form.

Represents a multidimensional spline S(t) determined by its coefficients C for a given basis B(t).

S(t) = C^T B(t)
)doc")
      .def(py::init<>(), R"doc(Default constructor for an empty spline.)doc")
      .def(
          py::init<const std::shared_ptr<Basis>, const Eigen::MatrixXd &>(),
          "basis"_a, "coefficients"_a,
          R"doc(Construct a new spline in basis form from a basis and coefficients.

Args:
     basis (Basis): Spline basis.
     coefficients (np.ndarray): Spline coefficients. Number of rows must correspond with basis dimensionality.
)doc")
      .def("getCoefficients", &Spline::getCoefficients,
           py::return_value_policy::reference_internal,
           R"doc(Get the spline coefficients.

Returns:
     np.ndarray: Spline coefficients. Rows correspond with basis dimensionality, columns with output dimensionality.
)doc")
      .def("setCoefficients", &Spline::setCoefficients, "coefficients"_a,
           R"doc(Set the spline coefficients.

Args:
     coefficients (np.ndarray): New spline coefficients. Must match shape of current coefficients.
)doc")
      .def("basis", &Spline::basis, py::return_value_policy::reference_internal,
           R"doc(Get the spline basis.

Returns:
     Basis: Spline basis.
)doc")
      .def("dim", &Spline::dim,
           R"doc(Get the spline output dimensionality.

Returns:
     int: Spline output dimensionality.
)doc")
      .def("__call__", &Spline::operator(), "points"_a,
           R"doc(Evaluate spline at given points.

Args:
     points (np.ndarray): Evaluation points.
Returns:
     np.ndarray: Spline function values at points. Rows = number of points, columns = output dimensionality.
)doc")
      .def("derivative", &Spline::derivative, "orderDer"_a = 1,
           R"doc(Create new spline as derivative of this spline.

Args:
     orderDer (int, optional): Derivative order. Default is 1.
Returns:
     Spline: Derivative spline.
)doc")
      .def("integral", &Spline::integral, "orderInt"_a = 1,
           R"doc(Create new spline as integral of this spline.

Args:
     orderInt (int, optional): Integral order. Default is 1.
Returns:
     Spline: Integral spline.
)doc")
      .def("add", &Spline::add<Interpolate>, "other"_a, "accScale"_a = 1e-6,
           "accBps"_a = 1e-6,
           R"doc(Create new spline as sum of this and other spline.

Args:
     other (Spline): Right spline summand.
     accScale (float, optional): Accepted difference between this and other splines' basis scaling. Default is 1e-6.
     accBps (float, optional): Tolerance for assigning knots to breakpoint. Default is 1e-6.
Returns:
     Spline: Spline sum.
)doc")
      .def("prod", &Spline::prod<Interpolate>, "other"_a, "accScale"_a = 1e-6,
           "accBps"_a = 1e-6,
           R"doc(Create new spline as product of this and other spline.

Args:
     other (Spline): Right product spline.
     accScale (float, optional): Accepted difference between this and other splines' basis scaling. Default is 1e-6.
     accBps (float, optional): Tolerance for assigning knots to breakpoint. Default is 1e-6.
Returns:
     Spline: Spline product.
)doc")
      .def("insertKnots", &Spline::insertKnots<Interpolate>, "knots"_a,
           R"doc(Create new spline including the given and this splines' knots.

Args:
     knots (np.ndarray): Knots to insert to this basis' knots.
Returns:
     Spline: New spline including the given knots.
)doc")
      .def("orderElevation", &Spline::orderElevation<Interpolate>, "change"_a,
           R"doc(Create new spline with order increased by change.

Args:
     change (int): Positive order change.
Returns:
     Spline: New spline with increased order.
)doc")
      .def(
          "getSegment", &Spline::getSegment, "first"_a, "last"_a,
          R"doc(Determine a spline representing the first and the last segment of this spline.

Args:
     first (int): Index of the first segment.
     last (int): Index of the last segment.
Returns:
     Spline: Segment spline.
)doc")
      .def("getClamped", &Spline::getClamped<Interpolate>,
           R"doc(Determine spline with knots clamped to spline segment.

Returns:
     Spline: Clamped spline.
)doc")
      .def("__neg__", &Spline::operator-,
           R"doc(Create new spline with negated spline coefficients.

Returns:
     Spline: Spline with negated coefficients.
)doc");
}
} // namespace BasisSplines