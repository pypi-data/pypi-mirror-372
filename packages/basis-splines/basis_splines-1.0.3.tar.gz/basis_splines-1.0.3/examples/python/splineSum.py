import basisSplines as bs
from helper import helper
import matplotlib.pyplot as plt
import numpy as np


def main():
    splines = [None, None, None]

    # definition first spline of order 3 with 4 breakpoints
    basis0 = bs.Basis(np.array([0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0]), 3)
    splines[0] = bs.Spline(basis0, np.array([0.0, 0.5, 0.25, -0.3, -1.0, 0.75]))

    # definition second spline of order 4 with 3 breakpoints
    basis1 = bs.Basis(np.array([0.0, 0.0, 0.0, 0.0, 0.2, 0.2, 1.0, 1.0, 1.0, 1.0]), 4)
    splines[1] = bs.Spline(basis1, np.array([1.0, -1.0, 0.3, 0.4, -0.1, 0.0]))

    # add two splines
    splines[2] = splines[0].add(splines[1])

    yLabels = ["$s_0(x)/1$", "$s_1(x)/1$", "$s_{0+1}(x)/1$"]

    _, axs = plt.subplots(len(splines), 1, figsize=(8, 6))
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
