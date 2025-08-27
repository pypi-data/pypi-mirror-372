#include <Eigen/Core>
#include <gtest/gtest.h>

#include "basisSplines/basis.h"
#include "basisSplines/interpolate.h"
#include "basisSplines/math.h"
#include "basisSplines/spline.h"
#include "basisTest.h"

namespace BasisSplines {
namespace Internal {
/**
 * @brief Test the determintation of greville sites for basis functions of
 * order 3.
 *
 */
TEST_F(BasisTest, GrevilleO3) {
  const Eigen::ArrayXd valuesEst{m_basisO3->greville()};
  const Eigen::ArrayXd valuesGtr{{0.0, 0.25, 0.75, 1.0}};

  expectAllClose(valuesEst, valuesGtr, 1e-10);
}

/**
 * @brief Test the determination of breakpoints for basis functions of order 3.
 *
 */
TEST_F(BasisTest, BreakpointsO3) {
  const std::pair<Eigen::ArrayXd, Eigen::ArrayXi> valuesEst{
      m_basisO3->getBreakpoints()};
  const std::pair<Eigen::ArrayXd, Eigen::ArrayXi> valuesGtr{{{0.0, 0.5, 1.0}},
                                                            {{0, 2, 0}}};

  expectAllClose(valuesEst.first, valuesGtr.first, 1e-10);
  expectAllClose(valuesEst.second, valuesGtr.second, 1e-10);
}

/**
 * @brief Test retrieving first 2 segments from basis functions of order 3.
 * Determine clamped basis fro segment basis and test for correct knots and
 * order.
 *
 */
TEST_F(BasisTest, GetSegment01O3) {
  // retrieve segment basis
  const Basis basisSeg{m_basisO3Seg3->getSegment(0, 1)};

  // test knots and order of segment basis
  expectAllClose(basisSeg.knots(),
                 Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.4, 0.6, 0.6, 1.0}}, 1e-10);
  EXPECT_EQ(basisSeg.order(), m_basisO3Seg3->order());

  // test evaluation of segment basis
  const Eigen::ArrayXXd valuesEst{basisSeg(basisSeg.greville())};
  const Eigen::ArrayXXd valuesGtr{(*m_basisO3Seg3)(basisSeg.greville())(
      Eigen::all, Eigen::seqN(0, basisSeg.knots().size() - basisSeg.order()))};

  expectAllClose(valuesEst, valuesGtr, 1e-10);

  // determine clamped basis from segment basis
  const Basis basisClamped{basisSeg.getClamped()};

  // test breakpoints
  const auto [bps, conts] = basisClamped.getBreakpoints();
  expectAllClose(bps, Eigen::ArrayXd{{0.0, 0.4, 0.6}}, 1e-10);
  expectAllClose(conts, Eigen::ArrayXi{{0, 2, 0}}, 1e-10);

  // test order
  EXPECT_EQ(basisClamped.order(), basisSeg.order());
}

/**
 * @brief Test retrieving last 2 segments from basis functions of order 3.
 * Determine clamped basis fro segment basis and test for correct knots and
 * order.
 *
 */
TEST_F(BasisTest, GetSegment12O3) {
  // retrieve segment basis
  const Basis basisSeg{m_basisO3Seg3->getSegment(1, 2)};

  // test knots and order of segment basis
  expectAllClose(basisSeg.knots(),
                 Eigen::ArrayXd{{0.0, 0.0, 0.4, 0.6, 0.6, 1.0, 1.0, 1.0}},
                 1e-10);
  EXPECT_EQ(basisSeg.order(), m_basisO3Seg3->order());

  // test evaluation of segment basis
  expectAllClose(
      Eigen::ArrayXXd{(*m_basisO3Seg3)(
          m_points)(Eigen::all, Eigen::seqN(1, basisSeg.knots().size() -
                                                   basisSeg.order()))},
      Eigen::ArrayXXd{basisSeg(m_points)}, 1e-10);

  // determine clamped basis from segment basis
  const Basis basisClamped{basisSeg.getClamped()};

  // test breakpoints
  const auto [bps, conts] = basisClamped.getBreakpoints();
  expectAllClose(bps, Eigen::ArrayXd{{0.4, 0.6, 1.0}}, 1e-10);
  expectAllClose(conts, Eigen::ArrayXi{{0, 1, 0}}, 1e-10);

  // test order
  EXPECT_EQ(basisClamped.order(), basisSeg.order());
}

/**
 * @brief Combine a basis of order 3 with a basis of order 2.
 *
 */
TEST_F(BasisTest, CombineO3O2) {
  const Eigen::ArrayXd knotsO2{{0.0, 0.0, 0.2, 0.5, 0.6, 1.0, 1.0}};
  const Basis basisO2{knotsO2, 2};

  const Basis estimate{m_basisO3->combine(basisO2, m_basisO3->order())};

  const Basis groundTruth{
      {{0.0, 0.0, 0.0, 0.2, 0.2, 0.5, 0.5, 0.6, 0.6, 1.0, 1.0, 1.0}},
      m_basisO3->order()};

  expectAllClose(estimate.knots(), groundTruth.knots(), 1e-6);
  EXPECT_EQ(estimate.order(), groundTruth.order());
}

/**
 * @brief Test conversion from breakpoints to knots for spline of order 3.
 *
 */
TEST_F(BasisTest, ToKnotsO3) {
  const auto [bps, conts] = m_basisO3->getBreakpoints();

  const Eigen::ArrayXd valuesEst{
      Basis::toKnots(bps, conts, m_basisO3->order())};
  const Eigen::ArrayXd valuesGtr{m_basisO3->knots()};

  expectAllClose(valuesEst, valuesGtr, 1e-10);
}

/**
 * @brief Test generation of derivative transformation matrix.
 *
 */
TEST_F(BasisTest, DerivMatO3) {
  // ground truth from spline fit to derivative
  const Eigen::ArrayXXd valuesGtr{m_splineO3Der.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{m_basisO3->derivative(basisEst, 1) *
                                 m_splineO3.getCoefficients().matrix()};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Der.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test generation of derivative transformation matrix with scaled basis.
 *
 */
TEST_F(BasisTest, DerivMatO3Scaled) {
  // scale basis with m_scalingFactor
  Basis basisO3Scale2{*m_basisO3};
  basisO3Scale2.setScale(m_scalingFactor);

  // get derivative of scaled basis
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{m_basisO3->derivative(basisEst, 1) *
                                 m_splineO3.getCoefficients().matrix()};

  // scale breakpoints with 2
  Basis basisO3Bps2{*m_basisO3};
  const Eigen::ArrayXd breakpoints{basisO3Bps2.getBreakpoints().first};
  basisO3Bps2.setBreakpoints(
      breakpoints * m_scalingFactor,
      Eigen::ArrayXi::LinSpaced(breakpoints.size(), 0, breakpoints.size()));

  // get derivative of breakpoint scaled basis
  Basis basisGtr{};
  const Eigen::ArrayXXd valuesGtr{m_basisO3->derivative(basisGtr, 1) *
                                 m_splineO3.getCoefficients().matrix()};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test generation of second derivative transformation matrix.
 *
 */
TEST_F(BasisTest, DderivMatO3) {
  // ground truth from spline fit to derivative
  const Eigen::ArrayXXd valuesGtr{m_splineO3Dder.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{m_basisO3->derivative(basisEst, 2) *
                                 m_splineO3.getCoefficients().matrix()};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Dder.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test generation of derivative value transformation.
 *
 */
TEST_F(BasisTest, DerivTransformO3) {
  // ground truth from spline fit to derivative
  const Eigen::ArrayXXd valuesGtr{m_splineO3Der.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{
      m_basisO3->derivative(basisEst, m_splineO3.getCoefficients(), 1)};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Der.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test generation of second derivative value transformation with scaled
 * basis.
 *
 */
TEST_F(BasisTest, DerivTransformO3Scaled) {
  // scale basis with m_scalingFactor
  Basis basisO3Scale2{*m_basisO3};
  basisO3Scale2.setScale(m_scalingFactor);

  // get derivative of scaled basis
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{
      basisO3Scale2.derivative(basisEst, m_splineO3.getCoefficients(), 1)};

  // scale breakpoints with m_scalingFactor
  Basis basisO3Bps2{*m_basisO3};
  const Eigen::ArrayXd breakpoints{basisO3Bps2.getBreakpoints().first};
  basisO3Bps2.setBreakpoints(
      breakpoints * m_scalingFactor,
      Eigen::ArrayXi::LinSpaced(breakpoints.size(), 0, breakpoints.size()));

  // get derivative of breakpoint scaled basis
  Basis basisGtr{};
  const Eigen::ArrayXXd valuesGtr{
      basisO3Bps2.derivative(basisEst, m_splineO3.getCoefficients(), 1)};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test generation of integral transformation matrix.
 *
 */
TEST_F(BasisTest, IntMatO3) {
  // ground truth from spline fit to integral
  const Eigen::ArrayXXd valuesGtr{m_splineO3Int.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{m_basisO3->integral(basisEst, 1) *
                                 m_splineO3.getCoefficients()};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Int.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test generation of integral transformation matrix with scaled basis.
 *
 */
TEST_F(BasisTest, IntMatO3Scaled) {
  // scale basis with m_scalingFactor
  Basis basisO3Scale2{*m_basisO3};
  basisO3Scale2.setScale(m_scalingFactor);

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{basisO3Scale2.integral(basisEst, 1) *
                                 m_splineO3.getCoefficients()};

  // scale breakpoints with m_scalingFactor
  Basis basisO3Bps2{*m_basisO3};
  const Eigen::ArrayXd breakpoints{basisO3Bps2.getBreakpoints().first};
  basisO3Bps2.setBreakpoints(
      breakpoints * m_scalingFactor,
      Eigen::ArrayXi::LinSpaced(breakpoints.size(), 0, breakpoints.size()));

  // get derivative of breakpoint scaled basis
  Basis basisGtr{};
  const Eigen::ArrayXXd valuesGtr{basisO3Bps2.integral(basisGtr, 1) *
                                 m_splineO3.getCoefficients()};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test generation of second integral transformation matrix.
 *
 */
TEST_F(BasisTest, IintMatO3) {
  // ground truth from spline fit to integral
  const Eigen::ArrayXXd valuesGtr{m_splineO3Iint.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{m_basisO3->integral(basisEst, 2) *
                                 m_splineO3.getCoefficients()};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Iint.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test generation of integral value transformation.
 *
 */
TEST_F(BasisTest, IntTransformO3) {
  // ground truth from spline fit to integral
  const Eigen::ArrayXXd valuesGtr{m_splineO3Int.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{
      m_basisO3->integral(basisEst, m_splineO3.getCoefficients(), 1)};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Int.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test generation of integral value transformation with scaled basis.
 *
 */
TEST_F(BasisTest, IntTransformO3Scaled) {
  // scale basis with m_scalingFactor
  Basis basisO3Scale2{*m_basisO3};
  basisO3Scale2.setScale(m_scalingFactor);

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{
      basisO3Scale2.integral(basisEst, m_splineO3.getCoefficients(), 1)};

  // scale breakpoints with m_scalingFactor
  Basis basisO3Bps2{*m_basisO3};
  const Eigen::ArrayXd breakpoints{basisO3Bps2.getBreakpoints().first};
  basisO3Bps2.setBreakpoints(
      breakpoints * m_scalingFactor,
      Eigen::ArrayXi::LinSpaced(breakpoints.size(), 0, breakpoints.size()));

  // get derivative of breakpoint scaled basis
  Basis basisGtr{};
  const Eigen::ArrayXXd valuesGtr{
      basisO3Bps2.integral(basisEst, m_splineO3.getCoefficients(), 1)};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test generation of second integral value transformation.
 *
 */
TEST_F(BasisTest, IintTransformO3) {
  // ground truth from spline fit to integral
  const Eigen::ArrayXXd valuesGtr{m_splineO3Iint.getCoefficients()};

  // get estimate from result spline
  Basis basisEst{};
  const Eigen::ArrayXXd valuesEst{
      m_basisO3->integral(basisEst, m_splineO3.getCoefficients(), 2)};

  // test if coefficients are almost equal
  expectAllClose(valuesGtr, valuesEst, 1e-8);

  // ground truth basis
  Basis basisGtr{*m_basisO3Iint.get()};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test summing two splines of order 3.
 *
 */
TEST_F(BasisTest, SumMatO3) {
  // instatiate left operand spline of order 3
  const Eigen::VectorXd coeffsL{Eigen::VectorXd::Random(m_basisO3->dim())};

  // instantiate right operand spline of order 3
  const Eigen::ArrayXd knotsR{{0.0, 0.0, 0.0, 0.25, 0.5, 0.8, 1.0, 1.0}};
  const Basis basisR{knotsR, 3};
  const Eigen::VectorXd coeffsR{Eigen::VectorXd::Random(basisR.dim())};

  // get gt from basis evaluations
  const Eigen::ArrayXd valuesGtr{(*m_basisO3)(m_points)*coeffsL +
                                 basisR(m_points) * coeffsR};

  // determine sum transformations
  Basis basisEst{};
  const auto [transformL, transformR] = m_basisO3->add(basisR, basisEst);

  // get estimate by applying sum transformations
  const Eigen::ArrayXd valuesEst{basisEst(m_points) *
                                 (transformL * coeffsL + transformR * coeffsR)};

  // test if evaluations are alomst equal
  expectAllClose(valuesGtr, valuesEst, 1e-10);

  // ground truth basis
  const Basis basisGtr{
      m_basisO3->combine(basisR, std::max(m_basisO3->order(), basisR.order()))};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test product two splines of order 3.
 *
 */
TEST_F(BasisTest, ProdMatO3) {
  // instatiate left operand spline of order 3
  const Eigen::VectorXd coeffsL{Eigen::VectorXd::Random(m_basisO3->dim())};

  // instantiate right operand spline of order 3
  const Eigen::ArrayXd knotsR{{0.0, 0.0, 0.0, 0.25, 0.5, 0.8, 1.0, 1.0}};
  const Basis basisR{knotsR, 3};
  const Eigen::VectorXd coeffsR{Eigen::VectorXd::Random(basisR.dim())};

  // get gt from basis evaluations
  const Eigen::ArrayXd valuesGtr{((*m_basisO3)(m_points)*coeffsL).array() *
                                 (basisR(m_points) * coeffsR).array()};

  // determine product transformations
  Basis basisEst{};
  const Eigen::MatrixXd transform{m_basisO3->prod(basisR, basisEst)};

  // get estimate by applying product transformations
  const Eigen::MatrixXd coeffsProd{transform *
                                  kron(coeffsL, coeffsR)};
  const Eigen::ArrayXd valuesEst{basisEst(m_points) *
                                 coeffsProd};

  // test if evaluations are alomst equal
  expectAllClose(valuesGtr, valuesEst, 1e-10);

  // ground truth basis
  const Basis basisGtr{
      m_basisO3->combine(basisR, m_basisO3->order() + basisR.order() - 1)};

  // test if knots are almost equal
  expectAllClose(basisGtr.knots(), basisEst.knots(), 1e-8);
  // test if order is equal
  EXPECT_EQ(basisGtr.order(), basisEst.order());
}

/**
 * @brief Test setting breakpoints successfully.
 *
 */
TEST_F(BasisTest, SetBreakpointsPositive) {
  // TEST: successful breakpoint setting
  // determine ground truth: set first breakpoint to 0.1, second to 0.6
  auto [breakpointsGtr, contsGtr] = m_basisO3->getBreakpoints();
  const Eigen::ArrayXi breakpointIdcs{{0, 1}};
  breakpointsGtr(breakpointIdcs) = Eigen::ArrayXd{{0.1, 0.6}};

  // expect: setting valit breakpoints does not throw invalid argument error
  EXPECT_NO_THROW(m_basisO3->setBreakpoints(breakpointsGtr(breakpointIdcs),
                                            breakpointIdcs));
  // determine estimate: get current breakpoints
  auto [breakpointsEst, contsEst] = m_basisO3->getBreakpoints();

  // expect: breakpoint estimates and ground truth almost equal
  expectAllClose(breakpointsGtr, breakpointsEst, 1e-8);
}

/**
 * @brief Test setting breakpoints resulting in a non-increasing order.
 *
 */
TEST_F(BasisTest, SetBreakpointsNegativeNonIncreasing) {
  // determine ground truth
  auto [breakpointsGtr, contsGtr] = m_basisO3->getBreakpoints();

  // expect: setting invalid breakpoints throws invalid arugment error
  EXPECT_THROW(m_basisO3->setBreakpoints({{0.1, 0.0}}, {{0, 1}}),
               std::invalid_argument);
  // determine estimate: get current breakpoints
  auto [breakpointsEst, contsEst] = m_basisO3->getBreakpoints();

  // expect: setting invalid breakpionts does not change basis
  expectAllClose(breakpointsGtr, breakpointsEst, 1e-8);
}

}; // namespace Internal
}; // namespace BasisSplines

int main(int argc, char **argv) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
