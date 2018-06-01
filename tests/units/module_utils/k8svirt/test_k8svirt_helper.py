import pytest
import sys

from kubevirt import DefaultApi, V1DeleteOptions, V1VirtualMachine, \
    V1OfflineVirtualMachine, V1VirtualMachineReplicaSet, V1VirtualMachinePreset

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
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    def test_virtualmachinehelper_create(self,
                                         mock_read,
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
        mock_read.return_value = None
        vm = helper.VirtualMachineHelper(client)
        vm.create(body, 'vms')
        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    def test_virtualmachinehelper_delete(self,
                                         mock_read,
                                         mock_delete):
        body = dict(
            kind='VirtualMachine',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='testvm', namespace='vms')
        )
        called_body = V1VirtualMachine().to_dict()
        called_body.update(body)
        client = DefaultApi()
        mock_read.return_value = None
        vm = helper.VirtualMachineHelper(client)
        vm.delete('testvm', 'vms')

        mock_delete.assert_called_once_with(V1DeleteOptions(), 'vms', 'testvm')

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine')
    def test_virtualmachinehelper_replace(self,
                                          mock_replace,
                                          mock_read,
                                          json_to_vm,
                                          user_vm):
        defined = user_vm
        client = DefaultApi()
        mock_read.return_value = json_to_vm
        vm = helper.VirtualMachineHelper(client)
        vm.replace(defined.to_dict(), 'vms', 'jhendrix')
        defined.metadata['resourceVersion'] = '177913'
        defined.status = dict(phase='Scheduling')
        mock_replace.assert_called_once_with(defined, 'vms', 'jhendrix')

    @patch('kubevirt.DefaultApi.create_namespaced_offline_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_offline_virtual_machine')
    def test_offlinevirtualmachinehelper_create(self,
                                                mock_read,
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
        mock_read.return_value = None
        ovm = helper.OfflineVirtualMachineHelper(client)
        ovm.create(body, 'vms')

        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_offline_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_offline_virtual_machine')
    def test_offlinevirtualmachinehelper_delete(self,
                                                mock_read,
                                                mock_delete):
        body = dict(
            kind='OfflineVirtualMachine',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='testovm', namespace='vms')
        )
        existing = V1OfflineVirtualMachine().to_dict()
        existing.update(body)
        client = DefaultApi()
        mock_read.return_value = existing
        ovm = helper.OfflineVirtualMachineHelper(client)
        ovm.delete('testovm', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testovm')

    @patch('kubevirt.DefaultApi.read_namespaced_offline_virtual_machine')
    @patch('kubevirt.DefaultApi.replace_namespaced_offline_virtual_machine')
    def test_offlinevirtualmachinehelper_replace(self,
                                                 mock_replace,
                                                 mock_read,
                                                 json_to_ovm,
                                                 user_ovm):
        defined = user_ovm
        client = DefaultApi()
        mock_read.return_value = json_to_ovm
        ovm = helper.OfflineVirtualMachineHelper(client)
        ovm.replace(defined.to_dict(), 'vms', 'baldr')
        defined.metadata['resourceVersion'] = '270363'
        defined.status = dict(created=True, ready=True)
        mock_replace.assert_called_once_with(defined, 'vms', 'baldr')

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_replica_set')
    def test_virtualmachinereplicasethelper_create(self,
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

        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_replica_set')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_replica_set')
    def test_virtualmachinereplicasethelper_delete(self,
                                                   mock_read,
                                                   mock_delete):
        body = dict(
            kind='VirtualMachineReplicaSet',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='testvmrs', namespace='vms')
        )
        existing = V1VirtualMachineReplicaSet().to_dict()
        existing.update(body)
        client = DefaultApi()
        mock_read.return_value = existing
        vmrs = helper.VirtualMachineReplicaSetHelper(client)
        vmrs.delete('testvmrs', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmrs')

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_replica_set')
    @patch(
        'kubevirt.DefaultApi.replace_namespaced_virtual_machine_replica_set')
    def test_virtualmachinereplicasethelper_replace(self,
                                                    mock_replace,
                                                    mock_read,
                                                    json_to_vmrs,
                                                    user_vmrs):
        defined = user_vmrs
        client = DefaultApi()
        mock_read.return_value = json_to_vmrs
        vmrs = helper.VirtualMachineReplicaSetHelper(client)
        vmrs.replace(defined.to_dict(), 'freyja', 'vms')
        defined.metadata['resourceVersion'] = '272140'
        defined.status = dict(replicas=2)
        mock_replace.assert_called_once_with(defined, 'freyja', 'vms')

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_preset')
    def test_virtualmachinepresethelper_create(self, mock_create):
        body = dict(
            kind='VirtualMachinePreset',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='vmps-small', namespace='vms')
        )
        called_body = V1VirtualMachinePreset().to_dict()
        called_body.update(body)
        client = DefaultApi()
        vmrs = helper.VirtualMachinePreSetHelper(client)
        vmrs.create(body, 'vms')

        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_preset')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_preset')
    def test_virtualmachinepresethelper_delete(self, mock_read, mock_delete):
        body = dict(
            kind='VirtualMachinePreset',
            spec=dict(),
            api_version='kubevirt.io/v1alpha',
            metadata=dict(name='vmps-small', namespace='vms')
        )
        existing = V1VirtualMachinePreset().to_dict()
        existing.update(body)
        client = DefaultApi()
        mock_read.return_value = existing
        vmrs = helper.VirtualMachinePreSetHelper(client)
        vmrs.delete('vmps-small', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'vmps-small')

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_preset')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine_preset')
    def test_virtualmachinepresethelper_replace(self,
                                                mock_replace,
                                                mock_read,
                                                json_to_vmps,
                                                user_vmps):
        defined = user_vmps
        client = DefaultApi()
        mock_read.return_value = json_to_vmps
        vmrs = helper.VirtualMachinePreSetHelper(client)
        vmrs.replace(defined.to_dict(), 'vmps-small', 'vms')
        defined.metadata['resourceVersion'] = '20928'
        mock_replace.assert_called_once_with(defined, 'vmps-small', 'vms')
