#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# Apache License, Version 2.0
# (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import copy
import os
import yaml

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.kubevirt.helper import to_snake
from ansible.module_utils.six import iteritems


#try:
#    import kubevirt
#    from kubevirt.rest import ApiException
#    HAS_KUBEVIRTPY = True
#except ImportError:
#    HAS_KUBEVIRTPY = False


class KubeVirtAnsibleModule(AnsibleModule):
    """ Module utils for KubeVirt Ansible modules """
    def __init__(self, *args, **kwargs):
        kwargs['argument_spec'] = self.argspec
        AnsibleModule.__init__(self, *args, **kwargs)

    @property
    def argspec(self):
        raise NotImplementedError()

    def execute_module(self):
        raise NotImplementedError()

    def resource_to_parameters(self, resource):
        """ Converts a resource definition to module parameters """
        parameters = dict()
        for key, value in iteritems(resource):
            if key in ('apiVersion', 'kind', 'status'):
                continue
            elif key == 'metadata' and isinstance(value, dict):
                for meta_key, meta_value in iteritems(value):
                    if meta_key in (
                            'name', 'namespace', 'labels', 'annotations'):
                        parameters[meta_key] = meta_value
            elif key in self.helper.argspec and value is not None:
                parameters[key] = value
            elif isinstance(value, dict):
                self._add_parameter(value, [to_snake(key)], parameters)
        return parameters

    def load_resource_definition(self, src):
        """ Load the requested src path """
        result = None
        path = os.path.normpath(src)
        if not os.path.exists(path):
            self.fail_json(
                msg="Error accessing {0}. Does the file exist?".format(path))
        try:
            result = yaml.safe_load(open(path, 'r'))
        except (IOError, yaml.YAMLError) as exc:
            self.fail_json(
                msg="Error loading resource_definition: {0}".format(exc))
        return result

    def _add_parameter(self, request, path, parameters):
        for key, value in iteritems(request):
            if path:
                param_name = '_'.join(path + [to_snake(key)])
            else:
                param_name = to_snake(key)
            if param_name in self.helper.argspec and value is not None:
                parameters[param_name] = value
            elif isinstance(value, dict):
                continue_path = copy.copy(path) if path else []
                continue_path.append(to_snake(key))
                self._add_parameter(value, continue_path, parameters)
            else:
                self.fail_json(
                    msg=(
                        ("Error parsing resource definition. ",
                         "Encountered {0}, which does not map to a parameter ",
                         "expected by the OpenShift Python module.".format(
                             param_name))
                    )
                )


#        if not HAS_KUBEPY:
#            raise errors.AnsibleModuleError(
#                "This module requires Kubernetes Python client."
#            )
#        self._api_group = kind
#        self.client = None
#        self._found = False
#        self._rsrc_definition = dict()
#        arg_spec = helper.get_spec(self._api_group)
#        self.no_log_values = set()
#        AnsibleModule.__init__(self,
#                               argument_spec=arg_spec,
#                               supports_check_mode=False)
#
#    @property
#    def name(self):
#        '''return resource name.'''
#        return self.params.get("name")
#
#    @property
#    def namespace(self):
#        '''return resource namespace.'''
#        return self.params.get("namespace")
#
#    def _connect(self):
#        '''set self.client to CustomObjectsApi object after parsing
#        user options.'''
#        config.load_kube_config()
#        cfg = Configuration()
#        if self.params.get("insecure"):
#            cfg.verify_ssl = False
#        api_client = client.ApiClient(configuration=cfg)
#        self.client = client.CustomObjectsApi(api_client=api_client)
#
#    def _create(self):
#        '''create resource and return API answer.'''
#        try:
#            meta = self.client.create_namespaced_custom_object(
#                DOMAIN, VERSION, self.namespace,
#                self._api_group, self._rsrc_definition)
#        except ApiException as err:
#            raise errors.AnsibleModuleError(
#                "Error creating resource: %s - %s" %
#                (str(err), str(self.params)))
#        return meta
#
#    def _delete(self):
#        '''delete resource and return API answer.'''
#        try:
#            meta = self.client.delete_namespaced_custom_object(
#                DOMAIN, VERSION, self.namespace, self._api_group, self.name,
#                client.V1DeleteOptions())
#        except ApiException as err:
#            raise errors.AnsibleModuleError(
#                "Error deleting resource: %s" % str(err))
#        return meta
#
#    def _exists(self):
#        '''return true if the resource already exists, otherwise false.'''
#        all_resources = self.client.list_cluster_custom_object(
#            DOMAIN, VERSION, self._api_group)["items"]
#        resource_instance = [
#            resource for resource in all_resources
#            if resource.get("metadata")["namespace"] ==
#            self.namespace and resource.get("metadata")["name"] == self.name]
#        self._found = True if resource_instance else False
#
#    def _build_resource_from_src(self):
#        '''build resource definition from source file.'''
#        src = self.params.get("src")
#        try:
#            with open(src) as data:
#                try:
#                    resource_definition = yaml.load(data)
#                except yaml.scanner.ScannerError as err:
#                    errors.AnsibleModuleError(str(err))
#            if resource_definition.get("metadata") is None:
#                raise errors.AnsibleModuleError(
#                    "failed to get metadata from %s" % src)
#        except IOError as err:
#            raise errors.AnsibleModuleError(
#                "Failed while opening %s: %s" % (src, str(err)))
#        self._rsrc_definition = resource_definition
#
#    def _build_volume_definition(self, pvc, registrydisk):
#        '''build myvolume object with user provided data.'''
#        myvolume = dict()
#        myvolume["volumeName"] = "myvolume"
#        myvolume["name"] = "myvolume"
#        if registrydisk is not None:
#            myvolume["registryDisk"] = dict({"image": registrydisk})
#        elif pvc is not None:
#            myvolume["persistentVolumeClaim"] = dict(
#                {'claimName': pvc})
#        if self._api_group == "virtualmachines":
#            self._rsrc_definition["spec"]["volumes"].append(myvolume)
#        else:
#            template = self._rsrc_definition["spec"]["template"]
#            template["spec"]["volumes"].append(myvolume)
#            del template
#
#    def _build_resource_definition(self):
#        '''return dict() containing the resource definition based on user
#        provided parameters.'''
#        resource_definition = dict()
#        resource_definition["spec"] = dict()
#        domain = dict()
#        resources = dict()
#        devices = dict()
#        devices["disks"] = list()
#        disk = dict()
#        spec = dict()
#        metadata = dict()
#        template = dict()
#        kind = helper.KIND_TRANS.get(self._api_group)
#
#        resources["requests"] = dict({"memory": self.params.get("memory")})
#
#        disk["volumeName"] = "myvolume"
#        disk["disk"] = dict({"bus": "virtio"})
#        disk["name"] = "mydisk"
#        devices["disks"].append(disk)
#
#        domain["resources"] = resources
#        domain["devices"] = devices
#        domain["cpu"] = dict({"cores": self.params.get("cores")})
#        domain["machine"] = dict({"type": "q35"})
#
#        metadata["name"] = self.name
#        metadata["namespace"] = self.namespace
#
#        spec["domain"] = domain
#        spec["volumes"] = list()
#
#        if self.params.get("labels") is not None:
#            metadata["labels"] = self.params.get("labels")
#
#        if kind == "OfflineVirtualMachine":
#            running = True if self.params.get("state") == "running" else False
#            resource_definition["spec"]["running"] = running
#
#        if kind == "VirtualMachineReplicaSet":
#            replicas = self.params.get("replicas")
#            paused = True if self.params.get("state") == "paused" else False
#            resource_definition["spec"]["selector"] = dict(
#                {"matchLabels": self.params.get("selector")})
#            if metadata.get("labels") is None:
#                metadata["labels"] = self.params.get("selector")
#            resource_definition["spec"]["replicas"] = replicas
#            resource_definition["spec"]["paused"] = paused
#
#        if kind == "VirtualMachine":
#            resource_definition["spec"] = spec
#        else:
#            template["spec"] = spec
#            template["metadata"] = metadata
#            resource_definition["spec"]["template"] = template
#
#        resource_definition["kind"] = kind
#        resource_definition["apiVersion"] = DOMAIN + "/" + VERSION
#        resource_definition["metadata"] = metadata
#        self._rsrc_definition = resource_definition
#
#    def _build_cloudinit_definition(self):
#        '''build cloud-init disk and volume objects.'''
#        cloudinit_disk = dict()
#        cloudinit_disk["volumeName"] = "cloudinitvolume"
#        cloudinit_disk["cdrom"] = dict({"readOnly": True, "bus": "sata"})
#        cloudinit_disk["name"] = "cloudinitdisk"
#        user_data_base64 = dict(
#            {"userDataBase64": base64.b64encode(self.params.get("cloudinit"))})
#        cloudinit_volume = dict()
#        cloudinit_volume["cloudInitNoCloud"] = user_data_base64
#        cloudinit_volume["name"] = "cloudinitvolume"
#
#        if self._api_group == "virtualmachines":
#            devs = self._rsrc_definition["spec"]["domain"]["devices"]
#            devs["disks"].append(cloudinit_disk)
#            del devs
#            self._rsrc_definition["spec"]["volumes"].append(cloudinit_volume)
#        else:
#            template = self._rsrc_definition["spec"]["template"]
#            template["spec"]["domain"]["devices"]["disks"].append(
#                cloudinit_disk)
#            template["spec"]["volumes"].append(cloudinit_volume)
#            del template
#
#    def execute_module(self):
#        '''perform the required operations.'''
#        self._connect()
#        self._exists()
#
#        if self.params.get("state") != "absent":
#            if self._found:
#                self.exit_json(
#                    changed=False, skipped=True,
#                    meta=dict({"result": "skipped"}))
#
#            pvc = self.params.get("pvc")
#            src = self.params.get("src")
#            registrydisk = None
#
#            if not helper.validate_data(pvc, registrydisk):
#                self.fail_json(msg="pvc is required when state is present")
#
#            if src is not None:
#                self._build_resource_from_src()
#            else:
#                self._build_resource_definition()
#                self._build_volume_definition(pvc, registrydisk)
#
#                if self.params.get("cloudinit") is not None:
#                    self._build_cloudinit_definition()
#
#            meta = self._create()
#
#            self.exit_json(changed=True, skipped=False, meta=meta)
#
#        # state = absent
#        if self._found:
#            meta = self._delete()
#            self.exit_json(changed=True, skipped=False, meta=meta)
#        self.exit_json(
#            changed=False, skipped=True, meta=dict({"result": "skipped"}))

