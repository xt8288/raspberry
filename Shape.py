#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import os
import math
import random
import time
import camera
import numpy as np
import threading    

def get_max_coutour(cou, max_area):
    '''
    找出最大的轮廓
    根据面积来计算，找到最大后，判断是否小于最小面积，如果小于侧放弃
    :param cou: 轮廓
    :return: 返回最大轮廓
    '''
    max_coutours = 0
    r_c = None
    if len(cou) < 1:
        return None
    else:
        for c in cou:
            # 计算面积
            temp_coutours = math.fabs(cv2.contourArea(c))
            if temp_coutours > max_coutours:
                max_coutours = temp_coutours
                cc = c
        # 判断所有轮廓中最大的面积
        if max_coutours > max_area:
            r_c = cc
        return r_c

def find_contours(binary, max_area):
    '''
    mode  提取模式.
    CV_RETR_EXTERNAL - 只提取最外层的轮廓
    CV_RETR_LIST - 提取所有轮廓，并且放置在 list 中
    CV_RETR_CCOMP - 提取所有轮廓，并且将其组织为两层的 hierarchy: 顶层为连通域的外围边界，次层为洞的内层边界。
    CV_RETR_TREE - 提取所有轮廓，并且重构嵌套轮廓的全部 hierarchy
    method  逼近方法 (对所有节点, 不包括使用内部逼近的 CV_RETR_RUNS).
    CV_CHAIN_CODE - Freeman 链码的输出轮廓. 其它方法输出多边形(定点序列).
    CV_CHAIN_APPROX_NONE - 将所有点由链码形式翻译(转化）为点序列形式
    CV_CHAIN_APPROX_SIMPLE - 压缩水平、垂直和对角分割，即函数只保留末端的象素点;
    CV_CHAIN_APPROX_TC89_L1,
    CV_CHAIN_APPROX_TC89_KCOS - 应用 Teh-Chin 链逼近算法. CV_LINK_RUNS - 通过连接为 1 的水平碎片使用完全不同的轮廓提取算法
    :param binary: 传入的二值图像
    :return: 返回最大轮廓
    '''
    # 找出所有轮廓
    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
    # 返回最大轮廓
    return get_max_coutour(contours, max_area)

# 要识别的颜色字典
color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              }

cv_ok = False
color_shape_list = []
def ShapeRecognition(frame):
    global color_dist, cv_ok
    global color_shape_list
    img_h, img_w = frame.shape[:2]
    # 高斯模糊
    gs_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    # 转换颜色空间
    hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)
    for i in color_dist:
        # 查找颜色
        mask = cv2.inRange(hsv, color_dist[i]['Lower'], color_dist[i]['Upper'])
        # 腐蚀
        mask = cv2.erode(mask, None, iterations=2)
        # 膨胀
        mask = cv2.dilate(mask, None, iterations=2)
        # 查找轮廓        
        cnts = find_contours(mask, 1000)
        if cnts is not None:
            cv2.drawContours(frame, cnts, -1, (0, 0, 255), 2)
            # 识别形状
            # 周长  0.035 根据识别情况修改，识别越好，越小
            epsilon = 0.035 * cv2.arcLength(cnts, True)
            # 轮廓相似
            approx = cv2.approxPolyDP(cnts, epsilon, True)
            # print len(approx)
            color_shape_list.append([i, len(approx)])
            cv_ok = True    

def run_action():
    global cv_ok
    global color_shape_list
   
    step = 0
    run_number = 0
    run_one_ok = False
    while True:       
        if cv_ok:
            if step == 0:
                if 0 < len(color_shape_list) < 3:
                    if run_one_ok is False:
                        run_number = random.randint(0, len(color_shape_list) - 1)
                        run_one_ok = True
                        step = 1
            if step == 1:     
                if color_shape_list[run_number][1] == 3:    # 三角形
                    pass   
                elif color_shape_list[run_number][1] == 4:  # 矩形
                    pass
                elif color_shape_list[run_number][1] >= 6:  # 圆形
                    pass
                step = 0
                run_one_ok = False
                run_number = 0
            color_shape_list = []
            cv_ok = False
        else:
            time.sleep(0.01) 

# 启动子线程
th2 = threading.Thread(target=run_action)
th2.setDaemon(True)
th2.start()

MyCamera = camera.USBCamera((320, 240))

while True:
    orgframe = MyCamera.getframe()
    if orgframe is not None:
        orgFrame = orgframe.copy()
        t1 = cv2.getTickCount()                
        ShapeRecognition(orgFrame)            
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()               
        fps = 1.0/time_r            
        cv2.putText(orgFrame, "FPS:" + str(int(fps)),
                (10, orgFrame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("orgFrame", orgFrame)
        cv2.waitKey(1)
        get_image_ok = False
    else:
        time.sleep(0.01)