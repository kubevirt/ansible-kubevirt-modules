# Ansible KubeVirt Modules

[Ansible](https://github.com/ansible/ansible) modules for [KubeVirt](https://github.com/kubevirt/kubevirt) management.

## Contents

- `lib`: Ansible modules files for KubeVirt management
- `tests`: Ansible playbook examples and unit tests

## Requirements

- Ansible >= 2.4.3.0
- [KubeVirt Python SDK](https://github.com/kubevirt/client-python)
- [KubeVirt](https://github.com/kubevirt/kubevirt)

## Installation and usage

* Using Git

```
$ git clone https://github.com/kubevirt/ansible-kubevirt-modules
```

* [Install KubeVirt Python SDK](https://github.com/kubevirt/client-python#installation--usage)

* Once installed, add it to a playbook:

```
---
- hosts: localhost
  remote_user: root
  roles:
    - role: ansible-kubevirt-modules
      install_python_requirements: no
    - role: hello-underworld
```

Because the role is referenced, the `hello-underworld` role is able to make use of the kubevirt modules

## Playbook examples

* [Virtual Machine](tests/raw_vm.yml)
* [Offline Virtual Machine](tests/raw_ovm.yml)
* [Virtual Machine ReplicaSet](tests/raw_vmrs.yml)
* [Virtual Machine facts](tests/kubevirt_vm_facts.yml)
* [Offline Virtual Machine facts](tests/kubevirt_ovm_facts.yml)
* [Virtual Machine Replica Set facts](tests/kubevirt_vmrs_facts.yml)

## Local testing

- Download [Fedora cloud raw image](https://alt.fedoraproject.org/cloud/)
- Create `fedoravm-pvc`, if using NFS, the following snippets can be used:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0002
spec:
  capacity:
    storage: 5Gi
  accessModes:
  - ReadWriteOnce
  nfs:
    path: /exports/fedora_kubevirt
    server: <ip_address>
  persistentVolumeReclaimPolicy: Retain
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fedoravm-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

- Place the uncompressed Fedora cloud raw image in `/exports/fedora_kubevirt/disk.img`
- Add the following entry to the NFS exports file (usually `/etc/exports`):

```
/exports/fedora_kubevirt *(rw,root_squash)
```

- Make sure KubeVirt can access the `disk.img` file:

```shell
$ chmod -R 755 /exports/fedora_kubevirt
$ chmod 666 /exports/fedora_kubevirt/disk.img
```

- Update the NFS service by running the following command:

```shell
$ exportfs -av
```

- Save the snippets to `fedora-pv.yml` and `fedora-pvc.yml` respectively and create the resources as follows:

```shell
$ kubectl create -f fedora-pv.yml
$ kubectl create -f fedora-pvc.yml
```

- Verify the PV and PVC have bound properly:

```shell
$ kubectl get pvc
NAME           STATUS    VOLUME    CAPACITY   ACCESS MODES   STORAGECLASS   AGE
fedoravm-pvc   Bound     pv0002    5Gi        RWO                           1m
```

- Run the tests as follows:

```shell
$ export ANSIBLE_CONFIG=tests/ansible.cfg
$ ansible-playbook tests/*yml
```

- All three playbook examples, `tests/raw_vm.yml`, `tests/raw_ovm.yml` and `tests/raw_vmrs.yml` include [cloud-init](http://cloudinit.readthedocs.io/en/latest/) configuration and can be accessed by SSH as follows:

```shell
$ kubectl get all
NAME                             READY     STATUS    RESTARTS   AGE
po/virt-launcher-bbecker-jw5kk   1/1       Running   0          22m

$ kubectl expose pod virt-launcher-bbecker-jw5kk --port=27017 --target-port=22 --name=vmservice
$ kubectl get svc vmservice
NAME        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)     AGE
vmservice   ClusterIP   172.30.133.9   <none>        27017/TCP   19m

$ ssh -i tests/kubevirt_rsa -p 27017 kubevirt@172.30.133.9
```

> **NOTE:** It might take a while for the VM to completely come up before SSH can be used.

### Facts

* Once one of the previous resources has been created, the fact modules can be tested as well as follows:

```shell
$ ansible-playbook tests/kubevirt_vm_facts.yml
```

The above command, will gather the information for the VM stated in the playbook and produce the following ouput:

```json
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
```
