import asyncio
import hashlib
import importlib.util
import os
import signal
import sys
import threading
import time
import webbrowser
from importlib.metadata import version
from typing import Optional, Tuple

import typer
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import start_client lazily inside the start command to avoid config initialization
from .cli_utils import (
    check_auth_status,
    cli_state,
    console,
    debug,
    docs_link,
    error,
    get_api_key,
    get_remote_applications,
    graceful_shutdown,
    info,
    select_application_interactive,
    select_stateful_interactive,
    spinner,
    success,
    warning,
)
from .config import get_rc_file_path
from .models import CompletionRequest, SnowglobeData, SnowglobeMessage
from .project_manager import get_project_manager

CONTROL_PLANE_URL = os.environ.get(
    "CONTROL_PLANE_URL", "https://api.snowglobe.guardrailsai.com"
)

UI_URL = os.environ.get("UI_URL", "https://snowglobe.so/app")

SNOWGLOBE_AUTH_CONFIGURE_PORT = int(
    os.environ.get("SNOWGLOBE_AUTH_CONFIGURE_PORT", 9001)
)


cli_app = typer.Typer(
    help="❄️  Snowglobe CLI - Connect your applications to Snowglobe experiments",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)


def setup_global_options(
    ctx: typer.Context,
    verbose: bool = False,
    quiet: bool = False,
    json_output: bool = False,
):
    """Setup global CLI options"""
    cli_state.verbose = verbose
    cli_state.quiet = quiet
    cli_state.json_output = json_output


@cli_app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimize output"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    version_flag: bool = typer.Option(
        False, "--version", help="Show version and exit", is_flag=True
    ),
):
    """
    ❄️  Snowglobe CLI - Connect your applications to Snowglobe experiments
    """
    if version_flag:
        try:
            pkg_version = version("snowglobe-connect")
            typer.echo(f"snowglobe-connect {pkg_version}")
        except Exception:
            typer.echo("snowglobe-connect (version unknown)")
        raise typer.Exit()

    # Show help if no command provided and no version flag
    if not ctx.invoked_subcommand and not version_flag:
        typer.echo(ctx.get_help())
        raise typer.Exit()

    setup_global_options(ctx, verbose, quiet, json_output)


# check if there is an override control plane URL in config file
rc_path = get_rc_file_path()

if os.path.exists(rc_path):
    with open(rc_path, "r") as rc_file:
        for line in rc_file:
            if line.startswith("CONTROL_PLANE_URL="):
                CONTROL_PLANE_URL = line.strip().split("=", 1)[1]
                break


@cli_app.command()
def test(
    filename: Optional[str] = typer.Argument(
        None, help="Agent filename to test (if not provided, will prompt for selection)"
    ),
):
    """
    Test an agent wrapper implementation
    """
    console.print("\n[bold blue]🧪 Test Agent Wrapper[/bold blue]\n")

    # Initialize project manager
    pm = get_project_manager()

    # Check if project is set up
    is_valid, issues = pm.validate_project()
    if not is_valid:
        error("Project validation failed:")
        for issue in issues:
            console.print(f"  - {issue}")
        info("Run 'snowglobe-connect init' to set up a project first")
        raise typer.Exit(1)

    # If no filename provided, list available agents
    if not filename:
        agents = pm.list_agents()
        if not agents:
            error("No agents found in this project")
            info("Run 'snowglobe-connect init' to create an agent first")
            raise typer.Exit(1)

        if len(agents) == 1:
            filename, agent_info = agents[0]
            info(f"Testing the only available agent: {filename}")
        else:
            # Multiple agents - let user choose
            console.print("Available agents:")
            for i, (fname, agent_info) in enumerate(agents, 1):
                console.print(f"  {i}. {fname} ({agent_info.get('name', 'Unknown')})")

            try:
                choice = typer.prompt("Select agent to test (number)")
                idx = int(choice) - 1
                if 0 <= idx < len(agents):
                    filename, agent_info = agents[idx]
                else:
                    error("Invalid selection")
                    raise typer.Exit(1)
            except (ValueError, KeyboardInterrupt):
                error("Invalid selection or cancelled")
                raise typer.Exit(1)
    else:
        # Validate provided filename
        agent_info = pm.get_agent_by_filename(filename)
        if not agent_info:
            error(f"Agent not found: {filename}")
            info("Available agents:")
            for fname, agent_info in pm.list_agents():
                console.print(f"  - {fname}")
            raise typer.Exit(1)

    # Get agent info
    app_id = agent_info.get("uuid")
    app_name = agent_info.get("name", "Unknown")

    console.print(f"Testing: [bold]{filename}[/bold] ({app_name})")

    # Run the test
    with spinner("Testing agent wrapper"):
        is_connected, conn_message = test_agent_wrapper(filename, app_id, app_name)

    if is_connected:
        success(f"Test passed: {conn_message}")
        info("Your agent wrapper is working correctly!")
        console.print()
        info("Next steps:")
        console.print("Start the client:")
        console.print("   [bold green]snowglobe-connect start[/bold green]")
    else:
        error(f"Test failed: {conn_message}")
        if "default template response" in conn_message.lower():
            info("This is expected with the default template.")
            info(
                "Please implement your application logic in the process_scenario function."
            )
        else:
            info("Check your implementation and try again.")
            docs_link(
                "Troubleshooting guide", "https://docs.snowglobe.so/troubleshooting"
            )
        raise typer.Exit(1)


@cli_app.command()
def init(
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path or filename (within project) for the agent wrapper",
    ),
    # option for stateful agent
    stateful: bool = typer.Option(
        False, "--stateful", help="Initialize a stateful agent template"
    ),
):
    """
    Initialize a new Snowglobe agent in the current directory
    """
    console.print("\n[bold blue]🚀 Initialize Snowglobe Agent[/bold blue]\n")

    # Initialize project manager
    pm = get_project_manager()

    # Check authentication first
    with spinner("Checking authentication"):
        is_auth, auth_message, _ = check_auth_status()

    if not is_auth:
        error("Authentication required to initialize agents")
        info("Please run 'snowglobe-connect auth' first to set up authentication")
        docs_link("Setup guide", "https://docs.snowglobe.so/setup")
        raise typer.Exit(1)

    success("Authenticated successfully")

    # Fetch available applications
    with spinner("Fetching your applications"):
        success_fetch, applications, fetch_message = get_remote_applications()

    if not success_fetch:
        error(f"Failed to fetch applications: {fetch_message}")
        if "401" in fetch_message or "authentication" in fetch_message.lower():
            info(
                "Your API key may have expired. Run 'snowglobe-connect auth' to re-authenticate"
            )
        raise typer.Exit(1)

    # Interactive application selection
    selected = select_application_interactive(applications)

    if selected is None:
        warning("No application selected. Exiting.")
        raise typer.Exit(0)
    elif selected == "new":
        info("Creating new application not yet implemented in init command")
        info(
            "Please visit https://snowglobe.guardrails-ai.com/applications/create to create a new app"
        )
        info("Then run this command again to select it")
        raise typer.Exit(0)

    # Selected is an existing application
    app_id = selected["id"]
    app_name = selected["name"]

    success(f"Selected application: {app_name}")

    # prompt user to confirm if stateful agent
    user_stateful = select_stateful_interactive(stateful)
    # Set up project structure
    with spinner("Setting up project structure"):
        pm.ensure_project_structure()

    # Determine filename
    if file:
        # User provided explicit file path or name
        from pathlib import Path

        provided_path = Path(os.path.expanduser(file))

        # Ensure .py suffix
        if provided_path.suffix != ".py":
            provided_path = provided_path.with_suffix(".py")

        # Normalize to a path within the project root
        if provided_path.is_absolute():
            try:
                relative_path = provided_path.relative_to(pm.project_root)
            except ValueError:
                error("--file must be within the current project directory")
                info(f"Project root: {pm.project_root}")
                raise typer.Exit(1)
        else:
            relative_path = provided_path

        # Store mapping as a POSIX-style relative path string
        filename = relative_path.as_posix()
    else:
        # Generate from app name
        filename = pm.sanitize_filename(app_name)

    # If filename was auto-generated from app name, find an available one
    if not file:
        filename = pm.find_available_filename(filename)

    file_path = pm.project_root / filename

    success(f"Using filename: {filename}")
    # use the appopriate template based on stateful option
    if user_stateful:
        snowglobe_connect_template = stateful_snowglobe_connect_template
    else:
        snowglobe_connect_template = stateless_snowglobe_connect_template

    # Ensure parent directories exist if a subpath was provided
    os.makedirs(file_path.parent, exist_ok=True)

    # Create agent wrapper file
    with spinner("Creating agent wrapper"):
        with open(file_path, "w") as f:
            f.write(snowglobe_connect_template)
    success(f"Created agent wrapper: {filename}")

    # Add to mapping
    pm.add_agent_mapping(filename, app_id, app_name)
    success("Added mapping to .snowglobe/agents.json")

    console.print("\n[dim]Project structure:[/dim]")
    console.print("[dim]  .snowglobe/agents.json\t- UUID mappings[/dim]")
    console.print(f"[dim]  {filename}\t- Your agent wrapper[/dim]")

    console.print()
    info("Next steps:")
    console.print("1. Edit the process_scenario function in your agent file:")
    console.print(f"   [bold cyan]{filename}[/bold cyan]")
    console.print("2. Implement your application logic")
    console.print("3. Test your agent:")
    console.print("   [bold green]snowglobe-connect test[/bold green]")
    console.print("4. Start the client:")
    console.print("   [bold green]snowglobe-connect start[/bold green]")

    console.print()
    success(f"Agent '{app_name}' initialized successfully! 🎉")


def test_agent_wrapper(filename: str, app_id: str, app_name: str) -> Tuple[bool, str]:
    """Test if an agent wrapper is working"""
    try:
        file_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(file_path):
            return False, f"File not found: {filename}"

        spec = importlib.util.spec_from_file_location("agent_wrapper", file_path)
        agent_module = importlib.util.module_from_spec(spec)

        # Add current directory to path
        sys_path_backup = sys.path.copy()
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        try:
            spec.loader.exec_module(agent_module)
        finally:
            sys.path = sys_path_backup

        if not hasattr(agent_module, "process_scenario"):
            return False, "process_scenario function not found"

        process_scenario = agent_module.process_scenario
        if not callable(process_scenario):
            return False, "process_scenario is not callable"

        # Test with a simple request

        test_request = CompletionRequest(
            messages=[
                SnowglobeMessage(
                    role="user",
                    content="Test connection",
                    snowglobe_data=SnowglobeData(
                        conversation_id="test", test_id="test"
                    ),
                )
            ]
        )

        if asyncio.iscoroutinefunction(process_scenario):
            response = asyncio.run(process_scenario(test_request))
        else:
            response = process_scenario(test_request)

        if hasattr(response, "response") and isinstance(response.response, str):
            if response.response == "Your response here":
                return False, "Using default template response"
            return True, "Connected"
        else:
            return False, "Invalid response format"

    except Exception as e:
        return False, f"Error: {str(e)}"


def status_code_to_actions(status_code: int) -> str:
    """
    Convert a status code to a string describing the action to take.
    """
    if status_code == 200:
        return "200 - Success"
    elif status_code == 400:
        return "400 - Bad Request - Check your input parameters"
    elif status_code == 401:
        return "401 - Unauthorized - Check your SNOWGLOBE_API_KEY in .snowglobe/config.rc or environment variables"
    elif status_code == 403:
        return "403 - Forbidden - You do not have permission to access this resource"
    elif status_code == 404:
        return (
            "404 - Not Found - The requested resource does not exist. Was it deleted?"
        )
    elif status_code == 500:
        return "500 - Internal Server Error - Try again later or contact support"
    else:
        return f"Unexpected Status Code: {status_code} Please try again later or contact support"


def enhanced_error_handler(status_code: int, operation: str = "operation") -> None:
    """Enhanced error handling with contextual help"""
    if status_code == 401:
        error("Authentication failed")
        info("Your API key may be invalid or expired")
        info("Run 'snowglobe-connect auth' to set up authentication")
        docs_link("Authentication help", "https://docs.snowglobe.so/auth")
    elif status_code == 403:
        error("Access forbidden")
        info("You don't have permission for this operation")
        info("Contact your administrator or check your account permissions")
    elif status_code == 404:
        error("Resource not found")
        info("The requested resource may have been deleted or moved")
        info("Verify the resource ID and try again")
    elif status_code == 429:
        error("Rate limit exceeded")
        info("Please wait a moment before trying again")
        info("Consider reducing the frequency of your requests")
    elif status_code >= 500:
        error(f"Server error during {operation}")
        info("This is likely a temporary issue")
        info("Please try again in a few minutes")
        docs_link("Status page", "https://status.snowglobe.so")
    else:
        error(f"Unexpected error during {operation}: {status_code}")
        info("Please try again or contact support if the issue persists")


stateless_snowglobe_connect_template = """from snowglobe.client import CompletionRequest, CompletionFunctionOutputs


def process_scenario(request: CompletionRequest) -> CompletionFunctionOutputs:
    \"\"\"
    Process a scenario request from Snowglobe.
    
    This function is called by the Snowglobe client to process requests. It should return a
    CompletionFunctionOutputs object with the response content.

    Example CompletionRequest:
    CompletionRequest(
        messages=[
            SnowglobeMessage(role="user", content="Hello, how are you?", snowglobe_data=None),
        ]
    )

    Example CompletionFunctionOutputs:
    CompletionFunctionOutputs(response="This is a string response from your application")
    
    Args:
        request (CompletionRequest): The request object containing the messages.

    Returns:
        CompletionFunctionOutputs: The response object with the generated content.
    \"\"\"

    # Process the request using the messages. Example:
    # messages = request.to_openai_messages()
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=messages
    # )
    return CompletionFunctionOutputs(response="Your response here")

"""

stateful_snowglobe_connect_template = """
# This file is auto-generated by the API client.

from snowglobe.client import CompletionRequest, CompletionFunctionOutputs
import logging
import websockets
import json
LOGGER = logging.getLogger(__name__)
socket_cache = {}
async def completion_fn(request: CompletionRequest) -> CompletionFunctionOutputs:
    # for debugging purposes
    # print(f"Received request: {request.messages}")
    
    completion_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # check the socket cache for a socket for this conversation_id
    conversation_id = request.messages[0].snowglobe_data.conversation_id
    if conversation_id in socket_cache:
        socket = socket_cache[conversation_id]
    else:
        # create a new socket connection 
        # this is talking to a local socket/stateful server that you implemented
        # update this or implement a way to connect to your actual server
        socket = await websockets.connect("ws://localhost:9000/ws")
        socket_cache[conversation_id] = socket
    
    # send the request to the socket
    await socket.send(json.dumps({
        "messages": completion_messages,
        "conversation_id": conversation_id
    }))

    # wait for the response from the socket
    response = await socket.recv()
    response_data = json.loads(response)

    # for debugging purposes
    # print(f"Received response from socket: {response_data}")
    
    # Example implementation, replace with actual logic
    return CompletionFunctionOutputs(response=response_data.messages[0]["content"])
"""


def _save_api_key_to_rc(api_key: str, rc_path: str) -> None:
    """Save API key to config file"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(rc_path), exist_ok=True)

    if os.path.exists(rc_path):
        # Update existing file
        with open(rc_path, "r") as f:
            lines = f.readlines()

        # Find and replace existing key or append new one
        updated = False
        for idx, line in enumerate(lines):
            if line.startswith("SNOWGLOBE_API_KEY="):
                lines[idx] = f"SNOWGLOBE_API_KEY={api_key}\n"
                updated = True
                break

        if not updated:
            lines.append(f"SNOWGLOBE_API_KEY={api_key}\n")

        with open(rc_path, "w") as f:
            f.writelines(lines)
    else:
        # Create new file
        with open(rc_path, "w") as f:
            f.write(f"SNOWGLOBE_API_KEY={api_key}\n")


def _create_auth_server(config_key: str, rc_path: str) -> FastAPI:
    """Create FastAPI server for OAuth callback"""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "message": "Welcome to the Snowglobe CLI Auth Server! Please run snowglobe-connect auth to set up your API key."
        }

    @app.post("/auth-configure")
    async def auth_configure(request: Request):
        try:
            # Verify authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or auth_header != f"Bearer {config_key}":
                return {
                    "error": "Unauthorized. Keys are only created and valid when snowglobe-connect auth is run."
                }, 401

            # Process API key
            body = await request.json()
            api_key = body.get("SNOWGLOBE_API_KEY")

            if api_key:
                info(f"Received API key: ...{api_key[-5:]}")
                info(f"Writing API key to {rc_path}")
                _save_api_key_to_rc(api_key, rc_path)

            return {"written": True}
        except Exception as e:
            error(f"Failed to process key configuration: {e}")
            return {"error": "Failed to process key configuration request"}

    return app


def _show_auth_success_next_steps() -> None:
    """Show helpful next steps after successful authentication"""
    console.print()
    info("Next steps:")
    console.print("1. Initialize an agent connection:")
    console.print("   [bold green]snowglobe-connect init[/bold green]")
    console.print("2. Test your agent:")
    console.print("   [bold green]snowglobe-connect test[/bold green]")
    console.print("3. Start the client:")
    console.print("   [bold green]snowglobe-connect start[/bold green]")
    console.print()
    docs_link("Getting started guide", "https://docs.snowglobe.so/getting-started")


def _poll_for_api_key(rc_path: str, timeout: int = 300) -> bool:
    """Poll for API key in config file"""
    start_time = os.times().elapsed

    with spinner("Waiting for API key configuration"):
        while True:
            time.sleep(0.5)

            # Check for API key
            if os.path.exists(rc_path):
                with open(rc_path, "r") as f:
                    for line in f:
                        if line.startswith("SNOWGLOBE_API_KEY="):
                            api_key = line.strip().split("=", 1)[1]
                            if api_key:
                                break
                    else:
                        continue
                    break

            # Check timeout
            if (os.times().elapsed - start_time) > timeout:
                break

    # Check if we found the API key
    api_key = get_api_key()
    if api_key:
        success(f"SNOWGLOBE_API_KEY configured in {rc_path}")
        _show_auth_success_next_steps()
        return True
    else:
        error("Authentication timed out")
        info("Please reach out to support or configure your API key manually")
        info("Set SNOWGLOBE_API_KEY= in your .snowglobe/config.rc file")
        return False


@cli_app.command()
def auth(
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip prompts and proceed with default options."
    ),
):
    """Authorize snowglobe client for test processing."""

    console.print("\n[bold blue]🔐 Authenticate with Snowglobe[/bold blue]\n")

    with spinner("Running preflight checks"):
        time.sleep(0.5)

    # Check if API key already exists
    api_key = get_api_key()
    rc_path = get_rc_file_path()

    if api_key:
        success(f"SNOWGLOBE_API_KEY found in {rc_path}")
        _show_auth_success_next_steps()
        return

    info("Starting authentication process...")

    # Start OAuth flow
    config_key = hashlib.sha256(os.urandom(32)).hexdigest()
    app = _create_auth_server(config_key, rc_path)

    # Start server in background
    def run_server():
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=SNOWGLOBE_AUTH_CONFIGURE_PORT,
            log_level="critical",
        )

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Show auth URL and poll for completion
    auth_url = f"{UI_URL}/keys/client-connect?port={SNOWGLOBE_AUTH_CONFIGURE_PORT}&token={config_key}"

    info("Opening authentication page in your browser...")
    try:
        webbrowser.open(auth_url)
        success("Browser opened successfully")
    except Exception as e:
        warning("Could not open browser automatically")
        debug(f"Browser error: {e}")

    # Show fallback link
    console.print()
    info("If the browser didn't open, visit this link:")
    console.print(f"   [link={auth_url}]{UI_URL}/auth[/link]")
    console.print()

    _poll_for_api_key(rc_path)


@cli_app.command()
def start(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed technical logs"
    ),
):
    """Start the Snowglobe client server to process requests."""

    # Clean startup sequence
    console.print("\n[bold blue]🔗 Connecting to Snowglobe...[/bold blue]\n")

    with spinner("Checking authentication"):
        is_auth, auth_message, _ = check_auth_status()

    if not is_auth:
        error("Authentication failed")
        info("Run 'snowglobe-connect auth' to set up authentication")
        raise typer.Exit(1)

    success("Authentication successful")

    with spinner("Loading agents"):
        time.sleep(0.5)  # Brief pause for UI

    console.print(
        "[bold green]🚀 Agent server is live! Processing scenarios...[/bold green]\n"
    )

    # Handle Ctrl+C gracefully (legacy handler delegates to smart shutdown internally)
    signal.signal(signal.SIGINT, graceful_shutdown)

    if not verbose:
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    # Show helpful links to open the application(s) in the Snowglobe UI
    try:
        pm = get_project_manager()
        agents = pm.list_agents()

        if agents:
            if len(agents) == 1:
                _, agent_info = agents[0]
                app_id = agent_info.get("uuid")
                app_name = agent_info.get("name", "Application")
                if app_id:
                    app_url = f"{UI_URL}/agents/{app_id}"
                    console.print(
                        "🔗 Agent connected! Go to your Snowglobe agent and kick off a simulation:"
                    )
                    console.print(f"   [link={app_url}]{app_name}[/link]\n")
            else:
                console.print(
                    "🔗 Agents connected! Go to your Snowglobe agents and kick off simulations:"
                )
                for _, agent_info in agents[:5]:
                    app_id = agent_info.get("uuid")
                    app_name = agent_info.get("name", "Application")
                    if app_id:
                        app_url = f"{UI_URL}/agents/{app_id}"
                        console.print(
                            f"   - {app_name}: [link={app_url}]{app_url}[/link]"
                        )
                if len(agents) > 5:
                    console.print("   (and more...)\n")
                else:
                    console.print()
    except Exception:
        # Do not block startup if we cannot load agents mapping
        pass

    # Import start_client here to avoid config initialization at module import time
    from .app import start_client

    # Call the existing start_client function with verbose flag
    try:
        start_client(verbose=verbose)
    except ValueError as e:
        # Handle config errors gracefully
        if "API key is required" in str(e):
            console.print()
            error("Authentication required")
            info("No API key found in environment or .snowglobe/config.rc file")
            console.print()
            info("Get started by running:")
            console.print("   [bold cyan]snowglobe-connect auth[/bold cyan]")
            raise typer.Exit(1)
        else:
            # Re-raise other ValueErrors
            raise
