import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

input_path = Path("data/reference/metadata_codes_0003060791.csv")
table_id = f"{project_id}.corporate_finance_staging.estat_metadata_codes"

with input_path.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    for key, value in row.items():
        row[key] = value if value else None

schema = [
    bigquery.SchemaField("class_id", "STRING"),
    bigquery.SchemaField("class_name", "STRING"),
    bigquery.SchemaField("code", "STRING"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("level", "STRING"),
    bigquery.SchemaField("unit", "STRING"),
]

client = bigquery.Client(project=project_id)

table = bigquery.Table(table_id, schema=schema)
table.description = "e-Stat法人企業統計調査の分類コード・名称対応表"
client.create_table(table, exists_ok=True)

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

load_job = client.load_table_from_json(
    rows,
    table_id,
    job_config=job_config,
)
load_job.result()

table = client.get_table(table_id)

print(f"メタデータ表を保存しました: {table_id}")
print(f"総行数: {table.num_rows}件")