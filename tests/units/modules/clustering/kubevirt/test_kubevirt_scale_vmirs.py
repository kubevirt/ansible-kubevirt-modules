import sys
import pytest

from ansible.compat.tests.mock import patch, MagicMock

from ansible.module_utils.k8s.common import K8sAnsibleMixin
from ansible.module_utils.k8s.raw import KubernetesRawModule

from openshift.dynamic import Resource, ResourceInstance
from openshift.helper.exceptions import KubernetesException

from utils import set_module_args, AnsibleExitJson, exit_json, AnsibleFailJson, fail_json, RESOURCE_DEFAULT_ARGS

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_scale_vmirs as mymodule


class TestKubeVirtScaleVMIRSModule(object):
    @pytest.fixture(autouse=True)
    def setup_class(cls, monkeypatch):
        monkeypatch.setattr(
            mymodule.KubeVirtScaleVMIRS, "exit_json", exit_json)
        monkeypatch.setattr(
            mymodule.KubeVirtScaleVMIRS, "fail_json", fail_json)
        # Create mock methods in Resource directly, otherwise dyn client
        # tries binding those to corresponding methods in DynamicClient
        # (with partial()), which is more problematic to intercept
        Resource.get = MagicMock()
        # Globally mock some methods, since all tests will use this
        KubernetesRawModule.patch_resource = MagicMock()
        KubernetesRawModule.patch_resource.return_value = ({}, None)
        K8sAnsibleMixin.get_api_client = MagicMock()
        K8sAnsibleMixin.get_api_client.return_value = None
        K8sAnsibleMixin.find_resource = MagicMock()

    @pytest.mark.parametrize("_replicas, _changed", ( (1, True),
                                                      (2, False),
                                                      (5, True), ) )
    def test_scale_vmirs_nowait(self, _replicas, _changed):
        _name = 'test-vmirs'
        # Desired state:
        args = dict(name=_name, namespace='vms', replicas=2, wait=False)
        set_module_args(args)

        # Mock pre-change state:
        resource_args = dict( kind='VirtualMachineInstanceReplicaSet', **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)
        res_inst = ResourceInstance('', dict(metadata = {'name': _name}, spec = {'replicas': _replicas}))
        Resource.get.return_value = res_inst

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtScaleVMIRS().execute_module()
        assert result.value[0]['changed'] == _changed


    @pytest.mark.parametrize("_replicas, _changed", ( (1, True),
                                                      (2, False),
                                                      (5, True), ) )
    @patch('kubevirt_scale_vmirs.KubeVirtScaleVMIRS._create_stream')
    def test_scale_vmirs_wait(self, mock_create_stream, _replicas, _changed):
        _name = 'test-vmirs'
        # Desired state:
        args = dict(name=_name, namespace='vms', replicas=_replicas, wait=True)
        set_module_args(args)

        # Mock pre-change state:
        resource_args = dict( kind='VirtualMachineInstanceReplicaSet', **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)
        res_inst = ResourceInstance('', dict(metadata = {'name': _name}, spec = {'replicas': 2}))
        Resource.get.return_value = res_inst

        # Mock post-change state:
        stream_obj = dict(
            status = dict(readyReplicas=_replicas),
            metadata = dict(name = _name)
            )
        mock_watcher = MagicMock()
        mock_create_stream.return_value = ( mock_watcher, [ dict(object=stream_obj) ] )

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtScaleVMIRS().execute_module()
        assert result.value[0]['changed'] == _changed

    @patch('openshift.watch.Watch')
    def test_stream_creation(self, mock_watch):
        _name = 'test-vmirs'
        # Desired state:
        args = dict(name=_name, namespace='vms', replicas=2, wait=True)
        set_module_args(args)

        # Mock pre-change state:
        resource_args = dict( kind='VirtualMachineInstanceReplicaSet', **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)
        res_inst = ResourceInstance('', dict(metadata = {'name': _name}, spec = {'replicas': 3}))
        Resource.get.return_value = res_inst

        # Actual test:
        mock_watch.side_effect = KubernetesException("Test", value=42)
        with pytest.raises(AnsibleFailJson) as result:
            mymodule.KubeVirtScaleVMIRS().execute_module()
