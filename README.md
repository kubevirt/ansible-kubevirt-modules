# Ansible KubeVirt Modules

[Ansible](https://github.com/ansible/ansible) modules for [KubeVirt](https://github.com/kubevirt/kubevirt) management. 

## Contents

- `library`: Ansible modules files for KubeVirt management
- `tests`: Ansible playbooks to test KubeVirt modules

## Requirements

- Ansible 2.4.3.0
- Kubernetes Python Module
- [kubevirt](https://github.com/kubevirt/kubevirt)

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

```
pip install kubernetes
set -x ANSIBLE_LIBRARY .
ansible-playbook tests/*yml
```
