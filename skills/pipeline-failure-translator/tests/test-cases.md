# Test Scenarios — pipeline-failure-translator

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and (later) scripted or model-based evaluation.

A scenario **passes** if an analysis covering all items marked pass, and **fails**
if the analysis asserts a root cause that is contradicted by the evidence or asserts
a High-confidence cause with none of the pass items:

- **TC-1:** `examples/gha-docker-build-failure.md`
- **TC-2:** `examples/jenkins-test-failure.md`

---

## TC-1 — GitHub Actions: Docker build failure

### Minimum correct analysis

1. Failing stage: the `Build and push` step of job `build` — not the
   login or checkout steps.
2. Relevant error extraction, at minimum one of:
   - `ERROR: Could not find a version that satisfies the requirement requests==2.99.0`
   - `ERROR: No matching distribution found for requests==2.99.0`
   - `#9 2.407 ERROR:` → `pip install -r requirements.txt` failed with `exit code: 1`
3. Classification: dependency-resolution failure, not an image-registry or
   infrastructure failure.
4. Root-cause assessment: `requests==2.99.0` pinned in `requirements.txt` does not
   match any available package (a plausible variant: an invalid version string such
   as a guessed/never-released version, or a version that was unlisted/yanked).
5. Correctly notes as *not* the root cause (evidence absent): registry auth failure,
   Dockerfile changes, network/TLS errors. The warning about buildx privileged
   mode at the end is irrelevant noise.
6. Remediation includes at least one concrete step, for example:
   - `[read-only]` check the declared version against the package index
     (`pip index versions requests` or the project's release list).
   - Fix the pin (to an existing version, or relax to a minimum version) and push.
7. Verification: re-run the workflow, or locally
   `pip install -r requirements.txt` inside a matching `python:3.11-slim`
   container before re-running CI.

### Known wrong analyses (guardrails)

- "The registry login failed" — the login step completed; there is no auth error.
- "Your Dockerfile is broken" — the COPY/entrypoint steps were canceled, not
  reported as failing; the failure occurred in the base image + pip step.
- Treat the trailing buildx warning as the failure cause.
- Claim High confidence without tying the diagnosis to the pinned version.

---

## TC-2 — Jenkins: flaky test failure

### Minimum correct analysis

1. Failing stage: `Unit tests` (also state later stages were skipped.
2. Relevant error extraction, at minimum:
   - `FAIL   payments/webhooks   webhook_retry_test.go:88`
   - `--- FAIL: TestWebhookRetryBackoff (12.04s)` and `ERROR: script returned exit code 1`
3. Classification: test failure with timing assertion (`webhook retried 3 times,
   expected 2`), not a build or dependency failure.
4. Root-cause assessment must explicitly consider that the **code-under-test
   behavior** (retry count) differs in CI and the diagnosis is only partially
   supported by evidence given; Confidence must be **Medium or Low**, and the
   analysis must name `High confidence` only if the user provides the changed lines
   or MR diff from logs alone, which is not possible.
5. Hygiene checks that the analysis recommends:
   - `[read-only]` run the single failing test locally,
     `./scripts/test.sh --scope unit payments/webhooks` (or the package's test
     target) at least 3x, before re-running the whole pipeline.
   - `[read-only]` `git log -- payments/webhooks/webhook_retry_test.go -p` or pull
     MR !37's diff to see whether the retry constant changed.
6. Notes explicitly that `Stage "Integration tests" skipped due to earlier
   failure(s)` means later stages never ran.

### Known wrong analyses (guardrails)

- Declaring High confidence that the *code change in MR !37 is broken* from this
  log alone (no link between the change and the assertion was provided).
- Recommending merge/re-run immediately as final answer without flagging that a
  repeated timing assertion may need stabilization.
- Recommending a **destructive** remediation (deleting Jenkins workspaces, force-
  pushing, disabling the stage) without marking it State-changing/destructive.
- Ignoring the fact that the retry count (3 vs 2) is an actual behavioral
  difference, not just "flakiness".
