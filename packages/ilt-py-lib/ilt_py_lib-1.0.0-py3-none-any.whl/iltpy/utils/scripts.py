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
import logging
import json
import numpy as np
from pathlib import Path

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")

# logging setup
logger = logging.getLogger("iltpy_logger")
logger.setLevel(logging.ERROR)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _multidim_matmul(x, y):
    """
    Perform multi-dimensional matrix multiplication on an input array.

    This function multiplies a 1D or multi-dimensional array `x` by a series of matrices specified in `y`.
    The multiplication is performed along each dimension of `x` using the corresponding matrix in `y`.

    Parameters
    ----------
    x : array_like
        A NumPy array to be transformed. Can be 1D, 2D, or higher-dimensional.

    y : list of array_like
        A list of matrices where each matrix `y[k]` (ndim=2) is used to multiply along the `k`-th dimension of `x`.
        Each matrix in `y` must be compatible with the corresponding dimension of `x`:
        - If `y[k]` is a scalar (1x1), it is converted to a diagonal matrix for that dimension.
        - If `y[k]` has the same number of rows as the `k`-th dimension of `x`, it will be transposed if needed.
        - If `y[k]` has a mismatched size, an error is raised.

    Returns
    -------
    ndarray
        The transformed multi-dimensional array resulting from the series of matrix multiplications.

    Raises
    ------
    ValueError
        If any matrix in `y` is not compatible with the corresponding dimension of `x` for multiplication.
    """
    x = np.asarray(x)
    ndim = x.ndim

    # ndim
    if ndim == 2 and min(x.shape) == 1:
        ndim = 1
    # y must be a list of numpy arrays with ndim=2
    # for iltpy, this is fulfilled in all instances in which this function is used.
    y = [np.asarray(mat) for mat in y]
    for k in range(ndim):
        if y[k].shape == (1, 1):
            y[k] = y[k].item() * np.eye(x.shape[k])
        elif y[k].shape[1] != x.shape[k]:
            if y[k].shape[0] == x.shape[k]:
                y[k] = y[k].T
            else:
                raise ValueError(
                    f"Dimension mismatch: Expected y[{k}] to have one of its dimensions equal to {x.shape[k]},"
                    f"but got shape {y[k].shape}."
                )

    if ndim > 1:
        for k in range(ndim):
            x = np.tensordot(y[k], x, axes=(1, k))
    else:
        x = y[0] @ x  # 1D case

    return x


def _generate_tau(t):
    """
    Generate log-spaced tau values based on the input time array `t`.

    This function creates an array of 100 logarithmically spaced values between
    the minimum and maximum of the provided time array `t`, scaled by factors of
    1/1000 and 100, respectively.

    Parameters
    ----------
    t : np.ndarray
        The input time array for which to generate tau values. Must be a 1D array-like
        structure of numeric values.

    Returns
    -------
    np.ndarray
        A 1D NumPy array of 100 log-spaced tau values ranging from `log10(min(t)/1000)`
        to `log10(max(t)*100)`.

    Notes
    -----
    - If the minimum value in `t` is 0, an offset is added to avoid taking
      the logarithm of zero.
    """
    t_min = np.min(t)
    t_max = np.max(t)

    start = (
        np.log10((t_min + np.mean(np.diff(t))) / 1000)
        if t_min == 0
        else np.log10(t_min / 1000)
    )
    stop = np.log10(t_max * 100)
    logger.debug(
        f"Generating tau as a logspaced array of size : 100 ranging from {start} to {stop}"
    )
    return np.logspace(start, stop, 100)


def _generate_idx(ndim):
    """
    Generate a list of index pairs for a given number of dimensions.

    This function generates a list of index pairs to be used for operations on a
    multidimensional array. For each combination of
    dimensions, the function produces index pairs representing all possible
    permutations of indices.

    Parameters
    ----------
    ndim : int
        The number of dimensions of the data.

    Returns
    -------
    list of list
        A list of index pairs, where each pair is a list of two integers.

    """
    idx = {}
    ctr = 1

    for k in range(ndim):
        idx[k] = [k, k]
        for i in range(k + 1, ndim):
            idx[ndim + ctr] = [k, i]
            idx[ndim + ctr + 1] = [i, k]
            ctr += 2

    return [idx[key] for key in sorted(idx.keys())]


def _ilt_movmax_diag(data, matdim, nmx, dim):
    """
    Compute the moving maximum of an n-dimensional matrix including diagonal directions.

    This function takes an input data array, reshapes it according to `matdim`, and computes
    the moving maximum along the specified dimensions (`dim`) with a filter size of `nmx`.

    Parameters
    ----------
    data : ndarray
        Input data array.

    matdim : tuple of int
        The shape of the data over which moving max is calculated.

    nmx : int
        The size of the window for the moving maximum.

    dim : array_like
        List or array of dimensions along which to compute the moving maximum.

    Returns
    -------
    ndarray
        The array after applying the moving maximum filter along the specified dimensions,
        returned as a flattened 1D array.

    Raises
    ------
    ValueError
        If the product of `matdim` does not match the number of elements in `data`.

    """
    if abs(nmx) <= 1:
        return data

    dim = np.atleast_1d(dim).flatten()

    data = data.reshape((-1, 1), order="F")
    sx = data.shape[0]

    if sx != np.prod(matdim):
        raise ValueError(
            f"Matrix dimensions mismatch for data with length {sx} and matrix dimensions {matdim}"
        )

    dim = dim[::-1]
    dm, dm_idx = np.unique(dim, return_index=True)
    dim = dim[np.sort(dm_idx)]
    dim = dim[::-1] + 1

    for k in range(dim.size - 1):
        if dim[k + 1] < dim[k]:
            dim[k] = -dim[k]

    if nmx % 2 != 0:
        Nneg = abs(nmx) // 2
        Npos = Nneg
    elif nmx > 0:
        Nneg = nmx // 2 - 1
        Npos = nmx // 2
    else:
        Nneg = abs(nmx) // 2
        Npos = abs(nmx) // 2 - 1

    n = matdim.size

    if n > 1:
        data = data.reshape(tuple(matdim), order="F")

    movmax_data = np.empty((sx, nmx), order="F")

    for k in range(nmx):
        data1 = data.copy(order="F")
        for dim_index in dim:
            perm = [abs(dim_index)] + list(range(2, n + 1))
            perm[abs(dim_index) - 1] = 1
            perm = np.array(perm)
            psx = matdim[perm - 1]
            psx_prod = int(np.prod(psx[1:]))

            if n > 1:
                data1 = np.transpose(data1, axes=perm - 1)
                if n > 2:
                    data1 = np.reshape(data1, (psx[0], psx_prod), order="F")
            if dim_index > 0:
                data1 = np.vstack(
                    (np.zeros((Nneg, psx_prod)), data1, np.zeros((Npos, psx_prod)))
                )
                data1 = data1[k : psx[0] + k, :]
            else:
                data1 = np.vstack(
                    (np.zeros((Npos, psx_prod)), data1, np.zeros((Nneg, psx_prod)))
                )
                data1 = data1[(nmx - (k + 1)) : psx[0] + (nmx - (k + 1)), :]

            if n > 1:
                if n > 2:
                    data1 = data1.reshape((psx), order="F")
                data1 = np.transpose(data1, axes=perm - 1)

        movmax_data[:, k] = data1.flatten(order="F")

    return np.max(movmax_data, axis=1)


def compute_stats(iltdata):
    """
    Computes various statistical parameters from a successful IltData.iltstats() run.

    Parameters
    ----------
    iltdata : IltData
        IltData instance which has been inverted and consistency check has been run.
    """

    out_dict = {
        "g_mean": np.mean(iltdata.statistics["g_list"], axis=0),
        "fit_mean": np.mean(iltdata.statistics["fit_list"], axis=0),
        "residuals_mean": np.mean(iltdata.statistics["residuals_list"], axis=0),
        "g_std": np.std(iltdata.statistics["g_list"], axis=0),
        "fit_std": np.std(iltdata.statistics["fit_list"], axis=0),
        "residuals_std": np.std(iltdata.statistics["residuals_list"], axis=0),
        "g_conf_interval": [
            np.mean(iltdata.statistics["g_list"], axis=0)
            - np.std(iltdata.statistics["g_list"], axis=0),
            np.mean(iltdata.statistics["g_list"], axis=0)
            + np.std(iltdata.statistics["g_list"], axis=0),
        ],
        "fit_conf_interval": [
            np.mean(iltdata.statistics["fit_list"], axis=0)
            - np.std(iltdata.statistics["fit_list"], axis=0),
            np.mean(iltdata.statistics["fit_list"], axis=0)
            + np.std(iltdata.statistics["fit_list"], axis=0),
        ],
    }

    iltdata.statistics.update(out_dict)


def _estimate_sparsity(k_list):
    """
    Estimate the sparsity of a matrix formed by Kronecker products of matrices in k_list.

    Parameters:
    -----------
    k_list : list
        List of matrices to be used in Kronecker products

    Returns:
    --------
    float
        Sparsity of the resulting Kronecker product matrix (proportion of zero elements)
    """
    nnz_total = 1
    size_total = 1
    for k in k_list:
        nnz_total *= np.count_nonzero(k)
        size_total *= k.shape[0] * k.shape[1]
    return 1 - nnz_total / size_total


def _read_parameter_file(parameter_file_path):
    """
    Reads a JSON-formatted parameter file and returns its contents as a dictionary.

    Parameters
    ----------
    parameter_file_path : str or Path
        Path to the JSON parameter file.

    Returns
    -------
    dict
        A dictionary containing the parameters read from the file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    Exception
        If any other error occurs while reading or parsing the file.
    """
    fp = Path(parameter_file_path)

    if not fp.exists():
        raise FileNotFoundError(f"Parameter file not found at {parameter_file_path}")

    try:
        with fp.open("r", encoding="utf-8") as f:
            parameters_dict = json.load(f)
    except Exception as e:
        raise Exception(f"An error occurred while reading {parameter_file_path}: {e}")

    return parameters_dict
