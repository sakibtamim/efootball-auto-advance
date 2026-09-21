"""
test_controller.py
Tests if virtual input devices (Keyboard Enter, Controller A) are functioning properly on Linux and Windows.
"""

import sys
import time

try:
    from gamepad import InputManager
except ImportError as err:
    print(f"Error: Could not import 'gamepad.py': {err}")
    print("Make sure you activated your venv and installed requirements:")
    print("  Linux:   source venv/bin/activate && pip install -r requirements.txt")
    print("  Windows: venv\\Scripts\\activate && pip install -r requirements.txt")
    sys.exit(1)

def test_controller():
    is_windows = (sys.platform == "win32")
    target_env = "Windows (DirectInput / ViGEmBus)" if is_windows else "Linux (/dev/uinput)"
    print(f"Testing input device creation for {target_env}...")

    try:
        inputs = InputManager(mode="both")
        print("Success! Input devices initialized.")
        
        print("\n1. Testing Keyboard 'Enter' key...")
        if inputs.kb:
            inputs.kb.press_enter()
            print("   -> Keyboard 'Enter' simulated.")

        print("2. Testing Controller 'A' button...")
        if inputs.pad:
            inputs.pad.press_a()
            print("   -> Controller 'A' simulated.")
        else:
            print("   -> Controller not active (ViGEmBus driver not found; use '--input keyboard').")

        print("3. Testing Unified advance() [Enter and/or A]...")
        inputs.advance()
        print("   -> Unified advance simulated.")

        print("4. Testing Unified skip() [Enter and/or A]...")
        inputs.skip()
        print("   -> Unified skip simulated.")
        
        inputs.close()

        if inputs.pad:
            print("\nAll input tests PASSED! Your system is ready for the bot (both Keyboard and Gamepad).")
        else:
            print("\nKeyboard input test PASSED! Ready for the bot using: python bot.py --input keyboard")
    except PermissionError as pe:
        print(f"\n[FAILED] Permission error: {pe}")
        if not is_windows:
            print("Run './setup_uinput.sh' to configure Linux /dev/uinput permissions.")
        sys.exit(1)
    except Exception as ex:
        print(f"\n[FAILED] Unexpected error: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    test_controller()
