"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023-2025.
All rights reserved.
"""

import itertools
import math
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle

from parityos_addons.rydberg_layout.base.rydberg_atoms import RydbergAtoms


def plot_rydberg_atoms(
    rydberg_atoms: RydbergAtoms,
    *,
    ax: Union[plt.Axes, None] = None,
    show: bool = False,
    show_qubit_labels: bool = True,
    colorbar: bool = True,
    cmap: Union[str, None] = None,
    patch_radius: Union[float, None] = None,
    plot_blockade_radii: bool = False,
    c6: float = 1.0,
    blockade_radii_plot_props: dict = None,
) -> plt.Axes:
    r"""
    Plot a :py:class:`RydbergAtoms` layout

    :param rydberg_atoms: `RydbergAtoms` layout to be plotted
    :param ax: Axes to plot in. If None (default), a new figure with axes is created for
        the plot.
    :param show: If True, the plot is immediately displayed on the screen. Otherwise, the
        `plt.show()` command can be used to display it.
    :param show_qubit_labels: If True, atoms are labelled with (parity qubit, data qubit)
        values
    :param colorbar: If True, a colorbar is plotted indicating the value of the detunings of each
        site
    :param cmap: A colormap to plot the detuning values.
    :param patch_radius: Radius for the circles to plot the atoms. If None, the radius is
        automatically calculated as the minimal distance between any two atoms.
    :param plot_blockade_radii: If True, blockade radius circles are plotted around each atom,
        defined as :math:`r_i = (c6 / \Delta_i)^{1/6}`, where :math:`\Delta_i` is the local detuning
        of each atom
    :param c6: The c6 coefficient to use for the blockade radius plot
    :param blockade_radii_plot_props: Plot properties for the blockade radius circles as dictionary.
        Properties of matplotlib.patches.Circle can be used.
    :return: The axes of the plot
    """
    # Create new figure if no axes is given
    if ax is None:
        _, ax = plt.subplots()

    # compute alpha
    alpha = min([atom.detuning.alpha for atom in rydberg_atoms.atoms])
    if np.abs(alpha) < 1e-6:
        alpha = 1.0

    # Plot layout
    x_coords = [atom.coordinate.x for atom in rydberg_atoms.atoms]
    y_coords = [atom.coordinate.y for atom in rydberg_atoms.atoms]
    detuning_plot_vals = [atom.detuning.value / alpha for atom in rydberg_atoms.atoms]

    # get minimal atom distance to define the circle size
    if patch_radius is None:
        min_squared_dist = min(
            (coord2.x - coord1.x) ** 2 + (coord2.y - coord1.y) ** 2
            for coord1, coord2 in itertools.combinations(rydberg_atoms.coordinates, r=2)
        )
        min_dist = math.sqrt(min_squared_dist)
        if min_dist == 0:
            min_dist = 1.0

        patch_radius = min_dist / 2

    # create PatchCollection
    patches = []
    for x, y, det in zip(x_coords, y_coords, detuning_plot_vals):
        circle = Circle((x, y), radius=patch_radius)
        patches.append(circle)

    # set color values by detunings
    if cmap is None:
        cmap = "cool"
    plot = PatchCollection(patches, cmap=cmap)
    plot.set_array(detuning_plot_vals)

    ax.add_collection(plot)

    _set_ax_limits(
        ax,
        np.min(x_coords) - patch_radius,
        np.max(x_coords) + patch_radius,
        np.min(y_coords) - patch_radius,
        np.max(y_coords) + patch_radius,
    )

    # Add text for qubit info or atom index info
    if show_qubit_labels:
        for atom in rydberg_atoms.atoms:
            qubit = atom.qubit
            if qubit.label == -1:
                continue

            if isinstance(qubit.label, int):
                label_to_show = qubit.label
            else:
                label_to_show = "".join(map(str, qubit.label))

            ax.text(
                atom.coordinate.x,
                atom.coordinate.y,
                label_to_show,
                ha="center",
                va="center",
                c="k",
            )

    if plot_blockade_radii and c6 is not None:
        if blockade_radii_plot_props is None:
            circle_props = {"edgecolor": ".7", "facecolor": "None", "linestyle": ":"}
        else:
            circle_props = blockade_radii_plot_props

        for atom in rydberg_atoms.atoms:
            detuning = atom.detuning.value
            if detuning < 1e-3:
                continue
            blockade_radius = (c6 / detuning) ** (1 / 6)
            circle = Circle(
                (atom.coordinate.x, atom.coordinate.y),
                radius=blockade_radius,
                **circle_props,
            )
            ax.add_patch(circle)

    # Plot properties
    ax.set_aspect("equal")
    if colorbar:
        cbar = plt.colorbar(plot, ax=ax, label=r"Detuning $\Delta/\alpha$")

        for atom in rydberg_atoms.atoms:
            cbar.ax.plot(0.5, atom.detuning.value / alpha, ".k", clip_on=False)

    ax.set_xlabel(r"x [$\mu$m]")
    ax.set_ylabel(r"y [$\mu$m]")
    ax.set_title(rf"$\alpha={alpha:g}$ [rad/$\mu$s]")

    if show:
        plt.show()

    return ax


def _set_ax_limits(
    ax: plt.Axes, x_min: float, x_max: float, y_min: float, y_max: float
) -> None:
    """
    Set axis limits given x_min, x_max, y_min, and y_max
    """
    x_min, x_max, y_min, y_max = float(x_min), float(x_max), float(y_min), float(y_max)
    ax.set_xlim(x_min - 0.02 * (x_max - x_min), x_max + 0.02 * (x_max - x_min))
    ax.set_ylim(y_min - 0.02 * (y_max - y_min), y_max + 0.02 * (y_max - y_min))
    ax.set_aspect("equal")
