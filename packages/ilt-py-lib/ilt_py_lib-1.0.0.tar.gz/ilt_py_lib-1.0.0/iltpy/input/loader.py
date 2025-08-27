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
import warnings
import logging
import numpy as np
from pathlib import Path

# iltpy
from iltpy.fit.inversion import IltData

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")
warnings.simplefilter("always", UserWarning)

# logging
logger = logging.getLogger("iltpy_logger")


def _load_txt(data_path):
    """

    Read data stored as txt files into IltData format.
    Folder must contain :
    one data file called 'data.txt' and dimension files. See folder structure below.

    /data.txt ->contains up to 2-dimensional data
    /dim1.txt
    /dim2.txt -> in case of 2D data

    Parameters
    ----------
    data_path : str
        Path to the directory containing text files, requires filenames in a valid format.

    Returns
    -------
    IltData
        An IltData object.

    Raises
    ------
    ValueError
        Raise if data_path is not provided as a string.
    FileNotFoundError
        Raised if data.txt is not found.
    """
    if not isinstance(data_path, str):
        raise ValueError("filepath must be provided as a string.")

    filepath = Path(data_path).resolve(strict=True)

    # initialize data dict
    data_dict = {
        "filepath": filepath,
        "dataset_type": "TXT",
        "data": None,
        "dims": None,
    }

    # Check if data.txt file is present
    if not (filepath / "data.txt").exists():
        raise FileNotFoundError(f"data.txt was not found at {str(filepath)}")

    # Order the dim files according to the dimension index found in the dim file names.
    data = np.loadtxt(str(filepath / "data.txt"))
    dim_files = sorted(filepath.glob("dim*.txt"))
    dims = [np.loadtxt(dim_file) for dim_file in dim_files]
    dim_shapes = tuple([max(dim.shape) for dim in dims])

    # Check if number of elements and shapes are consistent.
    if np.prod(dim_shapes) != np.prod(data.shape):
        raise ValueError(
            f"Shape mismatch: total elements in data ({data.shape}) do not match size of dimensions {dim_shapes}"
        )
    if dim_shapes != data.shape:
        raise ValueError(
            f"Shape mismatch: data.shape {data.shape} does not match size of dimensions {dim_shapes}"
        )

    # assign data and dims
    data_dict["dims"] = dims
    data_dict["data"] = data

    return IltData(data_dict)


def iltload(data=None, t=None, f=None, data_path=None):
    """
    Load data from various formats and output an IltData object.

    Parameters
    ----------
    data_path : str, optional
        Path to the directory containing text files, requires filenames in a valid format.
        If `None` then `data` and `t` should be provided. Default: `None`
    data : ndarray, optional
        1D or 2D data Data as a numpy array.
        If `None` then `data_path` must be provided. Default: `None`
    t : list of arrays or ndarray, optional
        Input Sampling array corresponding to each dimension e.g. in the case of NMR inversion recovery measurments, t could be the list of delays.
        If `None` then `data_path` must be provided. Default: `None`
    f : list of arrays or ndarray, only valid in case of impedance data
        Sampling vector corresponding to each dimension in frequency units.
        If `None` then `data_path` must be provided. Default: `None`

    Returns
    -------
    iltdata : IltData
        An instance of `IltData`.

    """
    if data_path is None:
        logger.debug("No data path given, checking if data and t are given")
        # for impedance, f can be provided instead of t
        t = f if f is not None and t is None else t

        if data is not None and t is not None:
            logger.debug("data and t were given.")
            data_dict = {}
            data_dict["dataset_type"] = "ndarray"
            data_dict["data"] = data

            if not isinstance(t, list):
                if isinstance(t, np.ndarray):
                    t = [t]
                    logger.debug("Converted parameter t to a list.")
                else:
                    raise ValueError(f"Expected t as a 1D numpy array, got {type(t)}")
            else:
                if not all(isinstance(t_array, np.ndarray) for t_array in t):
                    raise TypeError(
                        "t must be a list of numpy arrays or a single 1D numpy array."
                    )

            data_dict["dims"] = t
            logger.debug("Setting filepath to current working directory.")
            data_dict["filepath"] = Path().cwd()

            return IltData(data_dict)
        else:
            raise ValueError(
                "Either the `data_path` or both `data` and `t` must be provided."
            )

    else:
        logger.debug("data path was given: %s", data_path)
        if Path(data_path).exists():
            data_path = Path(data_path)
            if (data_path / "data.txt").exists() and (data_path / "dim1.txt").exists():
                logger.debug("data.txt and dim1.txt was found at the filepath.")
                iltdata = _load_txt(str(data_path))

                return iltdata
            else:
                raise ValueError(
                    f"iltload could not find any valid file type at {str(data_path)}"
                )
        else:
            raise FileNotFoundError(f"{str(data_path)} was not found.")
