# eveng_lab_archive

Export EVE-NG lab definitions to a controller-side archive and restore them
after redeployment. Routine exports do not include device images.

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

Saved device configurations can be refreshed in each lab definition before the
archive is built:

```yaml
eveng_lab_archive_capture_device_configs: true
eveng_lab_archive_api_password_env: EVENG_ADMIN_PASSWORD
```

The role uses EVE-NG's local API. A failed capture stops preservation before
the execution host is released. Intended device changes must be saved to
startup configuration before capture.

Each export is staged and verified before it replaces the current archive. The
previous verified generation is retained with a `.previous` suffix, including
its manifest and node-state companion when present.

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
checksummed companion archive without copying its vendor base image. Multi-disk
nodes retain each writable overlay. Export succeeds only after both fetched
archives have been read and their expected contents verified.

Restore requires the companion archive checksum:

```yaml
eveng_lab_archive_restore_node_state: true
eveng_lab_archive_node_state_path: /srv/hybridops/labs/student-lab.tar.gz.node-state.tar.gz
eveng_lab_archive_node_state_expected_sha256: CHANGE_ME
```

The matching base images must already be installed. Existing runtime disks are
not replaced unless overwrite is enabled explicitly.

An existing-lab migration can supply a separately verified image companion:

```yaml
eveng_lab_archive_restore_images: true
eveng_lab_archive_images_path: /srv/hybridops/labs/images.tar.gz
eveng_lab_archive_images_expected_sha256: CHANGE_ME
```

The companion may contain referenced QEMU, IOL and Dynamips bases. Licence
material is not accepted. Existing image paths remain protected unless
overwrite is enabled explicitly.

Restore verifies that the target filesystems can hold the compressed archives,
their expanded contents, and the free-space reserve before replacing lab data.
