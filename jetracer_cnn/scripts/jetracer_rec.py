#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
import nanocamera as nano
import Jetson.GPIO as GPIO
import uuid
import time


# 録画状態状態遷移用変数
recst = "recpre"

# 録画ボタンport
recbtn = 31
gobtn = 35

# 録画状態状態遷移用関数(イベント)
def btn_th(self):
    global recst
    recst_bf = recst
    if recst == "recgo":
        recst = "recend"
    elif recst == "recend":
        recst = "recpre"
    else:
        recst = "recgo"

# 録画用ループ関数
def recloop_old(camera, filepath, intv):
    global recst
    while recst == "recgo":
        img = camera.read()
        filename = filepath + '%d_%d_%s.jpg' % (0, 0, str(uuid.uuid1()))
        cv2.imwrite(filename, img)
        time.sleep(intv)

def recloopDual_old(cameraL, cameraR, filepathL, filepathR, intv):
    global recst
    while recst == "recgo":
        #img = camera.read()
        imgL = cameraL.read()
        imgR = cameraR.read()
        s_uuid = str(uuid.uuid1())
        # filename = filepath + '%d_%d_%s.jpg' % (0, 0, s_uuid))
        filenameL = filepathL + '%d_%d_%s.jpg' % (0, 0, s_uuid)
        filenameR = filepathR + '%d_%d_%s.jpg' % (0, 0, s_uuid)
        cv2.imwrite(filenameL, imgL)
        cv2.imwrite(filenameR, imgR)
        time.sleep(intv)

def recloopDual(cameraL, cameraR, filepath, intv):
    global recst
    while recst == "recgo":
        #img = camera.read()
        imgL = cameraL.read()
        imgR = cameraR.read()
        timestmp = time.time()
        # filename = filepath + '%d_%d_%s.jpg' % (0, 0, s_uuid))
        filenameL = filepath + str(timestmp) + '_L.jpg'
        filenameR = filepath + str(timestmp) + '_R.jpg'
        cv2.imwrite(filenameL, imgL)
        cv2.imwrite(filenameR, imgR)
        time.sleep(intv)

def recloopStereo_old(cameraL, cameraR, filepathMx, filepathL, filepathR, intv):
    global recst
    while recst == "recgo":
        #img = camera.read()
        imgL = cameraL.read()
        imgR = cameraR.read()
        s_uuid = str(uuid.uuid1())
        # filename = filepath + '%d_%d_%s.jpg' % (0, 0, s_uuid))
        filenameMx = filepathMx +'%d_%d_%s.jpg' % (0, 0, s_uuid)
        filenameL = filepathL + '%d_%d_%s.jpg' % (0, 0, s_uuid)
        filenameR = filepathR + '%d_%d_%s.jpg' % (0, 0, s_uuid)
        cv2.imwrite(filenameL, imgL)
        cv2.imwrite(filenameR, imgR)
        imgMx = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)
        cv2.imwrite(filenameMx, imgMx)
        time.sleep(intv)

def recloopStereo_old(cameraL, cameraR, filepathMx, filepathL, filepathR, intv):
    global recst
    while recst == "recgo":
        #img = camera.read()
        imgL = cameraL.read()
        imgR = cameraR.read()
        s_uuid = str(uuid.uuid1())
        # filename = filepath + '%d_%d_%s.jpg' % (0, 0, s_uuid))
        filenameMx = filepathMx +'%d_%d_%s.jpg' % (0, 0, s_uuid)
        filenameL = filepathL + '%d_%d_%s.jpg' % (0, 0, s_uuid)
        filenameR = filepathR + '%d_%d_%s.jpg' % (0, 0, s_uuid)
        cv2.imwrite(filenameL, imgL)
        cv2.imwrite(filenameR, imgR)
        imgMx = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)
        cv2.imwrite(filenameMx, imgMx)
        time.sleep(intv)

def testloop():
    global recst
    cnt = 0
    while recst == "recgo":
        print("loop")
        time.sleep(1)
        cnt = cnt + 1
        if cnt > 10:
            break

# 録画開始待関数
def waitrec():
    global recst
    while recst == "recpre":
        pass

def execute():
    global recst
    global recbtn
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(recbtn, GPIO.IN)
    GPIO.add_event_detect(recbtn,GPIO.FALLING, callback=btn_th, bouncetime=200)
    phpathL = "./data/apexL/"
#    phpathL = "./data/recR/"
    phpathR = "./data/apexR/"
#    phpathR = "./data/recR/"
    phpathMx = "./data/apexM/"
    os.makedirs(phpathL, exist_ok = True)
    os.makedirs(phpathR, exist_ok = True)
    os.makedirs(phpathMx, exist_ok = True)
    # Left Camera
    camera0 = nano.Camera(device_id=0, flip=2, width=224, height=224, fps=60)
    # Right Camera
    camera1 = nano.Camera(device_id=1, flip=2, width=224, height=224, fps=60)
    # wait rec button
    print("REC wait ...")
    waitrec()
    # rec start
    print("REC START! ...")
#    recloop_old(camera0, "./data/apex/", 0.1)
#    recloopDual_old(camera0,camera1, phpathL,phpathR, 0.1)
    recloopStereo_old(camera0,camera1, phpathMx, phpathL,phpathR, 0.1)
#    recloopDual(camera0,camera1, phpathL,phpathR, 0.05)
    # testloop()
    print("REC END!! ...")
    camera0.release()
    camera1.release()
    # finish
    del camera0
    GPIO.cleanup()


def new_execute():
    global recst
    global recbtn
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(recbtn, GPIO.IN)
    GPIO.add_event_detect(recbtn,GPIO.FALLING, callback=btn_th, bouncetime=200)
    phpath = "./data/rec/"
    os.makedirs(phpath, exist_ok = True)

    # Left Camera
    camera0 = nano.Camera(device_id=0, flip=2, width=224, height=224, fps=60)
    # Right Camera
    camera1 = nano.Camera(device_id=1, flip=2, width=224, height=224, fps=60)
    # wait rec button
    print("REC wait ...")
    waitrec()
    # rec start
    print("REC START! ...")
#    recloop_old(camera0, "./data/apex/", 0.1)
#    recloopDual_old(camera0,camera1, phpathL,phpathR, 0.1)
#    recloopStereo_old(camera0,camera1, phpathMx, phpathL,phpathR, 0.1)
    recloopDual(camera0,camera1, phpath, 0.05)
    # testloop()
    print("REC END!! ...")
    camera0.release()
    camera1.release()
    # finish
    del camera0
    GPIO.cleanup()




if __name__ == '__main__':
    # execute()
    new_execute()