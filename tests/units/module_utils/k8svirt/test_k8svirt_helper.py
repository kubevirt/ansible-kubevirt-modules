import pytest
import sys

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')

import helper


class TestHelperModuleUtils(object):
    def test_to_snake(self):
        assert helper.to_snake('VirtualMachine') == 'virtual_machine'
        assert helper.to_snake('V1VirtualMachine') == 'v1_virtual_machine'

    def test_get_helper(self):
        client = dict()
        core_client = dict()
        k8svirt_obj = helper.get_helper(
            client, core_client, 'virtual_machine_instance')
        assert isinstance(k8svirt_obj, helper.VirtualMachineInstanceHelper)
        k8svirt_obj = helper.get_helper(client, core_client, 'virtual_machine')
        assert isinstance(k8svirt_obj, helper.VirtualMachineHelper)
        k8svirt_obj = helper.get_helper(
            client, core_client, 'virtual_machine_instance_replica_set')
        assert isinstance(
            k8svirt_obj, helper.VirtualMachineInstanceReplicaSetHelper)
        k8svirt_obj = helper.get_helper(
            client, core_client, 'virtual_machine_instance_preset')
        assert isinstance(
            k8svirt_obj, helper.VirtualMachineInstancePreSetHelper)

    def test_get_helper_raise_exception(self):
        with pytest.raises(Exception) as excinfo:
            helper.get_helper({}, {}, 'non_existent_resource')
        assert 'Unknown kind non_existent_resource' in str(excinfo.value)
