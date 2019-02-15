# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment(object):

    # Standard oVirt documentation fragment
    DOCUMENTATION = '''
options:
    wait:
        description:
            - "I(True) if the module should wait for the resource to get into desired state."
        default: true
        type: bool
    wait_timeout:
        description:
            - "The amount of time in seconds the module should wait for the resource to get into desired state."
        default: 120
        type: int
    memory:
        description:
            - "The amount of memory to be requested by virtual machine."
            - "For example 1024Mi."
        type: str
    machine_type:
        description:
            - QEMU machine type is the actual chipset of the virtual machine.
        type: str
    cpu_cores:
        description:
            - "Number of CPU cores."
requirements:
    - python >= 2.7
    - openshift >= 0.8.2
notes:
  - "In order to use this module you have to install Openshift Python SDK.
     To ensure it's installed with correct version you can create the following task:
     I(pip: name=openshift version=0.8.2)"
'''
