import sys
import pytest

from ansible.compat.tests.mock import patch, MagicMock

from ansible.module_utils.k8s.common import K8sAnsibleMixin

from openshift.helper.exceptions import KubernetesException
from openshift.dynamic import Resource

from utils import set_module_args, AnsibleExitJson, exit_json, AnsibleFailJson, fail_json

# FIXME: paths/imports should be fixed before submitting a PR to Ansible
sys.path.append('lib/ansible/modules/clustering/kubevirt')

import kubevirt_raw as mymodule

RESOURCE_DEFAULT_ARGS = { 'api_version': 'v1', 'group': 'kubevirt.io',
                            'prefix': 'apis', 'namespaced': True }
TESTABLE_KINDS = ( 'VirtualMachineInstance', 'VirtualMachine', 'VirtualMachineInstanceReplicaSet',
                    'VirtualMachineInstancePreset', 'PersistentVolumeClaim' )
 

class TestKubeVirtRawModule(object):
    @pytest.fixture(autouse=True)
    def setup_class(cls, monkeypatch):
        monkeypatch.setattr(
            mymodule.KubeVirtVM, "exit_json", exit_json)
        monkeypatch.setattr(
            mymodule.KubeVirtVM, "fail_json", fail_json)
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


    @pytest.mark.parametrize("_wait", ( False, True ))
    @pytest.mark.parametrize("_kind", TESTABLE_KINDS)
    def test_resource_absent(self, _kind, _wait):
        # Desired state:
        args = dict(
            state='absent', kind=_kind, wait=_wait,
            name='testvmi', namespace='vms', api_version='v1')
        set_module_args(args)

        # Current state (mock):
        Resource.get.return_value = None # Resource does NOT exist in cluster
        resource_args = dict( kind=_kind, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['method'] == 'delete' and result.value[0]['changed'] == False


    @pytest.mark.parametrize("_phase, _exception", ( ('Bound', AnsibleExitJson),
                                                     ('Failed', AnsibleFailJson),
                                                     ('Unh4ndl3d', Exception) ) )
    @patch('kubevirt_raw.KubeVirtVM._create_stream')
    def test_pvc_creation_wait(self, mock_create_stream, _phase, _exception):
        _kind = 'PersistentVolumeClaim'
        # Desired state:
        args = dict(
            state='present', kind=_kind, wait=True,
            name='testvmi', namespace='vms', api_version='v1')
        set_module_args(args)

        # Mock pre-change state:
        Resource.get.return_value = None # Resource does NOT initially exist in cluster
        resource_args = dict( kind=_kind, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Mock post-change state:
        stream_obj = dict(
            status = dict( phase = _phase ),
            metadata = dict( annotations = { 'cdi.kubevirt.io/storage.pod.phase': 'Succeeded' } ),
            method = 'create', changed = True,
            )
        mock_watcher = MagicMock()
        mock_create_stream.return_value = ( mock_watcher, [ dict( object = stream_obj ) ] )

        # Actual test:
        with pytest.raises(_exception) as result:
            mymodule.KubeVirtVM().execute_module()
        if _exception is AnsibleExitJson:
            assert result.value[0]['method'] == 'create' and result.value[0]['changed'] == True


    @pytest.mark.parametrize("_kind", TESTABLE_KINDS)
    def test_resource_creation_nowait(self, _kind):
        # Desired state:
        args = dict(
            state='present', kind=_kind, wait=False,
            name='testvmi', namespace='vms', api_version='v1')
        set_module_args(args)

        # Current state (mock):
        Resource.get.return_value = None # Resource does NOT exist in cluster
        resource_args = dict( kind=_kind, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['method'] == 'create' and result.value[0]['changed'] == True


    @pytest.mark.parametrize("_wait", ( False, True ))
    @pytest.mark.parametrize("_kind", TESTABLE_KINDS)
    def test_resource_deletion(self, _kind, _wait):
        # Desired state:
        args = dict(
            state='absent', kind=_kind, wait=_wait,
            name='testvmi', namespace='vms', api_version='v1')
        set_module_args(args)

        # Current state (mock):
        Resource.get.return_value = True # Resource DOES exist in cluster
        resource_args = dict( kind=_kind, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

        # Actual test:
        with pytest.raises(AnsibleExitJson) as result:
            mymodule.KubeVirtVM().execute_module()
        assert result.value[0]['method'] == 'delete' and result.value[0]['changed'] == True

    @patch('openshift.watch.Watch')
    def test_stream_creation(self, mock_watch):
        _kind = 'PersistentVolumeClaim'
        # Desired state:
        args = dict(
            state='present', kind=_kind, wait=True,
            name='testvmi', namespace='vms', api_version='v1')
        set_module_args(args)

        # Mock pre-change state:
        Resource.get.return_value = None # Resource does NOT initially exist in cluster
        resource_args = dict( kind=_kind, **RESOURCE_DEFAULT_ARGS )
        K8sAnsibleMixin.find_resource.return_value = Resource(**resource_args)

         # Actual test:
        mock_watch.side_effect = KubernetesException("Test", value=42)
        with pytest.raises(AnsibleFailJson) as result:
            mymodule.KubeVirtVM().execute_module()
