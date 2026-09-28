import json
from pathlib import Path

input_path = Path("data/raw/corporate_finance_2016_2025.json")

with input_path.open(encoding="utf-8") as f:
    payload = json.load(f)

api_response = payload["GET_STATS_DATA"]

print("GET_STATS_DATA直下のキー:")
print(list(api_response.keys()))

statistical_data = api_response["STATISTICAL_DATA"]
data_inf = statistical_data["DATA_INF"]
values = data_inf["VALUE"]

if isinstance(values, dict):
    values = [values]

print(f"\n取得レコード数: {len(values)}件")
print("\n先頭3レコード:")

for value in values[:3]:
    print(value)
    

from collections import Counter

for dimension in ["cat01", "cat02", "cat03", "time"]:
    counter = Counter(row[f"@{dimension}"] for row in values)

    print(f"\n{dimension}: {len(counter)}種類")
    for code, count in sorted(counter.items()):
        print(f"  {code}: {count}件")