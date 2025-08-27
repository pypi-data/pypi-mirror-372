#include <Eigen/Core>
#include <gtest/gtest.h>

#include "basisSplines/basis.h"
#include "basisSplines/interpolate.h"
#include "basisSplines/spline.h"
#include "testBase.h"

namespace BasisSplines {
namespace Internal {
class InterpolateTest : public TestBase {
protected:
  void SetUp() {}

  const Eigen::ArrayXd m_knotsO2{{0.0, 0.0, 0.5, 1.0, 1.0}};
  std::shared_ptr<Basis> m_basisO2{std::make_shared<Basis>(m_knotsO2, 2)};
  const Spline m_splineO2{m_basisO2, Eigen::VectorXd{{0.0, 1.0, 0.25}}};
  const Interpolate m_interpO2{m_basisO2};

  const Eigen::ArrayXd m_knotsO3{{0.0, 0.0, 0.0, 0.5, 0.5, 1.0, 1.0, 1.0}};
  std::shared_ptr<Basis> m_basisO3{std::make_shared<Basis>(m_knotsO3, 3)};
  const Spline m_splineO3{
      m_basisO3,
      Eigen::MatrixXd::Random(m_knotsO3.size() - m_basisO3->order(), 2)};
  const Interpolate m_interpO3{m_basisO3};
};

/**
 * @brief Test interpolation of a piecewise linear spline function.
 * In the special case of linear segments the transformation matrix is a unit
 * matrix.
 *
 */
TEST_F(InterpolateTest, InterpolateSplineO2) {
  const Eigen::ArrayXd coeffsEst{
      m_interpO2.fit(m_splineO2(m_basisO2->greville()), m_basisO2->greville())};

  const Eigen::ArrayXd coeffsGtr{m_splineO2.getCoefficients()};

  expectAllClose(coeffsGtr, coeffsEst, 1e-6);
}

/**
 * @brief Test interpolation of a piecewise quadratic spline function.
 *
 */
TEST_F(InterpolateTest, InterpolateSplineO3) {
  const Eigen::ArrayXXd coeffsEst{
      m_interpO3.fit(m_splineO3(m_basisO3->greville()), m_basisO3->greville())};

  const Eigen::ArrayXXd coeffsGtr{m_splineO3.getCoefficients()};

  expectAllClose(coeffsGtr, coeffsEst, 1e-6);
}

/**
 * @brief Test interpolation of a piecewise quadratic spline function using
 * derivatives
 *
 */
TEST_F(InterpolateTest, InterpolateDerivSplineO3) {
  // breakpoints are evaluation points
  const auto [bps, conts] = m_basisO3->getBreakpoints();

  // determine spline derivatives at breakpoints
  std::vector<Eigen::MatrixXd> observations(3);
  observations[0] = Eigen::MatrixXd(2, m_splineO3.dim());
  observations[0] << m_splineO3({{bps(0)}}), m_splineO3.derivative()({{bps(0)}});
  observations[1] = m_splineO3({{bps(1)}});
  observations[2] = Eigen::MatrixXd(m_splineO3.dim(), 2);
  observations[2] << m_splineO3({{bps(2)}}), m_splineO3.derivative()({{bps(2)}});

  // specify derivative orders
  std::vector<Eigen::VectorXi> derivOrders{
      Eigen::VectorXi{{0, 1}}, Eigen::VectorXi{{0}}, Eigen::VectorXi{{0, 1}}};

  // // fit coefficients
  const Eigen::ArrayXXd coeffsEst{
      m_interpO3.fit(observations, derivOrders, bps)};

  const Eigen::ArrayXXd coeffsGtr{m_splineO3.getCoefficients()};

  expectAllClose(coeffsGtr, coeffsEst, 1e-6);
}

}; // namespace Internal
}; // namespace BasisSplines

int main(int argc, char **argv) {
  std::srand(0);
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
