"""Windows <-> WSL path conversion module.

Provides static methods for converting between Windows and WSL path formats,
handling drive letter mapping and path separator conversion.
"""

import re
from pathlib import PureWindowsPath, PurePosixPath


class PathConverter:
    """Static class for Windows <-> WSL path conversion."""

    @staticmethod
    def windows_to_wsl(windows_path: str) -> str:
        """Convert Windows path to WSL format.

        Converts Windows path format (E:\\tmp\\file.jpg) to WSL format
        (/mnt/e/tmp/file.jpg).

        Args:
            windows_path: Windows format path (e.g., "E:\\tmp\\file.jpg")

        Returns:
            WSL format path (e.g., "/mnt/e/tmp/file.jpg")

        Raises:
            ValueError: If path format is invalid
        """
        if not windows_path:
            raise ValueError("Path cannot be empty")

        # Validate Windows path format
        if not re.match(r"^[A-Za-z]:[\\]", windows_path):
            raise ValueError(f"Invalid Windows path format: {windows_path}")

        try:
            # Parse Windows path
            path_obj = PureWindowsPath(windows_path)

            # Extract drive letter (convert to lowercase)
            drive = path_obj.drive.rstrip(":").lower()

            # Get path parts (excluding drive)
            parts = path_obj.parts[1:]  # Skip drive part

            # Build WSL path
            if parts:
                wsl_path = f"/mnt/{drive}/" + "/".join(parts)
            else:
                wsl_path = f"/mnt/{drive}/"

            return wsl_path

        except Exception as e:
            raise ValueError(f"Failed to convert Windows path: {e}")

    @staticmethod
    def wsl_to_windows(wsl_path: str) -> str:
        """Convert WSL path to Windows format.

        Converts WSL path format (/mnt/e/tmp/file.jpg) to Windows format
        (E:\\tmp\\file.jpg).

        Args:
            wsl_path: WSL format path (e.g., "/mnt/e/tmp/file.jpg")

        Returns:
            Windows format path (e.g., "E:\\tmp\\file.jpg")

        Raises:
            ValueError: If path format is invalid
        """
        if not wsl_path:
            raise ValueError("Path cannot be empty")

        # Validate WSL path format
        match = re.match(r"^/mnt/([a-z])/(.*)$", wsl_path)
        if not match:
            raise ValueError(f"Invalid WSL path format: {wsl_path}")

        try:
            drive, path = match.groups()

            # Convert drive letter to uppercase
            drive = drive.upper()

            # Replace forward slashes with backslashes
            windows_path_part = path.replace("/", "\\")

            # Build Windows path
            if windows_path_part:
                windows_path = f"{drive}:\\{windows_path_part}"
            else:
                windows_path = f"{drive}:\\"

            return windows_path

        except Exception as e:
            raise ValueError(f"Failed to convert WSL path: {e}")

    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate if path is valid Windows or WSL format.

        Args:
            path: Path string to validate

        Returns:
            True if valid Windows or WSL path, False otherwise
        """
        if not path:
            return False

        # Check Windows format: starts with drive letter and colon-backslash
        if re.match(r"^[A-Za-z]:[\\]", path):
            return True

        # Check WSL format: /mnt/lowercase-drive-letter/...
        if re.match(r"^/mnt/[a-z]/", path):
            return True

        return False
