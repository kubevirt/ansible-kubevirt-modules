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
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    def test_facts_for_virtual_machine(self,
                                       mock_read,
                                       json_to_vm):
        args = dict(name='testvm', namespace='vms')
        set_module_args(args)
        vm_facts = facts.KubeVirtFacts(kind='virtual_machine')
        vm_facts.execute_module()
        mock_read.return_value = json_to_vm
        mock_read.assert_called_once_with('testvm', 'vms', exact=True)

    @patch('kubevirt.DefaultApi.read_namespaced_offline_virtual_machine')
    def test_facts_for_offline_virtual_machine(self,
                                               mock_read,
                                               json_to_ovm):
        args = dict(name='testovm', namespace='vms')
        set_module_args(args)
        ovm_facts = facts.KubeVirtFacts(kind='offline_virtual_machine')
        ovm_facts.execute_module()
        mock_read.return_value = json_to_ovm
        mock_read.assert_called_once_with('testovm', 'vms', exact=True)

    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine_replica_set')
    def test_facts_for_virtual_machine_replica_set(self,
                                                   mock_read,
                                                   json_to_vmrs):
        args = dict(name='testvmrs', namespace='vms')
        set_module_args(args)
        vm_facts = facts.KubeVirtFacts(kind='virtual_machine_replica_set')
        vm_facts.execute_module()
        mock_read.return_value = json_to_vmrs
        mock_read.assert_called_once_with('testvmrs', 'vms', exact=True)

    def test_private_resource_and_list_cleanup(self):
        subdict = dict(
            key1='value1', key2=None, key3=list(
                [{'subkey1': 'subvalue1', 'subkey2': None}]
            )
        )
        expected = dict(
            key1='value1', key3=list([{'subkey1': 'subvalue1'}])
        )

        vm_facts = facts.KubeVirtFacts(kind='')
        result = vm_facts._KubeVirtFacts__resource_cleanup(subdict=subdict)

        assert result == expected
