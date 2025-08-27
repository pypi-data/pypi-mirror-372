import basisSplines as bs
from helper import helper
import matplotlib.pyplot as plt
import numpy as np


def main():
    # basis of order 4 with 4 breakpoints
    basis = bs.Basis(np.array([0.0, 0.0, 0.0, 0.0, 0.4, 0.7, 1.0, 1.0, 1.0, 1.0]), 4)

    # spline of order 3
    spline = bs.Spline(basis, np.array([0.0, 0.5, 0.25, -0.3, -1.0, 0.75]))

    # plot spline
    nAxes = 3
    _, axs = plt.subplots(nAxes, 1, figsize=(8, 6))
    points = np.linspace(-0.1, 1.1, 121)

    axs[0].grid(True)
    axs[0].set_ylim([-1.0, 1.0])
    axs[0].set_xlabel("$x/1$")
    axs[0].set_ylabel("$s(x)/1$")
    helper.plotSpline(spline, points, axs[0])
    axs[0].legend()

    # determine segment spline
    splineSeg = spline.getSegment(1, 1)

    # plot spline segment
    axs[1].grid(True)
    axs[1].set_ylim([-1.0, 1.0])
    axs[1].set_xlabel("$x/1$")
    axs[1].set_ylabel("$s_{seg}(x)/1$")
    helper.plotSpline(splineSeg, points, axs[1])
    axs[1].legend()

    # determine clamped segment spline
    splineClamped = splineSeg.getClamped()

    # plot clamped segment spline
    axs[2].grid(True)
    axs[2].set_ylim([-1.0, 1.0])
    axs[2].set_xlabel("$x/1$")
    axs[2].set_ylabel("$s_{clamp}(x)/1$")
    helper.plotSpline(splineClamped, points, axs[2])
    axs[2].legend()

    plt.show()


if __name__ == "__main__":
    main()
