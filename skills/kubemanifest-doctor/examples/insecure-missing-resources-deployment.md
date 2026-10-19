# Example: Insecure Deployment with Missing Resource Limits and Flawed Probes

Sanitized example input for the `kubemanifest-doctor` skill. Fictional service and container
names. This represents a manifest prepared for a production rollout that contains multiple
operational and security anti-patterns.

## Input

User message:
"Can you review our new microservice deployment manifest before we merge it to our main branch?
It runs fine in minikube, but I want to make sure it is production-ready."

`deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-processor
  namespace: e-commerce
  labels:
    app: order-processor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: order-processor
  template:
    metadata:
      labels:
        app: order-processor
    spec:
      containers:
      - name: order-processor
        image: registry.example.dev/ecommerce/order-processor:1.4.0
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health/deep-db-check
            port: 8080
          initialDelaySeconds: 2
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /health/deep-db-check
            port: 8080
          initialDelaySeconds: 2
          periodSeconds: 5
```

User notes:
- The app handles order queue consumption and takes about 10 seconds to connect to the database on boot.
- `/health/deep-db-check` executes a `SELECT 1` query on the primary PostgreSQL database.

## What a correct analysis should do

See `tests/test-cases.md` → TC-12.
