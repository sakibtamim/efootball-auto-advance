# eFootball AI Match Automation Bot (EndeavourOS / Linux)

Automates skipping cutscenes, advancing through post-match screens (halftime stats, fulltime stats, EXP/player levels, rewards), and continuing to the next match in **eFootball** on Steam (via Proton) using a virtual controller and Computer Vision.

---

## Architecture Overview

1. **Input**: Emulates a physical Xbox controller using Linux's native `/dev/uinput` via `python-evdev`. Steam Input and Proton detect this as a real hardware controller.
2. **Vision**: Takes fast screen captures via `mss` and searches for UI buttons ("Continue", "Skip", "Next", "To Next Match", or controller 'A' icons) using OpenCV template matching.
3. **Anti-Detection**: Uses randomized delays and humanized button hold durations.

---

## 1. Prerequisites (EndeavourOS / Arch)

### Granting `/dev/uinput` Access
Linux restricts creating virtual hardware to root by default. Run the included setup script once:

```bash
chmod +x setup_uinput.sh
./setup_uinput.sh
```

Or manually:
```bash
sudo modprobe uinput
sudo usermod -aG input $USER
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```
*(Note: If you just added yourself to the `input` group, log out and back in once for permissions to apply).*

---

## 2. Installation

Create a Python virtual environment (recommended on Arch Linux):

```bash
cd efootball_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Quick Verification

Verify that your user has permission to create a virtual controller:

```bash
python test_controller.py
```
If configured correctly, this will create a virtual Xbox controller, simulate pressing 'A' and 'Start', and report success.

---

## 4. Capturing Template Images

For the bot to know when to press buttons, it needs small PNG reference templates of the buttons in your game resolution.

1. Launch **eFootball**.
2. When you reach a screen with a button you want to auto-click (e.g. "Continue", "Skip", or the "A: Advance" prompt), run:
   ```bash
   python grab_template.py
   ```
3. It gives you 3 seconds to switch to the game and saves `screenshot_raw.png`.
4. Crop just the button text or icon and save it into the `templates/` directory:
   - `templates/continue.png`
   - `templates/skip.png`
   - `templates/next.png`
   - `templates/advance_a.png`

---

## 5. Running the Bot

1. Set your match controls in eFootball to **AI Controlled** (available in VS AI Events and Tour Events).
2. Start the bot:
   ```bash
   # Default: fires BOTH Keyboard (Enter/Space) and Controller (A/Start)
   python bot.py

   # Keyboard only (uses Enter to advance, Space/Enter to skip):
   python bot.py --input keyboard

   # Controller only (uses 'A' to advance, 'Start' to skip):
   python bot.py --input controller
   ```
3. Switch back to eFootball.
4. Press `Ctrl+C` in the terminal when you want to stop the bot.

---

## Wayland vs X11 Note
- **X11**: Works out of the box.
- **Wayland (KDE / Hyprland / GNOME)**: Since Steam Proton runs under XWayland, `mss` captures XWayland windows directly in most configurations. If your display server blocks screen capture, run under an X11 session or adjust Wayland screen-capture permissions.

---

## Disclaimer
This project is developed for educational, accessibility, and personal automation purposes only. 
"eFootball" is a registered trademark of KONAMI. This project is not affiliated with, authorized, or endorsed by KONAMI. Use responsibly.

