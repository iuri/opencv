#!/bin/bash
# Activate OpenCV virtual enviuronment
source /home/pi/Applications/OpenCV-master-py3/bin/activate
# Got to Qonteo app home directory
cd /home/pi/Applications/qonteo
# Launch Watcher
python3 watcher.py &
# Launch Detect Faces
python3 detectFacesEyes.py
