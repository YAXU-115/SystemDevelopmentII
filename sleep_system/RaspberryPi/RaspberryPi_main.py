import time
import datetime
import statistics
try:
    import get_to_bme280
    import operation_csv
    import operation_db
    import operation_motor
except:
    import RaspberryPi.get_to_bme280 as get_to_bme280
    import RaspberryPi.operation_csv as operation_csv
    import RaspberryPi.operation_db as operation_db
    import RaspberryPi.operation_motor as operation_motor

NUM_READINGS = 5

def change_dict(client_name, temperature, humidity, pressure, altitude, fan_duty) -> dict: 
    message = {
        "client_name": client_name,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "altitude": altitude,
        "fan_duty": fan_duty
    }
    return message

def average_calculation(readings, num_reasings=NUM_READINGS):

    latest_readings = readings[-num_reasings:]

    #データを項目ごとにまとめる
    columns = list(zip(*latest_readings))
    columns_to_process = columns[1:-1]
    
    weighted_averages = []

    for column_data in columns_to_process:
        #中央値を取得
        median = statistics.median(column_data)

        #Weighted Medianフィルタ
        weighted_list = list(column_data) + [median, median]

        average = sum(weighted_list) / len(weighted_list)
        rounded_average = round(average, 2)
        weighted_averages.append(rounded_average)

    temperature = weighted_averages[0]
    humidity = weighted_averages[1]
    pressure = weighted_averages[2]
    altitude = weighted_averages[3]

    return temperature, humidity, pressure, altitude

def main():
    
    #初期化
    CSV_FILENAME = "sleep_system/RaspberryPi/data.csv"
    WAITINF_TIME = 5
    csv_operation = operation_csv.CsvClass(filename=CSV_FILENAME)
    operation_db.clear_table("sensor_readings","fan_control_logs")


    while True:
        #データベースの中身を取得
        try:
            db_datalist_bme280 = operation_db.get_db("sensor_readings")
            db_datalist_duty   = operation_db.get_db("fan_control_logs")
        except Exception:
            break
        # データベースの確認
        if db_datalist_bme280 == db_datalist_duty: #両社とも []　の場合
            pass
        elif db_datalist_bme280[-1][0] != db_datalist_duty[-1][0]: #idが一致しなかった場合
            operation_db.clear_table("sensor_readings","fan_control_logs")
        else: #通常時
            pass

        #センサデータまたはテストデータを取得
        try:
            temp, hum, pres, alt = get_to_bme280.get_bme280_data()
        except:
            temp, hum, pres, alt = get_to_bme280.get_bme280_data_test()

        #duty比の取得
        time_now = datetime.datetime.now()
        if (db_datalist_bme280 == [] and db_datalist_duty == []):
            duty = operation_motor.get_duty(temp, hum, pres, alt)
        elif (WAITINF_TIME * db_datalist_bme280[-1][0] ) // 60 == 0:
            a_temp, a_hum, a_pres, a_alt = average_calculation(db_datalist_bme280)
            duty = operation_motor.get_duty(a_temp, a_hum, a_pres, a_alt)
        
        operation_db.put_data_record(temperature=temp, humidity=hum, pressure=pres, altitude=alt, fan_duty=duty, time=time_now)

        print(f"Temperature: {temp}°C, Humidity: {hum}%, Pressure: {pres}hPa, Altitude: {alt}m, Fan Duty Cycle: {duty}% Now Time: {time_now}")

        message = csv_operation.change_csv(client_name='RaspberryPi',temperature=temp,humidity=hum,pressure=pres,altitude=alt,fan_duty=duty,time=datetime.datetime.now())
        csv_operation.append_csv(message=message)
        read_file = csv_operation.read_csv()
        operation_motor.dc_motor(duty,WAITINF_TIME)

        print(read_file)

if __name__ == "__main__":
    db_datalist_bme280 = operation_db.get_db("sensor_readings")
    a_temp, a_hum, a_pres, a_alt = average_calculation(db_datalist_bme280)
    print(a_temp, a_hum, a_pres, a_alt)
    # main()


