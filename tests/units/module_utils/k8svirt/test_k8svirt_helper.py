import pytest
import sys

from kubevirt import DefaultApi, V1DeleteOptions, V1VirtualMachine, \
    V1OfflineVirtualMachine, V1VirtualMachineReplicaSet

from ansible.compat.tests.mock import patch
# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')

import helper


class TestHelper(object):
    def test_to_snake(self):
        assert helper.to_snake('VirtualMachine') == 'virtual_machine'
        assert helper.to_snake(
            'V1OfflineVirtualMachine') == 'v1_offline_virtual_machine'

    def test_get_helper(self):
        client = dict()
        k8svirt_obj = helper.get_helper(client, 'virtual_machine')
        assert isinstance(k8svirt_obj, helper.VirtualMachineHelper)
        k8svirt_obj = helper.get_helper(client, 'offline_virtual_machine')
        assert isinstance(k8svirt_obj, helper.OfflineVirtualMachineHelper)
        k8svirt_obj = helper.get_helper(client, 'virtual_machine_replica_set')
        assert isinstance(k8svirt_obj, helper.VirtualMachineReplicaSetHelper)

    def test_get_helper_raise_exception(self):
        with pytest.raises(Exception) as excinfo:
            helper.get_helper({}, 'non_existent_resource')
        assert 'Unknown kind non_existent_resource' in str(excinfo.value)

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine')
    def test_virtualmachinehelper_class(self,
                                        mock_replace,
                                        mock_read,
                                        mock_delete,
                                        mock_create):
        body = dict(
            kind='VirtualMachine',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='testvm', namespace='vms')
        )
        called_body = V1VirtualMachine().to_dict()
        called_body.update(body)
        client = DefaultApi()
        vm = helper.VirtualMachineHelper(client)
        vm.create(body, 'vms')
        vm.delete('testvm', 'vms')
        vm.replace(body, 'vms', 'testvm')

        mock_create.assert_called_once_with(called_body, 'vms')
        mock_delete.assert_called_once_with(V1DeleteOptions(), 'vms', 'testvm')
        mock_replace.assert_called_once_with(called_body, 'vms', 'testvm')

    @patch('kubevirt.DefaultApi.create_namespaced_offline_virtual_machine')
    @patch('kubevirt.DefaultApi.delete_namespaced_offline_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_offline_virtual_machine')
    @patch('kubevirt.DefaultApi.replace_namespaced_offline_virtual_machine')
    def test_offlinevirtualmachinehelper_class(self,
                                               mock_replace,
                                               mock_read,
                                               mock_delete,
                                               mock_create):
        body = dict(
            kind='OfflineVirtualMachine',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='testovm', namespace='vms')
        )
        called_body = V1OfflineVirtualMachine().to_dict()
        called_body.update(body)
        client = DefaultApi()
        ovm = helper.OfflineVirtualMachineHelper(client)
        ovm.create(body, 'vms')
        ovm.delete('testovm', 'vms')
        ovm.replace(body, 'vms', 'testovm')

        mock_create.assert_called_once_with(called_body, 'vms')
        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testovm')
        mock_replace.assert_called_once_with(called_body, 'vms', 'testovm')

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_replica_set')
    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_replica_set')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_replica_set')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine_replica_set')
    def test_virtualmachinereplicasethelper_class(self,
                                                  mock_replace,
                                                  mock_read,
                                                  mock_delete,
                                                  mock_create):
        body = dict(
            kind='VirtualMachineReplicaSet',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='testvmrs', namespace='vms')
        )
        called_body = V1VirtualMachineReplicaSet().to_dict()
        called_body.update(body)
        client = DefaultApi()
        vmrs = helper.VirtualMachineReplicaSetHelper(client)
        vmrs.create(body, 'vms')
        vmrs.delete('testvmrs', 'vms')
        vmrs.replace(body, 'testvmrs', 'vms')

        mock_create.assert_called_once_with(called_body, 'vms')
        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmrs')
        mock_replace.assert_called_once_with(called_body, 'vms', 'testvmrs')
