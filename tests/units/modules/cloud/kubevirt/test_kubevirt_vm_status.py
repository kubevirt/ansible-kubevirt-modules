import json
import sys
import pytest

from ansible.compat.tests.mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/cloud/kubevirt')

import kubevirt_vm_status as mymodule


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught
    by the test case"""
    pass


def exit_json(*args, **kwargs):
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


class TestKubeVirtVMStatusModule(object):
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(cls, monkeypatch):
        monkeypatch.setattr(
            mymodule.K8sVirtAnsibleModule, "exit_json", exit_json)
        args = dict(name='baldr', namespace='vms', state='stopped')
        set_module_args(args)

    @patch('kubernetes.client.ApiClient')
    @patch('kubernetes.client.CustomObjectsApi.patch_namespaced_custom_object')
    @patch('kubernetes.client.CustomObjectsApi.get_namespaced_custom_object')
    def test_run_vm_main(
        self, mock_crd_get, mock_crd_patch, mock_client
    ):
        mock_client.return_value = dict()
        mock_crd_get.return_value = dict(spec=dict(running=True))
        mock_crd_patch.return_value = dict()
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVMStatus().execute_module()
        assert result.value[0]['changed']
        mock_crd_patch.assert_called_once_with(
            'kubevirt.io', 'v1alpha2', 'vms', 'virtualmachines',
            'baldr', dict(spec=dict(running=False)))

    @patch('kubernetes.client.ApiClient')
    @patch('kubernetes.client.CustomObjectsApi.patch_namespaced_custom_object')
    @patch('kubernetes.client.CustomObjectsApi.get_namespaced_custom_object')
    def test_run_vm_same_state(
        self, mock_crd_get, mock_crd_patch, mock_client
    ):
        mock_client.return_value = dict()
        mock_crd_get.return_value = dict(spec=dict(running=False))
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVMStatus().execute_module()
        assert not result.value[0]['changed']
