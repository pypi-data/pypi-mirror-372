import asyncio
import contextlib
import math
import os
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .config import get_rc_file_path
from .stats import get_shutdown_stats

console = Console()


class CliState:
    """Global CLI state management"""

    def __init__(self):
        self.verbose = False
        self.quiet = False
        self.json_output = False


class ShutdownManager:
    """Coordinate graceful shutdown between signal handler and background jobs"""

    def __init__(self):
        self.shutdown_event = threading.Event()  # For sync code
        self.async_shutdown_event = None  # Created when event loop available
        self.force_shutdown = False
        self.shutdown_initiated = False
        self.active_jobs = set()  # Track active background jobs
        self.active_jobs_lock = threading.Lock()

    def register_active_job(self, job_id: str):
        """Register a job as actively running"""
        with self.active_jobs_lock:
            self.active_jobs.add(job_id)

    def unregister_active_job(self, job_id: str):
        """Unregister a job when it completes"""
        with self.active_jobs_lock:
            self.active_jobs.discard(job_id)

    def has_active_jobs(self) -> bool:
        """Check if there are any active jobs running"""
        with self.active_jobs_lock:
            return len(self.active_jobs) > 0

    def initiate_shutdown(self) -> bool:
        """Initiate shutdown. Returns True if this is a force shutdown (second Ctrl+C)"""
        if self.shutdown_initiated:
            # Second Ctrl+C - force shutdown
            self.force_shutdown = True
            return True
        else:
            # First Ctrl+C - start graceful shutdown
            self.shutdown_initiated = True
            self.shutdown_event.set()

            # Set async event if event loop exists
            try:
                loop = asyncio.get_running_loop()
                if self.async_shutdown_event is None:
                    self.async_shutdown_event = asyncio.Event()
                loop.call_soon_threadsafe(self.async_shutdown_event.set)
            except RuntimeError:
                pass

            return False

    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested"""
        return self.shutdown_event.is_set()

    async def is_async_shutdown_requested(self) -> bool:
        """Async version of shutdown check"""
        if self.async_shutdown_event is None:
            return self.shutdown_event.is_set()
        return self.async_shutdown_event.is_set() or self.shutdown_event.is_set()


cli_state = CliState()
shutdown_manager = ShutdownManager()


def get_api_key() -> Optional[str]:
    """Get API key from environment or config file"""
    api_key = os.getenv("SNOWGLOBE_API_KEY") or os.getenv("GUARDRAILS_API_KEY")
    if not api_key:
        rc_path = get_rc_file_path()
        if os.path.exists(rc_path):
            with open(rc_path, "r") as rc_file:
                for line in rc_file:
                    if line.startswith("SNOWGLOBE_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break
    return api_key


def get_control_plane_url() -> str:
    """Get control plane URL from environment or config file"""
    control_plane_url = os.getenv("CONTROL_PLANE_URL")
    if not control_plane_url:
        control_plane_url = "https://api.snowglobe.guardrailsai.com"
        rc_path = get_rc_file_path()
        if os.path.exists(rc_path):
            with open(rc_path, "r") as rc_file:
                for line in rc_file:
                    if line.startswith("CONTROL_PLANE_URL="):
                        control_plane_url = line.strip().split("=", 1)[1]
                        break
    return control_plane_url


def success(message: str) -> None:
    """Print success message with formatting"""
    if cli_state.json_output:
        return
    if not cli_state.quiet:
        console.print(f"✅ {message}", style="green")


def warning(message: str) -> None:
    """Print warning message with formatting"""
    if cli_state.json_output:
        return
    if not cli_state.quiet:
        console.print(f"⚠️  {message}", style="yellow")


def error(message: str) -> None:
    """Print error message with formatting"""
    if cli_state.json_output:
        return
    console.print(f"❌ {message}", style="red")


def info(message: str) -> None:
    """Print info message with formatting"""
    if cli_state.json_output:
        return
    if not cli_state.quiet:
        console.print(f"💡 {message}", style="blue")


def debug(message: str) -> None:
    """Print debug message if verbose mode is enabled"""
    if cli_state.json_output:
        return
    if cli_state.verbose:
        console.print(f"🔍 {message}", style="dim")


def docs_link(message: str, url: str = "https://www.snowglobe.so/docs") -> None:
    """Print documentation link"""
    if cli_state.json_output:
        return
    if not cli_state.quiet:
        console.print(f"📖 {message}: {url}", style="cyan")


def show_session_summary():
    """Display session summary statistics"""
    stats = get_shutdown_stats()

    if stats and stats["total_messages"] > 0:
        success("Session summary:")
        if len(stats["experiment_totals"]) > 1:
            # Multiple experiments - show breakdown
            for exp_name, count in stats["experiment_totals"].items():
                console.print(f"   • {exp_name}: {count} scenarios processed")
            console.print(
                f"   • Total: {stats['total_messages']} scenarios in {stats['uptime']}"
            )
        else:
            # Single experiment or total only
            console.print(
                f"   • {stats['total_messages']} scenarios processed in {stats['uptime']}"
            )
    else:
        success("No scenarios processed during this session")


def begin_graceful_shutdown():
    """Coordinate graceful shutdown - runs in background thread"""
    TIMEOUT_SECONDS = 8

    console.print("\n")
    warning("🛑 Shutting down gracefully...")
    success("Completing current scenarios")

    # Wait for active jobs to finish (with timeout)
    start_time = time.time()
    while time.time() - start_time < TIMEOUT_SECONDS:
        if not shutdown_manager.has_active_jobs():
            break
        time.sleep(0.1)

        # Check if user pressed Ctrl+C again (force quit)
        if shutdown_manager.force_shutdown:
            return  # Signal handler will handle force quit

    # Jobs finished or timeout reached
    elapsed = time.time() - start_time
    if elapsed >= TIMEOUT_SECONDS:
        warning(
            f"Shutdown timeout reached after {TIMEOUT_SECONDS}s, completing shutdown..."
        )

    success("Connection closed")

    # Show session summary
    show_session_summary()

    console.print()
    success("Agent disconnected successfully")

    # Exit cleanly
    sys.exit(0)


def smart_signal_handler(sig, frame):
    """Smart two-stage signal handler with immediate exit when possible"""
    force_quit = shutdown_manager.initiate_shutdown()

    if force_quit:
        # Second Ctrl+C - force quit immediately
        console.print("\n[bold red]🚨 Force shutdown![/bold red]")
        sys.exit(1)
    else:
        # First Ctrl+C - check if we have active work
        if shutdown_manager.has_active_jobs():
            # Have active jobs - start graceful shutdown with user feedback
            console.print(
                "\n[bold yellow]🛑 Graceful shutdown initiated...[/bold yellow]"
            )
            console.print("[dim]Press Ctrl+C again to force quit[/dim]")

            # Start graceful shutdown in background thread
            threading.Thread(target=begin_graceful_shutdown, daemon=True).start()
        else:
            # No active jobs - shutdown immediately
            console.print("\n[bold blue]🛑 Shutting down...[/bold blue]")

            # Show session summary and exit
            show_session_summary()
            console.print()
            success("Agent disconnected successfully")
            sys.exit(0)


def graceful_shutdown(_sig_num, _frame):
    """Handle graceful shutdown with session summary (idempotent, always exits 0).

    This legacy entrypoint avoids toggling internal shutdown state so repeated
    calls behave consistently in tests and scripts.
    """
    # If there are active jobs, allow them a moment to finish similar to begin_graceful_shutdown,
    # but without changing the shutdown state in a way that triggers force-exit on reentry.
    if shutdown_manager.has_active_jobs():
        console.print("\n[bold yellow]🛑 Graceful shutdown initiated...[/bold yellow]")
        console.print("[dim]Press Ctrl+C again to force quit[/dim]")

    if cli_state.verbose:
        console.print(f"signal received: {_sig_num}, frame: {_frame}")

    # Show session summary and exit cleanly
    console.print("\n[bold blue]🛑 Shutting down...[/bold blue]")
    show_session_summary()
    console.print()
    success("Agent disconnected successfully")
    sys.exit(0)


@contextlib.contextmanager
def spinner(text: str):
    """Context manager for showing a spinner during operations"""
    if cli_state.json_output or cli_state.quiet:
        yield
        return

    with console.status(f"[bold blue]{text}..."):
        yield


def check_auth_status() -> Tuple[bool, str, Dict[str, Any]]:
    """Check authentication status"""
    api_key = get_api_key()
    if not api_key:
        return False, "No API key found", {}

    control_plane_url = get_control_plane_url()
    try:
        response = requests.get(
            f"{control_plane_url}/api/applications",
            headers={"x-api-key": api_key},
            timeout=10,
        )
        if response.status_code == 200:
            return True, "Authenticated", response.json()
        else:
            return False, f"Authentication failed: {response.status_code}", {}
    except requests.RequestException as e:
        return False, f"Connection error: {str(e)}", {}


def select_stateful_interactive(
    stateful: bool = False,
) -> bool:
    """Interactive prompt to confirm if the agent is stateful"""
    if cli_state.json_output:
        # For JSON mode, just return the default stateful value
        return stateful
    info(
        "Some stateful agents such as ones that maintain communication over a websocket or convo specific completion endpoint require stateful integration."
    )
    info(
        "If your agent takes messages and completions on a single completion endpoint regardless of context, you can answer no to the following question."
    )
    if Confirm.ask("Would you like to initialize a stateful application?"):
        return True
    return False


def select_application_interactive(
    applications: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Clean, readable application selection interface"""
    if cli_state.json_output:
        # For JSON mode, just return the first app or None
        return applications[0] if applications else None

    if not applications:
        info("No applications found")
        if Confirm.ask("Would you like to create a new application?"):
            return "new"
        return None

    # Sort applications by updated_at (most recent first)
    sorted_applications = sort_applications_by_date(applications)

    return display_applications_clean(sorted_applications)


def sort_applications_by_date(
    applications: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Sort applications by updated_at date, most recent first"""

    def get_sort_key(app):
        updated_at = app.get("updated_at", "")
        if not updated_at:
            return ""  # Apps without dates go to the end
        return updated_at

    # Sort in reverse order (most recent first)
    return sorted(applications, key=get_sort_key, reverse=True)


def display_applications_clean(
    applications: List[Dict[str, Any]], page_size: int = 15
) -> Optional[Dict[str, Any]]:
    """Display applications in a clean table format"""
    total_apps = len(applications)
    total_pages = math.ceil(total_apps / page_size) if total_apps > 0 else 1
    current_page = 0

    # Check if any apps have updated_at date information
    has_dates = any(app.get("updated_at") for app in applications)

    while True:
        # Calculate page boundaries
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total_apps)
        page_apps = applications[start_idx:end_idx]

        # Create table
        table = Table(title=f"📱 Your Applications ({total_apps} total)")
        if total_pages > 1:
            table.title = f"📱 Your Applications ({total_apps} total) - Page {current_page + 1}/{total_pages}"

        table.add_column("#", style="bold blue", width=4)
        table.add_column("Name", style="bold", min_width=15)

        # Add date column if date info is available
        if has_dates:
            table.add_column("Updated", style="dim", min_width=10)

        table.add_column("Description", style="green", min_width=20)

        # Add applications to table
        for i, app in enumerate(page_apps):
            app_idx = start_idx + i + 1
            name = app.get("name", "Unknown")
            description = app.get("description", "No description")

            # Clean up description - remove newlines and extra spaces
            description = " ".join(description.split())

            # Truncate description to 20 characters
            if len(description) > 20:
                description = description[:17] + "..."

            # Get the best available date
            date_str = "-"
            if has_dates:
                date_str = get_best_date(app)

            # Build row based on whether we have dates
            if has_dates:
                table.add_row(str(app_idx), name, date_str, description)
            else:
                table.add_row(str(app_idx), name, description)

        # Add create new option
        if has_dates:
            table.add_row("new", "🆕 Create New App", "-", "Set up new application")
        else:
            table.add_row("new", "🆕 Create New App", "Set up new application")

        console.print(table)

        # Navigation instructions
        nav_options = []
        if current_page > 0:
            nav_options.append("[bold cyan]p[/bold cyan] Previous")
        if current_page < total_pages - 1:
            nav_options.append("[bold cyan]n[/bold cyan] Next")
        nav_options.extend(
            [
                f"[bold yellow]1-{total_apps}[/bold yellow] Select app",
                "[bold green]new[/bold green] Create new",
                "[bold red]q[/bold red] Quit",
            ]
        )

        console.print("\nOptions: " + " | ".join(nav_options))

        # Get user input
        try:
            choice = Prompt.ask("\n[bold]Your choice[/bold]").strip().lower()

            if choice == "q":
                return None
            elif choice == "p" and current_page > 0:
                current_page -= 1
                continue
            elif choice == "n" and current_page < total_pages - 1:
                current_page += 1
                continue
            elif choice == "new":
                return "new"
            elif choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= total_apps:
                    return applications[idx - 1]
                else:
                    error(f"Please choose between 1 and {total_apps}")
                    time.sleep(1)
            else:
                error("Invalid choice. Try again.")
                time.sleep(1)

        except (KeyboardInterrupt, EOFError):
            warning("\nSelection cancelled")
            return None


def get_best_date(app: Dict[str, Any]) -> str:
    """Get updated_at date formatted for display"""
    date_value = app.get("updated_at")

    if not date_value:
        return "-"

    # Format ISO date like "2025-07-29T04:35:22.093Z" to "2025-07-29"
    date_str = str(date_value)
    if "T" in date_str:
        return date_str.split("T")[0]  # Take just the date part
    elif len(date_str) > 10:
        return date_str[:10]
    return date_str


def get_remote_applications() -> Tuple[bool, List[Dict[str, Any]], str]:
    """Fetch applications from the remote API"""
    api_key = get_api_key()
    if not api_key:
        return False, [], "No API key found"

    control_plane_url = get_control_plane_url()
    try:
        response = requests.get(
            f"{control_plane_url}/api/applications",
            headers={"x-api-key": api_key},
            timeout=10,
        )
        if response.status_code == 200:
            return True, response.json(), "Success"
        else:
            return False, [], f"HTTP {response.status_code}: {response.text}"
    except requests.RequestException as e:
        return False, [], f"Connection error: {str(e)}"
