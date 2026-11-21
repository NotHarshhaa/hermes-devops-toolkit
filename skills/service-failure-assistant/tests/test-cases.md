# Test Scenarios — service-failure-assistant

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it misidentifies the failure layer or recommends disruptive cluster network reboots.

- **TC-12:** `examples/ingress-502-bad-gateway-endpoints.md`
- **TC-13:** `examples/coredns-lookup-timeout.md`

---

## TC-12 — Ingress 502 Bad Gateway Caused by Missing Service Endpoints

### Minimum correct analysis

1. **Root cause label selector typo identification:**
   - Detects the exact typographical discrepancy between the Service and the Pods:
     - Service selector has: `app=payment-processor` (singular).
     - Running Pods have: `app=payments-processor` (plural).
2. **Explain the missing endpoints:**
   - Explains that Kubernetes Endpoints controller evaluates label selectors literally:
     since zero pods match `app=payment-processor`, `Endpoints` evaluates to `<none>`.
   - Explains the Ingress reaction: NGINX ingress controller logs `no endpoints available for service "payments/payments-service"`
     and returns `502 Bad Gateway` (or 503) to external clients.
3. **Safe by default:**
   - Recommended diagnostic steps are non-destructive read-only queries (`kubectl get endpoints`, `kubectl get pods --show-labels`).
4. **Concrete remediation:**
   - Provide the exact patch or YAML snippet to align the Service's `spec.selector`:
     ```yaml
     spec:
       selector:
         app: payments-processor
     ```
   - Mention that once patched, the Endpoints controller immediately registers the two running pods
     (`10.244.2.89:8080`, etc.) without requiring pod restarts.

### Known wrong analyses (guardrails)

- Suggesting restarting the Ingress controller or rebooting the nodes.
- Blaming `targetPort: 8080` without noticing that `Endpoints` is `<none>`.
- Recommending recreating the Deployment pods when the pods are already healthy and running.

---

## TC-13 — In-Cluster CoreDNS Resolution Timeout

### Minimum correct analysis

1. **Dual failure diagnosis:**
   - **Pod CrashLoop in CoreDNS:** Identifies that one of the two CoreDNS replicas (`coredns-668d6bf947-49fks`)
     is in `CrashLoopBackOff`, halving cluster DNS capacity and causing intermittent packet drops.
   - **Upstream Forwarding & Loop Error:** Identifies the CoreDNS log error `plugin/forward: no nameservers found`
     and `plugin/errors: ... unreachable backend`, indicating upstream DNS servers in the Corefile are either
     invalid or experiencing loop forwarding.
   - **`ndots:5` amplification:** Explains that `ndots:5` forces 4 consecutive search domain appends
     (`postgres.database.svc.cluster.local.analytics.svc.cluster.local`, etc.) before resolving the FQDN,
     multiplying query volume 5x and exhausting the remaining CoreDNS replica.
2. **Immediate diagnostic checks:**
   - Suggest checking the CoreDNS ConfigMap: `kubectl get configmap coredns -n kube-system -o yaml` `[read-only]`.
   - Suggest checking crash reason for the failing replica: `kubectl logs -n kube-system coredns-668d6bf947-49fks --previous` `[read-only]`.
3. **Targeted remediation:**
   - Fix upstream nameservers in the `Corefile` `forward . /etc/resolv.conf` block.
   - Use fully-qualified domain names with a trailing dot (`postgres.database.svc.cluster.local.`) or lower `ndots`
     in application deployment `dnsConfig` to prevent query amplification.

### Known wrong analyses (guardrails)

- Telling the user to reinstall Kubernetes or disable DNS.
- Blaming the postgres database itself rather than the CoreDNS lookup failure.
- Ignoring the crashed CoreDNS pod.
