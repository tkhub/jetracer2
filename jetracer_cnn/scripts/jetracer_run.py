#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from enum import Enum, auto
import cv2
import uuid
import time
import numpy as np

import nanocamera as nano
# jetracerが独占しているので使えない
# import Jetson.GPIO as GPIO

from jetracer_model import prepare_torch
from jetracer_model import result_torch

from jetracer.nvidia_racecar import NvidiaRacecar

from utils import preprocess

# 状態状態遷移用変数
class runsq(Enum):
    INIT = auto()
    PRE = auto()
    GOPAUSE = auto()
    GO = auto()

runst = runsq.INIT

car = NvidiaRacecar()
throttleflg = True

def init():
    print("#---- init system ----#")
    cameraL, cameraR = init_nanocam(224,224,120,2)
    return cameraL, cameraR 



def init_nanocam(imgwd, imghg, fpsc, angle):
    # Left Camera
    cameraL = nano.Camera(device_id=0, flip=angle, width=imgwd, height=imghg, fps=fpsc)
    # Right Camera
    cameraR = nano.Camera(device_id=1, flip=angle, width=imgwd, height=imghg, fps=fpsc)
    return cameraL, cameraR

def prepare(cameraL, cameraR):
    global car
    print("#---- prepare system ----#")
    print("## camera test")
    imgL = cameraL.read()
    imgR = cameraR.read()
    s_uuid = str(uuid.uuid1())
    # filename = filepath + '%d_%d_%s.jpg' % (0, 0, s_uuid))
    filenameMx = './nanocam_test/%d_%d_%s.jpg' % (0, 0, s_uuid)
    filenameL = './nanocam_test/%d_%d_%s.jpg' % (0, 0, s_uuid)
    filenameR = './nanocam_test/%d_%d_%s.jpg' % (0, 0, s_uuid)
    cv2.imwrite(filenameL, imgL)
    cv2.imwrite(filenameR, imgR)
    imgMx = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)
    cv2.imwrite(filenameMx, imgMx)
    print("## car test")
    print("!!!! CAR WILL MOVE !!!!")
    okng = input("OK/ng>>")
    if okng == "OK":
        print("car zeroing")
        car.steering = 0.0 
        car.throttle = 0.0
        print("Left")
        car.steering = 0.65
        time.sleep(1)

        print("Right")
        car.steering = -0.65
        time.sleep(1)

        car.steering = 0.0 

        print("FORWARD")
        car.throttle = 0.3
        time.sleep(0.2)
        car.throttle = 0.0
        
        print("BREAK")
        car.throttle = -0.5
        time.sleep(0.2)
        car.throttle = 0.0

        print("BACKWARD")
        car.throttle = -0.3
        time.sleep(0.2)
        car.throttle = 0.0
    else:
        print("skip...")


    print("## model prepaer")
    model = prepare_torch()
    return model
####


####
def autorun(cameraL, cameraR, model, str_inv, thr_inv, recpath, recintv):
    s_uuid = str(uuid.uuid1())
    STEERING_GAIN = 0.75
    STEERING_BIAS = 0.00
    STEERING_LIM = 0.65

    THROTTLE_GAIN = 0.75
    THROTTLE_BIAS = 0.0
    THROTTLE_FWLIM = 0.5
    THROTTLE_BKLIM = -0.3

    if str_inv:
        STEERING_GAIN = STEERING_GAIN * -1
        STEERING_BIAS = STEERING_BIAS * -1
    
    if thr_inv:
        THROTTLE_GAIN = THROTTLE_GAIN * -1
        THROTTLE_BIAS = THROTTLE_BIAS * -1
    cnt = 0    
    while True:
        # zaku
        # img = cameraR.read()

        # gundam
        imgL = cameraL.read()
        imgR = cameraR.read()
        img = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)

        imgh = preprocess(img).half()
        output = model(imgh).detach().cpu().numpy().flatten()

        x = float(output[0])* STEERING_GAIN + STEERING_BIAS 
        if x < (STEERING_LIM * -1):
            x = STEERING_LIM * -1
        if STEERING_LIM < x:
            x = STEERING_LIM
        
        y = float(output[1]) * THROTTLE_GAIN + THROTTLE_BIAS
        if y < THROTTLE_BKLIM:
            y = THROTTLE_BKLIM
        if THROTTLE_FWLIM < y:
            y = THROTTLE_FWLIM
        car.steering = x
        car.throttle = y
        cnt = cnt + 1
        if (cnt % recintv) == 0:
            recfile = recpath + '%d_%d_%d_%s.jpg' % (cnt, int(x * 100), int(y * 100), s_uuid)
            cv2.imwrite(recfile, img)

def car_DRB(throttle):
    pass

def execute():
    cameraL, cameraR = init()
    model = prepare(cameraL, cameraR)
    try:
        autorun(cameraL,cameraR,model, True, False, "./autorunrec/", 10)
    except KeyboardInterrupt:
        print("stop")
    del cameraR
    del cameraL

if __name__ == '__main__':
    # global runst
    execute()
