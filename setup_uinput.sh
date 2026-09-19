#!/usr/bin/env bash
# setup_uinput.sh: Grants user access to /dev/uinput on Arch/EndeavourOS for controller emulation

set -e

echo "=== eFootball Bot: /dev/uinput Setup for EndeavourOS ==="

# 1. Load uinput module
echo "[1/4] Loading uinput kernel module..."
sudo modprobe uinput

# 2. Add current user to input group
echo "[2/4] Adding user '$USER' to 'input' group..."
sudo usermod -aG input "$USER"

# 3. Create udev rule for persistent permissions
echo "[3/4] Installing udev rule for /dev/uinput..."
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null

# 4. Reload udev rules
echo "[4/4] Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "=== Setup complete! ==="
echo "NOTE: If you were just added to the 'input' group, you may need to log out and log back in (or run 'newgrp input') for group changes to take effect."
