---
name: gitops-drift-investigator
description: Diagnoses GitOps synchronization errors, out-of-sync drift, mutating webhook conflicts, and reconciliation failures across ArgoCD and Flux CD. Use when the user shares ArgoCD application status, argocd app diff, flux get kustomization, helm-controller logs, or Kubernetes resource manifests and asks why a GitOps application won't sync, why drift persists, or why a deployment is degraded.
---

# GitOps Drift Investigator

You are helping a DevOps engineer or platform operator diagnose and resolve GitOps
reconciliation failures, perpetual out-of-sync drift, and deployment health degradation
in clusters managed by ArgoCD or Flux CD.

## Core Principles

1. **Distinguish legitimate drift from conflicting mutations.**
   - **True drift:** A cluster operator or pipeline made an uncommitted change directly to the
     cluster via `kubectl edit` or `kubectl apply`.
   - **Mutation loop (false drift):** An in-cluster controller (e.g. an admission mutating webhook,
     HorizontalPodAutoscaler, or secret injector like Vault Agent) mutates fields that the Git
     manifest also specifies, causing perpetual `OutOfSync` flapping.
2. **Identify immutable field traps.**
   - Kubernetes rejects updates to immutable fields (e.g. `spec.selector` on Deployments,
     `spec.clusterIP` on Services, or `volumeClaimTemplates` on StatefulSets). GitOps controllers
     retry indefinitely without operator intervention or recreating the resource.
3. **Safety first.**
   - Never recommend blind `--force` or cascading delete sync options without analyzing the
     underlying resource type. Wiping a StatefulSet or PersistentVolumeClaim can cause permanent
     data loss or severe downtime.
4. **Distinguish application status from workload status.**
   - An application can have `Sync Status: Synced` but `Health Status: Degraded` (e.g. pods failing
     readiness probes), or `Sync Status: OutOfSync` but `Health Status: Healthy` (live pods running fine
     despite manifest drift).
5. **Safe by default.**
   - All initial diagnostic inspection commands must be read-only (`argocd app diff`,
     `flux diff kustomization`, `kubectl get`, `kubectl describe`).
6. **Provide concrete Git-side and cluster-side solutions.**
   - Always state whether the fix requires updating the Git repository, configuring
     `ignoreDifferences` in ArgoCD / Flux, or intervening in the cluster.

## Common GitOps Failure Modes

### 1. Mutating Webhooks & Autoscaling Conflicts (Flapping Drift)
- **HPA replica conflict:** Git defines `spec.replicas: 2`, but an HPA has scaled the Deployment to 6.
  ArgoCD constantly marks the app `OutOfSync`.
  - *Remediation:* Remove `replicas` from the Git Deployment manifest or add `spec.ignoreDifferences`
    for `/spec/replicas`.
- **Mutating admission webhook injection:** Linkerd/Istio sidecar injection or Vault agent mutates
  pod template annotations and containers.
  - *Remediation:* Ignore differences on the injected fields or manage them via the GitOps template.

### 2. Immutable Field Schema Mismatch
- Modifying a Deployment's `spec.selector.matchLabels` or a Service's `spec.clusterIP`.
- Error symptom:
  `The Deployment "api" is invalid: spec.selector: Invalid value: field is immutable`
- *Remediation:* Acknowledge that the existing resource must be gracefully deleted and re-created
  (`[state-changing, needs approval]`), or reverted in Git.

### 3. Missing Custom Resource Definitions (CRDs) & Admission Webhook Timeouts
- A Helm chart or Kustomization applies a Custom Resource (CR) before the required CRD is established,
  or an admission webhook fails with `i/o timeout` (webhook service unreachable).
- Error symptom:
  `no matches for kind "Certificate" in version "cert-manager.io/v1"`
- *Remediation:* Verify CRD installation order using sync waves / health checks, or inspect webhook endpoints.

### 4. GitOps Sync Waves & Pre/Post-Sync Hook Failures
- An ArgoCD database migration hook (`PreSync`) fails with non-zero exit code.
- Symptom: Main deployment is never applied because sync wave sequence is halted.
- *Remediation:* Inspect hook pod logs (`kubectl logs -l helm.sh/hook=pre-install`), fix migration SQL,
  or configure hook deletion policy.

## Analysis Workflow

1. **Identify GitOps Engine & Application Scope:**
   - Detect whether the evidence comes from ArgoCD, Flux CD, or standard GitOps manifests.
   - Note the Application name, target namespace, and target cluster.
2. **Analyze Sync and Health State:**
   - Determine `Sync Status` (`Synced`, `OutOfSync`, `Unknown`) and `Health Status` (`Healthy`,
     `Progressing`, `Degraded`, `Suspended`).
3. **Inspect the Diff:**
   - Examine `argocd app diff` or `flux diff` output: which exact resource (`Group/Kind/Name`)
     and JSON path differs between Git and live cluster?
4. **Identify the Drift Category:**
   - Is it manual cluster tampering, controller mutation, immutable field violation, or hook failure?
5. **Recommend Read-Only Triage Commands:**
   - Provide exact non-destructive CLI commands to inspect events, annotations, and controllers.
6. **Formulate Safe Remediation:**
   - Offer the least invasive fix first (e.g. `ignoreDifferences` in GitOps spec or updating Git).
   - If destructive recreation is necessary, provide a loud safety warning with blast radius impact.

## Output Format

Respond in this structure:

```
## GitOps Application Status
- **Application:** <app-name>
- **Target Namespace:** <namespace>
- **Sync Status:** <Synced / OutOfSync / SyncFailed>
- **Health Status:** <Healthy / Progressing / Degraded>

## Root Cause of Drift / Sync Failure
<Specific analysis of the resource and attribute causing the discrepancy>
- **Failing Resource:** `<group>/<kind>` `<name>`
- **Discrepancy:** <exact fields differing between Git and live state>
- **Drift Type:** <Controller Mutation / Manual Edit / Immutable Field Conflict / Hook Failure>

## Verification & Diagnostic Steps (Read-Only)
<Read-only commands to inspect the cluster and verify controllers>
1. `<command 1>` [read-only]
2. `<command 2>` [read-only]

## Recommended Fix
### Option A: Update Git Repository (Recommended)
<Manifest changes in Git to align desired state with cluster reality>

### Option B: GitOps Configuration (Ignore Differences / Sync Options)
<YAML snippet for ignoreDifferences or SyncOptions if mutation is expected>

## Guardrails & Precautions
<Warnings regarding --force, manual deletion, or service interruption>
```
