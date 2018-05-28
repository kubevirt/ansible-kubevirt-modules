import pytest
import sys

from ansible.compat.tests.mock import patch

sys.path.append('lib/ansible/module_utils/k8svirt')

import facts

VM_BODY = '''
"kubevirt_vm": {
    "api_version": "kubevirt.io/v1alpha1",
    "kind": "VirtualMachine",
    "metadata": {
        "annotations": {
            "presets.virtualmachines.kubevirt.io/presets-applied": "kubevirt.io/v1alpha1"
        },
        "creation_timestamp": "2018-05-28T16:29:00Z",
        "finalizers": [
            "foregroundDeleteVirtualMachine"
        ],
        "generation": 1,
        "name": "jhendrix",
        "namespace": "vms",
        "resource_version": "177913",
        "self_link": "/apis/kubevirt.io/v1alpha1/namespaces/vms/virtualmachines/jhendrix",
        "uid": "3a3e401f-6294-11e8-b0c9-5254009a8783"
    },
    "spec": {
        "domain": {
            "devices": {
                "disks": [
                    {
                        "disk": {
                            "bus": "virtio"
                        },
                        "name": "mydisk",
                        "volume_name": "myvolume"
                    },
                    {
                        "disk": {
                            "bus": "virtio"
                        },
                        "name": "cloudinitdisk",
                        "volume_name": "cloudinitvolume"
                    }
                ]
            },
            "machine": {},
            "resources": {
                "requests": {
                    "memory": "512M"
                }
            }
        },
        "volumes": [
            {
                "name": "myvolume",
                "persistent_volume_claim": {
                    "claim_name": "fedoravm-pvc"
                }
            },
            {
                "cloud_init_no_cloud": {
                    "user_data_base64": "ICNjbG91ZC1jb25maWcKICAgICAgICAgICBob3N0bmFtZTogamhlbmRyaXgKICAgICAgICAgICB1c2VyczoKICAgICAgICAgICAgIC0gbmFtZToga3ViZXZpcnQKICAgICAgICAgICAgICAgZ2Vjb3M6IEt1YmVWaXJ0IFByb2plY3QKICAgICAgICAgICAgICAgc3VkbzogQUxMPShBTEwpIE5PUEFTU1dEOkFMTAogICAgICAgICAgICAgICBzc2hfYXV0aG9yaXplZF9rZXlzOgogICAgICAgICAgICAgICAgICAgLSBzc2gtcnNhIEFBQUFCM056YUMxeWMyRUFBQUFEQVFBQkFBQUJBUUMrS01wMUY0U3JLaXR2Z0lMZjhRMkdRYmNPc2xJZzRzZnFVT2YrbTgzMnp3b1MyWjJuZG1wci8zRitOdExxNTZjVGFFeks5SVBCSWtOTEpmc1BxUnNUb0xCWVpEK2w0UzVGZnVaMnh3Q3hHQkgrVFZYQXBPK1NpRDZjODRybWpPeDQ3NjY1aVF2TUhLTCtuLzVnVnZTZFlEdWVnTktuajRyUnIvZUhuRzJ5QzRUVlpsM29ISTdUUE9VSlQra0tqU1dQMVVlc1dUWm1tY2szOUlhRlNtb3JnMzFYN2c5aEpId3E5SkVEUWlsY2JuSXlxRFpLaUg2SnU0R2pPVThtcWhhekJGQjRxdS9RRERiMjVwRHBQZDJwUUdCaWxHdm03Z3dKQ1ZueURrOVlaUVU3Z1lFNzM0S0xEZjV0Q0tNbUVRU2p3RngyVGo5bWZadmVDSUprYWozVCBrdWJldmlydAogICAgICAg"
                },
                "name": "cloudinitvolume"
            }
        ]
    },
    "status": {
        "phase": "Scheduling"
    }
}
'''

class TestFacts(object):
    @patch('kubevirt.DefaultApi.read_namespaced_virtual_machine')
    def test_execute_module(mock_read):
        pass
