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
import time
import logging
import warnings
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from scipy.special import seterr
from scipy.sparse import eye as speye
from scipy.sparse.linalg import spsolve
from scipy.sparse import diags as spdiags
from scipy.sparse.linalg import splu
from scipy.linalg import solve, solve_triangular, cholesky
from joblib import Parallel, delayed

# iltpy
from iltpy.fit.kernels import init_kernelmatrix
from iltpy.fit.regularization import up_reg, nn_reg, zc_reg, init_regmatrix
from iltpy.input.parameters import init_ndim, init_fit_dict
from iltpy.input.parameters import set_parameters, init_parameters
from iltpy.utils.scripts import _multidim_matmul, compute_stats
from iltpy.output.reporting import iltreport

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")
oldscipyerr = seterr(all="raise", underflow="ignore", slow="ignore", loss="warn")
warnings.simplefilter("always", UserWarning)

# logging
logger = logging.getLogger("iltpy_logger")


class IltData:
    """
    Main data handling class for ILTpy.

    Attributes
    ----------
    data : ndarray
        The input data to be inverted.
    t : list of ndarray
        t (input sampling) vectors for each dimension
    tau : list of ndarray
        Tau vectors for each dimension.
    dataset_type : str
        Refers to how the data was loaded, ndarray or txt
    data_dict : dict
        Dictionary containing 'dataset_type', 'data', 'dims' and 'filepath' as keys
    kernel : list of functions
        Kernel function object used for inversion.
    fit_dict : dict
        Dictionary of fit parameters before initialization as provided by user.
    fit_dict_init : dict
        Dictionary of fit parameters after initialization.
    g : ndarray
        The computed distribution after inversion.
    g_guess : ndarray, optional
        User-provided initial guess for the distribution.
    fit : ndarray
        The fitted data after inversion.
    residuals : ndarray
        Difference between fitted data and input data.
    statistics : dict
        Statistical analysis results after running iltstats().
    inverted : bool
        Indicates whether inversion has been performed.
    initialized : bool
        Indicates whether the object has been initialized.
    convergence : list
        List of convergence values for each iteration.
    Gamma2 : sparse matrix
        Regularization matrix used in inversion.
    Vbc : sparse matrix
        Boundary condition regularization matrix.
    nn : bool
        If True, non-negativity is enforced.
    maxloop : int
        Maximum number of inversion iterations.
    conv_limit : float
        Convergence threshold for stopping iterations.
    alt_g : int
        Alternative strategy for calculating g (0, 2, 4, or 6).
    force_sparse : bool
        If True, forces sparse matrix operations, mainly applicable for alt_g = 0.
    sparse_threshold : float
        Threshold for treating kernel matrices as sparse.
    """

    def __init__(self,data_dict):
        self.inception = time.time()
        self.dataset_type = data_dict["dataset_type"]
        self.filepath = data_dict["filepath"]
        self.data = data_dict["data"]
        self.t = data_dict["dims"]
        ndim = len(self.data.shape)

        if ndim > 1 and min(self.data.shape) == 1:
            ndim = ndim - 1
            self.data = np.squeeze(self.data)

        self.user_t_spec = [True]*ndim # check for user-specified t
        # add t for dimension which is likely not inverted.
        if ndim > 1:
            if ndim != len(self.t):
                for i in range(len(self.t), ndim):
                    self.user_t_spec[i] = False
                    self.t.append(np.arange(1, self.data.shape[i] + 1))

        for i in range(ndim):
            if self.data.shape[i] != self.t[i].size:
                raise ValueError(
                    f"Length of t: {self.t[i].size} along dimension {i} does not match "
                    f"length of data: {self.data.shape[i]}"
                )

        self.data_dict = deepcopy(data_dict)
        self.initialized = False
        self.inverted = False

        logger.debug(
            "Created IltData object with data shape: %s and size of t arrays: %s",
            self.data.shape,
            [t_array.size for t_array in self.t],
        )

    def init(
        self,
        tau=None,
        kernel=None,
        parameters=None,
        dim_ndim=None,
        sigma=None,
        g_guess=None,
        verbose=0,
        reinitialize=False,
    ):
        """
        Initializes IltData. The initialization steps are as follows:

        1. init_ndim : Sets dimension-related properties
        2. init_fit_dict : Sets the default parameters
        3. set_parameters : Sets values of fit_dict as class attributes
        4. init_parameters :  Initializes default and any user-defined parameters, consistency checks, etc.
        5. init_kernelmatrix :  Computes the kernel matrix, LHS, RHS of the Ax=B equation and initializes the weighting matrix if provided.
        6. init_regmatrix : Computes the initial regularization matrices.

        Parameters
        ----------
        tau : ndarray, optional
            The tau vector used by the inversion,if None, a logarithmically spaced tau is generated (only valid for relaxation data)

        kernel : object, parent class IltKernel
            A class defining the kernel function.

        dim_ndim : ndarray, optional
            The array defining the n-th dimension of n-D data in case of an uninverted but regularized dimension.

        parameters : dict, optional
            User-defined parameters, provided as a dict.
            Note that data, kernel, tau, g_guess, dim_ndim or sigma can't be provided as parameters and must be provided using keyword arguments.

        sigma : ndarray
            Array used for weighted inversions. It must have the same shape as the data.

        g_guess : ndarray
            User-defined guess for the initial g. It must have the same shape as the expected distribution.

        verbose : int
            Controls verbosity.

        reinitialize : bool
            If IltData is already initialized and if this argument is set to True, default parameters will be reloaded again.
        """

        if self.data is None:
            raise ValueError("IltData.data cannot be None")

        vprint = print if verbose > 0 else lambda *args, **kwargs: None
        vprint("Initializing...")
        logger.debug("Initializing IltData ...")

        start_time = time.time()

        # get dimensions, shape of data, also idx
        init_ndim(self)

        # read default parameters and update in case of user-defined parameters
        vprint("Reading fit parameters...")
        fit_dict = init_fit_dict(
            self, parameters, kernel, tau, dim_ndim, sigma, g_guess, reinitialize
        )

        # parameters as given by the user, before initiliazation.
        self.fit_dict = deepcopy(fit_dict)

        # set the parameters as class attributes
        vprint("Setting fit parameters...")
        set_parameters(self, fit_dict)

        # initializes parameters
        vprint("Initializing fit parameters...")
        init_parameters(self)

        # initialize kernel
        vprint("Initializing kernel matrices...")
        init_kernelmatrix(
            self,
            verbose=verbose,
        )

        # initialize regularization matrices
        vprint("Initializing regularization matrices...")
        init_regmatrix(self, verbose=verbose)

        # store the fit dict after intializing
        self.fit_dict_init = {i: self.__dict__[i] for i in self.fit_dict}

        # set class attributes
        self.inverted = False
        self.initialization_time = round(time.time() - start_time, 3)
        self.initialized = True

        logger.debug(
            "Initialization done. Shapes of data: %s, tau arrays: %s, t arrays: %s",
            self.data.shape,
            [tau_array.shape for tau_array in self.tau],
            [t_array.shape for t_array in self.t],
        )

        vprint(f"Initialization took {self.initialization_time} seconds.")
        logger.debug("Initialization took %s seconds.", self.initialization_time)

    def _setup_inversion(self, solver=None):
        """
        Sets up parameters for iterative inversion procedure.

        Parameters
        ----------
        solver : function, optional
            A function that solves sparse linear systems. The solver should take two arguments:
            - Sparse matrix A (representing W+gamma2)
            - Dense vector b (Y)
            and return the spectrum or distribution `g` as a flattened array.
            If not provided, the default solver is used.
        """

        # set Cz, added so that if invert is called again without init, Cz resets.
        self.Cz = [np.array([0]) for _ in range(self.ndim**2)]
        # make a list to hold convergence progress
        self.convergence = [None] * self.maxloop

        # initial fit with constant regularization matrix proportional to unity matrix
        self.Gamma2 = (
            self.alpha_00 * speye(self.Nxtot, format="csc") / np.mean(self.alpha_0)
        )
        logger.debug(
            "Computed initial Gamma2: constant regularization matrix proportional to unity matrix"
        )

        if self.alt_g != 0:
            logger.debug(
                f"Found alt_g not equal to 0, switching solver to alt_g : {self.alt_g}"
            )
            alt_g_solver = IltSolver(self)
            self.solver_type = "alt_g"
            if self.g_guess is not None:
                self.g = self.g_guess
                logger.debug("User provided an initial guess for g.")
            else:
                self.g = alt_g_solver.alt_g_solve(self)
                logger.debug("Computing initial guess for g")

            return alt_g_solver
        else:
            # set solver
            if solver is not None:
                if not callable(solver):
                    raise ValueError(
                        f"solver must be a callable function, got {type(solver)}."
                    )
                logger.debug("Using user-defined solver")
                self.solver_type = "user-defined"
            else:
                logger.debug("Using default solver")
                solver = IltSolver(self).get_default_solver()

            logger.debug("Solving with alt_g == 0.")
            if self.g_guess is not None:
                self.g = self.g_guess
                logger.debug("User provided an initial guess for g.")
            else:
                self.g = solver(self.W + self.Gamma2, self.Y)
                logger.debug("Computing initial guess for g")

            return solver

    def invert(self, solver=None, verbose=1):
        """
        Perform Inversion with Regularization

        The method iteratively solves the system (W + gamma_2)g = Y, where:
        - W is a sparse matrix representing the system,
        - g is the spectrum to be solved for,
        - Y is the observed data, and
        - gamma_2 is the regularization matrix, which includes terms for uniform penalty,
        zero-crossing penalty, and non-negativity.

        The regularization penalties are updated at each iteration, and the system is solved
        using either a provided solver or a default solver.

        Parameters
        ----------
        solver : function, optional
            A function that solves sparse linear systems. The solver should take two arguments:
            - Sparse matrix A (representing W+gamma2)
            - Dense vector b (Y)
            and return the spectrum `g` as a flattened 1D numpy array of shape (Nxtot,).
            If not provided, the default solver is used.

        verbose : int, default 1
            Controls verbosity. Setting this to zero will not display the progress bar.
            
        store_g : bool, default False
            If True, g (distribution or spectrum) after each iteration is stored in the attrbiute g_list

        Raises
        ------
        RuntimeError
            If the `IltData` object has not been initialized
            with `IltData.init(tau)`, an error is raised.

        ValueError
            If the provided initial guess for `g` does not match the expected size.
        """
        vprint = print if verbose > 0 else lambda *args, **kwargs: None

        if not self.initialized:
            raise RuntimeError(
                "invert() called on an uninitialized IltData object. Please call init() first."
            )
        
        logger.debug(
            "Starting inversion. Shapes of data: %s, tau arrays: %s, t arrays: %s",
            self.data.shape,
            [tau_array.shape for tau_array in self.tau],
            [t_array.shape for t_array in self.t],
        )

        # set up the inversion
        if self.alt_g != 0:
            alt_g_solver = self._setup_inversion(solver=solver)
        else:
            solver = self._setup_inversion(solver=solver)

        # start iterations
        vprint("Starting iterations ...")
        logger.debug("Starting iterations ...")
        start_time = time.time()
        i = 0
        
        if self.store_g:
            self.g_list = [np.reshape(self.g, self.Nx, order="F")]
        if self.store_gamma:
            self.gamma_list = [self.Gamma2]
        
        for i in tqdm(range(self.maxloop), disable=(verbose <= 0)):
            g_old = self.g

            ## UP regularization
            u_pen = up_reg(self)

            ## ZC regularization
            zc_pen = zc_reg(self, i)

            ## total reg term
            reg_term = u_pen + zc_pen + self.Vbc

            ## Gamma_NN2, non negativity
            if self.nn:
                nn_con = nn_reg(self)
                reg_term = reg_term + nn_con

            ## Gamma2
            gamma2 = self.alpha_00 * reg_term

            if i > self.reg_down:
                upd_ratio = self.reg_upd * max(
                    (1 - self.reg_downrate) ** (i - self.reg_down), self.reg_updmin
                )
                gamma2 = upd_ratio * gamma2 + (1 - upd_ratio) * self.Gamma2

            self.Gamma2 = gamma2
            ## solve for g
            if self.alt_g != 0:
                self.g = alt_g_solver.alt_g_solve(self)
            else:
                self.g = solver(self.W + self.Gamma2, self.Y)

            ## convergence limit check
            try:
                g_norm = np.linalg.norm(self.g)
                self.convergence[i] = np.linalg.norm(self.g - g_old) / g_norm
            except FloatingPointError as e:
                print(
                    f"||g|| = {g_norm}, max(g) = {np.max(self.g)}, min(g) = {np.min(self.g)}"
                )
                raise FloatingPointError(e)

            logger.debug(
                "||g-g_old||/||g|| = %.3e ||g|| = %.3e, max(g) = %.3e, min(g) = %.3e",
                self.convergence[i],
                np.linalg.norm(self.g),
                np.max(self.g),
                np.min(self.g),
            )
            
            if self.store_g:
                self.g_list.append(np.reshape(self.g, self.Nx, order="F"))
            if self.store_gamma:
                self.gamma_list.append(self.Gamma2)

            if self.convergence[i] < self.conv_limit:
                vprint(f"\nConvergence limit reached at iteration {i}.")
                break

        # store results
        self._post_inversion(start_time, i)
        vprint("Done.")

    def _post_inversion(self, start_time, iteration_number):
        """
        Computes fits, stores results post inversion.

        Parameters
        ----------
        start_time : float
            Time at which iterations started
        i : int
            Iteration at which inversion completed.
        """
        ## Store time taken for inversion
        self.inversion_time = round(time.time() - start_time, 3)
        logger.debug(
            f"Iterations completed at iteration number {iteration_number}, time taken: {self.inversion_time} seconds."
        )

        ## Store the last g before reshaping
        self.g_old = self.g.copy()

        ## Reshape from vector to matrix form
        if self.ndim > 1:
            logger.debug("Reshaping g from %s to %s", self.g.shape, self.Nx)
            self.g = np.reshape(self.g, self.Nx, order="F")

        ## Store results
        K = [k.T for k in self.K]
        logger.debug("Computing fit...")
        datafit = _multidim_matmul(self.g, K).T
        logger.debug("Setting class attributes...")
        self.fit = datafit
        self.residuals = self.fit - self.data
        self.inverted = True
        logger.debug("Inversion completed successfully.")

    def iltstats(self, n=10, solver=None, n_jobs=-1, verbose=1, random_seed=None):
        """
        Calculates statistical parameters for a distribution by adding random noise to the initial fit of the data
        and inverting `n` times.

        Parameters
        ----------
        n : int, optional
            The number of times the data is refit with different noise vectors, must be at least 2.
            If None, then `n` is set equal to 10.

        solver : function, optional
            The solver used for inversion.

        n_jobs : int, default -1
            The number of parallel jobs to create, by default -1. This will create as many jobs as cpu cores present on the system.

        verbose : int, default 0
            Controls joblib's verbosity.

        random_seed : int, optional
            Random seed for reproducible noise vector initialization.
        """
        if not self.inverted:
            raise RuntimeError(
                "IltData must be inverted at least once before computing statistics."
            )

        if not n >= 2:
            raise ValueError("Number of samples,n, must be >=2.")

        # preparation
        temp_data = deepcopy(self)
        initial_fit = self.fit
        tau = self.tau
        kernel = self.kernel
        parameters = self.user_parameters

        if random_seed is not None:
            np.random.seed(random_seed)

        # output dictionary for storing results
        out_dict = {
            "g_list": [None] * n,
            "fit_list": [None] * n,
            "residuals_list": [None] * n,
            "noise_samples": [np.random.randn(*initial_fit.shape) for _ in range(n)],
        }

        # make samples for analysis
        out_dict["data_samples"] = [
            initial_fit + noise_vec for noise_vec in out_dict["noise_samples"]
        ]

        # function for handling each sample
        def invert_sample(sample, iltdata, tau, kernel, parameters, solver):
            """
            Sub-function to invert each sample.
            """
            iltdata.data = sample.copy()
            iltdata.init(tau, kernel, parameters=parameters)
            iltdata.invert(solver=solver, verbose=-1)

            return {"g": iltdata.g, "fit": iltdata.fit, "residuals": iltdata.residuals}

        # Perform parallel inversion of samples
        results = Parallel(n_jobs=n_jobs, verbose=verbose, backend="loky")(
            delayed(invert_sample)(
                out_dict["data_samples"][i], temp_data, tau, kernel, parameters, solver
            )
            for i in range(n)
        )

        del temp_data

        # Collect results
        for idx, result in enumerate(results):
            out_dict["g_list"][idx] = result["g"]
            out_dict["fit_list"][idx] = result["fit"]
            out_dict["residuals_list"][idx] = result["residuals"]

        self.statistics = out_dict
        compute_stats(self)

    def report(
        self, filepath=None, save_arrays=False, level=0, parameters_to_file=False
    ):
        """
        Generates .txt files from results of inversion. Requires the dataset to be inverted.

        Parameters
        ----------
        filepath : str, optional
            Path where the results should be saved. If None, results are saved in the current working directory, by default None
        save_arrays : bool, by default False
            Whether to also output a file with numpy arrays in npz format.
        level : int, optional
            Controls the depth of saved data. Default is 0.
            - 0: Save attributes of type `np.ndarray`.
            - 1: Additionally, save lists containing only `np.ndarray` elements.
            - 2: Additionally, save sparse matrices (converted to dense arrays).
        parameters_to_file : bool, optional
            If True, saves the fit parameters to a separate file along with the results.
        """
        iltreport(
            self,
            filepath=filepath,
            save_arrays=save_arrays,
            level=level,
            parameters_to_file=parameters_to_file,
        )


class IltSolver:
    """
    Class for handling alternative strategies for calculating g.
    """

    def __init__(self, iltdata):
        self.alt_g = iltdata.alt_g
        # Make K0comp dense when alt_g != 0, this might fail for very large matrices.
        if not isinstance(iltdata.K0comp, np.ndarray) and self.alt_g in [2,4,6]:
            iltdata.K0comp = iltdata.K0comp.toarray()
            logger.debug("Converted K0comp to a dense array since alt_g is not equal 0")
        self.K_sparsity = iltdata.K_sparsity
        self.force_sparse = iltdata.force_sparse
        self.sparse_threshold = iltdata.sparse_threshold

    def get_default_solver(self):
        """
        Selects the default solver in case of alt_g=0 based on kernel sparsity.
        This function either returns scipy's spsolve or numpy's solve.

        The `permc_spec='NATURAL'` parameter specifies the natural ordering of the matrix
        for sparse LU decomposition. This ordering is chosen as the default because it
        avoids additional reordering overhead and is generally efficient for well-structured
        matrices, which are common in this application.

        Returns
        -------
        function
            A solver function as a lambda function based on kernel sparsity. For dense kernels, scipy.linalg.solve
            and for sparse kernels, scipy.sparse.linalg.spsolve is returned.
        """
        if self.K_sparsity < self.sparse_threshold and not self.force_sparse:
            logger.debug("Selected default solver : dense solver")
            return lambda A, b: solve(A.toarray() if not isinstance(A, np.ndarray) else A, b).flatten() # allows for solving even if A is sparse
        else:
            logger.debug("Selected default solver : sparse solver")
            return lambda A, b: spsolve(A, b, permc_spec="NATURAL")

    def alt_g_solve(self, iltdata):
        """
        Switches the strategy for calculating g based on the value of alt_g.

        Parameters
        ----------
        iltdata : IltData
            An instance of IltData class which is already initialized.

        Returns
        -------
        ndarray
            g as a flattened array

        Raises
        ------
        ValueError
            If alt_g parameter is not one of the accepted values : [0,2,4,6]
        """
        if iltdata.alt_g in [2,4,6]:
            AbarT, upper_tri = self._compute_AbarT(iltdata)

        if self.alt_g == 2:
            logger.debug("Computing xbar...")
            xbar = (
                AbarT
                @ (iltdata.Is - solve(iltdata.Is + AbarT.T @ AbarT, AbarT.T @ AbarT))
                @ iltdata.mcomp
            )
            logger.debug("Solving for g...")
            g = solve_triangular(upper_tri, xbar, lower=False, check_finite=False)
            return g.flatten()

        elif self.alt_g == 4:
            if iltdata.sigma is not None:
                logger.debug("Found sigma is not None, computing AbarT @ iltdata.isigma ...")
                AbarT = AbarT @ iltdata.isigma
                logger.debug("Computing cr...")
                cr = solve((AbarT.T @ AbarT + iltdata.Is), iltdata.mcompbar)
            else:
                logger.debug("Computing cr...")
                cr = solve((AbarT.T @ AbarT + iltdata.Is), iltdata.mcomp)
            logger.debug("Computing xbar...")
            xbar = AbarT @ cr
            logger.debug("Solving for g...")
            g = solve_triangular(upper_tri, xbar, lower=False, check_finite=False)
            return g.flatten()

        elif self.alt_g == 6:
            logger.debug("Computing AbarT2...")
            AbarT2 = AbarT.T @ AbarT
            logger.debug("Computing xbar...")
            xbar = AbarT @ (
                iltdata.mcomp - solve(iltdata.Is + AbarT2, AbarT2 @ iltdata.mcomp)
            )
            logger.debug("Solving for g...")
            g = solve_triangular(upper_tri, xbar, lower=False, check_finite=False)
            return g.flatten()
        
        elif self.alt_g == 8:
            # sparse LU decomposition
            logger.debug("Computing LU decompostion of Gamma2")
            lu_decomp = splu(iltdata.Gamma2, diag_pivot_thresh=0, permc_spec="NATURAL")
            # cholesky upper triangle from LU decomp
            logger.debug("Computing upper triangular matrix from LU decomposition")
            lower_tri = lu_decomp.L.dot(spdiags(lu_decomp.U.diagonal() ** 0.5)).toarray()

            # calculate AbarT
            AbarT = solve_triangular(
                lower_tri, iltdata.K0comp.T, lower=True, check_finite=False
            )

            AbarT2 = AbarT.T @ AbarT
            xbar = AbarT @ (
                iltdata.mcomp - solve(iltdata.Is + AbarT2, AbarT2 @ iltdata.mcomp)
            )
            g = solve_triangular(lower_tri.T, xbar, lower=False, check_finite=False)
            return g.flatten()

        else:
            raise ValueError(
                f"Invalid alt_g value: {self.alt_g}. Valid options are [0, 2, 4, 6, 8]."
            )

    def _compute_AbarT(self, iltdata):
        """
        Compute AbarT

        Parameters
        ----------
        iltdata : IltData
            An instance of iltdata class

        Returns
        -------
        AbarT
            ndarray
        upper_tri
            ndarray
        """

        #upper_tri = cholesky(iltdata.Gamma2.toarray(),check_finite=False,lower=False)
        logger.debug("Computing Cholesky factorisation...")
        lower_tri = cholesky(iltdata.Gamma2.toarray(),check_finite=False,lower=True) # slightly faster

        # calculate AbarT
        logger.debug("Computing AbarT...")
        AbarT = solve_triangular(
            lower_tri, iltdata.K0comp.T, lower=True, check_finite=False
        )

        return AbarT, lower_tri.T
