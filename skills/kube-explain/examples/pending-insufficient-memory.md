# Example: Pending (insufficient memory requests)

Sanitized example input for the kube-explain skill. Fictional cluster objects; no
real node names or IPs.

## Input

User message:
"I scaled up a small cluster and one of the new pods stays Pending. Nothing is
wrong with the image; the same Pod template was Running an hour ago before the
scale-up. Output:"

`kubectl get pod -n analytics`:

```text
NAME                            READY   STATUS    RESTARTS   AGE
dashboard-api-79aab0-4b2        1/2     Running   0          1d
dashboard-api-79aab0-4b3        0/1     Pending   0          9m
```

Relevant excerpt from
`kubectl describe pod dashboard-api-79aab0-4b3 -n analytics`:

```text
Status:         Pending
Containers:
  dashboard-api:
    Requests:
      cpu:     1
      memory:  3Gi
Events:
  Type     Reason            Age                 From               Message
  ----     ------            ----                ----               -------
  Normal   Scheduled         2m                  default-scheduler  Successfully assigned analytics/dashboard-api-79aab0-4b3 to (an unscheduled pod was scheduled)
  Warning  FailedScheduling  25s (x6 over 9m)    default-scheduler  0/3 nodes are available: 1 node(s) had untolerated taint {node-role.kubernetes.io/control-plane: }, 2 Insufficient memory. preemption: 0/3 nodes are available: 2 No preemption victims found for incoming pod.
```

Node capacity the user also pasted:

```text
$ kubectl top nodes
NAME           CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
node-worker-1  810m         9%     7200Mi          90%
node-worker-2  905m         10%    7350Mi          91%
```

Notes the user added separately:

- The cluster was scaled up from 2 worker nodes, not scaled up — same 2 workers,
  but a new application (a vector database) was deployed at the same time.
- The new database pods do not have a `requests.cpu` / `requests.memory` set, but
  their actual memory usage is already close to 7 GiB per cluster node.

## What a correct analysis should do

See `tests/test-cases.md` → TC-5.
