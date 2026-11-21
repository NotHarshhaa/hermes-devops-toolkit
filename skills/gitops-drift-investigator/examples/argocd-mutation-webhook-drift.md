# Example: ArgoCD Mutation Webhook & HPA Drift Flapping

Sanitized example input for the `gitops-drift-investigator` skill. Fictional application
and cluster information representing a classic GitOps perpetual drift issue.

## Input

User message:
"Our `checkout-service` application in ArgoCD has been stuck in `OutOfSync` status for three days.
Every time we click 'Sync', ArgoCD reports synced for 10 seconds, and then immediately flips back to
`OutOfSync`. Here is the output of `argocd app get checkout-service` and `argocd app diff checkout-service`:"

`argocd app get checkout-service`:

```text
Name:               checkout-service
Project:            ecommerce
Server:             https://kubernetes.default.svc
Namespace:          payments
URL:                https://argocd.example.dev/applications/checkout-service
Repo:               https://github.com/example-org/gitops-infra.git
Target:             main
Path:               apps/checkout-service
Sync Window:        Sync Allowed
Sync Policy:        Automated (Prune: true, SelfHeal: true)
Sync Status:        OutOfSync
Health Status:      Healthy
```

`argocd app diff checkout-service`:

```diff
===== apps/Deployment payments/checkout-api ======
8c8
<     replicas: 2
---
>     replicas: 7
16c16,19
<         image: registry.example.dev/ecommerce/checkout:v1.14.2
---
>         image: registry.example.dev/ecommerce/checkout:v1.14.2
>       - name: linkerd-proxy
>         image: cr.l5d.io/linkerd/proxy:stable-2.14.0
>         args: ["--identity-dir", "/var/run/linkerd/identity"]
```

User message continuation:
"Should we enable `--force` or delete the deployment in the cluster to make it match Git?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-10.
