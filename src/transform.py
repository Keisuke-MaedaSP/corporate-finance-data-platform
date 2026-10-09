import json
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/corporate_finance_2016_2025.json")
METADATA_PATH = Path("data/reference/metadata_codes_0003060791.csv")
OUTPUT_PATH = Path("data/processed/corporate_finance_long.csv")

with RAW_PATH.open(encoding="utf-8") as f:
    payload = json.load(f) # json.load(f) は、JSONファイルをPythonの辞書へ変換
# with を使うと、処理終了時にファイルを自動で閉じる
# payload は、APIレスポンス全体を持つ辞書

values = payload["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
# 辞書を階層順にたどり、統計レコードが格納されている VALUE を取り出す

if isinstance(values, dict):
    values = [values]
# isinstance(values, dict) は、values が辞書型かどうかを確認
# 通常、複数件のデータがあるとき、values はリストだが、e-Stat APIでは取得結果が1件だけの場合、
# リストではなく辞書だけが返る場合がある。
# そのままでは、複数件を前提にした後続の処理と形が異なってしまうため、辞書をリストで包む
# このコードによって、データが1件でも複数件でも、常に「レコードのリスト」として扱えるように形を統一する。

df = pd.DataFrame(values).rename(
    columns={
        "@cat01": "item_code",# 財務項目コード
        "@cat02": "industry_code",# 業種コード
        "@cat03": "capital_size_code",# 資本金規模コード
        "@time": "time_code",# 年度コード
        "@unit": "unit",
        "$": "amount",# 金額
    }
)

metadata = pd.read_csv(METADATA_PATH, dtype=str)
# dtype=strによって文字列として認識
# なぜ文字列とするか？⇒例えば045を数値として読むと45になり、先頭のゼロが消える。
# すると、APIデータの 045 と正しく結合できなくなってしまう

def create_name_mapping(class_id: str) -> dict[str, str]:
    target = metadata.loc[
        metadata["class_id"] == class_id,# 引数のclass_idと同じclass_id
        ["code", "name"],
    ].drop_duplicates()

    return dict(zip(target["code"], target["name"]))
# zip()は複数のイテラブル（リストやタプルなど）の要素を同じインデックス（順番）
# ごとにまとめてペアを作る組み込み関数

item_mapping = create_name_mapping("cat01")
industry_mapping = create_name_mapping("cat02")
capital_size_mapping = create_name_mapping("cat03")
time_mapping = create_name_mapping("time")

df["item_name"] = df["item_code"].map(item_mapping) 
#cat01のcodeと一致するnameを新しい列item_nameとして作る
df["industry_name"] = df["industry_code"].map(industry_mapping)
df["capital_size_name"] = df["capital_size_code"].map(capital_size_mapping)
df["fiscal_year"] = df["time_code"].str[:4].astype(int) # 例えば20250などを2025に変換
df["amount"] = pd.to_numeric(df["amount"], errors="raise") 
# 文字列になっている金額を数値に変換、エラーがあればエラー出て停止

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
) #dfをoutput_columnsの列に絞って列の順番を並び替え

key_columns = [
    "time_code",
    "industry_code",
    "capital_size_code",
    "item_code",
]

assert len(df) == 540, f"想定外のレコード数: {len(df)}"
# 540件でデータ取得漏れがないことを確認、あれば処理を止める
assert df[key_columns].duplicated().sum() == 0, "主キーの重複があります"
# 重複なし：同じ年度・業種・規模・項目が二重にないことを確認、あれば処理を止める
assert df[["item_name", "industry_name", "capital_size_name"]].isna().sum().sum() == 0, (
    "コードから名称へ変換できない値があります"
) # 名称欠損なし：コード変換に失敗していないことを確認、あれば処理を止める

negative_records = df[df["amount"] < 0]
if not negative_records.empty:
    print("\n負の値を含む財務項目:")
    print(
        negative_records[["item_code", "item_name"]]
        .drop_duplicates()
        .to_string(index=False)
    ) # 金額が負の値になっているものを確認

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

print(f"変換完了: {OUTPUT_PATH}")
print(f"レコード数: {len(df)}件")
print("\n財務項目:")
print(df[["item_code", "item_name"]].drop_duplicates().to_string(index=False))