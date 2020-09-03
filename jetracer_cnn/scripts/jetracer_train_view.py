#!/usr/bin/env python3


import os
import re
import glob
import cv2


mouse_pos = (0, 0)
mouse_event = 0

def mouse_callback(event, x, y, flags, param):
  global mouse_pos
  global mouse_event

  mouse_pos = (x, y)
  mouse_event = event
    

def execute():
  global mouse_pos
  global mouse_event


  # Folder search
  files = glob.glob('data/apex/*')
  files_num = len(files)

  # dict
  file_dict = dict()
  for f in files:
    pos = re.findall(r'\d+', f)    
    file_dict[f] = (int(pos[0]), int(pos[1]))

  # OpenCV
  cv2.namedWindow('JETRACER_TRAINE_VIEW', cv2.WINDOW_NORMAL)
  cv2.setMouseCallback('JETRACER_TRAINE_VIEW', mouse_callback)

  disp_count = 0
  disp_image = cv2.imread(files[disp_count], cv2.IMREAD_COLOR)
  disp_pos = file_dict[files[0]]
  lblatch = 0

  # Loop
  # while not rospy.is_shutdown():
  while True:

    # key function
    key = cv2.waitKey(30)    
    # "1"key
    if key == 50: # NEXT: ->
      disp_count = disp_count + 1
    # "2" key
    if key == 49: # PREV: <- 
      disp_count = disp_count -1

    if disp_count < 0:
      disp_count = 0
    if disp_count >= files_num:
      #disp_count = files_num - 1
      break

    # "1" key or "2" key 画像リロード
    if key == 49 or key == 50:
      disp_image = cv2.imread(files[disp_count], cv2.IMREAD_COLOR)
      disp_pos = file_dict[files[disp_count]]


    # ESCでbreak
    if key == 27:
      break
    if mouse_event == cv2.EVENT_LBUTTONDOWN:
      disp_pos = mouse_pos
      file_dict[files[disp_count]] = mouse_pos

    # display art
    temp = disp_image.copy()
    cv2.line(temp, (mouse_pos[0], 0), (mouse_pos[0], temp.shape[0]),
              (255, 0, 0), thickness=1, lineType=cv2.LINE_8)
    cv2.line(temp, (0, mouse_pos[1]), (temp.shape[1], mouse_pos[1]),
              (255, 0, 0), thickness=1, lineType=cv2.LINE_8)
    cv2.circle(temp, disp_pos, 5, (0, 255, 0), thickness=3)
    cv2.putText(temp, "PREV: 1 <- Del -> 2 :NEXT", 
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)
    cv2.putText(temp, files[disp_count],
                (10, temp.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)
    # display
    cv2.imshow('JETRACER_TRAINE_VIEW', temp)

  # rename
  for f in file_dict:
    pos = file_dict[f]
    
    f_new = re.sub('[0-9]_[0-9]_', 
            '{}_{}_'.format(pos[0], pos[1]), f)

    print(f_new)            

    os.rename(f, f_new)

if __name__ == '__main__':

  execute()
  #try
  #  execute()
  # except rospy.ROSInterruptException as ex:
  #  rospy.logerr(ex)
  # except KeyboardInterrupt:
  #  pass
  # except Exception as ex:
  #  rospy.logerr(ex)