#ifndef MATH_H
#define MATH_H

#include <Eigen/Core>

namespace BasisSplines {
/**
 * @brief Determine Khatri-Rao product of two matrices "matL" and "matR".
 * The Khatri-Rao product corresponds to a row-wise Kronecker product.
 * The number of rows n of "matL" and "matR" must be equal.
 *
 * @param matL left operand matrix (n x mL).
 * @param matR right operand matrix (n x mR).
 * @return Eigen::MatrixXd result matrix (n x mL*mR).
 */
Eigen::MatrixXd khatriRao(const Eigen::MatrixXd &matL,
                          const Eigen::MatrixXd &matR) {
  // test equality or row numbers
  assert(matL.rows() == matR.rows() &&
         "Number of rows in left and right arrays must be equal.");

  // initialize result matrix
  Eigen::MatrixXd matRes(matL.rows(), matL.cols() * matR.cols());

  // fill result matrix row-wise
  int cRow{};
  for (const auto rowArrL : matL.rowwise()) {
    // product of each matL row element with current row of matR
    int cCol{};
    for (const double coeffL : rowArrL) {
      matRes(cRow, Eigen::seqN(cCol, matR.cols())) =
          coeffL * matR(cRow, Eigen::all);
      cCol += matR.cols();
    }
    ++cRow;
  }

  return matRes;
}

/**
 * @brief Determines the Kronecker product of two matrices "matL" and "matR".
 *
 * @param matL left operand matrix (nL x mL).
 * @param matR right operand matrix (nL x mR).
 * @return Eigen::MatrixXd result matrix (nL*nR x mL*mR).
 */
Eigen::MatrixXd kron(const Eigen::MatrixXd &matL, const Eigen::MatrixXd &matR) {
  // initialize result matrix
  Eigen::MatrixXd matRes(matL.rows() * matR.rows(), matL.cols() * matR.cols());

  // fill result matrix row-wise
  int cRow{};
  for (const auto rowL : matL.rowwise()) {
    // product of each matL row element with matR
    int cCol{};
    for (const double coeffL : rowL) {
      matRes(Eigen::seqN(cRow, matR.rows()), Eigen::seqN(cCol, matR.cols())) =
          coeffL * matR;
      cCol += matR.cols();
    }
    cRow += matR.rows();
  }

  return matRes;
}
}; // namespace BasisSplines
#endif