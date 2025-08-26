# -*- coding: utf-8 -*-
"""
Test the static solver.

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


def test_solver_static_update_no_init(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="STATIC_SOLVER_NOT_INITIALIZED"):
        h2_dtu_10mw_only_blade.solver_static_update()


def test_solver_static_solve_no_init(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="STATIC_SOLVER_NOT_INITIALIZED"):
        h2_dtu_10mw_only_blade.solver_static_solve()


def test_solver_static_init(h2_dtu_10mw_only_blade):

    # First execution is fine.
    h2_dtu_10mw_only_blade.solver_static_init()

    # The next should automatically deallocate the static solver and initialize it again.
    h2_dtu_10mw_only_blade.solver_static_init()


def test_solver_static_update(h2_dtu_10mw_only_blade):
    # This should happen after test_solver_static_init().
    h2_dtu_10mw_only_blade.solver_static_update()


def test_solver_static_solve(h2_dtu_10mw_only_blade):
    # This should happen after test_solver_static_update().
    h2_dtu_10mw_only_blade.solver_static_solve()


def test_solver_static_delete(h2_dtu_10mw_only_blade):
    h2_dtu_10mw_only_blade.solver_static_delete()


def test_static_solver_run_fail(h2_dtu10mw_only_blade_low_max_iter):
    with pytest.raises(RuntimeError, match="STATIC_SOLVER_DID_NOT_CONVERGE"):
        h2_dtu10mw_only_blade_low_max_iter.solver_static_run()


def test_static_solver_run_1(h2_dtu_10mw_only_blade):
    # Use gravity to deflect the clamped blade.

    # Run the static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Test against: initial_condition 2; followed by time simulation.
    val = h2_dtu_10mw_only_blade.get_sensor_values((4, 5, 6))
    npt.assert_allclose(
        val, np.array([-1.071480e+04, -3.974322e-02, -4.064080e+01]), rtol=1e-6
    )


def test_static_solver_run_2(h2_dtu_10mw_only_blade_rotate_base):
    # Apply centrifugal loading with the base command.

    # Run the static solver.
    h2_dtu_10mw_only_blade_rotate_base.solver_static_run(reset_structure=True)

    # Test against: result at the time of writing.
    val = h2_dtu_10mw_only_blade_rotate_base.get_sensor_values((1, 2, 3))
    npt.assert_allclose(val, np.array([-5.02001147e+00, 1.87207970e-01, 1.09028022e+03]))


def test_static_solver_run_3(h2_dtu_10mw_only_blade_rotate_relative):
    # Apply centrifugal loading with the relative command.

    # Run the static solver.
    h2_dtu_10mw_only_blade_rotate_relative.solver_static_run(reset_structure=True)

    # Test against: result at the time of writing.
    val = h2_dtu_10mw_only_blade_rotate_relative.get_sensor_values((1, 2, 3))
    npt.assert_allclose(val, np.array([-5.02001146e+00, 1.87207914e-01, 1.09028022e+03]))


def test_static_solver_run_4(h2_dtu_10mw_only_blade_rotate_bearing3):
    # Apply centrifugal loading with the bearing3 command.

    # Run the static solver.
    h2_dtu_10mw_only_blade_rotate_bearing3.solver_static_run(reset_structure=True)

    # Test against: result at the time of writing.
    # The static solver does not work with bearing3 and we get 0 load.
    val = h2_dtu_10mw_only_blade_rotate_bearing3.get_sensor_values((4, 5, 6))
    npt.assert_allclose(val, np.array([0., 0., 0.]))

    # This is what happens by simulating for a long time.
    # The simulation must be long because the rotor speed is applied impulsively
    # and we get a very long initial transient.
    # h2_dtu_10mw_only_blade_rotate_bearing3.run(500.0)
    # npt.assert_allclose(h2_dtu_10mw_only_blade_rotate_bearing3.get_sensor_values(id),
    #                     np.array([-757.65278331,    4.16512026,    6.05878323]))
    # h2_dtu_10mw_only_blade_rotate_bearing3.run(1000.0)
    # npt.assert_allclose(h2_dtu_10mw_only_blade_rotate_bearing3.get_sensor_values(id),
    #                     np.array([-758.77170923,    4.31107218,    6.05914454]))


def test_static_solver_run_no_reset(h2_dtu_10mw_only_blade):
    # Use gravity to deflect the clamped blade.

    # Run the static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Run it again, without resetting the structure.
    # The static solver must exit immediately and output the same residuals.
    _, resq_1, resg_1, resd_1 = h2_dtu_10mw_only_blade.check_convergence()
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=False)
    _, resq_2, resg_2, resd_2 = h2_dtu_10mw_only_blade.check_convergence()

    npt.assert_allclose(
        np.array([resq_2, resg_2, resd_2]), np.array([resq_2, resg_2, resd_2])
    )


def test_static_solver_run_with_reset(h2_dtu_10mw_only_blade):
    # Use gravity to deflect the clamped blade.

    # Run the static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Run it again, but first reset the structure.
    # The static solver must follow the same convergence history.
    # Note that here we are only checking the last value of the residuals.
    _, resq_1, resg_1, resd_1 = h2_dtu_10mw_only_blade.check_convergence()
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)
    _, resq_2, resg_2, resd_2 = h2_dtu_10mw_only_blade.check_convergence()

    npt.assert_allclose(
        np.array([resq_2, resg_2, resd_2]), np.array([resq_2, resg_2, resd_2])
    )


def test_structure_reset(h2_dtu10mw_only_blade_high_gravity):
    h2 = h2_dtu10mw_only_blade_high_gravity

    id = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
    h2.step()
    val_1 = h2.get_sensor_values(id)
    h2.solver_static_run(reset_structure=True)
    val_2 = h2.get_sensor_values(id)
    h2.structure_reset()
    h2.step()
    val_3 = h2.get_sensor_values(id)

    with npt.assert_raises(AssertionError):
        npt.assert_allclose(val_1, val_2)
    npt.assert_allclose(val_1, val_3)


# %% Main.

if __name__ == "__main__":
    # pytest.main([__file__])
    pytest.main([__file__, "-k test_structure_reset"])
