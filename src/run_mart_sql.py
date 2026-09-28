import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["BIGQUERY_LOCATION"]

sql_path = Path("sql/marts/create_financial_kpis.sql")

sql = sql_path.read_text(encoding="utf-8")
sql = sql.replace("{{PROJECT_ID}}", project_id)

client = bigquery.Client(project=project_id)

query_job = client.query(sql, location=location)
query_job.result()

table_id = f"{project_id}.corporate_finance_mart.financial_kpis"
table = client.get_table(table_id)

print(f"KPIマートを作成しました: {table_id}")
print(f"総行数: {table.num_rows}件")