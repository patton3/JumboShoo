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
       ultralytics picamera2 opencv-python adafruit-circuitpython-rfm9x adafruit-blinka numpy
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

echo "XLarge Model saved to $MODEL_DIR/Elephants2x.pt"
# 5. Set Wallpaper
pcmanfm --set-wallpaper $BASE/backgrounds/CamBackground.png

echo "Camera node installed. Reboot to test, or run: sudo systemctl status lora_cam_bridge"
