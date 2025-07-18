import pymysql.cursors #pip install pymysql
import os
from dotenv import load_dotenv # dotenvからload_dotenvをインポート pip install python-dotenv
from pathlib import Path

# ディレクトリのパスを取得
script_dir = Path(__file__).resolve().parent

# .envファイルのフルパスを指定して読み込む
dotenv_path = script_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)

# 環境変数として読み込まれた値を取得
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

db_ip_addr = "localhost"
connection = pymysql.connect(host=db_ip_addr,user=db_user,password=db_password,db="iotdb",charset="utf8")
print("データベースに接続しました。")
# ... 処理 ...
connection.close()