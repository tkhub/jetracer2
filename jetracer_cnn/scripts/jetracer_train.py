#!/usr/bin/env python3

import sys

import rospy
from sensor_msgs.msg import Image

import cv2
from cv_bridge import CvBridge

from xy_dataset import XYDataset
import torchvision.transforms as transforms


save_image = None


def imageSubscribe(data):  
  global save_image

  save_image = data

def execute():

  # ROS initialize
  rospy.init_node('jetracer_traine', anonymous=False)

  # ROS parameters
  save_rate = 5.0
  image_topic = '/camera/color/image_raw'
  try:
    save_rate = rospy.get_param('~save_rate')
    image_topic = rospy.get_param('~image_topic')
  except KeyError:
    pass

  # Transform
  trans = transforms.Compose([
    transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
  ])
  # Dataset
  dataset = XYDataset('data/', ['apex'], trans, random_hflip=True)

  rate = rospy.Rate(save_rate)
  image_sub = rospy.Subscriber(image_topic, Image, imageSubscribe)
  cv_bridge = CvBridge()

  # save_count = 0

  while not rospy.is_shutdown():

    if save_image is not None:
      #cv_image = cv_bridge.imgmsg_to_cv2(save_image, desired_encoding="passthrough")
      cv_image = cv_bridge.imgmsg_to_cv2(save_image, desired_encoding="bgr8")

      dataset.save_entry('apex', cv_image, 0, 0)
      # path = 'data/{:06}_0_0.bmp'.format(save_count)
      # cv2.imwrite(path, cv_image)
      # save_count = save_count + 1

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
