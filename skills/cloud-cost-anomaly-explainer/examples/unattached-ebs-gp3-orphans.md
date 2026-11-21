# Example: Unattached EBS gp3 Volumes & Orphaned Snapshot Chains

Sanitized example input for the `cloud-cost-anomaly-explainer` skill. Fictional AWS account
inventory representing orphaned storage after deleting temporary staging EKS clusters.

## Input

User message:
"We decommissioned our staging Kubernetes cluster two weeks ago to cut costs, but our EBS storage bill
barely dropped. We're still paying over $450/month for EBS in `eu-west-1`. Here is the output of our
volume audit script:"

`aws ec2 describe-volumes --region eu-west-1 --filters Name=status,Values=available`:

```json
{
  "Volumes": [
    {
      "VolumeId": "vol-0a1829bc37f1982a1",
      "Size": 1000,
      "VolumeType": "gp3",
      "Iops": 3000,
      "Throughput": 125,
      "State": "available",
      "CreateTime": "2026-09-14T10:22:00.000Z",
      "Tags": [
        {"Key": "kubernetes.io/created-for/pvc/name", "Value": "data-staging-elasticsearch-0"}
      ]
    },
    {
      "VolumeId": "vol-0b2938cd48a2093b2",
      "Size": 1000,
      "VolumeType": "gp3",
      "State": "available",
      "CreateTime": "2026-09-14T10:22:00.000Z",
      "Tags": [
        {"Key": "kubernetes.io/created-for/pvc/name", "Value": "data-staging-elasticsearch-1"}
      ]
    },
    {
      "VolumeId": "vol-0c3049de59b3104c3",
      "Size": 2000,
      "VolumeType": "gp3",
      "State": "available",
      "CreateTime": "2026-08-01T15:10:00.000Z",
      "Tags": [
        {"Key": "Name", "Value": "legacy-staging-backup-disk"}
      ]
    }
  ]
}
```

User message continuation:
"Can we just run a script to delete all available volumes, or is there any risk?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-15.
