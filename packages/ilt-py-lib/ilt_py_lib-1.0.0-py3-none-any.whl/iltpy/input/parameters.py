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
import numpy as np
import warnings
import logging

# iltpy
from iltpy.fit.kernels import (
    Identity,
    IltKernel,
    Exponential,
    Diffusion,
    Gaussian,
    ImagRcKernel,
    RealRcKernel,
)
from iltpy.utils.scripts import _generate_idx, _generate_tau, _read_parameter_file

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")
warnings.simplefilter("always", UserWarning)

# logging
logger = logging.getLogger("iltpy_logger")


def _get_default_fit_parameters():
    """
    Gets default parameters required for inversion and returns them as a dictionary.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    Returns
    -------
    dict
        Python dictionary with fit parameters
    """
    fit_param_dict = {}
    # Compliance parameter for floor
    fit_param_dict["alpha_0"] = 1e-4
    # Global scaling for regularization matrix
    fit_param_dict["alpha_00"] = 1
    # Slope regularization parameter, calculated during init_alpha_terms if None
    fit_param_dict["alpha_p"] = None
    # Curvature regularization parameter, calculated during init if None
    fit_param_dict["alpha_c"] = None
    # Weighting for zero crossing
    fit_param_dict["alpha_a"] = 100000
    # Upper limit for boundary condition
    fit_param_dict["alpha_bc"] = 50
    # Non-negativity parameter
    fit_param_dict["alpha_nn"] = 1000
    # ZC penalty compliance parameter, calculated during init_alpha_terms if None
    fit_param_dict["alpha_d"] = None
    # Flag for choosing a different algorithm for g calculation, allowed values 0,2,4,6
    fit_param_dict["alt_g"] = 0

    # Compression
    # Flag for data compression
    fit_param_dict["compress"] = False
    # Flag for using svds instead of svd
    fit_param_dict["use_svds"] = False
    # Number of singular values for SVD
    fit_param_dict["s"] = 15

    # Array used for weighted inversions, weighting matrix
    fit_param_dict["sigma"] = None
    # User-defined guess for the initial g
    fit_param_dict["g_guess"] = None
    # Number of neighboring points per direction over which the maximum curvature is calculated
    fit_param_dict["c_nmax"] = 3
    # Number of neighboring points per direction over which the maximum slope is calculated
    fit_param_dict["p_nmax"] = 3
    # Calculated during init_parameters if None
    fit_param_dict["reg_bc"] = None
    # Kernel function for inversion, default is IltKernel
    fit_param_dict["kernel"] = IltKernel()
    # Defines the spacing for tau in each dimension, 1 for log-spaced and 0 for linear
    fit_param_dict["base_tau"] = 1
    # Maximum number of iterations
    fit_param_dict["maxloop"] = 100
    # Flag for non-negativity constraint
    fit_param_dict["nn"] = False

    # reg matrix update
    fit_param_dict["reg_down"] = 29
    fit_param_dict["reg_downrate"] = 0.05
    fit_param_dict["reg_upd"] = 1
    fit_param_dict["reg_updmin"] = 0.2
    fit_param_dict["reg_up"] = True
    # Flag for using static baseline in 1D inversions
    fit_param_dict["sb"] = False

    # zc penalty parameters
    # Flag for enabling ZC penalty
    fit_param_dict["reg_zc"] = True
    fit_param_dict["zc_max"] = 1
    # Iteration at which ZC update rate starts to decrease
    fit_param_dict["zc_down"] = 59
    # ZC penalty update rate (initial)
    fit_param_dict["zc_upd"] = 1
    # Minimum ZC penalty update rate
    fit_param_dict["zc_updmin"] = 0.2
    # Rate at which ZC update decreases
    fit_param_dict["zc_downrate"] = 0.05
    # Iteration number at which ZC penalty is switched on
    fit_param_dict["zc_on"] = 4
    fit_param_dict["zc_nmax"] = 3

    # User-defined array for dimensions which are not inverted but regularized
    fit_param_dict["dim_ndim"] = None
    # Output sampling vector
    fit_param_dict["tau"] = None
    # Convergence limit for the inversion
    fit_param_dict["conv_limit"] = 0.000001
    fit_param_dict["Cz"] = [np.array([0])]

    # store matrices durin each iteration
    fit_param_dict["store_g"] = False
    fit_param_dict["store_gamma"] = False

    # controlling sparse initialization
    fit_param_dict["force_sparse"] = False
    fit_param_dict["sparse_threshold"] = 0.92

    return fit_param_dict


def init_ndim(iltdata):
    """
    Initializes data characteristics.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    """

    # Get data shape and dimensions
    iltdata.Nt = iltdata.data.shape
    logger.debug("Set Nt to %s", iltdata.Nt)
    iltdata.ndim = len(iltdata.data.shape)
    logger.debug("Set ndim to %s", iltdata.ndim)

    # Generate indexes
    iltdata.idx = _generate_idx(iltdata.ndim)

    if iltdata.ndim > 1 and min(iltdata.data.shape) == 1:
        iltdata.ndim = iltdata.ndim - 1
        iltdata.data = np.squeeze(iltdata.data)
        logger.debug("Removed dimension with size 1")


def init_fit_dict(
    iltdata, parameters, kernel, tau, dim_ndim, sigma, g_guess, reinitialize
):
    """
    Gets the default fit dict and sets the fit parameters.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    parameters :str or dict, optional
        User-defined parameters, provide as a dict or in case of str,
        it should be the file path to a parameter file containing a dict.
        Note that data, kernel, tau, dim_ndim or sigma can't be provided as parameters.

    tau :ndarray,optional
        The tau vector used by the inversion,if None, a logarithmically spaced tau is generated.

    kernel : object, parent class IltKernel
        kernel function

    dim_ndim :ndarray, optional
        The array defining the n-th dimension of n-D data. If None, it is internally generated in case of
        inversions with 2D data where only the first dimension is inverted.

    sigma :ndarray
        Array used for weighted inversions.

    g_guess :ndarray
        User-defined guess for the initial g
    """
    # get default parameters
    default_parameters = _get_default_fit_parameters()
    if iltdata.initialized is True:
        if reinitialize is False:
            fit_dict_default = iltdata.fit_dict
            logger.debug("Using previously initialized fit dict.")
        elif reinitialize is True:
            logger.debug("Reinitializing IltData...")
            fit_dict_default = _get_default_fit_parameters()
            logger.debug("Using default fit dict.")
            # set keyword arguments to default values
            set_parameters(iltdata,fit_dict_default)
            logger.debug("Set all IltData attributes to default values.")

        else:
            raise ValueError("Parameter `reinitialize` must be True or False but got %s",reinitialize)
    else:
        fit_dict_default = _get_default_fit_parameters()
        logger.debug("Using default fit dict.")

    # if user defines a dict, then read parameters from the dict
    if parameters is not None:
        parameters_type = type(parameters)
        if parameters_type is dict:
            logger.debug("Found user-defined parameters, provided as dict.")
            iltdata.user_parameters = parameters
        elif parameters_type is str:
            logger.debug("Found user-defined parameters, provided as parameter file.")
            parameters_from_file = _read_parameter_file(parameters)
            parameters = parameters_from_file
            iltdata.user_parameters = parameters
        else:
            raise ValueError(
                "parameters must be provided as a dictionary or a path to an ILTpy-generated parameters file."
            )

        for parameter in parameters:
            if parameter in default_parameters:
                fit_dict_default[parameter] = parameters[parameter]
                logger.debug(
                    "Modified parameter %s to %s", parameter, parameters[parameter]
                )
            else:
                raise KeyError(f"""{parameter} is not a valid parameter. 
                            Consult the documentation for a list of valid parameters.""")
    else:
        iltdata.user_parameters = parameters

    # replace with user-defined parameters
    for parameter_name, parameter_val in zip(
        ["kernel", "tau", "dim_ndim", "g_guess", "sigma"],
        [kernel, tau, dim_ndim, g_guess, sigma],
    ):
        if parameter_val is not None:
            fit_dict_default[parameter_name] = parameter_val
            logger.debug("Modified %s to user-specified value.", parameter_name)

    return fit_dict_default


def set_parameters(iltdata, fit_dict):
    """
    Sets all the parameters previously initialized in the fit dict as class attributes.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    """
    # set IltData attributes
    iltdata.alpha_0 = fit_dict["alpha_0"]
    iltdata.alpha_00 = fit_dict["alpha_00"]
    iltdata.alpha_p = fit_dict["alpha_p"]
    iltdata.alpha_c = fit_dict["alpha_c"]
    iltdata.alpha_a = fit_dict["alpha_a"]
    iltdata.alpha_bc = fit_dict["alpha_bc"]
    iltdata.alpha_nn = fit_dict["alpha_nn"]
    iltdata.alpha_d = fit_dict["alpha_d"]

    iltdata.alt_g = fit_dict["alt_g"]
    iltdata.compress = fit_dict["compress"]
    iltdata.sigma = fit_dict["sigma"]
    iltdata.g_guess = fit_dict["g_guess"]

    iltdata.c_nmax = fit_dict["c_nmax"]
    iltdata.p_nmax = fit_dict["p_nmax"]
    iltdata.reg_bc = fit_dict["reg_bc"]
    iltdata.base_tau = fit_dict["base_tau"]
    iltdata.maxloop = fit_dict["maxloop"]
    iltdata.nn = fit_dict["nn"]

    iltdata.reg_down = fit_dict["reg_down"]
    iltdata.reg_downrate = fit_dict["reg_downrate"]
    iltdata.reg_upd = fit_dict["reg_upd"]
    iltdata.reg_updmin = fit_dict["reg_updmin"]

    iltdata.s = fit_dict["s"]
    iltdata.reg_up = fit_dict["reg_up"]
    iltdata.reg_zc = fit_dict["reg_zc"]
    iltdata.sb = fit_dict["sb"]
    iltdata.use_svds = fit_dict["use_svds"]

    iltdata.zc_max = fit_dict["zc_max"]
    iltdata.zc_down = fit_dict["zc_down"]
    iltdata.zc_upd = fit_dict["zc_upd"]
    iltdata.zc_updmin = fit_dict["zc_updmin"]
    iltdata.zc_downrate = fit_dict["zc_downrate"]
    iltdata.zc_on = fit_dict["zc_on"]
    iltdata.zc_nmax = fit_dict["zc_nmax"]
    iltdata.conv_limit = fit_dict["conv_limit"]
    iltdata.Cz = fit_dict["Cz"]

    # kernels and tau
    iltdata.tau = fit_dict["tau"]
    iltdata.kernel = fit_dict["kernel"]

    # flag for storing matrices
    iltdata.store_g = fit_dict["store_g"]
    iltdata.store_gamma = fit_dict["store_gamma"]

    # controls sparse initialization
    iltdata.force_sparse = fit_dict["force_sparse"]
    iltdata.sparse_threshold = fit_dict["sparse_threshold"]

    # dim_ndim
    iltdata.dim_ndim = fit_dict["dim_ndim"]

    logger.debug("Set parameters as IltData class attributes.")


def init_parameters(iltdata):
    """
    Intialises the parameters by reshaping them and checks for shape inconsistencies.
    Required parameters, if not user-defined are generated.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class

    Raises
    ------
    ValueError
        Raises ValueError if length of user-defined t along the non-inverted
        second dimension doesn't match the data shape in case of 2D data.

    ValueError
        Raises ValueError if the kernel is the inverted dimension is not specified.
    """

    kernel_dict = {
        "_IltKernel_": IltKernel(),
        "_exponential_": Exponential(),
        "_identity_": Identity(),
        "_diffusion_": Diffusion(),
        "_gaussian_": Gaussian(),
        "_real_rc_kernel_": RealRcKernel(),
        "_imag_rc_kernel_": ImagRcKernel(),
    }
    # these functions should be used in the specific order as shown below.

    # initialize kernel
    _init_kernel(iltdata, kernel_dict)

    # initalize compression, base_tau, singular values
    _init_compress(iltdata)

    # initialize base_tau
    _init_base_tau(iltdata, kernel_dict)

    # initialize reg_bc
    if iltdata.reg_bc is None:
        iltdata.reg_bc = 2 * np.abs(np.sign(iltdata.base_tau)).astype(np.int32)
    else:
        iltdata.reg_bc = (iltdata.reg_bc * np.ones((iltdata.ndim))).astype(np.int32)

    # initialize number of singular values, s
    _init_s(iltdata)

    # initialize t
    _init_t(iltdata)

    # initialize tau
    _init_tau(iltdata)

    # validate t and tau intialization
    _check_t_tau(iltdata)

    # reshape t and tau
    iltdata.t = [t_arr.reshape((1, max(t_arr.shape))) for t_arr in iltdata.t]
    logger.debug("Reshaped t for each dimension to (1,max(t.shape))")
    iltdata.tau = [tau_arr.reshape((max(tau_arr.shape), 1)) for tau_arr in iltdata.tau]
    logger.debug("Reshaped tau for each dimension to (max(tau.shape),1)")

    # dimension counts
    iltdata.Nx0 = np.array([len(i) for i in iltdata.tau])
    iltdata.Nx0tot = np.prod(iltdata.Nx0)  # Nx0 is Nx (see below) without sb.
    iltdata.Ntau = np.prod(iltdata.Nx0)

    # initialize static_baseline
    _init_static_baseline(iltdata)

    # Nx specifies number of data points of independent output variable in each dimension
    iltdata.Nx = np.array([len(r) for r in iltdata.tau]) + np.array(
        [int(r) for r in iltdata.sb]
    )
    iltdata.Nxtot = np.prod(iltdata.Nx)

    # initialize g_guess
    if iltdata.g_guess is not None:
        _init_g_guess(iltdata)

    # Initialize alpha terms
    _init_alpha_terms(iltdata)

    # move max points
    iltdata.c_nmax = iltdata.c_nmax * np.ones((iltdata.ndim))
    iltdata.p_nmax = iltdata.p_nmax * np.ones((iltdata.ndim))
    iltdata.zc_nmax = iltdata.zc_nmax * np.ones((iltdata.ndim))

    # Cz
    iltdata.Cz = iltdata.Cz * iltdata.ndim**2

    # data point spacing
    iltdata.Delta_Q = []

    for i in range(iltdata.ndim):
        if iltdata.base_tau[i] != 0:
            iltdata.Delta_Q.append(
                np.log(iltdata.tau[i][-1]) - np.log(iltdata.tau[i][-2])
            )
        else:
            iltdata.Delta_Q.append(
                (iltdata.tau[i][-1] - iltdata.tau[i][-2]) * np.log(10)
            )

    _extend_dims(iltdata)

    # Cast movemax points as integers
    iltdata.c_nmax = iltdata.c_nmax.astype(np.int32)
    iltdata.p_nmax = iltdata.p_nmax.astype(np.int32)
    iltdata.zc_nmax = iltdata.zc_nmax.astype(np.int32)


def _init_kernel(iltdata, kernel_dict):
    """
    Initializes the kernel functions for inversion.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    """

    # initialize kernel
    if not isinstance(iltdata.kernel, list):
        iltdata.kernel = [iltdata.kernel]
        logger.debug("Converted kernel parameter to a list.")
    if iltdata.ndim > 1 and len(iltdata.kernel) < iltdata.ndim:
        ndim_diff = iltdata.ndim - len(iltdata.kernel)
        iltdata.kernel += [Identity()] * ndim_diff
        logger.debug("Set kernel to Identity for unspecified dimensions.")

    # if an in-built kernel name is given, choose the correct kernel functions
    for idx, kernel_name in enumerate(iltdata.kernel):
        if type(kernel_name) is str:
            if kernel_name in kernel_dict.keys():
                logger.debug(
                    f"Set kernel corresponding to the kernel name : {kernel_name}"
                )
                iltdata.kernel[idx] = kernel_dict[kernel_name]
            else:
                raise ValueError(
                    f"""Kernel : {kernel_name} does not correspond to a built-in kernel class. 
                    In case of user-defined kernels, please use an instance of the IltKernel class as input."""
                )

    for kernel in iltdata.kernel:
        if not isinstance(kernel, IltKernel):
            raise TypeError("kernel must be an instance of IltKernel")

        for attribute in ["name", "kernel", "kernel_str"]:
            if not hasattr(kernel, attribute):
                raise AttributeError(
                    f"kernel is missing a required attribute: {attribute}"
                )

    # raise error if kernel was not changed from default by user input or otherwise
    if iltdata.kernel[0].name == "_IltKernel_":
        raise ValueError("No kernel was specified for the first dimension.")

    # raise error if an indenity kernel is specified in the first dimension
    if iltdata.kernel[0].name == "_identity_":
        raise ValueError("""Identity kernel cannot be specified in the first dimension. 
                         Dimension to be inverted must always be the first, transpose data accordingly.""")


def _init_compress(iltdata):
    """
    Initializes compression

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    """
    # intialize compress
    if not isinstance(iltdata.compress, list):
        iltdata.compress = [iltdata.compress]
        logger.debug("Converted compress parameter to a list.")
    if iltdata.ndim > 1 and len(iltdata.compress) < iltdata.ndim:
        ndim_diff = iltdata.ndim - len(iltdata.compress)
        iltdata.compress += [False] * ndim_diff
        logger.debug("Set compress to False for unspecified dimensions.")
    if not all(isinstance(i, bool) for i in iltdata.compress):
        raise TypeError("Value of `compress` must be a boolean or a list of booleans.")

    #iltdata.compress = np.array([int(i) for i in iltdata.compress], dtype=np.int32)


def _init_base_tau(iltdata, kernel_dict):
    """
    Initializes base_tau and number of singular values, s

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    """

    # base_tau
    if not isinstance(iltdata.base_tau, list):
        iltdata.base_tau = [iltdata.base_tau]
        logger.debug("Converted base_tau parameter to a list.")
    if iltdata.ndim > 1 and len(iltdata.base_tau) < iltdata.ndim:
        ndim_diff = iltdata.ndim - len(iltdata.base_tau)
        iltdata.base_tau += [0] * ndim_diff
        logger.debug("Set base_tau to 0 for unspecified dimensions.")
    if not all(isinstance(i, int) for i in iltdata.base_tau):
        raise TypeError("Value of `base_tau` must be an integer or a list of integers.")

    linear_base_kernels = ["_identity_", "_IltKernel_"]
    log_base_kernels = [key for key in kernel_dict if key not in linear_base_kernels]

    for i in range(iltdata.ndim):
        if iltdata.kernel[i].name in linear_base_kernels:
            iltdata.base_tau[i] = 0
            #iltdata.compress[i] = 0
            iltdata.compress[i] = False
            logger.debug("Set compress and base_tau to 0 for dimension %s", i)
        elif iltdata.kernel[i].name in log_base_kernels:
            iltdata.base_tau[i] = 1
            logger.debug("Set base_tau to 1 for dimension %s", i)
        else:
            base_tau_warn = (
                f"base_tau must be set appropriately for user-defined kernels: 0 for linear or 1 for logarithmic spacing. "
                f"Currently, base_tau[{i}] is {iltdata.base_tau[i]}. Please verify that it matches the spacing of the output sampling vector (tau)."
            )
            warnings.warn(base_tau_warn)

def _init_s(iltdata):
    """
    Initialize number of singular values used for SVD.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    """

    # number of singular values
    if not isinstance(iltdata.s, list):
        iltdata.s = [iltdata.s]
        logger.debug("Converted s parameter to a list.")
    if iltdata.ndim > 1 and len(iltdata.s) < iltdata.ndim:
        ndim_diff = iltdata.ndim - len(iltdata.s)
        iltdata.s += [iltdata.s[0]] * ndim_diff
        logger.debug("Set s to iltdata.s[0] for unspecified dimensions.")
    if not all(isinstance(i, int) for i in iltdata.s):
        raise TypeError("Value of `s` must be an integer or a list of integers.")
    
    iltdata.s = [
        iltdata.Nt[i]
        if iltdata.s[i] > iltdata.Nt[i] or iltdata.compress[i] is False
        else iltdata.s[i] * int(iltdata.compress[i])
        for i in range(iltdata.ndim)
    ]


def _init_t(iltdata):
    """
    Initializes t and tau

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    Raises
    ------
    ValueError
        If tau and t are not specified.
    """

    for i in range(iltdata.ndim):
        if iltdata.base_tau[i] != 0:
            if iltdata.user_t_spec[i] is False:
                raise ValueError(
                    f"t[{i}] was not specified by the user. "
                    f"t in a dimension to be inverted must be specified by the user."
                )
            if iltdata.t[i].size != iltdata.data.shape[i]:
                raise ValueError(
                    f"Length of t[{i}]: {iltdata.t[i].size} does not match "
                    f"data.shape[{i}]: {iltdata.data.shape[i]}."
                )

    # define sampling vector in uninverted,last dimension
    if iltdata.ndim > 1:
        if iltdata.dim_ndim is not None:
            logger.debug("Found user-defined dim_ndim")
            iltdata.t[-1] = iltdata.dim_ndim
            logger.debug("Set t for last dimension to user-defined dim_ndim")
            if max(iltdata.dim_ndim.shape) != iltdata.data.shape[-1]:
                raise ValueError(
                    f"""Length of array in dimension {iltdata.ndim} : {max(iltdata.dim_ndim.shape)} 
                    does not match size of data in dimension {iltdata.ndim} : {iltdata.data.shape[-1]}"""
                )
        else:
            if iltdata.base_tau[-1] == 0:
                # dimension which is not inverted.
                if iltdata.t[-1] is None:
                    iltdata.t[-1] = np.arange(1, iltdata.data.shape[-1] + 1)
                    logger.debug("Set t for last dimension to default dim_ndim")


def _init_tau(iltdata):
    """
    Initializes tau

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    Raises
    ------
    ValueError
        Raised if tau is not specified for kernels for which user is required to specify tau.
    TypeError
        Raised if tau is provided, but not as a 1D numpy array or a list of numpy arrays.
    """

    if iltdata.tau is not None: # if tau is provided, check input
        if not isinstance(iltdata.tau, list):
            logger.debug("Converted parameter tau to a list.")
            if isinstance(iltdata.tau, np.ndarray):
                iltdata.tau = [iltdata.tau]
            else:
                raise TypeError(f"Expected tau as a 1D numpy array, got {type(iltdata.tau)}")
        else:
            if not all(isinstance(tau_array, np.ndarray) for tau_array in iltdata.tau):
                raise TypeError(
                    "tau must be a list of numpy arrays or a single 1D numpy array."
                )
        # add tau for dimensions which are not specified.
        if iltdata.ndim > 1 and len(iltdata.tau) < iltdata.ndim:
            for i in range(len(iltdata.tau), iltdata.ndim):
                if iltdata.kernel[i].name == "_identity_":
                    logger.debug("Set tau equal to t for dimension %s", i)
                    iltdata.tau.append(iltdata.t[i])
                elif iltdata.kernel[i].name in ["_exponential_","_gaussian_"]:
                    logger.debug("Generating tau based on t for dimension %s", i)
                    tau_warn = f"tau[{i}] was not specified, proceeding with ILTpy-generated tau. Note that ILTpy-generated tau is only valid in case of NMR/EPR relaxation data."
                    warnings.warn(tau_warn)
                    iltdata.tau.append(_generate_tau(iltdata.t[i]))
                else:
                    raise ValueError(f"Found kernel: {iltdata.kernel[i].name} in dimension {i} but tau[{i}] was not specified.")

    else: # tau not provided, generate tau for all dimensions, if possible.
        iltdata.tau = []
        for i in range(iltdata.ndim):
            if iltdata.kernel[i].name == "_identity_":
                logger.debug("Set tau equal to t for dimension %s", i)
                iltdata.tau.append(iltdata.t[i])
            elif iltdata.kernel[i].name in ["_exponential_","_gaussian_"]:
                logger.debug("Generating tau based on t for dimension %s", i)
                tau_warn = f"tau[{i}] was not specified, proceeding with ILTpy-generated tau. Note that ILTpy-generated tau is only valid in case of NMR/EPR relaxation data."
                warnings.warn(tau_warn)
                iltdata.tau.append(_generate_tau(iltdata.t[i]))
            else:
                raise ValueError(f"Found kernel: {iltdata.kernel[i].name} in dimension {i} but tau[{i}] was not specified.")

def _check_t_tau(iltdata):
    """
    Validates the inputs of t and tau after initialization.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    Raises
    ------
    ValueError
        Raised if sizes of t does not match data dimensions.
    ValueError
        Raised if size of tau does not match size of data dimensions in which an identity kernel is used.
    """

    # check if size of tau matches data size for dimensions which are not inverted
    # check if size of t matches data size for all dimensions
    for dim in range(iltdata.ndim):
        if iltdata.t[dim].flatten().size != iltdata.data.shape[dim]:
            raise ValueError(
                f"Length of t: {iltdata.t[dim].size} in dimension {dim} "
                f"does not match the length of data: {iltdata.data.shape[dim]} in dimension {dim}"
            )
        if iltdata.kernel[dim].name == "_identity_":
            if iltdata.tau[dim].flatten().size != iltdata.data.shape[dim]:
                raise ValueError(
                    f"Length of tau: {iltdata.tau[dim].size} in dimension {dim} with identity kernel "
                    f"does not match the length of data: {iltdata.data.shape[dim]} in dimension {dim}"
                )


def _init_static_baseline(iltdata):
    """
    Initializes sb parameter for static baseline handling.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    """
    # initialize sb
    if not isinstance(iltdata.sb, list):
        iltdata.sb = [iltdata.sb]
        logger.debug("Converted sb parameter to a list.")
    if iltdata.ndim > 1 and True in iltdata.sb:
        iltdata.sb = [False] * iltdata.ndim
        static_baseline_warn = """Static baseline cannot be used in case of data dimensionality > 1.
        Setting `sb` to False."""
        warnings.warn(static_baseline_warn)
    else:
        iltdata.sb = [iltdata.sb[0]] * iltdata.ndim

    if not all(isinstance(i, bool) for i in iltdata.sb):
        raise TypeError("Value of `sb` must be a boolean or a list of booleans.")


def _init_g_guess(iltdata):
    """
    Initializes g_guess

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    """

    if iltdata.g_guess.ndim > 1:
        logger.debug("Found g_guess shape: %s", iltdata.g_guess.shape)
        iltdata.g_guess = iltdata.g_guess.flatten(order="F")
        logger.debug("Flattened g_guess to shape: %s", iltdata.g_guess.shape)
    if iltdata.g_guess.size != iltdata.Nxtot:
        raise ValueError(
            f"`g_guess` is of wrong size: {iltdata.g_guess.size}, expected: {iltdata.Nxtot}."
        )


def _init_alpha_terms(iltdata):
    """
    Initializes alpha terms needded for inversion

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    """
    # alpha_0
    iltdata.alpha_0 = iltdata.alpha_0 * np.ones((iltdata.ndim))
    compress_array = np.array([int(i) for i in iltdata.compress])

    # alpha_c
    if iltdata.alpha_c is None:
        alpha_c = []
        pn = np.prod(
            iltdata.data.shape * (1 - compress_array) + compress_array * iltdata.s
        )
        for i in range(iltdata.ndim):
            if iltdata.base_tau[i] == 0:
                alpha_c.append(
                    2
                    * (iltdata.tau[i][-1] - iltdata.tau[i][-2])
                    / pn
                    * np.prod(iltdata.Ntau)
                )
            else:
                alpha_c.append(
                    2
                    * (np.log(iltdata.tau[i][-1]) - np.log(iltdata.tau[i][-2]))
                    / pn
                    * np.prod(iltdata.Ntau)
                )
        iltdata.alpha_c = np.array(alpha_c)

    else:
        iltdata.alpha_c = iltdata.alpha_c * np.ones((iltdata.ndim))

    # alpha_p
    if iltdata.alpha_p is None:
        iltdata.alpha_p = 5 * iltdata.alpha_c
    else:
        iltdata.alpha_p = iltdata.alpha_p * np.ones((iltdata.ndim))

    # other alpha terms
    iltdata.alpha_a = iltdata.alpha_a * np.ones((iltdata.ndim))
    iltdata.alpha_bc = iltdata.alpha_bc * np.ones((iltdata.ndim))
    iltdata.alpha_nn = iltdata.alpha_nn * np.ones((iltdata.ndim))
    if iltdata.alpha_d is None:
        iltdata.alpha_d = 1 / iltdata.alpha_a
    else:
        iltdata.alpha_d = iltdata.alpha_d * np.ones((iltdata.ndim))

    logger.debug("Set alpha terms.")


def _extend_dims(iltdata):
    """
    Extend dimension of alpha terms and Delta_Q

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class

    """

    # extend dimension of alpha terms and Delta_Q
    for i in range(iltdata.ndim, iltdata.ndim**2):
        iltdata.alpha_0 = np.append(
            iltdata.alpha_0,
            np.sqrt(
                (
                    iltdata.alpha_0[iltdata.idx[i][0]] ** 2
                    + iltdata.alpha_0[iltdata.idx[i][1]] ** 2
                )
                / 2
            ),
        )
        iltdata.alpha_p = np.append(
            iltdata.alpha_p,
            np.sqrt(
                (
                    iltdata.alpha_p[iltdata.idx[i][0]] ** 2
                    + iltdata.alpha_p[iltdata.idx[i][1]] ** 2
                )
                / 2
            ),
        )
        iltdata.alpha_c = np.append(
            iltdata.alpha_c,
            np.sqrt(
                (
                    iltdata.alpha_c[iltdata.idx[i][0]] ** 2
                    + iltdata.alpha_c[iltdata.idx[i][1]] ** 2
                )
                / 2
            ),
        )
        iltdata.alpha_a = np.append(
            iltdata.alpha_a,
            np.sqrt(
                (
                    iltdata.alpha_a[iltdata.idx[i][0]] ** 2
                    + iltdata.alpha_a[iltdata.idx[i][1]] ** 2
                )
                / 2
            ),
        )
        iltdata.alpha_d = np.append(
            iltdata.alpha_d,
            np.sqrt(
                (
                    iltdata.alpha_d[iltdata.idx[i][0]] ** 2
                    + iltdata.alpha_d[iltdata.idx[i][1]] ** 2
                )
                / 2
            ),
        )
        iltdata.reg_bc = np.append(iltdata.reg_bc, 0)
        iltdata.Delta_Q.append(
            np.sqrt(
                iltdata.Delta_Q[iltdata.idx[i][0]] ** 2
                + iltdata.Delta_Q[iltdata.idx[i][1]] ** 2
            )
        )
        iltdata.c_nmax = np.append(
            iltdata.c_nmax, np.ceil(np.mean(iltdata.c_nmax[iltdata.idx[i]]))
        )
        iltdata.p_nmax = np.append(
            iltdata.p_nmax, np.ceil(np.mean(iltdata.p_nmax[iltdata.idx[i]]))
        )
        iltdata.zc_nmax = np.append(
            iltdata.zc_nmax, np.ceil(np.mean(iltdata.zc_nmax[iltdata.idx[i]]))
        )
