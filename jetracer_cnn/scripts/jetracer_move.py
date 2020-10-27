#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from jetracer.nvidia_racecar import NvidiaRacecar

class jetracerMove(NvidiaRacecar):
    def __init__(self):
        super(jetracerMove,self).__init__()
        # Left, Right Lim
        self.__STEERINGINV = False
        self.__STEERINGLIM = [0.65, -0.65]
        
        # 
        self.__STEERINGTRIM = 0.0

        # Left, Right GAIN
        self.__STEERINGGAIN = [self.__STEERINGLIM[0] - self.__STEERINGTRIM,  abs(self.__STEERINGLIM[1]) - self.__STEERINGTRIM]

        # if Assign is inverted 
        self.__THROTTLEINV = False
        # Forward, Break, BackWard
        self.__THROTTLELIM = [0.465, -0.5, -0.5]
        self.__THROTTLETRIM = 0.0
        self.__THROTTLEWAITBK = 0.1
        self.__THROTTLEHYS = 0.065
        self.__THROTTLEZERO = 0.01
        # Forward, Break, BackWard
        self.__THROTTLEGAIN = [self.__THROTTLELIM[0] - self.__THROTTLETRIM - self.__THROTTLEHYS,  abs(self.__THROTTLELIM[1]) - self.__THROTTLETRIM - self.__THROTTLEHYS, abs(self.__THROTTLELIM[2]) - self.__THROTTLETRIM - self.__THROTTLEHYS]

    def Showsetting(self):
        print(self.__STEERINGINV)
        print(self.__STEERINGLIM)        
        # 
        print(self.__STEERINGTRIM)

        # Left, Right GAIN
        print(self.__STEERINGGAIN)

        # if Assign is inverted 
        print(self.__THROTTLEINV)
        # Forward, Break, BackWard
        print(self.__THROTTLELIM)
        print(self.__THROTTLETRIM)
        print(self.__THROTTLEWAITBK)
        print(self.__THROTTLEHYS)
        print(self.__THROTTLEZERO)
        # Forward, Break, BackWard
        print(self.__THROTTLEGAIN)
    def Steering(self, strvar):
        x = 0.0
        # inverter
        if self.__STEERINGINV:
            strvar = strvar * -1

        # Limitter
        if strvar < -1.0:
            strvar = -1.0
        if 1.0 < strvar:
            strvar = 1.0

        if strvar < 0.0:
            x = self.__STEERINGGAIN[1] * strvar + self.__STEERINGTRIM
        else:
            x = self.__STEERINGGAIN[0] * strvar + self.__STEERINGTRIM

        self.steering = x


    def Throttle(self, thrtvar, backFlg):
        y = 0.0
        if self.__THROTTLEINV:
            thrtvar = thrtvar * -1

        # Limitter
        if thrtvar < -1.0:
            thrtvar = -1.0
        if 1.0 < thrtvar:
            thrtvar = 1.0

        # ほぼゼロ
        if abs(thrtvar) < self.__THROTTLEZERO:
            y = 0.0
        # 逆転 or ブレーキ
        elif thrtvar < 0.0:
            # ブレーキ
            if backFlg:
                y = self.__THROTTLEGAIN[2] * thrtvar + self.__THROTTLETRIM + self.__THROTTLEHYS
                # 一度ブレーキ
                self.throttle = self.__THROTTLELIM[1] 
                time.sleep(self.__THROTTLEWAITBK)
                # 一度ニュートラル
                self.throttle = self.__THROTTLETRIM
                time.sleep(0.04)
                self.throttle = y
            else:
                y = self.__THROTTLEGAIN[1] * thrtvar + self.__THROTTLETRIM - self.__THROTTLEHYS
        else:
            y = self.__THROTTLEGAIN[0] * thrtvar + self.__THROTTLETRIM + self.__THROTTLEHYS
        self.throttle = y

def __move():
    car = jetracerMove()
    exitflg = False 
    print("jetracer test....")
    car.Showsetting()
    # init
    car.Steering(0)
    car.Throttle(0,False)
    print("(1/2) steering test")
    while True:
        var = input("steering (float / \"next\" / \"exit\" )=  ")

        if var == "next":
            print("Go Next..")
            break
        elif var == "exit":
            print("Exit..")
            exitflg = True
            break
        else:
            try:
                steering = float(var)
            except:
                print(var +" is not number. Next.")
                break
            print("steering = " + str(steering))
        car.Steering(steering)
        
    print("zeroing all output")
    car.Steering(0)
    car.Throttle(0,False)

    throttle = 0.0
    backFlg = False
    
    if not exitflg:
        print("(2/2) throttle test")
        while True:
            var = input("throttle  (float / \"exit\" ) = ")
            if var == "exit":
                print("Exit..")
                break
            elif var == "back":
                backFlg = True
            else:
                backFlg = False 
                try:
                    throttle = float(var)
                except:
                    print(var +" is not number. Next.")
                    break
                print("throttle = " + str(throttle))
            car.Throttle(throttle, backFlg)

    print("zeroing all output")
    car.steering = 0.0 
    car.throttle = 0.0
    car.Steering(0)
    car.Throttle(0,False)


def __directmove():
    car = NvidiaRacecar()
    print(car)

    steering = 0.0
    steering_center = 0.0
    steering_leftlim = 0.0
    steering_rightlim = 0.0
    exitflg = False 
    print("jetracer adjust....")
    # init
    car.steering = 0.0 
    car.throttle = 0.0
    print("(1/2) steering test")
    while True:
        var = input("steering or center(c) or left_lim(l) or right_lim(r)  =  ")

        if var == "next":
            print("Go Next..")
            break
        elif var == "exit":
            print("Exit..")
            exitflg = True
            break
        elif var == 'c':
            # 前回値をセンターとして保存する
            steering_center = steering
            print("center = " +str(steering_center))
        elif var == 'l':
            # 前回値を左リミットとして保存する
            steering_leftlim = steering
            print("leftlim = " +str(steering_leftlim))
        elif var == 'r':
            # 前回値を右リミットとして保存する
            steering_rightlim = steering
            print("rightlim = " +str(steering_rightlim))
        else:
            try:
                steering = float(var)
            except:
                print(var +" is not number. Next.")
                break
            print("steering = " + str(steering))
        car.steering = steering
        
    print("zeroing all output")
    car.steering = 0.0 
    car.throttle = 0.0

    throttle = 0.0
    throttle_center = 0.0
    throttle_forwardth = 0.0
    throttle_forwardlim = 0.0
    throttle_backwardlim = 0.0
    if not exitflg:

        print("(2/2) throttle test")
        while True:
            var = input("throttle or center(c) or forward Threshold(t) or forward_lim(f) or backward_lim(b)  =  ")
            if var == "exit":
                print("Exit..")
                break
            elif var == 'c':
                # 前回値をセンターとして保存する
                throttle_center = throttle
                print("center = " +str(throttle_center))
            elif var == 'f':
                # 前回値を前進リミットとして保存する
                throttle_forwardlim = throttle
                print("forwardlim = " +str(throttle_forwardlim))
            elif var == 't':
                # 前回値をバックリミットとして保存する
                throttle_forwardth = throttle
                print("leftlim = " +str(throttle_forwardth))
            elif var == 'b':
                # 前回値をバックリミットとして保存する
                throttle_backwardlim = throttle
                print("backwardlim = " +str(throttle_backwardlim))
            else:
                try:
                    throttle = float(var)
                except:
                    print(var +" is not number. Next.")
                    break
                print("throttle = " + str(throttle))
            car.throttle = throttle

    print("zeroing all output")
    car.steering = 0.0 
    car.throttle = 0.0
    print("steering_center = " +str(steering_center))
    print("steering_leftlim = " +str(steering_leftlim))
    print("steering_rightlim = " +str(steering_rightlim))
    print("throttle_center = " +str(throttle_center))
    print("throttle_forwardlim = " +str(throttle_forwardlim))
    print("throttle_forwardth = " +str(throttle_forwardth))
    print("throttle_backwardlim = " +str(throttle_backwardlim))

    """
    example
    steering_center = 0.0
    steering_leftlim = 0.2
    steering_rightlim = -0.5
    throttle_center = 0.0
    throttle_forwardlim = 0.6
    throttle_forwardth = 0.05
    throttle_backwardlim = 0.0 
    """
if __name__ == "__main__":
    cmd = input("test(\"test\" or \"\") or adjust (\"adjust\")>>")
    if cmd == "adjust":
        __directmove()
    else:
        print("move test")
        __move()
   # testmove()