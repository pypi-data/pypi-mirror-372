#ifndef INTERPOLATE_H
#define INTERPOLATE_H

#include <Eigen/Core>
#include <Eigen/Dense>
#include <functional>
#include <memory>

#include "basisSplines/basis.h"

namespace BasisSplines {

/**
 * @brief Determines the spline coefficients for a basis to approximate the
 * given observations.
 *
 */
class Interpolate {
public:
  // MARK: public methods

  /**
   * @brief Construct a new Interpolate for the given Basis.
   *
   * @param basis spline basis.
   */
  Interpolate(const std::shared_ptr<Basis> basis) : m_basis{basis} {};

  /**
   * @brief Determine coefficients that fit a spline function at the given
   * "points" to the given "observations".
   *
   * @tparam DecompositionType type of Eigen matrix decomposition
   * @param observations values to fit the spline function.
   * @param points evaluation points corresponding to the "observations".
   * @return Eigen::MatrixXd spline coefficients fitting the observations.
   */
  template <
      typename DecompositionType = Eigen::ColPivHouseholderQR<Eigen::MatrixXd>>
  Eigen::MatrixXd fit(const Eigen::MatrixXd &observations,
                      const Eigen::VectorXd &points) const {
    return DecompositionType{m_basis->operator()(points)}.solve(observations);
  }

  /**
   * @brief Determine coefficients that fit a spline function at the given
   * "points" and the given "observations". The observations consist of an (n x
   * m)-array with n observations and derivatives until order m - 1.
   *
   * @param observations values and derivatives to fit the spline function.
   * @param points evaluation points corresponding to the "observations".
   * @return Eigen::ArrayXd spline coefficients fitting the observations.
   */
  template <
      typename DecompositionType = Eigen::ColPivHouseholderQR<Eigen::MatrixXd>>
  Eigen::MatrixXd fit(const std::vector<Eigen::MatrixXd> &observations,
                      const std::vector<Eigen::VectorXi> &derivOrders,
                      const Eigen::ArrayXd &points) const {

    // store transformation matrices and spline bases
    std::vector<Eigen::MatrixXd> transforms(m_basis->order() - 1);
    std::vector<Basis> bases(m_basis->order() - 1);

    // initialize transformations and bases with current
    transforms[0] = Eigen::MatrixXd::Identity(m_basis->dim(), m_basis->dim());
    bases[0] = *m_basis;

    // create higher order derivatives based on previous one
    int cOrder{};
    for (int cOrder{1}; cOrder < m_basis->order() - 1; ++cOrder)
      transforms[cOrder] = bases[cOrder - 1].derivative(bases[cOrder], 1);

    // evaluate basis functions at "points" and transform according to given
    // derivartive
    Eigen::MatrixXd basisValues(m_basis->dim(), m_basis->dim());
    int cObs{};
    int cRow{};
    for (const Eigen::MatrixXd &observation : observations) {
      int cValue{};
      for (auto row : observation.rowwise()) {
        basisValues(cRow++, Eigen::all) =
            bases[derivOrders[cObs](cValue)]({{points(cObs)}}) *
            transforms[derivOrders[cObs](cValue)];
        ++cValue;
      }
      ++cObs;
    }

    // arrange observation in array
    Eigen::MatrixXd splineValues(m_basis->dim(), observations[0].cols());
    int cElem{};
    for (const auto &observation : observations)
      for (auto row : observation.rowwise())
        splineValues(cElem++, Eigen::all) = row;

    // solve for spline coefficients
    return DecompositionType{basisValues}.solve(splineValues);
  }

  /**
   * @brief Determine coefficients that fit a spline function to the given
   * process.
   *
   * @param process function representation of the process.
   * @return Eigen::MatrixXd spline coefficients fitting the process.
   */
  Eigen::MatrixXd
  fit(std::function<Eigen::MatrixXd(Eigen::VectorXd)> process) const {
    return fit(process(m_basis->greville()), m_basis->greville());
  }

private:
  // MARK: public properties

  std::shared_ptr<Basis> m_basis; /**<< spline basis */
};
}; // namespace BasisSplines
#endif