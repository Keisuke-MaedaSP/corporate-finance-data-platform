import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

RAW_PATH = Path("data/raw/corporate_finance_2016_2025.json")
CONFIG_PATH = Path("config/selection.json")

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
app_id = os.environ["ESTAT_APP_ID"]

with RAW_PATH.open(encoding="utf-8") as f:
    payload_text = f.read()

with CONFIG_PATH.open(encoding="utf-8") as f:
    config = json.load(f)

payload = json.loads(payload_text)

values = payload["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
if isinstance(values, dict):
    values = [values]

# 万が一レスポンス内にappIdが含まれていても、BigQueryには保存しない
redacted_payload_text = payload_text.replace(app_id, "[REDACTED]")

client = bigquery.Client(project=project_id)

table_id = f"{project_id}.corporate_finance_raw.estat_api_responses"

schema = [
    bigquery.SchemaField("extraction_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("stats_data_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("record_count", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("response_json", "STRING", mode="REQUIRED"),
]

table = bigquery.Table(table_id, schema=schema)
table.description = "e-Stat APIから取得した法人企業統計調査の加工前レスポンス"
table.time_partitioning = bigquery.TimePartitioning(field="ingested_at")
table.clustering_fields = ["stats_data_id"]

client.create_table(table, exists_ok=True)

row = {
    "extraction_id": str(uuid.uuid4()),
    "ingested_at": datetime.now(timezone.utc).isoformat(),
    "stats_data_id": config["stats_data_id"],
    "source_name": "e-Stat API getStatsData",
    "record_count": len(values),
    "response_json": redacted_payload_text,
}

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
)

load_job = client.load_table_from_json(
    [row],
    table_id,
    job_config=job_config,
)
load_job.result()

loaded_table = client.get_table(table_id)

print(f"rawテーブルへ保存しました: {table_id}")
print(f"今回の取得レコード数: {len(values)}件")
print(f"rawテーブルの総行数: {loaded_table.num_rows}件")