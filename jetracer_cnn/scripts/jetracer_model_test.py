#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import torch
import torchvision
import cv2
from torch2trt import torch2trt
from torch2trt import TRTModule
from jetracer.nvidia_racecar import NvidiaRacecar

import nanocamera as nano

from utils import preprocess
import numpy as np

def prepare_torch():

    CATEGORIES = ['apex']
    device = torch.device('cuda')
    model = torchvision.models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(512, 2 * len(CATEGORIES))
    model = model.cuda().eval().half()
    # model.load_state_dict(torch.load('model.pth'))
    model.load_state_dict(torch.load('data/model.pth'))

    data = torch.zeros((1, 3, 224, 224)).cuda().half()
    model_trt = torch2trt(model, [data], fp16_mode=True)
    torch.save(model_trt.state_dict(), 'road_following_model_trt.pth')


    model_trt = TRTModule()
    model_trt.load_state_dict(torch.load('road_following_model_trt.pth'))

    return model_trt

def result_torch(model, img):
    output = model(img).detach().cpu().numpy().flatten()
    x = float(output[0])
    y = float(output[1])
    return x, y

def execute():
    print("jetracer_model_test")
    model = prepare_torch()

    print("model preper end")

    img = cv2.imread('LS_img.jpg')
    print("LS(x,y) = " +result_torch(model, img))

    img = cv2.imread('RS_img.jpg')
    print("LS(x,y) = " +result_torch(model, img))

    img = cv2.imread('CF_img.jpg')
    print("CF(x,y) = " +result_torch(model, img))

if __name__ == '__main__':
    execute()