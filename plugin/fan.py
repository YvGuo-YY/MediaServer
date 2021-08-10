from threading import Timer
import RPi.GPIO as GPIO


# 开始与结束阈值
start_thr = 50.0
stop_thr = 43.0
fan_gpio = 14
led_gpio = 15
# GPIO 设置
GPIO.setmode(GPIO.BCM)
GPIO.setup(fan_gpio, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(led_gpio, GPIO.OUT, initial=GPIO.HIGH)
is_fan_running = True


def cat_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', mode='r') as f:
        return int(f.read())


def fan_controller():
    global is_fan_running
    temp = cat_temp() / 1000
    if temp >= start_thr and not is_fan_running:
        GPIO.output(fan_gpio, GPIO.HIGH)
        GPIO.output(led_gpio, GPIO.HIGH)
        is_fan_running = True
    if temp < stop_thr and is_fan_running:
        GPIO.output(fan_gpio, GPIO.LOW)
        GPIO.output(led_gpio, GPIO.LOW)
        is_fan_running = False
    # 多运行一会
    if is_fan_running:
        Timer(60, fan_controller).start()
    # 及时响应高温
    else:
        Timer(10, fan_controller).start()


print("temp-controlled fan running")
fan_controller()
