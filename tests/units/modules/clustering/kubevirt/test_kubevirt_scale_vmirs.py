import sys
import pytest

from ansible.compat.tests.mock import patch

from openshift.dynamic import ResourceContainer, ResourceInstance

from utils import set_module_args, AnsibleExitJson, exit_json

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_scale_vmirs as mymodule



class TestKubeVirtScaleVMIRSModule(object):
    @pytest.fixture(autouse=True)
    def setup_class(cls, monkeypatch):
        monkeypatch.setattr(
            mymodule.KubeVirtScaleVMIRS, "exit_json", exit_json)
        args = dict(name='freyja', namespace='vms', replicas=2, wait=False)
        set_module_args(args)

    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.get_api_client')
    @patch('ansible.module_utils.k8s.raw.KubernetesRawModule.patch_resource')
    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.find_resource')
    @patch('openshift.dynamic.ResourceContainer.get')
    def test_scale_vmirs_main(
        self, mock_get_resource, mock_find_resource, mock_patch_resource, mock_api_client,
    ):
        mock_api_client.return_value = None
        mock_find_resource.return_value = ResourceContainer({})
        mock_get_resource.return_value = ResourceInstance('', {'metadata': {'name': 'freyja'}, 'spec': {'replicas': 1}})
        mock_patch_resource.return_value = ({}, None)
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtScaleVMIRS().execute_module()
        assert result.value[0]['changed']

    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.get_api_client')
    @patch('ansible.module_utils.k8s.raw.KubernetesRawModule.patch_resource')
    @patch('ansible.module_utils.k8s.common.K8sAnsibleMixin.find_resource')
    @patch('openshift.dynamic.ResourceContainer.get')
    def test_scale_vmirs_same_replica_number(
        self, mock_get_resource, mock_find_resource, mock_patch_resource, mock_api_client,
    ):
        mock_api_client.return_value = None
        mock_find_resource.return_value = ResourceContainer({})
        mock_get_resource.return_value = ResourceInstance('', {'metadata': {'name': 'freyja'}, 'spec': {'replicas': 2}})
        mock_patch_resource.return_value = ({}, None)
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtScaleVMIRS().execute_module()
        assert not result.value[0]['changed']
