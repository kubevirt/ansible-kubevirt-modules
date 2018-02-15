# ansible-kubevirt-modules

Provides access to the latest release of the kubevirt modules. 

Include this role in a playbook, and any other plays, roles, and includes will have access to the modules.

The modules are found in the [library folder](./library)

## Requirements

- Ansible
- [kubevirt](https://github.com/karmab/kubevirt)

## Installation and use

Use the Galaxy client to install the role:

```
$ ansible-galaxy install karmabs.kubevirt-modules
```

Once installed, add it to a playbook:

```
---
- hosts: localhost
  remote_user: root
  roles:
    - role: karmab.kubevirt-modules
      install_python_requirements: no
    - role: hello-underworld
```

Because the role is referenced, the `hello-underworld` role is able to make use of the kubevirt modules

### Module parameters

install_python_requirements
> Set to true, if you want kubernetes python module installed. Defaults to false. Will install via `pip`

## License

Apache V2
