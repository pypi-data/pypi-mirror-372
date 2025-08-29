"""Configuration management for DawnAI SDK.

Reads configuration from environment variables or config file.
Priority order:
1. Environment variables (highest priority)
2. .dawnai config file in current directory
3. .dawnai config file in home directory
4. Default values (lowest priority)
"""

import json
import os
from pathlib import Path
from typing import Any


class SDKConfig:
    """SDK Configuration manager."""

    # Environment variable names
    ENV_USER_ID = "DAWNAI_USER_ID"
    ENV_STRATEGY_ID = "DAWNAI_STRATEGY_ID"
    ENV_SESSION_ID = "DAWNAI_SESSION_ID"
    ENV_IS_PAPER = "DAWNAI_IS_PAPER"
    ENV_BASE_URL = "DAWNAI_BASE_URL"
    ENV_API_KEY = "DAWNAI_API_KEY"

    # Config file name
    CONFIG_FILE = ".dawnai"

    def __init__(self) -> None:
        """Initialize configuration."""
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from various sources."""
        # Start with defaults
        self._config = {
            "base_url": "http://localhost:3000",
            "api_key": None,
            "user_id": "sdk-user",
            "strategy_id": None,
            "agent_session_id": None,
            "is_paper": True,
        }

        # Load from config files (lower priority)
        self._load_from_config_file()

        # Override with environment variables (highest priority)
        self._load_from_env()

    def _load_from_config_file(self) -> None:
        """Load configuration from .dawnai file."""
        # Check current directory first
        local_config = Path.cwd() / self.CONFIG_FILE
        if local_config.exists():
            self._merge_config_file(local_config)
            return

        # Check home directory
        home_config = Path.home() / self.CONFIG_FILE
        if home_config.exists():
            self._merge_config_file(home_config)

    def _merge_config_file(self, config_path: Path) -> None:
        """Merge configuration from a file."""
        try:
            with config_path.open() as f:
                content = f.read().strip()

                # Try JSON first with proper validation
                try:
                    file_config = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    # Not valid JSON, try key=value format
                    file_config = {}
                    for raw_line in content.split("\n"):
                        line = raw_line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip().lower().replace("_", "-")
                            value = value.strip()

                            # Convert string booleans
                            if value.lower() in ("true", "yes", "1"):
                                value = True  # type: ignore[assignment]
                            elif value.lower() in ("false", "no", "0"):
                                value = False  # type: ignore[assignment]
                            elif value.lower() == "none":
                                value = None  # type: ignore[assignment]

                            # Map to internal names
                            if key in {"userid", "user-id"}:
                                file_config["user_id"] = value
                            elif key in {"strategyid", "strategy-id"}:
                                file_config["strategy_id"] = value
                            elif key in {"agentsessionid", "agent-session-id"}:
                                file_config["agent_session_id"] = value
                            elif key in {"ispaper", "is-paper"}:
                                file_config["is_paper"] = value
                            elif key in {"baseurl", "base-url"}:
                                file_config["base_url"] = value
                            elif key in {"apikey", "api-key"}:
                                file_config["api_key"] = value

                # Merge with existing config
                self._config.update(file_config)
                print(f"📁 Loaded config from: {config_path}")  # noqa: T201
        except Exception as e:
            print(f"⚠️  Error loading config from {config_path}: {e}")  # noqa: T201

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Check each environment variable
        if os.environ.get(self.ENV_USER_ID):
            self._config["user_id"] = os.environ[self.ENV_USER_ID]

        if os.environ.get(self.ENV_STRATEGY_ID):
            self._config["strategy_id"] = os.environ[self.ENV_STRATEGY_ID]

        if os.environ.get(self.ENV_SESSION_ID):
            self._config["agent_session_id"] = os.environ[self.ENV_SESSION_ID]

        if os.environ.get(self.ENV_IS_PAPER):
            value = os.environ[self.ENV_IS_PAPER].lower()
            self._config["is_paper"] = value in ("true", "yes", "1")

        if os.environ.get(self.ENV_BASE_URL):
            self._config["base_url"] = os.environ[self.ENV_BASE_URL]

        if os.environ.get(self.ENV_API_KEY):
            self._config["api_key"] = os.environ[self.ENV_API_KEY]

    @property
    def user_id(self) -> str:
        """Get user ID."""
        return str(self._config["user_id"])

    @property
    def strategy_id(self) -> str | None:
        """Get strategy ID."""
        val = self._config["strategy_id"]
        return str(val) if val is not None else None

    @property
    def agent_session_id(self) -> str | None:
        """Get agent session ID."""
        val = self._config["agent_session_id"]
        return str(val) if val is not None else None

    @property
    def is_paper(self) -> bool:
        """Get paper trading flag."""
        return bool(self._config["is_paper"])

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return str(self._config["base_url"])

    @property
    def api_key(self) -> str | None:
        """Get API key."""
        val = self._config["api_key"]
        return str(val) if val is not None else None

    def get_context(self) -> dict[str, Any]:
        """Get the context dictionary for API calls."""
        return {
            "userId": self.user_id,
            "strategyId": self.strategy_id,
            "agentSessionId": self.agent_session_id,
            "isPaper": self.is_paper,
        }

    def update(self, **kwargs: Any) -> None:
        """Update configuration values."""
        for key, value in kwargs.items():
            if key in self._config:
                self._config[key] = value

    def save_to_file(self, path: Path | None = None) -> None:
        """Save current configuration to a file."""
        if path is None:
            path = Path.cwd() / self.CONFIG_FILE

        config_to_save = {
            k: v for k, v in self._config.items() if v is not None  # Don't save None values
        }

        with path.open("w") as f:
            json.dump(config_to_save, f, indent=2)

        print(f"✅ Configuration saved to: {path}")  # noqa: T201

    def __str__(self) -> str:
        """String representation of config."""
        return (
            f"SDKConfig(\n"
            f"  base_url: {self.base_url}\n"
            f"  user_id: {self.user_id}\n"
            f"  strategy_id: {self.strategy_id}\n"
            f"  agent_session_id: {self.agent_session_id}\n"
            f"  is_paper: {self.is_paper}\n"
            f"  api_key: {'***' if self.api_key else 'None'}\n"
            f")"
        )


# Global config instance
_global_config = SDKConfig()


def get_config() -> SDKConfig:
    """Get the global SDK configuration instance."""
    return _global_config


def configure(**kwargs: Any) -> None:
    """Update the global configuration."""
    _global_config.update(**kwargs)


def create_config_file() -> None:
    """Interactive helper to create a config file."""
    print("\n🔧 DawnAI SDK Configuration Setup")  # noqa: T201
    print("-" * 40)  # noqa: T201

    config = {}

    # Get user inputs
    base_url = input("Base URL [http://localhost:3000]: ").strip()
    if base_url:
        config["base_url"] = base_url

    user_id = input("User ID [sdk-user]: ").strip()
    if user_id:
        config["user_id"] = user_id

    strategy_id = input("Strategy ID (optional): ").strip()
    if strategy_id:
        config["strategy_id"] = strategy_id

    session_id = input("Agent Session ID (optional): ").strip()
    if session_id:
        config["agent_session_id"] = session_id

    is_paper = input("Paper trading? [yes/no, default: yes]: ").strip().lower()
    if is_paper:
        config["is_paper"] = "true" if is_paper in ("yes", "y", "1", "true") else "false"

    api_key = input("API Key (optional): ").strip()
    if api_key:
        config["api_key"] = api_key

    # Save location
    print("\nWhere to save?")  # noqa: T201
    print("1. Current directory (./.dawnai)")  # noqa: T201
    print("2. Home directory (~/.dawnai)")  # noqa: T201
    choice = input("Choice [1]: ").strip() or "1"

    path = Path.home() / ".dawnai" if choice == "2" else Path.cwd() / ".dawnai"

    # Save the file
    with path.open("w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to: {path}")  # noqa: T201
    print("\nYou can also set environment variables:")  # noqa: T201
    print("  export DAWNAI_USER_ID='your-user-id'")  # noqa: T201
    print("  export DAWNAI_STRATEGY_ID='your-strategy-id'")  # noqa: T201
    print("  export DAWNAI_SESSION_ID='your-session-id'")  # noqa: T201
    print("  export DAWNAI_IS_PAPER=true")  # noqa: T201
    print("  export DAWNAI_BASE_URL='http://localhost:3000'")  # noqa: T201
    print("  export DAWNAI_API_KEY='your-api-key'")  # noqa: T201


if __name__ == "__main__":
    # If run directly, show current config or create new one
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_config_file()
    else:
        print("Current Configuration:")  # noqa: T201
        print(get_config())  # noqa: T201
        print("\nRun 'python -m dawnai.config create' to create a config file")  # noqa: T201
