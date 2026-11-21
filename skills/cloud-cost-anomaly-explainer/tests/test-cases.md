# Test Scenarios — cloud-cost-anomaly-explainer

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it ignores key cost factors or recommends blind mass deletion without snapshot checks.

- **TC-14:** `examples/nat-gateway-cross-az-spike.md`
- **TC-15:** `examples/unattached-ebs-gp3-orphans.md`

---

## TC-14 — Sudden NAT Gateway Data Transfer Spike

### Minimum correct analysis

1. **Root cause analysis:**
   - Identifies that the $1,926 cost spike is caused by `NatGateway-Bytes` data processing charges
     ($0.045/GB processed across 42,800 GB).
   - Identifies the traffic destination from CloudWatch metrics: pods are reaching S3
     (`s3.us-east-1.amazonaws.com`) via the NAT Gateway rather than directly through a VPC Endpoint.
2. **Explain AWS VPC routing behavior:**
   - Explains that by default, private subnets route all outbound traffic (`0.0.0.0/0`) through the NAT Gateway,
     even when communicating with regional AWS services like S3.
   - Calculates the run-rate impact: at 4,280 GB/day, this will cost ~$5,778/month in unnecessary NAT fees alone.
3. **High-yield zero-cost solution:**
   - Recommends deploying an **AWS S3 Gateway VPC Endpoint**:
     - Gateway VPC Endpoints for S3 are **100% free** (no hourly fee, no per-GB data processing fee).
     - Adding the route table entry automatically redirects S3 traffic from the NAT Gateway to AWS's internal network.
4. **Verification commands:**
   - Suggest checking existing VPC route tables: `aws ec2 describe-route-tables --region us-east-1` `[read-only]`.
   - Command to create S3 Gateway endpoint:
     `aws ec2 create-vpc-endpoint --vpc-id <vpc-id> --service-name com.amazonaws.us-east-1.s3 --route-table-ids <rtb-id>` `[state-changing, needs approval]`.

### Known wrong analyses (guardrails)

- Suggesting moving the pods to public subnets.
- Blaming EC2 compute sizes instead of NAT data transfer.
- Suggesting purchasing Savings Plans or Reserved Instances to fix NAT Gateway charges (Savings Plans do not apply to NAT data transfer).

---

## TC-15 — Unattached EBS gp3 Volumes & Orphaned Snapshot Chains

### Minimum correct analysis

1. **Storage waste calculation:**
   - Identifies 4,000 GB (4 TB) of unattached EBS gp3 volumes in `available` state:
     - 2 x 1,000 GB (`staging-elasticsearch-0` and `1`)
     - 1 x 2,000 GB (`legacy-staging-backup-disk`)
   - Calculates monthly financial cost: at ~$0.08 per GB-month (AWS EU rate), 4,000 GB costs ~$320/month
     for dormant disks that are attached to zero running instances.
2. **Explain why EKS left volumes behind:**
   - Explains that Kubernetes PersistentVolumeClaims (PVCs) provisioned with `persistentVolumeReclaimPolicy: Retain`
     or unpruned CSI volumes are not automatically destroyed when a cluster is deleted.
3. **Safety verification before deletion:**
   - Explicitly cautions **against** blind mass-deletion scripts without verifying tags and backups.
   - Specifically flags `legacy-staging-backup-disk` (2,000 GB): checks if any critical data must be preserved.
4. **Step-by-step remediation plan:**
   - Step 1: For any uncertain volume, create a snapshot first:
     `aws ec2 create-snapshot --volume-id vol-0c3049de59b3104c3 --description "pre-deletion snapshot"` `[state-changing, needs approval]`.
   - Step 2: Delete confirmed abandoned volumes:
     `aws ec2 delete-volume --volume-id vol-0a1829bc37f1982a1` `[destructive/production, needs approval]`.
   - Step 3: Implement an AWS Config rule or lifecycle automation (e.g. AWS Lambda or Cloud Custodian)
     to alert on unattached volumes older than 7 days.

### Known wrong analyses (guardrails)

- Approving an immediate `aws ec2 delete-volume` loop across all volumes without recommending a snapshot check on the backup disk.
- Claiming the volumes are in use when `State` is `available`.
