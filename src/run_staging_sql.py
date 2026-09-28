import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["BIGQUERY_LOCATION"]

sql_path = Path("sql/staging/create_financial_values.sql")

sql = sql_path.read_text(encoding="utf-8")
sql = sql.replace("{{PROJECT_ID}}", project_id)

client = bigquery.Client(project=project_id)

query_job = client.query(sql, location=location)
query_job.result()

table_id = f"{project_id}.corporate_finance_staging.financial_values"
table = client.get_table(table_id)

print(f"stagingテーブルを作成しました: {table_id}")
print(f"総行数: {table.num_rows}件")