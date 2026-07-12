# Changelog

## Unreleased

- Fail URL-based image runs when any requested archive is missing.
- Isolate MEGA downloads so an existing cache file cannot be renamed for a later request.

## [1.0.0] - 2026-01-13

### Added

- Initial release.
- Support for URL, local, and remote image sources.
- Routing of image types (QEMU, IOL, Dynamips) to standard EVE-NG paths.
- Support for image archive formats: `.tar.gz`, `.tgz`, `.zip`, `.gz`.
- Automatic organisation into the EVE-NG directory structure.
- Download caching and validation.
- Multi-file deployment support.
