"""
bot.py
Cross-platform automation bot for eFootball (Linux / Windows).
Supports:
- Windows (mss screen capture & DirectInput / ViGEmBus input)
- Linux / EndeavourOS / Steam Proton (Wayland KDE Spectacle / X11 mss & /dev/uinput)
- Keyboard input (Enter) and Controller input (Xbox A)
"""

import os
import sys
import glob
import time
import random
import argparse
import signal
import subprocess
import cv2
import numpy as np
import mss

from gamepad import InputManager

DEFAULT_CONFIDENCE = 0.75
TEMPLATES_DIR = "templates"

class ScreenGrabber:
    """Handles screenshot capture on Windows (mss), Wayland (KDE Spectacle), and X11 (mss)."""
    def __init__(self, monitor_idx=1):
        self.monitor_idx = monitor_idx
        self.is_windows = (sys.platform == "win32")

        if self.is_windows:
            # Enable per-monitor DPI awareness so MSS captures at 1:1 native resolution
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                try:
                    import ctypes
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
            self.is_wayland = False
            self.shm_path = None
            backend = "mss (Windows Native)"
        else:
            self.is_wayland = bool(
                os.environ.get("WAYLAND_DISPLAY") or
                os.environ.get("XDG_SESSION_TYPE") == "wayland"
            )
            self.shm_path = "/dev/shm/efootball_screen.png"
            backend = "KDE Spectacle (Wayland)" if self.is_wayland else "mss (Linux X11)"

        print(f"[Screen] Capture backend: {backend}")

    def grab(self):
        if not self.is_windows and self.is_wayland:
            # Native Wayland capture to RAM disk via Spectacle
            subprocess.run(
                ["spectacle", "-b", "-n", "-f", "-o", self.shm_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if self.shm_path and os.path.exists(self.shm_path):
                img = cv2.imread(self.shm_path)
                if img is not None and img.mean() > 1.0:
                    return img

        # Fallback to mss (Windows / Linux X11)
        with mss.MSS() as sct:
            if self.monitor_idx >= len(sct.monitors):
                self.monitor_idx = 1
            raw = np.array(sct.grab(sct.monitors[self.monitor_idx]))
            # If mss gives all black on Wayland, switch to Spectacle
            if not self.is_windows and raw.mean() < 1.0 and not self.is_wayland:
                print("[Screen] Notice: X11 returned black screen. Switching to Spectacle Wayland capture.")
                self.is_wayland = True
                return self.grab()
            return cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)

class EFootballBot:
    def __init__(self, confidence=DEFAULT_CONFIDENCE, monitor_idx=1, input_mode="both",
                 poke_interval=4.0, debug=False):
        self.confidence = confidence
        self.monitor_idx = monitor_idx
        self.input_mode = input_mode
        self.poke_interval = poke_interval
        self.auto_poke = poke_interval > 0
        self.debug = debug
        self.running = True
        self.templates = {}

        # Signal handling
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

        print("[Init] Loading button templates...")
        self.load_templates()

        print(f"[Init] Initializing Input (Mode: {self.input_mode.upper()})...")
        self.inputs = InputManager(mode=self.input_mode)
        self.grabber = ScreenGrabber(monitor_idx=self.monitor_idx)

    def _handle_exit(self, signum, frame):
        print("\n[Shutdown] Stopping bot gracefully...")
        self.running = False

    def load_templates(self):
        """Loads all .png files from templates directory in grayscale."""
        pattern = os.path.join(TEMPLATES_DIR, "*.png")
        files = glob.glob(pattern)
        if not files:
            print(f"[Warning] No PNG template files found in '{TEMPLATES_DIR}/'!")
            return

        for filepath in files:
            name = os.path.splitext(os.path.basename(filepath))[0].lower()
            img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                self.templates[name] = img
                print(f"  -> Loaded template: '{name}' ({img.shape[1]}x{img.shape[0]})")

    def find_best_match(self, screen_gray):
        """
        Scans current screen against all loaded templates.
        Returns (matched_name, max_confidence, max_loc).
        """
        matches = {}
        highest_sub_threshold = 0.0

        for name, template in self.templates.items():
            if template.shape[0] > screen_gray.shape[0] or template.shape[1] > screen_gray.shape[1]:
                continue

            res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if self.debug:
                print(f"    [Debug Match] {name}: {max_val:.3f}")

            if max_val >= self.confidence:
                matches[name] = (max_val, max_loc)
            elif max_val > highest_sub_threshold:
                highest_sub_threshold = max_val

        if not matches:
            return None, highest_sub_threshold, None

        # Prioritize 'skip' if it matched above threshold
        for name in matches:
            if "skip" in name:
                return name, matches[name][0], matches[name][1]

        # Otherwise pick the match with highest confidence
        best_name = max(matches, key=lambda k: matches[k][0])
        return best_name, matches[best_name][0], matches[best_name][1]

    def execute_action(self, template_name):
        """Triggers appropriate button/key press based on template name and input mode."""
        reaction_delay = random.uniform(0.5, 0.9)
        time.sleep(reaction_delay)

        hold_time = random.uniform(0.12, 0.20)

        if "skip" in template_name:
            print(f"  [Action] Skipping cutscene (A button / Enter)...")
            self.inputs.skip(hold_duration=hold_time)
        else:
            print(f"  [Action] Advancing screen (A button / Enter)...")
            self.inputs.advance(hold_duration=hold_time)

        # Post-action cooldown to let game transition screen
        cooldown = random.uniform(2.0, 3.0)
        time.sleep(cooldown)

    def run(self):
        print(f"\n==========================================")
        print(f" eFootball Bot Running")
        print(f" Input Mode: {self.input_mode.upper()} (Keyboard: Enter / Gamepad: A)")
        print(f" Cutscene Wakeup: {'Every ' + str(self.poke_interval) + 's' if self.auto_poke else 'Disabled'}")
        print(f" Confidence Threshold: {self.confidence}")
        print(f" Switch to eFootball window. Press Ctrl+C to stop.")
        print(f"==========================================\n")

        last_poke_time = time.time()

        while self.running:
            try:
                # 1. Capture screen
                screen_bgr = self.grabber.grab()
                if screen_bgr is None:
                    time.sleep(1.0)
                    continue

                screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)

                # 2. Template match
                matched_name, max_val, _ = self.find_best_match(screen_gray)

                if matched_name:
                    now_str = time.strftime("%H:%M:%S")
                    print(f"[{now_str}] Detected '{matched_name}' (Confidence: {max_val:.2f})")
                    self.execute_action(matched_name)
                    # Reset poke timer after any successful action
                    last_poke_time = time.time()
                else:
                    curr_time = time.time()
                    # If cutscene is playing without showing the skip prompt,
                    # tap A/Enter to force eFootball to display the 'Skip' button.
                    if self.auto_poke and (curr_time - last_poke_time >= self.poke_interval):
                        now_str = time.strftime("%H:%M:%S")
                        btn_name = "A button" if self.input_mode == "controller" else "Enter"
                        print(f"[{now_str}] [Cutscene Wakeup] Tapping {btn_name} to reveal skip button...")
                        self.inputs.advance(hold_duration=0.12)
                        last_poke_time = curr_time
                        time.sleep(0.4)
                    else:
                        if self.debug:
                            print(f"[{time.strftime('%H:%M:%S')}] In match / idle (Peak: {max_val:.2f})")
                        time.sleep(1.0)

            except Exception as ex:
                print(f"[Error in loop] {ex}")
                time.sleep(2.0)

        self.cleanup()

    def cleanup(self):
        if hasattr(self, "inputs") and self.inputs:
            self.inputs.close()
        # Clean temporary file
        if os.path.exists("/dev/shm/efootball_screen.png"):
            try:
                os.remove("/dev/shm/efootball_screen.png")
            except Exception:
                pass
        print("[Shutdown] Bot stopped cleanly.")

def main():
    parser = argparse.ArgumentParser(description="eFootball Auto-Skip / Auto-Continue Bot (Linux & Windows)")
    parser.add_argument("--confidence", "-c", type=float, default=DEFAULT_CONFIDENCE,
                        help="Confidence threshold for template matching (0.0 to 1.0, default: 0.75)")
    parser.add_argument("--monitor", "-m", type=int, default=1,
                        help="Monitor index to capture (default: 1)")
    parser.add_argument("--input", "-i", choices=["both", "keyboard", "controller"], default="both",
                        help="Input mode: 'both' (default), 'keyboard' (Enter), 'controller' (A)")
    parser.add_argument("--poke-interval", "-p", type=float, default=4.0,
                        help="Seconds between gentle Enter taps during cutscenes to show the skip button (0 to disable, default: 4.0)")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Print match score for all templates each scan")
    args = parser.parse_args()

    bot = EFootballBot(
        confidence=args.confidence,
        monitor_idx=args.monitor,
        input_mode=args.input,
        poke_interval=args.poke_interval,
        debug=args.debug
    )
    bot.run()

if __name__ == "__main__":
    main()
