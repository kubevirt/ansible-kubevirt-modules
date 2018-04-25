#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vm
short_description: Manage KubeVirt Offline VirtualMachines
description:
    - Create or delete a KubeVirt Offline VirtualMachine
extends_documentation_fragment:
  - kubevirt
options:
    state:
        description:
            - "Whether to create (C(present)) or delete (C(absent))
              the Offline VM."
        required: false
        default: "present"
        choices: ["present", "running", "absent"]
'''

EXAMPLES = '''
- name: Create the Offline VM
  kubevirt_ovm:
    name: testovm
    namespace: default

- name: Delete the Offline VM
  kubevirt_ovm:
    name: testovm
    namespace: default
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.kubevirt.common import KubeVirtAnsibleModule


def main():
    '''Entry point.'''
    run = KubeVirtAnsibleModule(api_group="offlinevirtualmachines")
    run.execute_module()


if __name__ == '__main__':
    main()
