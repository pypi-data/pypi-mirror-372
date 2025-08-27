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
import pprint
import json
import warnings
import numpy as np
from pathlib import Path
from copy import deepcopy
from datetime import datetime
from scipy.sparse import issparse

# iltpy
from iltpy import __version__

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")


def iltreport(
    iltdata, filepath=None, save_arrays=False, level=0, parameters_to_file=False
):
    """
    Generates reports from an IltData instance

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    filepath : str, optional
        Path where the results should be saved. If None, results are saved in the current working directory,
        If no filename is specified in the path, a filename based on timestamp is generated.
        If there is no extension specified for the file in the filepath, .txt is used by default.
    save_arrays : bool, by default False
        Whether to also output a file with numpy arrays in npz format.
    level : int, optional
        Controls the depth of saved data. Default is 0.
        - 0: Save attributes of type `np.ndarray`.
        - 1: Additionally, save lists containing only `np.ndarray` elements.
        - 2: Additionally, save sparse matrices (converted to dense arrays).
    """
    if iltdata.inverted:
        report_dict, out_file_path, folder = _generate_report_dict(iltdata, filepath)
        _write_report_to_file(report_dict, parameters_to_file)
        if save_arrays:
            _write_array_to_file(iltdata, out_file_path, level)
        print(f"Results saved at {folder}")
    else:
        raise ValueError("This dataset is not inverted. Use IltData.invert().")


def _generate_report_dict(iltdata, filepath=None):
    """
    Sets up a report dictionary to be written to file.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    filepath : str, optional
        Path where the results should be saved. If None, results are saved in the current working directory,
        If no filename is specified in the path, a filename based on timestamp is generated.
        If there is no extension specified for the file in the filepath, .txt is used by default.
    """
    report_dict = {
        "g": None,
        "fit": None,
        "residuals": None,
        "data": None,
        "sigma": None,
        "g_guess": None,
        "dim_ndim": None,
        "parameters": None,
    }

    # build dictionary
    report_dict["g"] = iltdata.g
    report_dict["fit"] = iltdata.fit
    report_dict["residuals"] = iltdata.residuals
    report_dict["data"] = iltdata.data
    report_dict["t"] = [i.flatten() for i in iltdata.t]
    report_dict["tau"] = [i.flatten() for i in iltdata.tau]
    report_dict["parameters"] = deepcopy(iltdata.fit_dict)

    if iltdata.sigma is not None:
        report_dict["sigma"] = iltdata.sigma
    if iltdata.dim_ndim is not None:
        report_dict["dim_ndim"] = iltdata.dim_ndim.flatten()
    if iltdata.g_guess is not None:
        report_dict["g_guess"] = iltdata.g_guess.flatten()

    if iltdata.ndim > 2:
        report_dict["g"] = np.reshape(
            report_dict["g"],
            (report_dict["g"].shape[0], np.prod(report_dict["g"].shape[1:])),
        )
        report_dict["fit"] = np.reshape(
            report_dict["fit"],
            (report_dict["fit"].shape[0], np.prod(report_dict["fit"].shape[1:])),
        )
        report_dict["residuals"] = np.reshape(
            report_dict["residuals"],
            (
                report_dict["residuals"].shape[0],
                np.prod(report_dict["residuals"].shape[1:]),
            ),
        )
        report_dict["data"] = np.reshape(
            report_dict["data"],
            (report_dict["data"].shape[0], np.prod(report_dict["data"].shape[1:])),
        )
        if iltdata.sigma is not None:
            report_dict["sigma"] = np.reshape(
                report_dict["sigma"],
                (
                    report_dict["sigma"].shape[0],
                    np.prod(report_dict["sigma"].shape[1:]),
                ),
            )

    # resolve filepath
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if filepath is None:
        filepath = Path.cwd() / f"iltpy_{timestamp}.txt"
    else:
        filepath = Path(filepath)
        if filepath.exists() and filepath.is_dir():
            filepath = filepath / f"iltpy_{timestamp}.txt"
        elif filepath.name == "":
            filepath = filepath / f"iltpy_{timestamp}.txt"
        elif filepath.suffix == "":
            filepath = filepath.with_suffix(".txt")

    if not filepath.parent.exists():
        raise OSError(f"Folder does not exist: {filepath.parent}")

    report_dict["filepath"] = filepath
    report_dict["inversion_time"] = iltdata.inversion_time
    report_dict["initialization_time"] = iltdata.initialization_time

    return (
        report_dict,
        report_dict["filepath"],
        str(report_dict["filepath"].absolute().parent),
    )


def _write_report_to_file(report_dict, parameters_to_file):
    """
    Write results to file from a report dictionary.

    Parameters
    ----------
    report_dict : dict
        A dictionary containing the results to be saved.
    """
    with open(str(report_dict["filepath"]), "w") as f:
        f.write("# --- ILTPY ---\n")
        f.write(f"# ILTpy report generated on {datetime.now()}\n")
        f.write(f"# ILTpy version : {__version__}\n")
        f.write(
            f"# Time taken for initialization : {report_dict['initialization_time']} seconds\n"
        )
        f.write(
            f"# Time taken for inversion : {report_dict['inversion_time']} seconds\n"
        )
        f.write("# --- ---\n")

    with open(str(report_dict["filepath"]), "a") as f:
        f.write("# --- ARRAYS ---\n")
        # data
        comments = f"\nData\nShape : {report_dict['data'].shape}\n"
        np.savetxt(f, report_dict["data"], header=comments)

        # t
        for idx, t_array in enumerate(report_dict["t"]):
            comments = f"\nT\nDim {idx}\nShape : {t_array.shape}\n"
            np.savetxt(f, t_array, header=comments)

        # tau
        for idx, tau_array in enumerate(report_dict["tau"]):
            tau_array = tau_array.flatten()
            comments = f"\nTAU\nDim {idx}\nShape : {tau_array.shape}\n"
            np.savetxt(f, tau_array, header=comments)

        # g
        comments = f"\nG\nShape : {report_dict['g'].shape}\n"
        np.savetxt(f, report_dict["g"], header=comments)

        # fit
        comments = f"\nFIT\nShape : {report_dict['fit'].shape}\n"
        np.savetxt(f, report_dict["fit"], header=comments)

        # RESIDUALS
        comments = f"\nRESIDUALS\nShape : {report_dict['residuals'].shape}\n"
        np.savetxt(f, report_dict["residuals"], header=comments)

        # dim ndim
        if report_dict["dim_ndim"] is not None:
            comments = f"\nDIM_NDIM\nShape : {report_dict['dim_ndim'].shape}\n"
            np.savetxt(f, report_dict["dim_ndim"], header=comments)

        # sigma
        if report_dict["sigma"] is not None:
            comments = f"\nSIGMA\nShape : {report_dict['sigma'].shape}\n"
            np.savetxt(f, report_dict["sigma"], header=comments)

        # g_guess
        if report_dict["g_guess"] is not None:
            comments = f"\nG_GUESS\nShape : {report_dict['g_guess'].shape}\n"
            np.savetxt(f, report_dict["g_guess"], header=comments)

        f.write("# --- ---\n")

        # PARAMETERS
        p_dict = report_dict["parameters"]

        f.write("# --- KERNEL ---\n")
        if not isinstance(p_dict["kernel"], list):
            p_dict["kernel"] = [p_dict["kernel"]]
        for k in range(len(p_dict["kernel"])):
            kernel_name = (
                p_dict["kernel"][k]
                if type(p_dict["kernel"][k]) is str
                else p_dict["kernel"][k].name
            )
            f.write(f"# Kernel name Dim {k} : {kernel_name}\n")
            if type(p_dict["kernel"][k]) is not str:
                f.write(
                    f"# Kernel function Dim {k} : {p_dict['kernel'][k].kernel_str}\n"
                )
            else:
                kernel_func_warn = f"Unable to report kernel function in Dim {k}."
                warnings.warn(kernel_func_warn)
        f.write("# --- ---\n")

        # remove parameters which are already reported already
        p_dict.pop("tau", None)
        p_dict.pop("kernel", None)
        p_dict.pop("Cz", None)
        p_dict.pop("sigma", None)
        p_dict.pop("dim_ndim", None)
        p_dict.pop("g_guess", None)

        f.write("# --- PARAMETERS ---\n")
        f.write(pprint.pformat(p_dict, sort_dicts=False))
        if parameters_to_file:
            with open(str(report_dict["filepath"].with_suffix(".param")), "w") as f2:
                json.dump(p_dict, f2, indent=0)
        f.write("\n")
        f.write("# --- ---\n")

        f.write("# --- END OF REPORT ---\n")


def _write_array_to_file(iltdata, out_file_path, level=0):
    """
    Save array-like attributes of an `IltData` object to an NPZ file.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    out_file_path : str
        Path (without extension) where the NPZ file will be saved.
    level : int, optional
        Controls the depth of saved data. Default is 0.
        - 0: Save attributes of type `np.ndarray`.
        - 1: Additionally, save lists containing only `np.ndarray` elements.
        - 2: Additionally, save sparse matrices (converted to dense arrays).

    Notes
    -----
    - Ensures compatibility with sparse matrices by converting them to dense at level 2.
    - Keys for list elements are suffixed with `_dim<index>`.
    - The output file is compressed at level 2.

    Raises
    ------
    ValueError
        If `level` is not 0, 1, or 2.
    """

    if level not in [0, 1, 2]:
        raise ValueError("level must be one of 0, 1, or 2.")

    f = vars(iltdata)
    array_dict = {}
    for key in f.keys():
        if isinstance(f[key], np.ndarray) and level > -1:
            array_dict[key] = f[key]
        elif isinstance(f[key], list) and level > 0:
            if all([isinstance(i, np.ndarray) for i in f[key]]):
                for idx, j in enumerate(f[key]):
                    array_dict[key + "_dim" + str(idx)] = j
        elif issparse(f[key]) and level == 2:
            array_dict[key] = f[key].todense()

    arr_file_path = out_file_path.with_suffix(".npz")
    if level == 2:
        np.savez_compressed(arr_file_path, **array_dict)
    else:
        np.savez(arr_file_path, **array_dict)
