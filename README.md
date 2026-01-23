# hybridops.helper – Evidence and NetBox Helper Roles

Helper roles for evidence collection and NetBox integration.  
This collection focuses on making automation runs explainable and auditable by
producing structured artefacts and maintaining inventory alignment with NetBox.

---

## 1. Collection scope

**Collection name:** `hybridops.helper`  
**Galaxy namespace/name:** `hybridops.helper` (planned)  
**Source repository:** [github.com/hybridops-studio/ansible-collection-helper](https://github.com/hybridops-studio/ansible-collection-helper)

The collection currently provides roles that:

- Capture logs, configuration, and artefacts from a playbook run into a
  structured output tree.
- Export or synchronise inventory information with NetBox.

Higher-level playbooks in HybridOps.Studio use these roles to keep a consistent
evidence story across network, platform, and application automation.

---

## 2. Roles

| Role name                   | Purpose                                                              |
|-----------------------------|----------------------------------------------------------------------|
| `helper_evidence_collector` | Collect logs and configuration into `output/artifacts/...`.         |
| `helper_netbox_inventory`   | Export or synchronise inventory data with NetBox APIs.              |

Additional helper roles may be added over time, but the collection remains
glue-focused and intentionally small.

---

## 3. Requirements

- Ansible **2.15+**.  
- Python **3.10+** on the control node.  
- For NetBox integration:
  - A reachable NetBox instance.
  - API token supplied via inventory variables, environment, or vault.

---

## 4. Installation

```bash
ansible-galaxy collection install hybridops.helper
```

In `collections/requirements.yml`:

```yaml
collections:
  - name: hybridops.helper
    version: "*"
```

---

## 5. Example usage

### 5.1 Wrap a network backup with evidence collection

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

### 5.2 Synchronise inventory to NetBox

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

---

## 6. Relationship to HybridOps.Studio

In the main HybridOps.Studio repository, this collection is used to:

- Attach structured evidence to automation runs for ADRs and briefings.  
- Support lab scenarios where operators run Ansible and review artefacts under
  `output/`.

The intent is that SDN rollouts, RKE2 bootstrap flows, DR drills, and similar
scenarios emit consistent evidence without duplicating logging logic in each
playbook.

---

## 7. Testing and CI

Helper roles in this collection are validated through:

- **Self-contained tests** under `tests/` (for example `tests/inventory.example.ini` and `tests/smoke.yml`) to exercise evidence and NetBox flows in isolation.
- **Molecule scenarios** under `molecule/default/` where richer validation is useful (for example, when interacting with a NetBox test instance).
- **Platform integration tests** in the HybridOps.Studio platform repository, where playbooks under `deployment/` and CI pipelines use `hybridops.helper` to attach evidence and maintain inventory alignment.

A repository-level `Makefile` provides a thin wrapper around Molecule:

- `make test` runs `molecule test` for all roles that have a `molecule/default/` scenario.
- `make test ROLE=helper_evidence_collector` runs `molecule test` for a single role.

This keeps helper roles small and focused while ensuring they behave correctly in end-to-end platform and CI runs.

---

## 8. Development and contributions

Layout (simplified):

```text
ansible_collections/hybridops/helper/
├── roles/
│   ├── helper_evidence_collector/
│   └── helper_netbox_inventory/
└── README.md
```

Guidelines for new helper roles:

- Keep roles focused and composable.  
- Avoid embedding platform-specific business logic; such logic belongs in
  `hybridops.app` or `hybridops.network`.  
- Ensure outputs land under a predictable `output/` structure that aligns with
  the wider evidence model documented in the main repository.
- Add tests under the role’s `tests/` directory or in consuming repositories
  for any non-trivial behaviour.

Release workflow matches other HybridOps collections: update `galaxy.yml`,
tag the repository, then build and publish to Galaxy.

---

## 9. Releases

This collection is versioned with Semantic Versioning and published to Ansible Galaxy as `hybridops.helper`.

Contribution guidelines are documented in `CONTRIBUTING.md` in this repository.

For maintainers, the end-to-end release workflow (versioning, changelog updates, build, publish and evidence capture) follows the standard HybridOps.Studio collections process described in ADR-0606:

- [ADR-0606 – Ansible collections release process](https://docs.hybridops.studio/adr/ADR-0606-ansible-collections-release-process/)

---

## 10. Licence

- Code in this collection: **MIT-0**.  
- Documentation in this repository: **CC BY 4.0**.

Project-wide licensing details are documented in the main HybridOps.Studio
repository.
