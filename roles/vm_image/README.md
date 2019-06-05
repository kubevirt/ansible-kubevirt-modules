# ansible-role-kubevirt-vm-image

## Vars

### Top level

| Name                   | Default | Description |
| ---------------------- | ------- | ----------- |
| kubevirt_image_volumes | UNDEF   | List of volumes to be created |

### Volume spec

| Name            | Default | Req | Description |
| --------------- | --------| --- | ----------- |
| name            | UNDEF   |  Y  | Name of volume to be created |
| namespace       | UNDEF   |     | Namespace to create the volume in |
| size            | UNDEF   |     | How much storage space to allocate |
| source          | blank   |     | What to initialize the volume with (see examples) |
| labels          | UNDEF   |     | Labels to be assigned to the resulting object |
| annotations     | UNDEF   |     | Annotations to be assigned to the resulting object |
| storage_class   | UNDEF   |     | Storage class name |
| wait            | yes     |     | Whether to wait for the volume to initialize |
| wait_timeout    | 300     |     | How long to wait for, while the volume initializes (in seconds) |

## Examples

```yaml
---
- name: Create
  hosts: localhost

  vars:
    kubevirt_image_volumes:
      - name: volume1
        namespace: default
        size: 100Mi
        source: "https://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img"

      - name: volume2
        namespace: default
        size: 100Mi
        source: "docker://kubevirt/cirros-container-disk-demo:latest"

      - name: volume3
        namespace: default
        size: 100Mi
        source: "/tmp/disk.qcow2"

      - name: volume4-blank
        namespace: default
        size: 100Mi

  roles:
    - kubevirt.vm_image
```


<!-- vim: set et ts=2 sw=2: -->
