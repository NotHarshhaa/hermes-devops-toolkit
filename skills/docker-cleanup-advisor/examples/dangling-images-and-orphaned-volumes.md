# Example: Dangling Images and Orphaned Volumes

Sanitized example input for the `docker-cleanup-advisor` skill. This represents a developer
workstation where Docker storage is growing, with multiple dangling images and an unattached
database volume.

## Input

User message:
"My laptop has only 15GB free, and Docker seems to take a huge chunk. Here is `docker system df`
and `docker volume ls`:"

`docker system df`:

```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          24        4         18.2GB    14.6GB (80%)
Containers      8         1         340MB     310MB (91%)
Local Volumes   5         1         12.4GB    10.8GB (87%)
Build Cache     88        0         6.2GB     6.2GB (100%)
```

`docker volume ls`:

```text
DRIVER    VOLUME NAME
local     app_frontend_node_modules
local     db_pgdata_staging_dump
local     legacy_mysql_data
local     redis_data_cache
local     test_tmp_vol
```

User notes:
- `db_pgdata_staging_dump` contains a sanitized export of staging data that took 3 hours to download.
- The user is currently only running one container for an unrelated microservice.

## What a correct analysis should do

See `tests/test-cases.md` → TC-9.
