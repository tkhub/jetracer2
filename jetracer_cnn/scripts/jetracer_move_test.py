#!/usr/bin/env python3

from jetracer.nvidia_racecar import NvidiaRacecar
car = NvidiaRacecar()
print(car)

steering = 0.0
steering_center = 0.0
steering_leftlim = 0.0
steering_rightlim = 0.0
exitflg = False 
print("jetracer test....")
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
        elif var == 'l':
            # 前回値を左リミットとして保存する
            throttle_forwardlim = throttle
            print("leftlim = " +str(throttle_forwardlim))
        elif var == 't':
            # 前回値を左リミットとして保存する
            throttle_forwardth = throttle
            print("leftlim = " +str(throttle_forwardth))
        elif var == 'r':
            # 前回値を右リミットとして保存する
            throttle_backwardlim = throttle
            print("rightlim = " +str(throttle_backwardlim))
        else:
            try:
                throttle = float(var)
            except:
                print(var +" is not number. Next.")
                break
            print("throttle = " + str(throttle))
        car.throttle = throttle


print("steering_center = " +str(steering_center))
print("steering_leftlim = " +str(steering_leftlim))
print("steering_rightlim = " +str(steering_rightlim))
print("throttle_center = " +str(throttle_center))
print("throttle_forwardlim = " +str(throttle_forwardlim))
print("throttle_forwardth = " +str(throttle_forwardth))
print("throttle_backwardlim = " +str(throttle_backwardlim))
