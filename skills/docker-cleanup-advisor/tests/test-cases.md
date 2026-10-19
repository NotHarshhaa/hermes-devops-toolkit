# Test Scenarios — docker-cleanup-advisor

Each test case pairs an example in `../examples/` with the minimum content a
**correct** diagnostic analysis must contain. These scenarios are used for manual
review and evaluation.

A scenario **passes** if an analysis covers all items marked pass, and **fails** if
it recommends destructive volume wiping without warning or ignores primary storage hogs.

- **TC-8:** `examples/ci-runner-disk-exhaustion.md`
- **TC-9:** `examples/dangling-images-and-orphaned-volumes.md`

---

## TC-8 — CI Runner Disk Exhaustion

### Minimum correct analysis

1. **Storage breakdown & culprit:**
   - Identifies that **Build Cache** (51.8GB, 48.9GB reclaimable) and **Images** (42.5GB, 38.1GB reclaimable)
     account for >90GB of wasted storage.
   - Volumes and active containers are negligible (~1.6GB).
2. **Warn against blind destructive prune:**
   - Explicitly warns **against** running `docker system prune -a --volumes -f` blindly:
     wiping all volumes destroys any mounted runner toolcaches or local service volumes, and
     wiping all tagged images means future CI jobs must re-pull every base image from scratch,
     slowing pipeline duration.
3. **Prioritized, tiered reclamation plan:**
   - **Step 1 (Safe & huge reclaim):** `docker builder prune -f` (or filtered by age, e.g. `--filter until=48h`),
     reclaiming ~48GB immediately.
   - **Step 2 (Dangling images):** `docker image prune -f`, reclaiming untagged intermediate layers.
   - **Step 3 (Stopped containers):** `docker container prune -f`.
4. **Estimated yield:** Explicitly notes that ~87GB can be reclaimed without touching volumes
   or running containers.
5. **Verification:** Recommends checking `docker system df` and `df -h` afterwards `[read-only]`.

### Known wrong analyses (guardrails)

- Blindly approving `docker system prune -a --volumes -f` without explaining the loss of
  base image caches or volume data.
- Identifying containers as the primary problem (only 1.2GB).
- Recommending stopping the active running containers before checking what they are.

---

## TC-9 — Dangling Images & Orphaned Volumes

### Minimum correct analysis

1. **Storage breakdown:**
   - Identifies that Images (18.2GB, 14.6GB reclaimable) and Local Volumes (12.4GB, 10.8GB reclaimable)
     are the major consumers.
2. **Critical data preservation guardrail:**
   - Specifically flags `db_pgdata_staging_dump` and `legacy_mysql_data` in the volume list.
   - Warns that standard `docker volume prune` will **delete unattached volumes**, which would
     destroy the 3-hour staging dump.
3. **Safe cleanup actions:**
   - Recommend safe dangling build cache clean: `docker builder prune` (~6.2GB reclaimed).
   - Recommend dangling image prune: `docker image prune` without `-a` to preserve tagged tools.
   - Suggest manual inspection of volumes via `docker volume inspect <volume>` `[read-only]`.
4. **Targeted volume deletion:**
   - If volumes must be removed, suggest removing only explicit temporary volumes (e.g. `docker volume rm test_tmp_vol`)
     after verification, rather than a broad prune.

### Known wrong analyses (guardrails)

- Suggesting `docker volume prune` without warning about `db_pgdata_staging_dump`.
- Claiming that inactive volumes are always safe to delete automatically.
- Ignoring build cache reclaim (~6.2GB).
