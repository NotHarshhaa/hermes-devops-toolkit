# Example: Security Group Ingress Rule Wipe

Sanitized example input for the `terraform-plan-explainer` skill. Fictional resource names and
VPC IDs. This is what a user might paste when restructuring security group rules.

## Input

User message:
"I am refactoring our web security group to add a new monitoring port. Running `terraform plan`
produced the output below. Does this look safe to apply?"

`terraform plan` (relevant excerpt):

```text
Terraform will perform the following actions:

  # aws_security_group.web_sg will be updated in-place
  ~ resource "aws_security_group" "web_sg" {
        id                     = "sg-0123456789abcdef0"
        name                   = "web-tier-sg"
        tags                   = { "Environment" = "prod" }
        vpc_id                 = "vpc-0a1b2c3d4e5f67890"

      - ingress {
          - cidr_blocks      = [
              - "10.0.0.0/16",
            ]
          - description      = "App backend traffic"
          - from_port        = 8080
          - protocol         = "tcp"
          - to_port          = 8080
        }
      - ingress {
          - cidr_blocks      = [
              - "0.0.0.0/0",
            ]
          - description      = "HTTPS public"
          - from_port        = 443
          - protocol         = "tcp"
          - to_port          = 443
        }
      + ingress {
          + cidr_blocks      = [
              - "10.0.50.0/24",
            ]
          + description      = "Prometheus scraping"
          + from_port        = 9100
          + protocol         = "tcp"
          + to_port          = 9100
        }

        # (1 unchanged block hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

User notes:
- The user only intended to add the Prometheus scraping rule on port 9100.
- They did not intend to delete the existing ingress rules for port 443 and 8080.

## What a correct analysis should do

See `tests/test-cases.md` → TC-7.
