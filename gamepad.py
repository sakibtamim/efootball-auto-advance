"""
gamepad.py
Hardware-level emulation via Linux /dev/uinput using python-evdev.
Provides:
- VirtualKeyboard: Pure keyboard device (ID_INPUT_KEYBOARD) sending Enter
- VirtualGamepad: Pure Xbox 360 controller device (ID_INPUT_JOYSTICK)
- InputManager: High-level controller supporting 'keyboard', 'controller', or 'both'
"""

import time
import os
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

class VirtualKeyboard:
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

class VirtualGamepad:
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

class InputManager:
    def __init__(self, mode="both"):
        if not os.path.exists("/dev/uinput"):
            raise FileNotFoundError("Kernel module 'uinput' is not loaded: sudo modprobe uinput")

        self.mode = mode.lower()
        self.kb = None
        self.pad = None

        if self.mode in ("keyboard", "both"):
            self.kb = VirtualKeyboard()
            print("[Input] Virtual Keyboard initialized (Enter).")

        if self.mode in ("controller", "both"):
            self.pad = VirtualGamepad()
            print("[Input] Virtual Xbox Gamepad initialized (A).")

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
