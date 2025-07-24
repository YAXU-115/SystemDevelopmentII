# -*- coding: utf-8 -*-
# config.py

# --- develop Settings ---
DEVELOP = False
CLOUD_DEVELOP = False

# --- Sensor Settings ---
I2C_ADDRESS = 0x76
SEA_LEVEL_PRESSURE = 1013.25  # hPa

# --- Fan Controller Settings ---
# GPIO Pin numbers (BCM mode)
PIN_FORWARD = 25  # 正転用ピン
PIN_REVERSE = 24  # 逆転用ピン

# Fan speed duty cycles (%)
FAN_SPEED = {
    "STOP": 0,
    "WEAK": 20,
    "MODERATELY_WEAK": 35,
    "MODERATE": 50,
    "MODERATELY_STRONG": 65,
    "STRONG": 80
}

# --- Data Logging Settings ---
CSV_FILENAME = "sleep_system/RaspberryPi/data/data.csv"
DB_TABLES = {
    "readings": "sensor_readings",
    "logs": "fan_control_logs"
}

# --- Main Application Settings ---
LOOP_INTERVAL_SECONDS = 5  # Main loop delay
NUM_READINGS_FOR_AVG = 5 # 平均計算に使用するデータ数
SENT_AZURE_COUNT = (60*60)//LOOP_INTERVAL_SECONDS  # 1時間に1回クラウドへ送信
import socket
CLIENT_NAME = socket.gethostname()