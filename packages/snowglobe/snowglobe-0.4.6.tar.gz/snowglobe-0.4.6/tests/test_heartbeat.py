import unittest
from fastapi.testclient import TestClient
from src.snowglobe.client.src.app import create_client, apps


class TestHeartbeatEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = create_client()
        self.client = TestClient(self.app)
        # Add a dummy app to simulate a loaded application
        apps["dummy_app_id"] = {"completion_fn": lambda x: None, "name": "Dummy App"}

    def tearDown(self):
        apps.clear()

    def test_heartbeat_success(self):
        response = self.client.post("/heartbeat", json={"app_id": "dummy_app_id"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "heartbeat received")

    def test_heartbeat_missing_app_id(self):
        response = self.client.post("/heartbeat", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Application ID must be provided", response.json()["detail"])

    def test_heartbeat_app_not_found(self):
        response = self.client.post("/heartbeat", json={"app_id": "not_found"})
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "Application with ID not_found not found", response.json()["detail"]
        )


if __name__ == "__main__":
    unittest.main()
