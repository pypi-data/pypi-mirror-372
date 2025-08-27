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
import warnings
import numpy as np
from scipy.sparse import csr_array
from scipy.sparse import identity as spidentity
from scipy.sparse import kron as spkron
from scipy.sparse import eye as speye
from scipy.sparse import diags as spdiags
from scipy.sparse.linalg import svds
from scipy.linalg import svd
from scipy.special import seterr

# iltpy
from iltpy.utils.scripts import _multidim_matmul, _estimate_sparsity

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")
oldscipyerr = seterr(all="raise", underflow="ignore", slow="ignore", loss="warn")

# logging
logger = logging.getLogger("iltpy_logger")


class IltKernel:
    """
    Parent class for kernels. For defining kernels:

    class MyKernel(IltKernel):
        def __init__(self):
            self.name = 'my_kernel'
            self.kernel = lambda t,tau : kernel_func(t,tau)
            self.kernel_str = "lambda t,tau : kernel_func(t,tau)"
    """

    def __init__(self):
        self.name = "_IltKernel_"
        self.kernel = lambda t, tau: np.eye(t.size)
        self.kernel_str = "lambda t, tau: np.eye(t.size)"


class Identity(IltKernel):
    def __init__(self):
        self.name = "_identity_"
        self.kernel = lambda t, tau: np.eye(t.size)
        self.kernel_str = "lambda t, tau: np.eye(t.size)"


class Exponential(IltKernel):
    def __init__(self):
        self.name = "_exponential_"
        self.kernel = lambda t, tau: np.exp(-t / tau)
        self.kernel_str = "lambda t, tau: np.exp(-t / tau)"


class Diffusion(IltKernel):
    def __init__(self):
        self.name = "_diffusion_"
        self.kernel = lambda B, D: np.exp(-B * D)
        self.kernel_str = "lambda B, D: np.exp(-B * D)"


class Gaussian(IltKernel):
    def __init__(self):
        self.name = "_gaussian_"
        self.kernel = lambda t, tau: np.exp(-(t**2) * (1 / tau) ** 2 / 2)
        self.kernel_str = "lambda t, tau: np.exp(-(t**2) * (1 / tau) ** 2 / 2)"


class RealRcKernel(IltKernel):
    def __init__(self):
        self.name = "_real_rc_kernel_"
        self.kernel = lambda f, tau: np.real((1.0 / (1 + 1j * 2 * np.pi * tau * f)))
        self.kernel_str = (
            "lambda f, tau: np.real((1.0 / (1 + 1j * 2 * np.pi * tau * f)))"
        )


class ImagRcKernel(IltKernel):
    def __init__(self):
        self.name = "_imag_rc_kernel_"
        self.kernel = lambda f, tau: np.imag((1.0 / (1 + 1j * 2 * np.pi * tau * f)))
        self.kernel_str = (
            "lambda f, tau: np.imag((1.0 / (1 + 1j * 2 * np.pi * tau * f)))"
        )


# Kernel Initialization
def init_kernel_dense(iltdata, verbose=0):
    """
    This function initializes kernel matrices if sparsity of kernel matrices is less than iltdata.sparse_threshold.
    It uses the dense form of matrices and uses corresponding functions. The sparse version of this function can
    be forced by setting iltdata.force_sparse to True during initialization.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    verbose : int
        Controls verbosity
    """
    vprint1 = print if verbose > 1 else lambda *args, **kwargs: None

    iltdata.K0comp = np.identity(1)
    iltdata.U = []
    iltdata.Ut = []

    for i in range(iltdata.ndim):
        vprint1(f"    Initializing kernel matrix in dimension {i}...")
        logger.debug("Initializing kernel matrix in dimension %s...", i)
        # Adjust size if static baseline feature is used
        if iltdata.sb[i] is True:
            logger.debug("Adjusting the size of K since sb is True for dimension %s", i)
            iltdata.K[i] = np.vstack(
                (iltdata.K[i], np.ones((1, iltdata.K[i].T.shape[0])))
            )

        # SVD compression
        if bool(iltdata.compress[i]) is True:
            if iltdata.use_svds is True:
                vprint1(f"    SVDS compression in dimension {i}...")
                logger.debug("SVDS compression in dimension %s...",i)
                [u1, d1, v1] = svds(iltdata.K[i].T, iltdata.s[i], solver="propack")
            else:
                vprint1(f"    SVD compression in dimension {i}...")
                logger.debug("SVD compression in dimension %s...",i)
                [u1, d1, v1] = svd(iltdata.K[i].T, full_matrices=False)

            v1 = v1.T
            d1_diag = np.diag(d1[: iltdata.s[i]])
            v1_red = v1[: iltdata.Nx[i], : iltdata.s[i]]

            iltdata.U.append(u1[: iltdata.Nt[i], : iltdata.s[i]])
            iltdata.K0comp = np.kron((d1_diag @ v1_red.T), iltdata.K0comp)
        else:
            iltdata.K0comp = np.kron(iltdata.K[i].T, iltdata.K0comp)
            iltdata.U.append(np.eye(iltdata.Nt[i]))

        iltdata.Ut.append(iltdata.U[i].T)

    Mcomp = _multidim_matmul(iltdata.data, iltdata.Ut)
    Ncomp = int(np.prod(iltdata.s))

    iltdata.mcomp = Mcomp.reshape((Ncomp, 1))
    iltdata.Is = np.eye(iltdata.K0comp.shape[0])

    # Sigma for weighted inversions
    if iltdata.sigma is not None and iltdata.alt_g in [0, 4]:
        vprint1("    Initializing weighting matrix for weighted inversion...")
        logger.debug("Initializing weighting matrix for weighted inversion...")

        init_sigma(iltdata)
        sigmacomp = np.reshape(iltdata.Sigma, (Ncomp, 1), order="F")
        iltdata.isigma = spdiags((1.0 / sigmacomp).flatten(order="F"))

        if iltdata.alt_g == 0:
            vprint1("    Calculating W and Y matrices...")
            logger.debug("Calculating W and Y matrices...")

            iltdata.W = iltdata.K0comp.T @ (iltdata.isigma @ iltdata.isigma) @ iltdata.K0comp
            iltdata.Y = (
                iltdata.K0comp.T @ (iltdata.isigma @ iltdata.isigma) @ iltdata.mcomp
            )

        if iltdata.alt_g == 4:
            logger.debug("Found alt_g = 4, calculating mcompbar...")
            iltdata.mcompbar = iltdata.isigma @ iltdata.mcomp
    else:
        if iltdata.alt_g == 0:
            vprint1("    Calculating W and Y matrices...")
            logger.debug("Calculating W and Y matrices...")

            iltdata.W = iltdata.K0comp.T @ iltdata.K0comp
            iltdata.Y = iltdata.K0comp.T @ iltdata.mcomp

    vprint1("    Kernel initialization done.")
    logger.debug("Kernel initialization done.")


def init_kernel_sparse(iltdata, verbose=0):
    """
    This function initializes kernel matrices if sparsity of kernel matrices is larger than iltdata.sparse_threshold.
    It uses the sparse form of matrices and uses corresponding functions.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class
    verbose : int
        Controls verbosity
    """
    vprint1 = print if verbose > 1 else lambda *args, **kwargs: None

    iltdata.K0comp = spidentity(1, format="csr")
    iltdata.U = []
    iltdata.Ut = []

    for i in range(iltdata.ndim):
        vprint1(f"    Initializing kernel matrix in dimension {i}...")
        logger.debug("Initializing kernel matrix in dimension %s...", i)
        # Adjust size if static baseline feature is used
        if iltdata.sb[i] is True:
            logger.debug("Adjusting the size of K since sb is True for dimension %s", i)
            iltdata.K[i] = np.vstack(
                (iltdata.K[i], np.ones((1, iltdata.K[i].T.shape[0])))
            )

        # SVD compression
        if bool(iltdata.compress[i]) is True:
            if iltdata.use_svds is True:
                vprint1(f"    SVDS compression in dimension {i}...")
                logger.debug("SVDS compression in dimension %s...", i)
                [u1, d1, v1] = svds(iltdata.K[i].T, iltdata.s[i], solver="propack")
            else:
                vprint1(f"    SVD compression in dimension {i}...")
                logger.debug("SVD compression in dimension %s...", i)
                [u1, d1, v1] = svd(iltdata.K[i].T, full_matrices=False)

            v1 = v1.T
            #d1_diag = np.diag(d1[: iltdata.s[i]])
            d1_diag = spdiags(d1[: iltdata.s[i]].flatten())
            v1_red = v1[: iltdata.Nx[i], : iltdata.s[i]]

            iltdata.U.append(u1[: iltdata.Nt[i], : iltdata.s[i]])
            iltdata.K0comp = spkron(
                csr_array(d1_diag @ v1_red.T), iltdata.K0comp, format="csr"
            )
        else:
            # converting K to csr_array is optional, but gets minor performance improvement
            iltdata.K0comp = spkron(
                csr_array(iltdata.K[i].T), iltdata.K0comp, format="csr"
            )
            iltdata.U.append(np.eye(iltdata.Nt[i]))

        iltdata.Ut.append(iltdata.U[i].T)

    Mcomp = _multidim_matmul(iltdata.data, iltdata.Ut)
    Ncomp = int(np.prod(iltdata.s))

    iltdata.mcomp = Mcomp.reshape((Ncomp, 1))
    iltdata.Is = speye(iltdata.K0comp.shape[0])

    # Sigma for weighted inversions
    if iltdata.sigma is not None and iltdata.alt_g in [0, 4]:
        vprint1("    Initializing weighting matrix for weighted inversion...")
        logger.debug("Initializing weighting matrix for weighted inversion...")
        init_sigma(iltdata)
        sigmacomp = np.reshape(iltdata.Sigma, (Ncomp, 1), order="F")
        iltdata.isigma = spdiags((1.0 / sigmacomp).flatten(order="F"))

        if iltdata.alt_g == 0:
            vprint1("    Calculating W and Y matrices...")
            logger.debug("Calculating W and Y matrices...")
            iltdata.W = (
                iltdata.K0comp.T @ (iltdata.isigma @ iltdata.isigma) @ iltdata.K0comp
            )
            iltdata.Y = (
                iltdata.K0comp.T @ (iltdata.isigma @ iltdata.isigma) @ iltdata.mcomp
            )

        if iltdata.alt_g == 4:
            logger.debug("Found alt_g = 4, calculating mcompbar...")
            iltdata.mcompbar = iltdata.isigma @ iltdata.mcomp
    else:
        if iltdata.alt_g == 0:
            vprint1("    Calculating W and Y matrices...")
            logger.debug("Calculating W and Y matrices...")
            iltdata.W = iltdata.K0comp.T @ iltdata.K0comp
            iltdata.Y = iltdata.K0comp.T @ iltdata.mcomp

    vprint1("    Kernel initialization done.")
    logger.debug("Kernel initialization done.")


def init_kernelmatrix(iltdata, verbose=0):
    """
    Initlializes kernel matrices required for inversion, requires that iltdata is intialized.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    verbose : int
        Controls verbosity
    """

    iltdata.K = [
        iltdata.kernel[i].kernel(iltdata.t[i], iltdata.tau[i])
        for i in range(iltdata.ndim)
    ]
    iltdata.K_sparsity = _estimate_sparsity(iltdata.K)
    logger.debug("Estimated sparsity of K0comp : %s", iltdata.K_sparsity)

    if iltdata.K_sparsity > 0.7 and iltdata.alt_g != 0:
        alt_g_warn = (
            "Setting alt_g equal to 0 may show better performance for this inversion."
        )
        warnings.warn(alt_g_warn)
    if iltdata.K_sparsity < 0.6 and iltdata.alt_g == 0 and iltdata.ndim > 1:
        alt_g_warn = (
            "Setting alt_g equal to 6 may show better performance for this inversion."
        )
        warnings.warn(alt_g_warn)

    if iltdata.K_sparsity < iltdata.sparse_threshold and not iltdata.force_sparse:
        logger.debug("Using dense kernel initialization.")
        init_kernel_dense(iltdata, verbose)
        iltdata.solver_type = "default-dense"
    else:
        logger.debug("Using sparse kernel initialization.")
        init_kernel_sparse(iltdata, verbose)
        iltdata.solver_type = "default-sparse"


def init_sigma(iltdata):
    """
    Initializes sigma for weighted inversions.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.
    """
    # Initialize Sigma
    iltdata.Sigma = iltdata.sigma

    if iltdata.Sigma.shape != iltdata.Nt:
        raise ValueError(
            f"Error in initializing weighting matrix. "
            f"Shape of Sigma {iltdata.Sigma.shape} is not equal to data shape: {iltdata.Nt}"
        )

    for i in range(iltdata.ndim):
        if bool(iltdata.compress[i]) is True:
            iltdata.Sigma = np.moveaxis(iltdata.Sigma, i, 0)
            iltdata.Sigma = np.full(
                (iltdata.s[i],) + iltdata.Sigma.shape[1:],
                np.sqrt(np.mean(iltdata.Sigma**2)),
            )
            # Restore original axis order
            iltdata.Sigma = np.moveaxis(iltdata.Sigma, 0, i)
