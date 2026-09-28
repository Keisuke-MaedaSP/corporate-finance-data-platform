import json
import os
from pathlib import Path
# json：JSON形式の設定・APIレスポンスを扱う
# os：環境変数を読む
# Path：ファイルパスを安全に扱う
# requests：Web APIにアクセスする
# load_dotenv：.env の設定値を読み込む
import requests
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path("config/selection.json")
OUTPUT_PATH = Path("data/raw/corporate_finance_2016_2025.json")

with CONFIG_PATH.open(encoding="utf-8") as f:
    config = json.load(f)

categories = config["categories"]

params = {
    "appId": os.environ["ESTAT_APP_ID"],
    "statsDataId": config["stats_data_id"],
    "cdCat01": ",".join(categories["cat01"]),
    "cdCat02": ",".join(categories["cat02"]),
    "cdCat03": ",".join(categories["cat03"]),
    "cdTime": ",".join(categories["time"]),
}

response = requests.get(
    "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData",
    params=params,
    timeout=60,
)
response.raise_for_status()

payload = response.json()

result = payload.get("GET_STATS_DATA", {}).get("RESULT", {})
status = result.get("@status") or result.get("STATUS")

if str(status) not in {"0", "None"}:
    raise RuntimeError(f"e-Stat APIエラー: {result}")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"データを保存しました: {OUTPUT_PATH}")
# print(f"リクエストしたURL: {response.url}")
print("取得元: e-Stat API getStatsData")