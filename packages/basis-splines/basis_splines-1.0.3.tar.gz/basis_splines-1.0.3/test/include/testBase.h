#ifndef TEST_BASE_H
#define TEST_BASE_H

#include <Eigen/Core>
#include <array>
#include <gtest/gtest.h>

namespace BasisSplines {
namespace Internal {
using limits = std::numeric_limits<double>;

/**
 * @brief Base class for tests providing commonly used functions and test cases.
 *
 */
class TestBase : public testing::Test {
protected:
  /**
   * @brief Expect that the elements of two arrays are sufficiently close.
   * Closeness of array elements is defined with an absolute and a relative
   * error.
   *
   * @tparam ValType type of array elements.
   * @param estimate array with estimations of "groundTruth" values.
   * @param groundTruth array with ground truth values.
   * @param errAbs tolerated absolute error between elements.
   * @param errRel tolerated relative error between elements.
   */
  template <typename ValType>
  void expectAllClose(const Eigen::ArrayBase<ValType> &estimate,
                      const Eigen::ArrayBase<ValType> &groundTruth,
                      double errAbs = limits::infinity(),
                      double errRel = limits::infinity()) {
    const ValType errAbsVals{(estimate - groundTruth).abs()};
    // const ValType errRelVals{errAbsVals / groundTruth};

    for (int idx{}; idx < estimate.size(); ++idx) {
      EXPECT_LT(errAbsVals(idx), errAbs)
          << "Error bound violated at index " << idx << '!';
      // if (!std::isinf(errRelVals(idx)) && !std::isnan(errRelVals(idx)))
      //   EXPECT_LT(errRelVals(idx), errRel)
      //       << "Error bound violated at index " << idx << '!';
    }
  }
};
}; // namespace Internal
}; // namespace BasisSpline

#endif