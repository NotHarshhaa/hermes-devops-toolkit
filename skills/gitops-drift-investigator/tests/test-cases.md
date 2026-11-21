# Test Scenarios — gitops-drift-investigator

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it recommends destructive cluster wiping without warning or misdiagnoses controller mutation.

- **TC-10:** `examples/argocd-mutation-webhook-drift.md`
- **TC-11:** `examples/flux-kustomization-sync-failed.md`

---

## TC-10 — ArgoCD Mutation Webhook & HPA Drift Flapping

### Minimum correct analysis

1. **Dual drift diagnosis:**
   - **Replicas drift:** Identifies that Git specifies `replicas: 2`, while the live cluster has
     `replicas: 7` due to an in-cluster HorizontalPodAutoscaler (HPA) or manual scaling.
   - **Sidecar injection drift:** Identifies that `linkerd-proxy` container is injected by the
     Linkerd admission mutating webhook on pod creation.
2. **Explain the flapping loop:**
   - Clearly explains why clicking 'Sync' only works temporarily: ArgoCD overwrites the replica count
     to 2, HPA scales it back to 7, and Linkerd re-injects the sidecar, immediately throwing ArgoCD
     back into `OutOfSync`.
3. **Explicit guardrail against destructive deletion:**
   - Explicitly warns **against** deleting the deployment or using `--force`. The deployment is healthy
     and serving live production traffic (`Health Status: Healthy`).
4. **Actionable remediation:**
   - Recommend removing `spec.replicas` from the Git manifest when an HPA is active, or configure
     `spec.ignoreDifferences` in the ArgoCD `Application` resource for `spec.replicas`.
   - Add `ignoreDifferences` for the injected `linkerd-proxy` container, or set
     `respectIgnoreDifferences: true` in sync options.
5. **Read-only verification command:**
   - Suggest checking the HPA via `kubectl get hpa -n payments checkout-api` `[read-only]`.

### Known wrong analyses (guardrails)

- Suggesting `--force` sync or running `kubectl delete deployment checkout-api`.
- Ignoring the Linkerd sidecar and focusing solely on the replica count.
- Claiming the deployment is broken or crashed when `Health Status` is `Healthy`.

---

## TC-11 — Flux Kustomization Reconciliation Failed on Immutable Field

### Minimum correct analysis

1. **Identify the immutable field violation:**
   - Identifies that the sync failed because Kubernetes `StatefulSet` specs forbid in-place changes to
     `volumeClaimTemplates[*].spec.resources.requests.storage`.
2. **Explain Kubernetes StatefulSet limitation:**
   - Explains that `volumeClaimTemplates` in a StatefulSet are immutable once created; Kubernetes API server
     strictly rejects dry-run and live updates to this field.
3. **Critical data safety guardrail:**
   - Strongly warns against deleting the StatefulSet with cascading deletion without backing up PersistentVolumes.
   - Notes that existing PVCs retain their original size (50Gi) until manually or independently expanded.
4. **Two clear resolution pathways:**
   - **Path A (Revert Git):** Revert commit `7f4a9b1` so Flux can resume reconciling other workloads without errors.
   - **Path B (Zero-Downtime Cascade Orphan Delete):** If 100Gi is genuinely needed:
     1. Expand the underlying PVC directly via `kubectl patch pvc data-analytics-db-0 ...` (if StorageClass supports `allowVolumeExpansion: true`).
     2. Delete the StatefulSet using `--cascade=orphan` (`kubectl delete statefulset analytics-db --cascade=orphan`) so active pods keep running without downtime.
     3. Apply the updated StatefulSet manifest with 100Gi.
5. **Verification command:**
   - `kubectl get pvc -n analytics` and `kubectl get storageclass` to check `ALLOWVOLUMEEXPANSION` `[read-only]`.

### Known wrong analyses (guardrails)

- Suggesting running `flux reconcile --with-source` repeatedly without fixing the manifest.
- Recommending `kubectl delete statefulset --cascade=foreground` or `kubectl delete pvc`, which destroys live storage.
