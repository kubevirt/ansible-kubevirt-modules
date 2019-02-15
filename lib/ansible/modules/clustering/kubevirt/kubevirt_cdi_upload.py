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

module: kubevirt_cdi_upload

short_description: Upload local VM images to CDI Upload Proxy.

version_added: "2.8"

author: KubeVirt Team (@kubevirt)


description:
  - Use Openshift Python SDK to create UploadTokenRequest objects.
  - Transfer contents of local files to the CDI Upload Proxy.

extends_documentation_fragment:
  - k8s_auth_options

options:
  pvc_name:
    description:
      - Use to specify the name of the target PersistentVolumeClaim.
    required: true
  pvc_namespace:
    description:
      - Use to specify the namespace of the target PersistentVolumeClaim.
    required: true
  upload_host:
    description:
      - URL containing the host and port on which the CDI Upload Proxy is available.
      - More info: U(https://github.com/kubevirt/containerized-data-importer/blob/master/doc/upload.md#expose-cdi-uploadproxy-service)
  upload_host_verify_ssl:
    description:
      - Whether or not to verify the CDI Upload Proxy's SSL certificates against Mozilla's CA Bundle.
    default: true
    type: bool
  path:
    description:
      - Path of local image file to transfer.
  kind:
    description:
      - Required for compatibility with ansible <2.8. Can't be modified.
    default: UploadTokenRequest
    choices:
      - UploadTokenRequest
  api_version:
    description:
      - Required for compatibility with ansible <2.8. Can't be modified.
    default: upload.cdi.kubevirt.io/v1alpha1
    choices:
      - upload.cdi.kubevirt.io/v1alpha1
  src:
    description:
      - Required for compatibility with ansible <2.8. Don't use.
  resource_definition:
    description:
      - Required for compatibility with ansible <2.8. Don't use.
  merge_type:
    description:
      - Required for compatibility with ansible <2.8. Don't use.
  name:
    description:
      - Required for compatibility with ansible <2.8. Don't use.
  namespace:
    description:
      - Required for compatibility with ansible <2.8. Don't use.

Notes:
  - Mozilla's CA bundle is provided by pip's "certifi" package.

requirements:
  - python >= 2.7
  - openshift >= 0.8.2
  - requests >= 2.0.0
'''

EXAMPLES = '''
- name: Upload local image to pvc-vm1
  kubevirt_cdi_upload:
    pvc_namespace: default
    pvc_name: pvc-vm1
    upload_host: https://localhost:8443
    upload_host_verify_ssl: false
    path: /tmp/cirros-0.4.0-x86_64-disk.img
'''

RETURN = '''# '''

import copy
import traceback
import requests

from collections import defaultdict

from ansible.module_utils.k8s.common import AUTH_ARG_SPEC
from ansible.module_utils.k8s.raw import KubernetesRawModule


SERVICE_ARG_SPEC = {
    'pvc_name': {'required': True},
    'pvc_namespace': {'required': True},
    'upload_host': {'required': True},
    'upload_host_verify_ssl': {
        'type': 'bool',
        'default': True
    },
    'path': {'required': True},
    # Workaround for ansible <2.8
    'kind': {
        'default': 'UploadTokenRequest',
        'choices': ['UploadTokenRequest'],
    },
    'api_version': {
        'default': 'upload.cdi.kubevirt.io/v1alpha1',
        'choices': ['upload.cdi.kubevirt.io/v1alpha1'],
    },
    'name': {
        'default': None,
    },
    'namespace': {
        'default': None,
    },
    'src': {
        'default': None,
    },
    'resource_definition': {
        'default': None,
    },
    'merge_type': {
        'type': 'list',
    }
}


class KubeVirtCDIUpload(KubernetesRawModule):
    def __init__(self, *args, **kwargs):
        super(KubeVirtCDIUpload, self).__init__(*args, **kwargs)

    @property
    def argspec(self):
        """ argspec property builder """
        argument_spec = copy.deepcopy(AUTH_ARG_SPEC)
        argument_spec.update(SERVICE_ARG_SPEC)
        return argument_spec

    def execute_module(self):
        """ Module execution """

        API = 'v1alpha1'
        KIND = 'UploadTokenRequest'

        self.client = self.get_api_client()

        api_version = 'upload.cdi.kubevirt.io/{}'.format(API)
        pvc_name = self.params.get('pvc_name')
        pvc_namespace = self.params.get('pvc_namespace')
        upload_host = self.params.get('upload_host')
        upload_host_verify_ssl = self.params.get('upload_host_verify_ssl')
        path = self.params.get('path')

        definition = defaultdict(defaultdict)

        definition['kind'] = KIND
        definition['apiVersion'] = api_version

        def_meta = definition['metadata']
        def_meta['name'] = pvc_name
        def_meta['namespace'] = pvc_namespace

        def_spec = definition['spec']
        def_spec['pvcName'] = pvc_name

        # Let's check the file's there before we do anything else
        imgfile = open(path, 'rb')
        # TODO: file format verification before uploading?

        resource = self.find_resource(KIND, api_version, fail=True)
        definition = self.set_defaults(resource, definition)
        result = self.perform_action(resource, definition)

        headers = {'Authorization': "Bearer {}".format(result['result']['status']['token'])}
        files = {'file': imgfile}
        url = "{}/{}/upload".format(upload_host, API)
        requests.post(url, files=files, headers=headers, verify=upload_host_verify_ssl)

        self.exit_json(changed=True)


def main():
    module = KubeVirtCDIUpload()
    try:
        module.execute_module()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
