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

def recloop(camera, filepath, intv):
    global recst
    while recst == "recgo":
        img = camera.read()
        filename = filepath + '%d_%d_%s.jpg' % (0, 0, str(uuid.uuid1()))
        cv2.imwrite(filename, img)
        time.sleep(intv)

def waitrec():
    global recst
    while recst == "recpre":
        pass

def execute():
    global recst
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(21, GPIO.IN)
    GPIO.add_event_detect(21,GPIO.FALLING, callback=btn_th, bouncetime=200)

    camera0 = nano.Camera(flip=2, width=224, height=224, fps=30)
    # wait rec button
    print("REC wait ...")
    waitrec()
    # rec start
    print("REC START! ...")
    recloop(camera0, "./data/apex/", 0.1)
    print("REC END!! ...")
    camera0.release()
    # finish
    del camera0
    GPIO.cleanup()





if __name__ == '__main__':
    execute()