#!/usr/bin/env python3
import cv2
import nanocamera as nano
import Jetson.GPIO as GPIO
import uuid
import time

recst = "recpre"
def btn_th(self):
    global recst
    recst_bf = recst
    if recst == "recgo":
        recst = "recend"
    elif recst == "recend":
        recst = "recpre"
    else:
        recst = "recgo"
    print(recst_bf + "->" + recst)

def execute():
    global recst
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(21, GPIO.IN)
    GPIO.add_event_detect(21,GPIO.FALLING, callback=btn_th, bouncetime=200)

    camera0 = nano.Camera(flip=2, width=224, height=224, fps=30)
    #for i in range(100):
    while recst == "recpre":
        pass
    while recst == "recgo":
        img = camera0.read()
        #print(sw)
        # 21
        filename = './data/apex/%d_%d_%s.jpg' % (0, 0, str(uuid.uuid1()))
        #filename = './data/apex/%d.jpg' % (i)
        cv2.imwrite(filename, img)
        time.sleep(0.1)
    camera0.release()
    del camera0
    GPIO.cleanup()





if __name__ == '__main__':
    execute()