#ifndef SPLINE_H
#define SPLINE_H

#include <Eigen/Core>
#include <memory>

#include "basisSplines/basis.h"
#include "basisSplines/interpolate.h"

namespace BasisSplines {
/**
 * @brief Polynomial spline in basis form.
 *
 * Represents a multidimensional spline S(t) determined by its coefficients C
 * for a given basis B(t).
 *
 * S(t) = C^T B(t)
 *
 */
class Spline {
public:
  // MARK: public methods
  Spline() = default;

  /**
   * @brief Construct a new spline in basis form from a "basis" spline and the
   * "coefficients". The number of "coefficients" rows must correspond with the
   * "basis" dimensionality.
   *
   * @param basis spline basis.
   * @param coefficients spline coefficients.
   */
  Spline(const std::shared_ptr<Basis> basis,
         const Eigen::MatrixXd &coefficients)
      : m_basis{basis}, m_coefficients{coefficients} {
    assert(coefficients.rows() == basis->dim() &&
           "Coefficients must have same rows as basis dimensionality.");
  }

  /**
   * @brief Get the spline coefficients.
   * The number of rows corresponds with the basis spline dimensionality.
   * The number of columns corresponds with the spline output dimensionality.
   *
   * @return const Eigen::ArrayXd& spline coefficients.
   */
  const Eigen::MatrixXd &getCoefficients() const { return m_coefficients; }

  /**
   * @brief Set the spline coefficients.
   * The coefficients' size must equal the spline's coefficients' size.
   *
   * @param coefficients new spline coefficients.
   */
  void setCoefficients(const Eigen::MatrixXd coefficients) {
    assert(coefficients.rows() == m_coefficients.rows() &&
           "Coefficients must have same rows as spline coefficients.");
    assert(coefficients.cols() == m_coefficients.cols() &&
           "Coefficients must have same columns as spline coefficients.");
    m_coefficients = coefficients;
  }

  /**
   * @brief Get the spline basis.
   *
   * @return const std::shared_ptr<Basis> spline basis.
   */
  const std::shared_ptr<Basis> basis() const { return m_basis; }

  /**
   * @brief Get the spline output dimensionality.
   *
   * @return int spline output dimensionality.
   */
  int dim() const { return m_coefficients.cols(); }

  /**
   * @brief Evaluate spline at given "points".
   * The number of output rows corresponds with the number of "points".
   * The number of output columns corresponds with the spline output
   * dimensionality.
   * [Boo01, def. (51)]
   *
   * @param points evaluation points.
   * @return Eigen::ArrayXd spline function values at "points".
   */
  Eigen::ArrayXXd operator()(const Eigen::ArrayXd &points) const {
    return (m_basis->operator()(points) * m_coefficients);
  }

  /**
   * @brief Create new spline with negated spline coefficients.
   *
   * @return Spline spline with negated spline coefficients.
   */
  Spline operator-() const { return {m_basis, -m_coefficients}; }

  /**
   * @brief Create new spline as derivative of this spline.
   *
   * @param orderDer derivative order.
   * @return Spline as derivative of "orderDer".
   */
  Spline derivative(int orderDer = 1) const {
    assert(orderDer >= 0 && "Derivative order must be positive.");

    // create derivative basis and determine coefficients
    Basis basisNew{};
    Eigen::MatrixXd coeffsNew(
        m_basis->derivative(basisNew, m_coefficients, orderDer));

    // return derivative spline
    return {std::make_shared<Basis>(basisNew), coeffsNew};
  }

  /**
   * @brief Create new spline as integral of this spline.
   *
   * @param orderInt integral order.
   * @return Spline as integral of "orderInt".
   */
  Spline integral(int orderInt = 1) const {
    assert(orderInt >= 0 && "Derivative order must be positive.");

    // create derivative basis and determine coefficients
    Basis basisNew{};
    Eigen::MatrixXd coeffsNew(
        m_basis->integral(basisNew, m_coefficients, orderInt));

    // return derivative spline
    return {std::make_shared<Basis>(basisNew), coeffsNew};
  }

  /**
   * @brief Create new spline as sum of "this" and "other" spline.
   * Combine basis of "this" and "other" splines to create the sum basis.
   * Determine sum coefficients by interpolating the sum of this and other
   * spline.
   *
   * @tparam Interp type of interpolation.
   * @param other right spline summand.
   * @param accScale accepted difference between "this" and "other" splines'
   * basis scaling.
   * @param accBps tolerance for assigning knots to breakpoint.
   * @return Spline representation of spline sum.
   */
  template <typename Interp = Interpolate>
  Spline add(const Spline &other, double accScale = 1e-6,
             double accBps = 1e-6) const {
    // combine this and other basis to new basis
    // new basis order is maximum of this and other basis order
    const std::shared_ptr<Basis> newBasis{std::make_shared<Basis>(
        m_basis->combine(*other.basis().get(),
                         std::max(m_basis->order(), other.basis()->order()),
                         accScale, accBps))};

    // determine coefficients by interpolating sum of this and other spline
    return {newBasis, Interp{newBasis}.fit([&](const Eigen::ArrayXd &points) {
              return Eigen::MatrixXd{(*this)(points) + other(points)};
            })};
  }

  /**
   * @brief Create new spline as product of "this" and "other" spline.
   * Combine basis of "this" and "other" splines to create the product basis.
   * Determine product coefficients by interpolating the product of "this" and
   * "other" spline.
   *
   * @tparam Interp type of interpolation.
   * @param other right product spline.
   * @param accScale accepted difference between "this" and "other" splines'
   * basis scaling.
   * @param accBps tolerance for assigning knots to breakpoint.
   * @return Spline representation of spline product.
   */
  template <typename Interp = Interpolate>
  Spline prod(const Spline &other, double accScale = 1e-6,
              double accBps = 1e-6) const {
    // combine this and other basis to new basis
    // new basis order is sum of this and other basis order - 1
    const std::shared_ptr<Basis> newBasis{std::make_shared<Basis>(
        m_basis->combine(*other.basis().get(),
                         m_basis->order() + other.basis()->order() - 1,
                         accScale, accBps))};

    // determine coefficients by interpolating product of this and other spline
    return {newBasis, Interp{newBasis}.fit([&](const Eigen::ArrayXd &points) {
              return Eigen::MatrixXd{(*this)(points)*other(points)};
            })};
  }

  /**
   * @brief Create new spline including the given and "this" splines' knots.
   * The new spline coincides with "this" spline.
   * The distance between coefficients and spline is decreased.
   * The knot multiplicity must remain smaller than the basis order.
   *
   * @tparam Interp type of interpolation.
   * @param knots knots to insert to this basis' knots.
   * @return Spline new spline including the given knots.
   */
  template <typename Interp = Interpolate>
  Spline insertKnots(const Eigen::ArrayXd &knots) const {
    // create new basis with inserted knot
    const std::shared_ptr<Basis> basis{
        std::make_shared<Basis>(m_basis->insertKnots(knots))};

    // determine new coefficients via interpolation
    return {basis, Interp{basis}.fit([&](const Eigen::ArrayXd &points) {
              return Eigen::MatrixXd{(*this)(points)};
            })};
  }

  /**
   * @brief Create new spline with order increased by "change".
   * The new spline coincides with "this" spline.
   * The distance between coefficients and spline is decreased.
   *
   * @tparam Interp type of interpolation.
   * @param change positive order change.
   * @return Spline new spline with increased order.
   */
  template <typename Interp = Interpolate>
  Spline orderElevation(int change) const {
    assert(change >= 0 && "Order change must be positive.");

    // create new basis with increased order
    const std::shared_ptr<Basis> basis{
        std::make_shared<Basis>(m_basis->orderElevation(change))};

    // determine new coefficients via interpolation
    return {basis, Interp{basis}.fit([&](const Eigen::ArrayXd &points) {
              return Eigen::MatrixXd{(*this)(points)};
            })};
  }

  /**
   * @brief Determine a spline representing the "first" and the "last" segment
   * of "this" spline.
   *
   * @param first index of the first segment.
   * @param last index of the last segment.
   * @return Spline segment spline.
   */
  Spline getSegment(int first, int last) const {
    // determine "begin" and "end" knot iterators of segment
    auto [begin, end] = m_basis->getSegmentKnots(first, last);

    // determine basis representation of segments
    const std::shared_ptr<Basis> basisSeg{
        std::make_shared<Basis>(m_basis->getSegment(begin, end))};

    // determine indices of coefficients of semgnet
    int firstCoeff{static_cast<int>(begin - m_basis->knots().begin())};
    int lastCoeff{static_cast<int>(end - m_basis->knots().begin()) -
                  m_basis->order() - 1};

    // new spline
    return {basisSeg,
            m_coefficients(Eigen::seq(firstCoeff, lastCoeff), Eigen::all)};
  }

  /**
   * @brief Determine spline with knots clamped to spline segment.
   *
   * @tparam Interp type of interpolation.
   * @return Spline clamped spline.
   */
  template <typename Interp = Interpolate> Spline getClamped() const {
    // determine clamped basis
    const std::shared_ptr<Basis> basisClamped{
        std::make_shared<Basis>(m_basis->getClamped())};

    // determine clamped spline coefficients by fitting clamped basis to this
    // spline
    return {basisClamped,
            Interp{basisClamped}.fit([&](const Eigen::MatrixXd &points) {
              return Eigen::MatrixXd{(*this)(points)};
            })};
  }

private:
  // MARK: private properties

  std::shared_ptr<Basis> m_basis{}; /**<< spline basis */
  Eigen::MatrixXd m_coefficients{}; /**<< spline coefficients */
};
}; // namespace BasisSplines

#endif
