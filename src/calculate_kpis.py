from pathlib import Path

import pandas as pd

INPUT_PATH = Path("data/processed/corporate_finance_long.csv")
OUTPUT_PATH = Path("data/mart/financial_kpis.csv")

df = pd.read_csv(
    INPUT_PATH,
    dtype={
        "time_code": str,
        "industry_code": str,
        "capital_size_code": str,
        "item_code": str,
    },
)

index_columns = [
    "fiscal_year",
    "industry_code",
    "industry_name",
    "capital_size_code",
    "capital_size_name",
]

wide_df = (
    df.pivot(
        index=index_columns,
        columns="item_code",
        values="amount",
    )
    .reset_index()
    .rename(
        columns={
            "022": "total_assets",
            "045": "net_sales",
            "051": "ordinary_income",
            "066": "employee_salary",
            "085": "real_investment",
            "157": "net_assets",
        }
    )
)

required_columns = [
    "total_assets",
    "net_sales",
    "ordinary_income",
    "employee_salary",
    "real_investment",
    "net_assets",
]

assert wide_df[required_columns].isna().sum().sum() == 0, "KPI計算に必要な値が不足しています"
assert (wide_df["net_sales"] != 0).all(), "売上高が0の行があるため比率を計算できません"
assert (wide_df["total_assets"] != 0).all(), "資産合計が0の行があるため比率を計算できません"

wide_df["ordinary_income_margin_pct"] = (
    wide_df["ordinary_income"] / wide_df["net_sales"] * 100
)

wide_df["net_assets_ratio_pct"] = (
    wide_df["net_assets"] / wide_df["total_assets"] * 100
)

wide_df["personnel_cost_ratio_pct"] = (
    wide_df["employee_salary"] / wide_df["net_sales"] * 100
)

wide_df["real_investment_ratio_pct"] = (
    wide_df["real_investment"] / wide_df["net_sales"] * 100
)

wide_df["ordinary_income_to_assets_pct"] = (
    wide_df["ordinary_income"] / wide_df["total_assets"] * 100
)

wide_df = wide_df.sort_values(
    ["fiscal_year", "industry_code", "capital_size_code"]
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
wide_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

print(f"KPIマートを作成しました: {OUTPUT_PATH}")
print(f"レコード数: {len(wide_df)}件")
print("\nKPI平均値（%）:")
print(
    wide_df[
        [
            "ordinary_income_margin_pct",
            "net_assets_ratio_pct",
            "personnel_cost_ratio_pct",
            "real_investment_ratio_pct",
            "ordinary_income_to_assets_pct",
        ]
    ]
    .mean()
    .round(2)
)