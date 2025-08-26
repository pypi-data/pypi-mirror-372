from numpy import testing as npt
import pytest

from multiclass_interface.multiprocess_interface import MultiProcessClassInterface
from h2lib_tests.test_files.my_test_cls import MyTest


@pytest.fixture(scope='module')
def mpri():
    return MultiProcessClassInterface(MyTest, [(1,), (2,)])


def test_attribute(mpri):
    npt.assert_array_equal(mpri.get_id(), [1, 2])
    npt.assert_array_equal(mpri.name, ["MyTest", "MyTest"])


def test_missing_attribute(mpri):
    with pytest.raises(AttributeError, match="'MyTest' object has no attribute 'missing'"):
        print(mpri.missing)


def test_execption(mpri):
    with pytest.raises(ZeroDivisionError, match="1 / 0  # raise ZeroDivisionError"):
        mpri.raise_exception()


def test_setattr(mpri):
    mpri.my_att = "new attribute"
    npt.assert_array_equal(mpri.my_att, ['new attribute'] * 2)


def get_process_id():
    import os
    return os.getpid()


def get_name(self):
    return self.name


def test_setattr_method(mpri):
    mpri.get_process_id = get_process_id
    main_id = get_process_id()
    pid1, pid2 = mpri.get_process_id()
    if isinstance(mpri, MultiProcessClassInterface):
        assert len({main_id, pid1, pid2}) == 3  # process ids should be unique
    else:
        # mpi, rank0 = main and first worker
        assert main_id == pid1
        assert pid1 != pid2

    mpri.get_name = get_name
    assert mpri.get_name() == mpri.name
