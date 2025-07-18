try:
    import RPi.GPIO as GPIO
    import get_to_bme280
    import operation_csv
except:
    import RaspberryPi.get_to_bme280 as get_to_bme280
    import RaspberryPi.operation_csv as operation_csv
finally:
    from time import sleep
    from datetime import datetime
    


def dc_motor(temp, hum, pres, alt):

    try:
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(25, GPIO.OUT)
        GPIO.setup(24, GPIO.OUT)
        p0 = GPIO.PWM(25, 50)
        p1 = GPIO.PWM(24, 50)
        p0.start(0)
        p1.start(0)

        duty = get_duty(temp, hum, pres, alt)

        # 例：p0を正転、p1を停止（逆転したい場合はp0とp1を逆に）
        p1.ChangeDutyCycle(0)
        p0.ChangeDutyCycle(duty)

        p0.stop()
        p1.stop()
        GPIO.cleanup()

    except KeyboardInterrupt:
        print("Enter Ctrl + C")
        if duty == None or duty == "":
            duty = 80 #強

    except Exception as error:
        print(f"Error: {error}")
        if duty == None or duty == "":
            duty = 80 #強

    return duty

def get_duty(temp, hum, pres, alt):
    # 温度ごとの閾値と出力レベル
    Weak = 20  # 弱
    Moderately_Weak = 35 # 微弱
    Moderate = 50 # 中
    Moderately_strong = 65 # 微強
    Strong = 80 # 強
    # 温度と湿度に基づいてファンの出力レベルを決定
    levels = [
        (20.0, [(20.0, Weak), (35.0, Moderately_Weak), (50.0, Moderate), (65.0, Moderately_strong), (float('inf'), Strong)]),
        (25.0, [(30.0, Moderately_Weak), (45.0, Moderate), (60.0, Moderately_strong), (float('inf'), Strong)]),
        (30.0, [(40.0, Moderate), (55.0, Moderately_strong), (float('inf'), Strong)]),
        (35.0, [(50.0, Strong), (float('inf'), Strong)]),
        (float('inf'), [(float('inf'), Strong)])  # 35度以上は強
    ]
    # 湿度ごとの閾値と出力レベル
    for temp_th, hum_levels in levels:
        if temp < temp_th:
            for hum_th, level in hum_levels:
                if hum < hum_th:
                    return level
    # デフォルトは強
    return Strong

def change_dict(client_name, temperature, humidity, pressure, altitude, fan_duty):
    message = {
        "client_name": client_name,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "altitude": altitude,
        "fan_duty": fan_duty
    }
    return message

def main():
    filename = "sleep_system/RaspberryPi/data.csv"
    operation = operation_csv.CsvClass(filename=filename)

    while True:
        try:
            temp, hum, pres, alt = get_to_bme280.get_bme280_data()
            duty = dc_motor(temp, hum, pres, alt)
        except:
            temp, hum, pres, alt = get_to_bme280.get_bme280_data_test()
            duty = 80

        print(f"Temperature: {temp}°C, Humidity: {hum}%, Pressure: {pres}hPa, Altitude: {alt}m, Fan Duty Cycle: {duty}%")

        message = operation.change_csv(client_name='RaspberryPi',temperature=temp,humidity=hum,pressure=pres,altitude=alt,fan_duty=duty,time=datetime.now())

        operation.append_csv(message=message)
        read_file = operation.read_csv()

        print(read_file)
        # Wait for a while before the next reading
        sleep(1)

if __name__ == "__main__":
    main()


