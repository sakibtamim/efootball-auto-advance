"""
grab_template.py
Tool to capture reference button templates from eFootball.
Takes a screenshot after a 3-second countdown and allows you to either:
1. Interactively draw a bounding box around the button using OpenCV ROI selector.
2. Or save the full raw screenshot so you can crop it in any image editor.
"""

import os
import sys
import time
import cv2
import numpy as np
import mss

TEMPLATES_DIR = "templates"

def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    os.makedirs(TEMPLATES_DIR, exist_ok=True)

    print("=== eFootball Template Grabber ===")
    print("Switch to the eFootball window now!")
    for i in range(3, 0, -1):
        print(f"Capturing in {i}...")
        time.sleep(1)

    with mss.mss() as sct:
        # Monitor 1 is usually primary
        monitor = sct.monitors[1]
        raw = np.array(sct.grab(monitor))
        # Convert BGRA to BGR
        frame = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)

    timestamp = int(time.time())
    raw_path = f"screenshot_raw_{timestamp}.png"
    cv2.imwrite(raw_path, frame)
    print(f"\n[Saved] Full screenshot saved to: {raw_path}")

    # Attempt interactive ROI crop if GUI window is supported
    try:
        print("\nAttempting interactive cropping window...")
        print("INSTRUCTIONS:")
        print("  1. Click and drag a box tightly around the button (e.g. 'Continue' or 'Skip').")
        print("  2. Press SPACE or ENTER to confirm selection.")
        print("  3. Press 'c' to cancel selection.")

        # Show ROI selector
        roi = cv2.selectROI("Crop Template (Select and press ENTER)", frame, fromCenter=False, showCrosshair=True)
        cv2.destroyAllWindows()

        x, y, w, h = roi
        if w > 0 and h > 0:
            cropped = frame[y:y+h, x:x+w]
            template_name = input("\nEnter a name for this template (e.g. 'continue', 'skip', 'next'): ").strip()
            if not template_name:
                template_name = f"template_{timestamp}"
            save_path = os.path.join(TEMPLATES_DIR, f"{template_name}.png")
            cv2.imwrite(save_path, cropped)
            print(f"[Success] Template saved to: {save_path}")
        else:
            print("No region selected. You can manually crop from:", raw_path)
    except Exception as e:
        print(f"Interactive window not available ({e}).")
        print(f"Please open '{raw_path}' in your favorite image viewer/GIMP and crop the button into '{TEMPLATES_DIR}/<name>.png'.")

if __name__ == "__main__":
    main()
