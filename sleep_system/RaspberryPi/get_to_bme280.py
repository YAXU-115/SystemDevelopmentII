# -*- coding: utf-8 -*-
# /usr/bin/env python
# Example code to use Adafruit_CircuitPython_BME280
# https://github.com/adafruit/Adafruit_CircuitPython_BME280
#
# 
# MIT License
# 
# Copyright (c) 2021 Michiharu Takemoto <takemoto.development@gmail.com>
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

import board
import time
from adafruit_bme280 import basic as adafruit_bme280

i2c = board.I2C()
instance_bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

instance_bme280.sea_level_pressure = 1013.30

def get_bme280_data():
    temperature = instance_bme280.temperature
    humidity = instance_bme280.relative_humidity
    pressure = instance_bme280.pressure
    altitude = instance_bme280.altitude
    return temperature, humidity, pressure, altitude

def get_bme280_data_as_dict():
    temp, hum, pres, alt = get_bme280_data()
    data = {
        "temperature": temp,
        "humidity": hum,
        "pressure": pres,
        "altitude": alt
    }
    return data

def get_bme280_data_as_list():
    temp, hum, pres, alt = get_bme280_data()
    data = [temp, hum, pres, alt]
    return data

def get_bme280_data_as_iterator():
    temp, hum, pres, alt = get_bme280_data()
    yield temp
    yield hum
    yield pres
    yield alt

if __name__ == "__main__":
    # while True:
    #     temp, hum, pres, alt = get_bme280_data()
    #     print(f"\nTemperature: {temp:.1f} C")
    #     print(f"Humidity: {hum:.1f} %")
    #     print(f"Pressure: {pres:.1f} hPa")
    #     print(f"Altitude = {alt:.2f} meters")
    #     time.sleep(3)  # Adjust the sleep time as needed
    while True:
        data = get_bme280_data_as_dict()
        print(data)  # Print the data dictionary for testing
        time.sleep(3)  # Adjust the sleep time as needed