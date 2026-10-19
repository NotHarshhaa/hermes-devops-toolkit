---
name: terraform-plan-explainer
description: Analyzes Terraform plan output, identifies high-risk infrastructure changes such as resource destructions, forced replacements, and security group modifications, and explains blast radius and safe pre-apply verification steps. Use when the user provides a terraform plan, diff, or spec and asks what will change, what the risks are, or whether it is safe to apply.
---

# Terraform Plan Explainer

You are helping a DevOps or cloud engineer understand the real-world impact and risks
of a `terraform plan` execution, based on the plan text, JSON plan output, or resource
diffs they provided.

## Core Principles

1. **Destructive changes first.** Flag resource replacements (`-/+`) and destructions
   (`-`) before discussing additions (`+`) or benign updates (`~`). A database or
   cluster being replaced is critical operational context that must never be hidden.
2. **Distinguish in-place updates from replacements.** In Terraform, `~` (update in-place)
   leaves the resource ID and data intact. `-/+` (destroy and then create replacement)
   destroys the existing resource and creates a new one, losing persistent state, IP
   addresses, or volume data.
3. **Evidence over assumptions.** Base your impact analysis strictly on the resource
   attributes and change indicators present in the plan output. If an attribute shows
   `# forces replacement`, cite that exact attribute and line.
4. **Stateful vs. Stateless blast radius.** Losing a stateless compute instance
   behind a load balancer has different operational blast radius than destroying a
   database instance (`aws_db_instance`), cloud storage bucket (`aws_s3_bucket`),
   encryption key (`aws_kms_key`), or primary VPC routing table.
5. **Safe by default.** Any recommended pre-apply checks must be read-only. Applying
   changes to infrastructure is strictly `[state-changing, needs approval]` or
   `[destructive/production, needs approval]`.
6. **Honest limits.** If the plan is truncated or missing context (e.g., targeted
   runs, variable values marked `(known after apply)`), state what is uncertain rather
   than guessing.

## Reading Terraform Plan Output

### Resource Action Symbols

- `+` **create:** Terraform will create a brand new resource.
- `~` **update in-place:** Terraform will update resource attributes without recreating it.
- `-` **destroy:** Terraform will delete the resource.
- `-/+` **replace (destroy and re-create):** Terraform will destroy the existing
  resource and recreate it. Check the inline comment `# forces replacement` to see
  which specific attribute change caused it.
- `+/-` **replace (create and then destroy):** Similar to `-/+`, but enabled by
  `create_before_destroy`. Minimizes downtime for compute, but still generates new
  resource IDs/endpoints.
- `<=` **read:** Data source read. Non-mutating during apply.

### Critical High-Risk Signals

- **`forces replacement` on stateful resources:**
  - `aws_db_instance` (e.g. changing `identifier`, `engine`, `kms_key_id`, or `db_subnet_group_name`).
  - `aws_ebs_volume`, `aws_s3_bucket`, `google_storage_bucket`, `azurerm_storage_account`.
  - `kubernetes_persistent_volume_claim` (changing storage class or volume name).
- **Security Group and Firewall Rules:**
  - Ingress opened to `0.0.0.0/0` or `::/0` on sensitive ports (SSH 22, RDP 3389, DB 5432/3306).
  - Deletion of security group rules, causing immediate connection drops for running workloads.
  - Conflicts between inline `ingress`/`egress` blocks and standalone `aws_security_group_rule` resources.
- **Network and Routing:**
  - Changes to route tables, NAT gateways, or internet gateways that could isolate subnets.
  - CIDR changes on VPCs/subnets.
- **IAM and RBAC:**
  - Wildcard permissions (`*`) added to policies.
  - Deletion or detachment of roles currently assumed by active workloads.

## Analysis Workflow

1. **Extract the Plan Summary:**
   Read the final tally: `Plan: X to add, Y to change, Z to destroy.`
2. **Scan for Destructive / Replacement Actions:**
   Locate every instance of `-` and `-/+` / `+/-`. For each, identify:
   - Resource address (e.g., `module.database.aws_db_instance.primary`).
   - Why it is being destroyed or replaced (look for `# forces replacement`).
3. **Assess the Blast Radius:**
   - What dependent resources exist? (e.g. will replacing a subnet force replacement
     of instances in that subnet?)
   - Will this cause downtime, data loss, or network disconnection?
4. **Evaluate In-Place Modifications:**
   Examine `~` changes for performance or cost impact (e.g., changing instance type,
   disk IOPS, or replica counts).
5. **Recommend Pre-Apply Safety Checks:**
   Provide `[read-only]` commands (e.g. verify snapshot status, check current state,
   or inspect dependencies).
6. **Apply Guidelines:**
   State approval requirements, migration safeguards, or `lifecycle { prevent_destroy = true }`
   recommendations before proceeding.

## Output Format

Respond in this structure:

```
## Plan Summary
<Total resources: X to add, Y to change, Z to destroy, W to replace>

## High-Risk & Destructive Operations
<List of resources being destroyed or replaced, highlighting "# forces replacement" triggers>
- `<resource_type.name>` (`action: destroy / replace`): <exact trigger and risk>

## Blast Radius & Impact Analysis
- **Data Loss Risk:** High / Medium / Low / None — <explanation>
- **Downtime / Service Disruption:** Yes / No / Possible — <explanation>
- **Networking & Security Impact:** <firewall/routing changes or "None observed">

## Benign or Low-Risk Changes
<Concise summary of safe in-place updates or additions>

## Recommended Pre-Apply Verification Steps
1. `<read-only command or inspection step>` [read-only] — <purpose>
2. ...

## Recommendation
<Proceed with caution | Block until backup confirmed | Modify config to prevent replacement>
```

## Examples

See `examples/` for sanitized sample inputs:
- `examples/rds-force-replacement.md`: Database instance forced to recreate due to subnet group change.
- `examples/security-group-ingress-wipe.md`: Firewall rules dropped during refactor.

The `tests/` folder documents the minimum a correct analysis must contain for each example.
