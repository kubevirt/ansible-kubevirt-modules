# Ansible KubeVirt Modules

[Ansible](https://github.com/ansible/ansible) modules for [KubeVirt](https://github.com/kubevirt/kubevirt) management.

## Contents

- `lib`: Ansible modules files for KubeVirt management
- `tests`: Ansible playbook examples and unit tests

## Requirements

- Ansible >= 2.4.3.0
- [KubeVirt Python SDK](https://github.com/kubevirt/client-python)
- [Kubernetes Python client](https://github.com/kubernetes-client/python)
- [KubeVirt](https://github.com/kubevirt/kubevirt)

## Installation and usage

### Using Git

1. Clone the repository:

```
$ git clone https://github.com/kubevirt/ansible-kubevirt-modules
```

2. [Install KubeVirt Python SDK](https://github.com/kubevirt/client-python#installation--usage)

3. [Install Kubernetes Python client](https://github.com/kubernetes-client/python/#installation)

4. Once installed, add it to a playbook:

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
* [Stop Offline Virtual Machine](tests/kubevirt_ovm_stopped.yml)
* [Virtual Machine facts](tests/kubevirt_vm_facts.yml)
* [Offline Virtual Machine facts](tests/kubevirt_ovm_facts.yml)
* [Virtual Machine Replica Set facts](tests/kubevirt_vmrs_facts.yml)

## Local testing

1. Download [Fedora cloud raw image](https://alt.fedoraproject.org/cloud/)
2. Create `fedoravm-pvc`, if using NFS, the following snippets can be used:

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

3. Place the uncompressed Fedora cloud raw image in `/exports/fedora_kubevirt/disk.img`
4. Add the following entry to the NFS exports file (usually `/etc/exports`):

```
/exports/fedora_kubevirt *(rw,root_squash)
```

5. Make sure KubeVirt can access the `disk.img` file:

```shell
$ chmod -R 755 /exports/fedora_kubevirt
$ chmod 666 /exports/fedora_kubevirt/disk.img
```

6. Update the NFS service by running the following command:

```shell
$ exportfs -av
```

7. Save the snippets to `fedora-pv.yml` and `fedora-pvc.yml` respectively and create the resources as follows:

```shell
$ kubectl create -f fedora-pv.yml
$ kubectl create -f fedora-pvc.yml
```

8. Verify the PV and PVC have bound properly:

```shell
$ kubectl get pvc
NAME           STATUS    VOLUME    CAPACITY   ACCESS MODES   STORAGECLASS   AGE
fedoravm-pvc   Bound     pv0002    5Gi        RWO                           1m
```

9. Run the tests as follows:

```shell
$ export ANSIBLE_CONFIG=tests/ansible.cfg
$ ansible-playbook tests/*yml
```

10. All three playbook examples, `tests/raw_vm.yml`, `tests/raw_ovm.yml` and `tests/raw_vmrs.yml` include [cloud-init](http://cloudinit.readthedocs.io/en/latest/) configuration and can be accessed by SSH as follows:

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

The above command, will gather the information for the VM stated in the playbook and print out a JSON document based on [KubeVirt VM spec](https://kubevirt.io/api-reference/master/definitions.html#_v1_virtualmachine).
