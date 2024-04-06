import time
from kubernetes import client, config

config.load_kube_config()

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
                        metadata=client.V1ObjectMeta(
                            name=configmap.metadata.name,
                            annotations={k: v for k, v in configmap.metadata.annotations.items() if not k.startswith('ns-object-mirror')}
                        ),
                        data=configmap.data
                    )
                    try:
                        old_configmap = v1.read_namespaced_config_map(configmap.metadata.name, namespace)
                        old_configmap_without_ns_object_mirror_annotations = client.V1ConfigMap(
                            api_version="v1",
                            kind="ConfigMap",
                            metadata=client.V1ObjectMeta(
                                name=old_configmap.metadata.name,
                                annotations={k: v for k, v in old_configmap.metadata.annotations.items() if not k.startswith('ns-object-mirror')} if old_configmap.metadata.annotations is not None else {}
                            ),
                            data=None
                        )
                        if old_configmap.data != new_configmap.data:
                            v1.replace_namespaced_config_map(configmap.metadata.name, namespace, new_configmap)
                            print(f"ConfigMap/Data for {configmap.metadata.name} in namespace {namespace} has been updated.")
                        elif old_configmap_without_ns_object_mirror_annotations.metadata.annotations != new_configmap.metadata.annotations:
                            v1.patch_namespaced_config_map(configmap.metadata.name, namespace, new_configmap)
                            print(f"ConfigMap/Annotations for {configmap.metadata.name} in namespace {namespace} have been updated.")
                        else:
                            print(f"ConfigMap {configmap.metadata.name} in namespace {namespace} is already up-to-date. Skipping.")
                    except client.rest.ApiException as e:
                        if e.status == 404:
                            v1.create_namespaced_config_map(namespace, new_configmap)
                            print(f"ConfigMap {configmap.metadata.name} has been mirrored to namespace {namespace}.")

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
                        metadata=client.V1ObjectMeta(
                            name=secret.metadata.name,
                            annotations={k: v for k, v in secret.metadata.annotations.items() if not k.startswith('ns-object-mirror')}
                        ),
                        data=secret.data
                    )
                    try:
                        old_secret = v1.read_namespaced_secret(secret.metadata.name, namespace)
                        old_secret_without_ns_object_mirror_annotations = client.V1Secret(
                            api_version="v1",
                            kind="Secret",
                            metadata=client.V1ObjectMeta(
                                name=old_secret.metadata.name,
                                annotations={k: v for k, v in old_secret.metadata.annotations.items() if not k.startswith('ns-object-mirror')} if old_secret.metadata.annotations is not None else {}
                            ),
                            data=None
                        )
                        if old_secret.data != new_secret.data:
                            v1.replace_namespaced_secret(secret.metadata.name, namespace, new_secret)
                            print(f"Secret/Data for {secret.metadata.name} in namespace {namespace} has been updated.")
                        elif old_secret_without_ns_object_mirror_annotations.metadata.annotations != new_secret.metadata.annotations:
                            v1.patch_namespaced_secret(secret.metadata.name, namespace, new_secret)
                            print(f"Secret/Annotations for {secret.metadata.name} in namespace {namespace} have been updated.")
                        else:
                            print(f"Secret {secret.metadata.name} in namespace {namespace} is already up-to-date. Skipping.")
                    except client.rest.ApiException as e:
                        if e.status == 404:
                            v1.create_namespaced_secret(namespace, new_secret)
                            print(f"Secret {secret.metadata.name} has been mirrored to namespace {namespace}.")

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
    while True:
        print("--- Running mirror at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " ---")
        run_mirror()
        print("--- Finished running mirror at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ". Sleeping for 30 seconds." + " ---")
        time.sleep(30)
