# Example: RDS Forced Replacement

Sanitized example input for the `terraform-plan-explainer` skill. Fictional resource names,
IDs, and accounts; no real cloud credentials or sensitive identifiers. This is what a user
might share when running `terraform plan` before a production database migration.

## Input

User message:
"I updated our Terraform module to point our staging database to the new private subnet group.
Can you review this plan output before I run `terraform apply`? I want to make sure it doesn't cause
unexpected downtime."

`terraform plan` (relevant excerpt):

```text
Terraform will perform the following actions:

  # module.db.aws_db_instance.postgres will be replaced
-/+ resource "aws_db_instance" "postgres" {
      ~ address                               = "stage-postgres.c123456789.us-east-1.rds.amazonaws.com" -> (known after apply)
      ~ arn                                   = "arn:aws:rds:us-east-1:123456789012:db:stage-postgres" -> (known after apply)
        allocated_storage                     = 100
        auto_minor_version_upgrade            = true
        backup_retention_period               = 7
      ~ db_subnet_group_name                  = "stage-db-subnet-group-v1" -> "stage-db-subnet-group-v2" # forces replacement
      ~ endpoint                              = "stage-postgres.c123456789.us-east-1.rds.amazonaws.com:5432" -> (known after apply)
        engine                                = "postgres"
        engine_version                        = "15.4"
        id                                    = "stage-postgres"
        identifier                            = "stage-postgres"
        instance_class                        = "db.r6g.large"
        multi_az                              = true
        port                                  = 5432
        publicly_accessible                   = false
      ~ status                                = "available" -> (known after apply)
        tags                                  = {
            "Environment" = "staging"
            "ManagedBy"   = "terraform"
        }
    }

Plan: 1 to add, 0 to change, 1 to destroy.
```

User notes:
- The database contains ~40GB of data.
- The user expected the subnet group update to happen in place without database destruction.

## What a correct analysis should do

See `tests/test-cases.md` → TC-6.
