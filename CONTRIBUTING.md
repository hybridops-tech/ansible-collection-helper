# Contributing to `hybridops.helper`

`hybridops.helper` provides evidence collection and NetBox integration helpers. The scope is operational traceability and audit-friendly outputs, not platform-specific business logic.

Design and release context is maintained in the HybridOps.Studio documentation site.

## Contribution scope

Appropriate changes include:

- Evidence layout improvements (structure, labelling, metadata, retention behaviour).
- Generic NetBox integration helpers (inventory export, synchronisation, diagnostics).
- Error handling and actionable diagnostics for misconfiguration and API failures.
- Documentation updates for CI, drills, and runbooks.

Avoid platform-specific business logic in this collection; prefer `hybridops.app` or `hybridops.network` when behaviour is domain-specific.

## Development workflow

### Local setup

Use versions compatible with `requirements.txt`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Change guidelines

- Keep interfaces stable where practical (inputs and output layout under `output/`).
- Fail with clear, actionable error messages.
- Treat evidence paths as an API surface; document path changes and include migration notes in `CHANGELOG.md` when required.

### Tests

Role-local smoke tests:

```bash
cd roles/<role_name>
ansible-playbook -i tests/inventory.example.ini tests/smoke.yml
```

NetBox-related changes should be validated against a lab NetBox instance and reflected in the smoke harness and example inventory.

Platform integration (via the harness):

```bash
# In galaxy-collections-harness
make workspace.clone
make collections.sync
make venv.refresh
make test ROLE=<role_name>
```

### Pull requests

Include:

- Summary of changes and expected impact (evidence layout and/or NetBox behaviour).
- Test evidence (smoke and/or platform integration).
- NetBox test details where applicable (version and assumptions).

## Evidence and NetBox expectations

Evidence helpers should:

- Write artefacts under predictable, documented roots (for example `output/artifacts/...`).
- Avoid overwriting evidence unless explicitly configured.
- Avoid emitting secrets or sensitive values into evidence output.

NetBox helpers should:

- Treat API and connectivity errors as first-class signals with clear messages.
- Avoid hard-coded site, tenant, or environment names beyond documented variables.
- Document model assumptions in role-level README content where relevant.

## Security and secrets

- Do not commit secrets, tokens, client IDs, or passwords.
- Consume sensitive values via variables, Vault, or environment lookups.
- Avoid logging sensitive values into task output and evidence artefacts.
