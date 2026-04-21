"""
os_control.py
Translates Action objects into real OS mouse/keyboard events.
Uses pynput (faster and more reliable than pyautogui).

Thread-safe: all calls can come from any thread.
"""
import threading
import time

try:
    from pynput.mouse import Button, Controller as MouseCtrl
    from pynput.keyboard import Key, Controller as KbCtrl
    _PYNPUT_IMPORT_ERROR = None
except Exception as exc:
    Button = None
    MouseCtrl = None
    Key = None
    KbCtrl = None
    _PYNPUT_IMPORT_ERROR = exc

from engine_bridge import Action, ActionType
from platform_compat import IS_LINUX, has_gui_session, is_wayland_session

class OSController:
    def __init__(self, screen_w: int, screen_h: int):
        if _PYNPUT_IMPORT_ERROR is not None:
            msg = f"pynput is unavailable: {_PYNPUT_IMPORT_ERROR}"
            if IS_LINUX:
                msg += " (Linux input control usually needs an active X11/Wayland desktop session)"
            raise RuntimeError(msg)
        if IS_LINUX and not has_gui_session():
            raise RuntimeError("Linux GUI session not detected; OS input control is unavailable")

        self._mouse   = MouseCtrl()
        self._kb      = KbCtrl()
        self._lock    = threading.Lock()
        self._sw      = screen_w
        self._sh      = screen_h

        # Smooth mouse movement: current position
        self._cur_x   = screen_w  // 2
        self._cur_y   = screen_h  // 2

        # Rate limiting for scroll/click to prevent spam
        self._last_scroll = 0.0
        self._last_click  = 0.0
        self._scroll_gap  = 0.4   # minimum seconds between scroll events
        self._click_gap   = 0.8   # minimum seconds between clicks

        if IS_LINUX and is_wayland_session():
            print("[OS] Wayland detected. If global input control is blocked,")
            print("     log into an X11 session or enable the needed permissions.")

    def execute(self, action: Action):
        """Execute an Action on the OS. Call from any thread."""
        if action.is_none():
            return
        with self._lock:
            self._dispatch(action)

    def _dispatch(self, a: Action):
        now = time.time()

        if a.type == ActionType.MOUSE_MOVE:
            # Convert 0-1 normalized to screen pixels
            tx = int(a.x * self._sw)
            ty = int(a.y * self._sh)
            # Smooth: move 30% toward target per frame (reduces jitter)
            self._cur_x = int(self._cur_x * 0.7 + tx * 0.3)
            self._cur_y = int(self._cur_y * 0.7 + ty * 0.3)
            self._mouse.position = (self._cur_x, self._cur_y)

        elif a.type in (ActionType.LEFT_CLICK, ActionType.DWELL_CLICK):
            if now - self._last_click < self._click_gap:
                return
            self._mouse.click(Button.left)
            self._last_click = now

        elif a.type == ActionType.DOUBLE_CLICK:
            if now - self._last_click < self._click_gap:
                return
            self._mouse.click(Button.left, 2)
            self._last_click = now

        elif a.type == ActionType.RIGHT_CLICK:
            if now - self._last_click < self._click_gap:
                return
            self._mouse.click(Button.right)
            self._last_click = now

        elif a.type == ActionType.SCROLL_UP:
            if now - self._last_scroll < self._scroll_gap:
                return
            amount = max(1, int(a.magnitude * 3))
            self._mouse.scroll(0, amount)
            self._last_scroll = now

        elif a.type == ActionType.SCROLL_DOWN:
            if now - self._last_scroll < self._scroll_gap:
                return
            amount = max(1, int(a.magnitude * 3))
            self._mouse.scroll(0, -amount)
            self._last_scroll = now

        elif a.type == ActionType.KEY_ENTER:
            self._kb.press(Key.enter)
            self._kb.release(Key.enter)

        elif a.type == ActionType.KEY_ESCAPE:
            self._kb.press(Key.esc)
            self._kb.release(Key.esc)

        elif a.type == ActionType.KEY_SPACE:
            self._kb.press(Key.space)
            self._kb.release(Key.space)

    def type_char(self, char: str):
        """Type a single character (called by virtual keyboard)."""
        with self._lock:
            self._kb.press(char)
            self._kb.release(char)

    def type_special(self, key):
        """Type a special key like Key.backspace."""
        with self._lock:
            self._kb.press(key)
            self._kb.release(key)
