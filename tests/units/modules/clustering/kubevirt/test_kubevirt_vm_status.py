import sys
import pytest

from ansible.compat.tests.mock import patch

from openshift.dynamic import ResourceContainer, ResourceInstance

from utils import set_module_args, AnsibleExitJson, exit_json

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_vm_status as mymodule


class TestKubeVirtVMStatusModule(object):
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(cls, monkeypatch):
        monkeypatch.setattr(
            mymodule.KubeVirtVMStatus, "exit_json", exit_json)
        args = dict(name='baldr', namespace='vms', state='stopped')
        set_module_args(args)

    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.get_api_client')
    @patch('ansible.module_utils.k8s.raw.KubernetesRawModule.patch_resource')
    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.find_resource')
    @patch('openshift.dynamic.ResourceContainer.get')
    def test_run_vm_main(
        self, mock_get_resource, mock_find_resource, mock_patch_resource, mock_api_client,
    ):
        mock_api_client.return_value = None
        mock_find_resource.return_value = ResourceContainer({})
        mock_get_resource.return_value = ResourceInstance('', {'spec': {'running': True}})
        mock_patch_resource.return_value = ({}, None)
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVMStatus().execute_module()
        assert result.value[0]['changed']

    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.get_api_client')
    @patch('ansible.module_utils.k8s.raw.KubernetesRawModule.patch_resource')
    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.find_resource')
    @patch('openshift.dynamic.ResourceContainer.get')
    def test_run_vm_same_state(
        self, mock_get_resource, mock_find_resource, mock_patch_resource, mock_api_client,
    ):
        mock_api_client.return_value = None
        mock_find_resource.return_value = ResourceContainer({})
        mock_get_resource.return_value = ResourceInstance('', {'spec': {'running': False}})
        mock_patch_resource.return_value = ({}, None)
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVMStatus().execute_module()
        assert not result.value[0]['changed']
