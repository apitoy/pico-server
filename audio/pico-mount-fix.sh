#!/bin/bash

echo "=== Pico Mount Fix Tool ==="
echo "Checking current mounts..."
mount | grep CIRCUITPY

echo -e "\nChecking device permissions..."
ls -la /run/media/tom/CIRCUITPY/ 2>/dev/null

echo -e "\nChecking USB devices..."
lsusb | grep -i "2e8a"

echo -e "\nAttempting to fix permissions..."
if [ -d "/run/media/tom/CIRCUITPY" ]; then
    sudo chown -R tom:tom /run/media/tom/CIRCUITPY/
    sudo chmod -R 755 /run/media/tom/CIRCUITPY/
fi

echo -e "\nCreating udev rule..."
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="0003", MODE="0666"' | sudo tee /etc/udev/rules.d/99-pico.rules

echo -e "\nReloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo -e "\nChecking system logs for USB errors..."
dmesg | grep -i "usb" | tail -n 20

echo -e "\nTry unplugging and plugging the Pico back in..."
echo "If the problem persists, try mounting manually with:"
echo "sudo mount -t vfat -o rw,uid=$(id -u),gid=$(id -g),umask=000 /dev/sdX /mnt/pico"

# Check if filesystem is corrupt
echo -e "\nChecking for filesystem errors..."
if [ -b "/dev/sdX" ]; then
    sudo fsck.vfat -n /dev/sdX
fi

# Print mount options if device is mounted
echo -e "\nCurrent mount options:"
mount | grep CIRCUITPY

# Try to remount with different options if mounted
if mount | grep -q CIRCUITPY; then
    echo "Attempting to remount with full permissions..."
    sudo mount -o remount,rw,uid=$(id -u),gid=$(id -g),umask=000 /run/media/tom/CIRCUITPY
fi