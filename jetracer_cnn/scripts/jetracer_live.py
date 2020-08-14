#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image

import cv2
import numpy
from cv_bridge import CvBridge

import torch
import torchvision
from utils import preprocess


recv_image = None


def imageSubscribe(data):  
  global recv_image

  recv_image = data


def execute():
  global recv_image

  # ROS initialize
  rospy.init_node('jetracer_live', anonymous=False)
  
  # ROS parameters
  image_rate = 30.0
  image_topic = '/camera/color/image_raw'

  rate = rospy.Rate(image_rate)
  image_sub = rospy.Subscriber(image_topic, Image, imageSubscribe)
  cv_bridge = CvBridge()

  # Device
  device_name = 'cpu'
  if torch.cuda.is_available():
    device_name = 'cuda'
  else:
    device_name = 'cpu'
  device = torch.device(device_name)

  rospy.loginfo('* Device load.')
  rospy.loginfo('   index: {}'.format(device.index))
  rospy.loginfo('   type : {}'.format(device.type))
  
  # Model
  model = torchvision.models.resnet18(pretrained=True)
  model.fc = torch.nn.Linear(model.fc.in_features, 2)  
  model = model.to(device)
  # model.load_state_dict(torch.load('data/model.pth', map_location=torch.device(device)))
  model.load_state_dict(torch.load('data/model.pth'))

  while not rospy.is_shutdown():

    if recv_image is not None:
      # 画像を取得する
      cv_image = cv_bridge.imgmsg_to_cv2(recv_image, desired_encoding="bgr8")

      # 画像データを前処理とGPUへ転送
      preprocessed = preprocess(cv_image)

      output = model(preprocessed)
      output = model(preprocessed).detach().cpu().numpy().flatten()
      
      # print(output)
      output = (output + 1.0) / 2.0 * numpy.array([cv_image.shape[1], cv_image.shape[0]])
      # print(output)
      # output = (output + 1.0) / 2.0 * numpy.array([cv_image.shape[0:2]])
      
      cv2.circle(cv_image, (int(output[0]), int(output[1])),
                  5, (0, 255, 0), 3)
      cv2.imshow('LIVE', cv_image)
      cv2.waitKey(30)

    rate.sleep()


if __name__ == '__main__':

  try:
    execute()
  except rospy.ROSInterruptException as ex:
    rospy.logerr(ex)
  except KeyboardInterrupt:
    rospy.logwarn('keyborad interrupt')
  except Exception as ex:
    rospy.logerr(ex) 

