# -*- coding: utf-8 -*-
# data_manager.py

import pymysql.cursors
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import config

# ディレクトリのパスを取得
script_dir = Path(__file__).resolve().parent

# .envファイルを読み込む
env_path = script_dir / '.env'
load_dotenv(dotenv_path=env_path)

class LocalDatabaseManager:
    """ローカルデータベース操作を管理するクラス"""

    def __init__(self):
        self.connection = self._get_db_connection()

    def _get_db_connection(self):
        try:
            connection = pymysql.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                db=os.getenv('DB_NAME'),
                charset="utf8",
                cursorclass=pymysql.cursors.DictCursor
            )
            if config.DEVELOP:
                print("データベースに接続しました。")
            return connection
        except pymysql.MySQLError as e:
            if config.DEVELOP:
                print(f"データベース接続エラー: {e}")
            return None

    def insert_record(self, temp: float, hum: float, pres: float, alt: float, duty: int, ts: datetime):
        if not self.connection: return
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO sensor_readings (temperature, humidity, pressure, altitude, timestamp) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (temp, hum, pres, alt, ts))

                sql = "INSERT INTO fan_control_logs (pwm_value, timestamp) VALUES (%s, %s)"
                cursor.execute(sql, (duty, ts))
            self.connection.commit()
        except pymysql.MySQLError as e:
            if config.DEVELOP:
                print(f"データベースへの書き込みエラー: {e}")

    def get_recent_readings(self, num_readings: int) -> list:
        if not self.connection: return []
        try:
            with self.connection.cursor() as cursor:
                sql = f"SELECT id, temperature, humidity, pressure, altitude FROM sensor_readings ORDER BY id DESC LIMIT %s"
                cursor.execute(sql, (num_readings,))
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            if config.DEVELOP:
                print(f"データベースからの読み取りエラー: {e}")
            return []

    def clear_tables(self, *table_names):
        if not self.connection: return
        try:
            with self.connection.cursor() as cursor:
                for table in table_names:
                    if not table.isidentifier(): continue
                    cursor.execute(f"TRUNCATE TABLE `{table}`")
                    print(f"テーブル '{table}' をクリアしました。")
            self.connection.commit()
        except pymysql.MySQLError as e:
            if config.DEVELOP:
                print(f"テーブルクリア中のエラー: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            if config.DEVELOP:
                print("データベース接続を閉じました。")

class CsvLogger:
    """CSVファイルへのロギングを管理するクラス"""

    def __init__(self, filename: str):
        self.filename = filename
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # ヘッダーを書き込む
        if not os.path.exists(filename):
            self.append_csv("client_name,temperature,humidity,pressure,altitude,fan_duty,timestamp\n")

    def format_for_csv(self, datatype: str, client_name: str, temp: float, hum: float, pres: float, alt: float, duty: int, ts: datetime) -> str:
        return f"{datatype},{client_name},{temp},{hum},{pres},{alt},{duty},{ts}\n"

    def append_csv(self, message: str):
        try:
            with open(self.filename, "a", encoding="UTF-8") as f:
                f.write(message)
        except IOError as e:
            if config.DEVELOP:
                print(f"CSVファイルへの書き込みエラー: {e}")