from kubernetes import client, config, V1ConfigMapList

config.load_kube_config()

v1 = client.CoreV1Api()
configmaps = v1.list_namespaced_config_map("airflow")

print("Listing configmaps with their annotations:")

for configmap in configmaps.items:
    print(f"{configmap.metadata.name}: {configmap.metadata.annotations}")
