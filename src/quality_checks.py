from pathlib import Path

import pandas as pd

INPUT_PATH = Path("data/processed/corporate_finance_long.csv")

df = pd.read_csv(
    INPUT_PATH,
    dtype={
        "time_code": str,
        "industry_code": str,
        "capital_size_code": str,
        "item_code": str,
    },
)

expected_item_codes = {"022", "045", "051", "066", "085", "157"}
expected_industry_codes = {"108", "129", "142"}
expected_capital_size_codes = {"16", "24", "25"}
expected_years = set(range(2016, 2026))

key_columns = [
    "time_code",
    "industry_code",
    "capital_size_code",
    "item_code",
]

# 1. レコード数
assert len(df) == 540, f"レコード数が想定外です: {len(df)}"

# 2. 主キーの一意性
assert df.duplicated(key_columns).sum() == 0, "主キーの重複があります"

# 3. 対象コードの完全性
assert set(df["item_code"]) == expected_item_codes, "財務項目コードに不足または想定外があります"
assert set(df["industry_code"]) == expected_industry_codes, "業種コードに不足または想定外があります"
assert set(df["capital_size_code"]) == expected_capital_size_codes, "資本金規模コードに不足または想定外があります"
assert set(df["fiscal_year"]) == expected_years, "年度に不足または想定外があります"

# 4. 各「年度 × 業種 × 規模」に、6財務項目がそろうこと
group_counts = df.groupby(
    ["fiscal_year", "industry_code", "capital_size_code"]
)["item_code"].nunique()

assert (group_counts == 6).all(), "財務項目が不足している組み合わせがあります"

# 5. 名称・単位・数値の欠損
required_columns = [
    "industry_name",
    "capital_size_name",
    "item_name",
    "amount",
    "unit",
]

assert df[required_columns].isna().sum().sum() == 0, "必須列に欠損があります"
assert set(df["unit"]) == {"百万円"}, "単位が想定と異なります"

# 6. 負値を許容しない項目の確認
non_negative_item_codes = {"022", "045", "066"}

invalid_negative = df[
    df["item_code"].isin(non_negative_item_codes) & (df["amount"] < 0)
]

assert invalid_negative.empty, "資産合計・売上高・従業員給与に負値があります"

print("品質チェックに合格しました。")
print(f"レコード数: {len(df)}件")
print(f"年度: {df['fiscal_year'].min()}〜{df['fiscal_year'].max()}年度")
print(f"業種数: {df['industry_code'].nunique()}件")
print(f"資本金規模数: {df['capital_size_code'].nunique()}件")
print(f"財務項目数: {df['item_code'].nunique()}件")