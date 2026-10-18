# Test Scenarios — kube-explain

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and (later) scripted or model-based evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it asserts a root cause contradicted by the evidence or asserts High confidence
without the corresponding pass items.

- **TC-3:** `examples/crashloopbackoff-oomkilled.md`
- **TC-4:** `examples/imagepullbackoff-wrong-tag.md`
- **TC-5:** `examples/pending-insufficient-memory.md`

---

## TC-3 — CrashLoopBackOff, OOMKilled

### Minimum correct analysis

1. State: `CrashLoopBackOff`, 8 restarts, roughly ~15–17 min between kills.
2. Decisive evidence: `Last State: Terminated / Reason: OOMKilled / Exit Code: 137`
   with `memory: 512Mi` limit.
3. Interpretation: the process's memory usage exceeded the container limit; this is
   consistent with the recently deployed cache-layer change (1.9.0 deploy note).
4. **Must** recommend as the next diagnostic step:
   `kubectl logs api-server-7d9f6c8b5-x2m4k --previous -n payments` 
   `[read-only]`, or `kubectl top pod -n payments`
   `[read-only]` — to confirm it is a steady-state growth vs. a startup spike.
5. Possible fixes must include at least one of:
   - Raise the container memory limit (e.g. to 768Mi–1Gi) — `[state-changing,
     needs approval]`, noting it changes pod bandwidth/cost per-pod.
   - Cap the cache size / configure cache eviction in the app — `[state-changing,
     needs approval]`, code/config change not directly presented here; the user
     must decide based on app docs.
6. Must state that the deploy note (cache holding more items) is a **hypothesis**
   not proven by the pasted data; proven facts are limit + OOMKilled + spacing.

### Known wrong analyses (guardrails)

- "Exit code 137 means SIGKILL, your container was killed externally by the
  scheduler eviction" as a competing cause with equal weight (no eviction events in
  the excerpt; the reason is OOMKilled inside the container cgroup, and this is the
  standard `OOMKilled` pattern).
- Recommending `kubectl delete pod` as the primary remediation without noting it
  only restarts the pod without fixing the limit.
- Emphasizing `CrashLoopBackOff` as the diagnosis and ending there without naming
  the variant (OOMKilled).

---

## TC-4 — ImagePullBackOff, wrong tag

### Minimum correct analysis

1. State: `ImagePullBackOff`, new ReplicaSet pods failing, old ReplicaSet pods
   (`checkout-6d4f5a8b3-…`) still Running.
2. Decisive evidence: the `Warning  Failed` event with
   `manifest unknown: manifest unknown`.
3. Interpretation: **the kubelet reached the registry and was refused because no
   manifest exists under that reference**.
4. Must correctly relate this to the user's belief that CI succeeded:
   - Evidence actually provided: CI push log excerpt was provided by the user
     (`docker push ... :v2.4.1` succeeded) — the analysis may treat this as
     plausible but should note that CI *tagging* succeeded while the registry has
     no manifest under that exact path; possible variants include:
     - the push went to a different registry/namespace/project than the one the
       deployment requests (e.g. a staging path vs. the path in the manifest);
       with the provided data this is **unverifiable**, and Confidence should be
       Medium;
     - the tag was later overwritten/deleted (less supported by given evidence).
5. Must recommend as next diagnostic step a **read-only** registry-side check, e.g.
   list tags of `team-acme/checkout-service` in the registry UI or via a read-only
   API/tool, to see whether `v2.4.1` (or the intended digest) exists under the
   exact path requested, *plus* a diff between the path CI pushed to and the path
   the deployment references.
6. Possible fixes must include at least one of:
   - Fix the path/tag mismatch in the deployment manifest or pipeline
     (`[state-changing, needs approval]`).
   - Re-tag/re-push, or pin by digest
     (`[state-changing, needs approval]`).
7. Must note that the old pod still serves traffic, so impact is currently limited
   to new rollouts.

### Known wrong analyses (guardrails)

- Claiming the registry credentials are broken / `regcred-team-acme` is wrong:
  `manifest unknown` is not an auth failure (`unauthorized`,
  `denied: requested access…`). Big guardrail.
- Claiming a network/TLS problem — no timeout/handshake errors in evidence.
- Telling the user to "just delete the pod" as the primary action — this only
  re-pulls the same failing image.
- Asserting High confidence that tag was deleted without any evidence of a
  retention policy or an overwrite in the provided data.

---

## TC-5 — Pending, insufficient memory requests

### Minimum correct analysis

1. State: `Pending`, `FailedScheduling` observed 6 times over 9m.
2. Decisive evidence: `0/3 nodes are available: 1 node(s) had untolerated taint
   {node-role.kubernetes.io/control-plane: }, 2 Insufficient memory.`
3. Interpretation: the two worker nodes do not have 3Gi of unallocated memory and
   therefore cannot satisfy the 3Gi request; the control-plane node is excluded by
   its taint (correctly reported as normal, not a bug).
4. Consistency check against the user's `kubectl top node` excerpt: both workers
   are at ~90% memory utilization, and the newly deployed database pods
   (per the user's note) have **no resource requests** — so they can consume
   unbounded memory and compete with the scheduling decision. The analysis must
   connect these pieces; it is fair to note the correlation
   (new DB deployment → nodes' memory filled up → requests can no longer fit).
5. Next diagnostic step: `[read-only]`
   `kubectl top pod -n <namespace-of-new-db> --sort-by=memory` and
   `kubectl describe node <worker>` (to see allocated vs. requested memory) to
   verify that hypothesis.
6. Possible fixes must include at least one of:
   - Set proper `requests.memory`/`limits.memory` on the uncapped database pods
     (`[state-changing, needs approval]`) — flagged as a change to workload
     resource scheduling behavior, and boom-radius noted (may evict other pods).
   - Lower the dashboard request (e.g. 3Gi → 1Gi) if realistic
     (`[state-changing, needs approval]`).
   - Add a worker node / capacity (`[state-changing = infra level], needs approval`).
7. Must NOT recommend pod eviction or node drains in any default list (should be
   avoided; at most flagged `[destructive/production`, approval-required`, and
   discouraged).

### Known wrong analyses (guardrails)

- "The control-plane taint is the problem, add tolerations to the pod" — that node
  is not meant to take these workloads, and the actual blocker is `Insufficient
  memory` on the two remaining schedulable nodes.
- Claiming "the image is missing / node is NotReady" — no such event; scheduling
  reached all 3 nodes and was refused for explicit reasons.
- Recommending removing the taint from the control-plane node as a first action
  (unsafe by default in most setups).
- Saying "the `top` 90% memory utilization means the node is full, but only 2
  nodes available" while neglecting the **requests vs. actual usage** distinction
  (the new DB pods have no requests — that's the scheduling blindspot the user's
  own note highlights).
