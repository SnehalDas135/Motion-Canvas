"""
platform_compat.py
Shared runtime helpers for macOS, Linux, and Windows.

The original project had a Windows-focused shim. This module expands that
behavior so the Linux copy can choose the correct native library, webcam
backend, and screen sizing logic without hard-coding macOS assumptions.
"""
import ctypes
import os
import platform

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def get_engine_lib_name() -> str:
    """Return the correct native library filename for this OS."""
    if IS_WINDOWS:
        return "engine.dll"
    if IS_MACOS:
        return "engine.dylib"
    return "engine.so"


def get_webcam_backend():
    """Return the most compatible OpenCV capture backend for this OS."""
    import cv2

    if IS_WINDOWS:
        return cv2.CAP_DSHOW
    if IS_LINUX and hasattr(cv2, "CAP_V4L2"):
        return cv2.CAP_V4L2
    return cv2.CAP_ANY


def has_gui_session() -> bool:
    """Whether a desktop session is available for windows/input hooks."""
    if IS_WINDOWS or IS_MACOS:
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def is_wayland_session() -> bool:
    """Detect Wayland, which can restrict global input control on Linux."""
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    return session == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY"))


def get_screen_size(default: tuple[int, int] = (1920, 1080)) -> tuple[int, int]:
    """
    Best-effort screen size detection.

    Order:
      1. FREEFACE_SCREEN_SIZE env override
      2. screeninfo monitors
      3. tkinter root geometry
      4. conservative default
    """
    override = os.environ.get("FREEFACE_SCREEN_SIZE", "").lower().strip()
    if "x" in override:
        try:
            w, h = override.split("x", 1)
            return int(w), int(h)
        except Exception:
            pass

    try:
        from screeninfo import get_monitors

        monitors = get_monitors()
        if monitors:
            primary = next((m for m in monitors if getattr(m, "is_primary", False)), monitors[0])
            width = int(getattr(primary, "width", 0))
            height = int(getattr(primary, "height", 0))
            if width > 0 and height > 0:
                return width, height
    except Exception:
        pass

    if has_gui_session():
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            if width > 0 and height > 0:
                return int(width), int(height)
        except Exception:
            pass

    return default


def check_admin_windows():
    """
    On Windows, pynput needs elevated privileges to control the mouse
    when certain apps (admin apps, UAC dialogs) are focused.
    """
    if not IS_WINDOWS:
        return
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("[WARN] FreeFace is not running as Administrator.")
            print("       Mouse control may not work over elevated windows (UAC dialogs).")
            print("       For full control: right-click cmd.exe -> Run as Administrator")
    except Exception:
        pass


def print_runtime_notes():
    """Emit non-fatal OS-specific guidance at startup."""
    check_admin_windows()

    if IS_LINUX and not has_gui_session():
        print("[WARN] No Linux GUI session detected.")
        print("       Camera processing can still run, but mouse/keyboard control")
        print("       and the virtual keyboard need an X11/Wayland desktop session.")

    if IS_LINUX and is_wayland_session():
        print("[INFO] Wayland session detected.")
        print("       Some Linux desktops restrict global input injection.")
        print("       If mouse or keyboard control is blocked, try an X11 session")
        print("       or ensure XWayland/input-control permissions are available.")


def get_makefile_command() -> str:
    """Return the correct build command for this OS."""
    if IS_WINDOWS:
        return "build_windows.bat"
    return "make"
