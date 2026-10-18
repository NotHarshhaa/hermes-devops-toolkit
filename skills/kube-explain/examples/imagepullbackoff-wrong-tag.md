# Example: ImagePullBackOff (wrong tag)

Sanitized example input for the kube-explain skill. Fictional project, registry
path, and cluster objects; no real credentials.

## Input

User message:
"After our release pipeline ran, the new pods never came up — they sit in
ImagePullBackOff. The tag in the deployment manifest matches the tag produced by
CI. The build succeeded. Here's the output:"

`kubectl get pods -n shop`:

```text
NAME                        READY   STATUS             RESTARTS   AGE
checkout-5b7c8d9f4-hk7pq    0/2     ImagePullBackOff   0          34m
checkout-6d4f5a8b3-pwl2m    2/2     Running            0          4d
```

Relevant event lines from
`kubectl describe pod checkout-5b7c8d9f4-hk7pq -n shop`:

```text
Containers:
  checkout:
    Image:      registry.example.dev/team-acme/checkout-service:v2.4.1
    State:      Waiting
      Reason:   ImagePullBackOff
Events:
  Type     Reason     Age                    From           Message
  ----     ------     ----                   ----           -------
  Normal   Scheduled  34m                    default-scheduler  Successfully assigned shop/checkout-5b7c8d9f4-hk7pq to node-worker-11
  Warning  Failed     12m (x7 over 33m)      kubelet         Failed to pull image "registry.example.dev/team-acme/checkout-service:v2.4.1": rpc error: code = Unknown desc = failed to pull and unpack image "registry.example.dev/team-acme/checkout-service:v2.4.1": failed to resolve reference "registry.example.dev/team-acme/checkout-service:v2.4.1": manifest unknown: manifest unknown
  Warning  BackOff    4m34s (x14 over 31m)   kubelet         Back-off pulling image "registry.example.dev/team-acme/checkout-service:v2.4.1"
```

Inline secret configuration in the deployment spec (excerpt):

```text
  Image Pull Secrets:
    Name:  regcred-team-acme
```

Notes the user added separately:

- CI logs show `docker push ... :v2.4.1` succeeded at 10:02.
- The pipeline runs the build step from a job with its own registry identity.

## What a correct analysis should do

See `tests/test-cases.md` → TC-4.
