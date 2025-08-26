import numpy as np
import pytest
from wetb.hawc2.htc_file import HTCFile
from wetb.hawc2.mainbody import MainBody
from h2lib_tests.test_files import tfp
from h2lib._h2lib import H2Lib


@pytest.fixture(scope="session")
def write_dtu10mw_only_tower():
    # Start from DTU_10MW_RWT and delete everything except the tower.
    htc = HTCFile(tfp + "DTU_10_MW/htc/DTU_10MW_RWT.htc")
    htc.set_name("DTU_10MW_RWT_only_tower")
    for key1 in htc["new_htc_structure"].keys():
        if key1.startswith("main_body"):
            if "tower" not in htc["new_htc_structure"][key1]["name"].values:
                htc["new_htc_structure"][key1].delete()
        if key1 == "orientation":
            for key2 in htc["new_htc_structure"]["orientation"].keys():
                if key2.startswith("relative"):
                    htc["new_htc_structure"]["orientation"][key2].delete()
        if key1 == "constraint":
            for key2 in htc["new_htc_structure"]["constraint"].keys():
                if key2 != "fix0":
                    htc["new_htc_structure"]["constraint"][key2].delete()
    htc["wind"].delete()
    htc["aerodrag"].delete()
    htc["aero"].delete()
    htc["dll"].delete()
    htc["output"].delete()
    # Reduce simulation time.
    htc.simulation.time_stop = 10.0
    # Change number of bodies in the tower.
    htc.new_htc_structure.main_body.nbodies = 3
    # Save the new file.
    htc.save()
    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_tower_rotated(write_dtu10mw_only_tower):
    # Start from the DTU_10MW_RWT_only_tower and rotate the tower.
    htc = write_dtu10mw_only_tower.copy()
    htc.set_name("DTU_10MW_RWT_only_tower_rotated")
    alpha = 30.0
    htc.new_htc_structure.orientation.base.body_eulerang = [
        alpha,
        0.0,
        0.0,
    ]
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()
    return (htc, alpha)


@pytest.fixture(scope="session")
def write_dtu10mw_only_tower_encrypted(write_dtu10mw_only_tower):
    # Start from the DTU_10MW_RWT_only_tower and then encrypt the tower.
    htc = write_dtu10mw_only_tower.copy()
    htc.set_name("DTU_10MW_RWT_only_tower_encrypted")
    # Only the tower is left.
    htc.new_htc_structure.main_body.timoschenko_input.filename = (
        "./data/DTU_10MW_RWT_Tower_st.dat.v3.enc"
    )
    htc.save()


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade():
    # Start from DTU_10MW_RWT and delete everything except the blade.
    htc = HTCFile(tfp + "DTU_10_MW/htc/DTU_10MW_RWT.htc")
    htc.set_name("DTU_10MW_RWT_only_blade")
    for key1 in htc["new_htc_structure"].keys():
        if key1.startswith("main_body"):
            if "blade1" not in htc["new_htc_structure"][key1]["name"].values:
                htc["new_htc_structure"][key1].delete()
        if key1 == "orientation":
            htc["new_htc_structure"][key1].delete()
        if key1 == "constraint":
            htc["new_htc_structure"][key1].delete()
    htc["wind"].delete()
    htc["aerodrag"].delete()
    htc["aero"].delete()
    htc["dll"].delete()
    htc["output"].delete()

    # Set the blade horizontal, to maximize gravity loading.
    htc.new_htc_structure.add_section("orientation")
    htc.new_htc_structure.orientation.add_section("base")
    htc.new_htc_structure.orientation.base.mbdy = "blade1"
    htc.new_htc_structure.orientation.base.inipos = [0.0, 0.0, 0.0]
    htc.new_htc_structure.orientation.base["mbdy_eulerang"] = [90.0, 0.0, 0.0]
    htc.new_htc_structure.orientation.base.mbdy_eulerang.comments = (
        "Blade span is horizontal."
    )

    # Clamp the blade.
    htc.new_htc_structure.add_section("constraint")
    htc.new_htc_structure.constraint.add_section("fix0")
    htc.new_htc_structure.constraint.fix0.mbdy = "blade1"

    # Set as many bodies as elements.
    htc.new_htc_structure.main_body__7.nbodies = 26

    htc.simulation.log_deltat.delete()

    # Do not use static solver, since it will be done during the test.
    htc.simulation.solvertype = 2
    htc.simulation.solvertype.comments = ""
    htc.simulation.initial_condition = 1

    # Set low convergence limits.
    htc.simulation.convergence_limits = [1e2, 1e-5, 1e-07]

    # No output, as we will use add_sensor().

    # Save the new file.
    htc.save()

    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_low_max_iter(write_dtu10mw_only_blade):
    # Start from the write_dtu10mw_only_blade and then reduce the number of max iterations,
    # so that the static solver will not have time to converge.
    htc = write_dtu10mw_only_blade.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_low_max_iter")
    htc.simulation.max_iterations = 1
    htc.save()

    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_1_body(write_dtu10mw_only_blade):
    # Start from the write_dtu10mw_only_blade and then set the number of bodies to 1.
    # This is to compute its mass properties.
    htc = write_dtu10mw_only_blade.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_1_body")
    htc.new_htc_structure.main_body__7.nbodies = 1
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()

    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_rotate_base(write_dtu10mw_only_blade):
    # Start from the write_dtu10mw_only_blade and then make it rotate by using the base command.
    # HAWC2 will use the initial condition, but then the blade will not rotate because of the fix0 constraint.
    # So, running the simulation will show a clamped blade that vibrates.
    # Rotate at about 9.5 rpm.
    htc = write_dtu10mw_only_blade.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_rotate_base")
    speed = 1.0  # [rad/s]
    htc.new_htc_structure.orientation.base["mbdy_ini_rotvec_d1"] = [
        0.0,
        1.0,
        0.0,
        speed,
    ]
    htc.new_htc_structure.orientation.base.mbdy_ini_rotvec_d1.comments = (
        f"= {speed * 30.0 / np.pi:.2f} rpm"
    )
    htc.new_htc_structure.main_body__7.gravity = 0.0
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()
    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_rotate_relative():
    # Start from DTU_10MW_RWT and delete everything except the blade and hub.
    # The blade now rotates because of the relative rotation.
    # Because of the fix1 constraint, the blade will not rotate after time 0.
    htc = HTCFile(tfp + "DTU_10_MW/htc/DTU_10MW_RWT.htc")
    htc.set_name("DTU_10MW_RWT_only_blade_rotate_relative")
    for key1 in (
        "main_body",  # tower
        "main_body__2",  # towertop
        "main_body__3",  # shaft
        "main_body__5",  # hub2
        "main_body__6",  # hub3
        "main_body__8",  # blade2
        "main_body__9",  # blade3
        "orientation",
        "constraint",
    ):
        htc["new_htc_structure"][key1].delete()
    htc["wind"].delete()
    htc["aerodrag"].delete()
    htc["aero"].delete()
    htc["dll"].delete()
    htc["output"].delete()

    # Set the hub as vertical.
    htc.new_htc_structure.add_section("orientation")
    htc.new_htc_structure.orientation.add_section("base")
    htc.new_htc_structure.orientation.base.mbdy = "hub1"
    htc.new_htc_structure.orientation.base.inipos = [0.0, 0.0, 0.0]
    htc.new_htc_structure.orientation.base["mbdy_eulerang"] = [180.0, 0.0, 0.0]
    htc.new_htc_structure.orientation.base.mbdy_eulerang.comments = (
        "Hub axis is up."
    )

    # Set the blade horizontal.
    htc.new_htc_structure.orientation.add_section("relative")
    htc.new_htc_structure.orientation.relative.mbdy1 = "hub1  last"
    htc.new_htc_structure.orientation.relative.mbdy2 = "blade1  1"
    htc.new_htc_structure.orientation.relative["mbdy2_eulerang"] = [
        -90.0,
        0.0,
        0.0,
    ]
    htc.new_htc_structure.orientation.relative.mbdy2_eulerang.comments = (
        "Blade span is horizontal."
    )
    speed = 1.0  # [rad/s]
    htc.new_htc_structure.orientation.relative["mbdy2_ini_rotvec_d1"] = [
        0.0,
        1.0,
        0.0,
        speed,
    ]
    htc.new_htc_structure.orientation.relative.mbdy2_ini_rotvec_d1.comments = (
        f"= {speed * 30.0 / np.pi:.2f} rpm"
    )

    # Disable gravity.
    htc.new_htc_structure.main_body__7.gravity = 0.0
    htc.new_htc_structure.main_body__4.gravity = 0.0

    # Clamp the hub and blade.
    htc.new_htc_structure.add_section("constraint")
    htc.new_htc_structure.constraint.add_section("fix0")
    htc.new_htc_structure.constraint.fix0.mbdy = "hub1"
    htc.new_htc_structure.constraint.add_section("fix1")
    htc.new_htc_structure.constraint.fix1.mbdy1 = "hub1  last"
    htc.new_htc_structure.constraint.fix1.mbdy2 = "blade1  1"

    # Set as many bodies as elements.
    htc.new_htc_structure.main_body__7.nbodies = 26

    htc.simulation.log_deltat.delete()

    # Do not use static solver, since it will be done during the test.
    htc.simulation.solvertype = 2
    htc.simulation.solvertype.comments = ""
    htc.simulation.initial_condition = 1

    # Set low convergence limits.
    htc.simulation.convergence_limits = [1e2, 1e-5, 1e-07]

    # Save the new file.
    htc.save()

    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_rotate_bearing3():
    # Start from DTU_10MW_RWT and delete everything except the blade and hub.
    # The blade now rotates because of the bearing3 between the blade and hub.
    htc = HTCFile(tfp + "DTU_10_MW/htc/DTU_10MW_RWT.htc")
    htc.set_name("DTU_10MW_RWT_only_blade_rotate_bearing3")
    for key1 in (
        "main_body",  # tower
        "main_body__2",  # towertop
        "main_body__3",  # shaft
        "main_body__5",  # hub2
        "main_body__6",  # hub3
        "main_body__8",  # blade2
        "main_body__9",  # blade3
        "orientation",
        "constraint",
    ):
        htc["new_htc_structure"][key1].delete()
    htc["wind"].delete()
    htc["aerodrag"].delete()
    htc["aero"].delete()
    htc["dll"].delete()
    htc["output"].delete()

    # Set the hub as vertical.
    htc.new_htc_structure.add_section("orientation")
    htc.new_htc_structure.orientation.add_section("base")
    htc.new_htc_structure.orientation.base.mbdy = "hub1"
    htc.new_htc_structure.orientation.base.inipos = [0.0, 0.0, 0.0]
    htc.new_htc_structure.orientation.base["mbdy_eulerang"] = [180.0, 0.0, 0.0]
    htc.new_htc_structure.orientation.base.mbdy_eulerang.comments = (
        "Hub axis is up."
    )

    # Set the blade horizontal.
    htc.new_htc_structure.orientation.add_section("relative")
    htc.new_htc_structure.orientation.relative.mbdy1 = "hub1  last"
    htc.new_htc_structure.orientation.relative.mbdy2 = "blade1  1"
    htc.new_htc_structure.orientation.relative["mbdy2_eulerang"] = [
        -90.0,
        0.0,
        0.0,
    ]
    htc.new_htc_structure.orientation.relative.mbdy2_eulerang.comments = (
        "Blade span is horizontal."
    )

    # Disable gravity.
    htc.new_htc_structure.main_body__7.gravity = 0.0
    htc.new_htc_structure.main_body__4.gravity = 0.0

    # Clamp the hub.
    htc.new_htc_structure.add_section("constraint")
    htc.new_htc_structure.constraint.add_section("fix0")
    htc.new_htc_structure.constraint.fix0.mbdy = "hub1"

    # Insert bearing3.
    htc.new_htc_structure.constraint.add_section("bearing3")
    htc.new_htc_structure.constraint.bearing3.name = "bearing"
    htc.new_htc_structure.constraint.bearing3.mbdy1 = "hub1 last"
    htc.new_htc_structure.constraint.bearing3.mbdy2 = "blade1 1"
    htc.new_htc_structure.constraint.bearing3.bearing_vector = [
        1,
        0.0,
        0.0,
        1.0,
    ]
    speed = 1.0  # [rad/s]
    htc.new_htc_structure.constraint.bearing3.omegas = speed
    htc.new_htc_structure.constraint.bearing3.omegas.comments = (
        f"= {speed * 30.0 / np.pi:.2f} rpm"
    )

    # Set as many bodies as elements.
    htc.new_htc_structure.main_body__7.nbodies = 26

    htc.simulation.log_deltat.delete()

    # Do not use static solver, since it will be done during the test.
    htc.simulation.solvertype = 2
    htc.simulation.solvertype.comments = ""
    htc.simulation.initial_condition = 1

    # Save the new file.
    htc.save()

    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_uniform_node_distribution(
    write_dtu10mw_only_blade,
):
    # Start from the write_dtu10mw_only_blade and then change the nodes distribution to uniform.
    htc = write_dtu10mw_only_blade.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_uniform_node_distribution")
    htc.new_htc_structure.main_body__7.nbodies = 10
    htc.new_htc_structure.main_body__7.node_distribution = ["uniform", 11]
    # Somehow the wind and output blocks are back.
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()
    return htc


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_high_gravity(
    write_dtu10mw_only_blade,
):
    # Start from the write_dtu10mw_only_blade and then increase the gravity loading.
    htc = write_dtu10mw_only_blade.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_high_gravity")
    htc.new_htc_structure.main_body__7.gravity = 100.0
    mb = MainBody(htc, "blade1")
    blade_c2def = mb.c2def
    # Somehow the wind and output blocks are back.
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()
    return htc, blade_c2def


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_high_gravity_1_body(
    write_dtu10mw_only_blade_high_gravity,
):
    # Start from the write_dtu10mw_only_blade_high_gravity and then set 1 body.
    htc_ori, _ = write_dtu10mw_only_blade_high_gravity
    htc = htc_ori.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_high_gravity_1_body")
    htc.new_htc_structure.main_body__7.nbodies = 1
    mb = MainBody(htc, "blade1")
    blade_c2def = mb.c2def
    # Somehow the wind and output blocks are back.
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()
    return htc, blade_c2def


@pytest.fixture(scope="session")
def write_dtu10mw_only_blade_high_gravity_deformed(
    write_dtu10mw_only_blade,
):
    # Start from the write_dtu10mw_only_blade and then increase the gravity loading.
    htc = write_dtu10mw_only_blade.copy()
    htc.set_name("DTU_10MW_RWT_only_blade_high_gravity_deformed")
    htc.new_htc_structure.main_body__7.gravity = 100.0
    # Deform c2_def.
    mb = MainBody(htc, "blade1")
    blade_c2def = mb.c2def
    blade_c2def[:, 0] *= 1.3
    blade_c2def[:, 1] *= 0.8
    blade_c2def[:, 2] *= 1.2
    blade_c2def[:, 3] -= 3.42796
    # Loop over the sec and set c2def.
    i = 0
    htc.new_htc_structure.main_body__7.c2_def.sec = f"{i + 1}  {blade_c2def[i, 0]:.14f}  {blade_c2def[i, 1]:.14f}  {blade_c2def[i, 2]:.14f}  {blade_c2def[i, 3]:.14f}"
    for i in range(1, blade_c2def.shape[0]):
        setattr(htc.new_htc_structure.main_body__7.c2_def, f"sec__{i + 1}", f"{i + 1}  {blade_c2def[i, 0]:.14f}  {blade_c2def[i, 1]:.14f}  {blade_c2def[i, 2]:.14f}  {blade_c2def[i, 3]:.14f}")

    # Somehow the wind and output blocks are back.
    htc["wind"].delete()
    htc["output"].delete()
    htc.save()
    return htc, blade_c2def


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_tower(write_dtu10mw_only_tower):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_tower.htc"
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_tower_rotated(write_dtu10mw_only_tower_rotated):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_tower_rotated.htc"
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_tower_encrypted(write_dtu10mw_only_tower_encrypted):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_tower_encrypted.htc"
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_blade(write_dtu10mw_only_blade):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade.htc"
    h2.add_sensor("mbdy forcevec blade1 1 1 blade1")  # 1, 2, 3
    h2.add_sensor("mbdy momentvec blade1 1 1 blade1")  # 4, 5, 6
    h2.add_sensor("mbdy statevec_new blade1 c2def global absolute 85.0 1.0 0.0 0.0")  # 7, 8, 9
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu10mw_only_blade_low_max_iter(write_dtu10mw_only_blade_low_max_iter):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_low_max_iter.htc"
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu10mw_only_blade_1_body(write_dtu10mw_only_blade_1_body):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_1_body.htc"
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_blade_rotate_base(write_dtu10mw_only_blade_rotate_base):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_rotate_base.htc"
    h2.add_sensor("mbdy forcevec blade1 1 1 blade1")  # 1, 2, 3
    h2.add_sensor("mbdy momentvec blade1 1 1 blade1")  # 4, 5, 6
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_blade_rotate_relative(
    write_dtu10mw_only_blade_rotate_relative,
):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_rotate_relative.htc"
    h2.add_sensor("mbdy forcevec blade1 1 1 blade1")  # 1, 2, 3
    h2.add_sensor("mbdy momentvec blade1 1 1 blade1")  # 4, 5, 6
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_blade_rotate_bearing3(
    write_dtu10mw_only_blade_rotate_bearing3,
):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_rotate_bearing3.htc"
    h2.add_sensor("mbdy forcevec blade1 1 1 blade1")  # 1, 2, 3
    h2.add_sensor("mbdy momentvec blade1 1 1 blade1")  # 4, 5, 6
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu_10mw_only_blade_uniform_node_distribution(
    write_dtu10mw_only_blade_uniform_node_distribution,
):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_uniform_node_distribution.htc"
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu10mw_only_blade_high_gravity(write_dtu10mw_only_blade_high_gravity):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_high_gravity.htc"
    h2.add_sensor("mbdy statevec_new blade1 c2def global absolute 90.0 1.0 0.0 0.0")  # 1-6
    h2.add_sensor("mbdy forcevec blade1 1 1 blade1")  # 7, 8, 9
    h2.add_sensor("mbdy momentvec blade1 1 1 blade1")  # 10, 11, 12
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu10mw_only_blade_high_gravity_deformed(write_dtu10mw_only_blade_high_gravity_deformed):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_high_gravity_deformed.htc"
    h2.add_sensor("mbdy statevec_new blade1 c2def global absolute 90.0 1.0 0.0 0.0")  # 1-6
    h2.add_sensor("mbdy forcevec blade1 1 1 blade1")  # 7, 8, 9
    h2.add_sensor("mbdy momentvec blade1 1 1 blade1")  # 10, 11, 12
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()


@pytest.fixture(scope="session")
def h2_dtu10mw_only_blade_high_gravity_1_body(write_dtu10mw_only_blade_high_gravity_1_body):
    h2 = H2Lib(suppress_output=True)
    model_path = f"{tfp}DTU_10_MW/"
    htc_path = "htc/DTU_10MW_RWT_only_blade_high_gravity_1_body.htc"
    h2.add_sensor("mbdy statevec_new blade1 c2def global absolute 90.0 1.0 0.0 0.0")
    h2.init(htc_path=htc_path, model_path=model_path)
    h2.stop_on_error(False)
    yield h2
    h2.close()
