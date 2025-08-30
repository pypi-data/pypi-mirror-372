"""
Project and agent management for the new clean file structure
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SNOWGLOBE_DIR = ".snowglobe"
AGENTS_FILE = "agents.json"
CONFIG_FILE = "config.json"


class ProjectManager:
    """Manages snowglobe project structure and agent mappings"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.snowglobe_dir = self.project_root / SNOWGLOBE_DIR
        self.agents_file = self.snowglobe_dir / AGENTS_FILE
        self.config_file = self.snowglobe_dir / CONFIG_FILE

    def ensure_project_structure(self) -> None:
        """Create .snowglobe directory if it doesn't exist"""
        self.snowglobe_dir.mkdir(exist_ok=True)

        # Create agents.json if it doesn't exist
        if not self.agents_file.exists():
            with open(self.agents_file, "w") as f:
                json.dump({}, f, indent=2)

    def load_agents_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Load agent UUID mappings from .snowglobe/agents.json"""
        if not self.agents_file.exists():
            return {}

        try:
            with open(self.agents_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return empty dict if file is corrupted
            return {}

    def save_agents_mapping(self, mapping: Dict[str, Dict[str, Any]]) -> None:
        """Save agent UUID mappings to .snowglobe/agents.json"""
        # Only ensure directory exists, not the full structure to avoid recursion
        self.snowglobe_dir.mkdir(exist_ok=True)

        with open(self.agents_file, "w") as f:
            json.dump(mapping, f, indent=2, sort_keys=True)

    def add_agent_mapping(self, filename: str, uuid: str, name: str) -> None:
        """Add a new agent mapping"""
        mapping = self.load_agents_mapping()

        mapping[filename] = {
            "uuid": uuid,
            "name": name,
            "created": datetime.utcnow().isoformat() + "Z",
        }

        self.save_agents_mapping(mapping)

    def get_agent_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get agent info by filename"""
        mapping = self.load_agents_mapping()
        return mapping.get(filename)

    def get_agent_by_uuid(self, uuid: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get agent filename and info by UUID"""
        mapping = self.load_agents_mapping()

        for filename, info in mapping.items():
            if info.get("uuid") == uuid:
                return filename, info

        return None

    def list_agents(self) -> List[Tuple[str, Dict[str, Any]]]:
        """List all agents in the project"""
        mapping = self.load_agents_mapping()
        agents = []

        for filename, info in mapping.items():
            # Check if the file actually exists
            file_path = self.project_root / filename
            if file_path.exists():
                agents.append((filename, info))

        return agents

    def remove_agent_mapping(self, filename: str) -> bool:
        """Remove an agent mapping"""
        mapping = self.load_agents_mapping()

        if filename in mapping:
            del mapping[filename]
            self.save_agents_mapping(mapping)
            return True

        return False

    def sanitize_filename(self, name: str, default: str = "agent_wrapper") -> str:
        """Convert agent name to safe filename"""
        if not name or not name.strip():
            return f"{default}.py"

        # Replace spaces and special chars with underscores
        safe_name = re.sub(r"[^\w\s-]", "", name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name)
        safe_name = safe_name.lower().strip("_")

        # Ensure it's not empty and has .py extension
        if not safe_name:
            safe_name = default

        return f"{safe_name}.py"

    def find_available_filename(self, preferred_name: str) -> str:
        """Find an available filename, adding numbers if needed"""
        base_name = preferred_name
        if base_name.endswith(".py"):
            base_name = base_name[:-3]

        counter = 1
        filename = f"{base_name}.py"

        while (self.project_root / filename).exists():
            filename = f"{base_name}_{counter}.py"
            counter += 1

        return filename

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from .snowglobe/config.json"""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to .snowglobe/config.json"""
        self.snowglobe_dir.mkdir(exist_ok=True)

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2, sort_keys=True)

    def get_api_key(self) -> Optional[str]:
        """Get API key from config or environment"""
        # Check environment first
        api_key = os.getenv("SNOWGLOBE_API_KEY") or os.getenv("GUARDRAILS_API_KEY")
        if api_key:
            return api_key

        # Check .snowglobe/config.json
        config = self.load_config()
        api_key = config.get("api_key")
        if api_key:
            return api_key

        # Check legacy .snowgloberc in current directory
        rc_path = self.project_root / ".snowgloberc"
        if rc_path.exists():
            try:
                with open(rc_path, "r") as f:
                    for line in f:
                        if line.startswith("SNOWGLOBE_API_KEY="):
                            return line.strip().split("=", 1)[1]
            except IOError:
                pass

        return None

    def set_api_key(self, api_key: str) -> None:
        """Set API key in config"""
        config = self.load_config()
        config["api_key"] = api_key
        self.save_config(config)

    def get_control_plane_url(self) -> str:
        """Get control plane URL from config or environment"""
        # Check environment first
        url = os.getenv("CONTROL_PLANE_URL")
        if url:
            return url

        # Check .snowglobe/config.json
        config = self.load_config()
        url = config.get("control_plane_url")
        if url:
            return url

        # Check legacy .snowgloberc in current directory
        rc_path = self.project_root / ".snowgloberc"
        if rc_path.exists():
            try:
                with open(rc_path, "r") as f:
                    for line in f:
                        if line.startswith("CONTROL_PLANE_URL="):
                            return line.strip().split("=", 1)[1]
            except IOError:
                pass

        return "https://api.snowglobe.guardrailsai.com"

    def set_control_plane_url(self, url: str) -> None:
        """Set control plane URL in config"""
        config = self.load_config()
        config["control_plane_url"] = url
        self.save_config(config)

    def migrate_legacy_config(self) -> bool:
        """Migrate .snowgloberc to .snowglobe/config.json"""
        rc_path = self.project_root / ".snowgloberc"
        if not rc_path.exists():
            return False

        config = self.load_config()
        migrated = False

        try:
            with open(rc_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SNOWGLOBE_API_KEY="):
                        api_key = line.split("=", 1)[1]
                        if api_key and not config.get("api_key"):
                            config["api_key"] = api_key
                            migrated = True
                    elif line.startswith("CONTROL_PLANE_URL="):
                        url = line.split("=", 1)[1]
                        if url and not config.get("control_plane_url"):
                            config["control_plane_url"] = url
                            migrated = True

            if migrated:
                self.save_config(config)
                # Optionally remove the old file
                # rc_path.unlink()  # Uncomment to delete legacy file

            return migrated
        except IOError:
            return False

    def validate_project(self) -> Tuple[bool, List[str]]:
        """Validate project structure and return issues"""
        issues = []

        # Check if .snowglobe directory exists
        if not self.snowglobe_dir.exists():
            issues.append(
                "No .snowglobe directory found. Run 'snowglobe-connect init' to set up."
            )
            return False, issues

        # Check if agents.json exists and is valid
        if not self.agents_file.exists():
            issues.append("No agents.json file found in .snowglobe/")
        else:
            try:
                mapping = self.load_agents_mapping()

                # Check for orphaned files
                for filename in mapping.keys():
                    file_path = self.project_root / filename
                    if not file_path.exists():
                        issues.append(f"Agent file missing: {filename}")

                # Check for unmapped agent files
                for py_file in self.project_root.glob("*_wrapper.py"):
                    if py_file.name not in mapping:
                        issues.append(f"Unmapped agent file found: {py_file.name}")

            except Exception as e:
                issues.append(f"Invalid agents.json file: {e}")

        is_valid = len(issues) == 0
        return is_valid, issues


def get_project_manager(project_root: str = None) -> ProjectManager:
    """Get a ProjectManager instance"""
    return ProjectManager(project_root)
