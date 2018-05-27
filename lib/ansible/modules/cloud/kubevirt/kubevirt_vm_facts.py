#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vm_facts

short_description: Retrieve facts about a KubeVirt virtual machine

version_added: "2.5"

author: KubeVirt Team (@kubevirt)

description:
  - Retrieve facts about a KubeVirt virtual machine

requirements:
  - python >= 2.7
  - kubevirt-python >= 0.4.1-132-g074b4658
'''

EXAMPLES = '''
# Gather facts about a VM called C(testvm) running on the namespace C(vms)
- kubevirt_vm_facts:
    name: testvm
    namespace: vms
- debug:
    var: kubevirt_vm
'''

RETURN = '''
kubevirt_vm:
    description: "Dictionary describing the virtual machine. Virtual Machine
                  attributes are mapped to dictionary keys, which can be found
                  at the following URL:
                  http://www.kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine"
    returned: On success.
    type: dict
'''

import os
import kubevirt

from kubernetes.config import kube_config
from kubevirt.rest import ApiException
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.k8svirt.helper import VirtualMachineHelper


def main():
    """ Entry point. """
    argument_spec = dict(
        name=dict(type='str', required=True),
        namespace=dict(type='str', required=True),
        verify_ssl=dict(type='bool', required=False, default='no')
    )

    module = AnsibleModule(argument_spec)
    if os.path.exists(
            os.path.expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)):
        if not module.params.get('verify_ssl'):
            kubevirt.configuration.verify_ssl = False
        kube_config.load_kube_config(
            client_configuration=kubevirt.configuration)

    client = kubevirt.DefaultApi()
    api = VirtualMachineHelper(client)
    try:
        vm = api.exists(
            module.params.get('name'), module.params.get('namespace'))

        if vm is not None:
            module.exit_json(
                changed=False,
                ansible_facts=dict(kubevirt_vm=vm.to_dict())
            )
    except ApiException as exc:
        module.fail_json(msg=str(exc))


if __name__ == '__main__':
    main()
