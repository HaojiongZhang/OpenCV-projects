import cv2 as cv
import time
import mediapipe as mp
import os
import math
import numpy as np
import pyautogui
#pip install pycaw encapsulates the following lib
#note macOS works with osascript
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class handDetector():
    def __init__(self, mode=False,maxHands=2,detectionCon=0.6,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode,self.maxHands,self.detectionCon,self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface,POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()

        self.path = os.path.abspath(__file__)
        self.path = os.path.dirname(self.path)

        self.width = 1280
        self.height = 480
        self.stime = [0.0,0.0,0.0,0.0]
        # 0: virtual mouse[click interval]  1: hide desktop 2: fps 3: virtual mouse[hold]
        
        self.plocX = 0.0
        self.plocY = 0.0

        self.hold = False

    #find and draw hands 
    def findHands(self,img,draw=True):
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,handLms,self.mpHands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self,img,handNo=0,draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h,w,c=img.shape
                cx,cy=int(lm.x*w),int(lm.y*h)
                lmList.append([id,cx,cy])
                if draw:
                    cv.circle(img,(cx,cy),15,(255,0,255),cv.FILLED)
        return lmList 

    #set the volume through hand gesture
    def setVolume(self,img,lmList,draw=True):
        if len(lmList) != 0:
            x1,y1 = lmList[4][1],lmList[4][2]   #thumb tip
            x2,y2 = lmList[12][1],lmList[12][2]   #middle finger tip
            cx,cy = (x1+x2)/2,(y1+y2)/2
            length = math.hypot(x2-x1,y2-y1)
            cv.line(img,(x1,y1),(x2,y2),(255,0,255),3)
            
            #handrange 50 - 150 change according to hand size
            vol = np.interp(length,[50,150],[self.volRange[0],self.volRange[1]])
            self.volume.SetMasterVolumeLevel(vol,None)


    #take a screenshot and store it in the given path
    def screenShot(self,lmList,img,path='myscreenshot.png'):
        point1 = lmList[8]
        point2 = lmList[2]
        point3 = lmList[4]
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
    
    #set the time stamp
    def setTime(self,ind):
        self.stime[ind] = time.time()
    
    def setpLoc(self,x,y):
        self.plocX = x
        self.plocY = y

    #check the passed time
    def passTime(self,num,ind):
        cur = time.time()
        return (cur-self.stime[ind])>=num

    #check if right hand
    def rightHand(self,lmList):
        return(lmList[4][1]<lmList[20][1])
    
    #hide the desktop
    def hideDesk(self,lmList):
        pyautogui.press(["win","d"])


    #moves mouse with index finger, two fingers for clicking
    def virtualMouse(self,lmList,smooth=3):
        width,height = pyautogui.size()
        if len(lmList)!=0:
            x1,y1 = lmList[8][1:]   #index finger loc
            x2,y2 = lmList[12][1:]

            #cv.rectangle(img,(red,red),(self.width-red,self.height-red),(255,0,255),2)
  
            if(self.countFinger(lmList,[1])):
                
                x = np.interp(x1,[200,1080],[0,width])
                x = width - x
                y = np.interp(y1,[200,280],[0,height])
                x = self.plocX+(x-self.plocX)/smooth
                y = self.plocY+(y-self.plocY)/smooth
                self.setpLoc(x,y)
                
               # print(x,y)
                pyautogui.moveTo(x,y)
                if(self.countFinger(lmList,[1,2]) ):
                    length = math.hypot(x2-x1,y2-y1)
                    #print(length)
                    #print(self.stime[3])
                    if length <45 and self.passTime(1,0):
                        pyautogui.mouseDown()
                        print("dragging")
                    elif length<45 and self.passTime(1,0):
                        pyautogui.click()
                        self.setTime(0)
                        print("click")

                    elif length>45:
                        pyautogui.mouseUp()
                        self.setTime(3)
                        print("mouseup")
    #count how many fingers are in use
    def countFinger(self,lmList,index = []):
        tipIds = [4,8,12,16,20]
        fingers = []

        if len(lmList)!=0:
            if self.rightHand(lmList):
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
        if not index:
            return fingers.count(1)
        elif lmList:
            allup = True
            for num in index:
                if fingers[num]==0 or fingers.count(1)>3 :
                    allup = False
            return allup
    #show fps
    def showFPS(self,img):
        cTime = time.time()
        pTime = self.stime[2]
        fps = 1/(cTime-pTime)
        pTime = cTime
        self.setTime(2)
        msg = "FPS:"+str(int(fps))
        cv.putText(img,msg,(10,70),cv.FONT_HERSHEY_SIMPLEX,1,(255,255,0),3)
        return img
        

def main():
    cap = cv.VideoCapture(0)
    detector = handDetector()
    wCam, hCam = 1280,480
    cap.set(3,wCam)
    cap.set(4,hCam)

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        img = cv.flip(img,1)
        
        lmList = detector.findPosition(img,draw=False) 
        #detector.setVolume(img,lmList)
        #if len(lmList)!=0:
            #detector.screenShot(lmList,img)
            
        img = detector.showFPS(img)

        #print(detector.countFinger(lmList,[1,2]))
        detector.virtualMouse(lmList)
        cv.imshow("Image",img)

        if cv.waitKey(20) & 0xFF==ord('d'):
            break
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()