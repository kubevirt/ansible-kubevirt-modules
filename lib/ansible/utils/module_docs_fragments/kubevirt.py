#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)


class ModuleDocFragment(object):
    '''Documentation fragments for KubeVirt resource options.'''
    DOCUMENTATION = '''
    version_added: "2.4.x"
    author:
    - KubeVirt Team (@kubevirt)
    options:
      cores:
        description:
        - Number of cores inside the VM.
        type: int
        required: false
        default: "2"
      memory:
        description:
        - Memory to assign to the VM.
        required: false
        type: str
        default: "512M"
      pvc:
        description:
        - "Name of a PersistentVolumeClaim existing in the same namespace
          to use as a base disk for the VM."
        - "**C(pvc) option is required to create the resource.
          It's not needed to remove it.**"
        type: str
        required: false
      cloudinit:
        description:
        - "String containing cloudInit information to pass to the VM.
          It will be encoded as base64."
        required: false
      insecure:
        description:
        - "Disable SSL certificate verification."
        type: bool
        required: false
        default: "no"
      src:
        description:
        - "Local YAML file to use as a source to define the resource.
          It overrides all parameters."
        type: str
        required: false
      labels:
        description:
        - VM attributes to be used as nodeSelector.
        type: dict
        required: false
    notes:
    - Details at https://github.com/kubevirt/kubevirt
    requirements:
    - Kubernetes Python package
'''
