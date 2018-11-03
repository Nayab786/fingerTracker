from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import pyautogui




y=0
yprev=0
framecount=0
flag=0
interval=100
difference=30
start=0
dbl=0
clickcounter=0


def drawbox(center,framecount):
    mystr=str(center)+","+str(framecount)
    cv2.rectangle(frame, (0, 0), (100, 60), (255, 255, 255), -1)
    cv2.putText(frame, mystr,(10,30),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    pyautogui.moveTo(center[0], center[1])

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())



greenLower = (80, 120, 120)
greenUpper = (180, 255, 255)
pts = deque(maxlen=args["buffer"])


if not args.get("video", False):
    vs = VideoStream(src=0).start()
else:
    vs = cv2.VideoCapture(args["video"])


time.sleep(0)

while True:
    framecount+=1
    img2 = vs.read()
    frame = cv2.flip(img2, 1)

    frame = frame[1] if args.get("video", False) else frame

    if frame is None:
        break


    frame = imutils.resize(frame, width=640)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    center = None


    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 10:

            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    pts.appendleft(center)
    if start==1:
        if center is None:
            if dbl==0:
                clickcounter+=1
                if clickcounter==50:
                    pyautogui.click(clicks=2)
                    dbl==1

    if center is not None:
        drawbox(center,framecount)
        start=1
        dbl=0
        clickcounter=0
        '''if (framecount%interval!=0):
            print('called'+str(framecount))
            if flag==0:
                yprev=center[1]
                flag=1
            else:
                y=center[1]
                if y-yprev<-difference:
                    pyautogui.press('up')
                    print('keyup'+str(framecount))
                    yprev=y'''
    else:
        flag=0

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
