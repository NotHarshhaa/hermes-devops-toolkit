# Hermes DevOps Toolkit

**Focused, AI-assisted DevOps troubleshooting skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent).**

Hermes DevOps Toolkit is an open-source collection of small, reusable skills that help DevOps engineers diagnose common CI/CD, Kubernetes, and cloud-native problems faster.

Instead of building another standalone AI agent or automation platform, this project extends the existing Hermes Agent with practical troubleshooting skills written in the standard `SKILL.md` format.

The goal is simple: **spend less time investigating errors and more time fixing the actual problem.**

> This is an independent community project and is not affiliated with or endorsed by Nous Research.

## Why This Project?

DevOps engineers regularly lose time searching through logs, documentation, configuration files, and command output.

Common examples:

- CI/CD pipelines failing with confusing error messages.
- Kubernetes pods stuck in `CrashLoopBackOff`, `ImagePullBackOff`, or `Pending`.
- Infrastructure configuration errors that are hard to interpret.
- Repeated troubleshooting tasks that benefit from consistent diagnostic guidance.

This toolkit tackles these with small, focused skills that can be developed, tested, and maintained independently.

## Skills

The toolkit currently ships nine skills.

| Skill | Description | Status |
|---|---|---|
| Pipeline Failure Translator | Analyzes CI/CD failure logs, identifies likely root causes, and suggests fixes. | Implemented |
| KubeExplain | Explains common Kubernetes failures and recommends diagnostic steps. | Implemented |
| Terraform Plan Explainer | Analyzes Terraform plans, flags forced replacements and blast radius risks. | Implemented |
| Docker Cleanup Advisor | Recommends prioritized, safe Docker disk space reclamation without data loss. | Implemented |
| DiskPressure Detective | Diagnoses Kubernetes node DiskPressure, eviction thresholds, and storage leaks. | Implemented |
| KubeManifest Doctor | Audits Kubernetes YAML manifests for security issues, resource limits, and deprecated APIs. | Implemented |
| GitOps Drift Investigator | Diagnoses ArgoCD/Flux sync errors, mutating webhook conflicts, and reconciliation failures. | Implemented |
| Service Failure Assistant | Diagnoses Kubernetes networking, Ingress 502/503 errors, missing endpoints, and CoreDNS timeouts. | Implemented |
| Cloud Cost Anomaly Explainer | Analyzes cloud billing spikes, NAT Gateway data surges, and orphaned storage waste across AWS/GCP/Azure. | Implemented |

*Statuses will be updated as each skill is tested and released.*

### 1. Pipeline Failure Translator

**Understand why your pipeline failed without reading hundreds of log lines manually.**

Capabilities:

- Analyze Jenkins and GitHub Actions failure logs.
- Identify the relevant error messages and failing stage.
- Explain likely root causes in plain language.
- Suggest targeted remediation steps.
- Recommend commands or tests to verify the fix.
- Clearly separate observed errors from hypotheses.

Example use case: a GitHub Actions workflow fails during a Docker image build. The skill examines the supplied logs, identifies the relevant build error, explains its likely cause, and suggests how to verify the fix.

### 2. KubeExplain

**Turn confusing Kubernetes errors into clear troubleshooting steps.**

Capabilities:

- Explain common pod states and failure conditions.
- Interpret `kubectl describe` output, pod events, and container logs.
- Investigate image-pull failures, crash loops, and scheduling problems.
- Recommend the next most useful diagnostic command.
- Explain potential fixes and their risks.
- Base explanations on the evidence provided, not generic guesses.

Example use case: a pod enters `CrashLoopBackOff`. The skill examines the available diagnostic output, identifies likely causes, and recommends next steps to investigate.

### 3. Terraform Plan Explainer

**Understand infrastructure blast radius and catch destructive changes before running apply.**

Capabilities:

- Detect resource destructions (`-`) and forced replacements (`-/+`).
- Identify the exact attribute modifications triggering `# forces replacement`.
- Distinguish stateful resource risks (e.g. databases, volumes, storage buckets) from stateless resources.
- Flag security group rule deletions and open CIDR ingress risks.
- Recommend safe `[read-only]` pre-apply verification commands.

Example use case: a Terraform refactoring changes an RDS subnet group, triggering `# forces replacement`. The skill flags the risk of data loss and downtime, advising snapshot verification prior to apply.

### 4. Docker Cleanup Advisor

**Safely reclaim gigabytes of Docker storage without destroying persistent development data.**

Capabilities:

- Analyze `docker system df` output, image registries, container statuses, and build caches.
- Prioritize high-yield, zero-risk cleanup (dangling build cache and untagged images).
- Protect persistent volumes and warn against blind `docker volume prune` or `docker system prune --volumes`.
- Provide tiered cleanup plans matching the severity of disk exhaustion.

Example use case: a CI/CD runner runs out of disk space (`no space left on device`). The skill pinpoints 50GB+ of unpruned buildx cache, recommending safe reclamation commands without wiping active runners.

### 5. DiskPressure Detective

**Diagnose Kubernetes node DiskPressure and pod evictions before nodes crash.**

Capabilities:

- Interpret node conditions (`DiskPressure: True`) and scheduler taints (`node.kubernetes.io/disk-pressure:NoSchedule`).
- Differentiate between `nodefs` (root filesystem), `imagefs` (container runtime), and pod `ephemeral-storage`.
- Detect unconstrained pod writes (`emptyDir` or container logs) triggering eviction manager thresholds.
- Recommend targeted, read-only diagnostic commands and preventive ephemeral limits.

Example use case: a worker node enters `NodeHasDiskPressure` and evicts analytics pods. The skill identifies an unconstrained container consuming 48GB of temporary storage and recommends setting `ephemeral-storage` limits.

### 6. KubeManifest Doctor

**Catch Kubernetes security flaws, missing limits, and deprecated APIs before applying YAML.**

Capabilities:

- Audit manifests for securityContext anti-patterns (running as root, missing `allowPrivilegeEscalation: false`).
- Identify missing resource `requests` and `limits` that cause `BestEffort` eviction vulnerability.
- Detect probe misconfigurations, such as database dependencies inside liveness probes.
- Validate API versions and detect deprecated schemas (e.g. `networking.k8s.io/v1beta1`).
- Flag selector mismatches between Services and Deployments.

Example use case: a team deploys a new service that fails to receive traffic. The skill catches a mismatched label selector in the Service and flags a flawed liveness probe that queries PostgreSQL.

### 7. GitOps Drift Investigator

**Diagnose GitOps sync failures, mutating webhook flapping, and immutable field blocks across ArgoCD and Flux.**

Capabilities:

- Differentiate legitimate drift from in-cluster mutating webhook conflicts (e.g., Linkerd/Istio sidecars, Vault agents, HPA replicas).
- Catch immutable field update rejections (e.g., `volumeClaimTemplates` on StatefulSets, `spec.selector` on Deployments).
- Detect missing CRDs, webhook timeout errors, and failing PreSync/PostSync hooks.
- Recommend targeted `ignoreDifferences` rules or safe zero-downtime recreation strategies without risking storage loss.

Example use case: an ArgoCD application flaps continuously between `Synced` and `OutOfSync`. The skill identifies an active HPA scaling replicas while Git hardcodes `replicas: 2`, and supplies the exact `ignoreDifferences` snippet.

### 8. Service Failure Assistant

**Trace Kubernetes networking breakdowns, Ingress 502/503 errors, and CoreDNS timeouts down to the exact layer.**

Capabilities:

- Follow the packet path: Client -> Ingress -> Service -> Endpoints -> Pod.
- Detect missing Service endpoints (`Endpoints: <none>`) caused by label selector typos or unready pods.
- Disambiguate Ingress 502 Bad Gateway (upstream connection refused/reset) from 503 Service Unavailable (no backend endpoints).
- Diagnose CoreDNS lookup timeouts, crash loops, upstream loop forwarding, and `ndots:5` amplification.
- Audit NetworkPolicy blocks and targetPort configuration errors.

Example use case: an Ingress controller starts throwing 502 Bad Gateway after a release. The skill detects that the Service selector specifies `app=payment-processor` while the new pods use `app=payments-processor`, leaving endpoints empty.

### 9. Cloud Cost Anomaly Explainer

**Explain sudden cloud bill spikes, NAT Gateway data transfer surges, and orphaned storage waste across AWS, GCP, and Azure.**

Capabilities:

- Pinpoint the exact root causes behind sudden cost surges (e.g., NAT Gateway per-GB processing fees vs compute uptime).
- Identify hidden data transfer traps, such as pods pulling from S3 through NAT Gateways instead of free S3 Gateway Endpoints.
- Detect orphaned storage assets (unattached EBS volumes in `available` state, abandoned snapshot chains, idle static IPs).
- Calculate financial run-rates ($/month) and prioritize high-yield, zero-risk architectural fixes.

Example use case: an AWS bill surges by $1,800 due to NAT Gateway transfer fees. The skill identifies ML training pods reading S3 across the NAT Gateway and provides the exact commands to provision a free S3 Gateway VPC Endpoint.

## Design Principles

- **Small and focused:** each skill solves one specific engineering problem.
- **Hermes-native:** reuse Hermes Agent capabilities instead of rebuilding the agent runtime.
- **Modular:** skills can be developed, tested, and improved independently.
- **Practical:** prioritize real-world troubleshooting workflows.
- **Evidence-based:** separate observed facts from inferred causes.
- **Safe by default:** prefer read-only diagnostics and require explicit approval for potentially destructive actions.
- **Extensible:** make it easy to add more DevOps and cloud skills.
- **Community-driven:** welcome contributions, reproducible examples, and improvements.

## How It Works

Each skill is a folder containing a `SKILL.md` file with instructions that Hermes Agent loads when the skill is relevant.

1. You invoke a skill, or Hermes selects a relevant one.
2. You provide logs, command output, configuration, or other diagnostic evidence.
3. Hermes uses its configured model and enabled tools to analyze the problem, guided by the skill's instructions.
4. The skill guides Hermes to explain the likely cause and recommend next steps.
5. You review the recommendations and decide what to run.

Actual behavior depends on your Hermes version, configured model, enabled tools, and permissions.

## Requirements

- A working installation of [Hermes Agent](https://github.com/NousResearch/hermes-agent).
- A model provider configured in Hermes.
- Python or other local tooling, only if a particular skill requires it.
- Appropriate permissions for any diagnostic tools you choose to enable.

Individual skills may list additional requirements in their own directories.

## Installation

Installation instructions will be finalized after the first skills are implemented and tested against the current Hermes skill conventions.

The expected approach is to copy a skill folder from `skills/` into your Hermes skills directory (`~/.hermes/skills/`), or to add this repository as a skill source using Hermes' `skills tap` command. Exact commands will be documented and verified before the first release.

In the meantime, see the official [Hermes Agent documentation](https://hermes-agent.nousresearch.com/docs/) to install and configure Hermes.

## Future Skill Ideas

Possible additions, subject to community interest and available time:

- Cloud Configuration Troubleshooter
- Ansible Failure Analyzer
- Container Build Failure Assistant
- SSL/TLS Certificate Expiry & Renewal Diagnoser
- Database Connection Pool Starvation Analyzer

These are ideas for exploration, not committed features.

## Contributing

Contributions are welcome! You can help by:

- Suggesting a specific DevOps problem worth solving.
- Adding reproducible, sanitized troubleshooting examples.
- Improving diagnostic instructions.
- Writing tests for known failure scenarios.
- Reporting incorrect or unsafe recommendations.
- Proposing new, self-contained skills.

Before contributing a new skill, please check existing issues and discussions to avoid duplicate work, and see [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed guidelines.

## Security and Safety

This toolkit is meant to assist engineers, not replace operational judgment.

- Never commit credentials, tokens, kubeconfig files, or unsanitized logs.
- CI/CD logs and `kubectl` output can contain secrets. Sanitize them before sharing with any external model provider.
- Prefer read-only access for diagnostics.
- Review suggested commands before running them.
- Require explicit approval for destructive operations or production changes.
- Validate recommendations in a safe environment when appropriate.

AI-generated diagnoses can be wrong. Always verify critical findings against the actual system state.

## Project Philosophy

A useful DevOps tool does not need to be a massive platform. Sometimes a small skill that reliably explains a pipeline failure or helps diagnose a Kubernetes problem is worth more than a complex system that tries to automate everything.

**One problem, one focused skill, one practical solution at a time.**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research, the underlying agent runtime.
- The open-source DevOps, Cloud Native, and SRE communities.

---

**Built for engineers who want to troubleshoot smarter, not maintain another platform.**
