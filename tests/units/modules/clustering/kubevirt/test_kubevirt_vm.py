import json
import pytest
import sys

from openshift.dynamic import Resource
from openshift.helper.exceptions import KubernetesException

from ansible.compat.tests.mock import patch, MagicMock
from ansible.module_utils.k8s.common import K8sAnsibleMixin
from ansible.module_utils.k8s.raw import KubernetesRawModule

from utils import set_module_args, AnsibleFailJson, AnsibleExitJson, exit_json, fail_json, RESOURCE_DEFAULT_ARGS

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_vm as mymodule

KIND = 'VirtulMachine'


class TestKubeVirtVmModule(object):

    @pytest.fixture(autouse=True)
    def setup_class(cls, monkeypatch):
        monkeypatch.setattr(
            KubernetesRawModule, "exit_json", exit_json)
        monkeypatch.setattr(
            KubernetesRawModule, "fail_json", fail_json)
        # Create mock methods in Resource directly, otherwise dyn client
        # tries binding those to corresponding methods in DynamicClient
        # (with partial()), which is more problematic to intercept
        Resource.get = MagicMock()
        Resource.create = MagicMock()
        Resource.delete = MagicMock()
        # Globally mock some methods, since all tests will use this
        K8sAnsibleMixin.get_api_client = MagicMock()
        K8sAnsibleMixin.get_api_client.return_value = None
        K8sAnsibleMixin.find_resource = MagicMock()

    def test_vm_multus_creation(self):
        args = dict(
            state='present', name='testvm',
            namespace='vms', api_version='v1',
            interfaces=[
                {'bridge': {}, 'name': 'default', 'network': {'pod': {}}},
                {'bridge': {}, 'name': 'mynet', 'network': {'multus': {'networkName': 'mynet'}}},
            ],
        )
        set_module_args(args)

        Resource.get.return_value = None
        resource_args = dict(kind=KIND, **RESOURCE_DEFAULT_ARGS)
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['changed']
        assert result.value[0]['result']['method'] == 'create'

    @pytest.mark.parametrize("_wait", ( False, True ))
    def test_resource_absent(self, _wait):
        # Desired state:
        args = dict(
            state='absent', name='testvmi',
            namespace='vms', api_version='v1',
            wait=_wait,
        )
        set_module_args(args)

        Resource.get.return_value = None
        resource_args = dict( kind=KIND, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['result']['method'] == 'delete'

    @patch('openshift.watch.Watch')
    def test_stream_creation(self, mock_watch):
        # Desired state:
        args = dict(
            state='running', name='testvmi',
            namespace='vms', api_version='v1',
            wait=True)
        set_module_args(args)

        # Mock pre-change state:
        Resource.get.return_value = None # Resource does NOT initially exist in cluster
        resource_args = dict( kind=KIND, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Actual test:
        mock_watch.side_effect = KubernetesException("Test", value=42)
        with pytest.raises(AnsibleFailJson) as result:
            mymodule.KubeVirtVM().execute_module()

    def test_simple_merge_dicts(self):
        dict1 = {'labels': {'label1': 'value'}}
        dict2 = {'labels': {'label2': 'value'}}
        dict3 = json.dumps({'labels': {'label1': 'value', 'label2': 'value'}}, sort_keys=True)
        assert dict3 == json.dumps(dict(mymodule.KubeVirtVM.merge_dicts(dict1, dict2)))

    def test_simple_multi_merge_dicts(self):
        dict1 = {'labels': {'label1': 'value', 'label3': 'value'}}
        dict2 = {'labels': {'label2': 'value'}}
        dict3 = json.dumps({'labels': {'label1': 'value', 'label2': 'value', 'label3': 'value'}}, sort_keys=True)
        assert dict3 == json.dumps(dict(mymodule.KubeVirtVM.merge_dicts(dict1, dict2)))

    def test_double_nested_merge_dicts(self):
        dict1 = {'metadata': {'labels': {'label1': 'value', 'label3': 'value'}}}
        dict2 = {'metadata': {'labels': {'label2': 'value'}}}
        dict3 = json.dumps({'metadata': {'labels': {'label1': 'value', 'label2': 'value', 'label3': 'value'}}}, sort_keys=True)
        assert dict3 == json.dumps(dict(mymodule.KubeVirtVM.merge_dicts(dict1, dict2)))
