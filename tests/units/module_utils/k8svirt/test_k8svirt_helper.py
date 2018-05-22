import pytest
import sys

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')

import helper


def test_to_snake():
    assert helper.to_snake('VirtualMachine') == 'virtual_machine'
    assert helper.to_snake(
        'V1OfflineVirtualMachine') == 'v1_offline_virtual_machine'


def test_get_helper():
    client = dict()
    k8svirt_obj = helper.get_helper(client, 'virtual_machine')
    assert isinstance(k8svirt_obj, helper.VirtualMachineHelper)
    k8svirt_obj = helper.get_helper(client, 'offline_virtual_machine')
    assert isinstance(k8svirt_obj, helper.OfflineVirtualMachineHelper)
    k8svirt_obj = helper.get_helper(client, 'virtual_machine_replica_set')
    assert isinstance(k8svirt_obj, helper.VirtualMachineReplicaSetHelper)


def test_get_helper_raise_exception():
    with pytest.raises(Exception) as excinfo:
        helper.get_helper({}, 'non_existent_resource')
    assert 'Unknown kind non_existent_resource' in str(excinfo.value)
