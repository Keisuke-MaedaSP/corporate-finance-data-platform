# 法人企業統計を用いた財務KPIデータ基盤

e-Statの「法人企業統計調査 時系列データ」を取得・整形し、BigQuery上で財務KPIを分析可能な形にしたデータエンジニアリング・ポートフォリオです。

税務会計の実務経験を生かし、財務指標の定義、異常値の扱い、データ品質チェックを意識して設計しました。

## 1. プロジェクト概要

法人企業統計調査の集計データを対象に、以下のデータパイプラインを構築しました。

```text
e-Stat API
  ↓
Raw層：APIレスポンスをJSONのまま保存
  ↓
Staging層：財務項目・業種・資本金規模・年度を縦持ちで整形
  ↓
Mart層：財務KPIを算出し、分析用テーブルを作成
  ↓
Jupyter Notebook：可視化・分析
```

## 2. 分析対象

- データソース: e-Stat 法人企業統計調査 時系列データ
- 対象年度: 2016〜2025年度
- 対象業種: 製造業、卸売業・小売業、情報通信業
- 資本金規模:
  - 1千万円未満
  - 1億円以上 - 10億円未満
  - 10億円以上

>対象とした財務項目は以下の6項目です。

- 資産合計
- 売上高
- 経常利益
- 従業員給与
- 実物投資
- 純資産

## 3. データ基盤の設計

BigQueryでは、用途ごとに3層のデータセットを作成しています。

| 層 | データセット | 役割 |
| --- | --- | --- |
| Raw | `corporate_finance_raw` | e-Stat APIレスポンスをJSON形式で保存 |
| Staging | `corporate_finance_staging` | JSONを展開し、分析可能な縦持ちデータへ整形 |
| Mart | `corporate_finance_mart` | 財務KPIを計算した分析用テーブル |

分析用マートの粒度は、`年度 × 業種 × 資本金規模` です。

## 4. 算出したKPI

| KPI | 計算式 | 意味 |
| --- | --- | --- |
| 経常利益率 | 経常利益 ÷ 売上高 × 100 | 本業・財務活動を含む収益性 |
| 純資産比率 | 純資産 ÷ 資産合計 × 100 | 資産に占める純資産の割合 |
| 人件費率 | 従業員給与 ÷ 売上高 × 100 | 売上に対する人件費の割合 |
| 実物投資比率 | 実物投資 ÷ 売上高 × 100 | 売上に対する設備等への投資規模 |
| 総資産経常利益率 | 経常利益 ÷ 資産合計 × 100 | 資産を用いた収益性 |

> 「純資産比率」は自己資本比率と完全に同義ではないため、本プロジェクトでは公表データの項目名に合わせて表記しています。

## 5. データ品質チェック

以下のチェックをPythonおよびBigQuery SQLで実装しました。

- 主キー（年度・業種・資本金規模・財務項目）の重複がないこと
- ディメンション項目・金額に欠損がないこと
- 全年度・全業種・全資本金規模の組み合わせが取得できていること
- 資産合計、売上高、従業員給与に不正な負数がないこと
- KPIマートの粒度が一意であること

経常利益・純資産・実物投資は会計上負の数になり得るため、一律に異常値として除外していません。

## 6. 分析結果

### 業種・資本金規模別の経常利益率推移

![業種・資本金規模別の経常利益率推移](docs/images/ordinary_income_margin_trends.png)

> 情報通信業では資本金規模別の収益性格差が大きく見られました。10億円以上の区分は高い経常利益率を維持する一方、1千万円未満の区分では2020〜2024年度に赤字となる年度があります。

### 売上成長率と純資産比率変化

![売上成長率と純資産比率変化](docs/images/sales_growth_vs_net_assets_change.png)

> 2016年度から2025年度にかけて、売上成長率と純資産比率の変化を比較しました。
> 
>- 製造業は、対象の全資本金規模で売上成長と純資産比率の改善が両立しています。
>- 情報通信業では、売上が伸びた区分でも純資産比率が低下したケースが見られます。
>- 情報通信業・1千万円未満は、純資産比率が約20ポイント低下しており、財務安全性の観点で注視すべき区分です。
>- 卸売業・小売業・10億円以上は、売上が減少した一方で純資産比率は改善しています。
> 
> これらは集計統計に基づく記述的な分析であり、因果関係を示すものではありません。

## 7. 使用技術

- Python 3.12
- uv
- pandas
- requests
- python-dotenv
- JupyterLab
- matplotlib
- BigQuery
- Google Cloud SDK
- SQL
- e-Stat API

## 8. 実行方法

### セットアップ

```bash
uv sync
```

`.env` を作成し、以下を設定します。

```env
ESTAT_APP_ID=取得したe-StatアプリケーションID
GOOGLE_CLOUD_PROJECT=Google CloudプロジェクトID
BIGQUERY_LOCATION=asia-northeast1
```

### データ取得からマート作成まで

```bash
uv run python src/get_metadata.py
uv run python src/export_metadata_codes.py
uv run python src/extract.py
uv run python src/transform.py
uv run python src/quality_checks.py

uv run python src/setup_bigquery.py
uv run python src/load_raw_to_bigquery.py
uv run python src/run_staging_sql.py
uv run python src/run_quality_checks_bigquery.py
uv run python src/load_metadata_to_bigquery.py
uv run python src/run_dimensions_sql.py
uv run python src/run_mart_sql.py
uv run python src/run_mart_quality_checks.py
```

### 分析・可視化

```bash
uv run python src/run_analysis.py
uv run jupyter lab
```

Notebook:

```text
notebooks/01_financial_kpi_analysis.ipynb
```
## 9. 作成したファイルの対応表
### ① ローカル環境での 取得・整形・確認・KPI試算

| 順番 | ファイル | 担当していること | 入力 | 出力 |
| --- | --- | --- | --- | --- |
| 1 | `config/selection.json` | 分析対象の条件を定義する | 業種・規模・年度・財務項目のコード | API取得条件 |
| 2 | `src/get_metadata.py` | e-Statのメタデータを取得する | e-Stat API | `data/raw/metadata_0003060791.json` |
| 3 | `src/export_metadata_codes.py` | コードと名称の対応表を作る | メタデータJSON | `data/reference/metadata_codes_0003060791.csv` |
| 4 | `src/extract.py` | 指定条件で法人企業統計を取得する | `selection.json`、e-Stat API | `data/raw/corporate_finance_2016_2025.json` |
| 5 | `src/inspect_raw_data.py` | API取得結果の件数・コードを確認する | Raw JSON | 取得結果の確認表示 |
| 6 | `src/transform.py` | API JSONを分析しやすい縦持ちデータに変換する | Raw JSON、コード対応表 | `data/processed/corporate_finance_long.csv` |
| 7 | `src/quality_checks.py` | ローカルデータの品質を検証する | 整形済みCSV | 品質チェック結果 |
| 8 | `src/calculate_kpis.py` | Python上でKPIを試算する | 整形済みCSV | `data/mart/financial_kpis.csv` |
### ② BigQuery上で同じデータを「再利用できるデータ基盤」として作成

| 順番 | ファイル | 担当していること | 作成・利用するもの |
| --- | --- | --- | --- |
| 9 | `src/setup_bigquery.py` | BigQueryのデータセットを準備する | Raw / Staging / Mart |
| 10 | `src/load_raw_to_bigquery.py` | APIレスポンスJSONをRaw層へ保存する | `corporate_finance_raw.estat_api_responses` |
| 11 | `sql/staging/create_financial_values.sql` | Raw JSONを展開して縦持ちに整形するSQL | `corporate_finance_staging.financial_values` |
| 12 | `src/run_staging_sql.py` | Staging作成SQLを実行する | `financial_values` |
| 13 | `sql/quality/check_financial_values.sql` | Staging層の品質を検査するSQL | 件数・欠損・重複・組合せ |
| 14 | `src/run_quality_checks_bigquery.py` | Staging品質チェックSQLを実行する | 品質チェック結果 |
| 15 | `src/load_metadata_to_bigquery.py` | コード対応表をBigQueryへ保存する | `estat_metadata_codes` |
| 16 | `sql/staging/create_dimensions.sql` | 業種・規模・財務項目のマスタを作るSQL | 各ディメンション表 |
| 17 | `src/run_dimensions_sql.py` | ディメンション作成SQLを実行する | `dim_industries` など |
| 18 | `sql/marts/create_financial_kpis.sql` | KPIを計算する分析用マートを作るSQL | `corporate_finance_mart.financial_kpis` |
| 19 | `src/run_mart_sql.py` | KPIマート作成SQLを実行する | `financial_kpis` |
| 20 | `sql/quality/check_financial_kpis.sql` | KPIマートの品質を検証するSQL | KPIの欠損・重複 |
| 21 | `src/run_mart_quality_checks.py` | KPI品質チェックSQLを実行する | 品質チェック結果 |

### ③ 分析・可視化

| ファイル | 担当していること |
| --- | --- |
| `sql/analysis/compare_2016_2025.sql` | 2016年度と2025年度の売上成長率・純資産比率変化を比較する |
| `src/run_analysis.py` | 比較SQLを実行し、結果を確認する |
| `notebooks/01_financial_kpi_analysis.ipynb` | BigQueryからKPIマートを読み込み、グラフと分析結果を作る |
| `docs/images/ordinary_income_margin_trends.png` | 業種・資本金規模別の経常利益率推移 |
| `docs/images/sales_growth_vs_net_assets_change.png` | 売上成長率と純資産比率変化の散布図 |
| `README.md` | 設計・技術・分析結果を第三者に伝える説明書 |


## 10. 今後の改善案

- e-Stat APIからの定期取得・差分更新
- BigQuery上のテーブル更新履歴の管理
- dbtによるSQLモデル・テスト管理
- Looker Studioによるダッシュボード化
- 業種・資本金規模・年度の対象範囲拡張

## 11. データ出典

- [e-Stat 法人企業統計調査 時系列データ](https://www.e-stat.go.jp/dbview?sid=0003060791)
- [e-Stat API](https://www.e-stat.go.jp/api/)

