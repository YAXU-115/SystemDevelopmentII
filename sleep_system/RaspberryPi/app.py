from flask import Flask, render_template, request
import datetime, csv, socket
from functools import wraps
import threading
import main, config

app = Flask(__name__)

main_thread = None

def log_access(method):
    """アクセスログ用デコレーター"""
    @wraps(method)
    def wrapper(*args, **kwargs):
        print(f"{request.method}_access {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("リクエストを受け付けました。")
        return method(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET"])
@log_access
def get_index():
    global main_thread
    sleep_status = request.args.get('status', '') 
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

@app.route("/", methods=["POST"])
@log_access
def post_index():
    """POSTリクエストでのインデックスページ"""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)