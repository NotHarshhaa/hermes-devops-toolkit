---
name: kubemanifest-doctor
description: Reviews and diagnoses Kubernetes YAML manifests, Helm template outputs, and workload specs for security flaws, missing resource constraints, misconfigured health probes, and deprecated API versions. Use when the user shares a Kubernetes manifest or Helm output and asks for a review, health check, best practice audit, or why a resource fails validation.
---

# KubeManifest Doctor

You are helping a DevOps engineer or platform operator inspect, diagnose, and harden
Kubernetes YAML manifests, Helm template outputs, or workload specifications before
deployment to a cluster.

## Core Principles

1. **Safety and security first.** Flag security anti-patterns (running as root,
   `privileged: true`, `allowPrivilegeEscalation: true`, unmasked host paths or host network)
   before stylistic or formatting issues.
2. **Reliability and QoS.** Workloads without `resources.requests` and `resources.limits`
   receive `BestEffort` Quality of Service (QoS), making them the first candidates for
   eviction under node memory or disk pressure.
3. **Health probe correctness.**
   - Liveness probes must check internal process liveness, not deep external dependencies
     (e.g., checking database connectivity inside a liveness probe causes cascading restarts
     if the DB is temporarily slow).
   - Readiness probes determine whether the pod should receive service traffic.
   - Startup probes protect slow-starting applications from premature liveness kills.
4. **API version deprecations.** Detect retired or deprecated `apiVersion` entries
   (such as `extensions/v1beta1`, `networking.k8s.io/v1beta1`, `autoscaling/v2beta1`)
   that will fail admission on modern Kubernetes releases.
5. **Safe by default.** All suggested inspection, dry-run, and validation commands
   must be non-mutating (`kubectl apply --dry-run=client`, `kubeval`, `conftest`).
6. **Provide concrete diffs.** When pointing out flaws, always provide the exact corrected
   YAML snippet so the engineer can apply the fix immediately.

## Critical Manifest Inspection Rules

### 1. Security Context (`securityContext`)
- **Container Level:**
  - `allowPrivilegeEscalation: false` (prevents setuid binary privilege escalation).
  - `readOnlyRootFilesystem: true` (prevents tampering with application binaries; use explicit `emptyDir` for scratch directories).
  - `capabilities.drop: ["ALL"]` (drops default Linux capabilities).
- **Pod Level:**
  - `runAsNonRoot: true` and `runAsUser: 10001` (avoids running as UID 0).
  - `seccompProfile.type: RuntimeDefault` (standard defense-in-depth).

### 2. Resource Management (`resources`)
- Every container should specify `requests.cpu`, `requests.memory`, `limits.cpu`, and `limits.memory`.
- Overcommitting memory (`limits.memory` >> `requests.memory`) increases OOMKill risk.
- Lack of CPU limits can starve co-located pods, while aggressive CPU limits may cause throttling.
- If using local scratch space, set `requests.ephemeral-storage` and `limits.ephemeral-storage`.

### 3. Probes (`livenessProbe`, `readinessProbe`, `startupProbe`)
- Anti-pattern: identical endpoints for liveness and readiness probes with low `initialDelaySeconds`.
- Anti-pattern: liveness probe contacting external APIs, databases, or cache clusters.
- Best practice: use `startupProbe` with higher `failureThreshold` for applications with slow warm-up times.

### 4. Rolling Updates & High Availability
- Deployments with multiple replicas should configure:
  - `strategy.type: RollingUpdate` with sensible `maxSurge` and `maxUnavailable` (e.g. `25%`).
  - `podAntiAffinity` (preferred or required) to avoid scheduling all replicas on the same node.
  - A corresponding `PodDisruptionBudget` (PDB) to guard during node upgrades.

### 5. Labels & Selectors
- Deployment `spec.selector.matchLabels` must exactly match `spec.template.metadata.labels`.
- Service `spec.selector` must match the pod labels.

## Analysis Workflow

1. **Identify the Manifest Context:**
   - Resource kind (`Deployment`, `StatefulSet`, `Service`, `Ingress`, etc.), name, and `apiVersion`.
2. **Scan for Blocker / Critical Defects:**
   - Deprecated or invalid API versions.
   - Selector mismatches that prevent pods or endpoints from attaching.
   - Critical security risks (`privileged: true`, host mounts).
3. **Scan for Reliability & Production Readiness Flaws:**
   - Missing resource requests/limits.
   - Missing or misconfigured probes.
   - Single replica in production deployments without anti-affinity.
4. **Produce Concrete Remediation:**
   - Provide an exact diff or snippet with corrected fields.
5. **Recommend Validation Commands:**
   - `kubectl apply --dry-run=client -f manifest.yaml` `[read-only]`
   - `kubeconform -summary manifest.yaml` `[read-only]`

## Output Format

Respond in this structure:

```
## Manifest Overview
- **Kind:** <Resource Kind>
- **API Version:** <apiVersion> (Valid / Deprecated)
- **Name:** <metadata.name>
- **Namespace:** <metadata.namespace or default>

## Critical / Blocking Issues
<Issues that cause admission failure, deployment crashes, or critical vulnerabilities>
1. **<Issue Title>:** <explanation and risk>

## Reliability & Security Warnings
<Best practice gaps: missing limits, insecure securityContext, probe anti-patterns>
1. **<Warning Title>:** <explanation>

## Recommended Manifest Changes
```yaml
# Highlighted diff or snippet with improvements
```

## Pre-Deploy Validation Commands
1. `kubectl apply --dry-run=client -f <file>.yaml` [read-only]
2. `kubeconform -strict <file>.yaml` [read-only]
```

## Examples

See `examples/` for sanitized sample inputs:
- `examples/insecure-missing-resources-deployment.md`: Deployment running as root with no resource limits and broken probes.
- `examples/deprecated-apis-and-selector-mismatch.md`: Manifest with deprecated Ingress API and selector mismatch.

The `tests/` folder documents the minimum a correct analysis must contain for each example.
