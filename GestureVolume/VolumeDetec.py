import cv2 as cv
import time
import numpy as np
from HandTrackingModule import handDetector as htm
import math
import pyautogui


def findAngle(point1,point2,point3,img,path='myscreenshot.png'):
    try:
        m1 = (point1[2]-point2[2])/(point1[1]-point2[1])
        m2 = (point3[2]-point2[2])/(point3[1]-point2[1])
        cv.line(img,(point1[1],point1[2]),(point2[1],point2[2]),(255,0,255),2)
        cv.line(img,(point3[1],point3[2]),(point2[1],point2[2]),(255,0,255),2)
    except ZeroDivisionError:
        cv.imwrite(path,img)
        return True
    angle = math.atan((m2-m1)/(1+m2*m1))
    angle = abs(angle)*180/math.pi
    if(angle>84):
        cv.imwrite(path,img)
        return True
def rightHand(lmList):
    return (lmList[4][1]<lmList[20][1])
    
def countFinger(lmList,index = []):
    tipIds = [4,8,12,16,20]
    fingers = []

    if len(lmList)!=0:
        if rightHand(lmList):
            if lmList[tipIds[0]][1]<lmList[tipIds[0]-1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            if lmList[tipIds[0]][1]>lmList[tipIds[0]-1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        for id in range(1,5):
            if lmList[tipIds[id]][2]<lmList[tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        print(fingers)
    if not index:
        return fingers.count(1)
    elif lmList:
        allup = True
        for num in index:
            if fingers[num]==0 or fingers.count(1)>3 :
                allup = False
        return allup
wCam, hCam = 1280,480
cap = cv.VideoCapture(0,cv.CAP_DSHOW)

detector = htm(detectionCon=0.7)
vol = 0

while True:
    success, img = cap.read()
    img = cv.flip(img,1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw = False)
    
    if len(lmList)!=0:
        x1,y1 = lmList[8][1:]   #index finger loc
        x2,y2 = lmList[12][1:]  #middle finger loc

    print(countFinger(lmList,[1,2]))


    cv.imshow('frame',img)
    if cv.waitKey(20) & 0xFF==ord('d'):
            break
cv.destroyAllWindows()