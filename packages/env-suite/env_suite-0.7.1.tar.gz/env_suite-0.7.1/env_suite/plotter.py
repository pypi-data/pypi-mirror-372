"""
A module for plotting
"""

# Imports
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, cdist, squareform
from scipy import constants

from .utils import masses

# Constants
FONT_SIZE = 8
LINE_WIDTH = 0.5
EVCONV = 1e10 * constants.e / (4 * np.pi * constants.epsilon_0)


def init_matplotlib():
    """
    Initializes matplotlib settings
    """

    plt.rc(
        "font",
        family="serif",
        serif="Times New Roman",
        size=FONT_SIZE,
    )

    plt.rc(
        "mathtext",
        fontset="cm",
        )

    plt.rc(
        "axes",
        linewidth=LINE_WIDTH,
        labelsize=FONT_SIZE,
    )

    plt.rc(
        "lines",
        linewidth=LINE_WIDTH,
    )

    tickparams = {
            'major.width': LINE_WIDTH,
            'minor.width': LINE_WIDTH,
            'direction': 'in',
    }

    plt.rc('xtick', **tickparams)
    plt.rc('ytick', **tickparams)


def evaluate_potential(coords: np.ndarray,
                       q: np.ndarray,
                       num_points: int,
                       N: int):

    """
    Evalulates the potential on a 2D grid in the xy plane

    Parameters
    ----------
    coords : np.ndarray
        The coordinates of the exact charge region and 
        the parameter region
    q : np.ndarray
        The charges of the exact charge region and 
        the parameter region
    num_points : int
        The number of points in the grid
    N : int
        The dimension of the grid

    Returns
    -------
    x : np.ndarray
        The x coordinates of the grid
    y : np.ndarray
        The y coordinates of the grid
    z : np.ndarray
        The potential on the grid
    """

    data = np.hstack((coords, q.reshape(-1, 1)))

    x = np.linspace(-N[0], N[0], num_points)
    y = np.linspace(-N[1], N[1], num_points)
    x, y = np.meshgrid(x, y)
    z = np.zeros_like(x)

    for i in range(len(x)):
        for j in range(len(x)):
            for k in range(len(data)):
                z[i, j] += data[k, 3] / np.sqrt((x[i, j] - data[k, 0])**2 +
                                                (y[i, j] - data[k, 1])**2 +
                                                (data[k, 2])**2)

    return x, y, z


def plot_potential(x: np.ndarray,
                   y: np.ndarray,
                   z: np.ndarray,
                   num_contours: int,
                   show: bool,
                   ):

    """
    Plots the potential on a 2D grid in the xy plane

    Parameters
    ----------
    x : np.ndarray
        The x coordinates of the grid
    y : np.ndarray
        The y coordinates of the grid
    z : np.ndarray
        The potential on the grid
    num_contours : int
        The number of contours to plot
    show : bool
        Whether to show the plot or not
    """

    # Initialize matplotlib settings
    init_matplotlib()

    # Plot the potential
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.contourf(x, y, z, num_contours, cmap='viridis')
    ax.set_xlabel('x/ Å')
    ax.set_ylabel('y/ Å')
    ax.set_aspect('equal')
    cbar = fig.colorbar(ax.contourf(x, y, z, num_contours, cmap='viridis'))
    cbar.set_label('Potential/ eV')
    fig.savefig('potential.png', dpi=500)
    if show:
        plt.show()


def plot_3d_model(sphere,
                  param,
                  qm,
                  ):
    """
    Plots the 3D model of the system

    Parameters
    ----------
    sphere : np.ndarray
        The exact charge region
    param : np.ndarray
        The parameter region
    qm : np.ndarray
        The quantum mechanical region
    """

    init_matplotlib()

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # plot the coordiates as a 3d scatter
    ax.scatter(sphere[:, 0], sphere[:, 1], sphere[:, 2], c='r',
               marker='o', alpha=0.12, s=3)
    ax.scatter(param[:, 0], param[:, 1], param[:, 2], c='b',
               marker='o', alpha=0.12, s=3)
    ax.scatter(qm[:, 0], qm[:, 1], qm[:, 2], c='red', marker='o',
               alpha=1, s=5)

    ax.set_xlabel('X / Å')
    ax.set_ylabel('Y / Å')
    ax.set_zlabel('Z / Å')
    ax.legend(['Exact charge region', 'Paramamter region', 'Quantum mechanical region'])
    ax.set_aspect('equal')

    fig.tight_layout()

    # draw onto canvas
    plt.show()
