# Contributing to `hybridops.helper`

`hybridops.helper` focuses on **evidence collection** and **NetBox integration**.  
It exists to make automation runs explainable and auditable, not to implement business logic.

Typical roles include:

- `helper_evidence_collector` – structure logs, configs, and artefacts under `output/`.
- `helper_netbox_inventory` – export and synchronise inventory data with NetBox.

Helpers should be reusable both inside HybridOps.Studio and in other environments.

---

## 1. Contribution scope

Good fits for this collection:

- Enhancements to evidence layout, labelling, or metadata.
- Additional NetBox integration helpers that remain generic and reusable.
- Improvements to error handling and diagnostics when NetBox or evidence paths are misconfigured.
- Documentation updates that clarify how to use helpers in CI, drills, and runbooks.

Avoid embedding **platform-specific business logic** here. That belongs in `hybridops.app` or `hybridops.network`.

---

## 2. Development workflow

1. **Fork and branch**

   - Fork the repository.
   - Create a topic branch: `feature/<short-description>` or `fix/<short-description>`.

2. **Local setup**

   - Install dependencies from `requirements.txt` into a virtualenv:

     ```bash
     python3 -m venv .venv
     . .venv/bin/activate
     pip install -r requirements.txt
     ```

3. **Make your change**

   - Keep interfaces stable where possible:
     - Input variables.
     - Output directory layout under `output/`.
   - Ensure helpers fail with clear, actionable error messages.
   - Preserve the evidence-first mindset: outputs should be easy to link from ADRs, HOWTOs, and runbooks.

4. **Run tests**

   - Role-local smoke tests:

     ```bash
     cd ansible_collections/hybridops/helper/roles/<role_name>
     ansible-playbook -i tests/inventory.example.ini tests/smoke.yml
     ```

   - If you add or change NetBox integration behaviour:
     - Test against a lab NetBox instance.
     - Update `tests/smoke.yml` and example inventory to reflect the expected configuration.

   - From the shared `ansible-galaxy-hybridops` workspace (integration with the wider platform), relevant roles can also be exercised via:

     ```bash
     make venv.refresh
     make test ROLE=helper_evidence_collector
     ```

5. **Open a pull request**

   - Describe what changed and how it affects evidence layout or NetBox behaviour.
   - Include details of the test environment (for example NetBox version, lab details, and any assumptions).

---

## 3. Evidence and NetBox expectations

Evidence-related roles should:

- Write artefacts under a clearly named root (for example `output/artifacts/...`).
- Avoid overwriting existing evidence unless explicitly configured to do so.
- Use predictable, documented paths so documentation can link to them.

NetBox-related roles should:

- Treat API and connectivity errors as first-class signals with clear messages.
- Avoid hard-coding site, tenant, or environment names beyond what is documented in variables.
- Keep NetBox models and assumptions documented in role-level READMEs.

---

## 4. Style and quality

- Keep comments brief and focused on non-obvious intent.
- Avoid logging secrets, tokens, or sensitive values into evidence output.
- Use variables for anything environment-specific (URLs, tokens, paths).
- Follow the versions and tools in `requirements.txt` for linting and testing (for example `ansible-lint`, `pre-commit` if configured).

By contributing here, you help strengthen the **evidence story** around automation runs, making it easier to prove what happened and why in both HybridOps.Studio and external environments.