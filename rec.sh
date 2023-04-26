#!/usr/bin/env sh

pc="phyOS"

sudo rmmod -f v4l2loopback
sudo modprobe v4l2loopback exclusive_caps=1 card_label=$pc max_buffers=2
(python rec1.py && disown) &
