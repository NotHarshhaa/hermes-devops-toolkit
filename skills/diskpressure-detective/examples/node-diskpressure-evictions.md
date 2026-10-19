# Example: Node DiskPressure and Ephemeral Storage Evictions

Sanitized example input for the `diskpressure-detective` skill. Fictional node names, namespaces,
and pod IDs. This represents a situation where a worker node enters `DiskPressure=True` and evicts
running workloads.

## Input

User message:
"One of our worker nodes (`node-worker-03`) suddenly went into `DiskPressure` and multiple pods
in the `analytics` namespace were evicted with errors about ephemeral-storage. What happened
and how do I fix it?"

`kubectl describe node node-worker-03` (relevant excerpts):

```text
Name:               node-worker-03
Roles:              worker
Conditions:
  Type                 Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----                 ------  -----------------                 ------------------                ------                       -------
  NetworkUnavailable   False   Tue, 13 Oct 2026 10:14:02 +0000   Tue, 13 Oct 2026 10:14:02 +0000   CalicoIsUp                   Calico is running on node
  MemoryPressure       False   Tue, 13 Oct 2026 12:45:10 +0000   Tue, 13 Oct 2026 10:14:00 +0000   KubeletHasSufficientMemory   kubelet has sufficient memory
  DiskPressure         True    Tue, 13 Oct 2026 12:45:10 +0000   Tue, 13 Oct 2026 12:41:03 +0000   KubeletHasDiskPressure       kubelet has disk pressure
  PIDPressure          False   Tue, 13 Oct 2026 12:45:10 +0000   Tue, 13 Oct 2026 10:14:00 +0000   KubeletHasNoPIDPressure      kubelet has no PID pressure
  Ready                True    Tue, 13 Oct 2026 12:45:10 +0000   Tue, 13 Oct 2026 10:14:00 +0000   KubeletReady                 kubelet is posting ready status
Taints:             node.kubernetes.io/disk-pressure:NoSchedule
Allocatable:
  cpu:                8
  ephemeral-storage:  95898328Ki
  memory:             31894236Ki
  pods:               110

Events:
  Type     Reason                   Age    From     Message
  ----     ------                   ----   ----     -------
  Warning  EvictionThresholdMet     5m12s  kubelet  Attempting to reclaim ephemeral-storage
  Warning  Evicted                  4m45s  kubelet  Pod analytics/worker-aggregator-849c7-5z9xp was evicted: The node was low on resource: ephemeral-storage. Container aggregator-task was using 48293120Ki, which exceeds its request of 0
  Normal   NodeHasDiskPressure      4m07s  kubelet  Node node-worker-03 status is now: NodeHasDiskPressure
```

User notes:
- `worker-aggregator` is a Python data-crunching job that extracts and decompresses archive files into `/tmp`.
- It was launched without any `resources.limits.ephemeral-storage` configured.

## What a correct analysis should do

See `tests/test-cases.md` → TC-10.
