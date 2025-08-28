"""Configuration management for the ASI1 MCP CLI."""

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
from typing import Dict, List, Optional
import commentjson

from .const import CONFIG_FILE, CONFIG_DIR


@dataclass
class LLMConfig:
    """Configuration for the ASI:One LLM."""
    model: str = "asi1-mini"
    provider: str = "asi-one"
    api_key: Optional[str] = None
    temperature: float = 0
    base_url: Optional[str] = "https://api.asi1.ai/v1/chat/completions"

    @classmethod
    def from_dict(cls, config: dict) -> "LLMConfig":
        """Create LLMConfig from dictionary."""
        return cls(
            model=config.get("model", cls.model),
            provider=config.get("provider", cls.provider),
            api_key=config.get("api_key", os.getenv("ASI1_API_KEY", "")),
            temperature=config.get("temperature", cls.temperature),
            base_url=config.get("base_url", cls.base_url),
        )


@dataclass
class ServerConfig:
    """Configuration for an MCP server."""
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    enabled: bool = True
    exclude_tools: Optional[List[str]] = None
    requires_confirmation: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}
        if self.exclude_tools is None:
            self.exclude_tools = []
        if self.requires_confirmation is None:
            self.requires_confirmation = []

    @classmethod
    def from_dict(cls, config: dict) -> "ServerConfig":
        """Create ServerConfig from dictionary."""
        return cls(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {}),
            enabled=config.get("enabled", True),
            exclude_tools=config.get("exclude_tools", []),
            requires_confirmation=config.get("requires_confirmation", [])
        )


@dataclass
class AppConfig:
    """Main application configuration."""
    llm: LLMConfig
    system_prompt: str
    mcp_servers: Dict[str, ServerConfig]
    tools_requires_confirmation: List[str]

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from file."""
        config_paths = [CONFIG_FILE, CONFIG_DIR / "config.json"]
        chosen_path = next((path for path in config_paths if os.path.exists(path)), None)

        if chosen_path is None:
            raise FileNotFoundError(f"Could not find config file in any of: {', '.join(map(str, config_paths))}. Please create one manually or run 'asi1 --init' for instructions.")

        with open(chosen_path, 'r') as f:
            config = commentjson.load(f)

        # Safely get mcpServers, defaulting to an empty dict if not present
        mcp_servers_config = config.get("mcpServers", {})

        tools_requires_confirmation = []
        for server_config in mcp_servers_config.values():
            tools_requires_confirmation.extend(server_config.get("requires_confirmation", []))

        return cls(
            llm=LLMConfig.from_dict(config.get("llm", {})),
            system_prompt=config["systemPrompt"],
            mcp_servers={name: ServerConfig.from_dict(server_config)
                         for name, server_config in mcp_servers_config.items()},
            tools_requires_confirmation=tools_requires_confirmation
        )

    def get_enabled_servers(self) -> Dict[str, ServerConfig]:
        """Get only enabled server configurations."""
        return {name: config for name, config in self.mcp_servers.items() if config.enabled}

# Removed copy_example_config function entirely
