import unittest
from unittest.mock import patch, MagicMock
import os

os.environ["SNOWGLOBE_API_KEY"] = "test_api_key"

from snowglobe.client.src import utils  # noqa: E402

os.environ["SNOWGLOBE_API_KEY"] = ""


class TestUtils(unittest.IsolatedAsyncioTestCase):
    @patch("httpx.AsyncClient.get")
    async def test_fetch_experiments_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "exp1"}]
        mock_get.return_value = mock_response

        result = await utils.fetch_experiments()
        self.assertEqual(result, [{"id": 1, "name": "exp1"}])
        mock_get.assert_called_once()

    @patch("httpx.AsyncClient.get")
    async def test_fetch_experiments_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "error"}
        mock_response.text = "error text"
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as exc:
            await utils.fetch_experiments()
        self.assertTrue(
            "error" in str(exc.exception) or "error text" in str(exc.exception)
        )

    @patch("httpx.AsyncClient.get")
    async def test_fetch_messages_full_turn(self, mock_get):
        # Setup parent test chain
        parent_test = {
            "prompt": "parent prompt",
            "response": "parent response",
            "parent_test_id": None,
            "conversation_id": "conv123",
            "id": "parent_id",
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = parent_test
        mock_get.return_value = mock_response

        test = {
            "prompt": "child prompt",
            "response": "child response",
            "parent_test_id": "parent_id",
            "experiment_id": "expid",
            "conversation_id": "conv123",
            "id": "test_id",
        }
        messages = await utils.fetch_messages(test=test)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "parent prompt")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].content, "parent response")
        self.assertEqual(messages[2].role, "user")
        self.assertEqual(messages[2].content, "child prompt")
        self.assertEqual(messages[3].role, "assistant")
        self.assertEqual(messages[3].content, "child response")

    @patch("httpx.AsyncClient.get")
    async def test_fetch_messages_no_response(self, mock_get):
        # No parent
        test = {
            "prompt": "prompt only",
            "experiment_id": "expid",
            "conversation_id": "conv123",
            "id": "test_id",
        }
        messages = await utils.fetch_messages(test=test)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "prompt only")


if __name__ == "__main__":
    unittest.main()
