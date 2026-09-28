import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["BIGQUERY_LOCATION"]

sql_path = Path("sql/analysis/compare_2016_2025.sql")

sql = sql_path.read_text(encoding="utf-8")
sql = sql.replace("{{PROJECT_ID}}", project_id)

client = bigquery.Client(project=project_id)

query_job = client.query(sql, location=location)
rows = list(query_job.result())

print(f"比較対象: {len(rows)}件\n")

for row in rows:
    print(dict(row))