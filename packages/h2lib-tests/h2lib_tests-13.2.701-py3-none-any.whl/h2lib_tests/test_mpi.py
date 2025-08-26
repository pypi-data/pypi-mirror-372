import os
import sys
import time
import traceback

from h2lib_tests.test_files import tfp
from numpy import testing as npt
import pytest
from wetb.hawc2.htc_file import HTCFile

import h2lib
from h2lib._h2lib import H2LibProcess, MultiH2Lib, set_LD_LIBRARY_PATH
from h2lib_tests.test_files.my_test_cls import MyTest
from multiclass_interface import mpi_interface
from multiclass_interface.mpi_interface import MPIClassInterface
from multiclass_interface.multiprocess_interface import ProcessClass, MultiProcessClassInterface
import numpy as np
import shutil


set_LD_LIBRARY_PATH

mpi_available = shutil.which('mpirun') is not None


def mpirun(f):
    if 'string' in traceback.format_stack()[0]:
        return f
    else:
        n = f.__name__

        def wrap():
            if mpi_available:
                exe = sys.executable.replace("\\", "/")
                allow_run_as_root = ["", "--allow-run-as-root"]['MPIRUN_RUN_AS_ROOT' in os.environ]
                cmd = f'''mpirun -n 4 {allow_run_as_root} {exe} -c "from h2lib_tests.test_mpi import {n}; {n}()"'''
                # print(cmd)
                assert os.system(cmd) == 0, n
            else:
                pytest.xfail('mpirun not available')
        wrap.__name__ = n
        return wrap


@mpirun
def test_mpi_MyTest():
    mpi_interface.activate_mpi()
    N = 4
    try:
        with MPIClassInterface(MyTest, [(i,) for i in range(N)]) as m:

            time.sleep(.1)
            i = m.get_id()
            npt.assert_array_equal(i, np.arange(N))

            npt.assert_array_equal(m[1:3].get_id(), np.arange(1, 3))
            t = time.time()
            m.work(1)
            t = time.time() - t
            assert t < 1.1

            with pytest.raises(Exception, match='Cannot close SubsetMPIClassInterface. Please close all instances at once'):
                m[:3].close()
            with pytest.raises(Exception, match='Cannot make subset of SubsetMPIClassInterface'):
                m[:3][1]

    except ChildProcessError:
        pass


@mpirun
def test_mpi_ProcessClass():
    mpi_interface.activate_mpi()

    with ProcessClass(MyTest) as cls:
        myTest = cls(1)
        assert myTest.get_id() == 1


@mpirun
def test_mpi_H2LibProcess():
    mpi_interface.activate_mpi()
    with H2LibProcess(suppress_output=False) as h2:
        assert h2lib.__version__.replace("+", "-").startswith(h2.get_version().strip()
                                                              ), (h2.get_version().strip(), h2lib.__version__)


@mpirun
def test_MultiH2Lib():
    mpi_interface.activate_mpi()
    with MultiH2Lib(3, suppress_output=1) as mh2:
        assert all([h2lib.__version__.replace("+", "-").startswith(v.strip()) for v in mh2.get_version()])
        assert len(mh2.get_version()) == 3
        if mpi_interface.size > 1:
            assert isinstance(mh2, mpi_interface.MPIClassInterface)
            _file__ = np.__file__
            if '/lib/' in _file__:
                lib_path = _file__[:_file__.index("/lib/") + 5]
            else:
                lib_path = "LibNotInLD_LIBRARY_PATH"
            if lib_path in os.environ.get('LD_LIBRARY_PATH', '') or os.path.relpath(
                    lib_path, os.getcwd()) in os.environ.get('LD_LIBRARY_PATH', ''):
                assert mh2.cls == H2LibThread, mh2.cls
            else:
                assert mh2.cls == H2LibProcess, mh2.cls
        else:
            assert isinstance(mh2, MultiProcessClassInterface)

        model_path = tfp + "minimal/"
        mh2.read_input('htc/minimal.htc', model_path)
        npt.assert_array_equal(mh2.model_path, [model_path] * 3)
        mh2.init_windfield(Nxyz=(128, 32, 16), dxyz=[(1, 2, 3), (4, 5, 6), (7, 8, 9)],
                           box_offset_yz=[0, 0], transport_speed=5)
        assert mh2.getState() == [0, 0, 0]
        mh2.setState([4, 5, 6])
        assert mh2.getState() == [4, 5, 6], mh2.getState()
        mh2[0].setState(10)
        assert mh2.getState() == [10, 5, 6]
        t = time.time()
        mh2.work(2)
        assert time.time() - t < 2.5
        with pytest.raises(Exception, match='Cannot close SubsetMPIClassInterface. Please close all instances at once'):
            mh2[:2].close()
        with pytest.raises(Exception, match='Cannot make subset of SubsetMPIClassInterface'):
            mh2[:2][1].getState()


def get_htc_lst(N=4):
    htc = HTCFile(tfp + 'DTU_10_MW/htc/DTU_10MW_RWT_no_aerodrag.htc')
    for i in range(N):
        htc.set_name(f'wt{i}')
        htc.save()
    return [f'htc/wt{i}.htc' for i in range(N)]


@mpirun
def test_ellipsys_mpi_dummy_workflow():
    mpi_interface.activate_mpi(collective_mpi=False)
    from h2lib_tests.test_ellipsys_couplings import Ellipsys
    from numpy import newaxis as na
    rank = mpi_interface.rank

    N = 4

    with MultiH2Lib(N, suppress_output=1) as h2:
        el = Ellipsys()
        h2.read_input(htc_path=get_htc_lst(),
                      model_path=tfp + 'DTU_10_MW')
        wt_pos = np.array([[0, 0, 0], [0, 500, 0], [0, 1000, 0], [0, 1500, 0]])
        h2.init_AD()
        t = 0
        while True:
            t = el.step()
            h2.run(t)
            pos_gl_xyz = np.array(h2.get_aerosections_position(), order='F') + wt_pos[[rank], na, na, :]
            assert pos_gl_xyz.shape == (1, 3, 50, 3), pos_gl_xyz.shape  # 1(current wt), blades, aero_sections, xyz
            uvw = np.asfortranarray(el.get_uvw(pos_gl_xyz))
            h2.set_aerosections_windspeed(uvw)
            frc_gl_xyz = h2.get_aerosections_forces()
            assert np.shape(frc_gl_xyz) == (1, 3, 50, 3)
            el.set_fxyz(pos_gl_xyz, frc_gl_xyz)
            if t == 1:
                break


@mpirun
def test_ellipsys_mpi_dummy_workflow_collective():
    mpi_interface.activate_mpi()
    from h2lib_tests.test_ellipsys_couplings import Ellipsys
    from numpy import newaxis as na
    rank = mpi_interface.rank
    N = 4

    with MultiH2Lib(N, suppress_output=1) as h2:
        with h2.release_mpi_workers():
            el = Ellipsys()
            h2.read_input(htc_path=get_htc_lst(),
                          model_path=tfp + 'DTU_10_MW')
            wt_pos = np.array([[0, 0, 0], [0, 500, 0], [0, 1000, 0], [0, 1500, 0]])
            h2.init_AD()
            t = 0
            while True:
                t = el.step()
                h2.run(t)
                pos_gl_xyz = np.array(h2.get_aerosections_position(), order='F') + wt_pos[[rank], na, na, :]
                assert pos_gl_xyz.shape == (1, 3, 50, 3), pos_gl_xyz.shape  # 1(current wt), blades, aero_sections, xyz
                uvw = np.asfortranarray(el.get_uvw(pos_gl_xyz))
                h2.set_aerosections_windspeed(uvw)
                frc_gl_xyz = h2.get_aerosections_forces()
                assert np.shape(frc_gl_xyz) == (1, 3, 50, 3)
                el.set_fxyz(pos_gl_xyz, frc_gl_xyz)
                if t == 1:
                    break
