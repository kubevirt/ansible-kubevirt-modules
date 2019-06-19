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

| Name                          | Default value |                                                    |
|-------------------------------|---------------|----------------------------------------------------|
| kubevirt_app_vms              | UNDEF         | Virtual machine applications specification.        |
| kubevirt_app_services         | UNDEF         | Services for the virtual machines and deployments. |
| kubevirt_app_deployments      | UNDEF         | Deployments applications specification.            |
| kubevirt_app_network_policies | UNDEF         | By default, all vmis in a namespace are accessible from other vmis and network endpoints. To isolate one or more vmis in a project, you can create NetworkPolicy objects in that namespace to indicate the allowed incoming connections. Note that your networking solution must support NetworkPolicy. |

`kubevirt_app_vms`

| Name      | Default value |                                              |
|-----------|---------------|----------------------------------------------|
| name      | UNDEF         | Name of the virtual machine.                 |
| affinity  | UNDEF         | Describes node affinity scheduling rules for the vm. |
| node_affinity | UNDEF     | Describes vm affinity scheduling rules e.g. co-locate this vm in the same node, zone, etc. as some other vms |
| anti_affinity | UNDEF     | Describes vm anti-affinity scheduling rules e.g. avoid putting this vm in the same node, zone, etc. as some other vms. |

`kubevirt_app_network_policies`

| Name                 | Default value |                                            |
|----------------------|---------------|--------------------------------------------|
| name                 | UNDEF         | Name of the network policy.                |
| pod_selector         | UNDEF         | Dict of pod labels to which the policy apply. When empty selects all pods in policy's namespace. |
| deny_all             | UNDEF         | If true deny all ingress and egress trafic to/from virtual machines. |
| ingress              | UNDEF         | List of specific ingress rules for VMIs. |
| ingress_allow_all    | UNDEF         | If true allow all ingress trafic to virtual machines. |
| ingress_deny_all     | UNDEF         | If true all ingress trafic to virtual machines will be denied. |
| ingress_allow_same_namespace | UNDEF | If true only ingress trafic from same namespace will be allowed. |
| egress               | UNDEF         | List of specific egress rules for VMIs. |
| egress_allow_all     | UNDEF         | If true allow all egress trafic to virtual machines. |
| egress_deny_all      | UNDEF         | If true all egress trafic to virtual machines will be denied. |
| egress_allow_same_namespace | UNDEF  | If true only egress trafic from same namespace will be allowed. |

`ingress`

| Name                 | Default value |                                            |
|----------------------|---------------|--------------------------------------------|
| ingress_ip_blocks    | UNDEF         | This selects particular IP CIDR ranges to allow as ingress sources. These should be cluster-external IPs, since VMI IPs are ephemeral and unpredictable |
| ingress_namespace_selector | UNDEF   | This selects particular namespaces for which all Pods should be allowed as egress destinations. |
| ingress_pod_selector | UNDEF         | Specify vmis to which the ingress rules apply. |
| ingress_ports        | UNDEF         | Define ports and protocol of the ports to be allowed by ingress traffic. |

`egress`

| Name                 | Default value |                                            |
|----------------------|---------------|--------------------------------------------|
| egress_ip_blocks     | UNDEF         | This selects particular IP CIDR ranges to allow as ingress sources. These should be cluster-external IPs, since VMI IPs are ephemeral and unpredictable |
| egress_namespace_selector | UNDEF    | This selects particular namespaces for which all Pods should be allowed as egress destinations. |
| egress_pod_selector  | UNDEF         | Specify vmis to which the egress rules apply. |
| egress_ports         | UNDEF         | Define ports and protocol of the ports to be allowed by egress traffic. |

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
