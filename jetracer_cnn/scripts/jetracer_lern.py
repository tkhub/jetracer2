#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import rospy

import time
import torch
import torchvision

# from utils import preprocess
from xy_dataset import XYDataset
import torchvision.transforms as transforms

import numpy
import cv2
from PIL import Image


def execute():
  
  # ROS initialize
  # rospy.init_node('jetracer_lerning', anonymous=False)

  # Transform: Datesetのデータ前処理
  trans = transforms.Compose([
    # ランダムに色合いを変更(bightness, contrast, saturation, hue)
    # transforms.ColorJitter(0.2, 0.2, 0.2, 0.2),
    # 画像サイズを224x224へ変換
    transforms.Resize((224, 224)),
    # Tensor型に変換
    transforms.ToTensor(),
    # 正規化(チャンネル平均, 標準偏差)
    # transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
  ])

  # Dataset
  dataset = XYDataset('data/', ['apex'], trans, random_hflip=True)  

#  rospy.loginfo('* Dataset load.')  
#  rospy.loginfo('   directory : {}'.format(dataset.directory))
#  rospy.loginfo('   category  : {}'.format(dataset.categories))
#  rospy.loginfo('   data count: {}'.format(len(dataset.annotations)))

  # Device
  device_name = 'cpu'
  if torch.cuda.is_available():
    device_name = 'cuda'
  else:
    device_name = 'cpu'
  device = torch.device(device_name)

#  rospy.loginfo('* Device load.')
#  rospy.loginfo('   index: {}'.format(device.index))
#  rospy.loginfo('   type : {}'.format(device.type))
  
  # Model
  model = torchvision.models.resnet18(pretrained=True)
  model.fc = torch.nn.Linear(model.fc.in_features, 2)
  model = model.to(device)

  # Optimizer
  optimizer = torch.optim.Adam(model.parameters())

  # ------------------------------------------#
  # DataLoader: データセットからサンプルを抽出する
  dataloader = torch.utils.data.DataLoader(
    dataset,      # 準備したデータ
    batch_size=8, # ミニバッチにする画像数
    shuffle=True) # シャッフル必要

  # Training: 準備したデータローダで学習開始
  model.train()

  epoch_count = 50
  sum_loss_hys = [100.0] * 5
  beforetime = time.time()
  while epoch_count > 0:

    sum_loss = 0.0
    sum_count = 0

    for images, category_idx, xy in iter(dataloader):

      # 画像と結果をデバイスに転送
      images = images.to(device)
      xy = xy.to(device)

      # パラメータをリセットする
      optimizer.zero_grad()

      # 現在のモデルで推定を行う
      outputs = model(images)    

      loss = 0.0
      for batch_idx, cat_idx in enumerate(list(category_idx.flatten())):      
        loss += torch.mean((outputs[batch_idx][2 * cat_idx:2 * cat_idx+2] - xy[batch_idx])**2)

      loss /= len(category_idx)      

      # ロス分の微分計算を行う
      loss.backward()

      # 微分値を適用して補正
      optimizer.step()

      sum_loss += float(loss)
      sum_count += len(category_idx.flatten())
      
      text = '\rEpoch: {} ['.format(epoch_count)      
      fin = int(sum_count / len(dataset.annotations) * 20)
      for i in range(20):
        if i < fin:
          text += '#'
        else:
          text += '-'
      text += '] ({} / {})'.format(sum_count, len(dataset.annotations))
      print(text, end="")

    print(" SumLoss: {}".format(sum_loss))
    for i in range(len(sum_loss_hys) -1):
      sum_loss_hys[i + 1] = sum_loss_hys[i]
    sum_loss_hys[0] = sum_loss
    sum_loss_hys_diff = []
    if len(sum_loss_hys) < epoch_count:
      for i in range(len(sum_loss_hys) - 1):
        sum_loss_hys_diff.append(sum_loss_hys[i + 1] - sum_loss_hys[i]/sum_loss_hys[i])
      
      cnclFlg = False
      for i in range(3):
        if sum_loss_hys_diff[i] < 0.1:
          cnclFlg = True
        else:
          cnclFlg = False
      
      if cnclFlg:
        print("sumLoss is convergence")
        break

    epoch_count = epoch_count - 1

  aftertime = time.time()
  print("time = " +str(aftertime - beforetime))
  # モデルを保存する
  torch.save(model.state_dict(), 'data/model.pth')
  model = model.eval()

  # ------------------------------------------#
  # DataLoader: データセットからサンプルを抽出する
  dataloader = torch.utils.data.DataLoader(
    dataset,      # 準備したデータ
    batch_size=1, # ミニバッチにする画像数
    shuffle=True) # シャッフル必要

  for images, category_idx, xy in iter(dataloader):    

    # 画像と結果をデバイスに転送
    images = images.to(device)

    # 現在のモデルで推定を行う
    outputs = model(images)    

    images = images.to('cpu')
    grid_image = torchvision.utils.make_grid(images)

    grid_image = grid_image.numpy().transpose((1, 2, 0))
    grid_image = numpy.clip(grid_image, 0, 1)

    cv_image = cv2.cvtColor(grid_image, cv2.COLOR_RGB2RGBA)    

    outputs = outputs.to('cpu')    
    outputs = ((outputs + 1.0) / 2.0) * torch.tensor(cv_image.shape[0:2])        

    cv2.circle(cv_image, (outputs[0,0], outputs[0,1]), 3, (0, 0, 255), 2)

    cv2.imshow('EVAL', cv_image)
    key = cv2.waitKey(0)
    if key == 27:
      break
    
    

if __name__ == '__main__':

  execute()
#  try:
#    execute()
#  except rospy.ROSInterruptException as ex:
#    rospy.logerr(ex)
#  except KeyboardInterrupt:
#    print("interrupt signal...")
#  except Exception as ex:
#    rospy.logerr(ex)
#  except:
#    pass

