# Shared Test Fixtures

This directory holds test material shared by more than one skill.

Per-skill test scenarios live inside each skill (`skills/<skill>/tests/`). Put
fixtures here only when a failure scenario is genuinely relevant to two or more
skills — for example, a container build failure that affects both the pipeline
translator (CI log view) and a future container-build skill.

## Conventions

- Keep every fixture **sanitized**: no real credentials, tokens, kubeconfig
  contents, internal hostnames, IPs, or project names you cannot share. Prefer
  obvious placeholders (`registry.example.dev`, `node-worker-1`, `payments`).
- Store raw evidence in plain `.log` or `.txt` files; keep interpretation in the
  skill's own `tests/test-cases.md`, not in the fixture itself.
- Name files after the scenario, not the skill:
  `<state>-<variant>.log`, e.g. `oomkilled-during-traffic.log`.
- When a fixture is shared, cross-reference it from each skill's test cases.
