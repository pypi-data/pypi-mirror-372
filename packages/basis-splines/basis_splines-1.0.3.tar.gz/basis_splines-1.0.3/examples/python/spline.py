import basisSplines as bs
from helper import helper
import matplotlib.pyplot as plt
import numpy as np


def main():
    splines = [None, None]

    # basis of order 3 with 4 breakpoints
    basis = bs.Basis(np.array([0.0, 0.0, 0.0, 0.4, 0.7, 0.7, 1.0, 1.0, 1.0]), 3)

    # first spline definition
    splines[0] = bs.Spline(basis, np.array([0.0, 0.5, 0.25, -0.3, -1.0, 0.75]))

    # second spline definition
    splines[1] = bs.Spline(basis, np.array([1.0, 0.5, 2, -3, -1.0, 0.75]))

    # plot splines
    _, axs = plt.subplots(len(splines), 2, figsize=(8, 6))
    points = np.linspace(-0.1, 1.1, 121)

    for cSpline, spline in enumerate(splines):
        ax = axs[cSpline, 0]
        ax.grid(True)
        ax.set_xlabel("$x/1$")
        ax.set_ylabel(f"$s_{cSpline}(x)/1$")
        helper.plotSpline(spline, points, ax)
        ax.legend()

    # change breakpoint at 0 to 0.3 and breakpoint at 2 to 0.8
    basis.setBreakpoints(np.array([0.3, 0.8]), np.array([0, 2]))

    # plot splines with new basis
    for cSpline, spline in enumerate(splines):
        ax = axs[cSpline, 1]
        ax.grid(True)
        ax.set_xlabel("$x/1$")
        ax.set_ylabel(f"$s_{{{cSpline},new}}(x)/1$")
        helper.plotSpline(spline, points, ax)
        ax.legend()

    plt.show()

if __name__ == "__main__":
    main()
