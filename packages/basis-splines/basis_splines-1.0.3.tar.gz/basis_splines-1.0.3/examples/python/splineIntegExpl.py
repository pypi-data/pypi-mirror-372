import basisSplines as bs
from helper import helper
import matplotlib.pyplot as plt
import numpy as np


def main():
    splines = [None, None]

    # basis of order 3 with 4 breakpoints
    basis = bs.Basis(np.array([0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0]), 3)

    # spline definition
    splines[0] = bs.Spline(basis, np.array([0.0, 0.5, 0.25, -0.3, -1.0, 0.75]))

    # spline integral (explicit transformation)
    basisInteg = bs.Basis(np.array([]), 0)  # create empty basis object
    trf = basis.integral(basisInteg)
    splines[1] = bs.Spline(basisInteg, trf @ splines[0].getCoefficients())

    # y-axis labels for each y axis
    yLabels = ["$s(x)/1$", "$Is(x)/1$"]

    fig, axs = plt.subplots(len(splines), 1, figsize=(8, 6))
    points = np.linspace(-0.1, 1.1, 121)

    for cSpline, spline in enumerate(splines):
        ax = axs[cSpline]
        ax.grid(True)
        ax.set_xlabel("$x/1$")
        ax.set_ylabel(yLabels[cSpline])
        helper.plotSpline(spline, points, ax)
        ax.legend()

    plt.show()


if __name__ == "__main__":
    main()
