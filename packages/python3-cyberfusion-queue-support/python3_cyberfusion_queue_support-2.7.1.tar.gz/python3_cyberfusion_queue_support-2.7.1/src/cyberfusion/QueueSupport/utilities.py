"""Utilities."""

import os
import stat


def get_decimal_permissions(path: str) -> int:
    """Get decimal permissions with all bits."""
    return stat.S_IMODE(os.lstat(path).st_mode)
