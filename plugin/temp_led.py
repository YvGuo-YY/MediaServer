from threading import Timer

import RPi.GPIO as GPIO
'''
0=_ABCDEFG=0111,1110
1=_BC____G=0011,0000
2=_AB_DE_G=0110,1101
3=_ABCD__G=0111,1001
4=__BC__FG=0011,0011
5=_A_CD_FG=0101,1011
6=_A_CDEFG=0101,1111
7=_ABC____=0111,0000
8=_ABCDEFG=0111,1111
9=_ABCD_FG=0111,1011
'''
seg_code = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5f, 0x70, 0x7f, 0x7B]  # 0~9（3f=00111111）
pins = [16, 21, 19, 6, 5, 20, 26, 13, 3, 2, 4, None]  # 端口a-b-c-d-e-f-g-dp,first-second-third
chip_select = pins[8:-1]  # 片选端口
chip_num = len(chip_select)
# 设置刷新参数
refresh_rate = 150  # 60Hz
data_refresh_rate = 3 * refresh_rate  # 180Hz
refresh_time = 1 / refresh_rate
# 刷新的数码管id
idx = 0
# 三个数码管要显示的值
chip_dis = 0, 0, 0


def setup():
    GPIO.setmode(GPIO.BCM)
    [GPIO.setup(port, GPIO.OUT) for port in pins if port]


def refresh():
    # display temperature
    global chip_dis, idx
    real_idx = idx % chip_num
    if idx % data_refresh_rate == 0:
        chip_dis = get_display_value()
        # print(chip_dis)
    digitalWriteByte(seg_code[chip_dis[real_idx]] if real_idx != 1 else with_dp(seg_code[chip_dis[real_idx]]),
                     real_idx)
    idx = idx + 1
    # refresh again after {refresh_time}
    Timer(refresh_time, refresh).start()


def get_display_value():
    temp = float(f'{cat_temp() / 1000:.1f}')
    _1 = int(temp / 10)
    _2 = int(temp % 10)
    _3 = int((temp * 10) % 10)
    return _1, _2, _3


def cat_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', mode='r') as f:
        return int(f.read())


def digitalWriteByte(val, _idx):
    # print(f'chip {_idx} display {val}')
    # 片选
    for _id, chip in enumerate(chip_select):
        GPIO.output(chip, GPIO.HIGH if _id != _idx else GPIO.LOW)
    # GPIO.output设置某个针脚输出状态，1or0
    # 由上往下是a\b\c\d\e\f\g\dp显示引脚
    GPIO.output(pins[0], val & 0x40)
    GPIO.output(pins[1], val & 0x20)
    GPIO.output(pins[2], val & 0x10)
    GPIO.output(pins[3], val & 0x08)
    GPIO.output(pins[4], val & 0x04)
    GPIO.output(pins[5], val & 0x02)
    GPIO.output(pins[6], val & 0x01)
    GPIO.output(pins[7], val & 0x80)


def with_dp(value):
    return value | 0x80


def display_debug():
    import time
    for x in range(10):
        digitalWriteByte(seg_code[x], 0)
        time.sleep(1)


if __name__ == "__main__":
    setup()
    refresh()
    # display_debug()
