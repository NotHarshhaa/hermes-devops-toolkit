# Example: GitHub Actions — Docker image build failure

Sanitized example input for the pipeline-failure-translator skill. Fictional
project, fictional registry path, no real credentials. This is what the user might
paste into a session when asking "why did my workflow fail?"

## Input

User message:
"I'm building a Docker image in GitHub Actions and the workflow keeps failing at the
build step. I didn't change the Dockerfile recently. Here's the log from the failed
run:"

```text
name: Build and Push Image
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to container registry
        uses: docker/login-action@v3
        with:
          registry: registry.example.dev
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: registry.example.dev/team-acme/service-api:latest
```

Run log (job `build`, step `Build and push`):

```text
2026-10-14T09:12:03.4012Z ##[group]Run docker/build-push-action@v6
2026-10-14T09:12:03.4021Z with:
2026-10-14T09:12:03.4025Z     context: .
2026-10-14T09:12:03.4030Z     push: true
2026-10-14T09:12:03.4034Z     tags: registry.example.dev/team-acme/service-api:latest
2026-10-14T09:12:03.4039Z ##[endgroup]
2026-10-14T09:12:04.1100Z #1 [internal] load git source
2026-10-14T09:12:04.8233Z #1 0.214 resolved "https://github.com/team-acme/service-api.git" to commit "a1b2c3d"
2026-10-14T09:12:05.0031Z #1 DONE 0.9s
2026-10-14T09:12:05.0100Z
2026-10-14T09:12:05.0110Z #3 [internal] load build definition from Dockerfile
2026-10-14T09:12:05.0131Z #3 DONE 0.0s
2026-10-14T09:12:05.0400Z
2026-10-14T09:12:05.0401Z #4 [internal] load metadata for docker.io/library/python:3.11-slim
2026-10-14T09:12:06.1130Z #4 DONE 1.1s
2026-10-14T09:12:06.1140Z
2026-10-14T09:12:06.1150Z #5 [1/6] FROM docker.io/library/python:3.11-slim
2026-10-14T09:12:07.2210Z #5 resolve docker.io/library/python:3.11-slim done
2026-10-14T09:12:09.4410Z #5 extracting sha256:6f1e9a2... 2.1MB / 26.4MB
2026-10-14T09:12:13.8821Z #5 extracting sha256:6f1e9a2... 26.4MB / 26.4MB 3.4s done
2026-10-14T09:12:13.9000Z #5 DONE 7.8s
2026-10-14T09:12:13.9100Z
2026-10-14T09:12:13.9101Z #7 [2/6] WORKDIR /app
2026-10-14T09:12:14.0100Z #7 DONE 0.1s
2026-10-14T09:12:14.0200Z
2026-10-14T09:12:14.0201Z #8 [3/6] COPY requirements.txt .
2026-10-14T09:12:14.0500Z #8 DONE 0.0s
2026-10-14T09:12:14.0600Z
2026-10-14T09:12:14.0601Z #9 [4/6] RUN pip install -r requirements.txt
2026-10-14T09:12:15.1200Z #9 1.001 Collecting fastapi==0.111.0
2026-10-14T09:12:15.8300Z #9 1.701   Downloading fastapi-0.111.0-py3-none-any.whl (102 kB)
2026-10-14T09:12:16.0100Z #9 1.920 Collecting uvicorn==0.30.1
2026-10-14T09:12:16.4400Z #9 2.312   Downloading uvicorn-0.30.1-py3-none-any.whl (62 kB)
2026-10-14T09:12:16.4500Z #9 2.404 Collecting requests==2.99.0
2026-10-14T09:12:16.4600Z #9 2.407 ERROR: Could not find a version that satisfies the requirement requests==2.99.0
2026-10-14T09:12:16.4610Z #9 2.407 ERROR: No matching distribution found for requests==2.99.0
2026-10-14T09:12:16.4700Z #9 ERROR: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully: exit code: 1
2026-10-14T09:12:16.4800Z #9 process "/bin/sh -c pip install -r requirements.txt" did not complete successfully: exit code: 1
2026-10-14T09:12:16.5000Z
2026-10-14T09:12:16.5100Z #10 [5/6] COPY . .
2026-10-14T09:12:16.5101Z #10 CANCELED
2026-10-14T09:12:16.5200Z #11 [6/6] RUN chmod +x ./entrypoint.sh
2026-10-14T09:12:16.5201Z #11 CANCELED
2026-10-14T09:12:16.5300Z
2026-10-14T09:12:16.6100Z ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully: exit code: 1
2026-10-14T09:12:16.6200Z
2026-10-14T09:12:16.6300Z Warning: Docker images are now built and pushed to privileged containers via buildx. See docs.
2026-10-14T09:12:16.7000Z ##[error]Process completed with exit code 1.
2026-10-14T09:12:16.7100Z Error: buildx failed with: ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully: exit code: 1
```

## What a correct analysis should do

See `tests/test-cases.md` → TC-1.
