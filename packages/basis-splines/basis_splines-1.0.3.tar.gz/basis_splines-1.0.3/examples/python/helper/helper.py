from typing import Tuple

import basisSplines as bs
import matplotlib.pyplot as plt
import numpy as np


def plotSpline(
    spline: bs.Spline, points: np.ndarray, axesHandle: plt.Axes, dim: int = 0
):
    splineVals = spline(points)[:, dim]
    axesHandle.plot(points, splineVals, label="spline")

    greville = spline.basis().greville()
    coefficients = spline.getCoefficients()[:, dim]
    axesHandle.plot(
        greville,
        coefficients,
        "-o",
        label="coefficients",
        markersize=10,
        fillstyle="none",
    )

    breakpoints, _ = spline.basis().getBreakpoints()
    splineValsBps = spline(breakpoints)[:, dim]
    axesHandle.plot(breakpoints, splineValsBps, "D", label="breakpoints")


def plotSpline2d(
    spline: bs.Spline, points: np.ndarray, axesHandle: plt.Axes, dims: Tuple[int, int]
):
    splineVals = spline(points)[:, dims]
    axesHandle.plot(splineVals[:, 0], splineVals[:, 1], label="spline")

    coefficients = spline.getCoefficients()[:, dims]
    axesHandle.plot(
        coefficients[:, 0],
        coefficients[:, 1],
        "-o",
        label="coefficients",
        markersize=10,
        fillstyle="none",
    )

    breakpoints, _ = spline.basis().getBreakpoints()
    splineValsBps = spline(breakpoints)[:, dims]
    axesHandle.plot(splineValsBps[:, 0], splineValsBps[:, 1], "D", label="breakpoints")
