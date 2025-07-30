from flask import Flask, render_template, request, redirect, url_for
import datetime, os
from functools import wraps
import threading
import main, config
from dotenv import load_dotenv
from pathlib import Path
import data_manager
import bcrypt


script_dir = Path(__file__).resolve().parent
env_path = script_dir / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

main_thread = None
feedback_status = None
signin_flag = False
sleep_status = "stop"
time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
user_id_db = None

def log_access(method):
    """アクセスログ用デコレーター"""
    @wraps(method)
    def wrapper(*args, **kwargs):
        global time_now
        visitor_ip = request.remote_addr
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{request.method}_access {time_now} {visitor_ip}")
        print("リクエストを受け付けました。")
        return method(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET"])
@log_access
def get_index():
    global signin_flag
    if signin_flag:
        global main_thread
        global sleep_status

        sleep_status = request.args.get('sleep_status') or request.args.get('status', '')
        if sleep_status:

            if sleep_status.lower() == 'start':
                print("Sleep mode started.")
                if main_thread is None or not main_thread.is_alive():
                    main_thread = threading.Thread(target=main.main, daemon=True)
                    main_thread.start()

            elif sleep_status.lower() == 'stop':
                print("Sleep mode stopped.")
                main.stop()
                main_thread = None
            else:
                print(f"Unknown sleep status: {sleep_status}")
        """GETリクエストでのインデックスページ"""
        return render_template("index.html", sleep_status=sleep_status)
    else:
        return render_template("signin.html")

@app.route("/feedback", methods=["POST"])
@log_access
def post_feedback():
    global sleep_status
    global time_now
    global user_id_db
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cloud_db_manager = data_manager.CloudDatabaseManager()
    print("POSTリクエストを受け付けました。")
    feedback_status = request.form.get('comfort_level', '')
    if not feedback_status:
        print("フィードバックステータスが提供されていません。")
    if feedback_status:
        feedback_data = feedback_status.lower()
        cloud_db_manager.feedback_insert_record(
            user_id=user_id_db,
            feedback=feedback_data,
            ts=time_now
    )



        print(f"フィードバックステータス: {feedback_data}")

    """POSTリクエストでのインデックスページ"""
    return redirect(url_for('index', sleep_status=sleep_status))

@app.route("/signin", methods=["POST"])
@log_access
def post_signin():
    global signin_flag
    global sleep_status
    user_id = request.form.get('user_id', '')
    user_pw = request.form.get('user_pw', '')
    certification = __get_user(user_id,user_pw)

    if certification:
        signin_flag = True
        return  redirect(url_for('index', sleep_status=sleep_status))
    else:
        signin_flag = False
        return render_template("signin.html")

def __get_user(user_id,user_pw):
    global user_id_db

    if user_id == None or user_pw == None:
        return False
    
    try:
        cloud_db_manager = data_manager.CloudDatabaseManager()
        user_data = cloud_db_manager.get_user_settings(user_id=user_id)

        if not user_data:
            print(f"認証エラー: ユーザー '{user_id}' が見つかりません。")
            return False

        stored_hash_str = user_data[2]

        password_bytes = user_pw.encode('utf-8')
        stored_hash_bytes = stored_hash_str.encode('utf-8')

        user_id_db = user_data[0]  # ユーザーID

        if bcrypt.checkpw(password_bytes, stored_hash_bytes):
            return True
        else:
            return False
    except:
        return False

@app.route("/feedback" , methods=["GET"])
def feedback():
    global sleep_status
    return render_template("feedback.html", sleep_status=sleep_status)

@app.route("/index", methods=["GET"])
def index():
    global sleep_status 
    return render_template("index.html", sleep_status=sleep_status)

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

@app.route("/signin", methods=["GET"])
def signin():
    return render_template("signin.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
    config.LOG_FILE.close()
    print("Flaskアプリケーションを終了します。")    
    main.stop()