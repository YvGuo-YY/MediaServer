from threading import Timer
import RPi.GPIO as GPIO
import math


def get_speed(face):
    with open('/proc/net/dev', mode='r') as f:
        regex = fr"{face}.*?(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)" \
                r"\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)"
        test_str = f.read()
        import re
        matches = re.finditer(regex, test_str)
        for matchNum, match in enumerate(matches, start=1):
            return int(match.group(9)), int(match.group(1))


up_gpio = 23
down_gpio = 24
upload_bytes, download_bytes = get_speed('eth0')
GPIO.setmode(GPIO.BCM)
GPIO.setup(up_gpio, GPIO.OUT)
GPIO.setup(down_gpio, GPIO.OUT)
u_pwm = GPIO.PWM(up_gpio, 1)
d_pwm = GPIO.PWM(down_gpio, 1)
u_pwm.start(0)
d_pwm.start(0)


def get_size_desc(size):
    if size >> 30 >= 1.0:
        return f'{size / (1024 * 1024 * 1024):.2f}GB'
    if size >> 20 >= 1.0:
        return f'{size / (1024 * 1024):.2f}MB'
    if size >> 10 >= 1.0:
        return f'{size / 1024:.2f}KB'
    return f'{size:.2f}B'


def get_led_times(bytes_per_second):
    return int(bytes_per_second / 10000 + 1)


def splash_led():
    global upload_bytes, download_bytes
    upload, download = get_speed('eth0')
    upload_speed = upload - upload_bytes
    download_speed = download - download_bytes
    set_freq(u_pwm, get_led_times(upload_speed))
    set_freq(d_pwm, get_led_times(download_speed))
    # print(f'upload:{get_size_desc(upload_speed)}/s,download:{get_size_desc(download_speed)}/s,up-led:'
    #       f'{get_led_times(upload_speed)}splash/s,down-led:{get_led_times(download_speed)}splash/s')
    upload_bytes = upload
    download_bytes = download
    Timer(1, splash_led).start()


def set_freq(_pwm, freq):
    if freq <= 0:
        _pwm.ChangeDutyCycle(0)
        _pwm.ChangeFrequency(1)
    else:
        _pwm.ChangeDutyCycle(1)
        _pwm.ChangeFrequency(min(10, freq))

if __name__ == '__main__':
    splash_led()
