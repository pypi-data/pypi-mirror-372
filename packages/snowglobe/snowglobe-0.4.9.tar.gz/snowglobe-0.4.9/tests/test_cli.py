import json
import os
import signal
import tempfile
import unittest
from unittest import mock

os.environ["SNOWGLOBE_API_KEY"] = "test"

import typer  # noqa: E402

from snowglobe.client.src import cli  # noqa: E402
from typer.testing import CliRunner  # noqa: E402

os.environ["SNOWGLOBE_API_KEY"] = ""


class TestCli(unittest.TestCase):
    def setUp(self):
        self._cwd_patch = mock.patch("os.getcwd", return_value=os.getcwd())
        self._cwd_patch.start()
        self.addCleanup(self._cwd_patch.stop)
        self._chdir_patch = mock.patch("os.chdir")
        self._chdir_patch.start()
        self.addCleanup(self._chdir_patch.stop)

    @mock.patch("time.sleep")
    @mock.patch("uvicorn.run")
    @mock.patch("snowglobe.client.src.cli_utils.console.status")
    def test_auth(self, mock_status, mock_uvicorn, mock_sleep):
        """Test that snowglobe-connect auth works in three scenarios."""

        # Configure status mock to be a simple context manager
        mock_status.return_value.__enter__ = mock.Mock()
        mock_status.return_value.__exit__ = mock.Mock(return_value=None)

        # Test Case 1: No API key is set - should trigger browser auth flow
        with mock.patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            with mock.patch("tempfile.mkdtemp"):
                with mock.patch("os.path.exists", return_value=False):
                    with mock.patch("webbrowser.open") as mock_browser:
                        with mock.patch(
                            "snowglobe.client.src.cli._poll_for_api_key",
                            return_value=True,
                        ) as mock_poll:
                            # Run the auth command
                            cli.auth()

                            # Verify browser was called
                            mock_browser.assert_called_once()
                            browser_url = mock_browser.call_args[0][0]

                            # Check URL format
                            self.assertIn(
                                "snowglobe.so/app/keys/client-connect",
                                browser_url,
                            )
                            self.assertIn("port=9001", browser_url)  # Default port
                            self.assertIn("token=", browser_url)  # Should have a token

                            # Verify polling was initiated
                            mock_poll.assert_called_once()

        # Test Case 2: API key is set in environment - should skip browser auth
        with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "env_test_key"}):
            with mock.patch("webbrowser.open") as mock_browser:
                with mock.patch(
                    "snowglobe.client.src.cli._show_auth_success_next_steps"
                ) as mock_success_steps:
                    # Run the auth command
                    cli.auth()

                    # Verify browser was NOT called
                    mock_browser.assert_not_called()

                    # Verify success steps were shown
                    mock_success_steps.assert_called_once()

        # Test Case 3: API key is set in config file - should skip browser auth
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, ".snowglobe", "config.rc")
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            # Write API key to config file
            with open(config_file, "w") as f:
                f.write("SNOWGLOBE_API_KEY=config_test_key\n")

            with mock.patch.dict(os.environ, {}, clear=True):  # Clear env vars
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch("webbrowser.open") as mock_browser:
                        with mock.patch(
                            "snowglobe.client.src.cli._show_auth_success_next_steps"
                        ) as mock_success_steps:
                            # Run the auth command
                            cli.auth()

                            # Verify browser was NOT called
                            mock_browser.assert_not_called()

                            # Verify success steps were shown
                            mock_success_steps.assert_called_once()

        # Test Case 4: Verify API key storage after successful auth
        with mock.patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                config_file = os.path.join(tmpdir, ".snowglobe", "config.rc")

                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch("webbrowser.open"):
                        # Mock successful polling that writes API key
                        def mock_poll_success(rc_path):
                            os.makedirs(os.path.dirname(rc_path), exist_ok=True)
                            with open(rc_path, "w") as f:
                                f.write("SNOWGLOBE_API_KEY=new_test_key\n")
                            return True

                        with mock.patch(
                            "snowglobe.client.src.cli._poll_for_api_key",
                            side_effect=mock_poll_success,
                        ):
                            # Run the auth command
                            cli.auth()

                            # Verify API key was written to config file
                            self.assertTrue(os.path.exists(config_file))
                            with open(config_file, "r") as f:
                                content = f.read()
                                self.assertIn("SNOWGLOBE_API_KEY=new_test_key", content)

    @mock.patch("time.sleep")  # Skip actual sleep delays
    @mock.patch(
        "snowglobe.client.src.cli_utils.console.status"
    )  # Mock Rich console status
    @mock.patch(
        "snowglobe.client.src.cli.check_auth_status"
    )  # Mock authentication check in cli module
    @mock.patch(
        "snowglobe.client.src.cli.get_remote_applications"
    )  # Mock application fetch in cli module
    @mock.patch(
        "snowglobe.client.src.cli.select_application_interactive"
    )  # Mock application selection in cli module
    @mock.patch(
        "snowglobe.client.src.cli.select_stateful_interactive"
    )  # Mock application selection in cli module
    def test_init(
        self,
        mock_select_stateful,
        mock_select_app,
        mock_get_apps,
        mock_check_auth,
        mock_status,
        mock_sleep,
    ):
        """Test that snowglobe-connect init works correctly."""

        # Configure status mock to be a simple context manager
        mock_status.return_value.__enter__ = mock.Mock()
        mock_status.return_value.__exit__ = mock.Mock(return_value=None)

        # Mock authentication check to succeed
        mock_check_auth.return_value = (True, "Authenticated", {})

        # Mock remote applications response
        mock_applications = [
            {
                "id": "test_app_123",
                "name": "Test Application",
                "description": "A test application for unit testing",
                "updated_at": "2025-01-01T00:00:00.000Z",
            },
            {
                "id": "demo_app_456",
                "name": "Demo App",
                "description": "Demo application",
                "updated_at": "2025-01-02T00:00:00.000Z",
            },
        ]
        mock_get_apps.return_value = (True, mock_applications, "Success")

        # Mock user selecting the first application
        mock_select_app.return_value = mock_applications[0]
        mock_select_stateful.return_value = False
        # Run the init command in a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("os.getcwd", return_value=tmpdir):
                with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "test_api_key"}):
                    # Run the init command (pass default values for typer options)
                    cli.init(file=None, stateful=False)

                # Verify authentication was checked
                mock_check_auth.assert_called_once()

                # Verify applications were fetched
                mock_get_apps.assert_called_once()

                # Verify user was prompted to select an application
                mock_select_app.assert_called_once_with(mock_applications)

                # Verify .snowglobe directory was created
                snowglobe_dir = os.path.join(tmpdir, ".snowglobe")
                self.assertTrue(os.path.exists(snowglobe_dir))

                # Verify agents.json was created and configured correctly
                agents_file = os.path.join(snowglobe_dir, "agents.json")
                self.assertTrue(os.path.exists(agents_file))

                with open(agents_file, "r") as f:
                    agents_data = json.load(f)

                # Should have one entry for the selected application
                self.assertEqual(len(agents_data), 1)

                # Find the agent file that was created
                agent_filename = None
                for filename in agents_data.keys():
                    if filename.endswith(".py"):
                        agent_filename = filename
                        break

                self.assertIsNotNone(agent_filename)

                # Verify agents.json has correct structure
                agent_info = agents_data[agent_filename]
                self.assertEqual(agent_info["uuid"], "test_app_123")
                self.assertEqual(agent_info["name"], "Test Application")

                # Verify agent wrapper file was created
                agent_file_path = os.path.join(tmpdir, agent_filename)
                self.assertTrue(os.path.exists(agent_file_path))

                # Verify agent wrapper file has correct content and format
                with open(agent_file_path, "r") as f:
                    agent_content = f.read()

                # Check for required imports
                self.assertIn(
                    "from snowglobe.client import CompletionRequest, CompletionFunctionOutputs",
                    agent_content,
                )

                # Check for required function definition
                self.assertIn(
                    "def process_scenario(request: CompletionRequest) -> CompletionFunctionOutputs:",
                    agent_content,
                )

                # Check that the file is valid Python (can be parsed)
                try:
                    compile(agent_content, agent_filename, "exec")
                except SyntaxError:
                    self.fail(
                        f"Generated agent file {agent_filename} has invalid Python syntax"
                    )

                # Verify filename format (should be sanitized app name)
                expected_filename = (
                    "test_application.py"  # Sanitized version of "Test Application"
                )
                self.assertEqual(agent_filename, expected_filename)

    @mock.patch("time.sleep")
    @mock.patch("snowglobe.client.src.cli_utils.console.status")
    @mock.patch("snowglobe.client.src.cli.check_auth_status")
    @mock.patch("snowglobe.client.src.cli.get_remote_applications")
    @mock.patch("snowglobe.client.src.cli.select_application_interactive")
    @mock.patch("snowglobe.client.src.cli.select_stateful_interactive")
    def test_init_with_file_option_creates_nested_path_and_mapping(
        self,
        mock_select_stateful,
        mock_select_app,
        mock_get_apps,
        mock_check_auth,
        mock_status,
        mock_sleep,
    ):
        """snowglobe-connect init --file /abs/path/inside/project creates file and mapping."""

        # Configure status mock to be a simple context manager
        mock_status.return_value.__enter__ = mock.Mock()
        mock_status.return_value.__exit__ = mock.Mock(return_value=None)

        mock_check_auth.return_value = (True, "Authenticated", {})
        mock_applications = [
            {
                "id": "app_abc",
                "name": "My Fancy App",
                "description": "desc",
                "updated_at": "2025-01-02T00:00:00.000Z",
            }
        ]
        mock_get_apps.return_value = (True, mock_applications, "Success")
        mock_select_app.return_value = mock_applications[0]
        mock_select_stateful.return_value = False  # Default to stateless

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Ensure cwd is the project root
            with mock.patch("os.getcwd", return_value=tmpdir):
                # Build an absolute file path inside the project
                abs_path = os.path.join(tmpdir, "agents", "my_agent")

                # Invoke the CLI
                result = runner.invoke(
                    cli.cli_app,
                    [
                        "init",
                        "--file",
                        abs_path,
                    ],
                )

                # Should succeed
                self.assertEqual(result.exit_code, 0, msg=result.output)

                # File should exist with .py suffix and nested directory created
                expected_file = os.path.join(tmpdir, "agents", "my_agent.py")
                self.assertTrue(os.path.exists(expected_file))

                # Mapping should use relative POSIX path
                agents_file = os.path.join(tmpdir, ".snowglobe", "agents.json")
                self.assertTrue(os.path.exists(agents_file))
                with open(agents_file, "r") as f:
                    agents_data = json.load(f)

                self.assertIn("agents/my_agent.py", agents_data)
                self.assertEqual(agents_data["agents/my_agent.py"]["uuid"], "app_abc")
                self.assertEqual(
                    agents_data["agents/my_agent.py"]["name"], "My Fancy App"
                )

    @mock.patch("time.sleep")  # Skip actual sleep delays
    @mock.patch(
        "snowglobe.client.src.cli_utils.console.status"
    )  # Mock Rich console status
    @mock.patch("snowglobe.client.src.cli.get_project_manager")  # Mock project manager
    @mock.patch("typer.prompt")  # Mock user input prompts
    def test_test(self, mock_prompt, mock_get_pm, mock_status, mock_sleep):
        """Test that snowglobe-connect test works correctly in various scenarios."""

        # Configure status mock to be a simple context manager
        mock_status.return_value.__enter__ = mock.Mock()
        mock_status.return_value.__exit__ = mock.Mock(return_value=None)

        # Test Case 1: Missing project (no .snowglobe directory)
        mock_pm = mock.Mock()
        mock_get_pm.return_value = mock_pm
        mock_pm.validate_project.return_value = (
            False,
            ["No .snowglobe directory found"],
        )

        with self.assertRaises(typer.Exit) as cm:
            cli.test(filename=None)
        self.assertEqual(cm.exception.exit_code, 1)
        mock_pm.validate_project.assert_called_once()

        # Test Case 2: Empty project (no agents)
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_pm.list_agents.return_value = []

        with self.assertRaises(typer.Exit) as cm:
            cli.test(filename=None)
        self.assertEqual(cm.exception.exit_code, 1)
        mock_pm.list_agents.assert_called_once()

        # Test Case 3: Single agent - should auto-select
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_agents = [("test_agent.py", {"uuid": "test_123", "name": "Test Agent"})]
        mock_pm.list_agents.return_value = mock_agents

        with mock.patch(
            "snowglobe.client.src.cli.test_agent_wrapper"
        ) as mock_test_wrapper:
            mock_test_wrapper.return_value = (True, "Connected")

            cli.test(filename=None)

            mock_test_wrapper.assert_called_once_with(
                "test_agent.py", "test_123", "Test Agent"
            )

        # Test Case 4: Multiple agents - should prompt for selection
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_agents = [
            ("agent1.py", {"uuid": "test_123", "name": "Agent One"}),
            ("agent2.py", {"uuid": "test_456", "name": "Agent Two"}),
        ]
        mock_pm.list_agents.return_value = mock_agents
        mock_prompt.return_value = "1"  # User selects first agent

        with mock.patch(
            "snowglobe.client.src.cli.test_agent_wrapper"
        ) as mock_test_wrapper:
            mock_test_wrapper.return_value = (True, "Connected")

            cli.test(filename=None)

            mock_prompt.assert_called_once()
            mock_test_wrapper.assert_called_once_with(
                "agent1.py", "test_123", "Agent One"
            )

        # Test Case 5: Specific filename provided - valid
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_pm.get_agent_by_filename.return_value = {
            "uuid": "test_789",
            "name": "Specific Agent",
        }

        with mock.patch(
            "snowglobe.client.src.cli.test_agent_wrapper"
        ) as mock_test_wrapper:
            mock_test_wrapper.return_value = (True, "Connected")

            cli.test("specific_agent.py")

            mock_pm.get_agent_by_filename.assert_called_once_with("specific_agent.py")
            mock_test_wrapper.assert_called_once_with(
                "specific_agent.py", "test_789", "Specific Agent"
            )

        # Test Case 6: Specific filename provided - invalid
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_pm.get_agent_by_filename.return_value = None
        mock_pm.list_agents.return_value = [
            ("other_agent.py", {"uuid": "test_999", "name": "Other Agent"})
        ]

        with self.assertRaises(typer.Exit) as cm:
            cli.test("nonexistent_agent.py")
        self.assertEqual(cm.exception.exit_code, 1)
        mock_pm.get_agent_by_filename.assert_called_once_with("nonexistent_agent.py")

        # Test Case 7: Invalid user selection (multiple agents)
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_pm.list_agents.return_value = mock_agents
        mock_prompt.side_effect = ValueError(
            "Invalid input"
        )  # User enters invalid input

        with self.assertRaises(typer.Exit) as cm:
            cli.test(filename=None)
        self.assertEqual(cm.exception.exit_code, 1)

        # Test Case 8: Agent wrapper test fails
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_pm.list_agents.return_value = mock_agents[:1]  # Single agent

        with mock.patch(
            "snowglobe.client.src.cli.test_agent_wrapper"
        ) as mock_test_wrapper:
            mock_test_wrapper.return_value = (
                False,
                "Missing process_scenario function",
            )

            with self.assertRaises(typer.Exit) as cm:
                cli.test(filename=None)
            self.assertEqual(cm.exception.exit_code, 1)

        # Test Case 9: Default template response warning
        mock_pm.reset_mock()
        mock_pm.validate_project.return_value = (True, [])
        mock_pm.list_agents.return_value = mock_agents[:1]

        with mock.patch(
            "snowglobe.client.src.cli.test_agent_wrapper"
        ) as mock_test_wrapper:
            mock_test_wrapper.return_value = (False, "Using default template response")

            with self.assertRaises(typer.Exit) as cm:
                cli.test(filename=None)
            self.assertEqual(cm.exception.exit_code, 1)

    def test_test_agent_wrapper_function(self):
        """Test the test_agent_wrapper helper function in various scenarios."""

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test Case 15: Missing Python file
            result, message = cli.test_agent_wrapper(
                "nonexistent.py", "test_123", "Test App"
            )
            self.assertFalse(result)
            self.assertIn("File not found", message)

            # Test Case 16: Invalid Python syntax
            invalid_file = os.path.join(tmpdir, "invalid.py")
            with open(invalid_file, "w") as f:
                f.write("def invalid_syntax(\n")  # Incomplete function

            with mock.patch("os.getcwd", return_value=tmpdir):
                result, message = cli.test_agent_wrapper(
                    "invalid.py", "test_123", "Test App"
                )
                self.assertFalse(result)
                # Should fail during module loading

            # Test Case 17: Missing process_scenario function
            no_func_file = os.path.join(tmpdir, "no_func.py")
            with open(no_func_file, "w") as f:
                f.write("# Valid Python but no process_scenario function\npass\n")

            with mock.patch("os.getcwd", return_value=tmpdir):
                result, message = cli.test_agent_wrapper(
                    "no_func.py", "test_123", "Test App"
                )
                self.assertFalse(result)
                self.assertIn("process_scenario function not found", message)

            # Test Case 18: Non-callable process_scenario
            non_callable_file = os.path.join(tmpdir, "non_callable.py")
            with open(non_callable_file, "w") as f:
                f.write("process_scenario = 'not a function'\n")

            with mock.patch("os.getcwd", return_value=tmpdir):
                result, message = cli.test_agent_wrapper(
                    "non_callable.py", "test_123", "Test App"
                )
                self.assertFalse(result)
                self.assertIn("process_scenario is not callable", message)

            # Test Case 19: Valid agent with default template response
            template_file = os.path.join(tmpdir, "template.py")
            with open(template_file, "w") as f:
                f.write(
                    """
from snowglobe.client import CompletionRequest, CompletionFunctionOutputs

def process_scenario(request):
    return CompletionFunctionOutputs(response="Your response here")
"""
                )

            with mock.patch("os.getcwd", return_value=tmpdir):
                result, message = cli.test_agent_wrapper(
                    "template.py", "test_123", "Test App"
                )
                self.assertFalse(result)
                self.assertIn("Using default template response", message)

    @mock.patch("signal.signal")  # Mock signal handling
    @mock.patch("time.sleep")  # Skip actual sleep delays
    @mock.patch(
        "snowglobe.client.src.cli_utils.console.status"
    )  # Mock Rich console status
    @mock.patch(
        "snowglobe.client.src.cli.check_auth_status"
    )  # Mock authentication check
    @mock.patch("snowglobe.client.src.app.start_client")  # Mock the actual server start
    def test_start(
        self, mock_start_client, mock_check_auth, mock_status, mock_sleep, mock_signal
    ):
        """Test that snowglobe-connect start works correctly in various scenarios."""

        # Configure status mock to be a simple context manager
        mock_status.return_value.__enter__ = mock.Mock()
        mock_status.return_value.__exit__ = mock.Mock(return_value=None)

        # Test Case 1: Valid authentication - should start server
        mock_check_auth.return_value = (True, "Authenticated", {})

        with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "test_api_key"}):
            cli.start(verbose=False)

            mock_check_auth.assert_called_once()
            mock_start_client.assert_called_once_with(verbose=False)
            mock_signal.assert_called_once()  # Signal handler should be set up

        # Test Case 2: No API key - should fail with helpful message
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_check_auth.return_value = (False, "No API key found", {})

        with self.assertRaises(typer.Exit) as cm:
            cli.start(verbose=False)
        self.assertEqual(cm.exception.exit_code, 1)
        mock_check_auth.assert_called_once()
        mock_start_client.assert_not_called()

        # Test Case 3: Invalid API key - should fail authentication
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_check_auth.return_value = (False, "Authentication failed: 401", {})

        with self.assertRaises(typer.Exit) as cm:
            cli.start(verbose=False)
        self.assertEqual(cm.exception.exit_code, 1)
        mock_check_auth.assert_called_once()
        mock_start_client.assert_not_called()

        # Test Case 4: Auth check network error - should handle gracefully
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_check_auth.return_value = (
            False,
            "Connection error: Network unreachable",
            {},
        )

        with self.assertRaises(typer.Exit) as cm:
            cli.start(verbose=False)
        self.assertEqual(cm.exception.exit_code, 1)

        # Test Case 5: Successful startup with verbose mode
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_check_auth.return_value = (True, "Authenticated", {})

        with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "test_api_key"}):
            cli.start(verbose=True)

            mock_check_auth.assert_called_once()
            mock_start_client.assert_called_once_with(verbose=True)

        # Test Case 7: Config validation errors - API key missing during server start
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_check_auth.return_value = (True, "Authenticated", {})
        mock_start_client.side_effect = ValueError(
            "API key is required either passed as an argument"
        )

        with self.assertRaises(typer.Exit) as cm:
            cli.start(verbose=False)
        self.assertEqual(cm.exception.exit_code, 1)
        mock_start_client.assert_called_once()

        # Test Case 8: Other ValueError during startup - should re-raise
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_check_auth.return_value = (True, "Authenticated", {})
        mock_start_client.side_effect = ValueError("Some other config error")

        with self.assertRaises(ValueError):
            cli.start(verbose=False)

        # Test Case 9: Verbose disabled - should show clean UI
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_start_client.side_effect = None  # Clear any previous side effects
        mock_check_auth.return_value = (True, "Authenticated", {})

        with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "test_api_key"}):
            cli.start(verbose=False)

            mock_start_client.assert_called_once_with(verbose=False)

        # Test Case 10: Verbose enabled - should show detailed logs
        mock_check_auth.reset_mock()
        mock_start_client.reset_mock()
        mock_start_client.side_effect = None  # Clear any previous side effects
        mock_check_auth.return_value = (True, "Authenticated", {})

        with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "test_api_key"}):
            cli.start(verbose=True)

            mock_start_client.assert_called_once_with(verbose=True)

    @mock.patch(
        "snowglobe.client.src.cli.graceful_shutdown"
    )  # Mock graceful shutdown in cli module
    def test_start_signal_handling(self, mock_graceful_shutdown):
        """Test signal handling during start command."""

        # Test Case 11: Graceful shutdown on signal
        with mock.patch("signal.signal") as mock_signal:
            with mock.patch("snowglobe.client.src.cli.check_auth_status") as mock_auth:
                with mock.patch("snowglobe.client.src.app.start_client"):
                    with mock.patch(
                        "snowglobe.client.src.cli_utils.console.status"
                    ) as mock_status:
                        mock_status.return_value.__enter__ = mock.Mock()
                        mock_status.return_value.__exit__ = mock.Mock(return_value=None)
                        mock_auth.return_value = (True, "Authenticated", {})

                        cli.start(verbose=False)

                        # Verify signal handler was registered
                        mock_signal.assert_called_once()
                        signal_call_args = mock_signal.call_args
                        self.assertEqual(
                            signal_call_args[0][0], signal.SIGINT
                        )  # Should handle SIGINT

                        # Test the signal handler function
                        signal_handler = signal_call_args[0][1]
                        signal_handler(signal.SIGINT, None)
                        mock_graceful_shutdown.assert_called_once()

    @mock.patch("snowglobe.client.src.cli_utils.get_shutdown_stats")
    @mock.patch("snowglobe.client.src.cli_utils.console")
    def test_graceful_shutdown_statistics(self, mock_console, mock_get_stats):
        """Test shutdown statistics display."""

        # Test Case 12: Shutdown with session statistics
        mock_stats = {
            "total_messages": 25,
            "uptime": "5m 32s",
            "experiment_totals": {"Test Experiment": 15, "Demo Experiment": 10},
        }
        mock_get_stats.return_value = mock_stats

        with mock.patch("sys.exit") as mock_exit:
            from snowglobe.client.src.cli_utils import graceful_shutdown

            graceful_shutdown(2, {})

            mock_get_stats.assert_called_once()
            mock_exit.assert_called_once_with(0)

        # Test Case 13: Shutdown with no statistics
        mock_get_stats.reset_mock()
        mock_get_stats.return_value = {
            "total_messages": 0,
            "uptime": "0s",
            "experiment_totals": {},
        }

        with mock.patch("sys.exit") as mock_exit:
            graceful_shutdown(2, {})

            mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
