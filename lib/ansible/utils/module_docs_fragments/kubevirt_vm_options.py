# -*- coding: utf-8 -*-                                                           
#                                                                                 
                                                                                  
# Copyright (c) 2018, KubeVirt Team <@kubevirt>                                   
# Apache License, Version 2.0                                                     
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0) 


class ModuleDocFragment(object):

    # Standard oVirt documentation fragment
    DOCUMENTATION = '''
options:
    wait:
        description:
            - "I(True) if the module should wait for the resource to get into desired state."
        default: true
        type: bool
    disks:
        description:
            - List of dictionaries which specify disks of the virtual machine.
            - A disk can be made accessible via four different types: I(disk), I(lun), I(cdrom), I(floppy).
            - All possible configuration options are available in U(https://kubevirt.io/api-reference/master/definitions.html#_v1_disk)
            - Each disk must have specified a I(volume) that declares which volume type of the disk
              All possible configuration options of volume are available in U(https://kubevirt.io/api-reference/master/definitions.html#_v1_volume).
        type: list
    labels:
        description:
            - Labels are key/value pairs that are attached to virtual machines. Labels are intended to be used to
              specify identifying attributes of virtual machines that are meaningful and relevant to users, but do not directly
              imply semantics to the core system. Labels can be used to organize and to select subsets of virtual machines.
              Labels can be attached to virtual machines at creation time and subsequently added and modified at any time.
            - More on labels that are used for internal implementation U(https://kubevirt.io/user-guide/#/misc/annotations_and_labels)
        type: dict
    interfaces:
        description:
            - An interface defines a virtual network interface of a virtual machine (also called a frontend).
            - All possible configuration options interfaces are available in U(https://kubevirt.io/api-reference/master/definitions.html#_v1_interface)
            - Each interface must have specified a I(network) that declares which logical or physical device it is connected to (also called as backend).
              All possible configuration options of network are available in U(https://kubevirt.io/api-reference/master/definitions.html#_v1_network).
        type: list
    cloud_init_nocloud:
        description:
            - Represents a cloud-init NoCloud user-data source. The NoCloud data will be added
              as a disk to the virtual machine. A proper cloud-init installation is required inside the guest.
              More info: U(https://kubevirt.io/api-reference/master/definitions.html#_v1_cloudinitnocloudsource)
        type: dict
extends_documentation_fragment:
    - kubevirt_common_options
'''
