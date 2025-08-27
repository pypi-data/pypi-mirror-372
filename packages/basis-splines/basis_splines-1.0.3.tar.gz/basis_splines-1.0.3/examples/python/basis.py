import basisSplines as bs
import matplotlib.pyplot as plt
import numpy as np


def main():
    # basis of order 3 with 3 breakpoints
    basis = bs.Basis(np.array([0.0, 0.0, 0.0, 0.5, 0.5, 1.0, 1.0, 1.0]), 3)

    # evaluate basis between -0.1 and 1.1
    points = np.linspace(-0.1, 1.1, 121)
    basisVals = basis(points)

    _, ax = plt.subplots()
    ax.grid()
    ax.set_xlabel("$x/1$")
    ax.set_ylabel("$b_i(x)$")

    for cRow, row in enumerate(basisVals.T):
        ax.plot(points, row, label=f"$b_{cRow}(x)$")

    ax.legend()
    plt.show()

if __name__ == "__main__":
    main()