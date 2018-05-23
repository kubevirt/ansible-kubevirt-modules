import pytest


@pytest.fixture(scope="module")
def args_present():
    """ yield basic argument_spec for state present """
    args = dict(
        state='present', kind='VirtualMachine', name='testvm', namespace='vms')
    yield args
    del args


@pytest.fixture(scope="module")
def args_absent():
    """ yield basic argument_spec for state absent """
    args = dict(
        state='absent', kind='VirtualMachine', name='testvm', namespace='vms')
    yield args
    del args


def pytest_configure(config):
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys
    del sys._called_from_test
