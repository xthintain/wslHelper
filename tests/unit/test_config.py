"""Unit tests for Configuration validation.

Tests configuration validation, serialization, and deserialization.
"""

import pytest
from src.utils.config import Configuration, ConfigManager
from pathlib import Path
import tempfile
import json


class TestConfiguration:
    """Test cases for Configuration class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = Configuration()

        assert config.hotkey == "ctrl+alt+a"
        assert config.save_directory == "E:\\tmp\\screenshots"
        assert config.image_format == "jpg"
        assert config.image_quality == 90
        assert config.auto_startup is True
        assert config.show_notification is True
        assert config.auto_cleanup is False
        assert config.cleanup_days == 7

    def test_validate_valid_configuration(self):
        """Test validation passes for valid configuration."""
        config = Configuration()
        errors = config.validate()

        assert len(errors) == 0

    def test_validate_empty_hotkey(self):
        """Test validation fails for empty hotkey."""
        config = Configuration(hotkey="")
        errors = config.validate()

        assert len(errors) > 0
        assert any("hotkey" in err for err in errors)

    def test_validate_empty_save_directory(self):
        """Test validation fails for empty save directory."""
        config = Configuration(save_directory="")
        errors = config.validate()

        assert len(errors) > 0
        assert any("save_directory" in err for err in errors)

    def test_validate_invalid_image_quality_low(self):
        """Test validation fails for quality < 1."""
        config = Configuration(image_quality=0)
        errors = config.validate()

        assert len(errors) > 0
        assert any("image_quality" in err for err in errors)

    def test_validate_invalid_image_quality_high(self):
        """Test validation fails for quality > 100."""
        config = Configuration(image_quality=101)
        errors = config.validate()

        assert len(errors) > 0
        assert any("image_quality" in err for err in errors)

    def test_validate_invalid_cleanup_days(self):
        """Test validation fails for cleanup_days <= 0."""
        config = Configuration(cleanup_days=0)
        errors = config.validate()

        assert len(errors) > 0
        assert any("cleanup_days" in err for err in errors)

    def test_validate_invalid_image_format(self):
        """Test validation fails for invalid image format."""
        # This will fail at type level, but we test the validation
        config = Configuration()
        config.image_format = "bmp"  # Invalid format
        errors = config.validate()

        assert len(errors) > 0

    def test_to_dict(self):
        """Test configuration serialization to dict."""
        config = Configuration(
            hotkey="ctrl+shift+s", save_directory="D:\\screenshots", image_quality=85
        )

        data = config.to_dict()

        assert data["hotkey"] == "ctrl+shift+s"
        assert data["save_directory"] == "D:\\screenshots"
        assert data["image_quality"] == 85
        assert isinstance(data, dict)

    def test_from_dict(self):
        """Test configuration deserialization from dict."""
        data = {
            "hotkey": "ctrl+shift+s",
            "save_directory": "D:\\screenshots",
            "image_format": "png",
            "image_quality": 85,
            "auto_startup": False,
            "show_notification": False,
            "auto_cleanup": True,
            "cleanup_days": 30,
        }

        config = Configuration.from_dict(data)

        assert config.hotkey == "ctrl+shift+s"
        assert config.save_directory == "D:\\screenshots"
        assert config.image_format == "png"
        assert config.image_quality == 85
        assert config.auto_startup is False
        assert config.show_notification is False
        assert config.auto_cleanup is True
        assert config.cleanup_days == 30

    def test_from_dict_filters_unknown_keys(self):
        """Test that from_dict filters out unknown keys."""
        data = {
            "hotkey": "ctrl+alt+a",
            "unknown_key": "should be ignored",
            "another_unknown": 123,
        }

        config = Configuration.from_dict(data)

        assert config.hotkey == "ctrl+alt+a"
        assert not hasattr(config, "unknown_key")

    def test_roundtrip_serialization(self):
        """Test that to_dict and from_dict are reversible."""
        original = Configuration(hotkey="ctrl+alt+s", image_quality=75, cleanup_days=14)

        data = original.to_dict()
        restored = Configuration.from_dict(data)

        assert restored.hotkey == original.hotkey
        assert restored.image_quality == original.image_quality
        assert restored.cleanup_days == original.cleanup_days


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_load_config_creates_default_if_missing(self, tmp_path, monkeypatch):
        """Test that load_config creates default config if file doesn't exist."""
        # Mock the config directory
        monkeypatch.setattr(ConfigManager, "_config_dir", tmp_path)
        monkeypatch.setattr(ConfigManager, "_config_file", tmp_path / "config.json")
        monkeypatch.setattr(ConfigManager, "_backup_file", tmp_path / "config.json.bak")

        config = ConfigManager.load_config()

        assert config.hotkey == "ctrl+alt+a"  # Default value
        assert (tmp_path / "config.json").exists()

    def test_save_config_creates_file(self, tmp_path, monkeypatch):
        """Test that save_config creates config file."""
        monkeypatch.setattr(ConfigManager, "_config_dir", tmp_path)
        monkeypatch.setattr(ConfigManager, "_config_file", tmp_path / "config.json")
        monkeypatch.setattr(ConfigManager, "_backup_file", tmp_path / "config.json.bak")

        config = Configuration(hotkey="ctrl+shift+s", image_quality=80)
        ConfigManager.save_config(config)

        assert (tmp_path / "config.json").exists()

        # Verify content
        with open(tmp_path / "config.json", "r") as f:
            data = json.load(f)
            assert data["hotkey"] == "ctrl+shift+s"
            assert data["image_quality"] == 80

    def test_save_config_creates_backup(self, tmp_path, monkeypatch):
        """Test that save_config creates backup of existing config."""
        monkeypatch.setattr(ConfigManager, "_config_dir", tmp_path)
        config_file = tmp_path / "config.json"
        backup_file = tmp_path / "config.json.bak"
        monkeypatch.setattr(ConfigManager, "_config_file", config_file)
        monkeypatch.setattr(ConfigManager, "_backup_file", backup_file)

        # Create initial config
        config1 = Configuration(hotkey="ctrl+alt+a")
        ConfigManager.save_config(config1)

        # Save new config
        config2 = Configuration(hotkey="ctrl+shift+s")
        ConfigManager.save_config(config2)

        # Backup should exist
        assert backup_file.exists()

    def test_save_config_validates_before_saving(self, tmp_path, monkeypatch):
        """Test that save_config validates configuration before saving."""
        monkeypatch.setattr(ConfigManager, "_config_dir", tmp_path)
        monkeypatch.setattr(ConfigManager, "_config_file", tmp_path / "config.json")

        # Invalid configuration
        config = Configuration(hotkey="", image_quality=0)

        with pytest.raises(ValueError) as exc_info:
            ConfigManager.save_config(config)

        assert "validation failed" in str(exc_info.value).lower()

    def test_load_config_from_existing_file(self, tmp_path, monkeypatch):
        """Test loading configuration from existing file."""
        monkeypatch.setattr(ConfigManager, "_config_dir", tmp_path)
        config_file = tmp_path / "config.json"
        monkeypatch.setattr(ConfigManager, "_config_file", config_file)

        # Create config file
        data = {
            "hotkey": "ctrl+shift+s",
            "save_directory": "D:\\screenshots",
            "image_format": "png",
            "image_quality": 95,
            "auto_startup": False,
            "show_notification": True,
            "auto_cleanup": False,
            "cleanup_days": 7,
        }

        with open(config_file, "w") as f:
            json.dump(data, f)

        # Load config
        config = ConfigManager.load_config()

        assert config.hotkey == "ctrl+shift+s"
        assert config.image_format == "png"
        assert config.image_quality == 95

    def test_load_config_restores_from_backup_on_corruption(
        self, tmp_path, monkeypatch
    ):
        """Test that load_config restores from backup if main file is corrupted."""
        monkeypatch.setattr(ConfigManager, "_config_dir", tmp_path)
        config_file = tmp_path / "config.json"
        backup_file = tmp_path / "config.json.bak"
        monkeypatch.setattr(ConfigManager, "_config_file", config_file)
        monkeypatch.setattr(ConfigManager, "_backup_file", backup_file)

        # Create corrupted main file
        with open(config_file, "w") as f:
            f.write("{ invalid json }")

        # Create valid backup
        backup_data = {"hotkey": "ctrl+alt+b", "save_directory": "E:\\backup"}
        with open(backup_file, "w") as f:
            json.dump(backup_data, f)

        # Should restore from backup
        config = ConfigManager.load_config()

        assert config.hotkey == "ctrl+alt+b"

    def test_get_config_path(self, tmp_path, monkeypatch):
        """Test getting configuration file path."""
        config_file = tmp_path / "config.json"
        monkeypatch.setattr(ConfigManager, "_config_file", config_file)

        path = ConfigManager.get_config_path()

        assert path == config_file
