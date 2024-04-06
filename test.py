import unittest
from kubernetes import client, config
import app

class TestMirror(unittest.TestCase):
    def setUp(self):
        config.load_kube_config(context="kind-kind")
        self.v1 = client.CoreV1Api()

        # Create test namespace
        self.test_namespace = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(name="test-namespace")
        )
        self.v1.create_namespace(self.test_namespace)

        # Create another namespace to mirror to
        self.mirror_namespace = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(name="mirror-namespace")
        )
        self.v1.create_namespace(self.mirror_namespace)

        # Create test configmap
        self.test_configmap = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(
                name="test-configmap",
                namespace="test-namespace",
                annotations={"ns-object-mirror/to": "mirror-namespace"}
            ),
            data={"key": "value"}
        )
        self.v1.create_namespaced_config_map("test-namespace", self.test_configmap)

        # Create test secret
        self.test_secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(
                name="test-secret",
                namespace="test-namespace",
                annotations={"ns-object-mirror/to": "mirror-namespace"}
            ),
            data={"key": "dmFsdWU="}  # "value" base64 encoded
        )
        self.v1.create_namespaced_secret("test-namespace", self.test_secret)

    def test_mirror(self):
        app.run_mirror()

        # Check if the configmap and secret are mirrored to the mirror-namespace
        mirrored_configmap = self.v1.read_namespaced_config_map("test-configmap", "mirror-namespace")
        self.assertEqual(mirrored_configmap.data, {"key": "value"})

        mirrored_secret = self.v1.read_namespaced_secret("test-secret", "mirror-namespace")
        self.assertEqual(mirrored_secret.data, {"key": "dmFsdWU="})

    def tearDown(self):
        # Delete test objects
        self.v1.delete_namespaced_config_map("test-configmap", "test-namespace")
        self.v1.delete_namespaced_secret("test-secret", "test-namespace")
        self.v1.delete_namespace("test-namespace")
        self.v1.delete_namespace("mirror-namespace")

# Test if existing mirror objects are updated from the original
class TestUpdateMirror(unittest.TestCase):
    def setUp(self):
        config.load_kube_config(context="kind-kind")
        self.v1 = client.CoreV1Api()

        # Create test namespace
        self.test_namespace = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(name="test-namespace-2")
        )
        self.v1.create_namespace(self.test_namespace)

        # Create another namespace to mirror to
        self.mirror_namespace = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(name="mirror-namespace-2")
        )
        self.v1.create_namespace(self.mirror_namespace)

        # Create test configmap
        self.test_configmap = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(
                name="test-configmap",
                namespace="test-namespace-2",
                annotations={"ns-object-mirror/to": "mirror-namespace-2"}
            ),
            data={"key": "value"}
        )
        self.v1.create_namespaced_config_map("test-namespace-2", self.test_configmap)

        # Create mirrored configmap
        self.mirrored_configmap = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(
                name="test-configmap",
                namespace="mirror-namespace-2",
                annotations={"ns-object-mirror/to": "mirror-namespace-2"}
            ),
            data={"key": "old-value"}
        )
        self.v1.create_namespaced_config_map("mirror-namespace-2", self.mirrored_configmap)

        # Create test secret
        self.test_secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(
                name="test-secret",
                namespace="test-namespace-2",
                annotations={"ns-object-mirror/to": "mirror-namespace-2"}
            ),
            data={"key": "dmFsdWU="}  # "value" base64 encoded
        )
        self.v1.create_namespaced_secret("test-namespace-2", self.test_secret)

        # Create mirrored secret
        self.mirrored_secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(
                name="test-secret",
                namespace="mirror-namespace-2",
                annotations={"ns-object-mirror/to": "mirror-namespace-2"}
            ),
            data={"key": "b2xkLXZhbHVl"}  # "old-value" base64 encoded
        )
        self.v1.create_namespaced_secret("mirror-namespace-2", self.mirrored_secret)

    def test_update_mirror(self):
        app.run_mirror()

        # Check if the configmap and secret are mirrored to the mirror-namespace
        mirrored_configmap = self.v1.read_namespaced_config_map("test-configmap", "mirror-namespace-2")
        self.assertEqual(mirrored_configmap.data, {"key": "value"})

        mirrored_secret = self.v1.read_namespaced_secret("test-secret", "mirror-namespace-2")
        self.assertEqual(mirrored_secret.data, {"key": "dmFsdWU="})

    def tearDown(self):
        # Delete test objects
        self.v1.delete_namespaced_config_map("test-configmap", "test-namespace-2")
        self.v1.delete_namespaced_config_map("test-configmap", "mirror-namespace-2")
        self.v1.delete_namespaced_secret("test-secret", "test-namespace-2")
        self.v1.delete_namespaced_secret("test-secret", "mirror-namespace-2")
        self.v1.delete_namespace("test-namespace-2")
        self.v1.delete_namespace("mirror-namespace-2")

if __name__ == '__main__':
    unittest.main()
