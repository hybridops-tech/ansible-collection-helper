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
eveng_lab_archive_guest_quiesced: true
```

Shut down stateful guests inside their operating systems, then stop the EVE-NG
nodes. The role rejects running QEMU processes, validates each overlay and
writes a checksummed companion archive without copying its vendor base image.
Multi-disk nodes retain each writable overlay. Export succeeds only after both
fetched archives have been read and their expected contents verified.

`eveng_lab_archive_guest_quiesced` is evidence for the current export. Do not
persist it as a standing environment acknowledgement. The legacy
`eveng_lab_archive_stop_running_nodes` input is accepted but has no effect.

For repeatable shutdown, provide a controller-side POSIX shell script instead:

```yaml
eveng_lab_archive_quiesce_script_path: /srv/hybridops/quiesce-lab.sh
eveng_lab_archive_quiesce_timeout_s: 300
```

The role runs the script on the EVE-NG host, waits for all QEMU processes to
stop, and records the script checksum. Script content and output are not stored.
The script and `eveng_lab_archive_guest_quiesced` are mutually exclusive.

Restore requires the companion archive checksum:

```yaml
eveng_lab_archive_restore_node_state: true
eveng_lab_archive_node_state_path: /srv/hybridops/labs/student-lab.tar.gz.node-state.tar.gz
eveng_lab_archive_node_state_expected_sha256: CHANGE_ME
```

The matching base images must already be installed. Existing runtime disks are
not replaced unless overwrite is enabled explicitly. Restore rejects structural
corruption. QCOW2 overlays that report only leaked clusters are retained without
rewriting the captured state.

An existing-lab migration can supply a separately verified image companion:

```yaml
eveng_lab_archive_restore_images: true
eveng_lab_archive_images_path: /srv/hybridops/labs/images.tar.gz
eveng_lab_archive_images_expected_sha256: CHANGE_ME
eveng_lab_archive_overwrite_images: false
```

The companion may contain referenced QEMU, IOL and Dynamips bases. Licence
material is not accepted. Existing image paths remain protected unless
image overwrite is enabled explicitly. Image content is staged before an
atomic promotion. A failed promotion or permission step restores the previous
paths.

Restore verifies that the target filesystems can hold the compressed archives,
their expanded contents, and the free-space reserve before replacing lab data.
