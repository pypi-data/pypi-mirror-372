"""Pydantic models for MCP configuration validation."""

import os
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Constants
ZENABLE_MCP_ENDPOINT = os.environ.get(
    "ZENABLE_API_ENDPOINT", "https://mcp.www.zenable.app/"
)


class _MCPServerConfig(BaseModel):
    """Base model for MCP server configuration."""

    command: str = Field(..., description="The command to execute")
    args: list[str] = Field(
        default_factory=list, description="Arguments for the command"
    )
    disabled: Optional[bool] = Field(None, description="Whether the server is disabled")
    alwaysAllow: Optional[list[str]] = Field(
        None, description="Tools to always allow without prompting"
    )
    autoApprove: Optional[list[str]] = Field(None, description="Tools to auto-approve")
    trust: Optional[bool] = Field(None, description="Whether to trust this server")

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility


class _ZenableMCPConfig(_MCPServerConfig):
    """Zenable-specific MCP server configuration."""

    command: str = Field(default="npx", description="The command to execute")
    args: list[str] = Field(
        ..., description="Arguments including mcp-remote and API key"
    )

    @field_validator("command")
    def validate_command(cls, v):
        if v != "npx":
            raise ValueError(f"Zenable MCP must use 'npx' command, got '{v}'")
        return v

    @field_validator("args")
    def validate_args(cls, v):
        if not v:
            raise ValueError("Args cannot be empty")

        # Check for required components
        args_str = " ".join(v)

        if "mcp-remote" not in args_str:
            raise ValueError("Args must include 'mcp-remote'")

        if ZENABLE_MCP_ENDPOINT not in args_str:
            raise ValueError(
                f"Args must include Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}"
            )

        # Check for API key
        has_api_key = any("API_KEY:" in arg for arg in v)
        if not has_api_key:
            raise ValueError("Args must include API_KEY header")

        return v

    @model_validator(mode="after")
    def validate_mcp_remote_version(self):
        """Validate that mcp-remote uses @latest version."""
        for arg in self.args:
            if "mcp-remote@" in arg and "@latest" not in arg:
                raise ValueError(f"mcp-remote must use @latest version, got: {arg}")
        return self


class _RooMCPConfig(_ZenableMCPConfig):
    """Roo-specific MCP configuration with strict requirements."""

    disabled: bool = Field(default=False, description="Must be explicitly set to false")
    alwaysAllow: list[str] = Field(
        default_factory=lambda: ["conformance_check"],
        description="Must include conformance_check",
    )

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Roo MCP must have disabled=false, got {v}")
        return v

    @field_validator("alwaysAllow")
    def validate_always_allow(cls, v):
        if "conformance_check" not in v:
            raise ValueError("Roo MCP must have 'conformance_check' in alwaysAllow")
        return v


class _KiroMCPConfig(_ZenableMCPConfig):
    """Kiro-specific MCP configuration."""

    disabled: bool = Field(default=False, description="Must be explicitly set to false")
    autoApprove: list[str] = Field(
        default_factory=lambda: ["conformance_check"],
        description="Must include conformance_check",
    )

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Kiro MCP must have disabled=false, got {v}")
        return v

    @field_validator("autoApprove")
    def validate_auto_approve(cls, v):
        if "conformance_check" not in v:
            raise ValueError("Kiro MCP must have 'conformance_check' in autoApprove")
        return v


class _GeminiMCPConfig(_ZenableMCPConfig):
    """Gemini CLI-specific MCP configuration."""

    trust: bool = Field(default=True, description="Must be set to true")

    @field_validator("trust")
    def validate_trust(cls, v):
        if v is not True:
            raise ValueError(f"Gemini MCP must have trust=true, got {v}")
        return v


class _VSCodeMCPServerConfig(BaseModel):
    """VS Code-specific MCP server configuration."""

    type: str = Field(..., description="Server type (sse, http, or stdio)")
    url: Optional[str] = Field(None, description="URL for sse/http servers")
    headers: Optional[dict[str, str]] = Field(None, description="HTTP headers")
    command: Optional[str] = Field(None, description="Command for stdio servers")
    args: Optional[list[str]] = Field(None, description="Args for stdio servers")

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility

    @field_validator("type")
    def validate_type(cls, v):
        valid_types = ["sse", "http", "stdio"]
        if v not in valid_types:
            raise ValueError(
                f"VS Code MCP server type must be one of {valid_types}, got '{v}'"
            )
        return v

    @model_validator(mode="after")
    def validate_config_consistency(self):
        """Validate that required fields are present based on server type."""
        if self.type in ["sse", "http"]:
            if not self.url:
                raise ValueError(f"URL is required for {self.type} servers")
            if self.url and ZENABLE_MCP_ENDPOINT not in self.url:
                raise ValueError(
                    f"URL must be Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}"
                )
            if self.headers and "API_KEY" not in self.headers:
                raise ValueError("Headers must include API_KEY for Zenable servers")
        elif self.type == "stdio":
            if not self.command:
                raise ValueError("Command is required for stdio servers")
        return self


class _MCPConfigFile(BaseModel):
    """Model for the complete MCP configuration file."""

    mcpServers: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="MCP server configurations"
    )

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional top-level fields
