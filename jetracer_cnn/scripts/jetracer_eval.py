#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image

import cv2
from cv_bridge import CvBridge

import torch
import torchvision

from utils import preprocess
from xy_dataset import XYDataset
import torchvision.transforms as transforms


save_image = None


def imageSubscribe(data):  
  global save_image

  save_image = data


def execute():
  
  # ROS initialize
  rospy.init_node('jetracer_lerning')

  image_topic = '/camera/color/image_raw'
  image_sub = rospy.Subscriber(image_topic, Image, imageSubscribe)


  # Transform
  trans = transforms.Compose([
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
  ])


  # Dataset
  dataset = XYDataset('data/', ['apex'], trans, random_hflip=True)
  dataset.refresh()  


  # torch
  device = torch.device('cuda')

  # model
  model = torchvision.models.resnet18(pretrained=True)
  model.fc = torch.nn.Linear(512, 2)
  model.load_state_dict(torch.load('data/model'))  
  model = model.to(device)
  # model = model.eval()

  cv_bridge = CvBridge()

  # window

  cv2.namedWindow('JETRACER_EVAL_VIEW', cv2.WINDOW_NORMAL)

  while not rospy.is_shutdown():

    if save_image is not None:
      cv_image = cv_bridge.imgmsg_to_cv2(save_image, desired_encoding="bgr8")

      preprocessed = preprocess(cv_image)
      output = model(preprocessed).detach().cpu().numpy().flatten()

      x = int(cv_image.shape[1] * (output[0]/2.0+0.5))
      y = int(cv_image.shape[0] * (output[1]/2.0+0.5))

      cv_image = cv2.circle(cv_image, (x, y), 8, (255, 0, 0), 3)

      cv2.imshow('JETRACER_EVAL_VIEW', cv_image)
      cv2.waitKey(30)      


if __name__ == '__main__':

  try:
    execute()
  except rospy.ROSInterruptException as ex:
    rospy.logerr(ex)
  except KeyboardInterrupt:
    print("interrupt signal...")
  except Exception as ex:
    rospy.logerr(ex)

