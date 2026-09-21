# eFootball Auto Advance (Linux & Windows)

Cross-platform bot that automates skipping cutscenes, advancing through post-match screens (halftime stats, fulltime stats, EXP/player levels, rewards), and continuing to the next match in **eFootball** on Steam using Computer Vision and simulated inputs.

Supports:
- **Linux** (EndeavourOS / Arch / Steam Proton via `/dev/uinput` and KDE Spectacle / X11 `mss`)
- **Windows** (DirectInput hardware scancodes via Win32 `SendInput`, `vgamepad` with ViGEmBus, and native `mss`)

---

## Architecture Overview

1. **Vision Engine (Cross-Platform)**: Takes high-performance screen captures via `mss` (Windows/X11) or `spectacle` (Linux Wayland) and detects UI buttons ("Continue", "Skip", "Next", "To Next Match", or controller 'A' prompts) using OpenCV template matching.
2. **Input Emulation**:
   - **Linux**: Emulates a hardware Xbox controller and/or keyboard via `/dev/uinput` using `python-evdev`.
   - **Windows**: Emulates DirectX hardware keyboard scancodes (`0x1C` for `Enter`) directly via Win32 `SendInput`, and Xbox 360 controller (`A` button) via `vgamepad` / ViGEmBus.
3. **Anti-Detection**: Employs randomized reaction delays, natural button hold intervals, and periodic cutscene wakeups.

---

## 1. Setup Guide

### Windows Setup

1. Make sure you have **Python 3.10+** installed (with **"Add python.exe to PATH"** checked).
2. Set eFootball display mode to **Borderless** or **Windowed** in the game's graphics settings.
3. Double-click `setup_windows.bat` or run in Command Prompt:
   ```cmd
   git clone https://github.com/sakibtamim/efootball-auto-advance.git
   cd efootball-auto-advance
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. *(Optional - For Gamepad Mode)*: If you wish to use controller mode instead of keyboard, install the [ViGEmBus Driver](https://github.com/nefarius/ViGEmBus/releases). (Keyboard mode works out of the box with 0 extra drivers).

### Linux (EndeavourOS / Arch) Setup

1. Grant `/dev/uinput` permissions once:
   ```bash
   chmod +x setup_uinput.sh
   ./setup_uinput.sh
   ```
   *(Or run `sudo modprobe uinput && sudo usermod -aG input $USER` and log out/in).*
2. Clone repository and install dependencies:
   ```bash
   git clone https://github.com/sakibtamim/efootball-auto-advance.git
   cd efootball-auto-advance
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 2. Quick Verification

Verify that your input devices are working properly (you can call the venv Python directly without activating):

```bash
# Linux
./venv/bin/python test_controller.py

# Windows
venv\Scripts\python.exe test_controller.py
```
This tests the Keyboard (`Enter`) and Controller (`A`) simulations and reports readiness.

---

## 3. Capturing Template Images

The bot matches small PNG reference templates of the buttons in your game resolution:

1. Launch **eFootball**.
2. When you reach a screen with a button to click (e.g. "Continue", "Skip", or "Next"), run:
   ```bash
   # Linux
   ./venv/bin/python grab_template.py

   # Windows
   venv\Scripts\python.exe grab_template.py
   ```
3. Switch to eFootball within 3 seconds. It will save `screenshot_raw_<timestamp>.png`.
4. Select and crop the button area using the interactive window, or crop it manually and save into the `templates/` folder:
   - `templates/continue.png`
   - `templates/skip.png`
   - `templates/next.png`
   - `templates/advance_a.png`

---

## 4. Running the Bot

1. Set your match controls in eFootball to **AI Controlled** (VS AI Events, Tour Events, etc.).
2. Start the bot directly using your virtual environment's Python (no need to run `source venv/bin/activate` every time):

   **Linux (EndeavourOS / Arch)**:
   ```bash
   # Keyboard only (uses Enter - Recommended):
   ./venv/bin/python bot.py --input keyboard

   # Default (fires both Enter + A):
   ./venv/bin/python bot.py

   # Controller only (uses 'A' button):
   ./venv/bin/python bot.py --input controller
   ```

   **Windows**:
   ```cmd
   # Keyboard only (uses Enter - Recommended):
   venv\Scripts\python.exe bot.py --input keyboard

   # Default (fires both Enter + A):
   venv\Scripts\python.exe bot.py

   # Controller only (uses 'A' button):
   venv\Scripts\python.exe bot.py --input controller
   ```

   *(Tip: If your terminal already has `venv` activated, typing plain `python bot.py ...` works identically).*

3. Switch back to eFootball.
4. Press `Ctrl+C` in the terminal when you wish to stop the bot.

---

## 5. Optional Shortcut: Linux Shell Alias

If you want to start the bot from **any** terminal directory without having to `cd` into the project or activate the virtual environment:

Add this alias to your shell configuration (`~/.bashrc` or `~/.zshrc`), replacing `/path/to/` with your actual directory path:

```bash
alias efootball-bot="/path/to/efootball-auto-advance/venv/bin/python /path/to/efootball-auto-advance/bot.py"
```

*(Or automatically add it from inside the project directory)*:
```bash
echo "alias efootball-bot=\"\$(pwd)/venv/bin/python \$(pwd)/bot.py\"" >> ~/.bashrc
```

Then reload your configuration (`source ~/.bashrc` or open a new terminal). You can now start the bot anytime simply by running:

```bash
efootball-bot --input keyboard
```

---

## Platform Notes

- **Windows**: Make sure eFootball is running in **Borderless** or **Windowed** mode (Exclusive Fullscreen may block screen grabbers).
- **Linux Wayland**: Native KDE Spectacle capture is automatically used when running under Wayland.
- **Linux X11**: `mss` is used for screen capture.

---

## Disclaimer
This project is developed for educational, accessibility, and personal automation purposes only. 
"eFootball" is a registered trademark of KONAMI. This project is not affiliated with, authorized, or endorsed by KONAMI. Use responsibly.
