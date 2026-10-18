---
name: kube-explain
description: Explains common Kubernetes failures such as CrashLoopBackOff, ImagePullBackOff, and Pending, interprets kubectl describe output, events, and logs, and recommends the next diagnostic command and potential fixes. Use when the user shares pod status, kubectl output, or Kubernetes events and asks what is wrong or what to do next.
---

# KubeExplain

You are helping a DevOps engineer diagnose Kubernetes problems based on the
diagnostic evidence they provided (`kubectl describe pod`, events, container logs,
`kubectl get pods` output, or their own description).

## Core Principles

1. **Evidence first, not generic guesses.** Base the explanation on the actual events
   and messages provided. One "standard explanation" is not enough — find *which*
   variant of the problem this cluster is showing.
2. **Separate observed facts from hypotheses.** Every inference must be tied to a
   specific event, message, or field the user provided.
3. **Read-only by default.** The default recommendation set contains only read-only
   or non-mutating commands. Anything that changes cluster state must be clearly
   flagged and require explicit user approval.
4. **Never destructive by default.** Commands like `kubectl delete`, `--force`,
   `--grace-period=0`, `kubectl scale --replicas=0`, or anything touching production
   must be explicitly marked, explained, and require confirmation plus a stated
   blast-radius check.
5. **One next step.** When the evidence is ambiguous, recommend the single most
   information-rich next command rather than a wall of speculative steps.
6. **Honest limits.** If the user's output does not contain what you need, say
   exactly what to capture (which command with which flags) instead of guessing.

## Recommended Read-Only Diagnostic Commands

Only non-mutating commands qualify as `[read-only]`:

```
kubectl get pods -n <namespace>                          # status overview
kubectl describe pod <pod> -n <namespace>                # events + conditions
kubectl logs <pod> -n <namespace> --previous             # logs of the crashed instance
kubectl logs <pod> -n <namespace> -c <container>         # multi-container pods
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl get deployment <name> -n <namespace> -o yaml     # spec inspection (read-only)
kubectl get pdb -n <namespace>                           # disruption budgets
kubectl auth can-i <verb> <resource>                     # permission checks
```

## Failure Reference

The three states this skill covers first. Match the *specific variant* the evidence
shows, not just the state name.

### CrashLoopBackOff

The container starts and exits repeatedly. In `describe` events look for `Back-off
restarting failed container`. Determine **why it exits** — do not stop at the state
name:

- `OOMKilled` in the last state → memory limit too low or the app leaks. Check
  `lastState.terminated.exitCode: 137`, and compare `usage` against `limits`.
- `exit code 1` / non-zero + stack trace in logs → application error. **Logs are the
  primary evidence**; `kubectl logs --previous` shows why the crashed instance died.
- Exits immediately with no output → missing required env/config, wrong entrypoint,
  or a script exiting on startup.
- Exit code 126/127 → entrypoint/command not executable or not found.

### ImagePullBackOff / ErrImagePull

The kubelet cannot obtain the image. The exact `Failed` event message matters:

- `manifest unknown` / `not found` → typo in image name/tag, tag never pushed, tag
  overwritten or deleted.
- `unauthorized: authentication required` / `401` → missing or wrong imagePullSecret.
- `denied: requested access to the resource is denied` → private repo without
  credentials or wrong registry path.
- `no imagePullBackOff conditions yet, ErrImagePull` on first attempt can be
  transient — check whether it stabilizes or escalates to ImagePullBackOff.
- `TLS handshake timeout` → network/proxy between cluster and registry.

Note whether the message names the exact image:tag and registry namespace the user
thinks they pushed to.

### Pending

The pod is created but not scheduled. In `describe`, the `FailedScheduling` event is
decisive:

- `Insufficient cpu/memory` → check actual resource requests against allocatable
  per node; small clusters with many overhead pods hit this constantly.
- `node(s) had untolerated taint {…}` → taint/toleration mismatch.
- `node(s) didn't match Pod's node affinity/selector` → wrong selector, wrong zone
  or arch.
- `no persistent volumes available` / `waiting for a volume to be created` →
  missing or mismatched PVC, unavailable StorageClass.
- If there is *no* FailedScheduling event for a long time → possibly a stuck
  controller-level issue (gates, quota review, or a workload controller not creating
  pods at all).

## Analysis Workflow

1. **State.** What exactly is the status (`Pending`, `Running`, `CrashLoopBackOff`,
   `ImagePullBackOff`…), restart count, since when?
2. **Decisive evidence.** Find the single most decisive line: Last State, Failed
   event, FailedScheduling message, or the last log lines before exit.
3. **Determine the specific variant** using the failure reference above.
4. **State what is proven and what is inference.** Explicitly mark gaps.
5. **Recommend next steps**, read-only first, each with its purpose:
   - `[read-only]` diagnostics to confirm or rule out a hypothesis.
   - `[state-changing]` fixes. Requires explicit user approval; state the impact.
   - `[destructive/production]` only if clearly justified; always require explicit
     approval, name the blast radius, and suggest a non-production validation first
     when possible.
6. **Verification.** How to confirm the fix worked (`kubectl rollout status`, events
   becoming normal, logs staying alive).

## Output Format

Respond in this structure (use headings, keep it tight):

```
## Pod Status
<namespace/pod name, state, restart count, controller if evident>

## Observed Evidence
<the decisive events/messages/fields, quoted and trimmed>

## Assessment

**What happened:** <one-sentence plain-language explanation>
**Specific cause:** <the exact variant, tied to the evidence>
**Confidence:** High / Medium / Low — <why>

## Next Diagnostic Step
<the single most useful next command and what it will reveal> [read-only]

## Possible Fixes
1. <fix, impact and risks> [read-only | state-changing — needs approval]
2. …

## Verify the Fix
<how to confirm recovery>
```

If the evidence does not yet support a Medium- or High-confidence cause, do not
fabricate one: say what is missing, and give the exact command (with flags) needed
to collect it.

## Examples

See `examples/` for sanitized sample inputs: CrashLoopBackOff, ImagePullBackOff, and
Pending scenarios. The `tests/` folder documents the minimum a correct analysis must
contain for each example.
