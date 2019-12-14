#!/usr/bin/python3
import platform
#coding:utf8
#训练及采集图像时的参数配置，谨慎修改！！！
############################
#采集图像时小车的行驶速度，范围-100 - 100, 超过范围的会自动设置为临界值
go_straight = (60,  60)
speed_up    = (80,  80)
turn_right  = (90,  20)
turn_left   = (20,  90)
go_back     = (-80, -80)
############################
#截取主要跑道区域，作为训练图像
roi_range  = (380, 480, 0, 640)

#保存及训练时图像的大小
image_size = (32, 32)
############################
if(platform.system()=='Windows'):
  print('Windows')
  path_model = '\\model\\' #模型默认的保存位置
  path_image = '\\train\\' #采集到的图像默认保存位置
elif(platform.system()=='Linux'):
  print('Linux')
  path_model = './model/'#模型默认的保存位置
  #path_image = '/media/pi/BOOT/training/'#采集到的图像默认保存位置
  path_image = './train/'#采集到的图像默认保存位置
else:
  print('others')
  
#保存模型的名称
model_names = 'track'
############################
#训练的批次
epochs     = 50

#每批次的数据量
batch_size = 100

#学习率
learn_rate = 0.0001
############################
