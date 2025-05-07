#!/usr/bin/env bash
# Run with:
#   curl -sL https://raw.githubusercontent.com/patton3/JumboShoo/main/bootstrap.sh | sudo bash

set -e

USERNAME=$(logname)
REPO="https://github.com/patton3/JumboShoo.git"
DEST="/home/a/JumboShoo"
BOOT_CFG="/boot/config.txt"
NEW_CFG_REL="scripts/config.txt"   # in the repo
NEW_CFG="$DEST/$NEW_CFG_REL"

echo "=== JShoo Pi bootstrap ==="

# Step 1: Clone or update repo
echo "Cloning (or updating) repo to $DEST ..."
if [ -d "$DEST/.git" ]; then
  sudo -u "$USERNAME" git -C "$DEST" pull
else
  sudo -u "$USERNAME" git clone "$REPO" "$DEST"
fi

# Step 2: Replace /boot/config.txt with version from repo
echo "Replacing /boot/config.txt with $NEW_CFG_REL"
sudo cp "$NEW_CFG" "$BOOT_CFG"
echo "/boot/config.txt updated — reboot required for SPI/I2C to take effect."

# Step 3: Run install selector
cd "$DEST/installers"

echo ""
echo "Select node type to install:"
select CHOICE in "Camera node" "Geophone node" "Brain node" "Quit"; do
  case $CHOICE in
    "Camera node")  sudo bash install_camera.sh  ; break ;;
    "Geophone node")sudo bash install_geophone.sh; break ;;
    "Brain node")   sudo bash install_brain.sh   ; break ;;
    "Quit")         exit 0 ;;
  esac
done
