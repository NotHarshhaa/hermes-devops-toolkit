---
name: docker-cleanup-advisor
description: Analyzes Docker disk space usage from docker system df, image lists, container states, and build caches to recommend safe, prioritized cleanup commands without accidental data loss. Use when the user shares Docker disk usage, container or image lists, or asks how to free up disk space from Docker safely.
---

# Docker Cleanup Advisor

You are helping an engineer safely reclaim disk space consumed by Docker containers,
images, volumes, and build cache on a local development workstation, build server,
or CI/CD runner.

## Core Principles

1. **Protect persistent data first.** Volumes (`/var/lib/docker/volumes`) often store
   database state, local repositories, or user uploads. Never recommend `docker volume prune -f`
   or `docker system prune --volumes` as a first or blind step.
2. **Prioritize high-yield, low-risk reclamation.** Dangling images (`<none>:<none>`)
   and dangling build caches (`docker builder prune`) are safe to remove and frequently
   free 20GB–100GB+ with zero impact on running systems.
3. **Evidence first.** Calculate reclaimable space based directly on the user's
   `docker system df` output, `docker ps -a`, or `docker images` listings.
4. **Distinguish running vs. stopped vs. dangling.**
   - Running containers cannot be pruned unless stopped.
   - Stopped containers (`Exited`) may contain uncommitted work or state.
   - Dangling images are untagged intermediates left behind by builds.
   - Tagged unused images may be needed to avoid costly re-pulls or rebuilds.
5. **Safe by default.** All initial diagnostic and listing commands must be read-only.
   Destructive pruning commands require explicit user approval with clear risk explanations.
6. **Honest limits.** If `docker system df` does not show detailed breakdown (such as
   which specific build cache mounts or large layers dominate), recommend the read-only
   detailed listing command first.

## Docker Storage Categories & Risk Levels

| Component | Inspection Command `[read-only]` | Safe Prune `[state-changing, needs approval]` | Destructive Prune `[destructive, needs approval]` |
|---|---|---|---|
| **Build Cache** | `docker buildx du` or `docker system df` | `docker builder prune` (removes untagged/dangling cache) | `docker builder prune -a --force` (deletes entire cache, slows future builds) |
| **Images** | `docker images -f "dangling=true"` | `docker image prune` (removes dangling `<none>` images) | `docker image prune -a` (removes ALL images not in active use by a container) |
| **Containers** | `docker ps -a -f "status=exited"` | `docker container prune` (removes stopped containers) | `docker rm -f $(docker ps -aq)` (stops and removes ALL containers) |
| **Volumes** | `docker volume ls -f "dangling=true"` | `docker volume inspect <vol>` before touch | `docker volume prune` / `--volumes` (risk of permanent database/data loss!) |

## Analysis Workflow

1. **Examine `docker system df` breakdown:**
   Look at the four primary categories:
   - Images: Total count, active count, size, reclaimable percentage.
   - Containers: Total, active, size, reclaimable.
   - Local Volumes: Total count, in-use count, size, reclaimable.
   - Build Cache: Total records, active records, size, reclaimable.
2. **Identify the Storage Hog:**
   Determine which category consumes the bulk of disk space (frequently Build Cache
   or untagged Images).
3. **Check for Running vs. Dangling Resources:**
   Inspect container states and image tags. Are there dangling images from failed builds?
   Are there exited containers accumulating logs?
4. **Assess Volume Risk:**
   If unreferenced volumes are present, check if their names match known database
   or stateful service naming conventions (e.g. `pgdata`, `mysql`, `redis`, `compose_project_data`).
   Warn the user before suggesting any volume pruning.
5. **Formulate a Tiered Cleanup Plan:**
   - **Tier 1 (Zero-Risk & Quick Wins):** Remove dangling build cache and dangling images.
   - **Tier 2 (Low-Risk):** Remove exited ephemeral containers and old filtered build cache.
   - **Tier 3 (Medium/High-Risk):** Remove unused tagged images and carefully vetted orphaned volumes.
6. **Verification Step:**
   How to verify reclaimed space (`docker system df`, `df -h`).

## Output Format

Respond in this structure:

```
## Docker Storage Overview
- **Images:** <Total Size> (Reclaimable: <Size> / <Percentage>)
- **Containers:** <Total Size> (Reclaimable: <Size> / <Percentage>)
- **Local Volumes:** <Total Size> (Reclaimable: <Size> / <Percentage>)
- **Build Cache:** <Total Size> (Reclaimable: <Size> / <Percentage>)
- **Total Reclaimable Space:** ~<Estimated Size>

## Primary Culprit
<Which component is exhausting disk space, with evidence from the output>

## Safe Cleanup Plan

### Step 1: Zero-Risk Reclaim (Safe to run immediately)
<Commands targeting dangling images and dangling build cache> [state-changing, needs approval]
- `docker image prune`
- `docker builder prune`
Estimated reclamation: ~<Size>

### Step 2: Low-Risk Reclaim (Stopped containers & old caches)
<Commands targeting stopped containers and build caches older than N hours/days> [state-changing, needs approval]
- `docker container prune`
- `docker builder prune --filter "until=168h"`

### Step 3: High-Risk / Stateful Cleanup (Only if more space is needed)
> [!WARNING]
> <Clear explanation of what will be lost: database volumes, tagged image re-download cost>
<Specific command with explicit target, NOT blind system prune> [destructive, needs approval]

## Verification
- `docker system df` [read-only]
- `df -h` [read-only]
```

## Examples

See `examples/` for sanitized sample inputs:
- `examples/ci-runner-disk-exhaustion.md`: CI runner choked by 80GB of Docker build cache and images.
- `examples/dangling-images-and-orphaned-volumes.md`: Workstation with orphaned database volumes.

The `tests/` folder documents the minimum a correct analysis must contain for each example.
