# `hybridops.helper`

Helper roles for HybridOps platform validation, EVE-NG content handling, and NetBox seeding.

This collection contains small roles that extend the higher-level platform services in `hybridops.app` and `hybridops.common` without bloating those collections.

Role-level variables and assumptions are documented in each role's `README.md`. Broader operator guidance lives at [docs.hybridops.tech](https://docs.hybridops.tech).

## Scope

- EVE-NG validation and content delivery helpers.
- NetBox seeding helpers.
- Small operational roles that are reused across multiple modules and blueprints.

## Roles

| Role | Purpose |
|------|---------|
| `eveng_healthcheck` | Verify the health of an EVE-NG deployment. |
| `eveng_images` | Deliver node images into EVE-NG. |
| `eveng_labs` | Deliver lab content into EVE-NG. |
| `netbox_seed` | Seed NetBox with initial or curated platform data. |

## Requirements

- Ansible `ansible-core` 2.15+
- Python 3.10+ on the control node

## Installation

Install from Ansible Galaxy:

```bash
ansible-galaxy collection install hybridops.helper
```

Pin in `collections/requirements.yml`:

```yaml
collections:
  - name: hybridops.helper
    version: ">=0.1.0"
```

## Usage

```yaml
- name: Check EVE-NG health
  hosts: eveng_hosts
  become: true
  collections:
    - hybridops.helper

  roles:
    - role: hybridops.helper.eveng_healthcheck
```

## Testing

- Role-local smoke tests are included where isolated validation is useful.
- Platform integration is proven through HybridOps module and blueprint runs in `hybridops-core`.

## License

- Code: [MIT-0](https://spdx.org/licenses/MIT-0.html)
- Documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

See the project licensing guidance at [docs.hybridops.tech](https://docs.hybridops.tech).
