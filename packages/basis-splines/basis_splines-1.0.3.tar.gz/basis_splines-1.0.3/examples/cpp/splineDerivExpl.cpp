#include <Eigen/Core>
#include <matplot/matplot.h>
#include <string>

#include "basisSplines/basis.h"
#include "basisSplines/spline.h"
#include "helper.h"

namespace Bs = BasisSplines;
namespace Mt = matplot;

int main(int argc, char *argv[]) {

  std::vector<Bs::Spline> splines(2);

  // basis of order 3 with 4 breakpoints
  std::shared_ptr<Bs::Basis> basis{std::make_shared<Bs::Basis>(
      Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0}}, 3)};

  // spline definition
  splines[0] =
      Bs::Spline{basis, Eigen::ArrayXd{{0.0, 0.5, 0.25, -0.3, -1.0, 0.75}}};

  // spline derivative
  Bs::Basis basisDeriv{};
  const auto trf{basis->derivative(basisDeriv)};
  splines[1] = Bs::Spline{std::make_shared<Bs::Basis>(basisDeriv), trf * splines[0].getCoefficients()};

  // setup figure handle
  auto figureHandle{Mt::figure()};
  figureHandle->size(800, 600);

  // y-axis labels for each y axis
  std::array<std::string, 3> yLabels{"s(x)/1", "s'(x)/1"};

  for (int cSpline{}; cSpline < splines.size(); ++cSpline) {
    // plot spline at evaluation points
    auto axesHandle{matplot::subplot(figureHandle, splines.size(), 1, cSpline)};
    axesHandle->hold(true);
    axesHandle->grid(true);
    axesHandle->xlabel("x/1");
    axesHandle->ylabel(yLabels[cSpline]);
    Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomleft);

    plotSpline(splines[cSpline], Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1),
               axesHandle);
  }

  // save and show figure
  saveFigure(figureHandle, getFileName(argc, argv), getFileEnding(argc, argv));
  matplot::show();

  return 0;
}