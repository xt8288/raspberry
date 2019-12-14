#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import os
import math
import time
import camera
import datetime
import numpy as np
import threading    

size = (320, 240)
MyCamera = camera.USBCamera(size)

if not os.path.exists('video'):
    os.mkdir('video')

def getDiskSpace():
    p = os.popen("df -h")
    i = 0
    while True:
        i += 1
        line = p.readline()
        if i == 2:
            remain_space = line.split()[-3]
            if "G" in remain_space:
                remain_space = float(remain_space.strip("G"))*1000
            else:
                remain_space = 0.0
            return remain_space

# 第一帧，用于比较
moving_last_gray = None

# 第一帧标志位
moving_first_flag = False  

recoding = False
text = "Unoccupied"
t3 = 0
while True:
    orgframe = MyCamera.getframe()
    if orgframe is not None:
        orgFrame = orgframe.copy()
        frame = orgframe.copy()
        t1 = cv2.getTickCount()
        if text == "Unoccupied":
            t3 = cv2.getTickCount()         
        # 转换成灰度图像
        gray = cv2.cvtColor(orgFrame, cv2.COLOR_BGR2GRAY)
        # 高斯模糊
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if moving_first_flag and moving_last_gray is not None:
            # 计算当前帧和第一帧的不同
            cv2.accumulateWeighted(gray, moving_last_gray, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(moving_last_gray))
            # cv2.imshow('frameDelta', frameDelta)
            thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
            # 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]            
            # 遍历轮廓
            for c in cnts:
                if cv2.contourArea(c) >= 5000:
                    t3 = cv2.getTickCount()
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(orgFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    text = "Occupied" 
                    moving_first_flag = False                           
        t4 = cv2.getTickCount() 
        t5 = (t4 - t3) / cv2.getTickFrequency()
        print(t5)
        if t5 > 5:
            text = "Unoccupied"
        # 保存上一帧
        moving_last_gray = gray.copy().astype("float")
        moving_first_flag = True
        # 在当前帧上写文字以及时间戳
        cv2.putText(orgFrame, "Monitor Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(orgFrame, datetime.datetime.now().strftime("%Y %m/%d %I:%M:%S"),
                    (100, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        if text == "Occupied":
            space = getDiskSpace()           
            if space > 500.0:
                if recoding == False:                   
                    #以日期作为视频的名称
                    time_data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    #cv2.VideoWrite(路径+名称+格式, 视频编解码器，帧数，分辨率）
                    out_video = cv2.VideoWriter('./video/' + time_data + '.avi', cv2.VideoWriter_fourcc('I','4','2','0'),
                          20.0,size)                    
                    recoding = True
                if recoding:
                    # 如果有画面有动，录制视频
                    out_video.write(frame)  
            else:
                recoding = False
        else:
            recoding = False

        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()               
        fps = 1.0/time_r            
        cv2.putText(orgFrame, "FPS:" + str(int(fps)),
                (10, orgFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imshow("orgFrame", orgFrame)
        cv2.waitKey(1)
    else:
        time.sleep(0.01)