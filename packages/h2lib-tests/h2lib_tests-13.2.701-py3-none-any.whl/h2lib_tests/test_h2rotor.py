import os
from h2lib._h2lib import H2Lib, MultiH2Lib, H2LibThread

from numpy import testing as npt
import pytest
from wetb.gtsdf import gtsdf

from h2lib_tests.dtu10mw import DTU10MW, DTU10MWRotor, DTU10MWSimple
from h2lib_tests.test_files import tfp
import matplotlib.pyplot as plt
import numpy as np
from wetb.hawc2.at_time_file import AtTimeFile
import h5py


def get_h2(htc_path='htc/DTU_10MW_RWT.htc'):
    h2 = H2Lib(suppress_output=1)
    h2.read_input(htc_path=htc_path, model_path=tfp + 'DTU_10_MW')
    return h2


@pytest.fixture(scope='module')
def h2():
    h2 = get_h2()
    h2.init()
    h2.step()
    yield h2
    h2.close()


def test_get_nxxx(h2):
    assert h2.get_rotor_dims() == [[50, 50, 50]]


def test_get_bem_grid_dim(h2):
    assert h2.get_bem_grid_dim() == [16, 50]


def test_get_bem_grid(h2):
    azi, rad = h2.get_bem_grid()

    npt.assert_array_almost_equal(np.roll(np.linspace(-np.pi, np.pi, 17)[1:], 9), azi)
    npt.assert_array_almost_equal([3.09929662, 11.4350243, 33.76886193, 60.8641887, 82.01217305], rad[::10], 4)


def test_mainbody_names(h2: H2LibThread):
    assert h2.get_mainbody_name_dict() == {'tower': 1, 'towertop': 2, 'shaft': 3, 'hub1': 4, 'hub2': 5, 'hub3': 6,
                                           'blade1': 7, 'blade2': 8, 'blade3': 9}


def test_get_mainbody_position_orientation(h2: H2LibThread):
    mainbody_coo_nr = 0
    mb_dict = h2.get_mainbody_name_dict()
    if 0:
        ax = plt.figure().add_subplot(projection='3d')
        for name, mainbody_nr in mb_dict.items():
            pos, ori = h2.get_mainbody_position_orientation(mainbody_nr, mainbody_coo_nr)
            ax.plot(*pos, 'o', label=name)
            for (exyz), c in zip(ori, 'rgb'):
                ax.plot(*np.array([pos, pos + exyz * 10]).T, color=c)
        plt.axis('equal')
        plt.legend()
        plt.show()

    pos, ori = h2.get_mainbody_position_orientation(mb_dict['blade2'], 0)
    npt.assert_array_almost_equal(pos, [2.42817657, -7.31388712, -117.62523996], 6)
    npt.assert_array_almost_equal(ori, [[0.49826649, 0.03782549, 0.86619844],
                                        [0.07555272, 0.99335333, -0.08683861],
                                        [-0.86372582, 0.10871241, 0.49209686]], 6)

    pos, ori = h2.get_mainbody_position_orientation(mb_dict['hub2'], 0)
    npt.assert_array_almost_equal(pos, [-2.42631565e-09, -7.07298239e+00, -1.18998544e+02], 6)
    npt.assert_array_almost_equal(ori, [[0.49826698, 0.03781904, 0.86619844],
                                        [0.07556557, 0.99335236, -0.0868386],
                                        [-0.86372441, 0.10872359, 0.49209687]], 6)


def test_induction(h2):
    h2.suppress_output = False
    azi, rad = h2.get_bem_grid()
    induc_grid = h2.get_induction_polargrid()
    induc_axisymmetric = h2.get_induction_axisymmetric()
    induc_rotoravg = h2.get_induction_rotoravg()
    if 0:
        Azi, Rad = np.meshgrid(azi, rad)
        ax = plt.gcf().add_subplot(111, polar=True)
        ax.set_theta_zero_location('S')
        ax.set_theta_direction(-1)
        cntf = ax.contourf(Azi, Rad, induc_grid.T, 50)
        plt.colorbar(cntf)
        plt.figure()
        plt.plot(rad, induc_axisymmetric)
        plt.axhline(induc_rotoravg, color='k')
        plt.show()

    npt.assert_array_almost_equal(np.mean(induc_grid, 0), induc_axisymmetric)
    npt.assert_array_almost_equal(np.sum(np.r_[0, np.diff(rad / rad[-1])] * induc_axisymmetric), induc_rotoravg, 3)


def test_rotor_orientation_multi_instance():
    dtu10 = DTU10MW()
    dtu10.simulation.visualization = 'visu', .5, 1.5
    dtu10.output.buffer = 1
    dtu10.output.data_format = 'gtsdf64'
    dtu10.set_name('tmp_5_0')
    dtu10.save()

    tilt_ref, yaw_ref = 6, 10
    dtu10.set_tilt_cone_yaw(tilt=tilt_ref, cone=0, yaw=yaw_ref)
    dtu10.set_name('tmp_6_10')
    dtu10.save()
    with MultiH2Lib(2, suppress_output=1) as mh2:
        mh2.read_input(['htc/tmp_5_0.htc', 'htc/tmp_6_10.htc'], model_path=tfp + "DTU_10_MW")
        # h2.suppress_output = False
        s_id = mh2.add_sensor('aero power')[0]
        mh2.init()
        yaw, tilt, _ = zip(*mh2.get_rotor_orientation())
        np.testing.assert_almost_equal(np.rad2deg(yaw), [0, 10])
        np.testing.assert_almost_equal(np.rad2deg(tilt), [5, 6])
        yaw, tilt, _ = zip(*mh2.get_rotor_orientation(deg=True))
        np.testing.assert_almost_equal(yaw, [0, 10])
        np.testing.assert_almost_equal(tilt, [5, 6])
        h2 = mh2[0]
        res = []
        for t in np.arange(0, 2.5, .01):
            h2.run(t)
            res.append([h2.get_rotor_orientation(deg=True)[0][2], h2.get_sensor_values(s_id)[0][0]] +
                       h2.get_rotor_position()[0].tolist())

        data = gtsdf.load(h2.model_path[0] + '/res/tmp_5_0.hdf5')[1]
        res = np.array(res)
        npt.assert_allclose(data[:, 0], res[1:-1, 0] % 360 - 180, rtol=0.002)  # azi
        npt.assert_array_almost_equal(data[:, 10], res[1:-1, 1])  # power
        npt.assert_array_almost_equal(data[:, 15:18], res[1:-1, 2:5])  # rotor position
        assert os.path.isfile(mh2.model_path[0] + '/visualization/tmp_5_0.hdf5')

        with h5py.File(mh2.model_path[0] + '/visualization/tmp_5_0.hdf5') as f:
            assert f.attrs['time_start'][0] == 0.5
            assert f.attrs['time_stop'][0] == 1.5
        assert os.path.isfile(mh2.model_path[1] + '/visualization/tmp_6_10.hdf5')


def test_rotor_avg_windspeed():
    h2 = get_h2()
    h2.init_windfield(Nxyz=(2, 2, 2), dxyz=(200, 200, 200), box_offset_yz=(-100, -19), transport_speed=6)
    h2.init()
    u = np.zeros((2, 2, 2))
    u[:, 1, :] = 10  # 0 in one side, 10 in other, 5 in avg
    h2.set_windfield(np.asfortranarray([u, u * 0, u * 0]), -100)
    h2.step()
    npt.assert_almost_equal(h2.get_rotor_avg_wsp(1), [0, 5, 0])
    npt.assert_almost_equal(h2.get_rotor_avg_uvw(), [5, 0, 0])

    h2.close()


def test_aerosections():
    plot = 0
    h2 = get_h2(htc_path='htc/DTU_10MW_RWT_no_aerodrag.htc')
    # blade 1, global coo, r>30
    pos_ids = [h2.add_sensor(f'aero position 3 1 {xyz} 30')[0] for xyz in [1, 2, 3]]
    wsp_ids = [h2.add_sensor(f'aero windspeed 3 1 {xyz} 30')[0] for xyz in [1, 2, 3]]
    frc_ids = [h2.add_sensor(f'aero secforce 1 {xyz} 30 3')[0] for xyz in [1, 2, 3]]
    mom_ids = [h2.add_sensor(f'aero secmoment 1 {xyz} 30 3')[0] for xyz in [1, 2, 3]]
    h2.init_AL(epsilon_smearing=5)

    a = h2.get_aerosections_position()
    if plot:
        ax = plt.figure().add_subplot(projection='3d')
        for b in a:
            ax.plot(*b.T)
        plt.show()

    assert a.shape == (3, 50, 3)

    r = np.sqrt(np.sum((a[0, :] - a[0, 0])**2, 1))
    i = np.searchsorted(r, 30)

    h2.step()
    name, unit, desc = h2.get_sensor_info(pos_ids[-1])
    assert str(np.round(r[i], 2)) in desc
    assert str(np.round(r[i], 1)) in name
    assert unit == 'm'

    a = h2.get_aerosections_position()
    npt.assert_array_almost_equal(a[0, i], [h2.get_sensor_values(id) for id in pos_ids])
    uvw = a * 0
    uvw[:, :, 0] = 6
    h2.set_aerosections_windspeed(uvw)
    h2.run(3)
    npt.assert_array_equal(h2.get_sensor_values(wsp_ids), [0, 6, 0])
    npt.assert_array_almost_equal(h2.get_sensor_values(frc_ids), h2.get_aerosections_forces()[0, i] / 1000)

    frc_before = h2.get_aerosections_forces()

    if plot:
        plt.figure()
        plt.plot(frc_before[:, :, 1].T)

    # rotor avg freestream wsp unknown after init_AD
    npt.assert_array_equal(h2.get_rotor_avg_wsp(), [np.nan, np.nan, np.nan])
    uvw[0, i, 0] = 12
    h2.set_aerosections_windspeed(uvw)

    h2.step()
    frc_after = h2.get_aerosections_forces()
    mom_after = h2.get_aerosections_moments()
    if plot:
        plt.plot(frc_after[:, :, 1].T, '--')
        plt.show()

    # Fy in section with u=12 instead of u=6m/s more than doubled
    assert frc_before[0, i, 1] * 2 < frc_after[0, i, 1]

    # rest is similar (within 7N/m, max Fxyz along blade is [331 , 378, 288]
    frc_after[0, i, :] = frc_before[0, i, :]  # reset frc at 30m to previous value. Now everything is similar
    npt.assert_allclose(frc_before, frc_after, atol=7)
    h2.close()


def test_compare_aerosection_coupling():
    """Compare simulations with 1) htc wind and 2) similar wind set to aerodynamic sections

    - yaw=20, tilt=10, cone=5
    - two blades (to check that xyz/uvw are not mixed up with number of blades)
    - stiff structure, fixed rotor speed and pitch
    - linear shear and no turb
    - aero_calc=1, induction=0, tiploss=0, dynstall=2
    - aerodrag turned off (requires wind speed at aerodrag sections, not implemented yet)
    """
    dtu10 = DTU10MWSimple(rotor_speed=.6, pitch=0, nbodies=1)
    dtu10.set_stiff()

    dtu10.set_wind(8, tint=0, turb_format=0, shear=(4, .01))
    dtu10.set_tilt_cone_yaw(tilt=10, cone=5, yaw=20)
    # remove third blade
    dtu10.aero.nblades = 2
    dtu10.aero.link__3.delete()

    dtu10.aerodrag.delete()

    T = 20
    dtu10.set_time(0, T)
    dtu10.set_aero(aero_calc=1, induction=0, tiploss=0, dynstall=2)

    for coo in [3, 4]:
        for xyz in [1, 2, 3]:
            dtu10.output.add_sensor('aero', 'windspeed', [coo, 1, xyz, 72, 1])
    for coo in [3]:
        for xyz in [1, 2, 3]:
            dtu10.output.add_sensor('aero', 'position', [coo, 1, xyz, 72, 1])

    # At time sensors
    at = dtu10.add_section(f'output_at_time aero {T}')
    at.filename = "tmp1_at"
    for sensor in ['vrel', 'alfa', 'alfadot', 'cl', 'cd', 'cm', 'lift', 'drag', 'moment', 'ct_local', 'cq_local', 'tiploss_f',
                   'chord', 'inflow_angle', 'dcldalfa', 'dcddalfa', 'twist']:
        at.add_sensor('', sensor, [1])

    for sensor in ['inipos']:
        for xyz in [1, 2, 3]:
            at.add_sensor('', sensor, [1, xyz])
    for sensor in ['secforce', 'secmoment', 'int_moment', 'int_force', 'position', 'velocity', 'acceleration', 'induc',
                   'windspeed']:
        for coo in [1, 2, 3, 4]:
            for xyz in [1, 2, 3]:
                at.add_sensor('', sensor, [1, xyz, coo])

    dtu10.set_name('tmp1')
    dtu10.save()
    with H2Lib(suppress_output=1) as h2:
        h2.init(dtu10.filename, dtu10.modelpath)
        h2.run(T)

    dtu10.wind.wsp = 20  # ensure htc wind speed is different and induction is large in case it by mistake is not turned off
    at.filename = "tmp2_at"
    dtu10.set_name('tmp2')
    dtu10.save()

    with H2Lib(suppress_output=1) as h2:
        h2.init_AD(htc_path=dtu10.filename, model_path=dtu10.modelpath, tiploss_method=0)
        last_pos_gl_xyz = np.array(h2.get_aerosections_position(), order='F')
        while h2.time < T:
            pos_gl_xyz = np.array(h2.get_aerosections_position(), order='F')
            uvw = np.asfortranarray(pos_gl_xyz * 0)
            dpos_gl_xyz = (pos_gl_xyz - last_pos_gl_xyz)
            next_pos_gl_xyz = pos_gl_xyz + dpos_gl_xyz
            uvw[:, :, 0] = (-next_pos_gl_xyz[:, :, 2] - 119) * .01 + 8
            last_pos_gl_xyz = pos_gl_xyz.copy()
            h2.set_aerosections_windspeed(uvw)
            h2.step()

    time, data1, info = gtsdf.load(tfp + 'DTU_10_MW/res/tmp1.hdf5')
    time, data2, info = gtsdf.load(tfp + 'DTU_10_MW/res/tmp2.hdf5')
    # exclude first time step where position extrapolation is not active
    for n, c1, c2 in zip(info['attribute_names'], data1[1:].T, data2[1:].T):
        if n not in ['WSP gl. coo.,Vx', 'WSP gl. coo.,Vy', 'WSP gl. coo.,Vz']:  # nan
            max_rel_err = np.abs(c2 - c1).max() / np.maximum(np.abs(c2).max(), 1)
            try:
                assert max_rel_err < 0.00001, n
            except BaseException:
                if 0:
                    plt.title(n)
                    plt.plot(c1)
                    plt.plot(c2)
                    plt.plot((c1 - c2))
                    plt.show()
                raise

    at1 = AtTimeFile(tfp + 'DTU_10_MW/tmp1_at.dat')
    at2 = AtTimeFile(tfp + 'DTU_10_MW/tmp2_at.dat')
    for n, c1, c2 in zip(at1.attribute_names, at1.data.T, at2.data.T):
        npt.assert_allclose(c2, c1, atol=1e-6, rtol=0.0001, err_msg=n)
        try:
            assert max_rel_err < 0.00001, n
        except BaseException:
            if 1:
                plt.title(n)
                plt.plot(c1)
                plt.plot(c2)
                plt.plot(c1 - c2)
                plt.show()
            raise


def test_iea15MW():
    with H2Lib(suppress_output=True) as h2:
        h2.read_input(htc_path='htc/IEA_15MW_RWT_Onshore.htc', model_path=tfp + 'IEA-15-240-RWT-Onshore')
        h2.init()
        h2.step()
        npt.assert_allclose(h2.get_diameter(), 240.806, atol=0.001)
