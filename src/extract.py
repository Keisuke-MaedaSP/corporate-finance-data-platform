import json # json：JSON形式の設定・APIレスポンスを扱う
import os # os：環境変数を読む
from pathlib import Path # Path：ファイルパスを安全に扱う
import requests # requests：Web APIにアクセスするライブラリ
from dotenv import load_dotenv # load_dotenv：.envの設定値を読み込む

load_dotenv()

CONFIG_PATH = Path("config/selection.json") # 取得条件の設定ファイル
OUTPUT_PATH = Path("data/raw/corporate_finance_2016_2025.json") # 取得したJSONの保存先

with CONFIG_PATH.open(encoding="utf-8") as f:
    config = json.load(f) # config = JSONをPythonの辞書として読み込んだもの

categories = config["categories"]

params = {
    "appId": os.environ["ESTAT_APP_ID"],
    "statsDataId": config["stats_data_id"],
    "cdCat01": ",".join(categories["cat01"]), # ",".joinでリストを","で区切っただけの形にする
    "cdCat02": ",".join(categories["cat02"]), # 例）["045", "051", "022"] ⇒ 045,051,022
    "cdCat03": ",".join(categories["cat03"]),
    "cdTime": ",".join(categories["time"]),
}

response = requests.get(
    "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData",
    params=params,
    timeout=60,
) # responseはjson形式のデータ
# requests.get: e-Stat APIへGETリクエストを送る
# params=params：先ほど作った取得条件を渡す
# timeout=60：60秒応答がなければ停止する
response.raise_for_status() 
# raise_for_status()：HTTPエラーなら、その時点でエラーにするrequestsのメソッド
payload = response.json() # .json()でPythonの辞書型に変換

result = payload.get("GET_STATS_DATA", {}).get("RESULT", {}) 
# GET_STATS_DATA があれば、その中身を返す、なければ空の辞書 {} を返す
# .get()だとキーがなくてもエラーにならず、空の値で返せる
status = result.get("@status") or result.get("STATUS")
# e-Stat APIのステータス表記には、@status または STATUS が使われる可能性があるため、どちらでも対応可能なコード
if str(status) not in {"0", "None"}:
    raise RuntimeError(f"e-Stat APIエラー: {result}")
# 0,Noneは正常なときの値
# raise RuntimeError(...)：意図的にエラーを発生させ、処理を止める
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
# APIからきたjsonを加工せず保存
print(f"データを保存しました: {OUTPUT_PATH}")
# print(f"リクエストしたURL: {response.url}")
print("取得元: e-Stat API getStatsData")