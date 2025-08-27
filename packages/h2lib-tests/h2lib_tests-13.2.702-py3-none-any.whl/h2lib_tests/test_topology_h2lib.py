from h2lib._h2lib import H2Lib

from numpy import testing as npt
from h2lib_tests.test_files import tfp
import numpy as np
import pytest


def test_number_of_bodies_and_constraints(
    h2_dtu_10mw_only_tower,
):
    nbdy, ncst = h2_dtu_10mw_only_tower.get_number_of_bodies_and_constraints()
    assert nbdy == 3
    assert ncst == 9


def test_number_of_bodies_and_constraints_encrypted(
    h2_dtu_10mw_only_tower_encrypted,
):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_number_of_bodies_and_constraints()


def test_get_number_of_elements(h2_dtu_10mw_only_tower):
    nelem = h2_dtu_10mw_only_tower.get_number_of_elements()
    npt.assert_array_equal(nelem, np.array([3, 3, 4]))


def test_get_number_of_elements_encrypted(
    h2_dtu_10mw_only_tower_encrypted,
):
    # This test is not really needed, since the check for confidential structure
    # is already done by test_number_of_bodies_and_constraints_encrypted().
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_number_of_elements()


def test_get_timoshenko_location(
    h2_dtu_10mw_only_tower,
):
    # Test first element.
    l, r1, r12, tes = h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=0, ielem=0)
    assert l - 11.5 < 1e-14
    npt.assert_array_equal(r1, np.array([0.0, 0.0, 0]))
    npt.assert_array_almost_equal_nulp(r12, np.array([0.0, 0.0, -11.5]))
    npt.assert_array_equal(
        tes,
        np.array([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]),
    )

    # Test last element.
    l, r1, r12, tes = h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=2, ielem=3)
    assert l - 12.13 < 1e-14
    npt.assert_array_almost_equal_nulp(r1, np.array([0.0, 0.0, -34.5]))
    npt.assert_array_almost_equal_nulp(r12, np.array([0.0, 0.0, -12.13]), nulp=3)
    npt.assert_array_equal(
        tes,
        np.array([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]),
    )


def test_get_timoshenko_location_body_does_not_exist(
    h2_dtu_10mw_only_tower,
):
    with pytest.raises(IndexError, match="BODY_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=1000, ielem=0)


def test_get_timoshenko_location_element_does_not_exist(
    h2_dtu_10mw_only_tower,
):
    with pytest.raises(IndexError, match="ELEMENT_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=0, ielem=1000)


def test_get_timoshenko_location_encrypted(
    h2_dtu_10mw_only_tower_encrypted,
):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_timoshenko_location(ibdy=0, ielem=0)


def test_get_body_rotation_tensor_1(h2_dtu_10mw_only_tower):
    amat = h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_equal(amat, np.eye(3))


def test_get_body_rotation_tensor_2(
    h2_dtu_10mw_only_tower_rotated, write_dtu10mw_only_tower_rotated
):
    amat = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    _, alpha = write_dtu10mw_only_tower_rotated
    alpha_rad = np.deg2rad(alpha)
    sa = np.sin(alpha_rad)
    ca = np.cos(alpha_rad)
    npt.assert_array_almost_equal_nulp(
        amat, np.array([[1.0, 0.0, 0.0], [0.0, ca, -sa], [0.0, sa, ca]])
    )


def test_get_body_rotation_tensor_body_does_not_exist(h2_dtu_10mw_only_tower):
    with pytest.raises(IndexError, match="BODY_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=1000)


def test_get_body_rotation_tensor_encrypted(h2_dtu_10mw_only_tower_encrypted):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_body_rotation_tensor(ibdy=0)


def test_body_output_mass_body_does_not_exist(h2_dtu_10mw_only_tower):
    with pytest.raises(IndexError, match="BODY_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=1000)


def test_body_output_mass_encrypted(h2_dtu_10mw_only_tower_encrypted):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.body_output_mass(ibdy=0)


def test_body_output_mass(h2_dtu10mw_only_blade_1_body):
    body_mass, body_inertia, cog_global_frame, cog_body_frame = h2_dtu10mw_only_blade_1_body.body_output_mass(ibdy=0)

    npt.assert_allclose(body_mass, 41715.74898702217)
    npt.assert_allclose(
        body_inertia,
        np.array(
            [
                4.59166245e07,
                4.59258429e07,
                1.68059539e05,
                -5.46069861e03,
                -1.63069037e05,
                -8.35539506e05,
            ]
        ),
    )
    npt.assert_allclose(
        cog_global_frame, np.array([-0.12113986, -26.17867389, -0.3688314])
    )
    npt.assert_allclose(
        cog_body_frame, np.array([-0.12113986, -0.3688314, 26.17867389])
    )


def test_body_output_element_body_does_not_exist(h2_dtu_10mw_only_tower):
    with pytest.raises(IndexError, match="BODY_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.body_output_element(ibdy=1000, ielem=0)


def test_body_output_element_element_does_not_exist(h2_dtu_10mw_only_tower):
    with pytest.raises(IndexError, match="ELEMENT_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.body_output_element(ibdy=0, ielem=1000)


def test_body_output_element_encrypted(h2_dtu_10mw_only_tower_encrypted):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.body_output_element(ibdy=0, ielem=0)


def test_body_output_element(h2_dtu10mw_only_blade_1_body):
    mass, stiffness, damping = h2_dtu10mw_only_blade_1_body.body_output_element(ibdy=0, ielem=0)
    assert mass.shape == (12, 12)
    assert stiffness.shape == (12, 12)
    assert damping.shape == (12, 12)


def test_set_orientation_base_not_found(h2_dtu_10mw_only_tower):
    with pytest.raises(ValueError, match="MAIN_BODY_NOT_FOUND"):
        h2_dtu_10mw_only_tower.set_orientation_base(main_body="blade")


def test_set_orientation_base_1(h2_dtu_10mw_only_tower, h2_dtu_10mw_only_tower_rotated):
    # Start from h2_dtu_10mw_only_tower and rotate the base.
    # See if it matches h2_dtu_10mw_only_tower_rotated.
    h2_dtu_10mw_only_tower.set_orientation_base(
        main_body="tower", mbdy_eulerang_table=np.array([30.0, 0.0, 0.0])
    )
    amat_desired = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    amat_actual = h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_almost_equal_nulp(amat_actual, amat_desired)
    # Reset orientation.
    h2_dtu_10mw_only_tower.set_orientation_base(main_body="tower")


def test_set_orientation_base_with_reset_orientation(
    h2_dtu_10mw_only_tower_rotated,
):
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower", reset_orientation=True
    )
    amat_actual = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_almost_equal_nulp(amat_actual, np.eye(3))
    # Reset orientation.
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower", mbdy_eulerang_table=np.array([30.0, 0.0, 0.0])
    )


def test_set_orientation_base_without_reset_orientation(
    h2_dtu_10mw_only_tower_rotated,
):
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower",
        mbdy_eulerang_table=np.array([-30.0, 0.0, 0.0]),
        reset_orientation=False,
    )
    amat_actual = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_almost_equal_nulp(amat_actual, np.eye(3))
    # Reset orientation.
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower", mbdy_eulerang_table=np.array([30.0, 0.0, 0.0])
    )


def test_set_orientation_base_speed(h2_dtu_10mw_only_blade):
    # Set speed.
    h2_dtu_10mw_only_blade.set_orientation_base(
        main_body="blade1",
        reset_orientation=False,
        mbdy_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )
    # Run static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade.step()
    val = h2_dtu_10mw_only_blade.get_sensor_values((1, 2, 3))

    # Test against: result at the time of writing.
    # The result is close, but not identical, to test_static_solver_run_2.
    npt.assert_allclose(val, [10879.363449, 793.564425, 1034.896613])

    # Reset speed.
    h2_dtu_10mw_only_blade.set_orientation_base(
        main_body="blade1",
        reset_orientation=False,
    )


def test_set_c2_def_main_body_not_found(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="MAIN_BODY_NOT_FOUND"):
        h2_dtu_10mw_only_blade.set_c2_def(
            "tower",
            np.array([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]),
        )


def test_set_c2_def_too_few_sections(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="TOO_FEW_SECTIONS_IN_C2DEF"):
        h2_dtu_10mw_only_blade.set_c2_def("blade1", np.zeros((1, 4)))


def test_set_c2_def_different_nsec(h2_dtu_10mw_only_blade):
    with pytest.raises(ValueError, match="DIFFERENT_NSEC"):
        h2_dtu_10mw_only_blade.set_c2_def(
            "blade1",
            np.array([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]),
        )


def test_set_c2_def_uniform_node_distribution(
    h2_dtu_10mw_only_blade_uniform_node_distribution,
):
    with pytest.raises(
        NotImplementedError,
    ):
        h2_dtu_10mw_only_blade_uniform_node_distribution.set_c2_def(
            "blade1", np.ones((27, 4), dtype=np.float64, order="F")
        )


def test_set_c2_def_beam_too_short(h2_dtu_10mw_only_blade):
    c2def = np.zeros((27, 4), dtype=np.float64, order="F")
    c2def[:, 2] = np.linspace(0.0, 1e-9, c2def.shape[0])
    with pytest.raises(ValueError, match="BEAM_TOO_SHORT"):
        h2_dtu_10mw_only_blade.set_c2_def("blade1", c2def)


def test_set_c2_def_blade_static_back_to_original(
    write_dtu10mw_only_blade_high_gravity,
    h2_dtu10mw_only_blade_high_gravity,
):
    # This test will:
    #  1. Take the DTU 10 MW blade subjected to high gravity loading.
    #  2. Compute the static solution.
    #  3. Change c2_def a few times and re-compute the static solution.
    #  4. Revert it to the original one and check that the static solution matches the one from step 2.

    # Get the clamped DTU 10 MW blade subjected to high gravity loading.
    _, blade_c2def = write_dtu10mw_only_blade_high_gravity
    h2 = h2_dtu10mw_only_blade_high_gravity

    # Sensors 1 to 6 are the displacement and rotation of the blade tip.
    #   h2.get_sensor_info(1)

    # Run the static solver and get the blade tip position and rotation.
    h2.solver_static_run(reset_structure=True)
    blade_tip_desired = h2.get_sensor_values((1, 2, 3, 4, 5, 6))

    # Change blade length and run the static solver.
    c2def_new = blade_c2def.copy()
    for factor in (0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4):
        c2def_new[:, 2] = factor * blade_c2def[:, 2]
        h2.set_c2_def("blade1", c2def_new)
        # Since we are smoothly changing c2_def, it makes sense to start the static solver from the last converged solution.
        h2.solver_static_run(reset_structure=False)

        # Get new blade displacement.
        blade_tip_actual = h2.get_sensor_values((1, 2, 3, 4, 5, 6))

        # Must differ from blade_tip_desired.
        with npt.assert_raises(AssertionError):
            npt.assert_allclose(blade_tip_actual, blade_tip_desired)

    # Restore blade c2_def.
    h2.set_c2_def("blade1", blade_c2def)
    h2.solver_static_run(reset_structure=True)
    blade_tip_actual = h2.get_sensor_values((1, 2, 3, 4, 5, 6))
    npt.assert_allclose(blade_tip_actual, blade_tip_desired)


def test_set_c2_def_blade_static_deformed(
    write_dtu10mw_only_blade_high_gravity,
    write_dtu10mw_only_blade_high_gravity_deformed,
    h2_dtu10mw_only_blade_high_gravity,
    h2_dtu10mw_only_blade_high_gravity_deformed,
):
    # Solve the static problem with the deformed blade loaded directly by HAWC2.
    h2_dtu10mw_only_blade_high_gravity_deformed.solver_static_run(reset_structure=True)
    blade_tip_desired = h2_dtu10mw_only_blade_high_gravity_deformed.get_sensor_values((1, 2, 3, 4, 5, 6))

    # Set c2_def in the original blade, thus making it equivalent to the deformed one.
    # Then, solve again the static problem.
    _, c2def_deformed = write_dtu10mw_only_blade_high_gravity_deformed
    h2_dtu10mw_only_blade_high_gravity.set_c2_def("blade1", c2def_deformed)
    h2_dtu10mw_only_blade_high_gravity.solver_static_run(reset_structure=True)
    blade_tip_actual = h2_dtu10mw_only_blade_high_gravity_deformed.get_sensor_values((1, 2, 3, 4, 5, 6))

    npt.assert_allclose(blade_tip_actual, blade_tip_desired)

    # Restore c2_def.
    _, c2def_original = write_dtu10mw_only_blade_high_gravity
    h2_dtu10mw_only_blade_high_gravity.set_c2_def("blade1", c2def_original)


@pytest.mark.skip(reason="The system eigenanalysis cannot be called more than once.")
def test_set_c2_def_blade_eig_back_to_original(
    write_dtu10mw_only_blade_high_gravity,
    h2_dtu10mw_only_blade_high_gravity,
):
    # Get the clamped DTU 10 MW blade.
    # We use the fixture with high gravity because it also returns c2_def.
    _, blade_c2def = write_dtu10mw_only_blade_high_gravity
    h2 = h2_dtu10mw_only_blade_high_gravity

    # Solve the eigenvalue problem.
    h2.structure_reset()
    h2.linearize()
    natural_frequencies_desired, damping_ratios_desired = h2.do_system_eigenanalysis(n_modes=6, include_damping=True)

    # Change blade length and solve again the eigenvalue problem
    c2def_new = blade_c2def.copy()
    for factor in (0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4):
        c2def_new[:, 2] = factor * blade_c2def[:, 2]
        h2.set_c2_def("blade1", c2def_new)
        h2.structure_reset()
        h2.linearize()
        natural_frequencies_actual, damping_ratios_actual = h2.do_system_eigenanalysis(n_modes=6, include_damping=True)

        # Must differ from the desired ones.
        with npt.assert_raises(AssertionError):
            npt.assert_allclose(natural_frequencies_actual, natural_frequencies_desired)
        with npt.assert_raises(AssertionError):
            npt.assert_allclose(damping_ratios_actual, damping_ratios_desired)

    # Restore blade c2_def.
    h2.set_c2_def("blade1", blade_c2def)
    h2.structure_reset()
    h2.linearize()
    natural_frequencies_actual, damping_ratios_actual = h2.do_system_eigenanalysis(n_modes=6, include_damping=True)
    npt.assert_allclose(natural_frequencies_actual, natural_frequencies_desired)
    npt.assert_allclose(damping_ratios_actual, damping_ratios_desired)


def test_set_c2_def_blade_mass_back_to_original(
    write_dtu10mw_only_blade_high_gravity_1_body,
    h2_dtu10mw_only_blade_high_gravity_1_body,
):
    # Get the clamped DTU 10 MW blade.
    # We use the fixture with high gravity because it also returns c2_def.
    _, blade_c2def = write_dtu10mw_only_blade_high_gravity_1_body
    h2 = h2_dtu10mw_only_blade_high_gravity_1_body

    # Get the inertia properties.
    h2.structure_reset()
    inertia_desired = h2.body_output_mass(0)

    # Change blade length and compute inertia properties.
    c2def_new = blade_c2def.copy()
    for factor in (0.6, 0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4):
        c2def_new[:, 2] = factor * blade_c2def[:, 2]
        h2.set_c2_def("blade1", c2def_new)
        inertia_actual = h2.body_output_mass(0)

        # Must differ from the desired ones.
        for i in range(4):  # Loop over tuple of arrays.
            with npt.assert_raises(AssertionError):
                npt.assert_allclose(inertia_actual[i], inertia_desired[i])

    # Restore blade c2_def.
    h2.set_c2_def("blade1", blade_c2def)
    inertia_actual = h2.body_output_mass(0)
    for i in range(4):  # Loop over tuple of arrays.
        npt.assert_allclose(inertia_actual[i], inertia_desired[i])


def test_set_c2_def_blade_mass_deformed(
    write_dtu10mw_only_blade_high_gravity,
    write_dtu10mw_only_blade_high_gravity_deformed,
    h2_dtu10mw_only_blade_high_gravity,
    h2_dtu10mw_only_blade_high_gravity_deformed,
):
    # Revert blades to the undeflected configuration.
    h2_dtu10mw_only_blade_high_gravity.structure_reset()
    h2_dtu10mw_only_blade_high_gravity_deformed.structure_reset()

    # Set c2_def in the original blade, thus making it equivalent to the deformed one.
    _, c2def_deformed = write_dtu10mw_only_blade_high_gravity_deformed
    h2_dtu10mw_only_blade_high_gravity.set_c2_def("blade1", c2def_deformed)

    # Compare inertia properties for all bodies.
    nbdy, _ = h2_dtu10mw_only_blade_high_gravity_deformed.get_number_of_bodies_and_constraints()
    for i in range(nbdy):
        inertia_desired = h2_dtu10mw_only_blade_high_gravity_deformed.body_output_mass(i)
        inertia_actual = h2_dtu10mw_only_blade_high_gravity.body_output_mass(i)

        for i in range(4):  # Loop over tuple of arrays.
            npt.assert_allclose(inertia_actual[i], inertia_desired[i], rtol=1e-6)

    # Restore c2_def.
    _, c2def_original = write_dtu10mw_only_blade_high_gravity
    h2_dtu10mw_only_blade_high_gravity.set_c2_def("blade1", c2def_original)


def test_set_c2_def_blade_element_deformed(
    write_dtu10mw_only_blade_high_gravity,
    write_dtu10mw_only_blade_high_gravity_deformed,
    h2_dtu10mw_only_blade_high_gravity,
    h2_dtu10mw_only_blade_high_gravity_deformed,
):
    # Revert blades to the undeflected configuration.
    h2_dtu10mw_only_blade_high_gravity.structure_reset()
    h2_dtu10mw_only_blade_high_gravity_deformed.structure_reset()

    # Set c2_def in the original blade, thus making it equivalent to the deformed one.
    _, c2def_deformed = write_dtu10mw_only_blade_high_gravity_deformed
    h2_dtu10mw_only_blade_high_gravity.set_c2_def("blade1", c2def_deformed)

    # Compare element matrices for all bodies.
    nelem = h2_dtu10mw_only_blade_high_gravity_deformed.get_number_of_elements()
    for ibdy in range(nelem.size):
        for ielem in range(nelem[ibdy]):
            mat_desired = h2_dtu10mw_only_blade_high_gravity_deformed.body_output_element(ibdy, ielem)
            mat_actual = h2_dtu10mw_only_blade_high_gravity.body_output_element(ibdy, ielem)

            npt.assert_allclose(mat_actual[0], mat_desired[0], rtol=1e-10)  # mass
            npt.assert_allclose(mat_actual[1], mat_desired[1], rtol=1e-10)  # stiffness
            npt.assert_allclose(mat_actual[2], mat_desired[2], rtol=1e-10)  # damping

    # Restore c2_def.
    _, c2def_original = write_dtu10mw_only_blade_high_gravity
    h2_dtu10mw_only_blade_high_gravity.set_c2_def("blade1", c2def_original)


def test_set_orientation_relative_main_body_not_found(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    h2_dtu_10mw_only_blade_rotate_relative.stop_on_error(False)
    with pytest.raises(ValueError, match="MAIN_BODY_NOT_FOUND"):
        h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative("hub1", "last", "blade", 0)


def test_set_orientation_relative_rot_not_found(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    with pytest.raises(ValueError, match="RELATIVE_ROTATION_NOT_FOUND"):
        h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
            "hub1", "last", "blade1", "last"
        )


def test_set_orientation_relative_reset(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    # Reset orientation.
    # Now the blade is aligned with the hub, which is vertical.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        reset_orientation=True,
    )
    # Get orientation of blade root.
    amat_actual = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=1
    )
    # It must be the same as the hub.
    amat_desired = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=0
    )
    npt.assert_array_almost_equal_nulp(amat_actual, amat_desired)
    # This matches a rotation around x by 180 deg.
    # angle = np.deg2rad(180.0)
    # s = np.sin(angle)
    # c = np.cos(angle)
    # amat_test = np.array(
    #     [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]],
    # )
    # Reset to original value.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        mbdy2_eulerang_table=np.array([-90.0, 0.0, 0.0]),
        reset_orientation=True,
        mbdy2_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )


def test_set_orientation_relative_2(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    # Get orientation of blade root.
    amat_desired = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=1
    )
    # Change orientation a few times.
    rng = np.random.default_rng(seed=123)
    for _ in range(5):
        h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
            main_body_1="hub1",
            node_1="last",
            main_body_2="blade1",
            node_2=0,
            mbdy2_eulerang_table=rng.uniform(0.0, 360.0, (7, 3)),
            reset_orientation=0,
        )
    # Reset to original value.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        mbdy2_eulerang_table=np.array([-90.0, 0.0, 0.0]),
        reset_orientation=True,
        mbdy2_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )
    # Check.
    amat_actual = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=1
    )
    npt.assert_array_almost_equal_nulp(amat_actual, amat_desired)


def test_set_orientation_relative_static(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    # Set arbitrary orientation and speed.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        reset_orientation=True,
        mbdy2_eulerang_table=np.array([-80.0, 0.0, 0.0]),
        mbdy2_ini_rotvec_d1=[0.0, 1.0, 0.0, 0.8],
    )
    # Run static solver.
    h2_dtu_10mw_only_blade_rotate_relative.solver_static_run(
        reset_structure=True
    )

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade_rotate_relative.step()
    val = h2_dtu_10mw_only_blade_rotate_relative.get_sensor_values((1, 2, 3))

    # Test against: result at the time of writing.
    npt.assert_allclose(val, np.array([8702.206018, 306.728782, 640.051269]))

    # Reset to original value.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        mbdy2_eulerang_table=np.array([-90.0, 0.0, 0.0]),
        reset_orientation=True,
        mbdy2_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )


# %% Main.

if __name__ == "__main__":
    # pytest.main([__file__])
    pytest.main([__file__, "-k test_set_c2_def_blade_element_deformed"])
