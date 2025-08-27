#include <Eigen/Core>
#include <matplot/matplot.h>
#include <string>

#include "basisSplines/basis.h"
#include "basisSplines/spline.h"
#include "helper.h"

namespace Bs = BasisSplines;
namespace Mt = matplot;

int main(int argc, char *argv[]) {

  // basis of order 3 with 4 breakpoints
  std::shared_ptr<Bs::Basis> basis{std::make_shared<Bs::Basis>(
      Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0}}, 3)};

  // first spline definition
  const Bs::Spline spline{basis, Eigen::ArrayXXd{{-0.8, 0.0},
                                                 {-0.2, 1.0},
                                                 {0.3, -0.5},
                                                 {1.0, 0.3},
                                                 {1.0, 0.6},
                                                 {0.0, 0.8}}};

  // setup figure
  auto figureHandle{Mt::figure()};
  figureHandle->size(800, 600);

  // plot splines along each dimension
  for (int cDim{}; cDim < spline.dim(); ++cDim) {
    // create axis handle for each spline dimension
    auto axesHandle{Mt::subplot(figureHandle, spline.dim(), 1, cDim)};

    // setup axes
    axesHandle->hold(true);
    axesHandle->grid(true);
    axesHandle->xlabel("x/1");
    axesHandle->ylabel(std::format("s_{}(x)/1", cDim));
    axesHandle->ylim({-1.1, 1.1});
    Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomright);

    // plot single spline dimension
    plotSpline(spline, Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1), axesHandle,
               cDim);
  }

  // save figure with individual spline dimensions
  std::string name{std::format("{}_singleDims", getFileName(argc, argv))};
  saveFigure(figureHandle, name, getFileEnding(argc, argv));

  // plot 2-dimensional spline
  figureHandle = Mt::figure();
  figureHandle->size(800, 600);

  // setup axis
  auto axesHandle{figureHandle->current_axes()};
  axesHandle->hold(true);
  axesHandle->grid(true);
  axesHandle->xlabel("s_0(x)/1");
  axesHandle->ylabel("s_1(x)/1");
  axesHandle->xlim({-0.9, 1.1});
  axesHandle->ylim({-0.7, 1.1});
  Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomleft);

  // plot 2 spline dimensions
  plotSpline2d(spline, Eigen::ArrayXd::LinSpaced(121, 0.0, 1.0), axesHandle,
               {{0, 1}});

  // save figure with 2 spline dimensions
  name = std::format("{}_allDims", getFileName(argc, argv));
  saveFigure(figureHandle, name, getFileEnding(argc, argv));

  // show figures
  Mt::show();

  return 0;
}