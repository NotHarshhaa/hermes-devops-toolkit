# Example: Deprecated Ingress API and Service Selector Mismatch

Sanitized example input for the `kubemanifest-doctor` skill. Fictional hostnames and labels.
This represents a manifest bundle that fails admission or leaves traffic disconnected due to
API version obsolescence and mismatched selectors.

## Input

User message:
"We are migrating our manifests to a new Kubernetes 1.28 cluster and our ingress is failing
to apply. Also, the service is not routing traffic to our pods. Here is the YAML:"

`ingress-and-service.yaml`:

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: customer-portal-ingress
  namespace: frontend
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: portal.example.dev
    http:
      paths:
      - path: /
        backend:
          serviceName: customer-portal-svc
          servicePort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: customer-portal-svc
  namespace: frontend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app.kubernetes.io/name: customer-portal
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-portal
  namespace: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: customer-portal
  template:
    metadata:
      labels:
        app: customer-portal
    spec:
      containers:
      - name: web
        image: registry.example.dev/frontend/portal:2.1.0
        ports:
        - containerPort: 3000
```

## What a correct analysis should do

See `tests/test-cases.md` → TC-13.
