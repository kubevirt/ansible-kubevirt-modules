import sys
import json

from ansible.compat.tests.mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


sys.path.append('lib/ansible/module_utils/k8svirt')

import facts


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class TestFacts(object):
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance')
    def test_facts_for_virtual_machine_instance(self,
                                                mock_read,
                                                json_to_vmi):
        args = dict(
            name='testvmi', namespace='vms', kind='virtual_machine_instance')
        set_module_args(args)
        vmi_facts = facts.KubeVirtFacts()
        vmi_facts.execute_module()
        mock_read.return_value = json_to_vmi
        mock_read.assert_called_once_with('testvmi', 'vms', exact=True)

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    def test_facts_for_virtual_machine(self,
                                       mock_read,
                                       json_to_vm):
        args = dict(name='testvm', namespace='vms', kind='virtual_machine')
        set_module_args(args)
        vm_facts = facts.KubeVirtFacts()
        vm_facts.execute_module()
        mock_read.return_value = json_to_vm
        mock_read.assert_called_once_with('testvm', 'vms', exact=True)

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_instance_replica_set')
    def test_facts_for_virtual_machine_instance_replica_set(self,
                                                            mock_read,
                                                            json_to_vmirs):
        args = dict(
            name='testvmirs', namespace='vms',
            kind='virtual_machine_instance_replica_set')
        set_module_args(args)
        vmirs_facts = facts.KubeVirtFacts()
        vmirs_facts.execute_module()
        mock_read.return_value = json_to_vmirs
        mock_read.assert_called_once_with('testvmirs', 'vms', exact=True)

    def test_private_resource_and_list_cleanup(self):
        subdict = dict(
            key1='value1', key2=None, key3=list(
                [{'subkey1': 'subvalue1', 'subkey2': None}]
            )
        )
        expected = dict(
            key1='value1', key3=list([{'subkey1': 'subvalue1'}])
        )

        vm_facts = facts.KubeVirtFacts()
        result = vm_facts._KubeVirtFacts__resource_cleanup(subdict=subdict)

        assert result == expected
