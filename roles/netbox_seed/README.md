---
# netbox_seed

Run the HybridOps NetBox seeding helper pipeline from a controller host.

## Scope

This role validates the controller runtime, reads NetBox API settings from a
host-local secrets env file, and then orchestrates the helper scripts for:

- infrastructure export
- IPAM import
- VM import
- optional device import

It can also write host-local evidence and optional mirrored repo artifacts.

This role does not deploy NetBox itself. Use `netbox_service` for the
application lifecycle.

## Runtime contract

The default mode is smoke validation only:

- `netbox_seed_smoke_only: true`

For a real run, set at least:

- `netbox_seed_smoke_only: false`
- `netbox_seed_repo_root: /path/to/repo-on-controller`

The role reads `NETBOX_API_URL` and `NETBOX_API_TOKEN` from:

- `netbox_seed_secrets_env_path`

By default that resolves to:

- `{{ netbox_seed_repo_root }}/control/secrets.vault.env`

## Smoke testing

Use the shipped smoke playbook for validation-only checks:

```bash
ansible-playbook -i tests/inventory.example.ini tests/smoke.yml
```

For a real run, provide a controller inventory that points at the repo root and
the secrets env file on that controller host.

## License

- Code: [MIT-0](https://spdx.org/licenses/MIT-0.html)
- Documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
