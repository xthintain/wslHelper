"""Single instance checker using file lock.

Ensures only one instance of the application runs at a time.
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    import msvcrt  # Windows file locking
except ImportError:
    msvcrt = None


class SingleInstance:
    """Single instance checker using file lock."""

    def __init__(self, app_name: str = "WSLScreenshot"):
        """Initialize single instance checker.

        Args:
            app_name: Application name for lock file
        """
        self.app_name = app_name
        self._lock_file: Optional[object] = None
        self._lock_path = self._get_lock_path()

    def _get_lock_path(self) -> Path:
        """Get lock file path.

        Returns:
            Path to lock file
        """
        # Use temp directory for lock file
        if sys.platform == "win32":
            temp_dir = Path(os.getenv("TEMP", "C:\\Windows\\Temp"))
        else:
            temp_dir = Path("/tmp")

        return temp_dir / f"{self.app_name}.lock"

    def is_already_running(self) -> bool:
        """Check if another instance is already running.

        Returns:
            True if another instance is running, False otherwise
        """
        try:
            # Try to open the lock file
            self._lock_file = open(self._lock_path, "w")

            if sys.platform == "win32" and msvcrt:
                # Windows: try to lock the file
                try:
                    msvcrt.locking(
                        self._lock_file.fileno(), msvcrt.LK_NBLCK, 1
                    )
                    # Write PID to lock file
                    self._lock_file.write(str(os.getpid()))
                    self._lock_file.flush()
                    return False  # Successfully locked, we're the only instance
                except OSError:
                    # File is locked by another process
                    self._lock_file.close()
                    return True  # Another instance is running
            else:
                # Non-Windows or no msvcrt: use simple file existence check
                # This is less robust but works
                if self._lock_path.exists():
                    # Try to read PID from lock file
                    try:
                        with open(self._lock_path, "r") as f:
                            pid = int(f.read().strip())
                        # Check if process is still running
                        if self._is_process_running(pid):
                            return True  # Another instance is running
                    except (ValueError, IOError):
                        pass

                # Write our PID
                self._lock_file.write(str(os.getpid()))
                self._lock_file.flush()
                return False

        except IOError:
            # Can't create lock file
            return False

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running.

        Args:
            pid: Process ID

        Returns:
            True if process is running, False otherwise
        """
        try:
            # Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def cleanup(self):
        """Cleanup lock file."""
        try:
            if self._lock_file:
                if sys.platform == "win32" and msvcrt:
                    try:
                        msvcrt.locking(
                            self._lock_file.fileno(), msvcrt.LK_UNLCK, 1
                        )
                    except OSError:
                        pass
                self._lock_file.close()

            # Remove lock file
            if self._lock_path.exists():
                self._lock_path.unlink()
        except Exception:
            # Ignore cleanup errors
            pass

    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()
