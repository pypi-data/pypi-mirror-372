#ifndef BASIS_H
#define BASIS_H

#include <Eigen/Core>
#include <Eigen/Dense>
#include <numeric>
#include <memory>

#include "basisSplines/math.h"

namespace BasisSplines {

class Interpolate;

/**
 * @brief Basis of piecewise polynomial functions represented by truncated
 * powers.
 *
 * The basis is defined by its order and an increasing sequence of knots.
 * It provides properties that are derived from the knots and degree.
 * Allows the combination of two splines bases.
 */
class Basis {
public:
  // MARK: public methods

  Basis() = default;

  /**
   * @brief Construct a new basis for the given "knots", "order", and knot
   * "scale".
   *
   * @param knots knot locations.
   * @param order basis order.
   * @param scale knot scaling factor.
   */
  Basis(const Eigen::ArrayXd &knots, int order, double scale = 1.0)
      : m_knots{knots}, m_order{order}, m_scale{scale} {}

  /**
   * @brief Create a new basis with knots including "knotsIn" and "this" basis
   * knots.
   *
   * @param knotsIn knots to insert to this basis' knots.
   * @return Basis new basis including the given knots.
   */
  Basis insertKnots(const Eigen::ArrayXd &knotsIn) const {
    // concatenate knots with this basis knots
    Eigen::ArrayXd knotsNew(knotsIn.size() + knots().size());
    knotsNew << knotsIn, knots();

    // sort for increasing knot sequence
    std::sort(knotsNew.begin(), knotsNew.end());
    return {knotsNew, order()};
  }

  /**
   * @brief Combine the knots of "this" and another "basis" to new
   * basis of given "order" [Loo+15].
   * The "order" cannot subceed maximum of "this" and other "basis" order.   *
   * The new basis retains the breakpoints of the source bases.
   *
   * @param basis other basis to combine with.
   * @param order result basis order.
   * @param accScale accepted difference between "this" and other "basis"
   * scaling.
   * @param accBps tolerance for assigning knots to breakpoint.
   * @return Eigen::ArrayXd knots as the combination of both bases.
   */
  Basis combine(const Basis &basis, int order, double accScale = 1e-6,
                double accBps = 1e-6) const {
    assert(std::abs(m_scale - basis.getScale()) < accScale &&
           "Only basis with same scale can be combined.");
    assert(order >= std::max(m_order, basis.order()) &&
           "New basis cannot subceed maximum of this and other bases order.");

    // create this and other bases knots considering target order
    Eigen::ArrayXd knotsThis{toKnots(getBreakpoints(accBps), order)};
    Eigen::ArrayXd knotsOther{toKnots(basis.getBreakpoints(accBps), order)};

    // combined knots cannot exceed size of this and other basis knots
    Eigen::ArrayXd knotsComb(knotsThis.size() + knotsOther.size());

    // iterate over both knot arrays
    // compare knots and place smaller one in "knotsComb"
    // auto knotComb {knotsComb.begin()};
    auto knotThis{knotsThis.begin()};
    auto knotOther{knotsOther.begin()};
    int numKnotsComb{};
    for (auto &knotComb : knotsComb) {
      // test if terminal knot of this and other basis are reached
      bool atThisEnd{knotThis == (knotsThis.end())};
      bool atOtherEnd{knotOther == (knotsOther.end())};

      // terminate since all knots are processed
      if (atThisEnd && atOtherEnd)
        break;

      // assign this knot if smaller or other end is reached
      if (*knotThis < *knotOther - accScale && !atThisEnd || atOtherEnd)
        knotComb = *(knotThis++);
      // assign other knot if smaller or other end is reached
      else if (*knotOther < *knotThis - accScale && !atOtherEnd || atThisEnd)
        knotComb = *(knotOther++);
      // asign this and other knot, which are equal
      else {
        knotComb = *knotOther;

        // count other knots since not fully processed
        if (!atOtherEnd)
          ++knotOther;

        // count this knots since not fully processed
        if (!atThisEnd)
          ++knotThis;
      }

      ++numKnotsComb;
    }

    return {knotsComb(Eigen::seqN(0, numKnotsComb)), order};
  }

  /**
   * @brief Determine new basis with order decreased by "change".
   *
   * @param change order to decrease.
   * @return Basis basis with reduced order.
   */
  Basis orderDecrease(int change = 1) const {
    assert(change >= 0 && "Order change must be positive.");

    // base case: no order decrease, create new instance of current basis
    if (change == 0)
      return Basis{*this};

    // create basis of lower order
    return {knots()(Eigen::seqN(change, knots().size() - 2 * change)),
            order() - change};
  }

  /**
   * @brief Determine new basis with order increased by "change". In contrast to
   * Basis::orderElevation the knot multiplicity is preserved except for the
   * first and last knots.
   *
   * @param change order to increase.
   * @return Basis basis with increased order.
   */
  Basis orderIncrease(int change = 1) const {
    assert(change >= 0 && "Order change must be positive.");

    // base case: no order increase, create new instance of current basis
    if (change == 0)
      return Basis{*this};

    // create new knots where the first and last knots are completed according
    // to order change
    Eigen::ArrayXd knotsNew(knots().size() + 2 * change);
    knotsNew << Eigen::ArrayXd::Zero(change) + knots()(0), knots(),
        Eigen::ArrayXd::Zero(change) + *(knots().end() - 1);

    // create basis of higher order
    return {knotsNew, order() + change};
  }

  /**
   * @brief Determine new basis with order increased by "change". In constrast
   * to Basis::orderIncrease the breakpoint continuity is preserved.
   *
   * @param change order to increase.
   * @return Basis basis with increased order.
   */
  Basis orderElevation(int change = 1) const {
    assert(change >= 0 && "Order change must be positive.");

    // base case: no order increase, create new instance of current basis
    if (change == 0)
      return Basis{*this};

    // create new knots with increased multiplicity for higher order basis
    Eigen::ArrayXd knotsNew{toKnots(getBreakpoints(), m_order + change)};

    // create basis of higher order
    return {knotsNew, order() + change};
  }

  /**
   * @brief Dertermines a matrix A to transform the spline coefficients c to
   * derivative coefficients dc.
   *
   * dc = A * c
   *
   * [Boo01, B-spline prop. (viii)]
   *
   * @param basis basis of reduced order.
   * @param orderDer derivative order.
   * @return Eigen::MatrixXd transformation matrix.
   */
  Eigen::MatrixXd derivative(Basis &basis, int orderDer = 1) const {
    assert(orderDer >= 0 && "Derivative order must be positive.");

    if (orderDer == 0) {
      basis = *this;
      return Eigen::MatrixXd::Identity(dim(), dim());
    }

    // determine transformation matrix
    Eigen::MatrixXd transform(Eigen::MatrixXd::Zero(dim() - 1, dim()));
    for (int cRow{}; cRow < transform.rows(); ++cRow) {
      transform(cRow, cRow) = (order() - 1) /
                              (knots()(cRow + 1) - knots()(order() + cRow)) /
                              m_scale;
      transform(cRow, cRow + 1) = -transform(cRow, cRow);
    }

    // provide basis derivative basis with decreased order
    Basis basisDeriv{orderDecrease()};

    // base case order 1 derivative
    if (orderDer == 1) {
      basis = basisDeriv;
      return transform;
    }

    // recursion higher order derivative
    return basisDeriv.derivative(basis, orderDer - 1) * transform;
  };

  /**
   * @brief Transforms the given values, which are basis spline values or
   * coefficients, to the derivative of this basis.
   *
   * [Boo01, B-spline prop. (viii)]
   *
   * @param basis basis of reduced order.
   * @param values basis values or spline coefficients.
   * @param orderDer derivative order.
   * @return Eigen::MatrixXd derivative values.
   */
  Eigen::MatrixXd derivative(Basis &basis, const Eigen::MatrixXd &values,
                             int orderDer = 1) const {
    assert(orderDer >= 0 && "Derivative order must be positive.");

    if (orderDer == 0) {
      basis = *this;
      return values;
    }

    // provide basis derivative basis with decreased order
    Basis basisDeriv{orderDecrease()};

    // values transformed to derivative valuesNew = o * (values_i+1 - values_i)
    // / (k_i+o - k_i+1)
    Eigen::MatrixXd valuesNew(basisDeriv.dim(), values.cols());
    for (int idx{}; idx < valuesNew.rows(); ++idx)
      valuesNew(idx, Eigen::all) =
          (order() - 1) *
          (values(idx + 1, Eigen::all) - values(idx, Eigen::all)) /
          (knots()(idx + order()) - knots()(idx + 1)) / m_scale;

    // base case order 1 derivative
    if (orderDer == 1) {
      basis = basisDeriv;
      return valuesNew;
    }

    // recursion higher order derivative
    return basisDeriv.derivative(basis, valuesNew, orderDer - 1);
  };

  /**
   * @brief Dertermines a matrix A to transform the spline coefficients c to
   * integral coefficients ic.
   *
   * ic = A * c
   *
   * [Boo01, eq. (31)]
   *
   * @param basis basis spline.
   * @param orderInt integral order.
   * @return Eigen::MatrixXd transformation matrix.
   */
  Eigen::MatrixXd integral(Basis &basis, int orderInt = 1) const {
    assert(orderInt >= 0 && "Integral order must be positive.");

    if (orderInt == 0) {
      basis = *this;
      return Eigen::MatrixXd::Identity(dim(), dim());
    }

    // initialize transformation matrix with zeros
    Eigen::MatrixXd transform(Eigen::MatrixXd::Zero(dim() + 1, dim()));

    // fill transformation matrix
    int cCol{};
    for (auto col : transform.colwise()) {
      for (int cRow{cCol + 1}; cRow < transform.rows(); ++cRow) {
        col(cRow) =
            (knots()(order() + cCol) - knots()(cCol)) / order() * m_scale;
      }
      ++cCol;
    }

    // provide basis integral basis with increased order
    Basis basisDeriv{orderIncrease()};

    // base case order 1 integral
    if (orderInt == 1) {
      basis = basisDeriv;
      return transform;
    }

    // recursion higher order integral
    return basisDeriv.integral(basis, orderInt - 1) * transform;
  }

  /**
   * @brief Transforms the given values, which are basis spline values or
   * coefficients, to the integral of this basis.
   *
   * [Boo01, eq. (31)]
   *
   * @param basis basis of increased order.
   * @param values basis values or spline coefficients.
   * @param orderInt integral order.
   * @return Eigen::VectorXd integral values.
   */
  Eigen::MatrixXd integral(Basis &basis, const Eigen::MatrixXd &values,
                           int orderInt = 1) const {
    assert(orderInt >= 0 && "Integral order must be positive.");

    if (orderInt == 0) {
      basis = *this;
      return values;
    }

    // provide basis integral basis with decreased order
    Basis basisInt{orderIncrease()};

    // values transformed to integral valuesNew_i+1 = values_i * (k_i+o -
    // k_i) / o + valuesNew_i
    Eigen::MatrixXd valuesNew{
        Eigen::MatrixXd::Zero(basisInt.dim(), values.cols())};
    for (int idx{}; idx < valuesNew.rows() - 1; ++idx)
      valuesNew(idx + 1, Eigen::all) =
          values(idx, Eigen::all) * (knots()(idx + order()) - knots()(idx)) /
              order() * m_scale +
          valuesNew(idx, Eigen::all);

    // base case order 1 integral
    if (orderInt == 1) {
      basis = basisInt;
      return valuesNew;
    }

    // recursion higher order integral
    return basisInt.integral(basis, valuesNew, orderInt - 1);
  };

  /**
   * @brief Determine transformation matrices Tl and Tr for left and right
   * operand coefficients cl and cr to get sum coefficients cs.
   *
   * cs = Tl * cl + Tr * cr
   *
   * @param basis right operand basis.
   * @param basisOut sum basis.
   * @return std::pair<Eigen::MatrixXd, Eigen::MatrixXd> transformation matrices
   * Tl and Tr.
   */
  template <typename Interp = Interpolate>
  std::pair<Eigen::MatrixXd, Eigen::MatrixXd> add(const Basis &basis,
                                                  Basis &basisOut) const {
    // combine this and other basis to sum basis
    basisOut = combine(basis, std::max(order(), basis.order()));

    // instantiate interpolate with sum basis
    const Interp interp{std::make_shared<Basis>(basisOut)};
    // determine transform for this basis by interpolating the sum basis
    const Eigen::MatrixXd transformThis{interp.fit([&](Eigen::ArrayXd points) {
      Eigen::ArrayXXd values{(*this)(points)};
      return values;
    })};
    // determine transform for other basis by interpolating the sum basis
    const Eigen::MatrixXd transformOther{interp.fit([&](Eigen::ArrayXd points) {
      Eigen::ArrayXXd values{basis(points)};
      return values;
    })};

    return {transformThis, transformOther};
  }

  /**
   * @brief Determine transformation matrixT for coefficients cl and cr to get
   * product coefficients cs.
   *
   * cs = T (cl \kron cr)
   *
   * @param basis right operand basis.
   * @param basisOut product basis.
   * @return Eigen::MatrixXd transformation matrix T.
   */
  template <typename Interp = Interpolate>
  Eigen::MatrixXd prod(const Basis &basis, Basis &basisOut) const {
    // combine this and other basis to sum basis
    basisOut = combine(basis, order() + basis.order() - 1);

    // instantiate interpolate with sum basis
    const Interp interp{std::make_shared<Basis>(basisOut)};
    // determine transform for this basis by interpolating the sum basis
    const Eigen::MatrixXd transformThis{interp.fit([&](Eigen::ArrayXd points) {
      Eigen::ArrayXXd values{khatriRao((*this)(points), basis(points))};
      return values;
    })};

    return transformThis;
  }

  /**
   * @brief Determine basis dimensionality.
   *
   * @return int basis dimensionality.
   */
  int dim() const { return m_knots.size() - m_order; }

  /**
   * @brief Determine basis order.
   *
   * @return int basis order.
   */
  int order() const { return m_order; }

  /**
   * @brief Determine basis knots.
   *
   * @return const Eigen::ArrayXd& basis knots.
   */
  const Eigen::ArrayXd &knots() const { return m_knots; }

  /**
   * @brief Set breakpoints at given breakpoint indices.
   *
   * @param breakpointsNew new breakpoints.
   * @param idcs breakpoint indices to set.
   */
  void setBreakpoints(const Eigen::ArrayXd &breakpointsNew,
                      const Eigen::ArrayXi &idcs) {
    auto [breakpoints, conts] = getBreakpoints();

    breakpoints(idcs) = breakpointsNew;

    if (!checkIncreasing(breakpoints))
      throw std::invalid_argument(
          "Breakpoints not aranged in strictly increasing order.");

    m_knots = toKnots({breakpoints, conts}, m_order);
  }

  /**
   * @brief Determine basis breakpoints and continuities at breakpoints.
   *
   * @param accuracy tolerance for assigning knots to breakpoint.
   * @return std::pair<Eigen::ArrayXd, Eigen::ArrayXi> breakpoints and
   * continuities.
   */
  std::pair<Eigen::ArrayXd, Eigen::ArrayXi>
  getBreakpoints(double accuracy = 1e-6) const {
    return toBreakpoints(m_knots, m_order, accuracy);
  }

  /**
   * @brief Get the basis scaling factor.
   *
   * @return double scaling fator.
   */
  double getScale() const { return m_scale; }

  /**
   * @brief Set the basis scaling factor.
   *
   * @param scale scaling fator.
   */
  void setScale(double scale) { m_scale = scale; }

  /**
   * @brief Evaluate the truncated power basis at the given "points".
   * The basis values are computed iteratively using lower order evaluations
   * [Boo01, B-spline prop. (i)] for each point.
   *
   *
   * @param points evaluation points.
   * @param accBps minimum distance between breakpoints.
   * @param accSegment accuracy point assignment to knot segment for order 1
   * basis values.
   * @return Eigen::ArrayXd values of truncated powers with "points.size()" rows
   * and "self->dim()" columns.
   */
  Eigen::MatrixXd operator()(const Eigen::ArrayXd &points, double accBps = 1e-6,
                             double accSegment = 1e-6) const {
    // stores evaluation of truncated powers at given points
    Eigen::MatrixXd basisValues{Eigen::MatrixXd::Zero(points.size(), dim())};

    // evaluate trunctated powers for each point
    int cPoint{};
    for (double point : points) {
      // each VectorXd stores values of bases of increasing order
      std::vector<Eigen::VectorXd> basesValues(m_order);

      // evaluate basis of order 1 which is eiter 1.0 or 0.0
      basesValues[0].resize(m_knots.size() - 1);
      for (int cKnot{}; cKnot < m_knots.size() - 1; ++cKnot)
        basesValues[0](cKnot) =
            inKnotSeg(m_knots(cKnot), m_knots(cKnot + 1), point, accSegment)
                ? 1.0
                : 0.0;

      // evaluate bases of order > 1 in ascending order
      for (int cOrder{2}; cOrder <= m_order; ++cOrder) {
        // get basis values of next higher order as weighted sum of neighboring
        // basis values
        for (int cKnot{}; cKnot < m_knots.size() - cOrder; ++cKnot) {
          // determine basis weight based on current knot
          const double denumCurr{m_knots(cKnot + cOrder - 1) - m_knots(cKnot)};
          const double weightCurr{std::abs(denumCurr) > accBps
                                      ? (point - m_knots(cKnot)) / denumCurr
                                      : 0.0};

          // determine basis weight based on next knot
          const double denumNext{m_knots(cKnot + cOrder) - m_knots(cKnot + 1)};
          const double weightNext{std::abs(denumNext) > accBps
                                      ? (m_knots(cKnot + cOrder) - point) /
                                            denumNext
                                      : 0.0};

          // basis value of higher order
          basesValues[cOrder - 1].resize(m_knots.size() - cOrder);
          basesValues[cOrder - 1](cKnot) =
              weightCurr * basesValues[cOrder - 2](cKnot) +
              weightNext * basesValues[cOrder - 2](cKnot + 1);
        }
      }

      // store maximum order basis values for current point
      basisValues(cPoint++, Eigen::seqN(0, dim())) =
          basesValues[m_order - 1](Eigen::seqN(0, dim()));
    }

    return basisValues;
  }

  /**
   * @brief Determine the Greville sites representing the knot averages [Boo01,
   * prop. (v)].
   *
   * @return Eigen::ArrayXd greville sites.
   */
  Eigen::ArrayXd greville() const {
    // basis order 1 greville abs. coincide with knots
    if (m_order == 1)
      return m_knots;

    // higher order basis knot averages
    Eigen::ArrayXd grevilleSites(dim());

    // assign greville sites as mean accumulation over knots
    for (int cKnot{}; cKnot < dim(); ++cKnot) {
      auto begin{m_knots.begin() + cKnot + 1};
      auto end{begin + m_order - 1};
      grevilleSites(cKnot) = std::accumulate(begin, end, 0.0) / (m_order - 1);
    }

    return grevilleSites;
  }

  /**
   * @brief Determine a basis representing the "first" to the "last" segment of
   * "this" basis.
   *
   * @param first index of the first segment.
   * @param last index of the last segment.
   * @return Basis segment basis.
   */
  Basis getSegment(int first, int last) const {
    // find first and last knots of the given segments
    auto [begin, end] = getSegmentKnots(first, last);
    return getSegment(begin, end);
  }

  /**
   * @brief Determine a basis representing the segment marked by "begin" and
   * "end" of this basis knots.
   *
   * @param begin iterator pointing to the first knot of a segment.
   * @param end iterator pointing to the last knot of a segment.
   * @return Basis segment basis.
   */
  Basis getSegment(
      Eigen::internal::pointer_based_stl_iterator<const Eigen::ArrayXd> begin,
      Eigen::internal::pointer_based_stl_iterator<const Eigen::ArrayXd> end)
      const {
    // copy knots to new variable
    Eigen::ArrayXd knots(end - begin);
    int cElem{};
    for (; begin < end; ++begin)
      knots(cElem++) = *begin;

    return {knots, m_order};
  }

  /**
   * @brief Determine iterators pointing to the begin and end of knots
   * corresponding to the "first" to the "last" segment of "this" basis.
   *
   * @param first index of the first segment.
   * @param last index of the last segment.
   * @return std::pair<Eigen::internal::pointer_based_stl_iterator<const
   * Eigen::ArrayXd>, Eigen::internal::pointer_based_stl_iterator<const
   * Eigen::ArrayXd>> Iterators pointing to the begin and end of a knot
   * sequence.
   */
  std::pair<Eigen::internal::pointer_based_stl_iterator<const Eigen::ArrayXd>,
            Eigen::internal::pointer_based_stl_iterator<const Eigen::ArrayXd>>
  getSegmentKnots(int first, int last) const {
    // store breakpoints to avoid recomputation
    const auto breakpoints{getBreakpoints()};

    // find first and last knots of the given segments
    auto end{
        std::find(m_knots.begin(), m_knots.end(), breakpoints.first(last + 1)) +
        m_order};
    auto begin{(std::find(std::make_reverse_iterator(m_knots.end()),
                          std::make_reverse_iterator(m_knots.begin()),
                          breakpoints.first(first)))
                   .base() -
               m_order};

    return {begin, end};
  }

  /**
   * @brief Determine basis with knots clamped to basis segment.
   *
   * @return Basis clamped basis.
   */
  Basis getClamped() const {
    // later clamped basis knots
    Eigen::ArrayXd knots{m_knots};

    // first m_order knots clamped to segment start
    knots(Eigen::seqN(0, m_order)) = knots(m_order - 1);

    // last m_order knots clamped to segment end
    knots(Eigen::seqN(knots.size() - m_order, m_order)) =
        knots(knots.size() - m_order);

    return {knots, m_order};
  }

  // MARK: public statics

  /**
   * @brief Map "breakpoints" and "continuities" to knots [Boo01, th. (44)].
   *
   * @param breakpoints breakpoints mapped to knots.
   * @param continuities breakpoint continuities.
   * @param order basis order.
   * @return Eigen::ArrayXd knot representation of given breakpoints.
   */
  static Eigen::ArrayXd toKnots(const Eigen::ArrayXd &breakpoints,
                                const Eigen::ArrayXi &continuities, int order) {
    // instantiate counters for breakpoint knot multiplicity
    Eigen::ArrayXi mults{order - continuities};
    // instantiate knot result array
    Eigen::ArrayXd knots(breakpoints.size() * order - continuities.sum());

    // assign knots according to breakpoints and their multiplicity
    auto mult{mults.begin()};
    auto bp{breakpoints.begin()};
    for (double &knot : knots) {
      knot = *bp;
      --(*mult);
      if (*mult == 0) {
        ++mult;
        ++bp;
      }
    }

    return knots;
  }

  /**
   * @brief Map a pair of breakpoints and continuities to knots [Boo01, th.
   * (44)].
   *
   * @param breakpoints pair of breakpoints and continuties
   * @param order basis order.
   * @return Eigen::ArrayXd
   */
  static Eigen::ArrayXd
  toKnots(const std::pair<Eigen::ArrayXd, Eigen::ArrayXi> &breakpoints,
          int order) {
    return toKnots(breakpoints.first, breakpoints.second, order);
  }

  /**
   * @brief Map "knots" to breakpoints and their order of continuity [Boo01, th.
   * (44)]. Map all knots in [breakpoint, breakpoint + "accuracy"] to the same
   * breakpoint.
   *
   * @param knots query points mapped to breakpoints.
   * @param order basis order.
   * @param accuracy tolerance for assigning knots to breakpoint.
   * @return std::pair<Eigen::ArrayXd, Eigen::ArrayXi> breakpoints and their
   * continuities.
   */
  static std::pair<Eigen::ArrayXd, Eigen::ArrayXi>
  toBreakpoints(const Eigen::ArrayXd &knots, int order,
                double accuracy = 1e-6) {
    // instantiate breakpoints, which cannot exceed the number of breakpoints
    Eigen::ArrayXd breakpoints(knots.size());
    // first breakpoint must equal first knot
    breakpoints(0) = knots(0);

    // instantiate breakpoint continuities
    Eigen::ArrayXi continuities{Eigen::ArrayXi::Zero(knots.size()) + order};
    // reduce first breakpoint continuity since it corresponds to first knot
    --continuities(0);

    // assign knots to breakpoints and reduce continuity per assigned knot
    int idxBps{};
    auto knot{knots.begin() + 1};
    for (; knot != knots.end(); ++knot) {
      // assign knot to breakpoint if in accuracy
      if (*knot > breakpoints(idxBps) + accuracy)
        breakpoints(++idxBps) = *knot;
      --continuities(idxBps);
    }

    // return visited breakpoints and continuities
    return {breakpoints(Eigen::seqN(0, idxBps + 1)),
            continuities(Eigen::seqN(0, idxBps + 1))};
  }

private:
  // MARK: private properties

  Eigen::ArrayXd m_knots; /**<< basis knots m_knots(i) <= m_knots(i+1) */
  int m_order{};          /**<< basis order = degree - 1 */
  double m_scale{};       /**<< scaling factor for m_knots */

  // MARK: private methods

  /**
   * @brief Test if "point" is in a knot segment ["knotL" - "accPoint", "knotR"
   * + "accPoint"].
   *
   * @param knotL left knot of the knot segment.
   * @param knotR right knot of the knot segment.
   * @param point query point.
   * @param accPoint accuracy assigning "point" to segment.
   * @param accKnot accuracy for distinguishing "knotL" and "knotR".
   * @return true "point" is in knot segment.
   * @return false "point" is not in knot segment.
   */
  bool inKnotSeg(double knotL, double knotR, double point,
                 double accPoint = 1e-6, double accKnot = 1e-6) const {

    const bool knotlEqsFirst{std::abs(knotL - m_knots(0)) <= accKnot};
    const bool knotrEqsLast{std::abs(knotR - m_knots(m_knots.size() - 1)) <=
                            accKnot};

    if (knotlEqsFirst && knotrEqsLast)
      return point > knotL - accPoint && point <= knotR + accPoint;
    else if (knotlEqsFirst)
      return point >= knotL - accPoint && point <= knotR;
    else if (knotrEqsLast)
      return point > knotL && point <= knotR + accPoint;
    return point > knotL && point <= knotR;
  }

  // MARK: private statics

  /**
   * @brief Test if the given sequence is strictly increasing.
   *
   * @param sequence sequence to check for monotonicity.
   * @return true sequence is strictly increasing.
   * @return false sequence is not strictly increasing.
   */
  static bool checkIncreasing(const Eigen::ArrayXd &sequence) {
    for (auto elemPtr{sequence.begin() + 1}; elemPtr < sequence.end();
         ++elemPtr)
      if (*elemPtr - *(elemPtr - 1) < 0)
        return false;
    return true;
  }
};
}; // namespace BasisSplines

#endif