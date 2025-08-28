# ParityQC © 2025. See the LICENSE file in the top level directory for details.
from matplotlib import pyplot as plt

from parityos_addons.rydberg_layout.utils.rydberg_atom_state import RydbergAtomState


def plot_rydberg_state(
    state: RydbergAtomState,
    *,
    ax: plt.Axes = None,
    legend: bool = True,
    show: bool = False,
    **kwargs,
) -> plt.Axes:
    """Plot a classical configuration (state) of Rydberg atoms. Atoms in the ground (Rydberg) state
    are plotted with empty (filled) markers

    :param state: Classical configuration (state) to plot.
    :param ax: Axes to plot in. If None (default), a new figure with axes is created for
        the plot.
    :param legend: If True, plot a legend, otherwise not.
    :param show: If True, the plot is immediately displayed on the screen. Otherwise, the
        `plt.show()` command can be used to display it.
    :param kwargs: keyword arguments to define plot properties
    :return: The axes of the plot
    """
    if ax is None:
        fig, ax = plt.subplots(constrained_layout=True)

    empty_marker = {"marker": "o", "mec": "r", "mfc": "None"}
    full_marker = {"marker": "o", "mec": "r", "mfc": "r"}

    for atom, bit in state.atom_bit_map.items():
        marker = full_marker if bit else empty_marker
        label = "rydberg" if bit else "ground"
        ax.plot(
            atom.coordinate.x,
            atom.coordinate.y,
            ls="None",
            **marker,
            **kwargs,
            label=label,
        )

    ax.set_aspect("equal")
    ax.set_title(f"state = |{state.to_bit_string()}>")

    if legend:
        handles, labels = ax.get_legend_handles_labels()
        label_to_handle = dict(zip(labels, handles))  # makes labels unique
        ax.legend(label_to_handle.values(), label_to_handle.keys())

    if show:
        plt.show()

    return ax
