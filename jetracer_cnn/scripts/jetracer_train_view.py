#!/usr/bin/env python3

# 学習入力

import os
import re
import glob
import cv2
import numpy as np
import uuid
import time
import pathlib
import copy


mouse_pos = (0, 0)
mouse_event = 0


# a	97
# b	98
# c	99
# d	100
# e	101
# f	102
# g	103
# h	104
# i	105
# j	106
# k	107
# l	108
# m	109
# n	110
# o	111
# p	112
# q	113
# r	114
# s	115
# t	116
# u	117
# v	118
# w	119
# x	120
# y	121
# z	122

# 1 key
nextkeycode = 50
# 2 key
backkeycode = 49
# d key
delkeycode = 100
# q key
quitkeycode = 113


def makeStereoimgRG():
  pass

def execute():
    global mouse_pos
    global mouse_event
    # 入力ファイルの一覧を作る
    inputPath = pathlib.Path('./data/rec/')
    outputPath = pathlib.Path('./data/apex_test/')
    filelistL, filelistR = readFilelist(inputPath)

    # イメージを読み出して表示し、X・Y座標を入力させる
    xylist, filelistL, filelistR = teachXY(inputPath, filelistL, filelistR)

    # イメージを所定の場所に変換し保存する。
    # imgStroSave(inputPath, outputPath, xylist, filelistL, filelistR)
    imgStroSaveGR(inputPath, outputPath, xylist, filelistL, filelistR)

def paths_sorted(paths):
    return sorted(paths, key = lambda x: int(x.name))

def readFilelist(path):
  recfiles = list(path.glob('*.jpg'))
  files_num = len(recfiles)
  LeftFiles = []
  RightFiles = []

  for i in range(files_num -1):
    fileNname = recfiles[i].name
    fileN1name = recfiles[i + 1].name
    fileNmatch = re.match(r"([0-9]+|[0-9]+\.[0-9]+)_(L|R).jpg", fileNname)
    fileN1match = re.match(r"([0-9]+|[0-9]+\.[0-9]+)_(L|R).jpg", fileN1name)
    if fileNmatch and fileN1match and fileNname[:-6] == fileN1name[:-6]:
      # ファイルが命名規則にあっており、L,R両方のファイルが揃っている
      if fileNname[-5:-4] == "L":
        LeftFiles.append(fileNname)
        RightFiles.append(fileN1name)
      else:
        RightFiles.append(fileNname)
        LeftFiles.append(fileN1name)

  return LeftFiles, RightFiles


def teachXY(inputPath, filelistL, filelistR):
  files = copy.copy(filelistL)
  # OpenCV
  cv2.namedWindow('JETRACER_TRAINE_VIEW', cv2.WINDOW_NORMAL)
  cv2.setMouseCallback('JETRACER_TRAINE_VIEW', mouse_callback)
  files_num = len(files)
  xyList = [[0,0]] * files_num
  disp_count = 0
  disp_image = cv2.imread(str(inputPath / files[disp_count]) , cv2.IMREAD_COLOR)
  disp_pos = (0,0)
  delflg = False

  while True:

    # key function
    key = cv2.waitKey(30)    
    # "1"key
    if key == nextkeycode: # NEXT: ->
      disp_count = disp_count + 1
    # "2" key
    if key == backkeycode: # PREV: <- 
      disp_count = disp_count -1
    if key == quitkeycode:
      return 
    if key == delkeycode:
      delflg = True


    if disp_count < 0:
      disp_count = 0
    if disp_count >= files_num:
      break

    # "1" key or "2" key 画像リロード
    if key == nextkeycode or key == backkeycode:
      # 次 or 前のdisp_countを表示
      disp_image = cv2.imread(str(inputPath / files[disp_count]) , cv2.IMREAD_COLOR)
      disp_pos = (0,0)




    # ESCでbreak
    if key == 27:
      break
    if mouse_event == cv2.EVENT_LBUTTONDOWN and not delflg:
      disp_pos = mouse_pos
      xyList[disp_count]  = mouse_pos
    if delflg:
      disp_pos = (0, 0)
      del xyList[disp_count]
      del filelistL[disp_count]
      del filelistR[disp_count]
      files_num = files_num -1
      if files_num < 0:
        print("All file is RUBBISH!")
        break
      delflg = False

    # display art
    temp = disp_image.copy()
    if delflg:
      # ばってんを描写
      cv2.line(temp, (0, 0), (temp.shape[1], temp.shape[0]),
                (0, 0, 255), thickness=5, lineType=cv2.LINE_8)
      cv2.line(temp, (temp.shape[1], 0), (0, temp.shape[0]),
                (0, 0, 255), thickness=5, lineType=cv2.LINE_8)
      cv2.putText(temp, "PREV: 1 <- Del -> 2 :NEXT", 
                  (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                  0.6, (255, 255, 255), 2)
      cv2.putText(temp, files[disp_count],
                  (10, temp.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
                  0.6, (255, 255, 255), 2)
      cv2.imshow('JETRACER_TRAINE_VIEW', temp)
    else: 
      # マウスポインタの場所に十字を描写
      cv2.line(temp, (mouse_pos[0], 0), (mouse_pos[0], temp.shape[0]),
                (255, 0, 0), thickness=2, lineType=cv2.LINE_8)
      cv2.line(temp, (0, mouse_pos[1]), (temp.shape[1], mouse_pos[1]),
                (255, 0, 0), thickness=2, lineType=cv2.LINE_8)
      # 中央の十字 
      cv2.line(temp, (0, int(temp.shape[1] / 2)), (temp.shape[0], int(temp.shape[1] / 2)),
                (127, 127, 127), thickness=1, lineType=cv2.LINE_8)
      cv2.line(temp, (int(temp.shape[0] / 2), 0), (int(temp.shape[0] / 2), temp.shape[1]),
                (127, 127, 127), thickness=1, lineType=cv2.LINE_8)

      cv2.circle(temp, (int(temp.shape[0] / 2), int(temp.shape[1] / 2)), int(temp.shape[1] / 2), (127, 127, 127), thickness=1)
      cv2.circle(temp, (int(temp.shape[0] / 2), int(temp.shape[1] / 2)), int(temp.shape[1] / 4), (127, 127, 127), thickness=1)

      # 決定した教示座標
      cv2.circle(temp, disp_pos, 5, (0, 255, 0), thickness=3)
      cv2.putText(temp, "PREV: 1 <- Del -> 2 :NEXT", 
                  (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                  0.6, (255, 255, 255), 2)
      cv2.putText(temp, files[disp_count],
                  (10, temp.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
                  0.6, (255, 255, 255), 2)

      cv2.imshow('JETRACER_TRAINE_VIEW', temp)
  return xyList, filelistL, filelistR

def mouse_callback(event, x, y, flags, param):
  global mouse_pos
  global mouse_event
  mouse_pos = (x, y)
  mouse_event = event



def imgStroSave(inpath, outpath, xylist, listL, listR):
  filenum = len(listL)
  for i in range(filenum):
    str_uuid = str(uuid.uuid1())
    imageLColor = cv2.imread(str(inpath / listL[i]) , cv2.IMREAD_COLOR)
    imageRColor = cv2.imread(str(inpath / listR[i]) , cv2.IMREAD_COLOR)
    imageSteroColor = cv2.addWeighted(src1 = imageLColor , alpha=0.5, src2 = imageRColor, beta = 0.5, gamma = 0)
    imageLGray = cv2.cvtColor(imageLColor, cv2.COLOR_BGR2GRAY)
    imageRGray = cv2.cvtColor(imageRColor, cv2.COLOR_BGR2GRAY)
    imageSteroGray = cv2.addWeighted(src1 = imageLGray, alpha=0.5, src2 = imageRGray, beta = 0.5, gamma = 0)
    outPathStr = str(outpath / ('%d_%d_%s.jpg' % (xylist[i][0],  xylist[i][1], str_uuid)))
    cv2.imwrite(outPathStr, imageSteroColor)

def imgStroSaveGR(inpath, outpath, xylist, listL, listR):
  filenum = len(listL)
  for i in range(filenum):
    str_uuid = str(uuid.uuid1())
    imageLColor = cv2.imread(str(inpath / listL[i]) , cv2.IMREAD_COLOR)
    imageRColor = cv2.imread(str(inpath / listR[i]) , cv2.IMREAD_COLOR)
    height, width, _ = imageLColor.shape[:3]
    zeros = np.zeros((height, width), imageLColor.dtype)

    _, imgL_green, _ =cv2.split(imageLColor)
    _, _, imgR_red =cv2.split(imageRColor)

    imggrL = cv2.merge((zeros, imgL_green, zeros))
    imgrdR = cv2.merge((zeros, zeros, imgR_red))

    imageSteroGR = cv2.addWeighted(src1 = imggrL, alpha=0.5, src2 = imgrdR, beta = 0.5, gamma = 0)
    outPathStr = str(outpath / ('%d_%d_%s.jpg' % (xylist[i][0],  xylist[i][1], str_uuid)))
    cv2.imwrite(outPathStr, imageSteroGR)

       


if __name__ == '__main__':

  execute()
  #execute_nkd()
  #try
  #  execute_nkd()
  # except rospy.ROSInterruptException as ex:
  #  rospy.logerr(ex)
  # except KeyboardInterrupt:
  #  pass
  # except Exception as ex:
  #  rospy.logerr(ex)