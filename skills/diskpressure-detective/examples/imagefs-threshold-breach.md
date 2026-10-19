# Example: Imagefs Threshold Breach on Dedicated Runtime Partition

Sanitized example input for the `diskpressure-detective` skill. Fictional node and event details.
This represents a scenario where the container runtime storage (`imagefs`) on a dedicated disk
hits hard eviction limits due to uncleaned container images.

## Input

User message:
"Our node `ci-worker-k8s-02` triggered `NodeHasDiskPressure` and is rejecting new jobs. The root
disk (`/`) has 60% free space according to our node exporter, so why is kubelet reporting disk pressure?"

`kubectl describe node ci-worker-k8s-02` (relevant excerpt):

```text
Conditions:
  Type             Status  LastTransitionTime                Reason                  Message
  ----             ------  ------------------                ------                  -------
  DiskPressure     True    Tue, 13 Oct 2026 15:30:12 +0000   KubeletHasDiskPressure  kubelet has disk pressure
  Ready            True    Tue, 13 Oct 2026 08:00:00 +0000   KubeletReady            kubelet is posting ready status

Events:
  Type     Reason                  Age    From     Message
  ----     ------                  ----   ----     -------
  Warning  FreeDiskSpaceFailed     12m    kubelet  failed to garbage collect required amount of images. Wanted to free 15234918400 bytes, but freed 1205862400 bytes
  Warning  ImageGCFailed           11m    kubelet  failed to garbage collect images: failed to free disk space: only freed 1205862400 bytes, minimum threshold not reached
  Warning  EvictionThresholdMet    10m    kubelet  eviction manager: threshold imagefs.available < 15% breached
  Normal   NodeHasDiskPressure     10m    kubelet  Node ci-worker-k8s-02 status is now: NodeHasDiskPressure
```

User notes:
- The node uses a separate dedicated NVMe drive mounted at `/var/lib/containerd` for the container runtime.
- The node runs continuous Jenkins and buildkit jobs pulling hundreds of ephemeral image tags daily.

## What a correct analysis should do

See `tests/test-cases.md` → TC-11.
