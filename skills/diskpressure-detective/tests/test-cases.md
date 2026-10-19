# Test Scenarios — diskpressure-detective

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it confuses root filesystems with imagefs or recommends random node reboots/deletions.

- **TC-10:** `examples/node-diskpressure-evictions.md`
- **TC-11:** `examples/imagefs-threshold-breach.md`

---

## TC-10 — Node DiskPressure & Ephemeral Storage Evictions

### Minimum correct analysis

1. **Condition & taint:** Identifies that `node-worker-03` has `DiskPressure = True` and
   is untolerated, applying taint `node.kubernetes.io/disk-pressure:NoSchedule`.
2. **Decisive cause:** Points directly to the eviction message:
   `Pod analytics/worker-aggregator-... was evicted: The node was low on resource: ephemeral-storage. Container aggregator-task was using 48293120Ki, which exceeds its request of 0`.
3. **Mechanism:** The worker task consumed ~46GB of unconstrained ephemeral storage
   (writing/extracting to `/tmp` in the writable container layer or emptyDir), eating almost
   half the node's allocatable storage (~91GB) and triggering the eviction manager.
4. **Distinction:** Demonstrates that the node itself has plenty of CPU and memory, and the
   issue is localized to unconstrained disk writes from this specific workload.
5. **Next diagnostic step:** Recommend `[read-only]` commands:
   - `kubectl get events -n analytics --field-selector reason=Evicted`
   - Inspecting the pod spec for `emptyDir` or local volume configurations.
6. **Remediation:**
   - **Immediate:** Acknowledge eviction freed the space; verify if node transitioned back to
     `DiskPressure = False`.
   - **Long-term:** Add explicit `resources.limits.ephemeral-storage` (e.g. `10Gi`) and
     `resources.requests.ephemeral-storage` to `worker-aggregator` so runaway tasks are
     isolated and killed before compromising the entire node.

### Known wrong analyses (guardrails)

- Claiming memory pressure or OOMKilled caused the eviction (memory condition is False).
- Suggesting draining and deleting the node as the primary remedy when a single workload
  caused the spike.
- Failing to highlight the missing `ephemeral-storage` limit.

---

## TC-11 — Imagefs Threshold Breach on Dedicated Partition

### Minimum correct analysis

1. **Filesystem differentiation:** Explains why the root disk (`/`) shows 60% free while
   kubelet reports `DiskPressure`: the failure is specifically on **`imagefs`**
   (`imagefs.available < 15%`), which is mounted on a separate partition (`/var/lib/containerd`).
2. **Decisive evidence:** Cites kubelet events:
   - `ImageGCFailed: failed to garbage collect images... minimum threshold not reached`
   - `eviction manager: threshold imagefs.available < 15% breached`
3. **Underlying cause:** Kubelet attempted to perform image garbage collection to free ~15GB,
   but could only free ~1.2GB. This happens because images are either pinned, actively referenced
   by running containers, or contain un-garbage-collected builder layer caches from continuous
   build jobs.
4. **Next diagnostic steps:** `[read-only]`
   - Node-level check: `df -h /var/lib/containerd` and `crictl images` or `crictl inspecti`
     to view cached images on the node.
5. **Remediation:**
   - **Immediate:** Safe prune of dead containers and untagged images via `crictl rmi --prune`
     `[state-changing, needs approval]`.
   - **Configuration:** Adjust kubelet image garbage collection flags
     (`--image-gc-high-threshold-percent`, `--image-gc-low-threshold-percent`) or expand the
     NVMe storage for container runtime data.

### Known wrong analyses (guardrails)

- Telling the user their node exporter is lying or the filesystem metrics are broken
  (missing that `imagefs` can be a separate mount from root `/`).
- Blaming pod ephemeral storage or container logs instead of image cache GC failure.
- Suggesting wiping `/` or cleaning `/var/log`.
