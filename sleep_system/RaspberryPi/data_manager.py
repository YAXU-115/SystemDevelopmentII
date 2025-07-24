# -*- coding: utf-8 -*-
# data_manager.py

import pymysql.cursors
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import config
import pyodbc


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
            if config.DEVELOP:
                print("ローカルデータベースにデータを送信しました。")
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

class CloudDatabaseManager:
    """クラウドデータベース操作を管理するクラス"""

    def __init__(self):
        self.connection = self._get_db_connection()

    def _get_db_connection(self):
        # クラウドデータベースの接続処理を実装
        try:
            connection_string = (
                f'DRIVER={os.getenv("AZURE_DRIVER")};SERVER={os.getenv("AZURE_SERVER")};PORT=1433;DATABASE={os.getenv("AZURE_DATABASE")};'
                f'UID={os.getenv("AZURE_USERNAME")};PWD={os.getenv("AZURE_PASSWORD")};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            )
            connection = pyodbc.connect(connection_string)
            if config.DEVELOP:
                print("クラウドデータベースに接続しました。")
            return connection
        except pyodbc.Error as e:
            if config.DEVELOP:
                print(f"クラウドデータベース接続エラー: {e}")
            return None

    def one_hour_insert_record(self, temp: float, hum: float, pres: float, alt: float, duty: int, ts: datetime):
        # クラウドデータベースへのレコード挿入処理を実装
        if not self.connection: return []
        try:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO raw_iot_data (recorded_time, avg_temp, avg_humidity, avg_pressure, avg_altitude, avg_pwm) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(sql, (ts, temp, hum, pres, alt, duty))

            self.connection.commit()
            if config.DEVELOP:
                print("Azure SQL にデータを送信しました。")
        except pyodbc.Error as e:
            if config.DEVELOP:
                print(f"クラウドデータベースへの書き込みエラー: {e}")

    def get_recent_readings(self, num_readings: int) -> list:
        # クラウドデータベースからの最近の読み取り値取得処理を実装
        if not self.connection: return []
        try:
            with self.connection.cursor() as cursor:
                sql = f"SELECT TOP {num_readings} * FROM sensor_readings ORDER BY timestamp DESC"
                cursor.execute(sql)
                return cursor.fetchall()
        except pyodbc.Error as e:
            if config.DEVELOP:
                print(f"クラウドデータベースからの読み取りエラー: {e}")
            return []
    
    def cloud_count_init(self):
        """クラウド送信カウンターの初期化"""
        if config.DEVELOP and config.CLOUD_DEVELOP:
            print("CLOUD_DEVELOPモードでクラウド送信カウンターを718に設定します。")
            return 718
        elif config.DEVELOP:
            print("クラウド送信カウンターを0に設定します。")
            return 0
        else:
            return 0
    
    def one_hour_average(self):
        try:
            # ローカルデータベースの直近１時間の平均値を取得する処理を実装
            localdb = LocalDatabaseManager()
            # localdb.get_recent_readings(config.SENT_AZURE_COUNT)  # ローカルデータベースからの最近の読み取り値を取得
            data = localdb.get_recent_readings(config.SENT_AZURE_COUNT - self.cloud_count_init())  # クラウド送信カウンターを引いた値で取得

            ave_temp = sum(d['temperature'] for d in data) / len(data)
            ave_hum = sum(d['humidity'] for d in data) / len(data)
            ave_pres = sum(d['pressure'] for d in data) / len(data)
            ave_alt = sum(d['altitude'] for d in data) / len(data)

            return ave_temp, ave_hum, ave_pres, ave_alt
        except ZeroDivisionError:
            if config.DEVELOP:
                print("データがありません。平均値を計算できません。")
            return None, None, None, None
        except pymysql.MySQLError as e:
            if config.DEVELOP:
                print(f"ローカルデータベースからの平均値取得エラー: {e}")
            return None, None, None, None
        except pyodbc.Error as e:
            if config.DEVELOP:
                print(f"クラウドデータベースからの平均値取得エラー: {e}")
            return None, None, None, None

    def clear_tables(self, *table_names):
        # クラウドデータベースのテーブルクリア処理を実装
        if not self.connection: return
        try:
            with self.connection.cursor() as cursor:
                for table in table_names:
                    if not table.isidentifier(): continue
                    cursor.execute(f"TRUNCATE TABLE {table}")
                    if config.DEVELOP:
                        print(f"テーブル '{table}' をクリアしました。")
            self.connection.commit()
        except pyodbc.Error as e:
            if config.DEVELOP:
                print(f"クラウドデータベースのテーブルクリア中のエラー: {e}")

    def close(self):
        # クラウドデータベース接続を閉じる処理を実装
        if self.connection:
            self.connection.close()
            if config.DEVELOP:
                print("クラウドデータベース接続を閉じました。")
        pass

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