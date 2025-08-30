import logging
import os

from rich.console import Console

LOGGER = logging.getLogger(__name__)
console = Console()


def get_rc_file_path() -> str:
    """Get path to snowglobe rc file"""
    return os.path.join(os.getcwd(), ".snowglobe", "config.rc")


def get_legacy_rc_file_path() -> str:
    """Get path to legacy .snowgloberc file for migration purposes"""
    return os.path.join(os.getcwd(), ".snowgloberc")


def migrate_rc_file_if_needed():
    """Migrate .snowgloberc to .snowglobe/config.rc if needed"""
    legacy_path = get_legacy_rc_file_path()
    new_path = get_rc_file_path()

    # If new file already exists, no migration needed
    if os.path.exists(new_path):
        return

    # If legacy file exists, migrate it
    if os.path.exists(legacy_path):
        # Ensure .snowglobe directory exists
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        # Copy content from legacy to new location
        with open(legacy_path, "r") as legacy_file:
            content = legacy_file.read()

        with open(new_path, "w") as new_file:
            new_file.write(content)

        LOGGER.info(f"Migrated {legacy_path} to {new_path}")


class Config:
    def __init__(self, require_api_key=True):
        # Migrate legacy .snowgloberc if needed
        migrate_rc_file_if_needed()

        self.SNOWGLOBE_APPLICATION_HEARTBEAT_INTERVAL_MINUTES = int(
            os.getenv("SNOWGLOBE_APPLICATION_HEARTBEAT_INTERVAL_MINUTES", "5")
        )
        self.CONCURRENT_HEARTBEATS_PER_INTERVAL = 120
        self.CONCURRENT_HEARTBEATS_INTERVAL_SECONDS = 60

        # Initialize API key - optionally raise exception if missing
        if require_api_key:
            self.API_KEY = self.get_api_key()
        else:
            # For auth command, don't require API key during initialization
            try:
                self.API_KEY = self.get_api_key()
            except ValueError:
                self.API_KEY = None

        self.APPLICATION_ID = self.get_application_id()
        self.CONTROL_PLANE_URL = self.get_control_plane_url()
        self.SNOWGLOBE_CLIENT_URL = self.get_snowglobe_client_url()
        self.SNOWGLOBE_CLIENT_PORT = self.get_snowglobe_client_port()
        self.CONCURRENT_COMPLETIONS_PER_INTERVAL = self.get_completions_per_interval()
        self.CONCURRENT_COMPLETIONS_INTERVAL_SECONDS = (
            self.get_completions_interval_seconds()
        )
        self.CONCURRENT_RISK_EVALUATIONS = self.get_concurrent_risk_evaluations()
        self.CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS = (
            self.get_concurrent_risk_evaluations_interval_seconds()
        )
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    def get_snowglobe_client_port(self) -> int:
        snowglobe_client_port = os.getenv("SNOWGLOBE_CLIENT_PORT")
        if not snowglobe_client_port:
            snowglobe_client_port = "8000"
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("SNOWGLOBE_CLIENT_PORT="):
                            snowglobe_client_port = line.strip().split("=", 1)[1]
                            break
        LOGGER.debug(f"setting SNOWGLOBE_CLIENT_PORT: {snowglobe_client_port}")
        return int(snowglobe_client_port)

    def get_snowglobe_client_url(self) -> str:
        snowglobe_client_url = os.getenv("SNOWGLOBE_CLIENT_URL")
        if not snowglobe_client_url:
            snowglobe_client_url = "http://localhost:8000"
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("SNOWGLOBE_CLIENT_URL="):
                            snowglobe_client_url = line.strip().split("=", 1)[1]
                            break
        LOGGER.debug(f"setting SNOWGLOBE_CLIENT_URL: {snowglobe_client_url}")
        return snowglobe_client_url

    def get_completions_interval_seconds(self) -> int:
        completions_interval_seconds = os.getenv("COMPLETIONS_INTERVAL_SECONDS")
        if not completions_interval_seconds:
            completions_interval_seconds = "60"
            LOGGER.debug(
                "COMPLETIONS_INTERVAL_SECONDS not found in environment variables, using COMPLETIONS_INTERVAL as fallback"
            )
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("COMPLETIONS_INTERVAL_SECONDS="):
                            completions_interval_seconds = line.strip().split("=", 1)[1]
                            break
        return int(completions_interval_seconds)

    def get_completions_per_interval(self) -> int:
        completions_per_second = os.getenv("COMPLETIONS_PER_SECOND")
        if not completions_per_second:
            completions_per_second = "120"
            LOGGER.debug(
                "COMPLETIONS_PER_SECOND not found in environment variables, using MAX_COMPLETIONS as fallback"
            )
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("COMPLETIONS_PER_SECOND="):
                            completions_per_second = line.strip().split("=", 1)[1]
                            break
        return int(completions_per_second)

    def get_concurrent_risk_evaluations(self) -> int:
        concurrent_risk_evaluations = os.getenv("CONCURRENT_RISK_EVALUATIONS")
        if not concurrent_risk_evaluations:
            concurrent_risk_evaluations = "120"
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("CONCURRENT_RISK_EVALUATIONS="):
                            concurrent_risk_evaluations = line.strip().split("=", 1)[1]
                            break
        return int(concurrent_risk_evaluations)

    def get_concurrent_risk_evaluations_interval_seconds(self) -> int:
        concurrent_risk_evaluations_interval_seconds = os.getenv(
            "CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS"
        )
        if not concurrent_risk_evaluations_interval_seconds:
            concurrent_risk_evaluations_interval_seconds = "60"
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith(
                            "CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS="
                        ):
                            concurrent_risk_evaluations_interval_seconds = (
                                line.strip().split("=", 1)[1]
                            )
                            break
        return int(concurrent_risk_evaluations_interval_seconds)

    def get_control_plane_url(self) -> str:
        control_plane_url = os.getenv("CONTROL_PLANE_URL")
        if not control_plane_url:
            control_plane_url = "https://api.snowglobe.guardrailsai.com"
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        LOGGER.debug(f"Checking line: {line.strip()}")
                        if line.startswith("CONTROL_PLANE_URL="):
                            control_plane_url = line.strip().split("=", 1)[1]
                            break
        LOGGER.debug(f"setting CONTROL_PLANE_URL: {control_plane_url}")
        return control_plane_url

    def get_api_key(self) -> str:
        api_key = os.getenv("SNOWGLOBE_API_KEY") or os.getenv("GUARDRAILS_API_KEY")
        if not api_key:
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("SNOWGLOBE_API_KEY="):
                            api_key = line.strip().split("=", 1)[1]
                            break
        if not api_key:
            raise ValueError(
                "API key is required either passed as an argument or set as an environment variable. \n"
                "You can set the API key as an environment variable by running: \n"
                "export SNOWGLOBE_API_KEY=<your_api_key> \n"
                "or \n"
                "export GUARDRAILS_API_KEY=<your_api_key> \n"
                "Or you can create a .snowglobe/config.rc file in the current directory with the line: \n"
                "SNOWGLOBE_API_KEY=<your_api_key> \n"
            )
        return api_key

    def get_application_id(self) -> str:
        application_id = os.getenv("SNOWGLOBE_APP_ID")
        if not application_id:
            rc_path = get_rc_file_path()
            if os.path.exists(rc_path):
                with open(rc_path, "r") as rc_file:
                    for line in rc_file:
                        if line.startswith("SNOWGLOBE_APP_ID="):
                            application_id = line.strip().split("=", 1)[1]
                            break
        return application_id


config = Config(require_api_key=False)


def get_api_key_or_raise() -> str:
    """Get API key, raising ValueError if not found - for commands that require it"""
    api_key = config.API_KEY
    if not api_key:
        # Try to get it fresh in case it was just set
        try:
            api_key = config.get_api_key()
            config.API_KEY = api_key  # Cache it
        except ValueError:
            pass

    if not api_key:
        raise ValueError(
            "API key is required either passed as an argument or set as an environment variable. \n"
            "You can set the API key as an environment variable by running: \n"
            "export SNOWGLOBE_API_KEY=<your_api_key> \n"
            "or \n"
            "export GUARDRAILS_API_KEY=<your_api_key> \n"
            "Or you can create a .snowglobe/config.rc file in the current directory with the line: \n"
            "SNOWGLOBE_API_KEY=<your_api_key> \n"
        )
    return api_key
