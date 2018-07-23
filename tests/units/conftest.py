import pytest
import json
import kubevirt

USER_VMI = '''
{
    "apiVersion": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachineInstance",
    "metadata": {
        "name": "jhendrix",
        "namespace": "vms"
    },
    "spec": {
        "domain": {
            "resources": {
                "requests": {
                    "memory": "1024M"
                }
            },
            "devices": {
                "disks": [
                    {
                        "volumeName": "myvolume",
                        "name": "mydisk",
                        "disk": {
                            "bus": "virtio"
                        }
                    },
                    {
                        "name": "cloudinitdisk",
                        "volumeName": "cloudinitvolume",
                        "disk": {
                            "bus": "virtio"
                        }
                    }
                ]
            }
        },
        "volumes": [
            {
                "volumeName": "myvolume",
                "name": "myvolume",
                "persistentVolumeClaim": {
                    "claimName": "fedoravm-pvc"
                }
            },
            {
                "cloudInitNoCloud": {
                    "userDataBase64": "ICNjbG91ZC1jb25maWcKICAgICAgICAgICBob3N0bmFtZTogamhlbmRyaXgKICAgICAgICAgICB1c2VyczoKICAgICAgICAgICAgIC0gbmFtZToga3ViZXZpcnQKICAgICAgICAgICAgICAgZ2Vjb3M6IEt1YmVWaXJ0IFByb2plY3QKICAgICAgICAgICAgICAgc3VkbzogQUxMPShBTEwpIE5PUEFTU1dEOkFMTAogICAgICAgICAgICAgICBzc2hfYXV0aG9yaXplZF9rZXlzOgogICAgICAgICAgICAgICAgICAgLSBzc2gtcnNhIEFBQUFCM056YUMxeWMyRUFBQUFEQVFBQkFBQUJBUUMrS01wMUY0U3JLaXR2Z0lMZjhRMkdRYmNPc2xJZzRzZnFVT2YrbTgzMnp3b1MyWjJuZG1wci8zRitOdExxNTZjVGFFeks5SVBCSWtOTEpmc1BxUnNUb0xCWVpEK2w0UzVGZnVaMnh3Q3hHQkgrVFZYQXBPK1NpRDZjODRybWpPeDQ3NjY1aVF2TUhLTCtuLzVnVnZTZFlEdWVnTktuajRyUnIvZUhuRzJ5QzRUVlpsM29ISTdUUE9VSlQra0tqU1dQMVVlc1dUWm1tY2szOUlhRlNtb3JnMzFYN2c5aEpId3E5SkVEUWlsY2JuSXlxRFpLaUg2SnU0R2pPVThtcWhhekJGQjRxdS9RRERiMjVwRHBQZDJwUUdCaWxHdm03Z3dKQ1ZueURrOVlaUVU3Z1lFNzM0S0xEZjV0Q0tNbUVRU2p3RngyVGo5bWZadmVDSUprYWozVCBrdWJldmlydAogICAgICAg"
                },
                "name": "cloudinitvolume"
            }
        ]
    }
}
'''

VMI_BODY = '''
{
    "api_version": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachineInstance",
    "metadata": {
        "annotations": {
            "presets.virtualmachineinstances.kubevirt.io/presets-applied": "kubevirt.io/v1alpha2"
        },
        "creation_timestamp": "2018-05-28T16:29:00Z",
        "finalizers": [
            "foregroundDeleteVirtualMachine"
        ],
        "generation": 1,
        "name": "jhendrix",
        "namespace": "vms",
        "resource_version": "177913",
        "self_link": "/apis/kubevirt.io/v1alpha1/namespaces/vms/virtualmachineinstances/jhendrix",
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

USER_VM = '''
{
    "apiVersion": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachine",
    "metadata": {
        "name": "baldr",
        "namespace": "vms",
        "labels": {
            "kubevirt.io/vm": "baldr"
        }
    },
    "spec": {
        "running": true,
        "template": {
            "metadata": {
                "labels": {
                    "kubevirt.io/vm": "baldr"
                }
            },
            "spec": {
                "domain": {
                    "resources": {
                        "requests": {
                            "memory": "512M"
                        }
                    },
                    "devices": {
                        "disks": [
                            {
                                "volumeName": "myvolume",
                                "name": "mydisk",
                                "disk": {
                                    "bus": "virtio"
                                }
                            },
                            {
                                "name": "cloudinitdisk",
                                "volumeName": "cloudinitvolume",
                                "disk": {
                                    "bus": "virtio"
                                }
                            }
                        ]
                    }
                },
                "volumes": [
                    {
                        "volumeName": "myvolume",
                        "name": "myvolume",
                        "persistentVolumeClaim": {
                            "claimName": "fedoravm-pvc"
                        }
                    },
                    {
                        "cloudInitNoCloud": {
                            "userDataBase64": "ICNjbG91ZC1jb25maWcKICAgICAgICAgICBob3N0bmFtZTogamhlbmRyaXgKICAgICAgICAgICB1c2VyczoKICAgICAgICAgICAgIC0gbmFtZToga3ViZXZpcnQKICAgICAgICAgICAgICAgZ2Vjb3M6IEt1YmVWaXJ0IFByb2plY3QKICAgICAgICAgICAgICAgc3VkbzogQUxMPShBTEwpIE5PUEFTU1dEOkFMTAogICAgICAgICAgICAgICBzc2hfYXV0aG9yaXplZF9rZXlzOgogICAgICAgICAgICAgICAgICAgLSBzc2gtcnNhIEFBQUFCM056YUMxeWMyRUFBQUFEQVFBQkFBQUJBUUMrS01wMUY0U3JLaXR2Z0lMZjhRMkdRYmNPc2xJZzRzZnFVT2YrbTgzMnp3b1MyWjJuZG1wci8zRitOdExxNTZjVGFFeks5SVBCSWtOTEpmc1BxUnNUb0xCWVpEK2w0UzVGZnVaMnh3Q3hHQkgrVFZYQXBPK1NpRDZjODRybWpPeDQ3NjY1aVF2TUhLTCtuLzVnVnZTZFlEdWVnTktuajRyUnIvZUhuRzJ5QzRUVlpsM29ISTdUUE9VSlQra0tqU1dQMVVlc1dUWm1tY2szOUlhRlNtb3JnMzFYN2c5aEpId3E5SkVEUWlsY2JuSXlxRFpLaUg2SnU0R2pPVThtcWhhekJGQjRxdS9RRERiMjVwRHBQZDJwUUdCaWxHdm03Z3dKQ1ZueURrOVlaUVU3Z1lFNzM0S0xEZjV0Q0tNbUVRU2p3RngyVGo5bWZadmVDSUprYWozVCBrdWJldmlydAogICAgICAg"
                        },
                        "name": "cloudinitvolume"
                    }
                ]
            }
        }
    }
}
'''

VM_BODY = '''
{
    "api_version": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachine",
    "metadata": {
        "creation_timestamp": "2018-05-29T16:20:14Z",
        "generation": 1,
        "labels": {
            "kubevirt.io/vm": "baldr"
        },
        "name": "baldr",
        "namespace": "vms",
        "resource_version": "270363",
        "self_link": "/apis/kubevirt.io/v1alpha2/namespaces/vms/virtualmachines/baldr",
        "uid": "2b2e31cc-635c-11e8-9b52-5254009a8783"
    },
    "spec": {
        "running": true,
        "template": {
            "metadata": {
                "labels": {
                    "kubevirt.io/vm": "baldr"
                }
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
            }
        }
    },
    "status": {
        "created": true,
        "ready": true
    }
}
'''


USER_VMIRS = '''
{
    "apiVersion": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachineInstanceReplicaSet",
    "metadata": {
        "name": "freyja",
        "namespace": "vms"
    },
    "spec": {
        "replicas": 2,
        "selector": {
            "matchLabels": {
                "rs": "freyjars"
            }
        },
        "template": {
            "metadata": {
                "name": "freyja",
                "labels": {
                    "rs": "freyjars"
                }
            },
            "spec": {
                "domain": {
                    "resources": {
                        "requests": {
                            "memory": "512M"
                        }
                    },
                    "devices": {
                        "disks": [
                            {
                                "volumeName": "myvolume",
                                "name": "mydisk",
                                "disk": {
                                    "bus": "virtio"
                                }
                            },
                            {
                                "name": "cloudinitdisk",
                                "volumeName": "cloudinitvolume",
                                "disk": {
                                    "bus": "virtio"
                                }
                            }
                        ]
                    }
                },
                "volumes": [
                    {
                        "volumeName": "myvolume",
                        "name": "myvolume",
                        "persistentVolumeClaim": {
                            "claimName": "fedoravm-pvc"
                        }
                    },
                    {
                        "name": "cloudinitvolume",
                        "cloudInitNoCloud": {
                            "userDataBase64": "ICNjbG91ZC1jb25maWcKICAgICAgICAgICBob3N0bmFtZTogamhlbmRyaXgKICAgICAgICAgICB1c2VyczoKICAgICAgICAgICAgIC0gbmFtZToga3ViZXZpcnQKICAgICAgICAgICAgICAgZ2Vjb3M6IEt1YmVWaXJ0IFByb2plY3QKICAgICAgICAgICAgICAgc3VkbzogQUxMPShBTEwpIE5PUEFTU1dEOkFMTAogICAgICAgICAgICAgICBzc2hfYXV0aG9yaXplZF9rZXlzOgogICAgICAgICAgICAgICAgICAgLSBzc2gtcnNhIEFBQUFCM056YUMxeWMyRUFBQUFEQVFBQkFBQUJBUUMrS01wMUY0U3JLaXR2Z0lMZjhRMkdRYmNPc2xJZzRzZnFVT2YrbTgzMnp3b1MyWjJuZG1wci8zRitOdExxNTZjVGFFeks5SVBCSWtOTEpmc1BxUnNUb0xCWVpEK2w0UzVGZnVaMnh3Q3hHQkgrVFZYQXBPK1NpRDZjODRybWpPeDQ3NjY1aVF2TUhLTCtuLzVnVnZTZFlEdWVnTktuajRyUnIvZUhuRzJ5QzRUVlpsM29ISTdUUE9VSlQra0tqU1dQMVVlc1dUWm1tY2szOUlhRlNtb3JnMzFYN2c5aEpId3E5SkVEUWlsY2JuSXlxRFpLaUg2SnU0R2pPVThtcWhhekJGQjRxdS9RRERiMjVwRHBQZDJwUUdCaWxHdm03Z3dKQ1ZueURrOVlaUVU3Z1lFNzM0S0xEZjV0Q0tNbUVRU2p3RngyVGo5bWZadmVDSUprYWozVCBrdWJldmlydAogICAgICAg"
                        }
                    }
                ]
            }
        }
    }
}
'''

VMIRS_BODY = '''
{
    "api_version": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachineInstanceReplicaSet",
    "metadata": {
        "creation_timestamp": "2018-05-29T16:37:20Z",
        "generation": 1,
        "name": "freyja",
        "namespace": "vms",
        "resource_version": "272140",
        "self_link": "/apis/kubevirt.io/v1alpha2/namespaces/vms/virtualmachineinstancereplicasets/freyja",
        "uid": "8eac7d2c-635e-11e8-9b52-5254009a8783"
    },
    "spec": {
        "replicas": 2,
        "selector": {
            "match_labels": {
                "rs": "freyjars"
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "rs": "freyjars"
                },
                "name": "freyja"
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
            }
        }
    },
    "status": {
        "replicas": 2
    }
}
'''

USER_VMIPS = '''
{
    "apiVersion": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachineInstancePreset",
    "metadata": {
        "name": "vmps-small"
    },
    "spec": {
        "domain": {
            "resources": {
                "requests": {
                    "memory": "1024M"
                }
            },
            "devices": {
                "disks": [
                    {
                        "volumeName": "myvolume",
                        "name": "mydisk",
                        "disk": {
                            "bus": "virtio"
                        }
                    }
                ]
            }
        },
        "selector": {
            "matchLabels": {
                "kubevirt.io/vmPreset": "vmps-small"
            }
        }
    }
}
'''

VMIPS_BODY = '''
{
    "api_version": "kubevirt.io/v1alpha2",
    "kind": "VirtualMachineInstancePreset",
    "metadata": {
        "creation_timestamp": "2018-06-01T17:13:03Z",
        "generation": 1,
        "name": "vmps-small",
        "namespace": "vms",
        "resource_version": "20928",
        "self_link": "/apis/kubevirt.io/v1alpha1/namespaces/vms/virtualmachineinstancepresets/vmps-small",
        "uid": "0ad9edf0-65bf-11e8-b964-52540024b209"
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
                    }
                ]
            },
            "resources": {
                "requests": {
                    "memory": "512M"
                }
            }
        },
        "selector": {
            "match_labels": {
                "kubevirt.io/vmPreset": "vmps-small"
            }
        }
    }
}
'''


@pytest.fixture(scope='module')
def args_present():
    """ yield basic argument_spec for state present """
    args = dict(
        state='present', kind='VirtualMachineInstance',
        name='testvm', namespace='vms')
    yield args
    del args


@pytest.fixture(scope='module')
def args_absent():
    """ yield basic argument_spec for state absent """
    args = dict(
        state='absent', kind='VirtualMachineInstance',
        name='testvm', namespace='vms')
    yield args
    del args


@pytest.fixture(scope='module')
def user_vmi():
    json_dict = json.loads(USER_VMI)
    vm = kubevirt.V1VirtualMachineInstance(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec'),
        status=json_dict.get('status')
    )
    yield vm
    del vm


@pytest.fixture(scope='module')
def user_vm():
    json_dict = json.loads(USER_VM)
    vm = kubevirt.V1VirtualMachine(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec'),
        status=json_dict.get('status')
    )
    yield vm
    del vm


@pytest.fixture(scope='module')
def user_vmirs():
    json_dict = json.loads(USER_VMIRS)
    vmirs = kubevirt.V1VirtualMachineInstanceReplicaSet(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec'),
        status=json_dict.get('status')
    )
    yield vmirs
    del vmirs


@pytest.fixture(scope='module')
def user_vmips():
    json_dict = json.loads(USER_VMIPS)
    vmips = kubevirt.V1VirtualMachineInstancePreset(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec')
    )
    yield vmips
    del vmips


@pytest.fixture(scope='module')
def json_to_vmi():
    json_dict = json.loads(VMI_BODY)
    vmi = kubevirt.V1VirtualMachineInstance(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec'),
        status=json_dict.get('status')
    )
    yield vmi
    del vmi


@pytest.fixture(scope='module')
def json_to_vm():
    json_dict = json.loads(VM_BODY)
    vm = kubevirt.V1VirtualMachine(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec'),
        status=json_dict.get('status')
    )
    yield vm
    del vm


@pytest.fixture(scope='module')
def json_to_vmirs():
    json_dict = json.loads(VMIRS_BODY)
    vmirs = kubevirt.V1VirtualMachineInstanceReplicaSet(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec'),
        status=json_dict.get('status')
    )
    yield vmirs
    del vmirs


@pytest.fixture(scope='module')
def json_to_vmips():
    json_dict = json.loads(VMIPS_BODY)
    vmips = kubevirt.V1VirtualMachineInstancePreset(
        api_version=json_dict.get('api_version'),
        kind=json_dict.get('kind'),
        metadata=json_dict.get('metadata'),
        spec=json_dict.get('spec')
    )
    yield vmips
    del vmips


def pytest_configure(config):
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys
    del sys._called_from_test
