"""
test_controller.py
Tests if /dev/uinput permissions and the VirtualGamepad class are functioning properly.
"""

import sys
import time

try:
    from gamepad import InputManager
except ImportError:
    print("Error: Could not import 'gamepad.py' or 'evdev'.")
    print("Make sure you activated your venv and installed requirements:")
    print("  source venv/bin/activate && pip install -r requirements.txt")
    sys.exit(1)

def test_controller():
    print("Testing /dev/uinput virtual device creation...")
    try:
        inputs = InputManager(mode="both")
        print("Success! Virtual devices created.")
        
        print("\n1. Testing Controller 'A' button...")
        if inputs.pad:
            inputs.pad.press_a()
            print("   -> Controller 'A' simulated.")

        print("2. Testing Controller 'Start' button...")
        if inputs.pad:
            inputs.pad.press_start()
            print("   -> Controller 'Start' simulated.")

        print("3. Testing Keyboard 'Enter' key...")
        if inputs.kb:
            inputs.kb.press_enter()
            print("   -> Keyboard 'Enter' simulated.")

        print("4. Testing Unified advance() [Both Enter + A]...")
        inputs.advance()
        print("   -> Unified advance simulated.")
        
        inputs.close()
        print("\nAll input tests PASSED! Your system is ready for the bot.")
    except PermissionError as pe:
        print(f"\n[FAILED] {pe}")
        sys.exit(1)
    except Exception as ex:
        print(f"\n[FAILED] Unexpected error: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    test_controller()
