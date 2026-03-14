# Changelog

All notable changes to the `hybridops.helper` collection will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- No unreleased changes yet.

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

[Unreleased]: https://github.com/hybridops-tech/ansible-collection-helper/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/hybridops-tech/ansible-collection-helper/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/hybridops-tech/ansible-collection-helper/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/hybridops-tech/ansible-collection-helper/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/hybridops-tech/ansible-collection-helper/releases/tag/v0.1.0
