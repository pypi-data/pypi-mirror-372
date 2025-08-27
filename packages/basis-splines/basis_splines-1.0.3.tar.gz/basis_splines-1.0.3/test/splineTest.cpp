#include <Eigen/Core>
#include <gtest/gtest.h>

#include "basisSplines/basis.h"
#include "basisSplines/interpolate.h"
#include "basisSplines/spline.h"
#include "basisTest.h"

namespace BasisSplines {
namespace Internal {
class SplineTest : public BasisTest {

protected:
  const Eigen::ArrayXd m_knotsO2{{0.0, 0.0, 0.5, 1.0, 1.0}};
  std::shared_ptr<Basis> m_basisO2{std::make_shared<Basis>(m_knotsO2, 2)};

  const Spline m_splineO3Seg3{m_basisO3Seg3,
                              Eigen::MatrixXd::Random(m_basisO3Seg3->dim(), 2)};
};

/**
 * @brief Test piecewise linear spline function.
 *
 */
TEST_F(SplineTest, SplineEvalO2) {
  // setup spline function of linear segments
  const Eigen::ArrayXd coeffs{{0.0, 1.0, 0.25}};
  const Spline spline{m_basisO2, coeffs};

  // evaluate spline functions
  const Eigen::ArrayXd points{{0.0, 0.25, 0.5, 1.0}};
  const Eigen::ArrayXXd valuesEst{spline(points)};

  // ground truth assumes picewise linear function between coefficients
  const Eigen::ArrayXXd valuesGtr{
      Eigen::ArrayXXd{{0.0, 0.5, 1.0, 0.25}}.transpose()};

  expectAllClose(valuesEst, valuesGtr, 1e-6);
}

/**
 * @brief Test piecewise linear spline function.
 *
 */
TEST_F(SplineTest, SplineEvalO2D2) {
  // setup spline function of linear segments
  const Eigen::MatrixXd coeffs{{0.0, 1.0, 0.25}, {0.0, 1.0, 0.25}};
  const Spline spline{m_basisO2, coeffs.transpose()};

  // evaluate spline functions
  const Eigen::ArrayXd points{{0.0, 0.25, 0.5, 1.0}};
  const Eigen::ArrayXXd valuesEst{spline(points)};

  // ground truth assumes picewise linear function between coefficients
  const Eigen::ArrayXXd valuesGtr{Eigen::ArrayXXd{
      {0.0, 0.5, 1.0, 0.25},
      {0.0, 0.5, 1.0, 0.25}}.transpose()};

  expectAllClose(valuesEst, valuesGtr, 1e-6);
}

/**
 * @brief Test summing two splines of order 3.
 *
 */
TEST_F(SplineTest, SplineSumO3) {
  // instatiate left operand spline of order 3
  const Spline splineL{m_basisO3, Eigen::MatrixXd::Random(m_basisO3->dim(), 2)};

  // instantiate right operand spline of order 3
  const Eigen::ArrayXd knotsR{{0.0, 0.0, 0.0, 0.25, 0.5, 0.8, 1.0, 1.0}};
  std::shared_ptr<Basis> basisR{std::make_shared<Basis>(knotsR, 3)};
  const Spline splineR{basisR, Eigen::MatrixXd::Random(basisR->dim(), 2)};

  // get gt from spline sum
  const Eigen::ArrayXXd valuesGtr{splineL(m_points) + splineR(m_points)};

  // get estimate from sum spline
  const Spline spline{splineL.add(splineR)};
  const Eigen::ArrayXXd valuesEst{spline(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-10);
}

/**
 * @brief Test multiplying two splines of order 3.
 *
 */
TEST_F(SplineTest, SplineProdO3) {
  // instatiate left operand spline of order 3
  const Spline splineL{m_basisO3, Eigen::MatrixXd::Random(m_basisO3->dim(), 2)};

  // instantiate right operand spline of order 3
  const Eigen::ArrayXd knotsR{{0.0, 0.0, 0.0, 0.25, 0.5, 0.8, 1.0, 1.0}};
  std::shared_ptr<Basis> basisR{std::make_shared<Basis>(knotsR, 3)};
  const Spline splineR{basisR, Eigen::MatrixXd::Random(basisR->dim(), 2)};

  // get gt from spline product
  const Eigen::ArrayXXd valuesGtr{splineL(m_points) * splineR(m_points)};

  // get estimate from product spline
  const Spline spline{splineL.prod(splineR)};
  const Eigen::ArrayXXd valuesEst{spline(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-10);
}

/**
 * @brief Test multiplying splines of order 4 and 3.
 *
 */
TEST_F(SplineTest, SplineProdO3O4) {
  // instatiate left operand spline of order 3
  const Spline splineL{m_basisO3, Eigen::MatrixXd::Random(m_basisO3->dim(), 2)};

  // instantiate right operand spline of order 4
  const Eigen::ArrayXd knotsR{{0.0, 0.0, 0.0, 0.25, 0.5, 0.8, 1.0, 1.0}};
  std::shared_ptr<Basis> basisR{std::make_shared<Basis>(knotsR, 4)};
  const Spline splineR{basisR, Eigen::MatrixXd::Random(basisR->dim(), 2)};

  // get gt from spline product
  const Eigen::ArrayXXd valuesGtr{splineL(m_points) * splineR(m_points)};

  // get estimate from product spline
  const Spline spline{splineL.prod(splineR)};
  const Eigen::ArrayXXd valuesEst{spline(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-10);
}

/**
 * @brief Test derivative spline of order 3.
 *
 */
TEST_F(SplineTest, SplineDerivO3) {
  const Eigen::ArrayXXd valuesGtr{polyO3Der(m_points)};
  const Eigen::ArrayXXd valuesEst{m_splineO3.derivative()(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test second order derivative spline of order 3.
 *
 */
TEST_F(SplineTest, SplineDderivO3) {
  const Eigen::ArrayXXd valuesGtr{polyO3Dder(m_points)};
  const Eigen::ArrayXXd valuesEst{m_splineO3.derivative(2)(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test integral spline of order 3.
 *
 */
TEST_F(SplineTest, SplineIntO3) {
  const Eigen::ArrayXXd valuesGtr{polyO3Int(m_points)};
  const Eigen::ArrayXXd valuesEst{m_splineO3.integral()(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test second order integral spline of order 3.
 *
 */
TEST_F(SplineTest, SplineIintO3) {
  const Eigen::ArrayXXd valuesGtr{polyO3Iint(m_points)};
  const Eigen::ArrayXXd valuesEst{m_splineO3.integral(2)(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-8);
}

/**
 * @brief Test knots insertion at {0.4, 0.5, 0.6}.
 *
 */
TEST_F(SplineTest, InsertKnots) {
  // instantiate spline of order 3
  const Spline spline{m_basisO3, Eigen::MatrixXd::Random(m_basisO3->dim(), 2)};

  // insert knots
  const Eigen::ArrayXd knotsInsert{{0.4, 0.5, 0.6}};
  const Spline splineInsert{spline.insertKnots(knotsInsert)};

  // get ground truth from initial spline
  const Eigen::ArrayXXd valuesGtr{spline(m_points)};

  // get estimate from result spline
  const Eigen::ArrayXXd valuesEst{splineInsert(m_points)};

  expectAllClose(valuesGtr, valuesEst, 1e-6);
}

/**
 * @brief Test order elevation by 2.
 *
 */
TEST_F(SplineTest, OrderElevation) {
  // instantiate spline of order 3
  const Spline spline{m_basisO3, Eigen::MatrixXd::Random(m_basisO3->dim(), 2)};

  // increase order
  const int orderChange{2};
  const Spline splineIncr{spline.orderElevation(orderChange)};

  // test order increase
  EXPECT_EQ(splineIncr.basis()->order(), m_basisO3->order() + orderChange);

  // get ground truth from initial spline
  const Eigen::ArrayXXd valuesGtr{spline(m_points)};

  // get estimate from result spline
  const Eigen::ArrayXXd valuesEst{splineIncr(m_points)};

  // test spline equality
  expectAllClose(valuesGtr, valuesEst, 1e-6);
}

/**
 * @brief Test retrieving first 2 segments from spline function of order 3.
 * Determine clamped spline from spline segment and test for equality.
 *
 */
TEST_F(SplineTest, GetSegment01O3) {
  // determine spline representing first 2 spline segments
  const Spline splineSeg{m_splineO3Seg3.getSegment(0, 1)};

  // test equality spline equality at points in the first 2 segments
  const auto breakpoints{splineSeg.basis()->getBreakpoints()};
  const Eigen::ArrayXd pointsSubset{
      getPointsSubset(breakpoints.first(0), breakpoints.first(2))};

  Eigen::ArrayXXd valuesEst{splineSeg(pointsSubset)};
  const Eigen::ArrayXXd valuesGtr{m_splineO3Seg3(pointsSubset)};
  expectAllClose(valuesEst, valuesGtr, 1e-10);

  // determine clamped equivalent spline
  const Spline splineClamped{splineSeg.getClamped()};

  // test equality of clamped spline and spline segment
  valuesEst = splineClamped(pointsSubset);
  expectAllClose(valuesEst, valuesGtr, 1e-10);
}

/**
 * @brief Test retrieving mid segment from spline function of order 3.
 * Determine clamped spline from spline segment and test for equality.
 *
 */
TEST_F(SplineTest, GetSegment1O3) {
  // determine spline representing mid spline segments
  const Spline splineSeg{m_splineO3Seg3.getSegment(1, 1)};

  // test equality spline equality at points in the first 2 segments
  const auto breakpoints{splineSeg.basis()->getBreakpoints()};
  const Eigen::ArrayXd pointsSubset{
      getPointsSubset(breakpoints.first(1), breakpoints.first(2))};

  Eigen::ArrayXXd valuesEst{splineSeg(pointsSubset)};
  const Eigen::ArrayXXd valuesGtr{m_splineO3Seg3(pointsSubset)};
  expectAllClose(valuesEst, valuesGtr, 1e-10);

  // determine clamped equivalent spline
  const Spline splineClamped{splineSeg.getClamped()};

  // test equality of clamped spline and spline segment
  valuesEst = splineClamped(pointsSubset);
  expectAllClose(valuesEst, valuesGtr, 1e-10);
}

/**
 * @brief Test retrieving last 2 segments from spline of order 3.
 * Determine clamped spline from spline segment and test for equality.
 *
 */
TEST_F(SplineTest, GetSegment12O3) {
  // determine spline representing last spline segments
  const Spline splineSeg{m_splineO3Seg3.getSegment(1, 2)};

  // test equality spline equality at points in the first 2 segments
  const auto breakpoints{splineSeg.basis()->getBreakpoints()};
  const Eigen::ArrayXd pointsSubset{
      getPointsSubset(breakpoints.first(1), breakpoints.first(3))};

  Eigen::ArrayXXd valuesEst{splineSeg(pointsSubset)};
  const Eigen::ArrayXXd valuesGtr{m_splineO3Seg3(pointsSubset)};
  expectAllClose(valuesEst, valuesGtr, 1e-10);

  // determine clamped equivalent spline
  const Spline splineClamped{splineSeg.getClamped()};

  // test equality of clamped spline and spline segment
  valuesEst = splineClamped(pointsSubset);
  expectAllClose(valuesEst, valuesGtr, 1e-10);
}

TEST_F(SplineTest, GetSegment11O4) {
  // basis of order 5 with 4 breakpoints
  std::shared_ptr<Basis> basis{std::make_shared<Basis>(
      Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.0, 0.4, 0.7, 1.0, 1.0, 1.0, 1.0}}, 4)};

  // spline of order 4
  Spline spline{basis, Eigen::ArrayXd{{0.0, 0.5, 0.25, -0.3, -1.0, 0.75}}};

  // determine spline representing last spline segments
  const Spline splineSeg{spline.getSegment(1, 1)};

  // test equality spline equality at points in the first 2 segments
  const auto breakpoints{splineSeg.basis()->getBreakpoints()};
  const Eigen::ArrayXd pointsSubset{
      getPointsSubset(breakpoints.first(1), breakpoints.first(2))};

  Eigen::ArrayXXd valuesEst{splineSeg(pointsSubset)};
  const Eigen::ArrayXXd valuesGtr{spline(pointsSubset)};
  expectAllClose(valuesEst, valuesGtr, 1e-10);

  // determine clamped equivalent spline
  const Spline splineClamped{splineSeg.getClamped()};

  // test equality of clamped spline and spline segment
  valuesEst = splineClamped(pointsSubset);
  expectAllClose(valuesEst, valuesGtr, 1e-10);

  EXPECT_DOUBLE_EQ(splineClamped.getCoefficients()(0), splineClamped(Eigen::ArrayXd{{breakpoints.first(1)}})(0,0));
  EXPECT_DOUBLE_EQ(splineClamped.getCoefficients()(3), splineClamped(Eigen::ArrayXd{{breakpoints.first(2)}})(0,0));
}

}; // namespace Internal
}; // namespace BasisSplines

int main(int argc, char **argv) {
  std::srand(0);
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
