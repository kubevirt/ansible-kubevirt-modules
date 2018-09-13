import sys
import json

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


sys.path.append('module_utils/k8svirt')

import facts


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class TestFactsModuleUtils(object):
    def test_private_resource_and_list_cleanup(self):
        subdict = dict(
            key1='value1', key2=None, key3=list(
                [{'subkey1': 'subvalue1', 'subkey2': None}]
            )
        )
        expected = dict(
            key1='value1', key3=list([{'subkey1': 'subvalue1'}])
        )

        args = dict(name='testvm', namespace='vms', kind='virtual_machine')
        set_module_args(args)
        vm_facts = facts.KubeVirtFacts()
        result = vm_facts._KubeVirtFacts__resource_cleanup(subdict=subdict)

        assert result == expected
