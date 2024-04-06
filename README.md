# ns-object-mirror
Copy objects from one Kubernetes namespace to another using annotations.

## Usage

Run the Docker image as a deployment on your cluster with a service account that has the necessary permissions to list and create objects in the source and destination namespaces.

The following objects are supported:
- ConfigMap
- Secret

Sample RBAC and deployment files are provided in the `deploy` directory.

```bash
kubectl apply -f deploy/rbac.yaml
kubectl apply -f deploy/deployment.yaml
```

Set the following annotations on the source object:

```yaml
metadata:
  annotations:
    ns-object-mirror/to: "destination-namespace,destination-namespace-2" # Comma separated list of destination namespaces
```
