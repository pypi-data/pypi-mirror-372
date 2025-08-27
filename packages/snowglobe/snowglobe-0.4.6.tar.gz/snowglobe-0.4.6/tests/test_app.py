import unittest
import os
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

# Mock config before importing app
os.environ["SNOWGLOBE_API_KEY"] = "test"
from src.snowglobe.client.src.app import (  # noqa: E402
    ConfigurableRateLimiter,
    rate_limit,
    process_risk_evaluation,
    process_test,
    poll_for_completions,
    poll_for_risk_evaluations,
    create_client,
    start_client,
    route_request_times,
    queued_tests,
    queued_evaluations,
    risks,
)
from src.snowglobe.client.src.models import (  # noqa: E402
    SnowglobeMessage,
    CompletionFunctionOutputs,
    RiskEvaluationOutputs,
)

from fastapi import HTTPException  # noqa: E402

os.environ["SNOWGLOBE_API_KEY"] = ""


class TestConfigurableRateLimiter(unittest.TestCase):
    def setUp(self):
        self.rate_limiter = ConfigurableRateLimiter()
        # Clear any existing rate limit data
        route_request_times.clear()

    def test_init(self):
        limiter = ConfigurableRateLimiter()
        self.assertEqual(limiter.route_configs, {})

    def test_configure_route(self):
        self.rate_limiter.configure_route("test_route", 10, 60)
        expected = {"max_requests": 10, "time_window": 60}
        self.assertEqual(self.rate_limiter.route_configs["test_route"], expected)

    def test_get_route_config_existing(self):
        self.rate_limiter.configure_route("test_route", 5, 30)
        config = self.rate_limiter.get_route_config("test_route")
        self.assertEqual(config, {"max_requests": 5, "time_window": 30})

    def test_get_route_config_default(self):
        config = self.rate_limiter.get_route_config("nonexistent_route")
        self.assertEqual(config, {"max_requests": 1, "time_window": 1})

    def test_is_allowed_first_request(self):
        self.rate_limiter.configure_route("test_route", 2, 60)
        result = self.rate_limiter.is_allowed("client1", "test_route")
        self.assertTrue(result)

    def test_is_allowed_within_limit(self):
        self.rate_limiter.configure_route("test_route", 3, 60)
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))

    def test_is_allowed_exceeds_limit(self):
        self.rate_limiter.configure_route("test_route", 2, 60)
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))
        self.assertFalse(self.rate_limiter.is_allowed("client1", "test_route"))

    @mock.patch("time.time")
    def test_is_allowed_time_window_reset(self, mock_time):
        # First request at time 0
        mock_time.return_value = 0
        self.rate_limiter.configure_route("test_route", 1, 2)
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))

        # Second request still at time 0 - should be rejected
        self.assertFalse(self.rate_limiter.is_allowed("client1", "test_route"))

        # Request after time window - should be allowed
        mock_time.return_value = 3
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))

    def test_is_allowed_different_clients(self):
        self.rate_limiter.configure_route("test_route", 1, 60)
        self.assertTrue(self.rate_limiter.is_allowed("client1", "test_route"))
        self.assertTrue(self.rate_limiter.is_allowed("client2", "test_route"))

    def test_is_allowed_different_routes(self):
        self.rate_limiter.configure_route("route1", 1, 60)
        self.rate_limiter.configure_route("route2", 1, 60)
        self.assertTrue(self.rate_limiter.is_allowed("client1", "route1"))
        self.assertTrue(self.rate_limiter.is_allowed("client1", "route2"))


class TestRateLimitDecorator(unittest.TestCase):
    def setUp(self):
        route_request_times.clear()
        self.mock_request = MagicMock()
        self.mock_request.client.host = "127.0.0.1"

    @mock.patch("src.snowglobe.client.src.app.rate_limiter")
    async def test_rate_limit_decorator_allowed(self, mock_rate_limiter):
        mock_rate_limiter.is_allowed.return_value = True

        @rate_limit("test_route", 5, 60)
        async def test_func(request):
            return {"status": "ok"}

        result = await test_func(self.mock_request)
        self.assertEqual(result, {"status": "ok"})
        mock_rate_limiter.configure_route.assert_called_with("test_route", 5, 60)
        mock_rate_limiter.is_allowed.assert_called_with("127.0.0.1", "test_route")

    @mock.patch("src.snowglobe.client.src.app.rate_limiter")
    async def test_rate_limit_decorator_rejected(self, mock_rate_limiter):
        mock_rate_limiter.is_allowed.return_value = False
        mock_rate_limiter.get_route_config.return_value = {
            "max_requests": 5,
            "time_window": 60,
        }

        @rate_limit("test_route", 5, 60)
        async def test_func(request):
            return {"status": "ok"}

        with self.assertRaises(HTTPException) as cm:
            await test_func(self.mock_request)

        self.assertEqual(cm.exception.status_code, 429)
        self.assertIn("Rate limit exceeded", cm.exception.detail)


class TestProcessRiskEvaluation(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "id": "test-123",
            "experiment_id": "exp-456",
            "prompt": "test prompt",
        }
        self.mock_messages = [SnowglobeMessage(role="user", content="test message")]

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_messages")
    async def test_process_risk_evaluation_async_function(
        self, mock_fetch_messages, mock_client
    ):
        mock_fetch_messages.return_value = self.mock_messages

        # Mock async risk function
        async def mock_risk_fn(request):
            return RiskEvaluationOutputs(
                triggered=True, severity=3, reason="test reason"
            )

        risks["test_risk"] = mock_risk_fn

        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        await process_risk_evaluation(self.test_data, "test_risk")

        mock_fetch_messages.assert_called_once_with(test=self.test_data)

        # Cleanup
        del risks["test_risk"]

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_messages")
    async def test_process_risk_evaluation_sync_function(
        self, mock_fetch_messages, mock_client
    ):
        mock_fetch_messages.return_value = self.mock_messages

        # Mock sync risk function
        def mock_risk_fn(request):
            return RiskEvaluationOutputs(triggered=False, severity=1, reason="no risk")

        risks["test_risk"] = mock_risk_fn

        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        await process_risk_evaluation(self.test_data, "test_risk")

        mock_fetch_messages.assert_called_once_with(test=self.test_data)

        # Cleanup
        del risks["test_risk"]

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_messages")
    async def test_process_risk_evaluation_http_error(
        self, mock_fetch_messages, mock_client
    ):
        mock_fetch_messages.return_value = self.mock_messages

        def mock_risk_fn(request):
            return RiskEvaluationOutputs(triggered=True, severity=2, reason="test")

        risks["test_risk"] = mock_risk_fn

        # Mock HTTP error
        mock_response = AsyncMock()
        mock_response.is_success = False
        mock_response.text = "Server error"
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        with self.assertRaises(Exception) as cm:
            await process_risk_evaluation(self.test_data, "test_risk")

        self.assertIn("Error posting risk evaluation", str(cm.exception))

        # Cleanup
        del risks["test_risk"]


class TestProcessTest(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "id": "test-123",
            "experiment_id": "exp-456",
            "prompt": "test prompt",
            "persona": "test persona",
        }
        self.mock_messages = [SnowglobeMessage(role="user", content="test message")]
        queued_tests.clear()

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_messages")
    async def test_process_test_async_function(self, mock_fetch_messages, mock_client):
        mock_fetch_messages.return_value = self.mock_messages

        # Mock async completion function
        async def mock_completion_fn(request):
            return CompletionFunctionOutputs(response="test response")

        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_client.return_value.__aenter__.return_value.put.return_value = (
            mock_response
        )

        # Add test to queue first
        queued_tests["test-123"] = True

        result = await process_test(self.test_data, mock_completion_fn)

        self.assertEqual(result.response, "test response")
        mock_fetch_messages.assert_called_once_with(test=self.test_data)
        # Test should be removed from queue
        self.assertNotIn("test-123", queued_tests)

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_messages")
    async def test_process_test_sync_function(self, mock_fetch_messages, mock_client):
        mock_fetch_messages.return_value = self.mock_messages

        # Mock sync completion function
        def mock_completion_fn(request):
            return CompletionFunctionOutputs(response="sync response")

        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_client.return_value.__aenter__.return_value.put.return_value = (
            mock_response
        )

        result = await process_test(self.test_data, mock_completion_fn)

        self.assertEqual(result.response, "sync response")
        mock_fetch_messages.assert_called_once_with(test=self.test_data)


class TestPollingFunctions(unittest.TestCase):
    def setUp(self):
        queued_tests.clear()
        queued_evaluations.clear()

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_experiments")
    async def test_poll_for_completions_success(
        self, mock_fetch_experiments, mock_client
    ):
        mock_experiments = [{"id": "exp-1"}]
        mock_fetch_experiments.return_value = mock_experiments

        mock_tests = [
            {"id": "test-1", "response": None},
            {"id": "test-2", "response": "existing response"},
        ]

        # Mock the HTTP client chain
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock tests response
        mock_tests_response = AsyncMock()
        mock_tests_response.is_success = True
        mock_tests_response.json.return_value = mock_tests
        mock_client_instance.get.return_value = mock_tests_response

        # Mock completion response
        mock_completion_response = AsyncMock()
        mock_completion_response.is_success = True
        mock_client_instance.post.return_value = mock_completion_response

        await poll_for_completions()

        # Should queue test-1 but not test-2 (already has response)
        self.assertIn("test-1", queued_tests)
        self.assertNotIn("test-2", queued_tests)

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_experiments")
    async def test_poll_for_completions_rate_limit(
        self, mock_fetch_experiments, mock_client
    ):
        mock_experiments = [{"id": "exp-1"}]
        mock_fetch_experiments.return_value = mock_experiments

        mock_tests = [{"id": "test-1", "response": None}]

        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock tests response
        mock_tests_response = AsyncMock()
        mock_tests_response.is_success = True
        mock_tests_response.json.return_value = mock_tests
        mock_client_instance.get.return_value = mock_tests_response

        # Mock rate limit response
        mock_completion_response = AsyncMock()
        mock_completion_response.is_success = False
        mock_completion_response.status_code = 429
        mock_completion_response.text = "Rate limited"
        mock_client_instance.post.return_value = mock_completion_response

        with self.assertRaises(HTTPException) as cm:
            await poll_for_completions()

        self.assertEqual(cm.exception.status_code, 429)

    @mock.patch("httpx.AsyncClient")
    @mock.patch("src.snowglobe.client.src.app.fetch_experiments")
    async def test_poll_for_risk_evaluations(self, mock_fetch_experiments, mock_client):
        mock_experiments = [
            {
                "id": "exp-1",
                "source_data": {
                    "evaluation_configuration": {"test_risk": {"enabled": True}}
                },
            }
        ]
        mock_fetch_experiments.return_value = mock_experiments

        # Add a risk to test
        risks["test_risk"] = lambda x: RiskEvaluationOutputs(triggered=True)

        mock_tests = [{"id": "test-1", "response": "test response"}]

        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock tests response
        mock_tests_response = AsyncMock()
        mock_tests_response.is_success = True
        mock_tests_response.json.return_value = mock_tests
        mock_client_instance.get.return_value = mock_tests_response

        # Mock risk evaluation response
        mock_risk_response = AsyncMock()
        mock_risk_response.is_success = True
        mock_client_instance.post.return_value = mock_risk_response

        await poll_for_risk_evaluations()

        self.assertIn("test-1", queued_evaluations)

        # Cleanup
        del risks["test_risk"]


class TestFastAPIApp(unittest.TestCase):
    def setUp(self):
        self.app = create_client()

    def test_create_client_returns_fastapi_app(self):
        from fastapi import FastAPI

        self.assertIsInstance(self.app, FastAPI)

    @mock.patch("uvicorn.run")
    def test_start_client(self, mock_uvicorn_run):
        start_client()
        mock_uvicorn_run.assert_called_once()
        args, kwargs = mock_uvicorn_run.call_args
        self.assertEqual(kwargs["host"], "0.0.0.0")
        self.assertEqual(kwargs["port"], 8000)
        self.assertEqual(kwargs["log_level"], "warning")


if __name__ == "__main__":
    unittest.main()
