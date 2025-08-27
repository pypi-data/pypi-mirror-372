#ifndef HELPER_H
#define HELPER_H

#include <Eigen/Core>
#include <matplot/matplot.h>

#include "basisSplines/basis.h"
#include "basisSplines/spline.h"

namespace Bs = BasisSplines;
namespace Mt = matplot;

/**
 * @brief Plot a spline function at the given points in an axis handle.
 * The plot includes the spline function, the coefficients at the greville
 * sites, and the breakpoints.
 *
 * @param spline spline object to plot.
 * @param points function evaluation points.
 * @param axesHandle axis handle for plotting.
 * @param dim output dimension to plot.
 */
void plotSpline(const Bs::Spline &spline, const Eigen::ArrayXd &points,
                const Mt::axes_handle axesHandle, int dim = 0) {
  // plot spline at evaluation points
  const Eigen::ArrayXd splineVals{spline(points)(Eigen::all, dim)};
  axesHandle
      ->plot(std::vector<double>{points.begin(), points.end()},
             std::vector<double>{splineVals.begin(), splineVals.end()})
      ->display_name("spline");

  // plot coefficients at greville sites
  const Eigen::ArrayXd greville{spline.basis()->greville()};
  matplot::plot(
      std::vector<double>{greville.begin(), greville.end()},
      std::vector<double>{spline.getCoefficients()(Eigen::all, dim).begin(),
                          spline.getCoefficients()(Eigen::all, dim).end()},
      "-o")
      ->marker_size(10.0)
      .display_name("coefficients");

  // plot breakpoints along spline
  const Eigen::ArrayXd bps = spline.basis()->getBreakpoints().first;
  const Eigen::ArrayXd splineValsBps{spline(bps)(Eigen::all, dim)};
  matplot::scatter(
      std::vector<double>{bps.begin(), bps.end()},
      std::vector<double>{splineValsBps.begin(), splineValsBps.end()})
      ->marker_style(matplot::line_spec::marker_style::diamond)
      .marker_color({0.0, 0.0, 1.0})
      .marker_face_color({0.0, 0.0, 1.0})
      .display_name("breakpoints");
}

void plotSpline2d(const Bs::Spline &spline, const Eigen::ArrayXd &points,
                  const Mt::axes_handle axesHandle,
                  const std::array<int, 2> &dims) {
  // plot spline at evaluation points
  const Eigen::ArrayXXd splineVals{spline(points)(Eigen::all, dims)};
  axesHandle
      ->plot(std::vector<double>{splineVals(Eigen::all, dims[0]).begin(),
                                 splineVals(Eigen::all, dims[0]).end()},
             std::vector<double>{splineVals(Eigen::all, dims[1]).begin(),
                                 splineVals(Eigen::all, dims[1]).end()})
      ->display_name("spline");

  // plot coefficients
  matplot::plot(
      std::vector<double>{spline.getCoefficients()(Eigen::all, dims[0]).begin(),
                          spline.getCoefficients()(Eigen::all, dims[0]).end()},
      std::vector<double>{spline.getCoefficients()(Eigen::all, dims[1]).begin(),
                          spline.getCoefficients()(Eigen::all, dims[1]).end()},
      "-o")
      ->marker_size(10.0)
      .display_name("coefficients");

  // plot breakpoints along spline
  const Eigen::ArrayXd bps = spline.basis()->getBreakpoints().first;
  const Eigen::ArrayXXd splineValsBps{spline(bps)};
  matplot::scatter(
      std::vector<double>{splineValsBps(Eigen::all, dims[0]).begin(),
                          splineValsBps(Eigen::all, dims[0]).end()},
      std::vector<double>{splineValsBps(Eigen::all, dims[1]).begin(),
                          splineValsBps(Eigen::all, dims[1]).end()})
      ->marker_style(matplot::line_spec::marker_style::diamond)
      .marker_color({0.0, 0.0, 1.0})
      .marker_face_color({0.0, 0.0, 1.0})
      .display_name("breakpoints");
}

/**
 * @brief Get output file name from arguments.
 *
 * @param argc argument counter.
 * @param argv argument variables.
 * @return std::string_view output file name.
 */
std::string_view getFileName(int argc, char *argv[]) {
  switch (argc) {
  case 3:
    return *(argv + 1);
    break;
  default:
    return "default";
  }
}

/**
 * @brief Get output file ending from arguments.
 *
 * @param argc argument counter.
 * @param argv argument variables.
 * @return std::string_view output file ending.
 */
std::string_view getFileEnding(int argc, char *argv[]) {
  switch (argc) {
  case 3:
    return *(argv + 2);
    break;
  default:
    return ".jpg";
  }
}

/**
 * @brief Save "figureHandle" to file with "name" and "ending".
 *
 * @param figureHandle figure handle to save.
 * @param name file name.
 * @param ending file ending.
 */
void saveFigure(const Mt::figure_handle &figureHandle,
                const std::string_view name, const std::string_view ending) {
  Mt::save(figureHandle, std::format("{}.{}", name, ending));
}

#endif