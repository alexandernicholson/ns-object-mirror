from kubernetes import client, config

config.load_kube_config(context="kind-kind")

v1 = client.CoreV1Api()

# Get a list of namespaces
namespaces = v1.list_namespace()

# Get configmaps and secrets for all namespaces
configmaps = v1.list_config_map_for_all_namespaces()
secrets = v1.list_secret_for_all_namespaces()

# Find the annotation "ns-object-mirror/to" in the configmap, which is a comma-separated list of namespaces to mirror the object to

for configmap in configmaps.items:
    if "ns-object-mirror/to" in configmap.metadata.annotations if configmap.metadata.annotations is not None else False:
        namespaces = configmap.metadata.annotations["ns-object-mirror/to"].split(",")
        print(f"ConfigMap {configmap.metadata.name} should be mirrored to the following namespaces: {namespaces}")

        for namespace in namespaces:
            if namespace not in [ns.metadata.name for ns in namespaces.items]:
                print(f"Namespace {namespace} does not exist. Skipping.")
                continue
            else:
                new_configmap = client.V1ConfigMap(
                    api_version="v1",
                    kind="ConfigMap",
                    metadata=client.V1ObjectMeta(name=configmap.metadata.name),
                    data=configmap.data
                )
                v1.create_namespaced_config_map(namespace, new_configmap)
                print(f"ConfigMap {configmap.metadata.name} has been mirrored to namespace {namespace}.")
    else:
        print(f"ConfigMap {configmap.metadata.name} in {configmap.metadata.namespace} does not have the annotation 'ns-object-mirror/to'. Skipping.")

for secret in secrets.items:
    if "ns-object-mirror/to" in secret.metadata.annotations if secret.metadata.annotations is not None else False:
        namespaces = secret.metadata.annotations["ns-object-mirror/to"].split(",")
        print(f"Secret {secret.metadata.name} should be mirrored to the following namespaces: {namespaces}")

        for namespace in namespaces:
            if namespace not in [ns.metadata.name for ns in namespaces.items]:
                print(f"Namespace {namespace} does not exist. Skipping.")
                continue
            else:
                new_secret = client.V1Secret(
                    api_version="v1",
                    kind="Secret",
                    metadata=client.V1ObjectMeta(name=secret.metadata.name),
                    data=secret.data
                )
                v1.create_namespaced_secret(namespace, new_secret)
                print(f"Secret {secret.metadata.name} has been mirrored to namespace {namespace}.")
    else:
        print(f"Secret {secret.metadata.name} in {secret.metadata.namespace} does not have the annotation 'ns-object-mirror/to'. Skipping.")
