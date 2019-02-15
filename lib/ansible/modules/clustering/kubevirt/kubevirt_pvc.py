#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''

module: kubevirt_pvc

short_description: Manage PVC on Kubernetes

version_added: "2.8"

author: KubeVirt Team (@kubevirt)

description:
  - Use Openshift Python SDK to manage PVC on Kubernetes
  - Support Containerized Data Importer out of the box

extends_documentation_fragment:
  - k8s_auth_options

options:
  resource_definition:
    description:
    - A partial YAML definition of the PVC object being created/updated. Here you can define Kubernetes
      PVC Resource parameters not covered by this module's parameters.
    - "NOTE: I(resource_definition) has lower priority than module parameters. If you try to define e.g.
      I(metadata.namespace) here, that value will be ignored and I(metadata) used instead."
    aliases:
    - definition
    - inline
    type: dict
  state:
    description:
    - Determines if an object should be created, patched, or deleted. When set to C(present), an object will be
      created, if it does not already exist. If set to C(absent), an existing object will be deleted. If set to
      C(present), an existing object will be patched, if its attributes differ from those specified using
      module options and I(resource_definition).
    default: present
    choices:
    - present
    - absent
  force:
    description:
    - If set to C(True), and I(state) is C(present), an existing object will be replaced.
    default: false
    type: bool
  merge_type:
    description:
    - Whether to override the default patch merge approach with a specific type. By default, the strategic
      merge will typically be used.
    - For example, Custom Resource Definitions typically aren't updatable by the usual strategic merge. You may
      want to use C(merge) if you see "strategic merge patch format is not supported"
    - See U(https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/#use-a-json-merge-patch-to-update-a-deployment)
    - Requires openshift >= 0.6.2
    - If more than one merge_type is given, the merge_types will be tried in order
    - If openshift >= 0.6.2, this defaults to C(['strategic-merge', 'merge']), which is ideal for using the same parameters
      on resource kinds that combine Custom Resources and built-in resources. For openshift < 0.6.2, the default
      is simply C(strategic-merge).
    choices:
    - json
    - merge
    - strategic-merge
    type: list
  name:
    description:
      - Use to specify a PVC object name.
    required: true
    type: str
  namespace:
    description:
      - Use to specify a PVC object namespace.
    required: true
    type: str
  annotations:
    description:
      - Annotations attached to this object.
      - U(https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)
    type: dict
  labels:
    description:
      - Labels attached to this object.
      - U(https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
    type: dict
  selector:
    description:
      - A label query over volumes to consider for binding.
      - U(https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
    type: dict
  access_modes:
    description:
      - accessModes contains the desired access modes the volume should have.
      - More info: U(https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes)
    type: list
  resources:
    description:
      - Resources represents the minimum resources the volume should have.
      - More info: U(https://kubernetes.io/docs/concepts/storage/persistent-volumes#resources)
    type: dict
  storage_class_name:
    description:
      - Name of the StorageClass required by the claim.
      - More info: U(https://kubernetes.io/docs/concepts/storage/persistent-volumes#class-1)
    type: str
  volume_mode:
    description:
      - volumeMode defines what type of volume is required by the claim. Value of Filesystem is implied when not included in claim spec. This is an alpha feature of kubernetes and may change in the future.
    type: str
  volume_name:
    description:
      - volumeName is the binding reference to the PersistentVolume backing this claim.
    type: str
  cdi_content_type:
    description:
      - Defines the content type of data being imported.
      - I(kubevirt) denotes a virtual machine image. (Default)
      - I(archive) denotes a tar archive.
    choices:
      - kubevirt
      - archive
  cdi_import_source:
    description:
      - Defaults to 'http' if missing of invalid.
      - TODO… choices?
  cdi_import_endpoint:
    description:
      - URL with the data. https or https is supported.
  cdi_import_secret_name:
    description:
      - The name of the secret containing credentials for the end point
  clone_request:
    description:
      - TODO
  kind:
    description:
      - Required for compatibility with ansible <2.8. Can't be modified.
    default: PersistentVolumeClaim
    choices:
      - PersistentVolumeClaim

requirements:
  - python >= 2.7
  - openshift >= 0.6.2
'''

EXAMPLES = '''
- name: Create a simple PVC and import data from an external source
  kubevirt_pvc:
    state: present
    name: pvc1
    namespace: default
    data_transfer_type: import
    data_import_endpoint: https://www.source.example/path/of/data/vm.img
    access_modes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 1Gi

- name: Create a simple PVC ready for data upload
  kubevirt_pvc:
    state: present
    name: pvc1
    namespace: default
    data_transfer_type: upload
    access_modes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 1Gi

#- name: Upload data to pvc
#  kubevirt_cdi_upload:
#    target_pvc: pvc1
#    target_namespace: default
#    upload_url: https://10.106.240.87/
#    local_file: /tmp/vm.img

'''

