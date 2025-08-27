#include <Eigen/Core>
#include <matplot/matplot.h>

#include "basisSplines/basis.h"
#include "basisSplines/spline.h"
#include "helper.h"

namespace Bs = BasisSplines;
namespace Mt = matplot;

int main(int argc, char *argv[]) {

  std::vector<Bs::Spline> splines(2);

  // definition spline of order 3 with 4 breakpoints
  splines[0] = Bs::Spline{
      std::make_shared<Bs::Basis>(
          Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0}}, 3),
      Eigen::ArrayXd{{0.0, 0.5, 0.25, -0.3, -1.0, 0.75}}};

  // definition spline with order increased by 2
  splines[1] = Bs::Spline{splines[0].orderElevation(2)};

  // setup figure
  auto figureHandle{Mt::figure()};
  figureHandle->size(800, 600);

  // y-axis labels for each y axis
  std::array<std::string, 2> yLabels {"s(x)/1", "s_{el}(x)/1"};

  // plot all splines
  for(int cSpline{}; cSpline < splines.size(); ++cSpline) {
    auto axesHandle{
        matplot::subplot(figureHandle, splines.size(), 1, cSpline)};
    axesHandle->hold(true);
    axesHandle->grid(true);
    axesHandle->xlabel("x/1");
    axesHandle->ylabel(yLabels[cSpline]);
    Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomleft);

    plotSpline(splines[cSpline], Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1), axesHandle);
  }

  // save and show figure
  saveFigure(figureHandle, getFileName(argc, argv), getFileEnding(argc, argv));
  matplot::show();

  return 0;
}