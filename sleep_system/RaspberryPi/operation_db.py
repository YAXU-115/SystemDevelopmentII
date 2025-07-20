import pymysql.cursors #pip install pymysql
import os
from dotenv import load_dotenv # dotenvからload_dotenvをインポート pip install python-dotenv
from pathlib import Path
# ディレクトリのパスを取得
script_dir = Path(__file__).resolve().parent

# .envファイルのフルパスを指定して読み込む
dotenv_path = script_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

def _get_db_connection():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_ip_addr = "localhost"
    return pymysql.connect(
        host=db_ip_addr, user=db_user, password=db_password,
        db="sleep_system_db", charset="utf8")

def get_db(tblname): 

    def _print_database(sqldata_list):
        for data in sqldata_list:
            print(data)
        if sqldata_list == []:
            print(sqldata_list)
        
    """
    import operation_db
    data = operation_db.get_db("tblname")
    print(data)
    """
    connection = _get_db_connection()
    print("データベースに接続しました。")

    sqldata_list = []
    try:
        with connection.cursor() as cursor:
            if not tblname.isidentifier():
                raise ValueError("Invalid table name")
            sql = f"SELECT * FROM {tblname}"
            cursor.execute(sql)
            result = cursor.fetchall()

        for data in result :
            sqldata_list.append(data)
    except Exception as e:
        print(f"DB取得時にエラーが発生しました: {e}")
    finally:
        connection.close()
        _print_database(sqldata_list)
        return sqldata_list

def put_data_record(temperature, humidity, pressure, altitude, fan_duty, time):
    """
    import operation_db
    import datetime
    time = datetime.datetime.now()
    operation_db.put_data_record(25.6, 30.0, 1013.3, 100.0, 35, time)
    """
    connection = _get_db_connection()
    print("データベースに接続しました。")

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO sensor_readings(temperature, humidity, pressure, altitude, timestamp) VALUES(%s, %s, %s, %s, %s)"
            print(sql)
            cursor.execute(sql,(temperature, humidity, pressure, altitude, time))
            sql = "INSERT INTO fan_control_logs(pwm_value, timestamp) VALUES(%s, %s)"
            print(sql)
            cursor.execute(sql,(fan_duty, time))
            print(f"DBにdataを送信しました。")
        connection.commit()
    except Exception as e:
        print(f"DB送信時にエラーが発生しました: {e}")
    finally:
        connection.close()

def clear_table(*tblnames):
    """
    import operation_db
    operation_db.clear_table("tblname1","tblname2",・・・)
    """
    for tblname in tblnames:
        connection = _get_db_connection()
        try:
            with connection.cursor() as cursor:
                if not tblname.isidentifier():
                    raise ValueError("Invalid table name")
                cursor.execute(f"TRUNCATE TABLE `{tblname}`")

            connection.commit()
            print(f"{tblname} のデータを初期化しました。")
        except Exception as e:
            print(f"初期化中にエラーが発生しました: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    import datetime

    time = datetime.datetime.now()

    get_db("sensor_readings")
    get_db("fan_control_logs")

    put_data_record(temperature=25.6, humidity= 30.0, pressure=1013.3, altitude=100.0, fan_duty=35, time=time)

    get_db("sensor_readings")
    get_db("fan_control_logs")

    clear_table("sensor_readings","fan_control_logs")

    get_db("sensor_readings")
    get_db("fan_control_logs")