# Safety Guidelines

Applies to everything in this repository: skills, examples, tests, scripts, and
contributions. This is part of the Phase 1 foundation.

## Sharing Diagnostic Data

CI/CD logs and `kubectl` output routinely contain more than you notice at paste
time:

- Registry credentials and base64-encoded `imagePullSecrets`.
- Bearer tokens and API keys in URLs, headers, or `Authorization` lines.
- Internal hostnames, node names, IP addresses, and cloud account IDs.
- Environment variable dumps that include database URLs.

**Rules:**

1. Never commit credentials, tokens, kubeconfig files, or unsanitized logs.
2. Sanitize before sharing with any external model provider — use
   [`scripts/sanitize.py`](../scripts/sanitize.py) for common patterns, then
   review manually. Scripts help; they are not a substitute for reading.
3. Prefer small extracts over full logs: paste the relevant section plus enough
   surrounding lines to give timing/step context.

## What Skills Are Allowed to Recommend

| Level | Meaning | Allowed as default step? |
|---|---|---|
| `[read-only]` | Non-mutating diagnostics (`describe`, `logs`, `get`) | Yes |
| `[state-changing, needs approval]` | Changes workspace, cluster, or config | Only when clearly the fix; always marked |
| `[destructive/production, needs approval]` | Irreversible or touches live traffic/data | Never as a first suggestion |

Skills must:

- Prefer read-only diagnostics and verification before fixes.
- Mark every state-changing step explicitly and state the impact.
- Require explicit approval for destructive operations or production changes.
- Refuse to store or repeat secrets from sanitized inputs.

## For Skill Authors

- No recommended command may destroy state by default (delete, force, drain,
  `--grace-period=0`, `scale --replicas=0`, cache annihilation, etc.).
- If such a command is genuinely the right move, present it last, labeled
  `[destructive/production, needs approval]`, with the blast radius stated and a
  safer validation path first (non-production, dry-run, preview).
- Use the standard safety levels (see `docs/skill-authoring.md`) so users can scan
  risk quickly.

## For Users

AI-generated diagnoses can be wrong. Always verify critical findings against the
actual system state, and never let an agent's suggestion bypass your own
judgment — review every command before you run it.
