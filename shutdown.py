# 导入 RPi.GPIO 模块
import RPi.GPIO as GPIO
# 导入 os 模块
import os
# 设置引脚模式为 BCM
GPIO.setmode(GPIO.BCM)
# 设置引脚 18 为输入，上拉电阻
GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_UP)
# 定义一个回调函数，用于执行关机命令
def shutdown(channel):
    GPIO.cleanup()
    os.system("sudo shutdown -h now")
# 添加一个事件检测，当引脚 18 的电平从高变低时，执行 shutdown 函数
GPIO.add_event_detect(27, GPIO.FALLING, callback=shutdown, bouncetime=300)
# 保持程序运行，直到按下 Ctrl+C
try:
    while True:
        pass
except KeyboardInterrupt:
    # 清理 GPIO 资源
    GPIO.cleanup()
