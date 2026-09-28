import csv
import json
from pathlib import Path


def as_list(value):
    return value if isinstance(value, list) else [value]


input_path = Path("data/raw/metadata_0003060791.json")
output_path = Path("data/reference/metadata_codes_0003060791.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with input_path.open(encoding="utf-8") as f:
    payload = json.load(f)

class_objects = payload["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]

rows = []

for class_object in as_list(class_objects):
    class_id = class_object.get("@id")
    class_name = class_object.get("@name")

    for item in as_list(class_object.get("CLASS", [])):
        rows.append(
            {
                "class_id": class_id,
                "class_name": class_name,
                "code": item.get("@code"),
                "name": item.get("@name"),
                "level": item.get("@level"),
                "unit": item.get("@unit"),
            }
        )

with output_path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"{len(rows)}件のコードを保存しました: {output_path}")