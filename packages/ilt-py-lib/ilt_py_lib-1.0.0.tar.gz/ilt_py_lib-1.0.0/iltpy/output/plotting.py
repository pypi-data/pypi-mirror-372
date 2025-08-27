# ILTpy : A python library for inverse Laplace transform of one dimensional and multidimensional data
# Copyright (c) 2025 Davis Thomas Daniel, Josef Granwehr and other contributors
# Licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0)
#
# This file is part of ILTpy.
#
# ILTpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ILTpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ILTpy. If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/env python

# imports
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec


def set_plot_param():
    plt.rcParams.update(
        {
            "axes.labelsize": 12,
            "axes.titlesize": 14,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "lines.linewidth": 1,
            "lines.markersize": 4,
            "grid.linestyle": "--",
            "grid.linewidth": 0.5,
            "grid.color": "gray",
            "savefig.dpi": 300,
            "figure.figsize": [6, 4],
            "figure.dpi": 120,
            "xtick.minor.visible": True,
            "ytick.minor.visible": True,
            "xtick.minor.size": 4,
            "ytick.minor.size": 4,
            "xtick.minor.width": 0.55,
            "ytick.minor.width": 0.55,
            "ytick.major.width": 0.75,
            "xtick.major.width": 0.75,
            "xtick.minor.top": True,
            "ytick.minor.right": True,
            "xtick.major.size": 6,
            "ytick.major.size": 6,
        }
    )


def iltplot(
    iltdata,
    dim_ndim=None,
    transform_g=False,
    negative_g=False,
    transpose_residuals=False,
    scale_residuals=True,
):
    """
    Generate plots from inverted iltdata.

    Parameters
    ----------
    iltdata : IltData
        IltData instance after inversion.

    dim_ndim : ndarray
        Numpy array defining the second dimension

    transform_g : bool, default False
        If True, the following transformation is applied to g in case of 2D data :
        `g = np.sign(g) * np.sqrt(np.abs(g))`

    negative_g : bool, default False
        If True, the negative of g is plotted.

    transpose_residuals : bool, default False
        If True, transpose of residuals are plotted.

    """
    if not iltdata.inverted:
        raise RuntimeError(
            "iltplot can only be used after the dataset has been inverted."
        )

    if iltdata.data.ndim not in [1, 2]:
        raise ValueError("iltplot can only be used with up to 2D datasets.")

    set_plot_param()

    # set up the figure
    fig = plt.figure(figsize=(5.30833333, 6.30833333))
    gs = GridSpec(3, 2, figure=fig)
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1:, 0:])
    ax2 = fig.add_subplot(gs[0, 1])

    # Get data to plot
    data = iltdata.data
    fit = iltdata.fit
    g = iltdata.g
    t = iltdata.t
    tau = np.log10(iltdata.tau[0].flatten())

    if iltdata.sigma is not None and scale_residuals is True:
        residuals = iltdata.residuals / iltdata.sigma
    else:
        residuals = iltdata.residuals

    if transpose_residuals:
        residuals = residuals.T


    if iltdata.ndim == 2:
        # For 2D data, plot sum
        if transpose_residuals:
            data = data.T.sum(axis=-1)
            fit = fit.T.sum(axis=-1)
        else:
            data = data.sum(axis=-1)
            fit = fit.sum(axis=-1)

        # Analyse residuals
        r_mean = residuals.mean(axis=-1)
        r_std = residuals.std(axis=-1)

        # Check for user-defined dim_ndim (e.g. ppm axis)
        if dim_ndim is None:
            if iltdata.base_tau[1] != 0:
                dim_ndim = np.log10(iltdata.tau[1].flatten())
            else:
                dim_ndim = iltdata.tau[1].flatten()

        # Flip g for inversion recovery-like experiments
        if negative_g:
            g = g * -1

        # Apply transformation to g, sutiable for spotting weak features
        if transform_g:
            g = np.sign(g) * np.sqrt(np.abs(g))

        # Pcolor plot in ax1
        c = ax1.pcolor(dim_ndim, tau, g, cmap="jet")
        fig.colorbar(c, ax=ax1)

    elif iltdata.ndim == 1:
        r_mean = [residuals.mean()] * len(t[0].flatten())
        r_std = [residuals.std()] * len(t[0].flatten())

        # Flip g if requested, useful in case of inversion-recovery like experiments
        if negative_g:
            g = g * -1

        # Plot g in ax1
        if iltdata.sb[0] is True:
            ax1.plot(
                np.log10(iltdata.tau[0]).flatten(), g[0:-1], color="green", marker="."
            )
        else:
            ax1.plot(np.log10(iltdata.tau[0]).flatten(), g, color="green", marker=".")
        ax1.grid(True)

    else:
        raise ValueError("iltplot cannot be used for datasets with ndim > 2.")

    # formatting plots
    ax2.plot(residuals, color="grey", alpha=0.5)
    ax2.plot(r_mean, color="black", label=r"$\overline{r}$")
    ax2.plot(r_std, "--m", label=r"$\sigma_{r}$")
    ax2.legend(
        frameon=False,
        fontsize=8,
        labelspacing=0.1,
        loc="upper right",
        handlelength=1.5,
        bbox_to_anchor=(1, 1.38),
    )
    ax2.set_title(r"$r = \mathbf{Kg}-\mathbf{s}$", fontsize=12)
    ax2.grid(True)
    if transpose_residuals:
        ax0.plot(t[1].flatten(), data, "k", linewidth=1.5)
        ax0.plot(t[1].flatten(), fit, "--r")
    else:
        ax0.plot(t[0].flatten(), data, "k", linewidth=1.5)
        ax0.plot(t[0].flatten(), fit, "--r")
    ax0.grid(True)

    xlabel = "t"
    label_tau = "log(" r"$\tau$" + ")"

    if iltdata.ndim > 1:
        ax1.set_ylabel(label_tau)
        if iltdata.base_tau[1] != 0:
            ax1.set_xlabel(label_tau)
    else:
        ax1.set_xlabel(label_tau)
    ax0.set_xlabel(xlabel)

    # Adjust layout
    fig.tight_layout()

    return fig, [ax0, ax1, ax2]
