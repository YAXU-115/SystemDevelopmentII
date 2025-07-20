# -*- coding: utf-8 -*-
# fan_controller.py

import time
import config

try:
    import RPi.GPIO as GPIO
    IS_RPI = True
except (ImportError, RuntimeError):
    GPIO = None
    IS_RPI = False

def calculate_fan_duty(temperature: float, humidity: float) -> int:
    """
    温度と湿度に基づいてファンのDuty比を決定する。
    Args:
        temperature (float): 温度 (°C)
        humidity (float): 湿度 (%)
    Returns:
        int: ファンのDuty比 (%)
    """
    s = config.FAN_SPEED
    if temperature < 20.0:
        if humidity < 30.0: return s["WEAK"]
        if humidity < 40.0: return s["MODERATELY_WEAK"]
        return s["MODERATE"]
    elif temperature < 25.0:
        if humidity < 45.0: return s["MODERATELY_WEAK"]
        if humidity < 60.0: return s["MODERATE"]
        return s["MODERATELY_STRONG"]
    elif temperature < 30.0:
        if humidity < 55.0: return s["MODERATE"]
        return s["MODERATELY_STRONG"]
    else: # 30.0度以上
        return s["STRONG"]

class FanController:
    """DCモーターファンを制御するクラス"""

    def __init__(self, pin_fwd: int, pin_rev: int):
        self.pin_fwd = pin_fwd
        self.pin_rev = pin_rev
        self.pwm_forward = None
        self.pwm_reverse = None

        if IS_RPI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin_fwd, GPIO.OUT)
            GPIO.setup(self.pin_rev, GPIO.OUT)
            self.pwm_forward = GPIO.PWM(self.pin_fwd, 50)  # 50Hz
            self.pwm_reverse = GPIO.PWM(self.pin_rev, 50)
            self.pwm_forward.start(0)
            self.pwm_reverse.start(0)
            if config.DEVELOP:
                print("ファンコントローラーを初期化しました。")
        else:
            if config.DEVELOP:
                print("RPi環境ではないため、ファンコントローラーはダミーモードです。")

    def set_speed(self, duty_cycle: int):
        """
        指定されたDuty比でファンの速度を設定する。
        Args:
            duty_cycle (int): ファンの速度 (0-100)
        """
        if not IS_RPI or not self.pwm_forward:
            if config.DEVELOP:
                print(f"ファン速度を {duty_cycle}% に設定しました (ダミー)。")
            return
        
        self.pwm_forward.ChangeDutyCycle(duty_cycle)
        self.pwm_reverse.ChangeDutyCycle(0)

    def stop(self):
        """ファンを停止する。"""
        self.set_speed(0)

    def cleanup(self):
        """GPIO設定をクリーンアップする。"""
        if IS_RPI:
            if self.pwm_forward: self.pwm_forward.stop()
            if self.pwm_reverse: self.pwm_reverse.stop()
            GPIO.cleanup()
            if config.DEVELOP:
                print("GPIOをクリーンアップしました。")