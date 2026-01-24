# `hybridops.helper`

Helper roles for evidence collection and NetBox integration. The collection focuses on audit-friendly outputs and inventory alignment, with role-level behaviour documented in each role’s `README.md`.

High-level platform context is maintained at [docs.hybridops.studio](https://docs.hybridops.studio).

## Scope

- Evidence helpers that produce predictable artefacts under `output/` roots (for example `output/artifacts/...`).
- NetBox helpers for inventory export and synchronisation using the NetBox API.
- Generic behaviour suitable for HybridOps.Studio and other environments.

## Roles

| Role | Purpose |
|------|---------|
| `helper_evidence_collector` | Collect logs and configuration into an artefact tree under `output/`. |
| `helper_netbox_inventory` | Export or synchronise inventory data with NetBox APIs. |

## Requirements

- Ansible `ansible-core` 2.15+.
- Python 3.10+ on the control node.
- NetBox integration requires a reachable NetBox instance and an API token provided via variables, Vault, or environment lookup.

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

### Wrap a playbook run with evidence collection

```yaml
- name: Nightly device backups with evidence
  hosts: all_network_devices
  gather_facts: false
  collections:
    - hybridops.network
    - hybridops.helper

  vars:
    backup_root: "/srv/network-backups"
    evidence_root: "/srv/hybridops/output/artifacts/network-backups"

  pre_tasks:
    - name: Start evidence session
      include_role:
        name: hybridops.helper.helper_evidence_collector
      vars:
        evidence_root: "{{ evidence_root }}"
        evidence_label: "nightly-backup"

  roles:
    - role: hybridops.network.device_backup
```

### Synchronise inventory to NetBox

```yaml
- name: Push inventory into NetBox
  hosts: network_inventory_source
  gather_facts: false
  collections:
    - hybridops.helper

  vars:
    netbox_url: "https://netbox.example.com"
    netbox_token: "{{ lookup('env', 'NETBOX_TOKEN') }}"

  roles:
    - role: hybridops.helper.helper_netbox_inventory
```

## Testing

- Role-local smoke tests are provided under `roles/<role>/tests/` and exercised against a lab inventory.
- Molecule scenarios may be provided where isolated validation is valuable (for example NetBox integration against a test instance).
- Platform integration tests are executed via HybridOps.Studio pipelines and lab inventories.

## License

- Code: [MIT-0](https://spdx.org/licenses/MIT-0.html)  
- Documentation & diagrams: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

See the [HybridOps.Studio licensing overview](https://docs.hybridops.studio/briefings/legal/licensing/)
for project-wide licence details, including branding and trademark notes.
