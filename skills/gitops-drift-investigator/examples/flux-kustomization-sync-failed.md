# Example: Flux Kustomization Reconciliation Failed on Immutable Field

Sanitized example input for the `gitops-drift-investigator` skill. Fictional cluster
information representing an immutable field update blocking Flux reconciliation.

## Input

User message:
"Our Flux kustomization `customer-data-sync` is failing to reconcile. The pipeline deployed a new commit
and now Flux is in `ReconciliationFailed`. Here is the output of `flux get kustomization customer-data-sync`
and `flux logs --level=error`:"

`flux get kustomization customer-data-sync`:

```text
NAME                REVISION            SUSPENDED   READY   MESSAGE
customer-data-sync  main@sha1:7f4a9b1   False       False   Kustomization/customer-data-sync/analytics dry-run failed: StatefulSet.apps "analytics-db" is invalid: spec: Forbidden: updates to statefulset spec for fields other than 'replicas', 'ordinals', 'template', 'updateStrategy', 'persistentVolumeClaimRetentionPolicy' and 'minReadySeconds' are forbidden
```

`flux logs --level=error`:

```text
{"level":"error","ts":"2026-11-20T08:14:22.401Z","msg":"Reconciliation failed","controller":"kustomize-controller","kustomization":"analytics/customer-data-sync","error":"StatefulSet.apps \"analytics-db\" is invalid: spec.volumeClaimTemplates[0].spec.resources.requests.storage: Forbidden: field is immutable"}
```

Git diff in commit `7f4a9b1`:

```diff
--- a/apps/analytics/statefulset.yaml
+++ b/apps/analytics/statefulset.yaml
@@ -28,5 +28,5 @@ spec:
   volumeClaimTemplates:
   - metadata:
       name: data
     spec:
       accessModes: [ "ReadWriteOnce" ]
       resources:
         requests:
-          storage: 50Gi
+          storage: 100Gi
```

User message continuation:
"Can Flux auto-heal this or do we need to force delete the StatefulSet?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-11.
