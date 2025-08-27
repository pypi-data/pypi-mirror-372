import basisSplines as bs
from helper import helper
import matplotlib.pyplot as plt
import numpy as np


def main():

    # basis of order 3 with 4 breakpoints
    basis = bs.Basis(np.array([0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0]), 3)

    # first spline definition
    spline = bs.Spline(
        basis,
        np.array(
            [[-0.8, 0.0], [-0.2, 1.0], [0.3, -0.5], [1.0, 0.3], [1.0, 0.6], [0.0, 0.8]]
        ),
    )

    points = np.linspace(0.0, 1.0, 101)

    nDims = 2

    # plot splines along each dimension
    _, axs = plt.subplots(nDims, 1)

    for cDim, ax in enumerate(axs):

        helper.plotSpline(spline, points, ax, cDim)

        ax.legend()
        ax.grid()
        ax.set_xlabel("$x/1$")
        ax.set_ylabel(f"$s_{cDim}(x)$")

    # plot 2-dimensional spline
    _, ax = plt.subplots()

    helper.plotSpline2d(spline, points, ax, (0, 1))

    ax.legend()
    ax.grid()
    ax.set_xlabel("$s_0(x)$")
    ax.set_ylabel("$s_1(x)$")

    plt.show()


if __name__ == "__main__":
    main()
