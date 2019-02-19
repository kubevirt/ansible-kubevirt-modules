# -*- coding: utf-8 -*-
#

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections import defaultdict
from distutils.version import Version

from ansible.module_utils.k8s.raw import KubernetesRawModule

from openshift import watch
from openshift.helper.exceptions import KubernetesException

import re

MAX_SUPPORTED_API_VERSION = 'v1alpha3'
API_GROUP = 'kubevirt.io'


VM_COMMON_ARG_SPEC = {
    'merge_type': {'type': 'list', 'choices': ['json', 'merge', 'strategic-merge']},
    'wait': {'type': 'bool', 'default': True},
    'wait_timeout': {'type': 'int', 'default': 120},
    'memory': {'type': 'str'},
    'cpu_cores': {'type': 'int'},
    'disks': {'type': 'list'},
    'labels': {'type': 'dict'},
    'interfaces': {'type': 'list'},
    'machine_type': {'type': 'str'},
    'cloud_init_nocloud': {'type': 'dict'},
}


def virtdict():
    """
    This function create dictionary, with defaults to dictionary.
    """
    return defaultdict(virtdict)


class KubeAPIVersion(Version):
    component_re = re.compile(r'(\d+ | [a-z]+)', re.VERBOSE)

    def __init__(self, vstring=None):
        if vstring:
            self.parse(vstring)

    def parse(self, vstring):
        self.vstring = vstring
        components = [x for x in self.component_re.split(vstring) if x]
        for i, obj in enumerate(components):
            try:
                components[i] = int(obj)
            except ValueError:
                pass

        errmsg = "version '{}' does not conform to kubernetes api versioning guidelines".format(vstring)
        c = components

        if len(c) not in (2, 4) or c[0] != 'v' or not isinstance(c[1], int):
            raise ValueError(errmsg)
        if len(c) == 4 and (c[2] not in ('alpha', 'beta') or not isinstance(c[3], int)):
            raise ValueError(errmsg)

        self.version = components

    def __str__(self):
        return self.vstring

    def __repr__(self):
        return "KubeAPIVersion ('%s')".format(str(self))

    def _cmp(self, other):
        if isinstance(other, str):
            other = KubeAPIVersion(other)

        myver = self.version
        otherver = other.version

        for ver in myver, otherver:
            if len(ver) == 2:
                ver.extend(['zeta', 9999])

        if myver == otherver:
            return 0
        if myver < otherver:
            return -1
        if myver > otherver:
            return 1

    # python2 compatibility
    def __cmp__(self, other):
        return self._cmp(other)


class KubeVirtRawModule(KubernetesRawModule):
    def __init__(self, *args, **kwargs):
        super(KubeVirtRawModule, self).__init__(*args, **kwargs)

    @staticmethod
    def merge_dicts(x, y):
        """
        This function merge two dictionaries, where the first dict has
        higher priority in merging two same keys.
        """
        for k in set(x.keys()).union(y.keys()):
            if k in x and k in y:
                if isinstance(x[k], dict) and isinstance(y[k], dict):
                    yield (k, dict(KubeVirtRawModule.merge_dicts(x[k], y[k])))
                else:
                    yield (k, y[k])
            elif k in x:
                yield (k, x[k])
            else:
                yield (k, y[k])

    def _create_stream(self, resource, namespace, wait_timeout):
        """ Create a stream of events for the object """
        w = None
        stream = None
        try:
            w = watch.Watch()
            w._api_client = self.client.client
            stream = w.stream(resource.get, serialize=False, namespace=namespace, timeout_seconds=wait_timeout)
        except KubernetesException as exc:
            self.fail_json(msg='Failed to initialize watch: {0}'.format(exc.message))
        return w, stream

    def get_resource(self, resource):
        try:
            existing = resource.get(name=self.name, namespace=self.namespace)
        except Exception:
            existing = None

        return existing

    def _define_cloud_init(self, cloud_init_nocloud, template_spec):
        """
        Takes the user's cloud_init_nocloud parameter and fill it in kubevirt
        API strucuture. The name for disk is hardcoded to ansiblecloudinitdisk.
        """
        if cloud_init_nocloud:
            if not template_spec['volumes']:
                template_spec['volumes'] = []
            if not template_spec['domain']['devices']['disks']:
                template_spec['domain']['devices']['disks'] = []

            template_spec['volumes'].append({'name': 'ansiblecloudinitdisk', 'cloudInitNoCloud': cloud_init_nocloud})
            template_spec['domain']['devices']['disks'].append({
                'name': 'ansiblecloudinitdisk',
                'disk': {'bus': 'virtio'},
            })

    def _define_interfaces(self, interfaces, template_spec):
        """
        Takes interfaces parameter of Ansible and create kubevirt API interfaces
        and networks strucutre out from it.
        """
        if interfaces:
            # Extract interfaces k8s specification from interfaces list passed to Ansible:
            spec_interfaces = []
            for i in interfaces:
                spec_interfaces.append({k: v for k, v in i.items() if k != 'network'})
            if 'interfaces' not in template_spec['domain']['devices']:
                template_spec['domain']['devices']['interfaces'] = []
            template_spec['domain']['devices']['interfaces'].extend(spec_interfaces)

            # Extract networks k8s specification from interfaces list passed to Ansible:
            spec_networks = []
            for i in interfaces:
                net = i['network']
                net['name'] = i['name']
                spec_networks.append(net)
            if 'networks' not in template_spec:
                template_spec['networks'] = []
            template_spec['networks'].extend(spec_networks)

    def _define_disks(self, disks, template_spec):
        """
        Takes disks parameter of Ansible and create kubevirt API disks and
        volumes strucutre out from it.
        """
        if disks:
            # Extract k8s specification from disks list passed to Ansible:
            spec_disks = []
            for d in disks:
                spec_disks.append({k: v for k, v in d.items() if k != 'volume'})
            if 'disks' not in template_spec['domain']['devices']:
                template_spec['domain']['devices']['disks'] = []
            template_spec['domain']['devices']['disks'].extend(spec_disks)

            # Extract volumes k8s specification from disks list passed to Ansible:
            spec_volumes = []
            for d in disks:
                volume = d['volume']
                volume['name'] = d['name']
                spec_volumes.append(volume)
            if 'volumes' not in template_spec:
                template_spec['volumes'] = []
            template_spec['volumes'].extend(spec_volumes)

    def find_supported_resource(self, kind):
        results = self.client.resources.search(kind=kind, group=API_GROUP)
        if not results:
            self.fail('Failed to find resource {0} in {1}'.format(kind, API_GROUP))
        sr = sorted(results, key=lambda r: KubeAPIVersion(r.api_version), reverse=True)
        for r in sr:
            if KubeAPIVersion(r.api_version) <= KubeAPIVersion(MAX_SUPPORTED_API_VERSION):
                return r
        self.fail("API versions {0} are too recent. Max supported is {1}/{2}.".format(
            str([r.api_version for r in sr]), API_GROUP, MAX_SUPPORTED_API_VERSION))


    def _construct_vm_definition(self, kind, definition, template, params):
        self.client = self.get_api_client()

        disks = params.get('disks', [])
        memory = params.get('memory')
        cpu_cores = params.get('cpu_cores')
        labels = params.get('labels')
        interfaces = params.get('interfaces')
        cloud_init_nocloud = params.get('cloud_init_nocloud')
        machine_type = params.get('machine_type')
        template_spec = template['spec']

        # Merge additional flat parameters:
        if memory:
            template_spec['domain']['resources']['requests']['memory'] = memory

        if cpu_cores is not None:
            template_spec['domain']['cpu']['cores'] = cpu_cores

        if labels:
            template['metadata']['labels'] = labels

        if machine_type:
            template_spec['domain']['machine']['type'] = machine_type

        # Define cloud init disk if defined:
        self._define_cloud_init(cloud_init_nocloud, template_spec)

        # Define disks
        self._define_disks(disks, template_spec)

        # Define interfaces:
        self._define_interfaces(interfaces, template_spec)

        # Perform create/absent action:
        definition = dict(self.merge_dicts(self.resource_definitions[0], definition))
        resource = self.find_supported_resource(kind)
        return dict(self.merge_dicts(self.resource_definitions[0], definition))

    def construct_vm_definition(self, kind, definition, template):
        definition = self._construct_vm_definition(kind, definition, template, self.params)
        resource = self.find_supported_resource(kind)
        definition = self.set_defaults(resource, definition)
        return resource, definition

    def construct_vm_template_definition(self, kind, definition, template, params):
        definition = self._construct_vm_definition(kind, definition, template, params)
        resource = self.find_resource(kind, definition['apiVersion'], fail=True)

        # Set defaults:
        definition['kind'] = kind
        definition['metadata']['name'] = params.get('name')
        definition['metadata']['namespace'] = params.get('namespace')

        return resource, definition

    def execute_crud(self, kind, definition):
        """ Module execution """
        resource = self.find_supported_resource(kind)
        definition = self.set_defaults(resource, definition)
        return self.perform_action(resource, definition)
