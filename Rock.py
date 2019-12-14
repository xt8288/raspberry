#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import os
import math
import camera
import numpy as np
import time
import threading

class Point(object):
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

def GetCrossAngle(l1, l2):
    '''
    求两直线之间的夹角
    :param l1:
    :param l2:
    :return:
    '''
    arr_0 = np.array([(l1.p2.x - l1.p1.x), (l1.p2.y - l1.p1.y)])
    arr_1 = np.array([(l2.p2.x - l2.p1.x), (l2.p2.y - l2.p1.y)])
    
    # 注意转成浮点数运算
    cos_value = (float(arr_0.dot(arr_1)) / (np.sqrt(arr_0.dot(arr_0)) * np.sqrt(arr_1.dot(arr_1))))
    return np.arccos(cos_value) * (180/np.pi)

def two_distance(start, end):
    """
    计算两点的距离
    :param start: 开始点
    :param end: 结束点
    :return: 返回两点之间的距离
    """
    s_x = start[0]
    s_y = start[1]
    e_x = end[0]
    e_y = end[1]
    x = s_x - e_x
    y = s_y - e_y
    return math.sqrt((x**2)+(y**2))

def get_defects_far(defects, contours, img):
    '''
    获取凸包中最远的点
    '''
    if defects is None and contours is None:
        return None
    far_list = []
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contours[s][0])
        end = tuple(contours[e][0])
        far = tuple(contours[f][0])
        # 求两点之间的距离
        a = two_distance(start, end)
        b = two_distance(start, far)
        c = two_distance(end, far)

        # 求出手指之间的角度
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180 / math.pi
        # 手指之间的角度一般不会大于100度
        if angle <= 75:
            # cv.circle(img, far, 10, [0, 0, 255], 1)
            far_list.append(far)
    return far_list

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
    cv2_RETR_EXTERNAL - 只提取最外层的轮廓
    cv2_RETR_LIST - 提取所有轮廓，并且放置在 list 中
    cv2_RETR_CCOMP - 提取所有轮廓，并且将其组织为两层的 hierarchy: 顶层为连通域的外围边界，次层为洞的内层边界。
    cv2_RETR_TREE - 提取所有轮廓，并且重构嵌套轮廓的全部 hierarchy
    method  逼近方法 (对所有节点, 不包括使用内部逼近的 cv2_RETR_RUNS).
    cv2_CHAIN_CODE - Freeman 链码的输出轮廓. 其它方法输出多边形(定点序列).
    cv2_CHAIN_APPROX_NONE - 将所有点由链码形式翻译(转化）为点序列形式
    cv2_CHAIN_APPROX_SIMPLE - 压缩水平、垂直和对角分割，即函数只保留末端的象素点;
    cv2_CHAIN_APPROX_TC89_L1,
    cv2_CHAIN_APPROX_TC89_KCOS - 应用 Teh-Chin 链逼近算法. cv2_LINK_RUNS - 通过连接为 1 的水平碎片使用完全不同的轮廓提取算法
    :param binary: 传入的二值图像
    :return: 返回最大轮廓
    '''
    # 找出所有轮廓
    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
    
    # 返回最大轮廓
    return get_max_coutour(contours, max_area)

def image_process(image):
    '''
    # 光线影响，请修改 cb的范围
    # 正常黄种人的Cr分量大约在140~160之间
    识别肤色
    :param image: 图像
    :return: 识别后的二值图像
    '''
    # 将图片转化为YCrCb
    YCC = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)
    
    # 分割YCrCb
    Y, Cr, Cb = cv2.split(YCC)

    Cr = cv2.inRange(Cr, 132, 175)
    Cb = cv2.inRange(Cb, 100, 140)
    Cb = cv2.bitwise_and(Cb, Cr)
    
    # 开运算，去除噪点
    open_element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opend = cv2.morphologyEx(Cb, cv2.MORPH_OPEN, open_element)
    
    #腐蚀
    kernel = np.ones((3, 3), np.uint8)
    erosion = cv2.erode(opend, kernel, iterations=1)

    return erosion

def get_hand_number(binary_image, rgb_image):
    '''
    返回手指的个数
    :param binary_image:
    :param rgb_image:
    :return:
    '''
    
    # 查找轮廓，返回最大轮廓
    contours = find_contours(binary_image, 1500)
    coord_list = []
    if contours is not None:
        # 周长  0.035 根据识别情况修改，识别越好，越小
        epsilon = 0.025 * cv2.arcLength(contours, True)
        # 轮廓相似
        approx = cv2.approxPolyDP(contours, epsilon, True)
        cv2.polylines(rgb_image, [approx], True, (0, 255, 0), 1)
        
        # 有三个点以上
        if approx.shape[0] >= 3:  
            approx_list = []
            for j in range(approx.shape[0]):
                approx_list.append(approx[j][0])
                
            # 在末尾添加第一个点
            approx_list.append(approx[0][0])
            
            # 在末尾添加第二个点
            approx_list.append(approx[1][0])    
            for i in range(1, len(approx_list) - 1):
                
                # 声明一个点
                p1 = Point(approx_list[i - 1][0], approx_list[i - 1][1])
                
                p2 = Point(approx_list[i][0], approx_list[i][1])
                p3 = Point(approx_list[i + 1][0], approx_list[i + 1][1])
                
                # 声明一条直线
                line1 = Line(p1, p2)
                
                line2 = Line(p2, p3)
                
                # 获取两条直线的夹角
                angle = GetCrossAngle(line1, line2)
                
                angle = 180 - angle    
                if angle < 42:  # 求出两线相交的角度，并小于42度的
                    coord_list.append(tuple(approx_list[i]))
        # 获取凸包缺陷点，最远点
        hull = cv2.convexHull(contours, returnPoints=False)
        
        # 找凸包缺陷点，返回的数据：起点，终点， 最远的点，到最远点的近似距离
        defects = cv2.convexityDefects(contours, hull)
        
        # 返回手指间的点
        hand_coord = get_defects_far(defects, contours, rgb_image)

        
        new_hand_list = [] 
        alike_flag = False
        
        # 从coord_list 去除最远点
        if len(coord_list) > 0:
            for l in range(len(coord_list)):
                for k in range(len(hand_coord)):
                    # 最比较X,Y轴, 相近的去除
                    if (-10 <= coord_list[l][0] - hand_coord[k][0] <= 10 and
                            -10 <= coord_list[l][1] - hand_coord[k][1] <= 10):    
                        alike_flag = True
                        break   #
                if alike_flag is False:
                    new_hand_list.append(coord_list[l])
                alike_flag = False

            # 获取指尖的坐标列表并显示
            for i in new_hand_list:
                cv2.circle(rgb_image, tuple(i), 5, [0, 0, 100], -1)
        if new_hand_list is []:
            return 0
        else:
            return len(new_hand_list)
    else:
        return None

def rock_paper_scissors(num):
    """
    # 根据返回的锐角个数判断  石头， 剪刀 ，布
    :param num: 手指个数
    :return:
    """
    status = None
    if num is None:
        return None
    if num < 1:
         # 石头
        status = 0 
    elif num == 2:
        # 剪刀
        status = 1  
    elif num > 3:
        status = 2
    return status

new_hand_num = None
last_hand_num = None
get_angle_ok = False
game_list = ['石头', '剪刀', '布']
game_action_list = ['rock', 'scissors', 'paper']  # 石头 ， 剪刀， 布
  
def run_action():
    global last_hand_num, new_hand_num
    while True: 
        if last_hand_num != new_hand_num:
            # 没有检测到手
            if new_hand_num is not None and get_angle_ok is not False:
                # 判断是否是有效
                game_state = rock_paper_scissors(new_hand_num)              
                if game_state == 0:  # 你出石头
                    pass# 布
                elif game_state == 1:  # 你出剪刀
                    pass# 石头
                elif game_state == 2:  # 你出布
                    pass# 剪刀                
                last_hand_num = new_hand_num
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.01) 

# 启动动作在运行线程
th2 = threading.Thread(target=run_action)
th2.setDaemon(True)
th2.start()

MyCamera = camera.USBCamera((320, 240))

while True:
    orgframe = MyCamera.getframe()
    if orgframe is not None:
        orgFrame = orgframe.copy()
        t1 = cv2.getTickCount()                
        # 查找轮廓，返回最大轮廓
        binary = image_process(orgFrame)

        # 获取手指个数
        hand_num = get_hand_number(binary, orgFrame)
        
        if hand_num is not None:
            new_hand_num = hand_num
            get_angle_ok = True
        else:
            get_angle_ok = False
            
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