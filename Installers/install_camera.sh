#!/usr/bin/env bash
set -e
echo "*** Installing CAMERA node ***"

BASE=/home/a/JumboShoo
SRC=$BASE
UNITDIR=/etc/systemd/system

# 1. build venv
if [ ! -d /home/a/JumboShoo/venv ]; then
  python3 -m venv --system-site-packages /home/a/JumboShoo/venv
  /home/a/JumboShoo/venv/bin/pip install --no-cache-dir \
       ultralytics picamera2 opencv-python adafruit-circuitpython-rfm9x adafruit-blinka numpy
fi

# 2. copy systemd units
install -m 644 $SRC/systemd/lora_cam_bridge.service   $UNITDIR/
install -m 644 $SRC/systemd/status_ping.service       $UNITDIR/
install -m 644 $SRC/systemd/status_ping.timer         $UNITDIR/
install -m 644 $SRC/systemd/reboot.service            $UNITDIR/
install -m 644 $SRC/systemd/reboot.timer              $UNITDIR/

# 3. reload + enable
systemctl daemon-reload
systemctl enable --now lora_cam_bridge.service
systemctl enable --now status_ping.timer
systemctl enable --now reboot.timer

echo "Camera node installed. Reboot to test, or run: sudo systemctl status lora_cam_bridge"
