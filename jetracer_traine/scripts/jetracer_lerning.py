#!/usr/bin/env python3

import rospy

import torch
import torchvision

from utils import preprocess
from xy_dataset import XYDataset
import torchvision.transforms as transforms


def execute():
  
  # ROS initialize
  rospy.init_node('jetracer_lerning')

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

  model = torchvision.models.resnet18(pretrained=True)
  model.fc = torch.nn.Linear(512, 2)

  model = model.to(device)

  optimizer = torch.optim.Adam(model.parameters())

  try:
    train_loader = torch.utils.data.DataLoader(
      dataset,
      batch_size=8,
      shuffle=True
    )

    model = model.train()

    for i in range(5):
      j = 0
      sum_loss = 0.0
      error_count = 0.0

      for images, category_idx, xy in iter(train_loader):
        print(xy)
        images = images.to(device)
        xy = xy.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = 0.0

        for batch_idx, cat_idx in enumerate(list(category_idx.flatten())):
          loss += torch.mean((outputs[batch_idx][2 * cat_idx:2 * cat_idx+2] - xy[batch_idx])**2)

        loss /= len(category_idx)

        loss.backward()
        optimizer.step()

        count = len(category_idx.flatten())
        j += count
        sum_loss += float(loss)

        print('[{}, {}]'.format(j, sum_loss))

  except e:
    print(e)


if __name__ == '__main__':

  try:
    execute()
  except rospy.ROSInterruptException as ex:
    rospy.logerr(ex)
  except KeyboardInterrupt:
    print("interrupt signal...")
  except Exception as ex:
    rospy.logerr(ex)

