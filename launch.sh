#!/bin/bash
# Activate OpenCV virtual enviuronment
source /home/qonteo/opencv/OpenCV-master-py3/bin/activate
# Got to Qonteo app home directory
cd /home/qonteo/opencv
# Launch Watcher
python3 watcher.py &
# Launch Detect Faces
python3 detectFacesEyes.py
