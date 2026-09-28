import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["BIGQUERY_LOCATION"]

sql_path = Path("sql/staging/create_dimensions.sql")

sql = sql_path.read_text(encoding="utf-8")
sql = sql.replace("{{PROJECT_ID}}", project_id)

client = bigquery.Client(project=project_id)

query_job = client.query(sql, location=location)
query_job.result()

dimension_tables = [
    "dim_financial_items",
    "dim_industries",
    "dim_capital_sizes",
]

for table_name in dimension_tables:
    table_id = f"{project_id}.corporate_finance_staging.{table_name}"
    table = client.get_table(table_id)
    print(f"{table_name}: {table.num_rows}件")