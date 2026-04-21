"""
Backward-compatible shim.

The Linux-safe copy now keeps cross-platform helpers in platform_compat.py.
Older imports from windows_compat.py still work by re-exporting them here.
"""
from platform_compat import *  # noqa: F401,F403
