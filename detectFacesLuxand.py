#!/usr/bin/env python3
from __future__ import print_function
import sys, fsdk, math
from fsdk import FSDK



import numpy as np
import io, cv2
from os import sys, path

import time, requests


def watcher():
  print("Running WATCHER.py...")
  path_to_watch = "."
  before = dict ([(f, None) for f in os.listdir (path_to_watch)])
  while 1:
    print("searching for files...")
    time.sleep (10)
    after = dict ([(f, None) for f in os.listdir (path_to_watch)])
    added = [f for f in after if not f in before]
    print(" Added", added)
    removed = [f for f in before if not f in after]
    if added: 
      print("Added: ", ", ".join (added))
      for f in added:
        headers = {'X-Auth-Token': '9fb6e731-b342-4952-b0c1-aa1d0b52757b', 'Content-Type': 'image/jpeg'}
        with open(f,'rb') as fp:
          data = fp.read()   
        response = requests.post("https://luna.qonteo.com:9000/4/storage/descriptors?estimate_attributes=1&estimate_emotions=1",data=data,headers=headers)
        # response = requests.post("https://dashboard.qonteo.com/REST/upload-face", data=data,headers=headers)
        print(response.text)
        os.remove(f)
    else:
      break
    if removed: print("Removed: ", ", ".join (removed))
    before = after



def detectFaces():
  license_key = "rzpo8cK5Eo1ap4N7ov63Y/eNdNk2Y85pSlAaLuMGCWIXUwg2Slz0byvKIdavKHSPPdXwCR748LlyHWIKvf5STT+GLPTEO3aWGIR8QpMTc7yGtiYdkXKCVAcrSlFWkgmnsqW2SgJx6bMkidD+LHWJ44B+EUbIFJ2iZtgJJvPH4Yo="

  FONT_SIZE = 30

  print("Initializing FSDK... ", end='')
  FSDK.ActivateLibrary(license_key); 
  FSDK.Initialize()
  print("OK\nLicense info:", FSDK.GetLicenseInfo())

  # url = 'rtsp://admin:Qont3o123@192.168.1.14:554/profile2/media.smp'
  url = 'rtsp://admin:FXGIQA@186.241.25.44:554'
  video_capture = cv2.VideoCapture(url)
  while True:
    ret, img = video_capture.read()
    # print("captured frame...")
    # encode
    buffer = cv2.imencode('.jpg', img)[1].tobytes()
    #cv2.imwrite("buffer-im.jpg", buffer)
    cv2.imwrite("original-img.jpg", img)
    # print("written image")
    type(buffer)
    io_buf = io.BytesIO(buffer)
    height, width, channels = img.shape

    # enum FSDK_IMAGEMODE
    # FSDK_IMAGE_GRAYSCALE_8BIT = 0, FSDK_IMAGE_COLOR_24BIT = 1, FSDK_IMAGE_COLOR_32BIT = 2
    imageMode = 1

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_height, gray_width = gray.shape
    scanLine = gray_width * 3
    #    print("LEN(BUFFER) {0} >= HEIGHT*SCANLINE {1} ??? {2}".format(len(buffer),(height*scanLine), resp))
    #    print("SIZE 5760 * 1080 = {0} ??? {1}".format((5760*1080), img.size))
    #    print("HEIGHT ", height)
    #    print("WIDTH ", width)
    #    print("IMAGEMODE ", imageMode)
    #    print("SCANLINE ", scanLine)
    # print("IMAGE ", buffer)
    # insert Luxand's call here 
    # FSDK_LoadImageFromBuffer(f, buffer, width, height, scanLine, imageMode)
    # print("Calling FSDK.LoadImageFromBuffer")
    # res = FSDK.LoadImageFromBuffer(buffer, int(width), int(height), int(scanLine), imageMode)
    # res = FSDK.LoadImageFromJpegBuffer(HImage* Image, unsigned char* Buffer, unsigned int BufferLength)
    res = FSDK.LoadImageFromJpegBuffer(buffer,len(buffer)) 
    # print("RESULT ", res)
    try:
      face_position = res.DetectFace() # image.DetectMultipleFaces() returns the list of all found face's positions
      print("FACEPOSITION", face_position)
      template = res.GetFaceTemplate(face_position) # calculate face template at given position
      print("TEMPLATE ", template)
      # features = res.DetectFacialFeatures(face_position) # find facial features at given position
      # print("FEATURES ", features)
      # templates = res.GetFaceTemplate()
      # print("TEMPLATES ", templates)
      watcher()
      features = res.DetectFacialFeatures()
      print("FEATURES ", features)
      age = res.DetectFacialAttributeUsingFeatures(features, "Age")
      print("AGE ", age)


    except Exception as e:
      print("FACE NOT FOUND", e)
    #This breaks on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
  video_capture.release()
  cv2.destroyAllWindows()



def main():
  detectFaces()

if __name__ == "__main__":
	main()
