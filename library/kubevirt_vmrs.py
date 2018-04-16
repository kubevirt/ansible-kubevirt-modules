#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vmrs
short_description: Manage KubeVirt VM ReplicaSets
description:
    - Create or delete a KubeVirt VM ReplicaSets
version_added: "2.4.x"
author:
    - KubeVirt Team (@kubevirt)
options:
    state:
        description:
            - "Whether to create (C(present)) or delete (C(absent))
              the VM ReplicaSet."
        required: false
        default: "present"
        choices: ["present", "absent"]
    name:
        description:
            - Name of the VM ReplicaSet.
        required: true
    namespace:
        description:
            - Namespace to add the VM ReplicaSet to or delete from.
        required: true
    replicas:
        description:
            - Number of desired pods.
        type: int
        required: false
        default: '3'
    memory:
        description:
            - Memory to assing to the VM ReplicaSet.
        required: false
        default: "64M"
    image:
        description:
            - Name of the image with the embedded disk.
        required: false
        default: 'kubevirt/cirros-registry-disk-demo:latest'
    label:
        description:
            - Attributes of the VM ReplicaSet.
        type: dict
        required: false
    src:
        description:
            - "Local YAML file to use as a source to define the VM ReplicaSet.
               It overrides all parameters."
        required: false
    insecure:
        description:
            - "Disable SSL certificate verification."
        type: bool
        required: false
        default: "no"notes:
    - Details at https://github.com/kubevirt/kubevirt
    - And https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
requirements:
    - Kubernetes Python package'''

EXAMPLES = '''
- name: Create a VM ReplicaSet
  kubevirt_vmrs:
    name: testvm
    namespace: default
    labels:
      flavor: big

- name: Delete a VM ReplicaSet
  kubevirt_vmrs:
    name: testvm
    namespace: default
    state: absent
'''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible import errors
from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
import yaml

DOMAIN = "kubevirt.io"
VERSION = "v1alpha1"


def build_vmrs_definition(params):
    '''return a dict() containing VM ReplicaSet definition based on params.'''
    vmrs_def = dict()
    vmrs_def["spec"] = dict()
    template = dict()
    template["spec"] = dict()
    domain = dict()
    resources = dict()
    devices = dict()
    devices["disks"] = list()
    disk = dict()
    volumes = list()
    vol = dict()
    metadata = dict()

    disk["volumeName"] = "registryvolume"
    disk["disk"] = dict({"bus": "virtio"})
    disk["name"] = "registrydisk"
    devices["disks"].append(disk)

    resources["requests"] = dict({"memory": params.get("memory")})

    domain["devices"] = devices
    domain["resources"] = resources

    vol["name"] = "registryvolume"
    vol["registryDisk"] = dict({"image": params.get("image")})

    volumes.append(vol)

    template["spec"]["domain"] = domain
    template["spec"]["volumes"] = volumes
    template["metadata"] = dict({"name": params.get("name")})

    metadata["name"] = params.get("name")
    metadata["namespace"] = params.get("namespace")

    vmrs_def["kind"] = "VirtualMachineReplicaSet"
    vmrs_def["apiVersion"] = DOMAIN + "/" + VERSION
    vmrs_def["metadata"] = metadata
    vmrs_def["spec"]["replicas"] = params.get("replicas")

    if params.get("labels") is not None:
        template["metadata"]["labels"] = params.get("labels")
        vmrs_def["spec"]["selector"] = {"matchLabels": params.get("labels")}

    vmrs_def["spec"]["template"] = template

    return vmrs_def


def build_vmrs_from_src(src):
    '''build VM ReplicaSet definition from the source file.'''
    try:
        with open(src) as data:
            try:
                vm_def = yaml.load(data)
            except yaml.scanner.ScannerError as err:
                errors.AnsibleModuleError(str(err))
        if vm_def.get("metadata") is None:
            raise errors.AnsibleModuleError(
                "failed to get metadata from %s" % src)
    except IOError as err:
        raise errors.AnsibleModuleError(
            "Failed while opening %s: %s" % (src, str(err)))
    return vm_def


def create_vmrs(crds, vmrs_def):
    '''create VM ReplicaSet and return API answer.'''
    try:
        metadata = vmrs_def.get("metadata")
        meta = crds.create_namespaced_custom_object(
            DOMAIN, VERSION, metadata.get("namespace"),
            "virtualmachinereplicasets", vmrs_def)
    except ApiException as err:
        raise errors.AnsibleModuleError(
            "Error creating vmrs: %s" % str(err))
    return meta


def delete_vmrs(crds, name, namespace):
    '''delete VM ReplicaSet and return API answer.'''
    try:
        meta = crds.delete_namespaced_custom_object(
            DOMAIN, VERSION, namespace, "virtualmachinereplicasets", name,
            client.V1DeleteOptions())
    except ApiException as err:
        raise errors.AnsibleModuleError("Error deleting vmrs: %s" % str(err))
    return meta


def exists(crds, name, namespace):
    '''return true if the VM ReplicaSet already exists, otherwise false.'''
    all_vmrs = crds.list_cluster_custom_object(
        DOMAIN, VERSION, "virtualmachinereplicasets")["items"]
    vmrss_instance = [
        vmrs for vmrs in all_vmrs if vmrs.get("metadata")["namespace"] ==
        namespace and vmrs.get("metadata")["name"] == name]
    result = True if vmrss_instance else False
    return result


def connect(params):
    '''return CustomObjectsApi object after parsing user options.'''
    config.load_kube_config()
    cfg = Configuration()
    if params.get("insecure"):
        cfg.verify_ssl = False
    api_client = client.ApiClient(configuration=cfg)
    return client.CustomObjectsApi(api_client=api_client)


def main():
    '''Entry point.'''
    argument_spec = {
        "state": {
            "default": "present",
            "choices": ["present", "absent"],
            "type": "str"
        },
        "name": {"required": True, "type": "str"},
        "namespace": {"required": True, "type": "str"},
        "replicas": {"required": False, "type": "int", "default": 3},
        "memory": {"required": False, "type": "str", "default": "64M"},
        "image": {
            "required": False, "type": "str",
            "default": "kubevirt/cirros-registry-disk-demo:latest"},
        "labels": {"required": False, "type": "dict"},
        "src": {"required": False, "type": "str"},
        "insecure": {"required": False, "type": "bool", "default": False}
    }
    module = AnsibleModule(argument_spec=argument_spec)
    crds = connect(module.params)
    src = module.params["src"]

    if src is not None:
        vmrs_def = build_vmrs_from_src(module.params)
    else:
        vmrs_def = build_vmrs_definition(module.params)

    found = exists(crds, module.params["name"], module.params["namespace"])

    if module.params["state"] == "present":
        if found:
            module.exit_json(
                changed=False, skipped=True, meta={"result": "skipped"})

        meta = create_vmrs(crds, vmrs_def)
        module.exit_json(changed=True, skipped=False, meta=meta)
    else:
        if found:
            meta = delete_vmrs(
                crds, module.params["name"], module.params["namespace"])
            module.exit_json(
                changed=True, skipped=False, meta=meta)
        module.exit_json(
            changed=False, skipped=True, meta=dict({"result": "skipped"}))


if __name__ == "__main__":
    main()
