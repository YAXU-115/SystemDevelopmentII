# -*- coding: utf-8 -*-
# /usr/bin/env python
# Example code to use Adafruit_CircuitPython_BME280
# https://github.com/adafruit/Adafruit_CircuitPython_BME280
# 
# MIT License
# 
# Original work: Copyright (c) 2021 Michiharu Takemoto <takemoto.development@gmail.com>
# Modifications: Copyright (c) 2025 YAXU-115 <yamaguchi.sota.main@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
import config

try:
    import board
    from adafruit_bme280 import basic as adafruit_bme280
    IS_RPI = True
except (ImportError, RuntimeError):
    IS_RPI = False

class SensorHandler:
    """BME280センサーを管理し、環境データを読み取るクラス"""

    def __init__(self, i2c_address: int = config.I2C_ADDRESS):
        """
        センサーを初期化する。
        Raspberry Pi以外の環境では、モック（テスト用）モードで動作する。
        """
        self.sensor = None
        if IS_RPI:
            try:
                i2c = board.I2C()
                self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=i2c_address)
                self.sensor.sea_level_pressure = config.SEA_LEVEL_PRESSURE
                if config.DEVELOP:
                    print("BME280センサーの初期化に成功しました。")
            except Exception as e:
                if config.DEVELOP:
                    print(f"センサーの初期化に失敗しました: {e}")
                self.sensor = None # Fallback to mock
        else:
            if config.DEVELOP:
                print("RPi環境ではないため、センサーをモックモードで起動します。")

    def read_data(self) -> tuple[float, float, float, float, str] | None:
        """
        センサーから温度、湿度、気圧、高度を読み取る。
        センサーが利用できない場合は、テストデータを返す。
        """
        if self.sensor:
            try:
                temperature = self.sensor.temperature
                humidity = self.sensor.relative_humidity
                pressure = self.sensor.pressure
                altitude = self.sensor.altitude
                datatype = "sensor"
                return temperature, humidity, pressure, altitude, datatype
            except Exception as e:
                if config.DEVELOP:
                    print(f"センサーデータの読み取り中にエラーが発生しました: {e}")
                return self._read_mock_data()
        else:
            return self._read_mock_data()

    def _read_mock_data(self) -> tuple[float, float, float, float, str]:
        """テスト用の模擬センサーデータを生成する。"""
        temp = round(random.uniform(20.0, 30.0), 2)
        hum = round(random.uniform(40.0, 60.0), 2)
        pres = round(random.uniform(1000.0, 1020.0), 2)
        alt = round(random.uniform(50.0, 150.0), 2)
        datatype = "test"
        if config.DEVELOP:
            print("モックデータを生成しました。")
        return temp, hum, pres, alt, datatype