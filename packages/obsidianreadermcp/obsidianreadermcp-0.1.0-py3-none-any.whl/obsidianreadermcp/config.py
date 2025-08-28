"""
Configuration management for ObsidianReaderMCP.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ObsidianConfig(BaseModel):
    """Configuration for Obsidian API connection."""

    host: str = Field(
        default_factory=lambda: os.getenv("OBSIDIAN_HOST", "localhost"),
        description="Obsidian API host",
    )
    port: int = Field(
        default_factory=lambda: int(os.getenv("OBSIDIAN_PORT", "27123")),
        description="Obsidian API port",
    )
    api_key: str = Field(
        default_factory=lambda: os.getenv("OBSIDIAN_API_KEY", ""),
        description="Obsidian API key",
    )
    use_https: bool = Field(
        default_factory=lambda: os.getenv("OBSIDIAN_USE_HTTPS", "false").lower()
        == "true",
        description="Whether to use HTTPS",
    )
    timeout: int = Field(
        default_factory=lambda: int(os.getenv("OBSIDIAN_TIMEOUT", "30")),
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("OBSIDIAN_MAX_RETRIES", "3")),
        description="Maximum number of retries for failed requests",
    )
    rate_limit: int = Field(
        default_factory=lambda: int(os.getenv("OBSIDIAN_RATE_LIMIT", "10")),
        description="Maximum requests per second",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        if not v:
            raise ValueError("API key is required")
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @property
    def base_url(self) -> str:
        """Get the base URL for the Obsidian API."""
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"

    @property
    def headers(self) -> dict:
        """Get the headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


class MCPConfig(BaseModel):
    """Configuration for MCP server."""

    server_name: str = Field(
        default="obsidian-reader-mcp", description="MCP server name"
    )
    version: str = Field(default="0.1.0", description="MCP server version")
    description: str = Field(
        default="Obsidian Vault Management MCP Server",
        description="MCP server description",
    )
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level",
    )
    enable_debug: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_DEBUG", "false").lower() == "true",
        description="Enable debug mode",
    )


def get_config() -> tuple[ObsidianConfig, MCPConfig]:
    """Get the configuration objects."""
    obsidian_config = ObsidianConfig()
    mcp_config = MCPConfig()
    return obsidian_config, mcp_config
