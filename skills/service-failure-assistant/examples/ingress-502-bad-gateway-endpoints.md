# Example: Ingress 502 Bad Gateway Caused by Missing Service Endpoints

Sanitized example input for the `service-failure-assistant` skill. Fictional ingress and service
configuration representing a common label mismatch causing an outage.

## Input

User message:
"Our external users are receiving `502 Bad Gateway` when hitting `https://api.example.dev/v1/payments`.
The ingress controller shows upstream errors. Here is the NGINX ingress log and `kubectl describe svc payments-service`:"

Ingress NGINX controller log:

```text
2026/11/20 14:22:01 [error] 1142#1142: *829107 kevent() reported that connect() failed (61: Connection refused) while connecting to upstream, client: 198.51.100.42, server: api.example.dev, request: "POST /v1/payments HTTP/2.0", upstream: "http://10.244.2.89:8080", host: "api.example.dev"
2026/11/20 14:22:05 [warn] 1142#1142: *829112 [ngx_http_ingress_module] no endpoints available for service "payments/payments-service"
```

`kubectl describe svc payments-service -n payments`:

```text
Name:              payments-service
Namespace:         payments
Labels:            app.kubernetes.io/name=payments
Annotations:       <none>
Selector:          app=payment-processor
Type:              ClusterIP
IP Family Policy:  SingleStack
IP Families:       IPv4
IP:                10.96.142.88
IPs:               10.96.142.88
Port:              http  80/TCP
TargetPort:        8080/TCP
Endpoints:         <none>
Session Affinity:  None
Events:            <none>
```

`kubectl get pods -n payments --show-labels`:

```text
NAME                                READY   STATUS    RESTARTS   AGE   LABELS
payments-deploy-57d89b6574-2xk8q    1/1     Running   0          42m   app=payments-processor,env=production
payments-deploy-57d89b6574-9m4lp    1/1     Running   0          42m   app=payments-processor,env=production
```

User message continuation:
"Why is Endpoints showing `<none>` even though the pods are running and ready?"

## What a correct analysis should do

See `tests/test-cases.md` → TC-12.
