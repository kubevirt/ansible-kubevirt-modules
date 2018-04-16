#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kubevirt_vm
short_description: Manage KubeVirt Offline VirtualMachines
description:
    - Create or delete a KubeVirt Offline VirtualMachine
version_added: "2.4.x"
author:
    - KubeVirt Team (@kubevirt)
options:
    state:
        description:
            - "Whether to create (C(present)) or delete (C(absent))
              the Offline VM."
        required: false
        default: "present"
        choices: ["present", "absent"]
    name:
        description:
            - Name of the Offline VM.
        required: true
    namespace:
        description:
            - Namespace to add the Offline VM to or delete from.
        required: true
    wait:
        description:
            - Wait for the Offline VM to start running.
        type: bool
        required: false
        default: 'no'
    timeout:
        description:
            - Maximum number of seconds to wait for.
        type: int
        required: false
        default: "20"
    cores:
        description:
            - Number of cores inside the Offline VM.
        type: int
        required: false
        default: "2"
    memory:
        description:
            - Memory to assign to the Offline VM.
        required: false
        default: "512M"
    registrydisk:
        description:
            - Name of a base disk for the Offline VM.
        required: false
        choices:
            - 'kubevirt/alpine-registry-disk-demo'
            - 'kubevirt/cirros-registry-disk-demo'
            - 'kubevirt/fedora-cloud-registry-disk-demo'
    pvc:
        description:
            - "Name of a PersistentVolumeClaim existing in the same namespace
              to use as a base disk for the Offline VM."
        required: false
    src:
        description:
            - "Local YAML file to use as a source to define the Offline VM.
              It overrides all parameters."
        required: false
    cloudinit:
        description:
            - "String containing cloudInit information to pass to
              the Offline VM. It will be encoded as base64."
        required: false
notes:
    - Details at https://github.com/kubevirt/kubevirt
requirements:
    - Kubernetes Python package'''

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

from ansible.module_utils.basic import AnsibleModule
from ansible import errors
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import base64
import time
import yaml

DOMAIN = "kubevirt.io"
VERSION = 'v1alpha1'
REGISTRYDISKS = [
    'kubevirt/alpine-registry-disk-demo',
    'kubevirt/cirros-registry-disk-demo',
    'kubevirt/fedora-cloud-registry-disk-demo']


def build_ovm_definition(params):
    '''build Offline VM from params.'''
    ovm_def = dict()
    ovm_def["spec"] = dict()
    spec = dict()
    domain = dict()
    resources = dict()
    devices = dict()
    devices["disks"] = list()
    disk = dict()
    metadata = dict()
    template = dict()

    resources["requests"] = dict()
    resources["requests"]["memory"] = params.get("memory")

    disk["volumeName"] = "myvolume"
    disk["disk"] = dict({"bus": "virtio"})
    disk["name"] = "mydisk"
    devices["disks"].append(disk)

    domain["resources"] = resources
    domain["devices"] = devices
    domain["cpu"] = dict({"cores": params.get("cores")})
    domain["machine"] = dict({'type': 'q35'})

    spec["domain"] = domain
    spec["volumes"] = list()

    template["spec"] = spec
    template["metadata"] = dict()

    metadata["annotations"] = dict()
    metadata["name"] = params.get("name")
    metadata["namespace"] = params.get("namespace")

    ovm_def["kind"] = "OfflineVirtualMachine"
    ovm_def["apiVersion"] = DOMAIN + "/" + VERSION
    ovm_def["spec"]["template"] = template
    ovm_def["spec"]["running"] = True
    ovm_def["metadata"] = metadata

    return ovm_def


def wait(crds, params):
    '''wait for the VM to be running.'''
    waittime = 0
    name = params.get("name")
    namespace = params.get("namespace")
    timeout = params.get("timeout")
    while True:
        currentstatus = status(crds, name, namespace)
        if currentstatus == 'Running':
            return True
        elif currentstatus == 'Not Found':
            return False
        elif waittime > timeout:
            return False
        else:
            waittime += 5
            time.sleep(5)


def build_volume_definition(pvc, registrydisk):
    '''build myvolume object with user provided data.'''
    myvolume = dict()
    myvolume["volumeName"] = "myvolume"
    myvolume["name"] = "myvolume"
    if registrydisk is not None:
        myvolume["registryDisk"] = dict({"image": registrydisk})
    elif pvc is not None:
        myvolume["persistentVolumeClaim"] = dict(
            {'claimName': pvc})
    return myvolume


def build_cloudinitdisk_definition():
    '''return cloudinitdisk dictionary.'''
    cloudinitdisk = dict()
    cloudinitdisk["volumeName"] = "cloudinitvolume"
    cloudinitdisk["cdrom"] = dict({"readOnly": True})
    cloudinitdisk["name"] = "cloudinitdisk"
    return cloudinitdisk


def build_cloudinitvol_definition(user_data):
    '''return cloudinitvolume dictionary.'''
    user_data_base64 = dict(
        {"userDataBase64": base64.b64encode(user_data)})
    cloudinitvolume = dict()
    cloudinitvolume["cloudInitNoCloud"] = user_data_base64
    cloudinitvolume["name"] = "cloudinitvolume"
    return cloudinitvolume


def validate_data(pvc, registrydisk):
    '''validate required that cannot be defined as required.'''
    if pvc is None and registrydisk is None:
        return False
    return True


def build_ovm_from_src(src):
    '''build Offline VM definition from source file.'''
    try:
        with open(src) as data:
            try:
                ovm_def = yaml.load(data)
            except yaml.scanner.ScannerError as err:
                raise errors.AnsibleModuleError(
                    "failed while parsing source file %s: %s"
                    % (src, str(err)))
        if ovm_def.get("metadata") is None:
            raise errors.AnsibleModuleError(
                "failed to get metadata from %s" % src)
    except IOError as err:
        raise errors.AnsibleModuleError(
            "failed while opening %s: %s" % (src, str(err)))
    return ovm_def


def create_ovm(crds, ovm_def):
    '''create offline vm and returns API answer.'''
    metadata = ovm_def.get("metadata")
    try:
        meta = crds.create_namespaced_custom_object(
            DOMAIN, VERSION, metadata.get("namespace"),
            "offlinevirtualmachines", ovm_def)
    except ApiException as err:
        raise errors.AnsibleModuleError("Error creating offline vm: %s" % err)
    return meta


def delete_ovm(crds, name, namespace):
    '''delete vm and returns API answer.'''
    try:
        meta = crds.delete_namespaced_custom_object(
            DOMAIN, VERSION, namespace, 'offlinevirtualmachines', name,
            client.V1DeleteOptions())
    except ApiException as err:
        raise errors.AnsibleModuleError("Error deleting vm: %s" % str(err))
    return meta


def exists(crds, name, namespace):
    '''return true if the offline virtual machine already exists, otherwise
    false.'''
    all_ovms = crds.list_cluster_custom_object(
        DOMAIN, VERSION, 'offlinevirtualmachines')["items"]
    ovms = [
        ovm for ovm in all_ovms if ovm.get("metadata")["namespace"] ==
        namespace and ovm.get("metadata")["name"] == name
    ]
    result = True if ovms else False
    return result


def status(crds, name, namespace):
    '''returns the current state of the offline virtual machine.'''
    try:
        ovm_instance = crds.get_namespaced_custom_object(
            DOMAIN, VERSION, namespace, 'offlinevirtualmachines', name)
        return ovm_instance['status']['phase']
    except ApiException as err:
        return err


def main():
    '''Entry point.'''
    argument_spec = {
        "state": {
            "default": "present",
            "choices": ['present', 'absent'],
            "type": 'str'
        },
        "name": {"required": True, "type": "str"},
        "namespace": {"required": True, "type": "str"},
        "wait": {"required": False, "type": "bool", "default": False},
        "timeout": {"required": False, "type": "int", "default": 20},
        "cores": {"required": False, "type": "int", "default": 2},
        "memory": {"required": False, "type": "str", "default": '512M'},
        "registrydisk": {
            "required": False, "type": "str", 'choices': REGISTRYDISKS},
        "pvc": {"required": False, "type": "pvc"},
        "src": {"required": False, "type": "str"},
        "cloudinit": {"required": False, "type": "str"}
    }
    module = AnsibleModule(argument_spec=argument_spec)
    config.load_kube_config()
    crds = client.CustomObjectsApi()
    registrydisk = module.params['registrydisk']
    pvc = module.params['pvc']
    src = module.params['src']

    if not validate_data(pvc, registrydisk):
        module.fail_json(msg="Either pvc or registrydisk is required")

    if src is not None:
        ovm_def = build_ovm_from_src(src)
    else:
        ovm_def = build_ovm_definition(module.params)
        ovm_def["spec"]["template"]["spec"]["volumes"].append(
            build_volume_definition(pvc, registrydisk))
        if module.params["cloudinit"] is not None:
            template = ovm_def["spec"]["template"]
            template["spec"]["domain"]["devices"]["disks"].append(
                build_cloudinitdisk_definition())
            template["spec"]["volumes"].append(
                build_cloudinitvol_definition(module.params["cloudinit"]))
            del template

    found = exists(crds, module.params["name"], module.params["namespace"])

    if module.params["state"] == 'present':
        if found:
            module.exit_json(
                chaged=False, skipped=True, meta={"result": "skipped"})

        meta = create_ovm(crds, ovm_def)
        if module.params["wait"]:
            if not wait(crds, module.params):
                module.fail_json(
                    msg="Timed out waiting for the Offline VM")
        module.exit_json(changed=True, skipped=False, meta=meta)

    else:
        if found:
            meta = delete_ovm(
                crds, module.params["name"], module.params["namespace"])
            module.exit_json(changed=True, skipped=False, meta=meta)

        module.exit_json(
            changed=False, skipped=True, meta=dict({"result": "skipped"}))


if __name__ == '__main__':
    main()
