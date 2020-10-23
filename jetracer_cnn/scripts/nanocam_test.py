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

filenameL = './nanocam_test/%d_%d_%s_L.jpg' % (0, 0, s_uuid)
filenameR = './nanocam_test/%d_%d_%s_R.jpg' % (0, 0, s_uuid)
filenameM = './nanocam_test/%d_%d_%s_M.jpg' % (0, 0, s_uuid)
imgMx = cv2.addWeighted(src1 = imgL, alpha=0.5, src2 = imgR, beta = 0.5, gamma = 0)

cv2.imwrite(filenameL, imgL)
cv2.imwrite(filenameR, imgR)
cv2.imwrite(filenameM, imgMx)

camera0.release()
camera1.release()