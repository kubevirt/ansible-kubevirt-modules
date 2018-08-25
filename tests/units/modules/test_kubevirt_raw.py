import json
import sys

from ansible.compat.tests.mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from kubevirt import V1VirtualMachineInstance, V1VirtualMachine, \
    V1VirtualMachineInstanceReplicaSet, V1VirtualMachineInstancePreset, \
    V1DeleteOptions
from kubernetes.client import V1PersistentVolumeClaim

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')
import raw


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class TestKubeVirtRawModule(object):
    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_instance')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_instance_present(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_create
    ):
        args = dict(
            state='present', kind='VirtualMachineInstance',
            name='testvmi', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachineInstance().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = None
        mock_kubevirt_create.return_value = V1VirtualMachineInstance()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1VirtualMachineInstance().to_dict())

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_present(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_create,
    ):
        args = dict(
            state='present', kind='VirtualMachine',
            name='testvm', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachine().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = None
        mock_kubevirt_create.return_value = V1VirtualMachine()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1VirtualMachine().to_dict())

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_instance_replica_set')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_replica_set')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_instance_replica_set_present(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_create,
    ):
        args = dict(
            state='present', kind='VirtualMachineInstanceReplicaSet',
            name='testvm', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachineInstanceReplicaSet().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = None
        mock_kubevirt_create.return_value = V1VirtualMachineInstanceReplicaSet()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(
            changed=True,
            result=V1VirtualMachineInstanceReplicaSet().to_dict())

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine_instance_preset')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_preset')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_instance_preset_present(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_create,
    ):
        args = dict(
            state='present', kind='VirtualMachineInstancePreset',
            name='testvm', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachineInstancePreset().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = None
        mock_kubevirt_create.return_value = V1VirtualMachineInstancePreset()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1VirtualMachineInstancePreset().to_dict())

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_absent(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_delete,
    ):
        args = dict(
            state='absent', kind='VirtualMachine',
            name='testvm', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachine().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = V1VirtualMachine()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_kubevirt_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvm')
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_instance')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_instance_absent(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_delete,
    ):
        args = dict(
            state='absent', kind='VirtualMachineInstance',
            name='testvmi', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachineInstance().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = V1VirtualMachineInstance()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_kubevirt_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmi')
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_instance_replica_set')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_replica_set')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_instance_replica_set_absent(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_delete,
    ):
        args = dict(
            state='absent', kind='VirtualMachineInstanceReplicaSet',
            name='testvmirs', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachineInstanceReplicaSet().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = V1VirtualMachineInstanceReplicaSet()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_kubevirt_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmirs')
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine_instance_preset')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_preset')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_virtual_machine_instance_preset_absent(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_delete,
    ):
        args = dict(
            state='absent', kind='VirtualMachineInstancePreset',
            name='testvmips', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachineInstancePreset().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = V1VirtualMachineInstancePreset()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_kubevirt_delete.assert_called_once_with(
            V1DeleteOptions(), 'vms', 'testvmips')
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('kubevirt.DefaultApi.create_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_execute_module_with_present_existing(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_create
    ):
        args = dict(
            state='present', kind='VirtualMachine',
            name='testvm', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachine().to_dict())
        set_module_args(args)
        mock_kubevirt_read.return_value = V1VirtualMachine()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(changed=False, result={})
        mock_kubevirt_create.assert_not_called()

    @patch('kubevirt.DefaultApi.delete_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_execute_module_with_absent_non_existing(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_delete
    ):
        args = dict(
            state='absent', kind='VirtualMachine',
            name='testvm', namespace='vms', api_version='v1')
        set_module_args(args)
        mock_kubevirt_read.return_value = None
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(changed=False, result={})
        mock_kubevirt_delete.assert_not_called()

    @patch('kubevirt.DefaultApi.replace_namespaced_virtual_machine')
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_execute_module_with_present_existing_with_force(
        self, mock_exit_json, mock_kubevirt_read, mock_kubevirt_replace
    ):
        args = dict(
            state='present', kind='VirtualMachine', force='yes',
            name='testvm', namespace='vms', api_version='v1',
            resource_definition=V1VirtualMachine(
                metadata=dict(resourceVersion='yyyyyy')).to_dict())

        set_module_args(args)

        existing = V1VirtualMachine(metadata=dict(resource_version='xxxxxxxx'))
        mock_kubevirt_read.return_value = existing
        mock_kubevirt_replace.return_value = V1VirtualMachine()

        k = raw.KubeVirtRawModule()
        k.execute_module()

        mock_kubevirt_replace.assert_called_once_with(
            V1VirtualMachine(metadata=dict(resourceVersion='xxxxxxxx')),
            'vms', 'testvm')
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1VirtualMachine().to_dict())

    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    def test_execute_module_without_kind(self, mock_fail_json):
        args = dict(
            state='present', name='testvm',
            namespace='vms', api_version='v1')

        set_module_args(args)
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_fail_json.assert_called_once_with(
            msg=("Error: missing kind. Use the kind parameter ",
                 "or specify it as part of a resource_definition."))

    @patch('kubernetes.client.CoreV1Api.create_namespaced_persistent_volume_claim')
    @patch('kubernetes.client.CoreV1Api.read_namespaced_persistent_volume_claim')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_persistent_volume_claim_present(
        self, mock_exit_json, mock_k8s_read, mock_k8s_create
    ):
        args = dict(
            state='present', kind='PersistentVolumeClaim',
            name='pvc-demo', namespace='vms', api_version='v1',
            resource_definition=V1PersistentVolumeClaim().to_dict())
        set_module_args(args)
        mock_k8s_read.return_value = None
        mock_k8s_create.return_value = V1PersistentVolumeClaim()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1PersistentVolumeClaim().to_dict())

    @patch('kubernetes.client.CoreV1Api.delete_namespaced_persistent_volume_claim')
    @patch('kubernetes.client.CoreV1Api.read_namespaced_persistent_volume_claim')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_persistent_volume_claim_absent(
        self, mock_exit_json, mock_k8s_read, mock_k8s_delete,
    ):
        args = dict(
            state='absent', kind='PersistentVolumeClaim',
            name='pvc-demo', namespace='vms', api_version='v1',
            resource_definition=V1PersistentVolumeClaim().to_dict())
        set_module_args(args)
        mock_k8s_read.return_value = V1PersistentVolumeClaim()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_k8s_delete.assert_called_once_with(
            name='pvc-demo', namespace='vms', body={})
        mock_exit_json.assert_called_once_with(changed=True, result={})
