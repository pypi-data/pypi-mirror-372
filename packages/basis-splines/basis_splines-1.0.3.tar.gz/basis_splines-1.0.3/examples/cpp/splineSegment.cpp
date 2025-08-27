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
      Eigen::ArrayXd{{0.0, 0.0, 0.0, 0.0, 0.4, 0.7, 1.0, 1.0, 1.0, 1.0}}, 4)};

  // spline of order 3
  Bs::Spline spline{basis,
                          Eigen::ArrayXd{{0.0, 0.5, 0.25, -0.3, -1.0, 0.75}}};

  // setup figure
  auto figureHandle{Mt::figure()};
  figureHandle->size(800, 600);

  // plot spline
  int nAxes{3};
  auto axesHandle{Mt::subplot(figureHandle, nAxes, 1, 0)};
  axesHandle->hold(true);
  axesHandle->grid(true);
  axesHandle->ylim({-1.0, 1.0});
  axesHandle->xlabel("x/1");
  axesHandle->ylabel("s(x)/1");
  Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomleft);
  plotSpline(spline, Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1), axesHandle);

  // determine segment spline
  const Bs::Spline splineSeg{spline.getSegment(1, 1)};

  // plot spline segment
  axesHandle = Mt::subplot(figureHandle, nAxes, 1, 1);
  axesHandle->hold(true);
  axesHandle->grid(true);
  axesHandle->ylim({-1.0, 1.0});
  axesHandle->xlabel("x/1");
  axesHandle->ylabel("s_{seg}(x)/1");
  Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomleft);
  plotSpline(splineSeg, Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1), axesHandle);

  // determine clamped segment spline
  const Bs::Spline splineClamped{splineSeg.getClamped()};

  // plot clamped segment spline
  axesHandle = Mt::subplot(figureHandle, nAxes, 1, 2);
  axesHandle->hold(true);
  axesHandle->grid(true);
  axesHandle->ylim({-1.0, 1.0});
  axesHandle->xlabel("x/1");
  axesHandle->ylabel("s_{clamp}(x)/1");
  Mt::legend(Mt::on)->location(Mt::legend::general_alignment::bottomleft);
  plotSpline(splineClamped, Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1),
             axesHandle);

  // save and show figure
  saveFigure(figureHandle, getFileName(argc, argv), getFileEnding(argc, argv));
  Mt::show();

  return 0;
}