#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import torch
import torchvision
import cv2
from torch2trt import torch2trt
from torch2trt import TRTModule


from utils import preprocess
import numpy as np


def prepare_torch_trt():

    # create model
    device = torch.device('cuda')
    model = torchvision.models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(512, 2)
    model = model.cuda().eval().half()

    # load saved model
    model.load_state_dict(torch.load('data/model.pth'))

    # convert and optimize the model using torch2trt.
    data = torch.zeros((1, 3, 224, 224)).cuda().half()
    model_trt = torch2trt(model, [data], fp16_mode=True)

    # save optimized model
    #torch.save(model_trt.state_dict(), 'road_following_model_trt.pth')


    # load optimized model
    #model_trt = TRTModule()
    #model_trt.load_state_dict(torch.load('road_following_model_trt.pth'))

    return model_trt


def result_torch(model, img):
    imgh = preprocess(img).half()
    output = model(imgh).detach().cpu().numpy().flatten()
    x = float(output[0])
    y = float(output[1])
    return x, y

def execute():
    print("jetracer_model_test")
    # model = prepare_torch()
    model = prepare_torch_trt()

    print("model preper end")
    print(model)

    #imgLL = cv2.imread('./modeltestimg/str/LS_img.jpg')
    #imgL = cv2.imread('./modeltestimg/str/LF_img.jpg')
    #imgRR = cv2.imread('./modeltestimg/str/RS_img.jpg')
    #imgR = cv2.imread('./modeltestimg/str/RF_img.jpg')
    #imgC = cv2.imread('./modeltestimg/str/CF_img.jpg')
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