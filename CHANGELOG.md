# Changelog

All notable changes to the `hybridops.helper` collection will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a fail-closed EVE-NG restore capacity check before existing lab and
  node-state data is replaced.
- Added checksum-verified restoration of referenced EVE-NG base-image
  companions before lab definitions and QEMU overlays.

### Changed

- Separated base-image replacement from lab-definition overwrite and promoted
  staged image paths as a rollback-capable transaction.
- Rejected automatic QEMU termination during node-state export. Stateful guests
  must be shut down inside the guest before their EVE-NG nodes are stopped.

### Fixed

- Rejected IOL licence material in migration image companions and accepted the
  archive formats supported by controller inspection.

## [0.1.10] - 2026-08-29

### Added

- Added native EVE-NG device-configuration capture before preservation and
  activation after restore.

### Changed

- Retained source-bound image downloads by default so interrupted image runs
  can resume without repeating completed transfers.
- Skipped unchanged local image archives and bounded local synchronization.
- Prepared controller-side acceleration for GCP IAP image transfers when the
  required Python support is available.

### Fixed

- Staged and verified EVE-NG lab exports before promotion, retaining one
  verified fallback generation with its manifest and node-state archive.
- Required every requested image archive to produce verified installed content
  before publishing readiness.
- Stopped MEGA downloads promptly when the transfer quota is exhausted.
- Avoided loop-variable collisions when a play restores EVE-NG lab state more
  than once.
- Reported every installed EVE-NG image and restored lab archives without
  replacing unrelated existing lab content.
- Preserved saved device configurations and QEMU node state together across
  repeated archive and restore cycles.
- Restored EVE-NG tenant ownership and runtime permissions so mixed IOL and
  QEMU labs can start after restoration.

## [0.1.9] - 2026-08-22

### Added

- Added protected placement and validation of operator-supplied EVE-NG IOL
  licence material without including it in reports or lab archives.

### Fixed

- Mapped root-layout IOL archives into the EVE-NG `iol/bin` directory and
  rejected archives that embed licence material.
- Scoped URL image installation to the declared download set so stale cache
  files from earlier runs are not validated or installed.
- Installed `iourc` before EVE-NG repairs image permissions, normalised line
  endings, and rejected licence material bound to another host.
- Reported the EVE-NG hostname and Linux host ID when operator-supplied IOL
  licence material does not match a rebuilt host.
- Refreshed same-name URL cache entries when their source changes and removed
  transient image caches unless retention is enabled explicitly.
- Normalised F5 BIG-IP ZIP archives into an EVE-NG `bigip-` appliance directory
  with deterministic system and datastore disk names.

## [0.1.8] - 2026-07-17

### Fixed

- Limited EVE-NG lab checkpoints to writable node overlays, excluding managed
  base images already supplied by the deployment lifecycle.
- Prevented failed or interrupted HTTP image downloads from leaving cache
  files that a later run could reuse.
- Rejected HTTP error responses and invalid QEMU disk content before EVE-NG
  installation.

## [0.1.7] - 2026-07-15

### Added

- Added deterministic export and checksum-verified restore for EVE-NG lab
  definitions.

### Security

- Rejected unsafe archive paths and archive links before restore.
- Protected existing lab content unless replacement is enabled explicitly.

## [0.1.6] - 2026-07-12

### Fixed

- Preserved every requested MEGA archive instead of allowing an existing cache
  file to be renamed for a later list entry.
- Failed image runs when any requested archive is missing.
- Installed detected QEMU, IOL, and Dynamips content into the EVE-NG addons
  tree and verified each installed path.
- Repaired EVE-NG image permissions after installation.

### Added

- Added an archive-installation fixture covering the QEMU folder layout.

## [0.1.5] - 2026-06-14

### Changed

- Cleaned public Galaxy metadata so collection references point to the published Galaxy and documentation surfaces.
- Tightened the package surface to exclude old build archives and showcase-only assets.

## [0.1.4] - 2026-04-03

### Changed

- Expanded Galaxy metadata tags for search discoverability.

## [0.1.3] - 2026-03-14

### Changed

- Brought the legacy EVE-NG helper roles up to the same lint and CI standard as the published helper surface.
- Prepared the collection runtime inside CI before direct `ansible-lint` so helper smoke playbooks resolve `hybridops.helper` consistently on GitHub runners.

### Fixed

- Aligned the NetBox seed role with the current lint contract.
- Corrected text-report rendering in `eveng_healthcheck`.

## [0.1.2] - 2026-03-13

### Changed

- Cleaned the helper collection packaging and README surface for Galaxy publication.
- Narrowed the published helper branch to the validated metadata and role surface only.

## [0.1.1] - 2026-03-10

### Changed

- Added repository-local `yamllint` configuration so release and CI checks run consistently.
- Cleaned helper release packaging to avoid stale test-output noise in the publish path.

## [0.1.0] - 2026-01-02

### Added

- Initial publication of the `hybridops.helper` collection.
- Helper and NetBox support roles:
  - `helper_evidence_collector`
  - `helper_netbox_inventory`
- Reusable operational layout for helper-generated data.
- `galaxy.yml` metadata for namespace `hybridops` and collection name `helper`.
