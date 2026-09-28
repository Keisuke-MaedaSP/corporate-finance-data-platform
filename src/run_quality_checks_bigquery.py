import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["BIGQUERY_LOCATION"]

sql_path = Path("sql/quality/check_financial_values.sql")

sql = sql_path.read_text(encoding="utf-8")
sql = sql.replace("{{PROJECT_ID}}", project_id)

client = bigquery.Client(project=project_id)

query_job = client.query(sql, location=location)
row = dict(next(iter(query_job.result())))

expected_values = {
    "record_count": 540,
    "unique_item_count": 6,
    "unique_industry_count": 3,
    "unique_capital_size_count": 3,
    "unique_fiscal_year_count": 10,
    "null_dimension_count": 0,
    "null_amount_count": 0,
    "invalid_negative_count": 0,
    "duplicate_key_count": 0,
    "incomplete_combination_count": 0,
}

for metric, expected in expected_values.items():
    actual = row[metric]
    assert actual == expected, (
        f"品質チェック失敗: {metric} "
        f"(期待値: {expected}, 実際: {actual})"
    )

print("BigQuery上の品質チェックに合格しました。")

for metric, value in row.items():
    print(f"{metric}: {value}")