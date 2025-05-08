#!/usr/bin/env bash
set -e
echo "*** Installing CAMERA node ***"

BASE=/home/a/JumboShoo
SRC=$BASE
UNITDIR=/etc/systemd/system
MODEL_DIR="$BASE/scripts/models"

# 1. build venv
if [ ! -d "$BASE/venv" ]; then
  python3 -m venv --system-site-packages "$BASE/venv"
  "$BASE/venv/bin/pip" install --no-cache-dir \
       ultralytics picamera2 opencv-python adafruit-circuitpython-rfm9x adafruit-blinka
fi

# 2. copy systemd units
install -m 644 "$SRC/systemd/lora_cam_bridge.service" "$UNITDIR/"
install -m 644 "$SRC/systemd/status_ping.service"     "$UNITDIR/"
install -m 644 "$SRC/systemd/status_ping.timer"       "$UNITDIR/"
install -m 644 "$SRC/systemd/reboot.service"          "$UNITDIR/"
install -m 644 "$SRC/systemd/reboot.timer"            "$UNITDIR/"

# 3. reload + enable
systemctl daemon-reload
systemctl enable --now lora_cam_bridge.service
systemctl enable --now status_ping.timer
systemctl enable --now reboot.timer

# 4. Download yolo11x.pt
wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt \
     -O "$MODEL_DIR/Elephants2x.pt"
echo "✓ XLarge Model saved to $MODEL_DIR/Elephants2x.pt"

# 5. Set wallpaper
pcmanfm --set-wallpaper "$BASE/backgrounds/CamBackground.png"

# 6. Fix gpiomem access for non-root (RPi camera RuntimeError workaround)
UDEV_RULE="/etc/udev/rules.d/99-com.rules"
FIX_LINE='KERNEL=="gpiomem", OWNER="root", GROUP="dialout"'

echo "Applying gpiomem fix for RPi compatibility..."
if ! grep -Fxq "$FIX_LINE" "$UDEV_RULE"; then
  echo "$FIX_LINE" | tee -a "$UDEV_RULE" > /dev/null
  udevadm control --reload-rules && udevadm trigger
  echo "✓ udev rule added to $UDEV_RULE"
else
  echo "✓ gpiomem rule already present"
fi

echo "Camera node installed. Reboot to test, or run: sudo systemctl status lora_cam_bridge"
