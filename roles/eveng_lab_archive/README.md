# eveng_lab_archive

Export EVE-NG lab definitions to a controller-side archive and restore them
after redeployment. Device images and temporary node runtime data are outside
the lab tree and are not included.

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
