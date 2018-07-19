import json
import sys
import pytest

# from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from kubevirt import V1VirtualMachineInstance

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')
import raw


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class TestMyModule(object):
    @patch('raw.K8sVirtAnsibleModule')
    def test_module_initialization(self, mock_raw, args_present):
        mock_raw.return_value = {'params': args_present}
        set_module_args(args_present)
        k = raw.KubeVirtRawModule()
        assert k.kind == 'virtual_machine_instance'
        assert isinstance(k.params, dict)

    @patch('helper.VirtualMachineInstanceHelper.create')
    @patch('helper.VirtualMachineInstanceHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_present(self,
                                         mock_exit_json,
                                         mock_exists,
                                         mock_create,
                                         args_present):
        set_module_args(args_present)
        mock_create.return_value = V1VirtualMachineInstance()
        mock_exists.return_value = None
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_create.assert_called_once_with(None, 'vms')
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1VirtualMachineInstance().to_dict())

    @patch('helper.VirtualMachineInstanceHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_present_existing(self,
                                                  mock_exit_json,
                                                  mock_exists,
                                                  args_present):
        set_module_args(args_present)
        mock_exists.return_value = dict(name='testvm', namespace='vms')
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(changed=False, result={})

    @patch('helper.VirtualMachineInstanceHelper.replace')
    @patch('helper.VirtualMachineInstanceHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_present_existing_with_force(self,
                                                             mock_exit_json,
                                                             mock_exists,
                                                             mock_replace,
                                                             args_present):
        args_present['force'] = 'yes'
        set_module_args(args_present)
        mock_exists.return_value = dict(name='testvm', namespace='vms')
        mock_replace.return_value = V1VirtualMachineInstance()
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_replace.assert_called_once_with(None, 'vms', 'testvm')
        mock_exit_json.assert_called_once_with(
            changed=True, result=V1VirtualMachineInstance().to_dict())

    @patch('helper.VirtualMachineInstanceHelper.delete')
    @patch('helper.VirtualMachineInstanceHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_absent(self,
                                        mock_exit_json,
                                        mock_exists,
                                        mock_delete,
                                        args_absent):
        set_module_args(args_absent)
        mock_delete.return_value = {}
        mock_exists.return_value = dict(name='testvm', namespace='vms')
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_delete.assert_called_once_with('testvm', 'vms')
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('helper.VirtualMachineInstanceHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_absent_non_existing(self,
                                                     mock_exit_json,
                                                     mock_exists,
                                                     args_absent):
        set_module_args(args_absent)
        mock_exists.return_value = None
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(changed=False, result={})
