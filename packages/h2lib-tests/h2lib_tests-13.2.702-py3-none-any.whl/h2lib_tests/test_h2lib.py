from wetb.gtsdf import gtsdf
import matplotlib.pyplot as plt
import numpy as np
from numpy import newaxis as na
import pytest
from h2lib._h2lib import H2Lib, MultiH2Lib
from numpy import testing as npt
from h2lib_tests.test_files import tfp
from wetb.hawc2.htc_file import HTCFile
import time
from tqdm import tqdm
import sys
import os
import h2lib
import re


def test_version():
    with H2Lib(False) as h2:
        h2.echo_version()
        v = h2.get_version()
        if sys.version_info >= (3, 8) and 'site-packages' in h2lib.__file__:
            from importlib.metadata import version
            assert v.strip().replace(".", '-').replace('+', '-') == version('h2lib').replace(".", '-').replace('+', '-')


def test_extern_write_log():
    with H2Lib(False) as h2:
        s = "hello world"
        h2.extern_write_log(s, len(s), "python", False, False)


def test_sensors():
    with H2Lib() as h2:
        model_path = tfp + "minimal/"
        htc = HTCFile(model_path + 'htc/minimal.htc')
        htc.output.add_sensor("general", 'variable', [1, 5, 'mysensor1', 'myunit1', 'mydesc1'])
        htc.output.add_sensor("wind", 'free_wind', [1, 5, 0, -119])
        htc.wind.shear_format = 1, 0

        htc.set_name('tmp')
        htc.save()
        h2.init('htc/tmp.htc', model_path)
        s = " " * 1024
        assert h2.get_filename(s)[0][0].strip() == 'htc/tmp.htc'
        i1 = h2.add_sensor('wind free_wind 1 0 0 -119;')  # adds three sensors
        assert i1 == (1, 2, 3)
        i2 = h2.add_sensor('general step 0.5 1 2;')
        assert i2 == (4,)
        i3 = h2.add_sensor('general variable 1 5 # $name(myname2) $unit(myunit2) $desc(mydesc2);')
        assert i3 == (5,)
        t = h2.step()
        assert h2.get_sensor_info(1) == ['WSP gl. coo.,Vx', 'm/s',
                                         'Free wind speed Vx, gl. coo, of gl. pos    0.00,   0.00,-119.00']
        assert h2.get_sensor_info(2) == ['WSP gl. coo.,Vy', 'm/s',
                                         'Free wind speed Vy, gl. coo, of gl. pos    0.00,   0.00,-119.00']
        assert h2.get_sensor_info(3) == ['WSP gl. coo.,Vz', 'm/s',
                                         'Free wind speed Vz, gl. coo, of gl. pos    0.00,   0.00,-119.00']
        assert [n for n, u, d in h2.get_sensor_info(i1)] == ['WSP gl. coo.,Vx', 'WSP gl. coo.,Vy', 'WSP gl. coo.,Vz']
        assert h2.get_sensor_info(4) == ['Step', '-', 'Step value']
        assert h2.get_sensor_info(5) == ['myname2', 'myunit2', 'mydesc2'], h2.get_sensor_info(5)

        r = []
        for _ in range(10):
            r.append([t, h2.get_sensor_values(4), h2.get_sensor_values(5)] + h2.get_sensor_values(i1).tolist())
            if t == 0.6:
                h2.set_variable_sensor_value(1, 2)
            t = h2.step()
        r = np.array(r)
        npt.assert_array_equal(r[:, 1], np.where(r[:, 0] <= .5, 1, 2))
        npt.assert_array_equal(r[:, 2], np.where(r[:, 0] >= .7, 2, 5.))
        time, data, _ = gtsdf.load(h2.model_path + 'res/tmp.hdf5')
        npt.assert_array_equal(data[:, 0], np.where(time >= .7, 2, 5.))
        npt.assert_array_equal(data[:, 1:4], r[:, 3:6])


@pytest.mark.parametrize('time_stop', [1, 10])
def test_write_output(time_stop):

    model_path = tfp + "minimal/"
    if os.path.isfile(model_path + 'res/tmp.hdf5'):
        os.remove(model_path + 'res/tmp.hdf5')
    with H2Lib() as h2:
        htc = HTCFile(model_path + 'htc/minimal.htc')
        htc.simulation.time_stop = time_stop
        htc.output.buffer = 1000
        htc.output.add_sensor('general', 'step', [0.9, 1, 2])
        htc.output.add_sensor('general', 'step', [1, 1, 2])
        htc.set_name('tmp')
        htc.save()
        h2.init('htc/tmp.htc', model_path)
        h2.run(1)

    time, data, _ = gtsdf.load(model_path + 'res/tmp.hdf5')
    assert data.shape == (10, 2)
    npt.assert_array_equal(time, np.arange(.1, 1.1, .1))
    if 0:
        plt.plot(time, data)
        plt.show()


def test_set_windspeed_uvw():
    with H2Lib() as h2:
        pos = [0, 0, -119]
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        Nxyz = [8, 4, 2]
        h2.init()
        h2.init_windfield(Nxyz, dxyz=[1., 1, 1], box_offset_yz=[0., -119], transport_speed=5)
        u, v, w = 1, 2, 3
        uvw = np.asfortranarray(np.zeros([3] + Nxyz) + np.array([u, v, w])[:, na, na, na])
        h2.set_windfield(uvw, 0)
        vx, vy, vz = h2.get_wind_speed(pos)
        assert vx == v
        assert vy == u
        assert vz == -w
        npt.assert_array_equal([u, v, w], h2.get_uvw(pos))


def test_set_windspeed_interpolation():
    with H2Lib() as h2:
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        Nxyz = np.array([8, 4, 2])
        h2.init()
        h2.init_windfield(Nxyz, dxyz=[2., 3, 4], box_offset_yz=[-4.5, 117], transport_speed=5)
        uvw = np.asfortranarray(np.meshgrid(np.arange(Nxyz[0]) + 100, np.arange(Nxyz[1]) + 200, np.arange(Nxyz[2]) + 300,
                                            indexing='ij'))
        h2.set_windfield(uvw, 0)

        # test u
        y = np.linspace(0, 14, 10)
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1] for y_ in y], np.linspace(100, 107, 10))

        h2.set_windfield(uvw, -5.)
        # box moved -6m offset
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1]
                                             for y_ in y - 5], np.linspace(100, 107, 10))

        h2.run(3)
        # box moved 3s * 5m/s - 5m offset = 10
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1]
                                             for y_ in y + 10], np.linspace(100, 107, 10))

        h2.set_windfield(uvw, -5.)
        # box moved 6m offset
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, y_, 0])[1]
                                             for y_ in y - 5], np.linspace(100, 107, 10))

        # test v
        x = np.linspace(-4.5, 4.5, 10)
        np.testing.assert_array_almost_equal([h2.get_wind_speed([x_, 0, 0])[0] for x_ in x], np.linspace(200, 203, 10))

        # test w
        z = np.linspace(-117, -121, 10)
        np.testing.assert_array_almost_equal([h2.get_wind_speed([0, 0, z_])[2] for z_ in z], -np.linspace(300, 301, 10))


def test_mann_turb():
    with H2Lib() as h2:
        U = 5
        from hipersim import MannTurbulenceField
        mtf = MannTurbulenceField.from_hawc2(filenames=[tfp + f'minimal/turb/hawc2_mann_l33.6_ae0.1000_g3.9_h0_512xd32xd16_2.000x3.00x4.00_s0001_{uvw}' for uvw in 'uvw'],
                                             alphaepsilon=.1, L=33.6, Gamma=3.9,
                                             Nxyz=(512, 32, 16), dxyz=(2, 3, 4), seed=1, HighFreqComp=0)
        mtf.uvw = np.asfortranarray(mtf.uvw)
        time, data, _ = gtsdf.load(tfp + 'minimal/res/minimal_mann_turb.hdf5')
        time, data = time[:100], data[:100]
        vx, vy, vz = data.T
        h2_uvw = [vy, vx, -vz]
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        h2.init_windfield(Nxyz=mtf.Nxyz, dxyz=mtf.dxyz, box_offset_yz=[0, 0], transport_speed=5)
        h2.init()
        h2.set_windfield(uvw=mtf.uvw.astype(np.float64), box_offset_x=-(mtf.Nx - 1) * mtf.dx)
        h2l_vxyz = []
        for t in tqdm(time, disable=0):
            h2.run(t)
            h2l_vxyz.append(h2.get_wind_speed([0, 0, 0]))
        npt.assert_almost_equal(t, h2.get_time())
        vx, vy, vz = np.array(h2l_vxyz).T
        h2l_uvw = [vy, vx, -vz]

        x = (mtf.Nx * mtf.dx) - U * time - 2
        mtf_uvw = mtf(x, x * 0, x * 0).T

        if 0:
            plt.plot(time, h2_uvw[0], label='h2')
            plt.plot(time, mtf_uvw[0], label='mtf')
            plt.plot(time, h2l_uvw[0], label='h2l')
            plt.legend()
            plt.show()

        npt.assert_array_almost_equal(mtf_uvw, h2_uvw)
        npt.assert_array_almost_equal(mtf_uvw, h2l_uvw)


def test_mann_turb_small_buffer():
    with H2Lib() as h2:
        from hipersim import MannTurbulenceField
        U = 5
        mtf = MannTurbulenceField.from_hawc2(filenames=[tfp + f'minimal/turb/hawc2_mann_l33.6_ae0.1000_g3.9_h0_512xd32xd16_2.000x3.00x4.00_s0001_{uvw}' for uvw in 'uvw'],
                                             alphaepsilon=.1, L=33.6, Gamma=3.9,
                                             Nxyz=(512, 32, 16), dxyz=(2, 3, 4), seed=1, HighFreqComp=0)
        mtf.uvw = np.asfortranarray(mtf.uvw)
        time, data, _ = gtsdf.load(tfp + 'minimal/res/minimal_mann_turb.hdf5')
        time, data = time[:200], data[:200]
        vx, vy, vz = data.T
        h2_uvw = [vy, vx, -vz]
        model_path = tfp + "minimal/"
        h2.read_input('htc/minimal.htc', model_path)
        h2.init_windfield(Nxyz=(128, 32, 16), dxyz=mtf.dxyz, box_offset_yz=[0, 0], transport_speed=5)
        h2.init()
        h2l_vxyz = []
        h2.set_windfield(uvw=mtf.uvw[:, -128:].astype(np.float64), box_offset_x=-(mtf.Nx - 1) * mtf.dx)
        for t in tqdm(time):
            t = np.round(t, 6)
            h2.run(t)
            if t % 10 == 0:
                i = int(512 - 128 - t * U / 2)
                h2.set_windfield(uvw=mtf.uvw[:, i:i + 128].astype(np.float64), box_offset_x=-(mtf.Nx - 1) * mtf.dx)
            h2l_vxyz.append(h2.get_wind_speed([0, 0, 0]))
        vx, vy, vz = np.array(h2l_vxyz).T
        h2l_uvw = [vy, vx, -vz]

        x = ((mtf.Nx - 1) * mtf.dx) - U * time
        mtf_uvw = mtf(x, x * 0, x * 0).T

        if 0:
            plt.plot(time, h2_uvw[0], '-', label='h2')
            plt.plot(time, mtf_uvw[0], '--', label='mtf')
            plt.plot(time, h2l_uvw[0], '-', label='h2l')
            plt.legend()
            plt.show()

        npt.assert_array_almost_equal(mtf_uvw, h2_uvw)
        npt.assert_array_almost_equal(mtf_uvw, h2l_uvw)


def test_context_manager():
    if os.name == 'nt':
        with H2Lib(subprocess=False) as h2:
            h2.get_version()


def test_parallel():
    N = 3
    mh2 = MultiH2Lib(N)
    assert mh2.getState() == [0, 0, 0]
    mh2.setState([4, 5, 6])
    assert mh2.getState() == [4, 5, 6]
    mh2.close()


def test_parallel_context_manager():
    N = 3
    with MultiH2Lib(N) as mh2:
        model_path = tfp + "minimal/"
        mh2.read_input('htc/minimal.htc', model_path)
        npt.assert_array_equal(mh2.model_path, [model_path] * 3)
        mh2.init_windfield(Nxyz=(128, 32, 16), dxyz=[(1, 2, 3), (4, 5, 6), (7, 8, 9)],
                           box_offset_yz=[0, 0], transport_speed=5)
        assert mh2.getState() == [0, 0, 0]
        mh2.setState([4, 5, 6])
        assert mh2.getState() == [4, 5, 6]
        mh2[0].setState(10)
        assert mh2.getState() == [10, 5, 6]
        mh2.work(.1)

        N_0 = mh2[0].work(1)[0]  # reference iterations for 1 wt
        N_all = np.array(mh2.work(1.))
        slow_down = (N_0 - N_all) / N_0
        print(np.all(slow_down < 0.2), (N_0, N_all, slow_down))

        t_0 = mh2[0].loop(N_0)[0]
        t_all = np.array(mh2.loop(N_0))
        slow_down = (t_all - t_0) / t_0
        print(np.all(slow_down < 0.2), (t_0, t_all, slow_down))

        subset = mh2[:2]
        cls_name = subset.__class__.__name__
        with pytest.raises(Exception, match=f'Cannot close {cls_name}. Please close all instances at once'):
            subset.close()

        with pytest.raises(Exception, match=f'Cannot make subset of {cls_name}'):
            subset[1]

        # all of subset is ok
        assert subset[:].getState() == [10, 5]
        assert mh2[:3] == mh2


def test_process_died():
    h2 = H2Lib()
    h2.inputQueue.put(('close', [], {}))
    h2.outputQueue.get()  # None from close method
    h2.outputQueue.get()  # "Exit process"
    with pytest.raises(Exception, match="H2LibThread process died before or while checking if 'echo_version' is callable"):
        for _ in range(10):
            time.sleep(1)
            h2.echo_version()


def test_error(capfd):
    model_path = tfp + "minimal/"
    htc = HTCFile(model_path + 'htc/minimal_mann_turb.htc')
    htc.wind.scale_time_start = 200
    htc.wind.turb_format = 1
    htc.wind.mann.dont_scale = 0
    htc.set_name('tmp')
    htc.save()

    with H2Lib(suppress_output=0) as h2:
        version = h2.get_version()
        with pytest.raises(Exception, match='Turbulence scale_time_start >= simulation length'):
            h2.init('htc/tmp.htc', model_path)
        out, err = capfd.readouterr()
        assert "*** ERROR *** Turbulence scale_time_start >= simulation length" in out
        assert h2.get_version() == version  # hawc2 still alive
    with pytest.raises(ValueError):
        h2.get_version()  # now it is closed

    with MultiH2Lib(2) as h2:
        version = h2.get_version()
        with pytest.raises(Exception, match='Turbulence scale_time_start >= simulation length'):
            h2.init('htc/tmp.htc', model_path)
        assert h2.get_version() == version  # hawc2 still alive


def test_fail():
    with H2Lib() as h2:
        version = h2.get_version()
        with pytest.raises(Exception, match='MyError'):
            h2.fail('MyError')
        assert h2.get_version() == version  # hawc2 still alive
        stop_code = 0

        # cover get_stop_code, get_stop_message and reset_stop_code_and_message, but
        # reset_stop_code_and_message is already called, so stop_code and stop_message are 0 and ""
        assert h2.get_stop_code(stop_code)[0][0] == 0
        stop_msg = " " * 1024
        assert h2.get_stop_message(stop_msg)[0][0].strip() == ''
        h2.reset_stop_code_and_message()

    with MultiH2Lib(2) as h2:
        # , match=re.escape('H2LibThread process died before or while executing fail(...)')):
        with pytest.raises(Exception, match='MyError'):
            h2.fail('MyError')
