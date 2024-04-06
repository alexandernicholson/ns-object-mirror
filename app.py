from kubernetes import client, config

config.load_kube_config(context="kind-kind")

v1 = client.CoreV1Api()

def mirror_configmaps(configmaps, namespaces):
    for configmap in configmaps.items:
        if "ns-object-mirror/to" in configmap.metadata.annotations if configmap.metadata.annotations is not None else False:
            namespaces_to = configmap.metadata.annotations["ns-object-mirror/to"].split(",")
            print(f"ConfigMap {configmap.metadata.name} should be mirrored to the following namespaces: {namespaces_to}")

            for namespace in namespaces_to:
                if namespace not in namespaces:
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

def mirror_secrets(secrets, namespaces):
    for secret in secrets.items:
        if "ns-object-mirror/to" in secret.metadata.annotations if secret.metadata.annotations is not None else False:
            namespaces_to = secret.metadata.annotations["ns-object-mirror/to"].split(",")
            print(f"Secret {secret.metadata.name} should be mirrored to the following namespaces: {namespaces_to}")

            for namespace in namespaces_to:
                if namespace not in namespaces:
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

def run_mirror():
    # Get a list of namespaces
    namespaces = [namespace.metadata.name for namespace in v1.list_namespace().items]

    # Get configmaps and secrets for all namespaces
    configmaps = v1.list_config_map_for_all_namespaces()
    secrets = v1.list_secret_for_all_namespaces()

    # Mirror configmaps and secrets
    mirror_configmaps(configmaps, namespaces)
    mirror_secrets(secrets, namespaces)

if __name__ == "__main__":
    run_mirror()
