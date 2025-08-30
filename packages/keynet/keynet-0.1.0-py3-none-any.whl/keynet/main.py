# main.py
import threading
import time
from typing import Callable, Set, List, Tuple, Dict, Any, Optional
import psutil
import pynput
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pythoncom

class KeyNet:
    """A class to detect and handle system events (keyboard, mouse, battery, network, volume) on Windows."""
    
    def __init__(self):
        self.listeners: Dict[str, List[Tuple[Callable, Dict[str, Any]]]] = {
            "key_press": [],
            "key_release": [],
            "key_combo": [],
            "mouse_click": [],
            "mouse_move": [],
            "mouse_scroll": [],
            "volume_threshold": [],
            "volume_mute": [],
            "battery": [],
            "network": []
        }
        self.current_keys: Set[str] = set()  # Store string keys
        self.running: bool = False
        self._key_lock = threading.Lock()
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None

    def _key_to_string(self, key: Key | KeyCode) -> str:
        """Convert a pynput Key or KeyCode to a string (e.g., 'c', 'ctrl', 'enter')."""
        if isinstance(key, KeyCode) and key.char is not None:
            return key.char.lower()  # e.g., 'c', '1'
        elif isinstance(key, Key):
            # Map special keys to their names (e.g., Key.ctrl -> 'ctrl')
            for name, value in Key.__members__.items():
                if value == key:
                    return name.lower()  # e.g., 'ctrl', 'shift', 'enter'
        return str(key).strip("'")  # Fallback: strip quotes from str(key)

    def on(self, event_type: str, callback: Callable, **kwargs) -> None:
        """Register a listener for an event with optional parameters.

        Args:
            event_type: The type of event to listen for (e.g., 'key_press', 'volume_mute').
            callback: The function to call when the event occurs.
            **kwargs: Additional parameters (e.g., combo for key_combo, threshold for volume).
        
        Raises:
            ValueError: If the event_type is unknown.
        """
        if event_type not in self.listeners:
            raise ValueError(f"Unknown event type: {event_type}")
        self.listeners[event_type].append((callback, kwargs))

    def _start_keyboard_listener(self) -> None:
        """Start the keyboard listener for key press, release, and combo events."""
        def on_press(key: Key | KeyCode) -> None:
            key_str = self._key_to_string(key)
            with self._key_lock:
                self.current_keys.add(key_str)
            for cb, _ in self.listeners["key_press"]:
                cb(key_str)  # Pass string key to callback
            for cb, params in self.listeners["key_combo"]:
                combo = params.get("combo", [])
                if combo and self._check_combo(combo):
                    cb(combo)

        def on_release(key: Key | KeyCode) -> None:
            key_str = self._key_to_string(key)
            with self._key_lock:
                if key_str in self.current_keys:
                    self.current_keys.remove(key_str)
            for cb, _ in self.listeners["key_release"]:
                cb(key_str)  # Pass string key to callback

        self._keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._keyboard_listener.start()

    def _check_combo(self, combo: List[str]) -> bool:
        """Check if the required combo keys are pressed.

        Args:
            combo: List of key names (e.g., ['ctrl', 'c']).

        Returns:
            bool: True if all combo keys are currently pressed.

        Raises:
            ValueError: If a key in the combo is invalid.
        """
        with self._key_lock:
            return set(combo).issubset(self.current_keys)

    def _start_mouse_listener(self) -> None:
        """Start the mouse listener for click, move, and scroll events."""
        def on_click(x: int, y: int, button: mouse.Button, pressed: bool) -> None:
            for cb, _ in self.listeners["mouse_click"]:
                cb(x, y, button, pressed)

        def on_move(x: int, y: int) -> None:
            for cb, _ in self.listeners["mouse_move"]:
                cb(x, y)

        def on_scroll(x: int, y: int, dx: int, dy: int) -> None:
            for cb, _ in self.listeners["mouse_scroll"]:
                cb(x, y, dx, dy)

        self._mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)
        self._mouse_listener.start()

    def _start_system_monitors(self) -> None:
        """Start monitoring system events (battery, network, volume, mute) in a separate thread."""
        def monitor() -> None:
            pythoncom.CoInitialize()
            try:
                last_battery = None
                last_net = None
                last_volume_state = None
                last_mute_state = None
                while self.running:
                    if self.listeners["battery"]:
                        try:
                            batt = psutil.sensors_battery()
                            if batt and (last_battery != (batt.percent, batt.power_plugged)):
                                last_battery = (batt.percent, batt.power_plugged)
                                for cb, _ in self.listeners["battery"]:
                                    cb(batt.percent, batt.power_plugged)
                        except Exception as e:
                            print(f"Battery monitoring error: {e}")

                    if self.listeners["network"]:
                        try:
                            net = psutil.net_if_stats()
                            connected = any(iface.isup for iface in net.values())
                            if last_net != connected:
                                last_net = connected
                                for cb, _ in self.listeners["network"]:
                                    cb(connected)
                        except Exception as e:
                            print(f"Network monitoring error: {e}")

                    if self.listeners["volume_threshold"] or self.listeners["volume_mute"]:
                        try:
                            vol, is_muted = self._get_system_volume()
                            for cb, params in self.listeners["volume_threshold"]:
                                threshold = params.get("threshold", 50)
                                current_state = vol is not None and vol >= threshold
                                if vol is not None and last_volume_state != current_state:
                                    last_volume_state = current_state
                                    cb(vol)
                            for cb, _ in self.listeners["volume_mute"]:
                                if is_muted is not None and last_mute_state != is_muted:
                                    last_mute_state = is_muted
                                    cb(is_muted)
                        except Exception as e:
                            print(f"Volume monitoring error: {e}")

                    time.sleep(1)
            finally:
                pythoncom.CoUninitialize()

        t = threading.Thread(target=monitor, daemon=True)
        t.start()

    def _get_system_volume(self) -> Tuple[Optional[int], Optional[bool]]:
        """Get the current system volume (0-100) and mute state on Windows.

        Returns:
            Tuple[Optional[int], Optional[bool]]: The current volume percentage and mute state, or (None, None) if unavailable.
        """
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            vol = int(volume.GetMasterVolumeLevelScalar() * 100)
            is_muted = bool(volume.GetMute())
            return vol, is_muted
        except (OSError, ValueError, AttributeError) as e:
            print(f"Volume detection error: {e}")
            return None, None

    def start(self) -> None:
        """Start all event listeners and monitors."""
        try:
            import psutil
            import pynput
            import pycaw
            import pythoncom
        except ImportError as e:
            raise ImportError(f"Missing required dependency: {e}")

        self.running = True
        self._start_keyboard_listener()
        self._start_mouse_listener()
        self._start_system_monitors()

    def stop(self) -> None:
        """Stop all event listeners and monitors."""
        self.running = False
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None