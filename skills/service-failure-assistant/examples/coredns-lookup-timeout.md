# Example: In-Cluster CoreDNS Resolution Timeout

Sanitized example input for the `service-failure-assistant` skill. Fictional pod
logs and CoreDNS configuration representing a DNS resolution timeout crisis.

## Input

User message:
"Pods in our `analytics` namespace suddenly cannot reach our internal database or external APIs.
The application logs are flooded with DNS lookup errors. Here is the application stack trace,
pod resolv.conf, and CoreDNS logs:"

Application pod log:

```text
2026-11-20T16:04:12.891Z [ERROR] failed to connect to database: dial tcp: lookup postgres.database.svc.cluster.local on 10.96.0.10:53: read udp 10.244.1.45:49152->10.96.0.10:53: i/o timeout
2026-11-20T16:04:17.893Z [ERROR] failed to fetch remote token: dial tcp: lookup auth.company.internal on 10.96.0.10:53: read udp 10.244.1.45:49153->10.96.0.10:53: i/o timeout
```

Pod `/etc/resolv.conf`:

```text
nameserver 10.96.0.10
search analytics.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

`kubectl logs -n kube-system -l k8s-app=kube-dns --tail=20`:

```text
[INFO] 10.244.1.45:49152 - 12048 "A IN postgres.database.svc.cluster.local.analytics.svc.cluster.local. udp 84 false 512" NXDOMAIN qr,aa,rd 177 0.00018421s
[INFO] 10.244.1.45:49152 - 12049 "A IN postgres.database.svc.cluster.local.svc.cluster.local. udp 74 false 512" NXDOMAIN qr,aa,rd 167 0.00015410s
[WARNING] plugin/forward: no nameservers found
[ERROR] plugin/errors: 2 auth.company.internal.analytics.svc.cluster.local. A: unreachable backend
```

`kubectl get pods -n kube-system -l k8s-app=kube-dns`:

```text
NAME                       READY   STATUS             RESTARTS   AGE
coredns-668d6bf947-49fks   0/1     CrashLoopBackOff   8          32m
coredns-668d6bf947-8q2zm   1/1     Running            0          4d
```

User message continuation:
"Why is CoreDNS timing out and crashing?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-13.
