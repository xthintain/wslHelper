"""Configuration management module.

Handles loading, saving, and validating application configuration with
JSON schema validation and default values.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal, Optional


@dataclass
class Configuration:
    """Application configuration dataclass."""

    hotkey: str = "ctrl+alt+s"
    save_directory: str = "E:\\tmp\\screenshots"
    image_format: Literal["jpg", "png"] = "jpg"
    image_quality: int = 90
    auto_startup: bool = True
    show_notification: bool = True
    auto_cleanup: bool = False
    cleanup_days: int = 7

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.hotkey:
            errors.append("hotkey cannot be empty")

        if not self.save_directory:
            errors.append("save_directory cannot be empty")

        if not (1 <= self.image_quality <= 100):
            errors.append("image_quality must be between 1 and 100")

        if self.cleanup_days <= 0:
            errors.append("cleanup_days must be greater than 0")

        if self.image_format not in ["jpg", "png"]:
            errors.append("image_format must be 'jpg' or 'png'")

        return errors

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Configuration":
        """Create configuration from dictionary.

        Args:
            data: Dictionary with configuration values

        Returns:
            Configuration instance
        """
        # Filter out unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def copy(self) -> "Configuration":
        """Create a copy of this configuration.

        Returns:
            New Configuration instance with same values
        """
        return Configuration.from_dict(self.to_dict())


class ConfigManager:
    """Configuration file manager."""

    _config_dir: Path = Path(os.getenv("APPDATA", "")) / "WSLScreenshot"
    _config_file: Path = _config_dir / "config.json"
    _backup_file: Path = _config_dir / "config.json.bak"

    @classmethod
    def load_config(cls) -> Configuration:
        """Load configuration from file or create default.

        Returns:
            Configuration instance
        """
        # Create config directory if it doesn't exist
        cls._config_dir.mkdir(parents=True, exist_ok=True)

        # If config file doesn't exist, create default
        if not cls._config_file.exists():
            default_config = Configuration()
            cls.save_config(default_config)
            return default_config

        try:
            with open(cls._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Configuration.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            # If config is corrupted, try backup
            if cls._backup_file.exists():
                try:
                    with open(cls._backup_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return Configuration.from_dict(data)
                except (json.JSONDecodeError, IOError):
                    pass

            # If all else fails, return default
            return Configuration()

    @classmethod
    def save_config(cls, config: Configuration) -> None:
        """Save configuration to file with backup.

        Args:
            config: Configuration to save

        Raises:
            ValueError: If configuration validation fails
        """
        # Validate configuration
        errors = config.validate()
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

        # Create config directory if it doesn't exist
        cls._config_dir.mkdir(parents=True, exist_ok=True)

        # Backup existing config if it exists
        if cls._config_file.exists():
            import shutil

            shutil.copy2(cls._config_file, cls._backup_file)

        # Save new config
        with open(cls._config_file, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def get_config_path(cls) -> Path:
        """Get configuration file path.

        Returns:
            Path to configuration file
        """
        return cls._config_file


# Convenience functions
def load_config() -> Configuration:
    """Load configuration from file.

    Returns:
        Configuration instance
    """
    return ConfigManager.load_config()


def save_config(config: Configuration) -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save
    """
    ConfigManager.save_config(config)
