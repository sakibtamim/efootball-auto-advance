"""
gamepad.py
Cross-platform hardware/input emulation for eFootball:
- Linux: Linux /dev/uinput via python-evdev
- Windows: DirectInput hardware scancodes via Win32 SendInput & ViGEmBus via vgamepad

Provides:
- VirtualKeyboard: Pure keyboard device sending Enter
- VirtualGamepad: Pure Xbox 360 controller device sending A button
- InputManager: High-level cross-platform controller supporting 'keyboard', 'controller', or 'both'
"""

import sys
import time
import os

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    # Win32 INPUT structure definitions for DirectInput hardware scancodes
    PUL = ctypes.POINTER(ctypes.c_ulong)

    class KeyBdInput(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", PUL),
        ]

    class HardwareInput(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        ]

    class MouseInput(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", PUL),
        ]

    class Input_I(ctypes.Union):
        _fields_ = [
            ("ki", KeyBdInput),
            ("mi", MouseInput),
            ("hi", HardwareInput),
        ]

    class Input(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("ii", Input_I),
        ]

    INPUT_KEYBOARD = 1
    KEYEVENTF_SCANCODE = 0x0008
    KEYEVENTF_KEYUP = 0x0002
    DIK_RETURN = 0x1C  # DirectInput hardware scan code for Enter

    class WindowsDirectInputKeyboard:
        """Sends DirectInput hardware scancodes via Win32 SendInput (DirectX compatible)."""
        def __init__(self, name="Windows DirectInput Keyboard"):
            self.send_input = ctypes.windll.user32.SendInput

        def press_key(self, scan_code, hold_duration=0.15):
            extra = ctypes.c_ulong(0)
            ii_down = Input_I()
            ii_down.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
            x_down = Input(INPUT_KEYBOARD, ii_down)
            self.send_input(1, ctypes.byref(x_down), ctypes.sizeof(x_down))

            time.sleep(hold_duration)

            ii_up = Input_I()
            ii_up.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
            x_up = Input(INPUT_KEYBOARD, ii_up)
            self.send_input(1, ctypes.byref(x_up), ctypes.sizeof(x_up))

        def press_enter(self, hold_duration=0.15):
            self.press_key(DIK_RETURN, hold_duration)

        def close(self):
            pass

    class WindowsVirtualGamepad:
        """Emulates an Xbox 360 controller on Windows via vgamepad and ViGEmBus."""
        def __init__(self, name="Microsoft X-Box 360 pad"):
            try:
                import vgamepad as vg
                self.vg = vg
                self.device = vg.VX360Gamepad()
            except ImportError:
                raise ImportError(
                    "Python package 'vgamepad' is not installed. "
                    "Run 'pip install vgamepad' and install the ViGEmBus driver, "
                    "or run the bot with '--input keyboard'."
                )
            except Exception as ex:
                raise RuntimeError(
                    f"Failed to initialize ViGEmBus virtual gamepad: {ex}. "
                    "Make sure ViGEmBus is installed (https://github.com/nefarius/ViGEmBus/releases) "
                    "or run with '--input keyboard'."
                )

        def press_a(self, hold_duration=0.15):
            self.device.press_button(button=self.vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.device.update()
            time.sleep(hold_duration)
            self.device.release_button(button=self.vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.device.update()

        def close(self):
            if hasattr(self, "device") and self.device:
                pass

    VirtualKeyboard = WindowsDirectInputKeyboard
    VirtualGamepad = WindowsVirtualGamepad

else:
    # Linux implementation using evdev and /dev/uinput
    from evdev import UInput, ecodes as e

    VENDOR_MICROSOFT = 0x045E
    PRODUCT_XBOX360 = 0x028E

    KEYBOARD_CAPS = {
        e.EV_KEY: [
            e.KEY_ENTER,
        ]
    }

    GAMEPAD_CAPS = {
        e.EV_KEY: [
            e.BTN_SOUTH,       # 'A' Button (Advance / Select)
            e.BTN_EAST,        # 'B' Button (Cancel / Back)
            e.BTN_NORTH,       # 'X' Button
            e.BTN_WEST,        # 'Y' Button
            e.BTN_START,       # Menu / Start Button (Pause / Skip cutscenes)
            e.BTN_SELECT,      # View / Back Button
            e.BTN_TL,          # Left Bumper
            e.BTN_TR,          # Right Bumper
            e.BTN_DPAD_UP,     # D-Pad Up
            e.BTN_DPAD_DOWN,   # D-Pad Down
            e.BTN_DPAD_LEFT,   # D-Pad Left
            e.BTN_DPAD_RIGHT,  # D-Pad Right
        ],
        e.EV_ABS: [
            (e.ABS_X, (0, -32768, 32767, 16, 128)),
            (e.ABS_Y, (0, -32768, 32767, 16, 128)),
            (e.ABS_RX, (0, -32768, 32767, 16, 128)),
            (e.ABS_RY, (0, -32768, 32767, 16, 128)),
        ]
    }

    class LinuxVirtualKeyboard:
        def __init__(self, name="Virtual Standard Keyboard"):
            self.device = UInput(
                events=KEYBOARD_CAPS,
                name=name,
                vendor=0x0001,
                product=0x0001,
                bustype=e.BUS_USB,
            )

        def press_key(self, key_code, hold_duration=0.15):
            self.device.write(e.EV_KEY, key_code, 1)
            self.device.syn()
            time.sleep(hold_duration)
            self.device.write(e.EV_KEY, key_code, 0)
            self.device.syn()

        def press_enter(self, hold_duration=0.15):
            self.press_key(e.KEY_ENTER, hold_duration)

        def close(self):
            if hasattr(self, "device") and self.device:
                self.device.close()

    class LinuxVirtualGamepad:
        def __init__(self, name="Microsoft X-Box 360 pad"):
            self.device = UInput(
                events=GAMEPAD_CAPS,
                name=name,
                vendor=VENDOR_MICROSOFT,
                product=PRODUCT_XBOX360,
                version=0x0110,
                bustype=e.BUS_USB,
            )

        def press_button(self, btn_code, hold_duration=0.15):
            self.device.write(e.EV_KEY, btn_code, 1)
            self.device.syn()
            time.sleep(hold_duration)
            self.device.write(e.EV_KEY, btn_code, 0)
            self.device.syn()

        def press_a(self, hold_duration=0.15):
            self.press_button(e.BTN_SOUTH, hold_duration)

        def press_b(self, hold_duration=0.15):
            self.press_button(e.BTN_EAST, hold_duration)

        def press_start(self, hold_duration=0.15):
            self.press_button(e.BTN_START, hold_duration)

        def close(self):
            if hasattr(self, "device") and self.device:
                self.device.close()

    VirtualKeyboard = LinuxVirtualKeyboard
    VirtualGamepad = LinuxVirtualGamepad


class InputManager:
    def __init__(self, mode="both"):
        self.is_windows = (sys.platform == "win32")

        if not self.is_windows and not os.path.exists("/dev/uinput"):
            raise FileNotFoundError("Kernel module 'uinput' is not loaded: sudo modprobe uinput")

        self.mode = mode.lower()
        self.kb = None
        self.pad = None

        if self.mode in ("keyboard", "both"):
            self.kb = VirtualKeyboard()
            backend = "DirectInput" if self.is_windows else "uinput"
            print(f"[Input] Virtual Keyboard initialized ({backend}: Enter).")

        if self.mode in ("controller", "both"):
            try:
                self.pad = VirtualGamepad()
                backend = "ViGEmBus" if self.is_windows else "uinput"
                print(f"[Input] Virtual Xbox Gamepad initialized ({backend}: A).")
            except Exception as ex:
                if self.mode == "both":
                    print(f"[Input Warning] Virtual Gamepad not available ({ex}). Falling back to Keyboard only.")
                    self.pad = None
                else:
                    raise

        time.sleep(0.8)

    def advance(self, hold_duration=0.15):
        """Presses Enter (Keyboard) and/or A button (Controller) to continue."""
        if self.kb:
            self.kb.press_enter(hold_duration)
        if self.pad:
            self.pad.press_a(hold_duration)

    def skip(self, hold_duration=0.15):
        """Skips cutscenes via Enter (Keyboard) and/or A button (Controller)."""
        if self.kb:
            self.kb.press_enter(hold_duration)
        if self.pad:
            self.pad.press_a(hold_duration)

    def close(self):
        if self.kb:
            self.kb.close()
        if self.pad:
            self.pad.close()
        print("[Input] Virtual devices closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
