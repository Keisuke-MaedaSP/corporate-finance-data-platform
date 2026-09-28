import json
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/corporate_finance_2016_2025.json")
METADATA_PATH = Path("data/reference/metadata_codes_0003060791.csv")
OUTPUT_PATH = Path("data/processed/corporate_finance_long.csv")

with RAW_PATH.open(encoding="utf-8") as f:
    payload = json.load(f)

values = payload["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]

if isinstance(values, dict):
    values = [values]

df = pd.DataFrame(values).rename(
    columns={
        "@cat01": "item_code",
        "@cat02": "industry_code",
        "@cat03": "capital_size_code",
        "@time": "time_code",
        "@unit": "unit",
        "$": "amount",
    }
)

metadata = pd.read_csv(METADATA_PATH, dtype=str)


def create_name_mapping(class_id: str) -> dict[str, str]:
    target = metadata.loc[
        metadata["class_id"] == class_id,
        ["code", "name"],
    ].drop_duplicates()

    return dict(zip(target["code"], target["name"]))


item_mapping = create_name_mapping("cat01")
industry_mapping = create_name_mapping("cat02")
capital_size_mapping = create_name_mapping("cat03")
time_mapping = create_name_mapping("time")

df["item_name"] = df["item_code"].map(item_mapping)
df["industry_name"] = df["industry_code"].map(industry_mapping)
df["capital_size_name"] = df["capital_size_code"].map(capital_size_mapping)
df["fiscal_year"] = df["time_code"].str[:4].astype(int)
df["amount"] = pd.to_numeric(df["amount"], errors="raise")

output_columns = [
    "fiscal_year",
    "time_code",
    "industry_code",
    "industry_name",
    "capital_size_code",
    "capital_size_name",
    "item_code",
    "item_name",
    "amount",
    "unit",
]

df = df[output_columns].sort_values(
    ["fiscal_year", "industry_code", "capital_size_code", "item_code"]
)

key_columns = [
    "time_code",
    "industry_code",
    "capital_size_code",
    "item_code",
]

assert len(df) == 540, f"想定外のレコード数: {len(df)}"
assert df[key_columns].duplicated().sum() == 0, "主キーの重複があります"
assert df[["item_name", "industry_name", "capital_size_name"]].isna().sum().sum() == 0, (
    "コードから名称へ変換できない値があります"
)
negative_records = df[df["amount"] < 0]

if not negative_records.empty:
    print("\n負の値を含む財務項目:")
    print(
        negative_records[["item_code", "item_name"]]
        .drop_duplicates()
        .to_string(index=False)
    )

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

print(f"変換完了: {OUTPUT_PATH}")
print(f"レコード数: {len(df)}件")
print("\n財務項目:")
print(df[["item_code", "item_name"]].drop_duplicates().to_string(index=False))