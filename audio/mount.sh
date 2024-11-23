#!/bin/bash

ls -la /run/media/tom/CIRCUITPY/
sudo chown -R tom:tom /run/media/tom/CIRCUITPY/
sudo chmod -R 755 /run/media/tom/CIRCUITPY/

exit 1
sudo umount /run/media/tom/CIRCUITPY
sudo mount -o uid=$(id -u),gid=$(id -g) /dev/sdX /run/media/tom/CIRCUITPY  # gdzie sdX to właściwe urządzenie


sudo nano /etc/udev/rules.d/99-pico.rules
sudo udevadm control --reload-rules
sudo udevadm trigger


sudo mount -t vfat -o rw,uid=$(id -u),gid=$(id -g),umask=000 /dev/sdX /mnt/pico