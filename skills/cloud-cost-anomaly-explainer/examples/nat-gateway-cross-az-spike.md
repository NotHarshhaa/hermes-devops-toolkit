# Example: Sudden NAT Gateway Data Transfer Spike

Sanitized example input for the `cloud-cost-anomaly-explainer` skill. Fictional AWS billing
and CloudWatch metrics representing a massive NAT Gateway cost anomaly.

## Input

User message:
"Our AWS bill in `us-east-1` jumped by $1,850 over the last 10 days. Looking at Cost Explorer,
the surge is listed under `EC2-Other` -> `NatGateway-Bytes`. We haven't deployed any new public
services. Here is the cost report snippet and CloudWatch NAT Gateway metric breakdown:"

AWS Cost Explorer breakdown (`us-east-1`):

```text
Usage Type                            Unblended Cost (Last 10 Days)   Projected Monthly
USE1-NatGateway-Bytes (42,800 GB)     $1,926.00                       $5,778.00
USE1-NatGateway-Hours (720 Hrs)       $32.40                          $97.20
USE1-BoxUsage:m6i.xlarge              $460.80                         $1,382.40
```

CloudWatch metric `BytesOutToDestination` for `nat-04a189f72b901cd12`:

```text
Timestamp                 Average Megabytes/sec   Total Gigabytes/day   Top Destination
2026-11-10 -> 2026-11-20  49.5 MB/s               4,280 GB/day          s3.us-east-1.amazonaws.com
```

User message continuation:
"Our ML analytics pods in the private subnet are running daily retraining jobs reading parquet files
from our S3 bucket `s3://company-analytics-lake-prod`. Why is NAT Gateway charging us so much if S3 is in the same region?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-14.
