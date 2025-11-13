"""Privilege management module for Windows UAC.

Provides functions to check and request administrator privileges on Windows.
"""

import ctypes
import sys
from typing import Optional


def check_admin() -> bool:
    """Check if the application is running with administrator privileges.

    Returns:
        True if running as administrator, False otherwise
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def request_admin() -> Optional[int]:
    """Request administrator privileges by relaunching the application.

    This function will relaunch the application with elevated privileges
    using Windows UAC dialog. The current process will exit if successful.

    Returns:
        Exit code if relaunch fails, None if successful (process exits)
    """
    if check_admin():
        return None  # Already running as admin

    try:
        # Get the path to the current executable or script
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            script = sys.executable
        else:
            # Running as Python script
            script = sys.argv[0]

        # Build command line arguments
        params = " ".join(sys.argv[1:])

        # Request elevation
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # Request elevation
            sys.executable if not getattr(sys, "frozen", False) else script,
            f'"{script}" {params}' if not getattr(sys, "frozen", False) else params,
            None,
            1,  # SW_SHOWNORMAL
        )

        if ret > 32:
            # Success - exit current process
            sys.exit(0)
        else:
            # Failed to elevate
            return ret

    except Exception as e:
        print(f"Failed to request admin privileges: {e}")
        return 1


def is_elevated() -> bool:
    """Check if the current process is elevated (same as check_admin).

    Returns:
        True if process is elevated, False otherwise
    """
    return check_admin()
