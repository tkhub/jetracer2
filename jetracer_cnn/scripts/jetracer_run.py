#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import datetime
import threading
from enum import Enum, auto
import cv2
import uuid
import time
import numpy as np
from jetracer_move import jetracerMove

import nanocamera as nano
# jetracerが独占しているので使えない
# import Jetson.GPIO as GPIO

from jetracer_model import prepare_torch_trt
from jetracer_model import result_torch

from jetracer.nvidia_racecar import NvidiaRacecar
import jetracer_move

from utils import preprocess

intrMsg = "go"
STEERING_GAIN = -0.40
STEERING_BIAS = 0.1
STEERING_LIM = 0.65

THROTTLE_GAIN = -0.23
THROTTLE_BIAS = 0.00
THROTTLE_FWLIM = 0.30
THROTTLE_BKLIM = 0.075
IMPLSINV  = 7

"""
STEERING_GAIN =-0.4
STEERING_BIAS =0.1
THROTTLE_GAIN =-0.23
THROTTLE_BIAS =0.05
THROTTLE_FWLIM =0.3
THROTTLE_BKLIm =0.1
"""

# 状態状態遷移用変数
class runsq(Enum):
    INIT = auto()
    PRE = auto()
    GOPAUSE = auto()
    GO = auto()

runst = runsq.INIT
runmon = False

#car = NvidiaRacecar()
car = jetracerMove()
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

def runCountDown():
    print("!!!! COUNT DOWN !!!!")
    print("3...")
    time.sleep(1)
    print("2..")
    time.sleep(1)
    print("1.")
    time.sleep(1)
    print("!!!! START !!!!")


def prepare(cameraL, cameraR):
    global car
    print("#---- prepare system ----#")
    print("## camera test")
    imgL = cameraL.read()
    imgR = cameraR.read()
    s_uuid = str(uuid.uuid1())
    dt_now = datetime.datetime.now()
    datestr = dt_now.strftime('%y_%m_%d_%H_%M_%S')
    # filename = filepath + '%d_%d_%s.jpg' % (0, 0, s_uuid))
    filenameMx = './nanocam_test/%d_%d_%s.jpg' % (0, 0, datestr)
    filenameL = './nanocam_test/%d_%d_%s.jpg' % (0, 0, datestr)
    filenameR = './nanocam_test/%d_%d_%s.jpg' % (0, 0, datestr)
    cv2.imwrite(filenameL, imgL)
    cv2.imwrite(filenameR, imgR)
    imgMx = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)
    cv2.imwrite(filenameMx, imgMx)
    print("## car test")
    print("!!!! CAR WILL MOVE !!!!")
    print("car zeroing")
    car.Steering(0.0)
    car.Throttle(0.0, False)
    okng = input("OK/ng>>")
    if okng == "OK":
        print("car zeroing")
        car.Steering(0.0)
        car.Throttle(0.0, False)
        print("Left")
        car.Steering(1)
        time.sleep(1)

        print("Right")
        car.Steering(-1)
        time.sleep(1)

        car.Steering(0.0)

        print("FORWARD")
        car.Throttle(0.2, False)
        time.sleep(0.2)
        car.Throttle(0.0, False)
        
        print("BREAK")
        car.Throttle(-0.5, False)
        time.sleep(0.5)
        car.Throttle(0, False)

        print("BACKWARD")
        car.Throttle(-0.3, True)
        time.sleep(0.2)
        car.Throttle(0.0, True)
    else:
        print("skip...")


    print("## model prepaer")
    model = prepare_torch_trt()
    return model
####

def prepare_old(cameraL, cameraR):
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
    print("car zeroing")
    car.steering = 0.0 
    car.throttle = 0.0
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
def autorun_old(cameraL, cameraR, model, recpath, recintv):
    global STEERING_GAIN
    global STEERING_BIAS
    global STEERING_LIM
    global THROTTLE_GAIN
    global THROTTLE_BIAS
    global THROTTLE_FWLIM
    global THROTTLE_BKLIM
    global intrMsg
    global runmon

    
    s_uuid = str(uuid.uuid1())
    dt_now = datetime.datetime.now()
    datestr = str(dt_now.strftime('%Y_%m_%d_%H:%M:%S'))
    cnt = 0    
    ys = 0.0
    while intrMsg != "QUIT":
        car.steering = 0.0
        car.throttle = 0.0
        runmon = False
        runmon_tmp = False
        while intrMsg != "PAUSE" and intrMsg != "QUIT":
            runmon = True
            if runmon and not runmon_tmp:
                print("autorun active!")
                runCountDown()
            # zaku
            #img = cameraR.read()

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
            if 0 < y and y < 0.15:
                if cnt % IMPLSINV == 0:
                    ys = 0.35
                    y = 0.35
            else:
                if 0.4 > abs(x):
                    if y > 0.2:
                        y  = 0.2
                    

            ys = (y - ys) * 0.5 + ys
            car.steering = x
            car.throttle = ys
            cnt = cnt + 1
           # if (cnt % recintv) == 0:
           #     recfile = recpath + '%s_%d_%d_%d_%s.jpg' % (datestr,cnt, int(x * 100), int(y * 100), s_uuid)
           #     cv2.imwrite(recfile, img)
            runmon_tmp = runmon
    car.steering = 0.0
    car.throttle = 0.0
    print("# auto run end...")
####
def autorun(cameraL, cameraR, model, recpath, recintv):
    global STEERING_GAIN
    global STEERING_BIAS
    global STEERING_LIM
    global THROTTLE_GAIN
    global THROTTLE_BIAS
    global THROTTLE_FWLIM
    global THROTTLE_BKLIM
    global intrMsg
    global runmon

    
    s_uuid = str(uuid.uuid1())
    dt_now = datetime.datetime.now()
    datestr = str(dt_now.strftime('%Y_%m_%d_%H:%M:%S'))
    cnt = 0    
    ys = 0.0
    while intrMsg != "QUIT":
        car.steering = 0.0
        car.throttle = 0.0
        runmon = False
        runmon_tmp = False
        while intrMsg != "PAUSE" and intrMsg != "QUIT":
            runmon = True
            if runmon and not runmon_tmp:
                print("autorun active!")
                runCountDown()
            # zaku
            #img = cameraR.read()

            # gundam
            imgL = cameraL.read()
            imgR = cameraR.read()
            img = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)

            output = result_torch(model, img)

            x = float(output[0])* STEERING_GAIN + STEERING_BIAS 
            y = float(output[1]) * THROTTLE_GAIN + THROTTLE_BIAS
            car.Steering(x)
            car.Throttle(y,False)
            cnt = cnt + 1
           # if (cnt % recintv) == 0:
           #     recfile = recpath + '%s_%d_%d_%d_%s.jpg' % (datestr,cnt, int(x * 100), int(y * 100), s_uuid)
           #     cv2.imwrite(recfile, img)
            runmon_tmp = runmon
    car.Steering(0)
    car.Throttle(0, False)
    print("# auto run end...")

def commander():
    global STEERING_GAIN
    global STEERING_BIAS
    global STEERING_LIM
    global THROTTLE_GAIN
    global THROTTLE_BIAS
    global THROTTLE_FWLIM
    global THROTTLE_BKLIM
    global intrMsg
    while intrMsg != "QUIT":
        cmd = input("Pause?(yes/no)>>")
        if cmd == "yes":
            intrMsg = "PAUSE"
            cmd = input("input command(gain/start/quit)>>")
            if cmd == "gain":
                # STEERING GAIN setting 
                ver = input("STEERING_GAIN = " +str(STEERING_GAIN)+ "(float/\"keep\")>>")
                if ver != "keep":
                    STEERING_GAIN = float(ver)
                    print("STEERING_GAIN was updated to " +str(STEERING_GAIN))

                # STEERING BIAS setting 
                ver = input("STEERING_BIAS = " +str(STEERING_BIAS)+ "(float/\"keep\")>>")
                if ver != "keep":
                    STEERING_BIAS = float(ver)
                    print("STEERING_GAIN was updated to " +str(STEERING_BIAS))

                # THROTTLE_GAIN setting 
                ver = input("THROTTLE_GAIN = " +str(THROTTLE_GAIN)+ "(float/\"keep\")>>")
                if ver != "keep":
                    THROTTLE_GAIN = float(ver)
                    print("STEERING_GAIN was updated to " +str(THROTTLE_GAIN))
                # THROTTLE_BIAS setting 
                ver = input("THROTTLE_BIAS = " +str(THROTTLE_BIAS)+ "(float/\"keep\")>>")
                if ver != "keep":
                    THROTTLE_BIAS = float(ver)
                    print("THROTTLE_BIAS was updated to " +str(THROTTLE_BIAS))

                ver = input("THROTTLE_FWLIM = " +str(THROTTLE_FWLIM)+ "(float/\"keep\")>>")
                if ver != "keep":
                    THROTTLE_FWLIM = float(ver)
                    print("THROTTLE_FWLIM was updated to " +str(THROTTLE_FWLIM))

                ver = input("THROTTLE_BKLIM = " +str(THROTTLE_BKLIM)+ "(float/\"keep\")>>")
                if ver != "keep":
                    THROTTLE_BKLIM = float(ver)
                    print("THROTTLE_FWLIM was updated to " +str(THROTTLE_BKLIM))

                print("STEERING_GAIN =" +str(STEERING_GAIN))
                print("STEERING_BIAS =" +str(STEERING_BIAS))
                print("THROTTLE_GAIN =" +str(THROTTLE_GAIN))
                print("THROTTLE_BIAS =" +str(THROTTLE_BIAS))
                print("THROTTLE_FWLIM =" +str(THROTTLE_FWLIM))
                print("THROTTLE_BKLIm =" +str(THROTTLE_BKLIM))
                intrMsg = "GO"
            elif cmd == "start":
                intrMsg = "GO"
            elif cmd == "quit":
                intrMsg = "QUIT"
    print("commander end...")

def execute():
    global intrMsg
    # init
    cameraL, cameraR = init()

    # model prepare
    model = prepare(cameraL, cameraR)

    # wait user go
    OKng = input("RUN OK/ng >>")
    if OKng != "OK":
        return
    # run and command wait
    intrMsg = "GO"
    #thrdAutoRun = threading.Thread(target=autorun, args=(cameraL, cameraR, model, "./autorunrec/", 20))
    thrdCommander = threading.Thread(target=commander)
    thrdCommander.start()
    autorun(cameraL, cameraR, model, "./autorunrec/", 20)
    #autorun_old(cameraL, cameraR, model, "./autorunrec/", 20)
    #thrdAutoRun.start() 
    thrdCommander.join()
    #thrdAutoRun.join()
    del cameraR
    del cameraL
    print("# ---- END ----")

if __name__ == '__main__':
    # global runst
    execute()
