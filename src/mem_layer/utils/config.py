"""Configuration management."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    """Storage configuration."""

    backend: str = "sqlite"
    path: str = "{scope_path}/memory.db"
    auto_save: bool = True
    save_interval: int = 300


class GraphConfig(BaseModel):
    """Graph configuration."""

    default_scope: str = "project"
    max_nodes: int = 10000
    enable_temporal: bool = True


class QueryConfig(BaseModel):
    """Query configuration."""

    default_limit: int = 100
    max_depth: int = 5
    enable_full_text: bool = True


class ConsolidationConfig(BaseModel):
    """Memory consolidation configuration."""

    enabled: bool = True
    interval: str = "daily"
    keep_important: bool = True
    threshold: float = 0.7


class DecayConfig(BaseModel):
    """Memory decay configuration."""

    enabled: bool = True
    half_life: int = 30
    min_importance: float = 0.1


class MemoryConfig(BaseModel):
    """Memory management configuration."""

    consolidation: ConsolidationConfig = Field(default_factory=ConsolidationConfig)
    decay: DecayConfig = Field(default_factory=DecayConfig)


class CLIConfig(BaseModel):
    """CLI configuration."""

    output_format: str = "table"
    color_scheme: str = "auto"


class TUIConfig(BaseModel):
    """TUI configuration."""

    theme: str = "dark"


class WebConfig(BaseModel):
    """Web UI configuration."""

    host: str = "localhost"
    port: int = 8080
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])


class UIConfig(BaseModel):
    """UI configuration."""

    cli: CLIConfig = Field(default_factory=CLIConfig)
    tui: TUIConfig = Field(default_factory=TUIConfig)
    web: WebConfig = Field(default_factory=WebConfig)


class Config(BaseModel):
    """Main configuration."""

    version: str = "1.0"
    storage: StorageConfig = Field(default_factory=StorageConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)
    query: QueryConfig = Field(default_factory=QueryConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """Load configuration from file.

        Configuration is loaded in order of priority:
        1. Provided config_path
        2. Project config (.mem-layer/config.yaml)
        3. User config (~/.mem-layer/config.yaml)
        4. Environment variables (MEM_LAYER_*)
        5. Default config

        Args:
            config_path: Optional path to config file

        Returns:
            Loaded configuration
        """
        # Start with defaults
        config_data: dict[str, Any] = {}

        # Load user config
        user_config_path = Path.home() / ".mem-layer" / "config.yaml"
        if user_config_path.exists():
            with open(user_config_path) as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    config_data.update(user_config)

        # Load project config
        project_config_path = Path.cwd() / ".mem-layer" / "config.yaml"
        if project_config_path.exists():
            with open(project_config_path) as f:
                project_config = yaml.safe_load(f)
                if project_config:
                    config_data.update(project_config)

        # Load specified config
        if config_path and config_path.exists():
            with open(config_path) as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config_data.update(file_config)

        # Override with environment variables
        cls._load_env_vars(config_data)

        return cls(**config_data)

    @classmethod
    def _load_env_vars(cls, config_data: dict[str, Any]) -> None:
        """Load configuration from environment variables.

        Environment variables should be prefixed with MEM_LAYER_
        Example: MEM_LAYER_STORAGE_BACKEND=sqlite

        Args:
            config_data: Configuration dictionary to update
        """
        prefix = "MEM_LAYER_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to nested dict
                config_key = key[len(prefix) :].lower()
                parts = config_key.split("_")

                # Navigate/create nested structure
                current = config_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Set value
                current[parts[-1]] = value

    def save(self, config_path: Path) -> None:
        """Save configuration to file.

        Args:
            config_path: Path to save config file
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "storage.backend")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        parts = key.split(".")
        current = self.model_dump()

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "storage.backend")
            value: Value to set
        """
        parts = key.split(".")
        data = self.model_dump()

        # Navigate to parent
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set value
        current[parts[-1]] = value

        # Recreate config from updated data
        self.__dict__.update(Config(**data).__dict__)
