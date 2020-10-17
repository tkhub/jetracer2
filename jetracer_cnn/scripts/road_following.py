#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import torch
import torchvision
from torch2trt import torch2trt
from torch2trt import TRTModule
from jetracer.nvidia_racecar import NvidiaRacecar

import nanocamera as nano
import Jetson.GPIO as GPIO

from utils import preprocess
import numpy as np


def execute():
    print("start")
    CATEGORIES = ['apex']

    device = torch.device('cuda')
    model = torchvision.models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(512, 2 * len(CATEGORIES))
    model = model.cuda().eval().half()
    # model.load_state_dict(torch.load('model.pth'))
    model.load_state_dict(torch.load('data/model.pth'))

    print("1")

    data = torch.zeros((1, 3, 224, 224)).cuda().half()

    model_trt = torch2trt(model, [data], fp16_mode=True)

    torch.save(model_trt.state_dict(), 'road_following_model_trt.pth')

    print("2")

    model_trt = TRTModule()
    model_trt.load_state_dict(torch.load('road_following_model_trt.pth'))
    print("model load end")

    car = NvidiaRacecar()

        # Left Camera
    camera0 = nano.Camera(device_id=0, flip=2, width=224, height=224, fps=60)
        # Right Camera
    camera1 = nano.Camera(device_id=1, flip=2, width=224, height=224, fps=60)


    STEERING_GAIN = 0.75
    STEERING_BIAS = 0.00

    car.throttle = 0.15
    cnt = 0
    while True:
        image = camera0.read()
        image = preprocess(image).half()
        output = model_trt(image).detach().cpu().numpy().flatten()
        x = float(output[0])
        car.steering = x * STEERING_GAIN + STEERING_BIAS
        print(str(cnt) + ":" + str(x) + ":" )
        cnt = cnt + 1


if __name__ == '__main__':
    execute()