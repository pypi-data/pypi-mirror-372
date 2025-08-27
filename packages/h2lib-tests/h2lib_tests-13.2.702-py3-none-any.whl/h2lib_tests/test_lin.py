# -*- coding: utf-8 -*-
"""
Test the system-eigenanalysis.

@author: ricriv
"""

# Here we are relying on the default behavior of pytest, which is to execute
# the tests in the same order that they are specified.
# If one day this will not be the case anymore, we can enforce the order by
# using the solution proposed at: https://stackoverflow.com/a/77793427/3676517

import pytest

import numpy as np
from numpy import testing as npt

from h2lib._h2lib import H2Lib
from h2lib_tests.test_files import tfp


def test_system_not_linearized_1(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="SYSTEM_NOT_LINEARIZED"):
        h2_dtu_10mw_only_blade.do_system_eigenanalysis(2)


def test_system_not_linearized_2(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="SYSTEM_NOT_LINEARIZED"):
        h2_dtu_10mw_only_blade.get_system_eigenvalues_and_eigenvectors(2, 2)


def test_system_not_linearized_3(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="SYSTEM_NOT_LINEARIZED"):
        h2_dtu_10mw_only_blade.get_system_matrices(312, 156)


def test_linearize(h2_dtu_10mw_only_blade):
    h2_dtu_10mw_only_blade.structure_reset()
    n_tdofs, n_rdofs = h2_dtu_10mw_only_blade.linearize()
    assert n_rdofs == 26 * 6  # = number of nodes * 6
    assert n_tdofs == 26 * 6 * 2  # times 2 because of speed.


def test_too_many_modes(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="TOO_MANY_MODES_REQUESTED"):
        h2_dtu_10mw_only_blade.do_system_eigenanalysis(n_modes=1000)


def test_sys_eig_not_done(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="SYSTEM_EIGENANALYSIS_NOT_DONE"):
        h2_dtu_10mw_only_blade.get_system_eigenvalues_and_eigenvectors(2, 2)


def test_sys_eig_no_damping(h2_dtu_10mw_only_blade):
    natural_frequencies = h2_dtu_10mw_only_blade.do_system_eigenanalysis(
        n_modes=4, include_damping=False
    )
    # Test against: result at the time of writing.
    npt.assert_allclose(
        natural_frequencies,
        np.array([0.610409, 0.930443, 1.739081, 2.761946]),
        rtol=1e-6,
    )


def test_sys_eig_no_damping_wrong_n_modes(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="TOO_MANY_MODES_REQUESTED"):
        h2_dtu_10mw_only_blade.get_system_eigenvalues_and_eigenvectors(1000, 156)


def test_sys_eig_no_damping_wrong_ny(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="WRONG_REDUCED_DOF"):
        h2_dtu_10mw_only_blade.get_system_eigenvalues_and_eigenvectors(4, 2)


def test_sys_eig_no_damping_eigv(h2_dtu_10mw_only_blade):
    n_modes = 4
    n_rdofs = 156
    eig_val, eig_vec = h2_dtu_10mw_only_blade.get_system_eigenvalues_and_eigenvectors(
        n_modes, n_rdofs, include_damping=False
    )
    assert eig_val.size == n_modes
    assert eig_vec.shape == (n_modes, n_rdofs)
    assert eig_val.dtype == np.float64
    assert eig_vec.dtype == np.float64
    npt.assert_allclose(eig_val, [3.835311, 5.846144, 10.92697, 17.353821], atol=2e-6)


def test_sys_eig_with_damping(h2_dtu_10mw_only_blade):
    freq, damp = h2_dtu_10mw_only_blade.do_system_eigenanalysis(
        n_modes=4, include_damping=True
    )
    # Test against: result at the time of writing.
    npt.assert_allclose(
        freq, np.array([0.610409, 0.930444, 1.739086, 2.762015]), rtol=1e-6
    )
    npt.assert_allclose(
        damp, np.array([0.004826, 0.004758, 0.013395, 0.014198]), atol=1e-6
    )


def test_sys_eig_with_damping_eigv(h2_dtu_10mw_only_blade):
    n_modes = 4
    n_rdofs = 156
    eig_val, eig_vec = h2_dtu_10mw_only_blade.get_system_eigenvalues_and_eigenvectors(
        n_modes, n_rdofs, include_damping=True
    )
    assert eig_val.size == n_modes
    assert eig_vec.shape == (n_modes, 2 * n_rdofs)
    assert eig_val.dtype == np.complex128
    assert eig_vec.dtype == np.complex128
    npt.assert_allclose(
        eig_val,
        np.array(
            [
                -0.01851 - 3.835268j,
                -0.027814 - 5.846088j,
                -0.146364 - 10.926018j,
                -0.246401 - 17.352505j,
            ]
        ),
        atol=1e-6,
    )


def test_get_system_matrices_wrong_nt(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="WRONG_TOTAL_DOF"):
        h2_dtu_10mw_only_blade.get_system_matrices(300, 156)


def test_get_system_matrices_wrong_nr(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="WRONG_REDUCED_DOF"):
        h2_dtu_10mw_only_blade.get_system_matrices(312, 150)


def test_get_system_matrices(h2_dtu_10mw_only_blade):
    n_rdofs = 26 * 6
    n_tdofs = 2 * n_rdofs
    M, C, K, R = h2_dtu_10mw_only_blade.get_system_matrices(n_tdofs, n_rdofs)
    assert M.shape == (n_rdofs, n_rdofs)
    assert C.shape == (n_rdofs, n_rdofs)
    assert K.shape == (n_rdofs, n_rdofs)
    assert R.shape == (n_tdofs, n_rdofs)


def test_sys_eig_encrypted(h2_dtu_10mw_only_tower_encrypted):
    h2_dtu_10mw_only_tower_encrypted.structure_reset()
    n_tdofs, n_rdofs = h2_dtu_10mw_only_tower_encrypted.linearize()
    n_modes = 4
    freq, damp = h2_dtu_10mw_only_tower_encrypted.do_system_eigenanalysis(
        n_modes=n_modes, include_damping=True
    )
    eig_val = h2_dtu_10mw_only_tower_encrypted.get_system_eigenvalues_and_eigenvectors(
        n_modes=n_modes, n_rdofs=n_rdofs, include_damping=True
    )
    npt.assert_allclose(freq, [0.770592, 0.770592, 3.449993, 3.449993], atol=1e-5)

    npt.assert_allclose(
        damp,
        np.array([0.010006, 0.010006, 0.044675, 0.044675]),
        atol=1e-6,
    )
    npt.assert_allclose(eig_val, [-0.048444 - 4.84153j,
                                  -0.048444 - 4.84153j,
                                  -0.968409 - 21.6553j,
                                  -0.968409 - 21.6553j], atol=1e-5,
                        )


def test_get_system_matrices_encrypted(h2_dtu_10mw_only_tower_encrypted):
    n_tdofs, n_rdofs = h2_dtu_10mw_only_tower_encrypted.linearize()
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_system_matrices(n_tdofs, n_rdofs)
