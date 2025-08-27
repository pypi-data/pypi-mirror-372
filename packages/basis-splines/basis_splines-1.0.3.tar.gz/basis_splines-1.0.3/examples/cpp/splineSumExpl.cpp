#include <Eigen/Core>
#include <matplot/matplot.h>

#include "basisSplines/basis.h"
#include "basisSplines/spline.h"
#include "helper.h"

namespace Bs = BasisSplines;
namespace Mt = matplot;

int main(int argc, char *argv[]) {

  std::vector<Bs::Spline> splines(3);

  // definition first spline of order 3 with 4 breakpoints
  splines[0] = Bs::Spline{
      std::make_shared<Bs::Basis>(
          Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0}}, 3),
      Eigen::ArrayXd{{0.0, 0.5, 0.25, -0.3, -1.0, 0.75}}};

  // definition second spline of order 4 with 3 breakpoints
  splines[1] = Bs::Spline{
      std::make_shared<Bs::Basis>(
          Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.0, 0.2, 0.2, 1.0, 1.0, 1.0, 1.0}},
          4),
      Eigen::ArrayXd{{1.0, -1.0, 0.3, 0.4, -0.1, 0.0}}};

  // add two splines
  Bs::Basis basisSum{};
  const auto [trfLeft, trfRight] =
      splines[0].basis()->add(*splines[1].basis(), basisSum);
  splines[2] = Bs::Spline{std::make_shared<Bs::Basis>(basisSum),
                          trfLeft * splines[0].getCoefficients() +
                              trfRight * splines[1].getCoefficients()};

  // setup figure handle
  auto figureHandle{Mt::figure()};
  figureHandle->size(800, 600);

  // y-axis labels for each y axis
  std::array<std::string, 3> yLabels{"s_0(x)/1", "s_1(x)/1", "s_{0+1}(x)/1"};

  for (int cSpline{}; cSpline < splines.size(); ++cSpline) {
    // plot spline at evaluation points
    auto axesHandle{matplot::subplot(figureHandle, splines.size(), 1, cSpline)};
    axesHandle->hold(true);
    axesHandle->grid(true);
    axesHandle->xlabel("x/1");
    axesHandle->ylabel(yLabels[cSpline]);
    Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottom);

    plotSpline(splines[cSpline], Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1),
               axesHandle);
  }

  // enable grid, save and show figure
  saveFigure(figureHandle, getFileName(argc, argv), getFileEnding(argc, argv));
  matplot::show();

  return 0;
}