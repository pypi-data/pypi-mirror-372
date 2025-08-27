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
import numpy as np
from scipy.sparse import kron, csr_array
from scipy.sparse import diags as spdiags
from scipy.sparse import eye as speye
from scipy.special import seterr

# iltpy
from iltpy.utils.scripts import _ilt_movmax_diag

# warnings settings
oldnperr = np.seterr(all="raise", under="ignore")
oldscipyerr = seterr(all="raise", underflow="ignore", slow="ignore", loss="warn")

# logging
logger = logging.getLogger("iltpy_logger")


def init_g_red(iltdata):
    """
    Initialize g_red

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    """
    # initalize g_red
    g_redf = np.identity(1, dtype=int)
    g_red = [None] * iltdata.ndim**2
    g_red_tmp = [None] * iltdata.ndim**2

    temp1 = [np.ones((iltdata.Nx0[i], 1)) for i in range(iltdata.ndim)]
    temp2 = [np.zeros((int(iltdata.sb[i]), 1)) for i in range(iltdata.ndim)]
    temp3 = [np.ones((iltdata.Nx[i], 1)) for i in range(iltdata.ndim)]

    for i in range(iltdata.ndim):
        if iltdata.sb[i] is True:
            g_red[i] = kron(np.vstack((temp1[i], temp2[i])), g_redf)
        else:
            g_red[i] = kron(temp1[i], g_redf)
        for k in range(i):
            g_red[k] = kron(temp3[i], g_red[k])

        g_redf = kron(temp3[i], g_redf)

    del temp1, temp2, temp3

    for i in range(iltdata.ndim**2):
        g_red_tmp[i] = g_red[iltdata.idx[i][0]].multiply(g_red[iltdata.idx[i][1]])

    for i in range(iltdata.ndim, iltdata.ndim**2):
        g_red[i] = g_red[iltdata.idx[i][0]].multiply(g_red[iltdata.idx[i][1]])

    iltdata.g_red = [i.toarray().flatten() for i in g_red]
    logger.debug("Computed g_red")
    iltdata.idx_red = [np.nonzero(g_red_tmp[i])[0] for i in range(iltdata.ndim**2)]
    logger.debug("Computed idx_red")


def amp_reg(iltdata):
    """
    Amplitude regularization

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    """
    if np.sum(iltdata.reg_bc) != 0:
        Vbc = np.zeros(iltdata.Nx)
        Vbc[: iltdata.reg_bc[0]] = iltdata.alpha_bc[0]
        Vbc[iltdata.Nx0[0] - iltdata.reg_bc[0] : iltdata.Nx0[0]] = iltdata.alpha_bc[0]

        for i in range(1, iltdata.ndim):
            Vbc = np.swapaxes(Vbc, 0, i)
            Vbc[: iltdata.reg_bc[i]] += iltdata.alpha_bc[i]
            Vbc[iltdata.Nx0[i] - iltdata.reg_bc[i] : iltdata.Nx0[i]] += (
                iltdata.alpha_bc[i]
            )
            Vbc = np.swapaxes(Vbc, i, 0)

        iltdata.Vbc = spdiags(Vbc.T.flatten(), 0, (iltdata.Nxtot, iltdata.Nxtot))
        logger.debug("Computed amplitude regularization matrix.")
    else:
        iltdata.Vbc = csr_array((iltdata.Nxtot, iltdata.Nxtot))


def init_regmatrix(iltdata, verbose=0):
    """
    This function generates and initializes the regularization matrices.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    verbose : int, optional
        Controls verbosity, by default 0
    """
    vprint1 = print if verbose > 1 else lambda *args, **kwargs: None

    # Initialize g_red
    init_g_red(iltdata)

    vprint1("   Calculating constant, regularization matrices...")
    # Calculate constant, regularization matrices
    lm = [spdiags(np.ones(iltdata.Nx0[k] - 1), -1) for k in range(iltdata.ndim)]
    ld = [speye(iltdata.Nx0[k]) for k in range(iltdata.ndim)]
    lp = [spdiags(np.ones(iltdata.Nx0[k] - 1), 1) for k in range(iltdata.ndim)]

    for i in range(iltdata.ndim):
        if iltdata.sb[i] is True:
            lm[i].resize((iltdata.Nx0[i] + 1, iltdata.Nx0[i] + 1))
            ld[i].resize((iltdata.Nx0[i] + 1, iltdata.Nx0[i] + 1))
            lp[i].resize((iltdata.Nx0[i] + 1, iltdata.Nx0[i] + 1))

            lm[i] = lm[i].tolil()
            ld[i] = ld[i].tolil()
            lp[i] = lp[i].tolil()

            lm[i][-1, -1] = 0
            ld[i][-1, -1] = 0
            lp[i][-1, -1] = 0

    pm = [(p - m) / 2 for p, m in zip(lp, lm)]
    iltdata.Pms = [
        kron(
            speye(np.prod(iltdata.Nx[k + 1 :])),
            kron(pm[k], speye(np.prod(iltdata.Nx[:k]))),
        )
        for k in range(iltdata.ndim)
    ]

    iltdata.Sms = [np.abs(i) for i in iltdata.Pms]

    vm = [p - 2 * d + m for p, d, m in zip(lp, ld, lm)]
    iltdata.Gm = [
        kron(
            speye(np.prod(iltdata.Nx[k + 1 :])),
            kron(vm[k], speye(np.prod(iltdata.Nx[:k]))),
        )
        for k in range(iltdata.ndim)
    ]

    vprint1("   Calculating diagonal matrices...")
    iltdata.GmI = speye(np.prod(iltdata.Nx))
    for ii in range(iltdata.ndim, iltdata.ndim**2, 2):
        tmp_diagU = [k for k in ld]
        tmp_diagL = [k for k in ld]
        tmp_antiU = [k for k in ld]
        tmp_antiL = [k for k in ld]

        tmp_diagU[iltdata.idx[ii][0]] = lp[iltdata.idx[ii][0]]
        tmp_diagL[iltdata.idx[ii][0]] = lm[iltdata.idx[ii][0]]
        tmp_antiU[iltdata.idx[ii][0]] = lp[iltdata.idx[ii][0]]
        tmp_antiL[iltdata.idx[ii][0]] = lm[iltdata.idx[ii][0]]

        tmp_diagU[iltdata.idx[ii][1]] = lp[iltdata.idx[ii][1]]
        tmp_diagL[iltdata.idx[ii][1]] = lm[iltdata.idx[ii][1]]
        tmp_antiU[iltdata.idx[ii][1]] = lm[iltdata.idx[ii][1]]
        tmp_antiL[iltdata.idx[ii][1]] = lp[iltdata.idx[ii][1]]

        GmdU = kron(tmp_diagU[1], tmp_diagU[0])
        GmdL = kron(tmp_diagL[1], tmp_diagL[0])
        GmaU = kron(tmp_antiU[1], tmp_antiU[0])
        GmaL = kron(tmp_antiL[1], tmp_antiL[0])

        for iii in range(2, iltdata.ndim):
            GmdU = kron(tmp_diagU[iii], GmdU)
            GmdL = kron(tmp_diagL[iii], GmdL)
            GmaU = kron(tmp_antiU[iii], GmaU)
            GmaL = kron(tmp_antiL[iii], GmaL)

        iltdata.Gm.append(-2 * iltdata.GmI + GmdU + GmdL)
        iltdata.Gm.append(-2 * iltdata.GmI + GmaU + GmaL)
        iltdata.Pms.append((GmdU - GmdL) / 2)
        iltdata.Pms.append((GmaU - GmaL) / 2)
        iltdata.Sms.append(np.abs(iltdata.Pms[-2]))
        iltdata.Sms.append(np.abs(iltdata.Pms[-1]))

        del GmdU, GmdL, GmaU, GmaL, tmp_diagU, tmp_diagL, tmp_antiU, tmp_antiL

    vprint1("   Calculating amplitude regularization...")

    # Perform amplitude regularization
    amp_reg(iltdata)

    vprint1("   Regularization matrices initialization done.")


def up_reg(iltdata):
    """
    Uniform Penalty regularization.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    """
    # init Gamma_L2
    Gamma_L2 = csr_array((iltdata.Nxtot, iltdata.Nxtot))

    p = [None] * iltdata.ndim**2
    CSq_inv = [None] * iltdata.ndim**2
    gammak = [None] * iltdata.ndim**2

    for i in range(iltdata.ndim**2):
        c = (iltdata.Gm[i] @ iltdata.g.flatten()) ** 2
        p[i] = (iltdata.Pms[i] @ iltdata.g.flatten()) ** 2

        c[iltdata.idx_red[i]] = _ilt_movmax_diag(
            c[iltdata.idx_red[i]], iltdata.Nx0, iltdata.c_nmax[i], iltdata.idx[i]
        )
        p[i][iltdata.idx_red[i]] = _ilt_movmax_diag(
            p[i][iltdata.idx_red[i]], iltdata.Nx0, iltdata.p_nmax[i], iltdata.idx[i]
        )

        igammak = (
            iltdata.alpha_0[i] * iltdata.Delta_Q[i] ** 5
            + iltdata.alpha_p[i] * iltdata.Delta_Q[i] * p[i]
            + iltdata.alpha_c[i] * c / iltdata.Delta_Q[i]
        )

        CSq_inv[i] = np.array(igammak)
        gammak[i] = (
            spdiags(
                np.sqrt(1 / CSq_inv[i]).flatten(), 0, (iltdata.Nxtot, iltdata.Nxtot)
            )
            @ iltdata.Gm[i]
        )

        Gamma_L2 = Gamma_L2 + gammak[i]

    iltdata.CSq_inv = CSq_inv
    u_pen = np.transpose(Gamma_L2) @ Gamma_L2

    return u_pen


def zc_reg(iltdata, it):
    """
    Zero crossing regularization.

    This function computes the zero-crossing (ZC) penalty matrix.
    The ZC penalty discourages oscillatory solutions in the spectrum `g` by penalizing zero-crossings.
    After `zc_down` number of iterations, `zc_ratio` is updated.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    it : int
        Number of iterations
    """
    # init Gamma_L1
    Gamma_L1 = csr_array((iltdata.Nxtot, iltdata.Nxtot))

    ck = [None] * iltdata.ndim**2
    zc_ratio = iltdata.zc_upd

    for i in range(iltdata.ndim**2):
        sg_g = np.sign(iltdata.g).reshape((-1, 1))
        if iltdata.reg_zc is True and it > iltdata.zc_on and i <= iltdata.ndim - 1:
            pa = (
                iltdata.Delta_Q[i]
                * (1 - sg_g.flatten() * (iltdata.Sms[i] @ sg_g).flatten())
                * iltdata.g_red[i]
            )

            if it > iltdata.zc_down:
                zc_ratio = iltdata.zc_upd * np.maximum(
                    (1 - iltdata.zc_downrate) ** (it - iltdata.zc_down),
                    iltdata.zc_updmin,
                )

            mvmax = zc_ratio * _ilt_movmax_diag(
                np.minimum(
                    (pa / (iltdata.alpha_d[i] * iltdata.Delta_Q[i] ** 3)).flatten(),
                    (iltdata.zc_max / iltdata.CSq_inv[i]).flatten(),
                ),
                iltdata.Nx,
                iltdata.zc_nmax[i],
                [i],
            )

            iltdata.Cz[i] = ((1 - zc_ratio) * iltdata.Cz[i]) + mvmax

            ck[i] = (
                spdiags(
                    np.sqrt(iltdata.Cz[i]).flatten(), 0, (iltdata.Nxtot, iltdata.Nxtot)
                )
                @ iltdata.Pms[i]
            )

            Gamma_L1 = Gamma_L1 + ck[i]

    zc_pen = np.transpose(Gamma_L1) @ Gamma_L1

    return zc_pen


def nn_reg(iltdata):
    """
    Non negativity constraint.

    Parameters
    ----------
    iltdata : IltData
        An instance of IltData class.

    """
    sg_g = np.sign(iltdata.g).reshape((-1, 1))
    Gamma_NN2 = spdiags(
        (0.5 * iltdata.alpha_nn[0] * (1 - sg_g)).flatten(),
        0,
        (iltdata.Nxtot, iltdata.Nxtot),
    )

    return Gamma_NN2
