import LeCmd
import time
import Serial_Servo_Running as SSR
print('''*****调用总线舵机以及动作组范例*****''')

#参数1：运行时间(ms);参数2：运行舵机个数;参数3：运行舵机id;参数4：位置值(0-1000)
LeCmd.cmd_i001([500, 1, 8, 400])
#中间加延时，延时时间应大于等于运行时间
time.sleep(0.5)
LeCmd.cmd_i001([500, 1, 8, 600])
time.sleep(0.5)

#控制2个舵机
#参数1：运行时间(ms);参数2：运行舵机个数;参数3：运行舵机id;参数4：位置值(0-1000);参数5：运行舵机id;参数6：位置值(0-1000)
LeCmd.cmd_i001([500, 2, 8, 400, 7, 400])
time.sleep(0.5)
LeCmd.cmd_i001([500, 2, 8, 600, 7, 600])
time.sleep(0.5)

#控制多个舵机,修改舵机个数值，然后在后面依次增加舵机id和位置值
#参数1：运行时间(ms);参数2：运行舵机个数;参数3：运行舵机id;参数4：位置值(0-1000);参数5：运行舵机id;参数6：位置值(0-1000)...

#调用动作组，注意调用的动作组应保存在路径/home/pi/human_code/ActionGroups下
#调用9号动作组一次
SSR.runAction('9')
print('finish!')

#开始动作组运行子线程
SSR.start_action_thread()
#运行9号动作组1次 参数1：动作组编号;参数2：运行次数（当为0时表示循环运行）
SSR.change_action_value('9', 1)
#注意此种调用方式和上面的区别，上一种方式是在动作组运行完程序才会继续往下走
#下面这种方式是以子线程方式运行，所以不会阻塞
while not SSR.action_finish():
    print('unfinished')
print('finish')
#循环运行1号动作组
SSR.change_action_value('1', 0)
#运行2s后停止
time.sleep(2)
SSR.stop_action_group()
