# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from time import sleep

# MCP3208からSPI通信で12ビットのデジタル値を取得。0から7の8チャンネル使用可
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if adcnum > 7 or adcnum < 0:
        return -1
    GPIO.output(cspin, GPIO.HIGH)
    GPIO.output(clockpin, GPIO.LOW)
    GPIO.output(cspin, GPIO.LOW)

    commandout = adcnum
    commandout |= 0x18  # スタートビット＋シングルエンドビット
    commandout <<= 3    # LSBから8ビット目を送信するようにする
    for i in range(5):
        # LSBから数えて8ビット目から4ビット目までを送信
        if commandout & 0x80:
            GPIO.output(mosipin, GPIO.HIGH)
        else:
            GPIO.output(mosipin, GPIO.LOW)
        commandout <<= 1
        GPIO.output(clockpin, GPIO.HIGH)
        GPIO.output(clockpin, GPIO.LOW)
    adcout = 0
    # 13ビット読む（ヌルビット＋12ビットデータ）
    for i in range(13):
        GPIO.output(clockpin, GPIO.HIGH)
        GPIO.output(clockpin, GPIO.LOW)
        adcout <<= 1
        if i>0 and GPIO.input(misopin)==GPIO.HIGH:
            adcout |= 0x1
    GPIO.output(cspin, GPIO.HIGH)
    return adcout

GPIO.setmode(GPIO.BCM)
# ピンの名前を変数として定義
SPICLK = 11
SPIMOSI = 10
SPIMISO = 9
SPICS = 8
# SPI通信用の入出力を定義
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICS, GPIO.OUT)

GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
p0 = GPIO.PWM(25, 50)
p1 = GPIO.PWM(24, 50)
p0.start(0)
p1.start(0)

adc_pin0 = 0

def set_input_value(val=None):
    """アナログ入力値を取得または外部からセット"""
    if val is not None:
        return val
    else:
        return readadc(adc_pin0, SPICLK, SPIMOSI, SPIMISO, SPICS)
import random

try:
    while True:
        # ランダムな値（0～4095）を生成して入力値とする
        inputVal0 = set_input_value(random.randint(0, 4095))

        # 5段階に分ける
        if inputVal0 < 819:  # 0～818
            duty = 20  # 弱
        elif inputVal0 < 1638:  # 819～1637
            duty = 35  # 微弱
        elif inputVal0 < 2457:  # 1638～2456
            duty = 50  # 中
        elif inputVal0 < 3276:  # 2457～3275
            duty = 65  # 微強
        else:  # 3276～4095
            duty = 80  # 強

        # 例：p0を正転、p1を停止（逆転したい場合はp0とp1を逆に）
        p1.ChangeDutyCycle(0)
        p0.ChangeDutyCycle(duty)

        print(f"inputVal0={inputVal0}, duty={duty}")

        sleep(10)


except KeyboardInterrupt:
    pass

p0.stop()
p1.stop()
GPIO.cleanup()
