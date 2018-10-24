import json

from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic

RESOURCE_DEFAULT_ARGS = { 'api_version': 'v1', 'group': 'kubevirt.io',
                            'prefix': 'apis', 'namespaced': True }

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


