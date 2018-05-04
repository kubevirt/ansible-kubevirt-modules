#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vmrs
short_description: Manage KubeVirt VM ReplicaSets
description:
  - Create or delete a KubeVirt VM ReplicaSets
extends_documentation_fragment:
  - kubevirt
options:
  state:
    description:
    - "Whether to create (C(present)), create but pause (C(paused)
      or delete (C(absent)) the VM ReplicaSet."
    required: false
    default: "present"
    choices: ["present", "paused", "absent"]
  replicas:
    description:
    - Number of desired pods.
    type: int
    required: false
    default: "1"
  selector:
    description:
    - Label selector for pods.
    - "Existing ReplicaSets whose pods are selected by this will be the ones
      affected by this deployment."
    type: dict
    required: true
notes:
    - And https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
'''

EXAMPLES = '''
- name: Create a VM ReplicaSet
  kubevirt_vmrs:
    name: testvm
    namespace: default
    selector:
      flavor: big

- name: Delete a VM ReplicaSet
  kubevirt_vmrs:
    name: testvm
    namespace: default
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.kubevirt.common import KubeVirtAnsibleModule


def main():
    '''Entry point.'''
    run = KubeVirtAnsibleModule(api_group="virtualmachinereplicasets")
    run.execute_module()


if __name__ == "__main__":
    main()
