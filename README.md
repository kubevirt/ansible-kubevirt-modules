# Ansible KubeVirt Modules

[Ansible](https://github.com/ansible/ansible) modules for [KubeVirt](https://github.com/kubevirt/kubevirt) management.

## Contents

- `library`: Ansible modules files for KubeVirt management
- `tests`: Ansible playbooks to test KubeVirt modules

## Requirements

- Ansible 2.4.3.0
- Kubernetes Python Module
- [KubeVirt](https://github.com/kubevirt/kubevirt)

## Installation and usage

Use the Galaxy client to install the role:

```
$ ansible-galaxy install kubevirt.kubevirt-modules
```

Once installed, add it to a playbook:

```
---
- hosts: localhost
  remote_user: root
  roles:
    - role: kubevirt.kubevirt-modules
      install_python_requirements: no
    - role: hello-underworld
```
> **NOTE:** Set `install_python_reqirememnts: yes` to install Kubernetes Python module

Because the role is referenced, the `hello-underworld` role is able to make use of the kubevirt modules

## LOCAL TESTING

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
$ pip install kubernetes
$ export ANSIBLE_CONFIG=tests/ansible.cfg
$ ansible-playbook tests/*yml
```

- Virtual machines created by `tests/vm.yml` and `tests/ovm.yml` include [cloud-init](http://cloudinit.readthedocs.io/en/latest/) configuration and can be accessed by SSH as follows:

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
