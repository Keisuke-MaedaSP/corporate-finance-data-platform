import os

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = os.environ["BIGQUERY_LOCATION"]

client = bigquery.Client(project=project_id)

datasets = {
    "corporate_finance_raw": "e-Stat APIから取得した加工前の法人企業統計データ",
    "corporate_finance_staging": "標準化・品質検証済みの法人企業統計データ",
    "corporate_finance_mart": "業種・資本金規模別の財務KPIデータマート",
}

for dataset_id, description in datasets.items():
    dataset_ref = f"{project_id}.{dataset_id}"

    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = location
    dataset.description = description

    created_dataset = client.create_dataset(dataset, exists_ok=True)

    print(
        f"データセットを確認しました: "
        f"{created_dataset.project}.{created_dataset.dataset_id} "
        f"(location={created_dataset.location})"
    )