from flask import Flask, render_template, request, redirect, url_for
import datetime, csv, socket
from functools import wraps
import threading
import main, config


app = Flask(__name__)

main_thread = None
feedback_status = None

def log_access(method):
    """アクセスログ用デコレーター"""
    @wraps(method)
    def wrapper(*args, **kwargs):
        visitor_ip = request.remote_addr
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{request.method}_access {time_now} {visitor_ip}")
        print("リクエストを受け付けました。")
        return method(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET"])
@log_access
def get_index():
    global main_thread
    global sleep_status
    sleep_status = request.args.get('sleep_status') or request.args.get('status', '')
    if sleep_status:
        # ここでsleep_statusを処理するロジックを追加できます
        # 例: データベースに保存、ログに記録など
        # 現在はコンソールに出力するだけ
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

@app.route("/feedback", methods=["POST"])
@log_access
def post_feedback():
    global sleep_status
    print("POSTリクエストを受け付けました。")
    feedback_status = request.form.get('comfort_level', '')
    if not feedback_status:
        print("フィードバックステータスが提供されていません。")
    if feedback_status:
        # ここでfeedback_statusを処理するロジックを追加できます
        # 例: データベースに保存、ログに記録など
        # 現在はコンソールに出力するだけ
        feedback_data = feedback_status.lower()

        print(f"フィードバックステータス: {feedback_data}")

    """POSTリクエストでのインデックスページ"""
    return redirect(url_for('index', sleep_status=sleep_status))

@app.route("/feedback" , methods=["GET"])
def feedback():
    global sleep_status
    return render_template("feedback.html", sleep_status=sleep_status)

@app.route("/index", methods=["GET"])
def index():
    global sleep_status 
    return render_template("index.html", sleep_status=sleep_status)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
    config.LOG_FILE.close()
    print("Flaskアプリケーションを終了します。")    
    main.stop()