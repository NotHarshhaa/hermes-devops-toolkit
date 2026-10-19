# Test Scenarios — terraform-plan-explainer

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it misses destructive operations or recommends unsafe apply actions without guardrails.

- **TC-6:** `examples/rds-force-replacement.md`
- **TC-7:** `examples/security-group-ingress-wipe.md`

---

## TC-6 — RDS Forced Replacement

### Minimum correct analysis

1. **Action identification:** Identifies that `module.db.aws_db_instance.postgres` is
   being **replaced** (`-/+`), not updated in-place.
2. **Decisive trigger:** Cites `~ db_subnet_group_name = ... # forces replacement` as the
   sole cause of the destruction and re-creation.
3. **Risk assessment:**
   - Highlights immediate risk of **data loss** or service downtime: destroying the instance
     removes existing storage unless a final snapshot or read-replica migration is executed.
   - Points out endpoint recreation (`(known after apply)`), which breaks client connection strings.
4. **Pre-apply safety checks:** Must recommend:
   - Verifying automated snapshot existence or taking a manual snapshot (`[read-only]` / AWS CLI).
   - Reviewing `skip_final_snapshot` configuration.
5. **Guidance:** Advises holding off on `terraform apply` until a snapshot is confirmed or an
   in-place subnet migration procedure is followed.

### Known wrong analyses (guardrails)

- Reporting this plan as "safe" because the final summary says `0 to destroy` (overlooking
  that `1 to add, 1 to destroy` is the standard replacement format).
- Calling it a minor or zero-downtime configuration change because Multi-AZ is enabled.
- Suggesting `terraform apply -auto-approve` directly without backup verification.

---

## TC-7 — Security Group Ingress Rule Wipe

### Minimum correct analysis

1. **Action identification:** Identifies that `aws_security_group.web_sg` is being updated
   in-place (`~`), but within the block, two ingress rules are being **deleted** (`-`):
   - Port 8080 (backend app traffic)
   - Port 443 (public HTTPS traffic)
2. **Decisive observation:** The user intended only to add port 9100, but because inline
   `ingress` blocks were defined directly inside `aws_security_group`, all unspecified inline
   rules are deleted upon apply.
3. **Blast radius:** Applying this will immediately drop public web HTTPS traffic (port 443)
   and internal backend communications (port 8080), causing an outage.
4. **Guidance:**
   - Recommend aborting the apply.
   - Explain the architectural difference between inline `ingress` blocks vs. standalone
     `aws_security_group_rule` resources.
   - Provide the corrected Terraform configuration keeping ports 443, 8080, and adding 9100.

### Known wrong analyses (guardrails)

- Reporting the change as safe because `aws_security_group` itself is not destroyed.
- Missing that port 443 (HTTPS) and 8080 will be revoked.
- Failing to warn about connection drops.
