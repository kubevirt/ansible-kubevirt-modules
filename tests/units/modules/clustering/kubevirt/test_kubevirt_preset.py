import pytest
import sys

from openshift.dynamic import Resource

from ansible.compat.tests.mock import MagicMock
from ansible.module_utils.k8s.common import K8sAnsibleMixin
from ansible.module_utils.k8s.raw import KubernetesRawModule

from utils import set_module_args, AnsibleExitJson, exit_json, fail_json, RESOURCE_DEFAULT_ARGS

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_vm as mymodule

KIND = 'VirtulMachineInstancePreset'


class TestKubeVirtVMIPresetModule(object):

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
        Resource.search = MagicMock()
        Resource.create = MagicMock()
        Resource.delete = MagicMock()
        # Globally mock some methods, since all tests will use this
        K8sAnsibleMixin.get_api_client = MagicMock()
        K8sAnsibleMixin.get_api_client.return_value = None
        mymodule.KubeVirtVM.find_supported_resource = MagicMock()

    def test_preset_creation(self):
        args = dict(
            state='present', name='testvmipreset',
            namespace='vms', api_version='v1',
            memory='1024Mi',
        )
        set_module_args(args)

        Resource.get.return_value = None
        Resource.search.return_value = None
        resource_args = dict(kind=KIND, **RESOURCE_DEFAULT_ARGS)
        mymodule.KubeVirtVM.find_supported_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['changed']
        assert result.value[0]['result']['method'] == 'create'

    def test_preset_absent(self):
        args = dict(
            state='absent', name='testvmipreset',
            namespace='vms', api_version='v1',
        )
        set_module_args(args)

        Resource.get.return_value = None
        Resource.search.return_value = None
        resource_args = dict(kind=KIND, **RESOURCE_DEFAULT_ARGS)
        mymodule.KubeVirtVM.find_supported_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['result']['method'] == 'delete'
