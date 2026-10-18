# Skill Authoring Format

This document defines the consistent format every skill in this repository must
follow (Phase 1 roadmap item). Introduce it to contributors: new skills must match
it; changes to this file should be reflected across existing skills.

## Location and Naming

```text
skills/<kebab-case-skill-name>/
├── SKILL.md
├── examples/
│   └── <scenario-name>.md    # sanitized, annotated inputs
└── tests/
    └── test-cases.md         # what a correct analysis must contain
```

- Folder and name use lowercase kebab-case (`pipeline-failure-translator`).
- One skill = one problem. If a skill covers two unrelated problems, split it.
- Optional `scripts/` folder inside a skill is allowed, but keep it minimal and
  document every script; shared scripts go in the top-level `scripts/`.

## SKILL.md Format

Every `SKILL.md` consists of:

1. **A YAML frontmatter block** with two required fields:
   - `name:` — machine-readable skill identifier, same as the folder name.
   - `description:` — one to three sentences stating *what the skill does* and
     *when the agent should load it*. This is the primary trigger for skill
     selection, so it must mention the concrete inputs a user provides (logs,
     `kubectl describe` output, etc.) rather than abstract goals.
2. **A title line** (`# <Human-readable Name>`).
3. **Role statement** — one paragraph setting the expected context and audience.
4. **Core principles** — numbered, ordered by importance. Safety principles
   (read-only by default, explicit approval for state changes) always appear here.
5. **Analysis workflow / reference material** — skill-specific guidance: how to
   read the input, which patterns matter, which variants to distinguish.
6. **Output format** — an exact response template the agent should reproduce.
7. **Pointer to examples and tests.**

### Content Rules

- **Evidence over guesses.** Every skill must require that observed facts and
  hypotheses are separated, and must specify what to do when evidence is
  insufficient (say what's missing; don't fabricate a diagnosis).
- **Safety levels are standardized** across all skills:
  - `[read-only]` — safe to run.
  - `[state-changing, needs approval]` — modifies workspace/cluster/config.
  - `[destructive/production, needs approval]` — irreversible or affects live
    traffic/data; must be rare, justified, and preceded by a blast-radius note.
- **No command that destroys state** may appear in a skill's recommended default
  steps.
- Keep `SKILL.md` focused and skimmable — it is loaded into the model's context
  when triggered. Long reference tables belong in `docs/` or in linked examples.

## Examples

Each example file contains:

1. A short intro stating the scenario and how the user presents the problem.
2. The sanitized diagnostic evidence in fenced code blocks, clearly labeled.
3. Any extra context the user volunteered (marked as such).
4. A pointer to the matching test case (never an inline answer).

Rules:

- Sanitized: no real credentials, tokens, kubeconfig contents, internal hostnames,
  IPs, or shared-secrets URLs. Use placeholders such as `registry.example.dev`,
  `node-worker-1`, `payments`.
- Minimal but realistic: enough content to exercise the diagnosis, no filler.
- One scenario per file; if you need a variant, create a second file.

## Tests

Each skill has a `tests/test-cases.md` where each case names its example and lists
the **minimum content a correct analysis must contain**, plus a "known wrong
analyses (guardrails)" list of wrong diagnoses the analysis must not make.

Tests are review prompts for humans and evaluation fixtures for scripted or
model-based checks — they are not unit tests and require no framework. Keep them
short and assertion-like.

## Checklist Before Opening a PR

- [ ] `SKILL.md` frontmatter has `name` and a `description` stating when to load.
- [ ] Output format section present and consistent with this document.
- [ ] All default steps are `[read-only]`.
- [ ] At least one sanitized example.
- [ ] `tests/test-cases.md` with pass criteria and guardrails.
- [ ] README Skills table updated (`Planned` until tested).
