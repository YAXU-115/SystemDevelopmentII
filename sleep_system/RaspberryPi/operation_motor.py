import time
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    print("Import failure 'RPi.GPIO'")
    GPIO = None

# GPIOピン番号
PIN_FORWARD = 25       # 正転用ピン
PIN_REVERSE = 24       # 逆転用ピン

# 温度ごとの閾値と出力レベル
STOP = 0 #切
WEAK = 20  # 弱
MODERATELY_WEAK = 35 # 微弱
MODERATE = 50 # 中
MODERATELY_STRONG = 65 # 微強
STRONG = 80 # 強

def dc_motor(duty, sleep_time=5):

    p_forward = None
    p_reverse = None

    if GPIO is None:
        print("'RPi.GPIO' not imported")
        return

    try:
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(PIN_FORWARD, GPIO.OUT)
        GPIO.setup(PIN_REVERSE, GPIO.OUT)

        # PWMオブジェクトを作成
        p_forward = GPIO.PWM(PIN_FORWARD, 50) # 周波数50Hz
        p_reverse = GPIO.PWM(PIN_REVERSE, 50)

        p_forward.start(0)
        p_reverse.start(0)

        # 正転方向にデューティ比を設定
        p_reverse.ChangeDutyCycle(0)
        p_forward.ChangeDutyCycle(duty)

        time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Enter Ctrl + C")

    except Exception as error:
        print(f"Error: {error}")

    finally:

        if p_forward:
            p_forward.stop()
        if p_reverse:
            p_reverse.stop()

        GPIO.cleanup()

def get_duty(temperature, humidity, pressure, altitude):
    # 温度と湿度に基づいてファンの出力レベルを決定
    levels = [
        (20.0, [(20.0, STOP), (30.0, WEAK), (40.0, MODERATELY_WEAK), (50.0, MODERATE), (60.0, MODERATELY_STRONG), (float('inf'), STRONG)]),
        (23.0, [(20.0, WEAK), (35.0, MODERATELY_WEAK), (50.0, MODERATE), (65.0, MODERATELY_STRONG), (float('inf'), STRONG)]),
        (25.0, [(30.0, MODERATELY_WEAK), (45.0, MODERATE), (60.0, MODERATELY_STRONG), (float('inf'), STRONG)]),
        (30.0, [(40.0, MODERATE), (55.0, MODERATELY_STRONG), (float('inf'), STRONG)]),
        (35.0, [(50.0, MODERATELY_STRONG), (float('inf'), STRONG)]),
        (float('inf'), [(float('inf'), STRONG)])  # 35度以上は強
    ]
    # 湿度ごとの閾値と出力レベル
    for temperature_th, humidity_levels in levels:
        if temperature < temperature_th:
            for humidity_th, level in humidity_levels:
                if humidity < humidity_th:
                    return level
    # デフォルトは強
    return STRONG