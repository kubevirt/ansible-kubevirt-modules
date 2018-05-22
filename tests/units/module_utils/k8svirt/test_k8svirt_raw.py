import json
import sys
import pytest

# from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/module_utils/k8svirt')

import raw
import helper

# KubeVirtRawModule
# Calls K8sVirtAnsibleModule() which itself calls AnsibleModule
# AnsibleModule does some magic but basically, module.(params, fail_json and
# exit_json) would be mocked


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestMyModule(object):
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch('raw.K8sVirtAnsibleModule')
    def test_module_initialization(self, mock_raw):
        args = dict(state='present', kind='VirtualMachine')
        mock_raw.return_value = {'params': args}
        set_module_args(args)
        k = raw.KubeVirtRawModule()
        assert k.kind == 'virtual_machine'
        assert isinstance(k.params, dict)

    @patch('helper.VirtualMachineHelper.create')
    @patch('helper.VirtualMachineHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_present(self, mock_exit_json, mock_exists, mock_create):
        args = dict(state='present', kind='VirtualMachine')
        set_module_args(args)
        mock_create.return_value = {}
        mock_exists.return_value = None
        mock_exit_json.return_value = exit_json
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_create.assert_called_once_with(None, None)
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('helper.VirtualMachineHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_present_existing(self, mock_exit_json, mock_exists):
        args = dict(state='present', kind='VirtualMachine', name='testvm', namespace='vms')
        set_module_args(args)
        mock_exists.return_value = dict(name='testvm', namespace='vms')
        mock_exit_json.return_value = exit_json
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(changed=False, result={})

    @patch('helper.VirtualMachineHelper.delete')
    @patch('helper.VirtualMachineHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_absent(self, mock_exit_json, mock_exists, mock_delete):
        args = dict(state='absent', kind='VirtualMachine', name='testvm', namespace='vms')
        set_module_args(args)
        mock_delete.return_value = {}
        mock_exists.return_value = dict(name='testvm', namespace='vms')
        mock_exit_json.return_value = exit_json
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_delete.assert_called_once_with('testvm', 'vms')
        mock_exit_json.assert_called_once_with(changed=True, result={})

    @patch('helper.VirtualMachineHelper.exists')
    @patch('raw.KubeVirtRawModule.exit_json')
    def test_execute_module_with_absent_non_existing(self, mock_exit_json, mock_exists):
        args = dict(state='absent', kind='VirtualMachine', name='testvm', namespace='vms')
        set_module_args(args)
        mock_exists.return_value = None
        mock_exit_json.return_value = exit_json
        k = raw.KubeVirtRawModule()
        k.execute_module()
        mock_exit_json.assert_called_once_with(changed=False, result={})
