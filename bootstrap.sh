#!/usr/bin/env bash
# curl -sL https://github.com/patton3/JumboShoo.git/main/bootstrap.sh | sudo bash

mkdir -p /home/a/JumboShoo
set -e
REPO="https://github.com/patton3/JumboShoo.git"
DEST="/home/a/JumboShoo"

echo "=== JShoo Pi bootstrap ==="
echo "Cloning (or updating) repo to $DEST ..."
if [ -d "$DEST/.git" ]; then
  sudo -u pi git -C "$DEST" pull
else
  sudo -u pi git clone "$REPO" "$DEST"
fi

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
