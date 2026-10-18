# Example: CrashLoopBackOff (OOMKilled)

Sanitized example input for the kube-explain skill. Fictional namespace and
workload names; no real cluster data. This is what a user might paste when asking
"why is my pod crash-looping?"

## Input

User message:
"My API pod went into CrashLoopBackOff a few hours after deploying, and it will not
come back. Traffic was fine before the deploy. Here's what I have:"

`kubectl get pod -n payments`:

```text
NAME                           READY   STATUS             RESTARTS   AGE
api-server-7d9f6c8b5-x2m4k     0/1     CrashLoopBackOff   8          21m
```

`kubectl describe pod api-server-7d9f6c8b5-x2m4k -n payments` (relevant excerpt):

```text
Status:          Running
Containers:
  api-server:
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
      Started:      Tue, 13 Oct 2026 14:02:11 +0000
      Finished:     Tue, 13 Oct 2026 14:19:48 +0000
    Ready:          false
    Restart Count:  8
    Limits:
      memory:  512Mi
    Requests:
      cpu:      250m
      memory:   256Mi
Events:
  Type     Reason      Age                     From               Message
  ----     ------      ----                    ----               -------
  Normal   Scheduled   22m                     default-scheduler  Successfully assigned payments/api-server-7d9f6c8b5-x2m4k to node-worker-04
  Normal   Pulled      20m (x9 over 22m)       kubelet            Container image "registry.example.dev/team-acme/service-api:1.9.0" already present on machine
  Normal   Created     20m (x9 over 22m)       kubelet            Created container api-server
  Normal   Started     20m (x9 over 22m)       kubelet            Started container api-server
  Warning  BackOff     18s (x32 over 20m)      kubelet            Back-off restarting failed container api-server in pod api-server-7d9f6c8b5-x2m4k_payments(f1c2e3a4)
```

Notes the user added separately:

- Deploy 1.9.0 changed the cache layer to hold more items in memory.
- The pod survives for ~15–17 minutes after each restart before being killed again.

## What a correct analysis should do

See `tests/test-cases.md` → TC-3.
