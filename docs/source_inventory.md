### 統計表名
> 法人企業統計調査 時系列データ

### 統計表ID
> 0003060791

### 更新頻度
> 1年

### 対象期間
> 1960年度～2025年度

### 単位
> 項目ごとに異なる。

### 業種・資本金規模の分類
- 全規模
- 10億円以上
- 1億円以上 - 10億円未満
- 5千万円以上 - 1億円未満
- 1千万円以上 - 1億円未満
- 1千万円以上 - 5千万円未満
- 1千万円未満
- 1億円以上
- 1億円未満
- 2千万円以上 - 5千万円未満
- 1千万円以上 - 2千万円未満
- 5百万円以上 - 1千万円未満
- 3百万円以上 - 5百万円未満
- 2百万円以上 - 5百万円未満
- 2百万円以上 - 3百万円未満
- 2百万円未満

### 利用上の注意点


# データソース一覧

## 法人企業統計調査 時系列データ

- 統計表ID: `0003060791`
- 表題: 金融業、保険業以外の業種（原数値）
- 取得方法: e-Stat API `getMetaInfo` / `getStatsData`
- 更新頻度: 年次データは年1回公表
- 単位: 項目ごとに確認して記録する

## 初期対象のコード

| 分類 | 名称 | コード |
|---|---|---|
| 業種 | 製造業 | `108` |
| 業種 | 卸売業・小売業（集約） | `129` |
| 業種 | 情報通信業 | `142` |
| 規模 | 1千万円未満 | `16` |
| 規模 | 1億円以上 - 10億円未満 | `24` |
| 規模 | 10億円以上 | `25` |
| 調査項目 | 売上高（当期末） | `045` |
| 調査項目 | 経常利益（当期末） | `051` |
| 調査項目 | 資産合計（当期末） | `022` |
| 調査項目 | 負債（当期末） | `224` |
| 調査項目 | 純資産（当期末） | `157` |
| 調査項目 | 従業員給与（当期末） | `066` |
| 調査項目 | 実物投資（当期末資金需給） | `085` |


## 作成したファイルの対応表
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