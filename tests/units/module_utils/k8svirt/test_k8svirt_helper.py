import pytest
import sys

from kubevirt import DefaultApi, V1DeleteOptions, V1VirtualMachineInstance, \
    V1VirtualMachine, V1VirtualMachineInstanceReplicaSet, \
    V1VirtualMachineInstancePreset

from ansible.compat.tests.mock import patch
# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')

import helper


class TestHelper(object):
    def test_to_snake(self):
        assert helper.to_snake('VirtualMachine') == 'virtual_machine'
        assert helper.to_snake('V1VirtualMachine') == 'v1_virtual_machine'

    def test_get_helper(self):
        client = dict()
        k8svirt_obj = helper.get_helper(client, 'virtual_machine_instance')
        assert isinstance(k8svirt_obj, helper.VirtualMachineInstanceHelper)
        k8svirt_obj = helper.get_helper(client, 'virtual_machine')
        assert isinstance(k8svirt_obj, helper.VirtualMachineHelper)
        k8svirt_obj = helper.get_helper(
            client, 'virtual_machine_instance_replica_set')
        assert isinstance(
            k8svirt_obj, helper.VirtualMachineInstanceReplicaSetHelper)

    def test_get_helper_raise_exception(self):
        with pytest.raises(Exception) as excinfo:
            helper.get_helper({}, 'non_existent_resource')
        assert 'Unknown kind non_existent_resource' in str(excinfo.value)

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_instance')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance')
    def test_virtualmachineinstancehelper_create(self,
                                                 mock_read,
                                                 mock_create):
        body = dict(
            kind='VirtualMachineInstance',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='testvmi', namespace='vms')
        )
        called_body = V1VirtualMachineInstance().to_dict()
        called_body.update(body)
        client = DefaultApi()
        mock_read.return_value = None
        vmi = helper.VirtualMachineInstanceHelper(client)
        vmi.create(body, 'vms')
        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_instance')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance')
    def test_virtualmachineinstancehelper_delete(self,
                                                 mock_read,
                                                 mock_delete):
        body = dict(
            kind='VirtualMachineInstance',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='testvmi', namespace='vms')
        )
        called_body = V1VirtualMachine().to_dict()
        called_body.update(body)
        client = DefaultApi()
        mock_read.return_value = None
        vmi = helper.VirtualMachineInstanceHelper(client)
        vmi.delete('testvmi', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmi')

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine_instance')
    def test_virtualmachineinstancehelper_replace(self,
                                                  mock_replace,
                                                  mock_read,
                                                  json_to_vmi,
                                                  user_vmi):
        defined = user_vmi
        client = DefaultApi()
        mock_read.return_value = json_to_vmi
        vmi = helper.VirtualMachineInstanceHelper(client)
        vmi.replace(defined.to_dict(), 'vms', 'jhendrix')
        defined.metadata['resourceVersion'] = '177913'
        defined.status = dict(phase='Scheduling')
        mock_replace.assert_called_once_with(defined, 'vms', 'jhendrix')

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    def test_virtualmachinehelper_create(self,
                                         mock_read,
                                         mock_create):
        body = dict(
            kind='VirtualMachine',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
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
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='testvm', namespace='vms')
        )
        existing = V1VirtualMachine().to_dict()
        existing.update(body)
        client = DefaultApi()
        mock_read.return_value = existing
        vm = helper.VirtualMachineHelper(client)
        vm.delete('testvm', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvm')

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
        vm.replace(defined.to_dict(), 'vms', 'baldr')
        defined.metadata['resourceVersion'] = '270363'
        defined.status = dict(created=True, ready=True)
        mock_replace.assert_called_once_with(defined, 'vms', 'baldr')

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_instance_replica_set')
    def test_virtualmachineinstancereplicasethelper_create(self,
                                                           mock_create):
        body = dict(
            kind='VirtualMachineInstanceReplicaSet',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='testvmirs', namespace='vms')
        )
        called_body = V1VirtualMachineInstanceReplicaSet().to_dict()
        called_body.update(body)
        client = DefaultApi()
        vmirs = helper.VirtualMachineInstanceReplicaSetHelper(client)
        vmirs.create(body, 'vms')

        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_instance_replica_set')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_replica_set')
    def test_virtualmachineinstancereplicasethelper_delete(self,
                                                           mock_read,
                                                           mock_delete):
        body = dict(
            kind='VirtualMachineInstanceReplicaSet',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='testvmirs', namespace='vms')
        )
        existing = V1VirtualMachineInstanceReplicaSet().to_dict()
        existing.update(body)
        client = DefaultApi()
        mock_read.return_value = existing
        vmirs = helper.VirtualMachineInstanceReplicaSetHelper(client)
        vmirs.delete('testvmirs', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmirs')

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_replica_set')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine_instance_replica_set')
    def test_virtualmachineinstancereplicasethelper_replace(self,
                                                            mock_replace,
                                                            mock_read,
                                                            json_to_vmirs,
                                                            user_vmirs):
        defined = user_vmirs
        client = DefaultApi()
        mock_read.return_value = json_to_vmirs
        vmirs = helper.VirtualMachineInstanceReplicaSetHelper(client)
        vmirs.replace(defined.to_dict(), 'freyja', 'vms')
        defined.metadata['resourceVersion'] = '272140'
        defined.status = dict(replicas=2)
        mock_replace.assert_called_once_with(defined, 'freyja', 'vms')

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_instance_preset')
    def test_virtualmachineinstancepresethelper_create(self, mock_create):
        body = dict(
            kind='VirtualMachineInstancePreset',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='vmps-small', namespace='vms')
        )
        called_body = V1VirtualMachineInstancePreset().to_dict()
        called_body.update(body)
        client = DefaultApi()
        vmips = helper.VirtualMachineInstancePreSetHelper(client)
        vmips.create(body, 'vms')

        mock_create.assert_called_once_with(called_body, 'vms')

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_instance_preset')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_preset')
    def test_virtualmachineinstancepresethelper_delete(self,
                                                       mock_read,
                                                       mock_delete):
        body = dict(
            kind='VirtualMachineInstancePreset',
            spec=dict(),
            api_version='kubevirt.io/v1alpha2',
            metadata=dict(name='vmps-small', namespace='vms')
        )
        existing = V1VirtualMachineInstancePreset().to_dict()
        existing.update(body)
        client = DefaultApi()
        mock_read.return_value = existing
        vmips = helper.VirtualMachineInstancePreSetHelper(client)
        vmips.delete('vmps-small', 'vms')

        mock_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'vmps-small')

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_preset')
    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine_instance_preset')
    def test_virtualmachineinstancepresethelper_replace(self,
                                                        mock_replace,
                                                        mock_read,
                                                        json_to_vmips,
                                                        user_vmips):
        defined = user_vmips
        client = DefaultApi()
        mock_read.return_value = json_to_vmips
        vmips = helper.VirtualMachineInstancePreSetHelper(client)
        vmips.replace(defined.to_dict(), 'vmps-small', 'vms')
        defined.metadata['resourceVersion'] = '20928'
        mock_replace.assert_called_once_with(defined, 'vmps-small', 'vms')
