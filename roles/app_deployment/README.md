KubeVirt application deployment
===============================

The `kubevirt.app_deployment` role manages the hybrid application infrastructure.
You can manage the virtual machines together with deployments and services.

Requirements
------------

 * Ansible version 2.8 or higher
 * openshift SDK version 0.8.6 or higher

Role Variables
--------------

| Name                     | Default value |                                              |
|--------------------------|---------------|-------------------------------------------------------------|
| kubevirt_app_vms         | UNDEF         | Virtual machine applications specification. |
| kubevirt_app_services    | UNDEF         | Services for the virtual machines and deployments. |
| kubevirt_app_deployments | UNDEF         | Deployments applications specification/ |

`kubevirt_app_vms`
| Name     | Default value |                                              |
|----------|---------------|-------------------------------------------------------------|
| name     | UNDEF         | Name of the virtual machine. |

Dependencies
------------

None.

Example Playbook
----------------

```yaml
---
- name: Deploy application
  hosts: localhost

  vars:
    kubevirt_app_vms:
      - name: myapp
        namespace: default
        memory: 128Mi
        image:
          url: https://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img
          storage: 1Gi
        labels:
          app: myappdb

    kubevirt_app_services:
      - name: myapp-db-service
        namespace: default
        selector:
          app: myappdb
        ports:
          - protocol: TCP
            port: 22
            targetPort: 9376

      - name: myapp-nginx-service
        namespace: default
        selector:
          app: myapphttp
        ports:
          - protocol: TCP
            port: 80
            targetPort: 9377

    kubevirt_app_deployments:
      - name: myapp
        replicas: 2
        namespace: default
        containers:
          - image: nginx
        labels:
          app: myapphttp

  roles:
    - kubevirt.app_deployment
```

License
-------

Apache License 2.0
