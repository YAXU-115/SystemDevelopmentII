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

try:
    import board
    from adafruit_bme280 import basic as adafruit_bme280

    i2c = board.I2C()
    instance_bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

    instance_bme280.sea_level_pressure = 1013.30
except Exception:
    pass
finally:
    import time
    import random

def get_bme280_data():
    temperature = instance_bme280.temperature
    humidity = instance_bme280.relative_humidity
    pressure = instance_bme280.pressure
    altitude = instance_bme280.altitude
    return temperature, humidity, pressure, altitude

def get_bme280_data_test():
    temp = 200.0
    hum  = 100.0
    pres = 1013.25
    alt = 10000.0
    return temp, hum, pres, alt

if __name__ == "__main__":
    while True:
        try:
            temp, hum, pres, alt = get_bme280_data()
        except:
            temp, hum, pres, alt = get_bme280_data_test()
        print(f"Temperature: {temp:.2f} C")
        print(f"Humidity: {hum:.2f} %")
        print(f"Pressure: {pres:.2f} hPa")
        print(f"Altitude: {alt:.2f} m")
        time.sleep(1)
