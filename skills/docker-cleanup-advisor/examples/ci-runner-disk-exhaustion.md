# Example: CI Runner Disk Exhaustion

Sanitized example input for the `docker-cleanup-advisor` skill. Fictional host and container
information. This represents a typical CI/CD runner disk space crisis (`no space left on device`).

## Input

User message:
"Our self-hosted GitHub Actions runner disk is 98% full. Docker builds are failing with
`write /var/lib/docker/tmp/...: no space left on device`. Here is the output of `docker system df`:"

`docker system df`:

```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          84        6         42.5GB    38.1GB (89%)
Containers      14        2         1.2GB     1.1GB (91%)
Local Volumes   3         2         450MB     120MB (26%)
Build Cache     412       18        51.8GB    48.9GB (94%)
```

User message continuation:
"Can I just run `docker system prune -a --volumes -f` to wipe everything clean?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-8.
