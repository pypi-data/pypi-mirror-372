#ifndef BASIS_TEST_H
#define BASIS_TEST_H

#include <Eigen/Core>
#include <gtest/gtest.h>

#include "basisSplines/basis.h"
#include "basisSplines/interpolate.h"
#include "basisSplines/math.h"
#include "basisSplines/spline.h"
#include "testBase.h"

namespace BasisSplines {
namespace Internal {
class BasisTest : public TestBase {
protected:
  Eigen::ArrayXd getPointsSubset(double beginValue, double endValue,
                                 double accuracy = 1e-8) const {
    auto beginSubset{
        std::find_if(m_points.begin(), m_points.end(), [&](double point) {
          return std::abs(point - beginValue) <= accuracy;
        })};
    auto endSubset{
        std::find_if(m_points.begin(), m_points.end(), [&](double point) {
          return std::abs(point - endValue) <= accuracy;
        })};

    Eigen::ArrayXd subset(endSubset - beginSubset + 1);
    for (double &value : subset) {
      value = *beginSubset;
      ++beginSubset;
    }

    return subset;
  }

  static Eigen::MatrixXd polyO3(const Eigen::ArrayXd &points) {
    Eigen::MatrixXd values (points.size(), 2);
    values << points.pow(2), points.pow(2);
    return values;
  }

  static Eigen::MatrixXd polyO3Der(const Eigen::ArrayXd &points) {
    Eigen::MatrixXd values (points.size(), 2);
    values << 2 * points, 2 * points;
    return values;
  }

  static Eigen::MatrixXd polyO3Dder(const Eigen::ArrayXd &points) {
    return Eigen::ArrayXXd::Zero(points.size(), 2) + 2;
  }

  static Eigen::MatrixXd polyO3Int(const Eigen::ArrayXd &points) {
    Eigen::MatrixXd values (points.size(), 2);
    values << points.pow(3) / 3, points.pow(3) / 3;
    return values;
  }

  static Eigen::MatrixXd polyO3Iint(const Eigen::ArrayXd &points) {
    Eigen::MatrixXd values (points.size(), 2);
    values << points.pow(4) / 12, points.pow(4) / 12;
    return values;
  }

  // create basis of order 3
  const Eigen::ArrayXd m_knotsO3{
      {0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0}}; /**<< knots of order 3 basis */
  std::shared_ptr<Basis> m_basisO3{
      std::make_shared<Basis>(m_knotsO3, 3)}; /**<< order 3 basis */

  // create order 3 interatpolation
  const Interpolate m_interpolateO3{
      m_basisO3}; /**<< interpolation for order 3 basis */

  // create order 3 spline interpolating order 3 polynomial
  const Spline m_splineO3{
      m_basisO3, m_interpolateO3.fit(&polyO3)}; /**<< spline of order 3 */

  // create order 3 derivative spline
  std::shared_ptr<Basis> m_basisO3Der{std::make_shared<Basis>(
      m_basisO3->orderDecrease())}; /**<< order 3 derivative basis */
  const Interpolate m_interpolateO3Der{
      m_basisO3Der}; /**<< order 3 derivative interpolation */
  Spline m_splineO3Der{
      m_basisO3Der,
      m_interpolateO3Der.fit(&polyO3Der)}; /** order 3 derivative spline */

  // create order 3 second derivative spline
  std::shared_ptr<Basis> m_basisO3Dder{std::make_shared<Basis>(
      m_basisO3Der->orderDecrease())}; /**<< order 3 second derivative basis */
  const Interpolate m_interpolateO3Dder{
      m_basisO3Dder}; /**<< order 3 second derivative interpolation */
  Spline m_splineO3Dder{
      m_basisO3Dder, m_interpolateO3Dder.fit(
                         &polyO3Dder)}; /** order 3 second derivative spline */

  // create order 3 integral spline
  std::shared_ptr<Basis> m_basisO3Int{std::make_shared<Basis>(
      m_basisO3->orderIncrease())}; /**<< order 3 integral basis */
  const Interpolate m_interpolateO3Int{
      m_basisO3Int}; /**<< order 3 integral interpolation */
  Spline m_splineO3Int{
      m_basisO3Int,
      m_interpolateO3Int.fit(&polyO3Int)}; /** order 3 integral spline */

  // create order 3 second integral spline
  std::shared_ptr<Basis> m_basisO3Iint{std::make_shared<Basis>(
      m_basisO3Int->orderIncrease())}; /**<< order 3 integral basis */
  const Interpolate m_interpolateO3Iint{
      m_basisO3Iint}; /**<< order 3 integral interpolation */
  Spline m_splineO3Iint{
      m_basisO3Iint,
      m_interpolateO3Iint.fit(&polyO3Iint)}; /** order 3 integral spline */

  // create basis of order 3
  std::shared_ptr<Basis> m_basisO3Seg3{std::make_shared<Basis>(
      Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.4, 0.6, 0.6, 1.0, 1.0, 1.0}},
      3)}; /**<< order 3 basis */

  const Eigen::ArrayXd m_points{Eigen::ArrayXd::LinSpaced(101, 0.0, 1.0)};

  const double m_scalingFactor {2.0};
};

}; // namespace Internal
}; // namespace BasisSplines

#endif