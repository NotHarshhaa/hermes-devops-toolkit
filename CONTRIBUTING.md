# Contributing to Hermes DevOps Toolkit

Thank you for considering a contribution! This project grows one focused skill at a
time, and contributions of all sizes are welcome — from a typo fix to a brand-new
troubleshooting skill.

Please note this is an independent community project and is **not** affiliated with
or endorsed by Nous Research.

## Ways to Contribute

- Suggest a specific DevOps problem worth solving (open an issue first).
- Add reproducible, sanitized troubleshooting examples.
- Improve diagnostic instructions in existing skills.
- Write tests for known failure scenarios.
- Report incorrect or unsafe recommendations.
- Propose new, self-contained skills.

## Ground Rules

1. **Check existing issues first.** Before starting work on a new skill or a large
   change, check issues and discussions to avoid duplicate effort.
2. **One problem, one skill.** Each skill solves one specific engineering problem.
   If a skill is drifting into two problems, split it.
3. **Evidence over guesses.** Skills must separate observed facts from inferred
   causes, and must be honest when the evidence is insufficient.
4. **Safe by default.** Prefer read-only diagnostics. Potentially destructive or
   state-changing operations must require explicit user approval, and must never be
   suggested as a default step.
5. **No secrets, ever.** Never commit credentials, tokens, kubeconfig files, or
   unsanitized logs. CI/CD logs and `kubectl` output routinely contain secrets —
   sanitize them before they are added anywhere in this repository. You can use
   `scripts/sanitize.py` to redact common secret patterns.

## Getting Started

```bash
git clone <your-fork-url>
cd hermes-devops-toolkit
```

No build step is required — skills are Markdown (`SKILL.md`) files plus example and
test material. See [`docs/skill-authoring.md`](docs/skill-authoring.md) for the
format each skill must follow.

## Adding a New Skill

A minimal new skill looks like this:

```text
skills/<your-skill-name>/
├── SKILL.md          # Frontmatter + instructions (see docs/skill-authoring.md)
├── examples/         # At least 1–2 sanitized real-world-style examples
└── tests/            # Test scenarios with expected diagnostic outcomes
```

Before opening a PR for a new skill, please make sure:

- [ ] `SKILL.md` follows the format in `docs/skill-authoring.md`.
- [ ] The `description` in the frontmatter clearly states *when* Hermes should load
      the skill (this is how skill selection works).
- [ ] All diagnostic steps are read-only by default.
- [ ] Examples are fully sanitized (no URLs with tokens, no real hostnames, IPs, or
      account/project names you cannot share).
- [ ] At least one test scenario documents the expected analysis outcome.
- [ ] The skill has a row in the README's Skills table (status: `Planned` until it
      is tested against representative input).

## Writing Examples and Tests

Examples are shared diagnostic inputs (`*.log`, `*.txt`, `*.md`) that a skill can be
exercised against. Tests describe, for a given example, what a correct analysis must
identify at minimum. They are reviewed by humans and used as prompts for manual (and
future automated) evaluation — they do not require a test framework. See
[`tests/README.md`](tests/README.md) for details.

## Commit and PR Style

- Use clear, imperative commit messages (`Add CrashLoopBackOff example`, not
  `added stuff`).
- Keep PRs focused: one skill, one example set, or one documentation change per PR.
  This makes review much faster.
- Update the README (Skills table and/or Roadmap) when your change affects the
  project's public description.

## Reporting Problems

When reporting an incorrect or unsafe recommendation, include:

- The skill and version (or commit) involved.
- The sanitized input/output that triggered the issue.
- What you expected versus what happened.
- For safety issues: what could go wrong if the recommendation were followed.

Please **always sanitize logs before posting them publicly.**

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE) of this project.
