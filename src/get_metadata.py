import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

app_id = os.environ["ESTAT_APP_ID"]
stats_data_id = "0003060791"

response = requests.get(
    "https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo",
    params={
        "appId": app_id,
        "statsDataId": stats_data_id,
    },
    timeout=30,
)
response.raise_for_status()

payload = response.json()

output_path = Path("data/raw/metadata_0003060791.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"メタ情報を保存しました: {output_path}")