# netbox_seed

Seed NetBox (SoT) from an exported infrastructure CSV.

## Architecture alignment (HybridOps.Studio)

- [ADR-0002 — Source of Truth: NetBox-Driven Inventory](https://docs.hybridops.studio/adr/ADR-0002-source-of-truth-netbox-driven-inventory/) — seed NetBox from exported infra and pivot inventories.
- [ADR-0020 — Secrets Strategy](https://docs.hybridops.studio/adr/ADR-0020-secrets-strategy-akv-now-sops-fallback-vault-later/) — API token is supplied by the caller.

## Purpose and scope

Included:
- NetBox API connectivity validation.
- CSV parsing and idempotent upserts using NetBox Ansible modules.

Excluded:
- NetBox application deployment (use `netbox_service`).
- CSV export generation (handle via platform helper/export job).

## License

- Code: [MIT-0](https://spdx.org/licenses/MIT-0.html)  
- Documentation & diagrams: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
