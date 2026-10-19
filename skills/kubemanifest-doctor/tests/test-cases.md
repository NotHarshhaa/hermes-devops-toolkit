# Test Scenarios — kubemanifest-doctor

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it ignores security/reliability flaws or misses the selector mismatch and deprecated API.

- **TC-12:** `examples/insecure-missing-resources-deployment.md`
- **TC-13:** `examples/deprecated-apis-and-selector-mismatch.md`

---

## TC-12 — Insecure Deployment with Missing Resources & Flawed Probes

### Minimum correct analysis

1. **Missing resource constraints:**
   - Flags complete absence of `resources.requests` and `resources.limits`.
   - Explains that the pod will receive `BestEffort` QoS, putting it at first priority
     for OOM and eviction when node pressure occurs.
2. **Liveness probe anti-pattern:**
   - Identifies that `/health/deep-db-check` queries the database inside a **livenessProbe**.
   - Explains the cascading failure risk: if the database is under load or briefly restarts,
     kubelet will kill and restart the app pod, aggravating cluster storm instead of letting
     traffic back off.
   - Points out `initialDelaySeconds: 2` is too low given the app's 10-second startup time,
     guaranteeing immediate CrashLoopBackOff before the container is ready.
   - Recommends separating a simple shallow HTTP endpoint (`/healthz` or `/live`) for liveness
     and using readiness for dependency checks, or adding a `startupProbe`.
3. **Security posture deficiencies:**
   - Flags missing `securityContext`: container runs as root by default (`runAsNonRoot: true` missing),
     writable root filesystem, and missing capability drops.
4. **Reliability:**
   - Flags single replica (`replicas: 1`), presenting a single point of failure during node maintenance.
5. **Concrete remediation:**
   - Provides corrected YAML with `resources`, hardened `securityContext`, adjusted probes,
     and multi-replica deployment.

### Known wrong analyses (guardrails)

- Claiming the manifest is completely ready for production without mentioning resources or security.
- Approving a database check in the liveness probe.
- Suggesting deleting the readiness probe altogether instead of decoupling it.

---

## TC-13 — Deprecated Ingress API and Service Selector Mismatch

### Minimum correct analysis

1. **Deprecated API version:**
   - Identifies `networking.k8s.io/v1beta1` for `Ingress` is deprecated and removed in modern
     Kubernetes (1.22+).
   - Shows how to convert to `networking.k8s.io/v1`, replacing `backend.serviceName` and
     `backend.servicePort` with `backend.service.name` and `backend.service.port.number`.
   - Notes `pathType` (e.g. `pathType: Prefix`) must be specified in `v1`.
2. **Service selector mismatch:**
   - Points out the silent disconnection between Service and Deployment:
     - Service selector has: `app.kubernetes.io/name: customer-portal`
     - Deployment template labels have: `app: customer-portal`
   - Explains that the Service will find **0 endpoints**, causing all HTTP requests to return 503
     or connection refused.
3. **Target port check:**
   - Verifies that `targetPort: 3000` matches `containerPort: 3000`.
4. **Concrete remediation:**
   - Provides the updated `networking.k8s.io/v1` Ingress spec.
   - Provides the aligned labels in Service or Deployment.
5. **Validation command:** Recommends running `kubectl apply --dry-run=client -f ingress-and-service.yaml`
   `[read-only]`.

### Known wrong analyses (guardrails)

- Failing to catch the selector mismatch (`app.kubernetes.io/name` vs `app`).
- Claiming `networking.k8s.io/v1beta1` is valid on Kubernetes 1.28.
- Missing required `pathType` in the updated `networking.k8s.io/v1` Ingress.
