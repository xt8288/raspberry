#!/usr/bin/python3
#coding=utf8
import os
import cv2
import time
import camera

#设置，打印分辨率
size = (640, 480)
MyCamera = camera.USBCamera(size)
print('Camera size: ' + str(size[0]) + 'X' + str(size[1]))

#判断对应文件夹是否存在，不存在则创建
if not os.path.exists('picture'):
    os.mkdir('picture')
if not os.path.exists('video'):
    os.mkdir('video')

#设置fps
fps = 30
recording = False
while True:
    t1 = cv2.getTickCount()
    #获取图像
    orgframe = MyCamera.getframe()    
    if orgframe is not None:
        orgFrame = orgframe.copy()
        frame = orgframe.copy()
        
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()
        #由于中间没有执行复杂到程序，程序运行速度会很快，此处加适当延时和分辨率对应上
        time.sleep(abs(round(((1/fps) - time_r), 5)))
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()        
        FPS = int(1.0/time_r)
        
        #打印分辨率到画面
        cv2.putText(orgFrame, str(FPS), (0, size[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        
        #显示画面
        cv2.imshow('MyWindow', orgFrame)
        #适当延时，获取按键
        key = cv2.waitKey(1)
        #打印键盘键值
        if key != -1:
            print('KeyBoard KeyCode: ' + str(key))
        #当按下esc键时退出程序
        if key == 27:
            break
        #当按下空格键时，存储一张图像
        elif key == 32:
            #以存储文件夹下图片数量作为名称
            number = len(os.listdir('./picture'))
            #cv2.imwrite(路径+名称+格式, 图片）
            cv2.imwrite('./picture/' + str(number + 1) + '.png', frame)
            print('Save picture: ' + str(number) + '.png')
        #当按下enter键时，开始录制，再次按下停止录制
        elif key == 10:
            if recording:
                print('Stop recording')
                recording = False
            else:
                #以日期作为视频的名称
                time_data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #cv2.VideoWrite(路径+名称+格式, 视频编解码器，帧数，分辨率）
                videoWriter = cv2.VideoWriter('./video/' + time_data + '.avi', cv2.VideoWriter_fourcc('I','4','2','0'),
                      FPS,size)
                print('Start recording...')
                recording = True
        if recording:
            #视频写入
            videoWriter.write(frame)        

MyCamera.shutdown()