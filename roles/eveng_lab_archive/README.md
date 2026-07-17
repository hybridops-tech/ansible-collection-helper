# eveng_lab_archive

Export EVE-NG lab definitions to a controller-side archive and restore them
after redeployment. Device images are not included.

## Export

```yaml
eveng_lab_archive_action: export
eveng_lab_archive_path: /srv/hybridops/labs/student-lab.tar.gz
eveng_lab_archive_folders:
  - student
```

An empty folder list exports the complete `/opt/unetlab/labs` tree. The role
publishes the controller path and SHA-256 checksum in
`eveng_lab_archive_results`.

## Restore

```yaml
eveng_lab_archive_action: restore
eveng_lab_archive_path: /srv/hybridops/labs/student-lab.tar.gz
eveng_lab_archive_expected_sha256: CHANGE_ME
eveng_lab_archive_overwrite: false
```

Restore verifies the checksum and rejects unsafe archive paths. Existing lab
content is protected unless overwrite is enabled explicitly.

## Stopped node state

QEMU overlay capture is optional and requires a complete lab export:

```yaml
eveng_lab_archive_include_node_state: true
```

All QEMU nodes must be stopped. The role validates each overlay and writes a
checksummed companion archive without copying its vendor base image.

Restore requires the companion archive checksum:

```yaml
eveng_lab_archive_restore_node_state: true
eveng_lab_archive_node_state_path: /srv/hybridops/labs/student-lab.tar.gz.node-state.tar.gz
eveng_lab_archive_node_state_expected_sha256: CHANGE_ME
```

The matching base images must already be installed. Existing runtime disks are
not replaced unless overwrite is enabled explicitly.
