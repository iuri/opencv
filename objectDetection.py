import numpy as np
import cv2
import sys, random, string, time
import os, os.path
import logging
import config


faceCascade = cv2.CascadeClassifier('../../OpenCV/opencv/haarcascade/haarcascade_frontalface_default.xml')
# eyeCascade = cv2.CascadeClassifier('./haarcascade/haarcascade_eye.xml')
eyeCascade = cv2.CascadeClassifier('../../OpenCV/opencv/haarcascade/haarcascade_eye_tree_eyeglasses.xml')

# video_capture = cv2.VideoCapture(0)
video_capture = cv2.VideoCapture(config.camera_url)

cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
cv2.resizeWindow('Window', 400, 400)

path = "images"
os.chdir(".")

if not os.path.isdir(path):
    #now = datetime.datetime.now().strftime("%y%m%d%H%M")
    os.umask(0)
    os.makedirs(path, mode=0o777, exist_ok=False)

print("Connecting to camera ", config.camera_url) 
while True:
    ret, img = video_capture.read()
    if np.shape(img) != ():
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3, minSize=(30, 30))
        for (x, y, w, h) in faces:
            print("Potential Face!")
            cv2.rectangle(img, (x, y), (x+w, y+h), (255,0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eyeCascade.detectMultiScale(roi_gray)
            eyes = eyeCascade.detectMultiScale(roi_color)
        
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0), 2)        
                if len(eyes) != 0:
                    print("EYES", eyes)
                crop_img = img[y-99:y+h+99, x-36:x+w+36]
                if len(crop_img) != 0:
                    letters = string.ascii_lowercase
                    result_str = ''.join(random.choice(letters) for i in range(12))
                    status = cv2.imwrite("./images/"+result_str+".jpg", crop_img)
                    os.chmod("./images/"+result_str+".jpg", 0o777)
    cv2.imshow("Window",img)
                
    # This breaks on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # time.sleep(2)
video_capture.release()
cv2.destroyAllWindows()