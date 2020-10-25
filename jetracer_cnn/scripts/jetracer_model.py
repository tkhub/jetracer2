#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import torch
import torchvision
import cv2
from torch2trt import torch2trt
from torch2trt import TRTModule


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
    imgh = preprocess(img).half()
    output = model(imgh).detach().cpu().numpy().flatten()
    x = float(output[0])
    y = float(output[1])
    return x, y

def execute():
    print("jetracer_model_test")
    model = prepare_torch()

    print("model preper end")

    # imgLL = cv2.imread('./modeltestimg/str/LS_img.jpg')
    # imgL = cv2.imread('./modeltestimg/str/LF_img.jpg')
    # imgRR = cv2.imread('./modeltestimg/str/RS_img.jpg')
    # imgR = cv2.imread('./modeltestimg/str/RF_img.jpg')
    # imgC = cv2.imread('./modeltestimg/str/CF_img.jpg')
    imgLL = cv2.imread('./modeltestimg/mono/LS_img.jpg')
    imgL = cv2.imread('./modeltestimg/mono/LF_img.jpg')
    imgRR = cv2.imread('./modeltestimg/mono/RS_img.jpg')
    imgR = cv2.imread('./modeltestimg/mono/RF_img.jpg')
    imgC = cv2.imread('./modeltestimg/mono/CF_img.jpg')

    xLL, yLL = result_torch(model, imgLL)
    xL, yL = result_torch(model, imgL)
    xR, yR = result_torch(model, imgR)
    xRR, yRR = result_torch(model, imgRR)
    xC, yC = result_torch(model, imgC)

    print("LS(x,y) = " +str(xLL)+ "," +str(yLL))
    print("LF(x,y) = " +str(xL)+ "," +str(yL))
    print("CF(x,y) = " +str(xC)+ "," +str(yC))
    print("RF(x,y) = " +str(xR)+ "," +str(yR))
    print("RS(x,y) = " +str(xRR)+ "," +str(yRR))

if __name__ == '__main__':
    execute()