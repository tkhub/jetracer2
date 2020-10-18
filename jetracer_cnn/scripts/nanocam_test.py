#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import nanocamera as nano
import uuid

# Left Camera
camera0 = nano.Camera(device_id=0, flip=2, width=224, height=224, fps=30)
# Right Camera
camera1 = nano.Camera(device_id=1, flip=2, width=224, height=224, fps=30)

imgL = camera0.read()
imgR = camera1.read()
s_uuid = str(uuid.uuid1())

filenameL = '%d_%d_%s_L.jpg' % (0, 0, s_uuid)
filenameR = '%d_%d_%s_R.jpg' % (0, 0, s_uuid)
cv2.imwrite(filenameL, imgL)
cv2.imwrite(filenameR, imgR)
camera0.release()
camera1.release()