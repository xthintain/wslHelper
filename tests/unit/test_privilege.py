"""Unit tests for PrivilegeManager.

Tests UAC privilege checking and elevation request.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


class TestPrivilegeManager:
    """Test cases for PrivilegeManager class."""

    @patch("src.system.privilege.ctypes")
    def test_check_admin_true(self, mock_ctypes):
        """Test check_admin returns True when running as admin."""
        from src.system.privilege import check_admin

        # Mock IsUserAnAdmin to return non-zero (True)
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 1

        result = check_admin()

        assert result is True

    @patch("src.system.privilege.ctypes")
    def test_check_admin_false(self, mock_ctypes):
        """Test check_admin returns False when not running as admin."""
        from src.system.privilege import check_admin

        # Mock IsUserAnAdmin to return zero (False)
        mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = 0

        result = check_admin()

        assert result is False

    @patch("src.system.privilege.ctypes")
    def test_check_admin_exception(self, mock_ctypes):
        """Test check_admin handles exceptions gracefully."""
        from src.system.privilege import check_admin

        # Simulate exception
        mock_ctypes.windll.shell32.IsUserAnAdmin.side_effect = Exception("Access error")

        result = check_admin()

        assert result is False

    @patch("src.system.privilege.ctypes")
    @patch("src.system.privilege.check_admin")
    @patch("src.system.privilege.sys")
    def test_request_admin_already_admin(self, mock_sys, mock_check_admin, mock_ctypes):
        """Test request_admin when already running as admin."""
        from src.system.privilege import request_admin

        # Already admin
        mock_check_admin.return_value = True

        result = request_admin()

        # Should return None (no need to elevate)
        assert result is None
        mock_ctypes.windll.shell32.ShellExecuteW.assert_not_called()

    @patch("src.system.privilege.ctypes")
    @patch("src.system.privilege.check_admin")
    @patch("src.system.privilege.sys")
    @patch("src.system.privilege.getattr")
    def test_request_admin_elevation_success(
        self, mock_getattr, mock_sys, mock_check_admin, mock_ctypes
    ):
        """Test successful elevation request."""
        from src.system.privilege import request_admin

        # Not admin
        mock_check_admin.return_value = False

        # Mock sys.argv
        mock_sys.argv = ["app.py", "--arg1"]
        mock_sys.executable = "python.exe"

        # Not frozen (running as script)
        mock_getattr.return_value = False

        # Mock successful elevation (return > 32)
        mock_ctypes.windll.shell32.ShellExecuteW.return_value = 42

        # Should call sys.exit(0)
        with pytest.raises(SystemExit) as exc_info:
            request_admin()

        assert exc_info.value.code == 0
        mock_ctypes.windll.shell32.ShellExecuteW.assert_called_once()

    @patch("src.system.privilege.ctypes")
    @patch("src.system.privilege.check_admin")
    @patch("src.system.privilege.sys")
    @patch("src.system.privilege.getattr")
    def test_request_admin_elevation_failure(
        self, mock_getattr, mock_sys, mock_check_admin, mock_ctypes
    ):
        """Test failed elevation request."""
        from src.system.privilege import request_admin

        # Not admin
        mock_check_admin.return_value = False

        mock_sys.argv = ["app.py"]
        mock_sys.executable = "python.exe"
        mock_getattr.return_value = False

        # Mock failed elevation (return <= 32)
        mock_ctypes.windll.shell32.ShellExecuteW.return_value = 5  # ERROR_ACCESS_DENIED

        result = request_admin()

        # Should return error code
        assert result == 5

    @patch("src.system.privilege.ctypes")
    @patch("src.system.privilege.check_admin")
    @patch("src.system.privilege.sys")
    @patch("src.system.privilege.getattr")
    def test_request_admin_frozen_executable(
        self, mock_getattr, mock_sys, mock_check_admin, mock_ctypes
    ):
        """Test elevation request for frozen executable."""
        from src.system.privilege import request_admin

        mock_check_admin.return_value = False

        # Mock frozen executable
        mock_sys.executable = "C:\\app\\WSLScreenshot.exe"
        mock_sys.argv = ["WSLScreenshot.exe"]
        mock_getattr.return_value = True  # sys.frozen = True

        mock_ctypes.windll.shell32.ShellExecuteW.return_value = 42

        with pytest.raises(SystemExit):
            request_admin()

        # Should call ShellExecuteW with executable path
        call_args = mock_ctypes.windll.shell32.ShellExecuteW.call_args
        assert call_args is not None

    @patch("src.system.privilege.check_admin")
    def test_is_elevated_same_as_check_admin(self, mock_check_admin):
        """Test that is_elevated is same as check_admin."""
        from src.system.privilege import is_elevated

        mock_check_admin.return_value = True

        result = is_elevated()

        assert result is True
        mock_check_admin.assert_called_once()

    @patch("src.system.privilege.ctypes")
    @patch("src.system.privilege.check_admin")
    @patch("src.system.privilege.sys")
    def test_request_admin_exception_handling(
        self, mock_sys, mock_check_admin, mock_ctypes
    ):
        """Test exception handling in request_admin."""
        from src.system.privilege import request_admin

        mock_check_admin.return_value = False
        mock_sys.argv = ["app.py"]

        # Simulate exception during elevation
        mock_ctypes.windll.shell32.ShellExecuteW.side_effect = Exception(
            "Elevation error"
        )

        result = request_admin()

        # Should return error code 1
        assert result == 1
