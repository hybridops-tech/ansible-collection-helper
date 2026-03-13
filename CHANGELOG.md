# Changelog

All notable changes to the `hybridops.helper` collection will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- No unreleased changes yet.

## [0.1.1] - 2026-03-10

### Changed

- Added repository-local `yamllint` configuration so release and CI checks run consistently.
- Cleaned helper release packaging to avoid stale test-output noise in the publish path.

## [0.1.0] - 2026-01-02

### Added

- Initial publication of the `hybridops.helper` collection.
- Evidence and NetBox helper roles:
  - `helper_evidence_collector`
  - `helper_netbox_inventory`
- Reusable operational layout for helper-generated run data.
- `galaxy.yml` metadata for namespace `hybridops` and collection name `helper`.

[Unreleased]: https://github.com/hybridops-tech/ansible-collection-helper/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/hybridops-tech/ansible-collection-helper/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/hybridops-tech/ansible-collection-helper/releases/tag/v0.1.0
