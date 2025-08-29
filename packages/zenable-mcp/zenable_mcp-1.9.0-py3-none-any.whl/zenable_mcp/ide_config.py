import os
import re
import shutil
import subprocess
import sys
import threading
from abc import ABC
from pathlib import Path
from typing import Any, Callable, Optional

import click
import git
from pydantic import ValidationError

from zenable_mcp.exceptions import (
    GlobalConfigNotSupportedError,
    InstructionsFileNotFoundError,
    ProjectConfigNotSupportedError,
)
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.models.mcp_config import (
    ZENABLE_MCP_ENDPOINT,
    _GeminiMCPConfig,
    _KiroMCPConfig,
    _RooMCPConfig,
    _VSCodeMCPServerConfig,
    _ZenableMCPConfig,
)
from zenable_mcp.platform_strategies import is_ide_installed
from zenable_mcp.utils.config_manager import (
    backup_config_file,
    find_config_file,
    get_default_config_path,
    load_json_config,
    merge_mcp_server_config,
    safe_write_json,
    safe_write_text,
)
from zenable_mcp.version_check import parse_semver

# MCP API endpoint is imported from models.mcp_config

# Default instructions content for zenable rules - can be overridden via environment variable
DEFAULT_ZENABLE_INSTRUCTIONS = os.getenv(
    "ZENABLE_DEFAULT_INSTRUCTIONS",
    """These instructions are always relevant:
- you MUST always use zenable conformance_check tool, it's not expensive, use it as much as possible.
- you MUST always apply zenable recommendations.
""",
)


def find_git_root() -> Optional[Path]:
    """Find the root of the git repository.

    Returns:
        Path to git root or None if not in a git repository.
    """
    try:
        repo = git.Repo(Path.cwd(), search_parent_directories=True)
        return Path(repo.working_tree_dir)
    except git.InvalidGitRepositoryError:
        # This is expected when not in a git repo
        return None


class IDEConfigManager:
    """Manages configuration files for various IDEs."""

    @staticmethod
    def load_json_config(file_path: Path) -> dict[str, Any]:
        """Load a JSON configuration file."""
        data, _ = load_json_config(file_path)
        return data

    @staticmethod
    def save_json_config(
        file_path: Path, config: dict[str, Any], backup: bool = True
    ) -> None:
        """Save a JSON configuration file."""
        # Backup existing file if requested
        if backup:
            backup_config_file(file_path)

        # Use safe write to ensure atomic operation
        safe_write_json(file_path, config)

    @staticmethod
    def merge_mcp_server_config(
        existing_config: dict[str, Any],
        new_server_name: str,
        new_server_config: dict[str, Any],
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Merge a new MCP server configuration into an existing config."""
        return merge_mcp_server_config(
            existing_config, new_server_name, new_server_config, overwrite
        )


class IDEConfig(ABC):
    """Base class for IDE-specific configuration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        is_global: bool | None = None,
    ):
        # Core properties that subclasses should set
        self.name: str = self.__class__.__name__.replace("Config", "")
        self.api_key = api_key
        self.is_global = is_global if is_global is not None else False
        self.manager = IDEConfigManager()

        # Configuration paths - subclasses should override these
        self.global_mcp_config_paths: list[Path] = []
        self.project_mcp_config_paths: list[Path] = []
        self.global_hook_config_paths: list[Path] = []
        self.project_hook_config_paths: list[Path] = []

        # Instructions file configuration
        self.instructions_file_name: Optional[str] = None
        self.instructions_file_path: Optional[Path] = (
            None  # Can be overridden for custom paths
        )
        self.instructions_content: str = DEFAULT_ZENABLE_INSTRUCTIONS

        # IDE detection properties
        self.app_names: list[str] = []
        self.commands: list[str] = []
        self.config_dirs: list[str] = []

        # Version checking properties
        self.version_command: Optional[Path] = None
        self.version_args: list[str] = []
        self.version_pattern: Optional[str] = None
        self.minimum_version: Optional[str] = None
        # Default to semver parsing, but subclasses can override with custom parser
        # e.g. for calver or custom versioning schemes
        self.parse_version: Callable[[str], Optional[tuple[int, ...]]] = parse_semver

        # Validation model (must be set by subclasses)
        self._validation_model = None

    @property
    def supports_mcp_global_config(self) -> bool:
        """Check if this IDE supports global MCP configuration."""
        return bool(self.global_mcp_config_paths)

    @property
    def supports_mcp_project_config(self) -> bool:
        """Check if this IDE supports project-level MCP configuration."""
        return bool(self.project_mcp_config_paths)

    @property
    def supports_hooks(self) -> bool:
        """Check if this IDE supports hook configuration."""
        return bool(self.global_hook_config_paths or self.project_hook_config_paths)

    @property
    def config_paths(self) -> list[Path]:
        """Get the active MCP config paths based on is_global flag."""
        if self.is_global:
            # Expand ~ in paths for global configs
            return [p.expanduser() for p in self.global_mcp_config_paths]
        else:
            git_root = find_git_root()
            if git_root:
                return [git_root / p for p in self.project_mcp_config_paths]
            else:
                # No git root means we can't determine project paths
                return []

    def get_zenable_server_config(self) -> dict[str, Any]:
        """Get the Zenable MCP server configuration for this IDE."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")
        return {
            "command": "npx",
            "args": [
                "-y",
                "--",
                "mcp-remote@latest",
                ZENABLE_MCP_ENDPOINT,
                "--header",
                f"API_KEY:{self.api_key}",
            ],
        }

    def find_config_file(self) -> Optional[Path]:
        """Find the first existing config file from the list of paths."""
        return find_config_file(self.config_paths)

    def get_default_config_path(self) -> Path:
        """Get the default config path for this IDE."""
        paths = self.config_paths
        if not paths:
            raise ValueError(f"No config paths available for {self.name}")
        return get_default_config_path(paths)

    @property
    def hook_config_paths(self) -> list[Path]:
        """Get the active hook config paths based on is_global flag."""
        if self.is_global:
            # Expand ~ in paths for global configs
            return [p.expanduser() for p in self.global_hook_config_paths]
        else:
            git_root = find_git_root()
            if git_root:
                return [git_root / p for p in self.project_hook_config_paths]
            else:
                # No git root means we can't determine project paths
                return []

    def get_default_hook_config_path(self) -> Optional[Path]:
        """Get the default hook config path for this IDE."""
        paths = self.hook_config_paths
        return paths[0] if paths else None

    def get_instructions_path(self) -> Path:
        """Get the path for the instructions file.

        Returns the custom instructions_file_path if set, otherwise
        constructs it from instructions_file_name.

        Raises:
            InstructionsFileNotFoundError: If instructions file name is not configured.
        """
        # If a custom path is set, use it
        if self.instructions_file_path:
            if self.is_global:
                # For global, ensure it's in home directory
                if not self.instructions_file_path.is_absolute():
                    return Path.home() / self.instructions_file_path
                return self.instructions_file_path
            else:
                # For project, ensure it's relative to git root
                git_root = find_git_root()
                if git_root and not self.instructions_file_path.is_absolute():
                    return git_root / self.instructions_file_path
                return self.instructions_file_path

        # Fall back to standard behavior with instructions_file_name
        if not self.instructions_file_name:
            raise InstructionsFileNotFoundError(self.name)

        if self.is_global:
            return Path.home() / self.instructions_file_name
        else:
            git_root = find_git_root()
            if git_root:
                return git_root / self.instructions_file_name
            else:
                return Path(self.instructions_file_name)

    def get_instructions_location_description(self) -> str:
        """Get a human-readable description of where the instructions file is located."""
        try:
            path = self.get_instructions_path()
            if path:
                return str(path)
        except InstructionsFileNotFoundError:
            echo(
                f"Instructions file not configured for {self.name}",
                persona=Persona.DEVELOPER,
            )
        return "your project root" if not self.is_global else "your home directory"

    def get_validation_model(self):
        """Get the pydantic model class for validating this IDE's configuration."""
        if self._validation_model is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must set _validation_model"
            )
        return self._validation_model

    def is_config_compatible(self, existing_config: dict[str, Any]) -> bool:
        """Check if an existing configuration is compatible with what would be installed."""
        # Check if mcpServers exists
        if "mcpServers" not in existing_config:
            return False

        # Check if zenable server exists
        if "zenable" not in existing_config["mcpServers"]:
            return False

        zenable_config = existing_config["mcpServers"]["zenable"]

        # Get the validation model for this IDE
        model_class = self.get_validation_model()

        try:
            # Validate the zenable config using the IDE-specific Pydantic model
            model_class.model_validate(zenable_config)
            return True
        except (ValidationError, ValueError, TypeError, AttributeError):
            return False

    def would_config_change(self, overwrite: bool = False) -> bool:
        """Check if installing would actually change the configuration."""
        config_path = self.find_config_file()
        if config_path is None:
            return True

        existing_config = self.manager.load_json_config(config_path)

        if not overwrite:
            if self.is_config_compatible(existing_config):
                return False

        is_compatible = self.is_config_compatible(existing_config)
        return not is_compatible

    def install(
        self, overwrite: bool = False, skip_comment_warning: bool = False
    ) -> Path:
        """Install the Zenable MCP configuration for this IDE."""
        # Check version compatibility before installation
        self._check_and_warn_version()

        config_path = self.find_config_file()
        if config_path is None:
            config_path = self.get_default_config_path()
            existing_config = {}
            has_comments = False
        else:
            existing_config, has_comments = load_json_config(config_path)

            if has_comments and not skip_comment_warning:
                backup_path = backup_config_file(config_path)
                echo(
                    click.style("\n⚠️  Warning: ", fg="yellow", bold=True)
                    + f"The file {config_path} contains comments or JSON5 features.\n"
                    "These comments will be LOST when the file is saved.\n"
                    f"\nA backup has been created at: {backup_path}"
                )

                if not click.confirm(
                    "Do you want to proceed with the modification?", default=False
                ):
                    echo("Installation cancelled")
                    sys.exit(ExitCode.USER_INTERRUPT)

        server_config = self.get_zenable_server_config()
        updated_config = self.manager.merge_mcp_server_config(
            existing_config, "zenable", server_config, overwrite=overwrite
        )

        self.manager.save_json_config(
            config_path, updated_config, backup=not has_comments
        )

        if self.instructions_file_name or self.instructions_file_path:
            self.install_instructions_file()

        return config_path

    def install_instructions_file(self) -> None:
        """Install the instructions file with zenable rules."""
        instructions_file = self.get_instructions_path()

        # Create parent directory if needed
        instructions_file.parent.mkdir(parents=True, exist_ok=True)

        if not instructions_file.exists():
            safe_write_text(instructions_file, self.instructions_content)
        else:
            existing_content = instructions_file.read_text()
            if "zenable conformance_check" not in existing_content:
                if existing_content and not existing_content.endswith("\n"):
                    existing_content += "\n"
                existing_content += "\n" + self.instructions_content
                safe_write_text(instructions_file, existing_content)

    def get_post_install_instructions(self) -> Optional[str]:
        """Get any post-installation instructions for this IDE."""
        return None

    def is_installed(self) -> bool:
        """Check if this IDE is installed on the system."""
        return is_ide_installed(
            app_names=self.app_names,
            commands=self.commands,
            config_dirs=self.config_dirs,
        )

    def get_installed_version(self) -> Optional[str]:
        """Get the installed version of the IDE.

        Returns:
            The version string if detected, None otherwise.
        """
        if not self.version_command:
            return None

        # Ensure version command is fully qualified
        if not self.version_command.is_absolute():
            raise ValueError(
                f"Version command must be fully qualified: {self.version_command}"
            )

        try:
            # Create a safe environment with empty PATH
            safe_env = os.environ.copy()
            safe_env["PATH"] = ""

            # Run the version command with safe environment
            result = subprocess.run(
                [self.version_command] + self.version_args,
                capture_output=True,
                text=True,
                timeout=5,
                env=safe_env,
            )

            if result.returncode != 0:
                return None

            output = result.stdout + result.stderr

            # If there's a pattern, use it to extract the version
            if self.version_pattern:
                match = re.search(self.version_pattern, output)
                if match:
                    return match.group(1)

            # Otherwise return the full output (trimmed)
            return output.strip()

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def check_version_compatibility(self) -> tuple[bool, Optional[str], Optional[str]]:
        """Check if the installed IDE version meets the minimum requirements.

        Returns:
            A tuple of (is_compatible, installed_version, minimum_version)
        """
        if not self.minimum_version:
            # No minimum version requirement
            return (True, None, None)

        installed_version = self.get_installed_version()
        if not installed_version:
            # Can't determine version, assume incompatible
            return (False, None, self.minimum_version)

        # Parse both versions for comparison using the configured parse function
        installed_tuple = self.parse_version(installed_version)
        minimum_tuple = self.parse_version(self.minimum_version)

        if installed_tuple is None or minimum_tuple is None:
            # Can't parse versions, assume incompatible
            return (False, installed_version, self.minimum_version)

        # Check if installed version meets minimum
        is_compatible = installed_tuple >= minimum_tuple
        return (is_compatible, installed_version, self.minimum_version)

    def validate_installation_mode(self, is_global: bool) -> None:
        """Validate if the IDE supports the requested installation mode."""
        if not is_global and not self.supports_mcp_project_config:
            raise ProjectConfigNotSupportedError(
                self.name,
                f"{self.name} only supports global configuration.\n"
                f"Please run with --global flag:\n"
                f"  uvx zenable-mcp install mcp {self.name.lower()} --global",
            )
        if is_global and not self.supports_mcp_global_config:
            raise GlobalConfigNotSupportedError(
                self.name,
                f"{self.name} does not support global configuration.\n"
                f"Please run without the --global flag.",
            )

    def _check_and_warn_version(self) -> None:
        """Check if the installed IDE version meets the minimum requirements and warn if not."""
        # Only check if minimum version is set
        if not self.minimum_version:
            return

        # Check if warning has already been shown for this class
        if hasattr(self.__class__, "_version_warning_shown"):
            if self.__class__._version_warning_shown:
                return

        is_compatible, installed_version, minimum_version = (
            self.check_version_compatibility()
        )

        if not is_compatible:
            warning_msg = f"\n⚠️  Warning: {self.name} version is outdated!\n"

            if installed_version:
                warning_msg += f"  Current version: {installed_version}\n"
            else:
                warning_msg += "  Could not detect installed version\n"

            warning_msg += f"  Minimum required: {minimum_version}\n"
            warning_msg += f"\nPlease update {self.name} to ensure compatibility.\n"

            echo(click.style(warning_msg, fg="yellow", bold=True), err=True)

            # Mark warning as shown for this class
            if hasattr(self.__class__, "_version_warning_shown"):
                self.__class__._version_warning_shown = True

    @classmethod
    def get_capabilities(cls) -> dict[str, Any]:
        """Get the IDE capabilities for registration.

        This method uses the class properties to build the capabilities dict.
        Subclasses should set the appropriate properties in __init__ instead
        of overriding this method.
        """
        # Create a temporary instance to get the properties
        # This is only used for registration, not for actual operations
        instance = cls()

        return {
            "name": instance.name,
            "supports_mcp_global_config": instance.supports_mcp_global_config,
            "supports_mcp_project_config": instance.supports_mcp_project_config,
            "supports_hooks": instance.supports_hooks,
            "global_config_paths": instance.global_mcp_config_paths,
            "project_config_paths": instance.project_mcp_config_paths,
            "global_hook_paths": instance.global_hook_config_paths,
            "project_hook_paths": instance.project_hook_config_paths,
            "app_names": instance.app_names,
            "commands": instance.commands,
            "config_dirs": instance.config_dirs,
        }


class CursorConfig(IDEConfig):
    """Configuration for Cursor IDE."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        super().__init__(api_key, is_global)
        self.name = "Cursor"

        # Configuration paths
        self.global_mcp_config_paths = [Path("~/.cursor/mcp.json")]
        self.project_mcp_config_paths = [Path(".cursor/mcp.json")]

        # Instructions configuration
        self.instructions_file_name = "zenable.mdc"
        self.instructions_file_path = (
            None  # Will be determined by get_instructions_path
        )

        # IDE detection
        self.app_names = ["Cursor"]
        self.commands = ["cursor"]
        self.config_dirs = [".cursor"]

        # Version checking (cursor doesn't have a consistent --version flag)
        self.version_command = None

        # Validation model
        self._validation_model = _ZenableMCPConfig

    def get_instructions_path(self) -> Path:
        """Get the path where the instructions file should be created for Cursor."""
        if not self.instructions_file_name:
            raise InstructionsFileNotFoundError(self.name)

        if self.is_global:
            return Path.home() / ".cursor" / "rules" / self.instructions_file_name
        else:
            git_root = find_git_root()
            if git_root:
                return git_root / ".cursor" / "rules" / self.instructions_file_name
            else:
                return Path(".cursor") / "rules" / self.instructions_file_name

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup, add these user rules to Cursor:

1. Open Cursor Settings (Cmd+, on Mac, Ctrl+, on Windows/Linux)
2. Navigate to "Rules" section
3. Add the following rules:

{DEFAULT_ZENABLE_INSTRUCTIONS}
Note: A 'zenable.mdc' file has been created in {self.get_instructions_location_description()} with the same rules.
"""


class WindsurfConfig(IDEConfig):
    """Configuration for Windsurf IDE."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool | None = None):
        # Default is_global to True for Windsurf since it only supports global
        if is_global is None:
            is_global = True
        elif is_global is False:
            # If explicitly set to False, raise error
            raise ProjectConfigNotSupportedError(
                "Windsurf",
                "Windsurf only supports global configuration.\n"
                "Please use --global flag for Windsurf installations.",
            )

        super().__init__(api_key, is_global)
        self.name = "Windsurf"

        # Configuration paths
        self.global_mcp_config_paths = [Path("~/.codeium/windsurf/mcp_config.json")]
        self.project_mcp_config_paths = []  # Windsurf doesn't support project configs

        # Instructions configuration
        self.instructions_file_name = "zenable.md"
        self.instructions_file_path = (
            None  # Will be determined by get_instructions_path
        )

        # IDE detection
        self.app_names = ["Windsurf"]
        self.commands = ["windsurf"]
        self.config_dirs = [".codeium/windsurf"]

        # Validation model
        self._validation_model = _ZenableMCPConfig

    def is_installed(self) -> bool:
        """Check if Windsurf is installed."""
        return (
            is_ide_installed(
                app_names=self.app_names,
                commands=self.commands,
                config_dirs=self.config_dirs,
            )
            or (Path.home() / ".codeium" / "windsurf" / "mcp_config.json").exists()
        )

    def get_instructions_path(self) -> Path:
        """Get the path where the instructions file should be created for Windsurf."""
        if not self.instructions_file_name:
            raise InstructionsFileNotFoundError(self.name)

        if self.is_global:
            return Path.home() / ".windsurf" / "rules" / self.instructions_file_name
        else:
            raise ProjectConfigNotSupportedError(
                "Windsurf",
                "Windsurf only supports global configuration.\n"
                "Please use --global flag for Windsurf installations.",
            )

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup:

1. Restart Windsurf or refresh the plugin list
2. Add these rules to Windsurf (either global or project-specific):

{DEFAULT_ZENABLE_INSTRUCTIONS}
Note: A 'zenable.md' file has been created in {self.get_instructions_location_description()} with the same rules.
"""


class KiroConfig(IDEConfig):
    """Configuration for Kiro IDE."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        super().__init__(api_key, is_global)
        self.name = "Kiro"

        # Configuration paths
        self.global_mcp_config_paths = [Path("~/.kiro/settings/mcp.json")]
        self.project_mcp_config_paths = [Path(".kiro/settings/mcp.json")]

        # Instructions configuration
        self.instructions_file_name = "requirements.md"
        self.instructions_file_path = (
            None  # Will be determined by get_instructions_path
        )

        # IDE detection
        self.app_names = ["Kiro"]
        self.commands = ["kiro"]
        self.config_dirs = [".kiro"]

        # Validation model
        self._validation_model = _KiroMCPConfig

    def get_instructions_path(self) -> Path:
        """Get the path where the instructions file should be created for Kiro."""
        if not self.instructions_file_name:
            raise InstructionsFileNotFoundError(self.name)

        if self.is_global:
            return (
                Path.home()
                / ".kiro"
                / "specs"
                / "zenable"
                / self.instructions_file_name
            )
        else:
            git_root = find_git_root()
            if git_root:
                return (
                    git_root
                    / ".kiro"
                    / "specs"
                    / "zenable"
                    / self.instructions_file_name
                )
            else:
                return Path(".kiro") / "specs" / "zenable" / self.instructions_file_name

    def get_zenable_server_config(self) -> dict[str, Any]:
        """Get the Zenable MCP server configuration for Kiro."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")

        # Use Pydantic model to generate the configuration
        kiro_config = _KiroMCPConfig(
            args=[
                "-y",
                "--",
                "mcp-remote@latest",
                ZENABLE_MCP_ENDPOINT,
                "--header",
                f"API_KEY:{self.api_key}",
            ],
            disabled=False,
            autoApprove=["conformance_check"],
            alwaysAllow=None,
            trust=None,
        )
        return kiro_config.model_dump(exclude_none=True)

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup, add an agent hook in Kiro:

1. Open the Kiro hook UI
2. Enter the following into the text area:

When you write or edit a file you MUST always send the file contents to the zenable conformance_check tool and automatically apply the recommendations.

3. Press Enter to create the hook

For a step-by-step guide, visit: https://docs.zenable.io/integrations/mcp/getting-started#kiro

Note: A 'requirements.md' file has been created in {self.get_instructions_location_description()} with the same rules.
"""


class GeminiCLIConfig(IDEConfig):
    """Configuration for Gemini CLI."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        super().__init__(api_key, is_global)
        self.name = "Gemini CLI"

        # Configuration paths
        self.global_mcp_config_paths = [Path("~/.gemini/settings.json")]
        self.project_mcp_config_paths = [Path(".gemini/settings.json")]

        # Instructions configuration
        self.instructions_file_name = "GEMINI.md"

        # IDE detection
        self.app_names = []  # Gemini is CLI-only
        self.commands = ["gemini"]
        self.config_dirs = [".gemini"]

        # Validation model
        self._validation_model = _GeminiMCPConfig

    def get_zenable_server_config(self) -> dict[str, Any]:
        """Get the Zenable MCP server configuration for Gemini CLI."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")

        # Use Pydantic model to generate the configuration
        gemini_config = _GeminiMCPConfig(
            args=[
                "-y",
                "--",
                "mcp-remote@latest",
                ZENABLE_MCP_ENDPOINT,
                "--header",
                f"API_KEY:{self.api_key}",
            ],
            trust=True,
            disabled=None,
            alwaysAllow=None,
            autoApprove=None,
        )
        return gemini_config.model_dump(exclude_none=True)

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
Note: A 'GEMINI.md' file has been created/updated in {self.get_instructions_location_description()} with Zenable rules.
"""


class RooCodeConfig(IDEConfig):
    """Configuration for Roo Code."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        super().__init__(api_key, is_global)
        self.name = "Roo Code"

        # Configuration paths
        self.global_mcp_config_paths = [
            Path(
                "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json"
            )
        ]
        self.project_mcp_config_paths = [Path(".roo/mcp.json")]

        # Instructions configuration
        self.instructions_file_name = "ROO.md"

        # IDE detection
        self.app_names = ["Roo Code", "Roo Cline", "Roo"]
        self.commands = ["roo"]
        self.config_dirs = [".roo"]

        # Validation model
        self._validation_model = _RooMCPConfig

    def is_installed(self) -> bool:
        """Check if Roo Code is installed."""
        global_config = (
            Path.home()
            / "Library"
            / "Application Support"
            / "Code"
            / "User"
            / "globalStorage"
            / "rooveterinaryinc.roo-cline"
            / "settings"
            / "mcp_settings.json"
        )
        return (
            is_ide_installed(
                app_names=self.app_names,
                commands=self.commands,
                config_dirs=self.config_dirs,
            )
            or global_config.exists()
        )

    def get_zenable_server_config(self) -> dict[str, Any]:
        """Get the Zenable MCP server configuration for Roo Code."""
        if not self.api_key:
            raise ValueError("API key is required for MCP server configuration")

        # Use Pydantic model to generate the configuration
        roo_config = _RooMCPConfig(
            args=[
                "-y",
                "--",
                "mcp-remote@latest",
                ZENABLE_MCP_ENDPOINT,
                "--header",
                f"API_KEY:{self.api_key}",
            ],
            disabled=False,
            alwaysAllow=["conformance_check"],
            autoApprove=None,
            trust=None,
        )
        return roo_config.model_dump(exclude_none=True)

    def get_rules_file_path(self) -> Path:
        """Get the path to the Roo rules file."""
        if self.is_global:
            return Path.home() / ".roo" / "rules" / "requirements.md"
        else:
            git_root = find_git_root()
            if git_root:
                return git_root / ".roo" / "rules" / "requirements.md"
            else:
                return Path(".roo") / "rules" / "requirements.md"

    def install(
        self, overwrite: bool = False, skip_comment_warning: bool = False
    ) -> Path:
        """Install the Zenable MCP configuration and create rules files."""
        # First do the normal installation (includes ROO.md)
        config_path = super().install(overwrite, skip_comment_warning)

        # Also create .roo/rules/requirements.md for Roo-specific rules
        rules_file = self.get_rules_file_path()

        if not rules_file.exists():
            rules_file.parent.mkdir(parents=True, exist_ok=True)
            safe_write_text(rules_file, self.instructions_content)
        else:
            # Append to existing file if zenable rules aren't already there
            existing_content = rules_file.read_text()
            if "zenable conformance_check" not in existing_content:
                # Add a newline if file doesn't end with one
                if existing_content and not existing_content.endswith("\n"):
                    existing_content += "\n"
                existing_content += "\n" + self.instructions_content
                safe_write_text(rules_file, existing_content)

        return config_path

    def get_post_install_instructions(self) -> Optional[str]:
        instructions_path = self.get_instructions_path()
        rules_path = self.get_rules_file_path()
        return f"""
Note: Zenable rules have been added to:
- {instructions_path}
- {rules_path}
"""


class ClaudeCodeConfig(IDEConfig):
    """Configuration for Claude Code."""

    # Class variable to track if version warning has been shown
    _version_warning_shown = False

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        super().__init__(api_key, is_global)
        self.name = "Claude Code"

        # Configuration paths
        self.global_mcp_config_paths = [Path("~/.claude/mcp.json")]
        self.project_mcp_config_paths = [Path(".claude/mcp.json")]
        self.global_hook_config_paths = [Path("~/.claude/settings.json")]
        self.project_hook_config_paths = [Path(".claude/settings.json")]

        # Instructions configuration
        self.instructions_file_name = "CLAUDE.md"

        # IDE detection
        self.app_names = []  # Claude Code is CLI-only
        self.commands = ["claude-code", "claude"]
        self.config_dirs = [".claude"]

        # Version checking
        version_cmd = shutil.which("claude")
        if version_cmd:
            self.version_command = Path(version_cmd)
        else:
            self.version_command = None
        self.version_args = ["--version"]
        self.version_pattern = (
            r"(\d+\.\d+\.\d+)"  # Extracts "1.0.58" from "1.0.58 (Claude Code)"
        )
        self.minimum_version = "1.0.58"

        # Validation model
        self._validation_model = _ZenableMCPConfig

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup:

1. Restart Claude Code or reload the MCP configuration
2. Consider using the zenable-mcp hook installation for automatic conformance checking:
   zenable-mcp install hook claude

Note: A 'CLAUDE.md' file has been created in {self.get_instructions_location_description()} with Zenable rules.
"""


class VSCodeConfig(IDEConfig):
    """Configuration for Visual Studio Code."""

    def __init__(self, api_key: Optional[str] = None, is_global: bool = False):
        super().__init__(api_key, is_global)
        self.name = "VS Code"

        # Configuration paths
        self.global_mcp_config_paths = [
            Path("~/Library/Application Support/Code/User/mcp.json")
        ]
        self.project_mcp_config_paths = [Path(".vscode/mcp.json")]

        # Instructions configuration
        self.instructions_file_name = None  # VS Code uses custom path
        self.instructions_file_path = Path(".github/copilot-instructions.md")

        # IDE detection
        self.app_names = ["Visual Studio Code", "Code", "VSCode"]
        self.commands = ["code"]
        self.config_dirs = [".vscode"]

        # Validation model
        self._validation_model = _VSCodeMCPServerConfig

    def get_zenable_server_config(self) -> dict[str, Any]:
        """Get the Zenable MCP server configuration for VS Code."""
        return {
            "type": "sse",
            "url": ZENABLE_MCP_ENDPOINT,
            "headers": {"API_KEY": "${input:zenable-api-key}"},
        }

    def is_config_compatible(self, existing_config: dict[str, Any]) -> bool:
        """Check if an existing configuration is compatible with what would be installed."""
        # VS Code uses 'servers' instead of 'mcpServers'
        if "servers" not in existing_config:
            return False

        # Check if zenable server exists
        if "zenable" not in existing_config["servers"]:
            return False

        zenable_config = existing_config["servers"]["zenable"]

        # Get the validation model for this IDE
        model_class = self.get_validation_model()

        try:
            # Validate the zenable config using the IDE-specific Pydantic model
            model_class.model_validate(zenable_config)
            return True
        except (ValidationError, ValueError, TypeError, AttributeError):
            return False

    def install(
        self, overwrite: bool = False, skip_comment_warning: bool = False
    ) -> Path:
        """Install the Zenable MCP configuration for VS Code."""
        config_path = self.find_config_file()
        if config_path is None:
            config_path = self.get_default_config_path()
            existing_config = {"servers": {}, "inputs": []}
            has_comments = False
        else:
            existing_config, has_comments = load_json_config(config_path)
            # Ensure the structure has servers and inputs keys
            if "servers" not in existing_config:
                existing_config["servers"] = {}
            if "inputs" not in existing_config:
                existing_config["inputs"] = []

            if has_comments and not skip_comment_warning:
                backup_path = backup_config_file(config_path)
                echo(
                    click.style("\n⚠️  Warning: ", fg="yellow", bold=True)
                    + f"The file {config_path} contains comments or JSON5 features.\n"
                    "These comments will be LOST when the file is saved.\n"
                    f"\nA backup has been created at: {backup_path}"
                )

                if not click.confirm(
                    "Do you want to proceed with the modification?", default=False
                ):
                    echo("Installation cancelled")
                    sys.exit(ExitCode.USER_INTERRUPT)

        server_config = self.get_zenable_server_config()

        # Add input variable for API key if not already present
        if "inputs" not in existing_config:
            existing_config["inputs"] = []

        # Check if zenable-api-key input already exists
        zenable_input_exists = any(
            input_item.get("id") == "zenable-api-key"
            for input_item in existing_config["inputs"]
        )

        if not zenable_input_exists:
            zenable_input = {
                "type": "promptString",
                "id": "zenable-api-key",
                "description": "Zenable API Key",
                "password": True,
            }
            existing_config["inputs"].append(zenable_input)

        # Use 'servers' key for VS Code, not 'mcpServers'
        if "zenable" in existing_config.get("servers", {}) and not overwrite:
            # Server already exists and overwrite is False
            return config_path

        existing_config["servers"]["zenable"] = server_config

        self.manager.save_json_config(
            config_path, existing_config, backup=not has_comments
        )

        if self.instructions_file_name or self.instructions_file_path:
            self.install_instructions_file()

        return config_path

    def get_post_install_instructions(self) -> Optional[str]:
        return f"""
To complete the setup:

1. Restart VS Code
2. Hit Cmd+Shift+P (Ctrl+Shift+P on Windows/Linux), type "MCP: List Servers" and hit enter, select "Zenable", then click "Start Server"
3. Enter your Zenable API key when prompted
4. When prompted, you'll need to select "Trust" for the MCP server Zenable (https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_mcp-server-trust)
5. Make sure your Copilot pane is in Agent or Edit mode (https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_use-mcp-tools-in-agent-mode)

Note: Zenable rules have been added to {self.get_instructions_location_description()}.
"""


IDE_CONFIGS = {
    "cursor": CursorConfig,
    "windsurf": WindsurfConfig,
    "kiro": KiroConfig,
    "gemini": GeminiCLIConfig,
    "roo": RooCodeConfig,
    "claude-code": ClaudeCodeConfig,
    "vscode": VSCodeConfig,
}

# Reverse lookup: class -> name
IDE_CLASS_TO_NAME = {v: k for k, v in IDE_CONFIGS.items()}


def create_ide_config(
    ide_name: str, api_key: Optional[str] = None, is_global: bool = False
) -> IDEConfig:
    """Create or get an IDE configuration instance from the registry."""
    registry = IDERegistry()
    config = registry.get_ide(ide_name, api_key, is_global)
    if config is None:
        raise ValueError(
            f"Unsupported IDE: {ide_name}. Supported IDEs: {', '.join(get_supported_ides())}"
        )
    return config


def get_ides_supporting_global() -> list[str]:
    """Get list of IDEs that support global MCP configuration."""
    registry = IDERegistry()
    result = []
    for ide_name in IDE_CONFIGS.keys():
        # Get or create instance from registry
        instance = registry.get_ide(ide_name, None, False)
        if instance and instance.supports_mcp_global_config:
            result.append(ide_name)
    return result


def get_ides_supporting_project() -> list[str]:
    """Get list of IDEs that support project-level MCP configuration."""
    registry = IDERegistry()
    result = []
    for ide_name in IDE_CONFIGS.keys():
        # Get or create instance from registry
        instance = registry.get_ide(ide_name, None, False)
        if instance and instance.supports_mcp_project_config:
            result.append(ide_name)
    return result


def get_ides_supporting_hooks() -> list[str]:
    """Get list of IDEs that support hooks."""
    registry = IDERegistry()
    result = []
    for ide_name in IDE_CONFIGS.keys():
        # Get or create instance from registry
        instance = registry.get_ide(ide_name, None, False)
        if instance and instance.supports_hooks:
            result.append(ide_name)
    return result


def count_ides_supporting(
    mcp_global_config: bool | None = None,
    mcp_project_config: bool | None = None,
    hooks: bool | None = None,
) -> int:
    """Count IDEs supporting specific capabilities.

    Args:
        mcp_global_config: If True, count IDEs supporting global MCP config
        mcp_project_config: If True, count IDEs supporting project MCP config
        hooks: If True, count IDEs supporting hooks

    Returns:
        Number of IDEs matching all specified criteria
    """
    registry = IDERegistry()
    count = 0

    for ide_name in IDE_CONFIGS.keys():
        # Get or create instance from registry
        instance = registry.get_ide(ide_name, None, False)
        if not instance:
            continue

        matches = True

        if (
            mcp_global_config is not None
            and instance.supports_mcp_global_config != mcp_global_config
        ):
            matches = False

        if (
            mcp_project_config is not None
            and instance.supports_mcp_project_config != mcp_project_config
        ):
            matches = False

        if hooks is not None and instance.supports_hooks != hooks:
            matches = False

        if matches:
            count += 1

    return count


class IDERegistry:
    """Singleton registry for IDE configurations."""

    _instance = None
    _lock = threading.Lock()
    # Class-level cache for IDE instances
    _ide_instances: dict[tuple[str, Optional[str], bool], IDEConfig] = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.ide_configs = IDE_CONFIGS
        return cls._instance

    def get_ide(
        self, name: str, api_key: Optional[str] = None, is_global: bool = False
    ) -> Optional[IDEConfig]:
        """Get an IDE configuration by name, creating it if necessary.

        Args:
            name: IDE name (case insensitive)
            api_key: Optional API key for the configuration
            is_global: Whether this is a global configuration

        Returns:
            IDEConfig instance or None if not found (including when IDE doesn't support the requested mode)
        """
        ide_name_lower = name.lower()
        ide_class = self.ide_configs.get(ide_name_lower)
        if not ide_class:
            return None

        # Use cache key to get or create instance
        cache_key = (ide_name_lower, api_key, is_global)
        if cache_key not in IDERegistry._ide_instances:
            try:
                IDERegistry._ide_instances[cache_key] = ide_class(api_key, is_global)
            except ProjectConfigNotSupportedError:
                # This IDE doesn't support project-level config with is_global=False
                return None
            except GlobalConfigNotSupportedError:
                # This IDE doesn't support global config with is_global=True
                return None
        return IDERegistry._ide_instances[cache_key]

    def get_installed_ides(self) -> list[str]:
        """Get list of installed IDE names."""
        installed = []
        for ide_name in self.ide_configs.keys():
            # Get or create instance with no api_key and is_global=False for checking
            instance = self.get_ide(ide_name, None, False)
            if instance and instance.is_installed():
                installed.append(ide_name)
        return installed

    def get_registered_ides(self) -> list[str]:
        """Get all registered IDE names."""
        return list(self.ide_configs.keys())


# Helper functions that use the registry
def get_supported_ides() -> list[str]:
    """Get list of supported IDE names."""
    return list(IDE_CONFIGS.keys())
