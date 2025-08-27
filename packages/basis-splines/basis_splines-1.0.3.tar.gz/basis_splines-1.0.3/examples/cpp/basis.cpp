#include <Eigen/Core>
#include <matplot/matplot.h>

#include "basisSplines/basis.h"
#include "helper.h"

namespace Bs = BasisSplines;
namespace Mt = matplot;

int main(int argc, char *argv[]) {
  // basis of order 3 with 3 breakpoints
  const BasisSplines::Basis basis{{{0.0, 0.0, 0.0, 0.5, 0.5, 1.0, 1.0, 1.0}},
                                  3};

  // evaluate basis between -0.1 and 1.1
  const Eigen::ArrayXd points{Eigen::ArrayXd::LinSpaced(121, -0.1, 1.1)};
  const Eigen::ArrayXXd basisVals{basis(points)};

  // setup figure
  auto figureHandle{Mt::figure()};
  figureHandle->size(800, 600);

  // setup figure axis
  auto axisHandle{figureHandle->current_axes()};
  axisHandle->hold(true);
  axisHandle->ylim({-0.1, 1.1});
  axisHandle->grid(true);
  axisHandle->xlabel("x/1");
  axisHandle->ylabel("b_i(x)");
  Mt::legend(Mt::on);

  // plot each basis function
  int cCol{};
  for (auto col : basisVals.colwise())
    axisHandle
        ->plot(std::vector<double>{points.begin(), points.end()},
               std::vector<double>{col.begin(), col.end()})
        ->display_name(std::format("basis {}", cCol++));

  // save and show figure
  saveFigure(figureHandle, getFileName(argc, argv), getFileEnding(argc, argv));
  matplot::show();

  return 0;
}