# -*- coding: utf-8 -*-
# main.py

import time
import datetime
import statistics
import config
from collections import deque

# モジュールのインポート
import sensor_handler
import fan_controller
import data_manager

def calculate_average(readings: list[dict]) -> tuple[float, float, float, float]:
    """
    直近のデータ群から各項目の平均値を計算する。
    外れ値の影響を低減するため、中央値を加えた加重平均を使用する。
    """
    if not readings:
        return 0.0, 0.0, 0.0, 0.0

    # データを項目ごとにまとめる
    temps = [r['temperature'] for r in readings]
    hums = [r['humidity'] for r in readings]
    press = [r['pressure'] for r in readings]
    alts = [r['altitude'] for r in readings]

    def weighted_avg(data: list) -> float:
        if not data: return 0.0
        median = statistics.median(data)#中央値を取得
        weighted_list = data + [median, median]#Weighted Medianフィルタ
        return round(sum(weighted_list) / len(weighted_list), 2)

    avg_temp = weighted_avg(temps)
    avg_hum = weighted_avg(hums)
    avg_pres = weighted_avg(press)
    avg_alt = weighted_avg(alts)

    return avg_temp, avg_hum, avg_pres, avg_alt


def main():
    """メイン処理"""
    # --- 初期化 ---
    sensor = sensor_handler.SensorHandler()
    fan = fan_controller.FanController(config.PIN_FORWARD, config.PIN_REVERSE)
    db_manager = data_manager.LocalDatabaseManager()
    csv_logger = data_manager.CsvLogger(config.CSV_FILENAME)

    # 起動時にテーブルをクリア
    db_manager.clear_tables(config.DB_TABLES["readings"], config.DB_TABLES["logs"])

    # 平均計算用のデータ保持（固定長キュー）
    recent_readings_for_avg = deque(maxlen=config.NUM_READINGS_FOR_AVG)

    try:
        while True:
            # --- 1. センサーデータ取得 ---
            sensor_data = sensor.read_data()
            if sensor_data is None:
                if config.DEVELOP:
                    print(f"センサーデータが取得できません。{config.LOOP_INTERVAL_SECONDS}秒待機します。")
                time.sleep(config.LOOP_INTERVAL_SECONDS)
                continue

            temp, hum, pres, alt = sensor_data

            # --- 2. Duty比の計算 ---
            # 十分なデータが溜まるまでは現在の値で、溜まったら平均値で判断
            if len(recent_readings_for_avg) < config.NUM_READINGS_FOR_AVG:
                duty = fan_controller.calculate_fan_duty(temp, hum)
            else:
                avg_temp, avg_hum, _, _ = calculate_average(list(recent_readings_for_avg))
                duty = fan_controller.calculate_fan_duty(avg_temp, avg_hum)

            # --- 3. ファン制御 ---
            fan.set_speed(duty)

            # --- 4. データ記録 ---
            now = datetime.datetime.now()
            db_manager.insert_record(temp, hum, pres, alt, duty, now)

            csv_message = csv_logger.format_for_csv(
                config.CLIENT_NAME, temp, hum, pres, alt, duty, now
            )
            csv_logger.append_csv(csv_message)

            if config.DEVELOP:
                for data in db_manager.get_recent_readings(config.NUM_READINGS_FOR_AVG):
                    print(data)


            # 現在の読み取り値を辞書としてキューに追加
            current_reading = {"temperature": temp, "humidity": hum, "pressure": pres, "altitude": alt}
            recent_readings_for_avg.append(current_reading)

            print(f"Time: {now.strftime('%H:%M:%S')} | Temp: {temp}°C | Hum: {hum}% | Duty: {duty}%")

            # --- 5. 待機 ---
            time.sleep(config.LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        if config.DEVELOP:
            print("\nプログラムを終了します。")
    except Exception as e:
        if config.DEVELOP:
            print(f"予期せぬエラーが発生しました: {e}")
    finally:
        # --- 終了処理 ---
        fan.stop()
        fan.cleanup()
        db_manager.close()

if __name__ == "__main__":
    main()