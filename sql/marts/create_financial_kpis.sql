-- industry_nameとcapital_size_nameを持つ読みやすいKPIマートに更新
CREATE OR REPLACE TABLE --既存テーブルがあれば置き換え、最新版として作り直す
  `{{PROJECT_ID}}.corporate_finance_mart.financial_kpis`
CLUSTER BY industry_code, capital_size_code 
--CLUSTER BYはテーブルを保存するときのデータの物理的な整理方法を指定する
AS
WITH pivoted_values AS (
  SELECT
    fiscal_year,
    industry_code,
    capital_size_code,

    MAX(IF(item_code = "022", amount_million_yen, NULL)) AS total_assets_million_yen,
    --今回のデータでは、年度、業種、資本金規模でグループバイした場合、１つの財務項目コード
    --に対して１つの値しか無くなるため、MAXはその財務項目コードの１つの値の取り出しを行う
    --手段となっている
    MAX(IF(item_code = "045", amount_million_yen, NULL)) AS net_sales_million_yen,
    MAX(IF(item_code = "051", amount_million_yen, NULL)) AS ordinary_income_million_yen,
    MAX(IF(item_code = "066", amount_million_yen, NULL)) AS employee_salary_million_yen,
    MAX(IF(item_code = "085", amount_million_yen, NULL)) AS real_investment_million_yen,
    MAX(IF(item_code = "157", amount_million_yen, NULL)) AS net_assets_million_yen

  FROM
    `{{PROJECT_ID}}.corporate_finance_staging.financial_values`
  GROUP BY
    fiscal_year,
    industry_code,
    capital_size_code
)

SELECT
  p.fiscal_year,
  p.industry_code,
  i.industry_name,
  p.capital_size_code,
  c.capital_size_name,

  p.total_assets_million_yen,
  p.net_sales_million_yen, --売上高
  p.ordinary_income_million_yen, --経常利益
  p.employee_salary_million_yen,
  p.real_investment_million_yen,
  p.net_assets_million_yen,

  SAFE_DIVIDE(p.ordinary_income_million_yen, p.net_sales_million_yen) * 100
    AS ordinary_income_margin_pct,
  --SAFE_DIVIDE() は、通常の"/"の代わりに安全に割り算するBigQuery関数、分母が0になる場合
  --にNULLを返す。
  SAFE_DIVIDE(p.net_assets_million_yen, p.total_assets_million_yen) * 100
    AS net_assets_ratio_pct,

  SAFE_DIVIDE(p.employee_salary_million_yen, p.net_sales_million_yen) * 100
    AS personnel_cost_ratio_pct,

  SAFE_DIVIDE(p.real_investment_million_yen, p.net_sales_million_yen) * 100
    AS real_investment_ratio_pct,

  SAFE_DIVIDE(p.ordinary_income_million_yen, p.total_assets_million_yen) * 100
    AS ordinary_income_to_ending_assets_pct

FROM
  pivoted_values AS p
LEFT JOIN
  `{{PROJECT_ID}}.corporate_finance_staging.dim_industries` AS i
ON --dim_industriesはBig Query上に予め作ったテーブル
  p.industry_code = i.industry_code
LEFT JOIN
  `{{PROJECT_ID}}.corporate_finance_staging.dim_capital_sizes` AS c
ON --dim_capital_sizesはBig Query上予めに作ったテーブル
  p.capital_size_code = c.capital_size_code;


/* 置き換える前のSQLクエリ
CREATE OR REPLACE TABLE
  `{{PROJECT_ID}}.corporate_finance_mart.financial_kpis`
CLUSTER BY industry_code, capital_size_code
AS
WITH pivoted_values AS (
  SELECT
    fiscal_year,
    industry_code,
    capital_size_code,

    MAX(IF(item_code = "022", amount_million_yen, NULL)) AS total_assets_million_yen,
    MAX(IF(item_code = "045", amount_million_yen, NULL)) AS net_sales_million_yen,
    MAX(IF(item_code = "051", amount_million_yen, NULL)) AS ordinary_income_million_yen,
    MAX(IF(item_code = "066", amount_million_yen, NULL)) AS employee_salary_million_yen,
    MAX(IF(item_code = "085", amount_million_yen, NULL)) AS real_investment_million_yen,
    MAX(IF(item_code = "157", amount_million_yen, NULL)) AS net_assets_million_yen

  FROM
    `{{PROJECT_ID}}.corporate_finance_staging.financial_values`
  GROUP BY
    fiscal_year,
    industry_code,
    capital_size_code
)

SELECT
  fiscal_year,
  industry_code,
  capital_size_code,

  total_assets_million_yen,
  net_sales_million_yen,
  ordinary_income_million_yen,
  employee_salary_million_yen,
  real_investment_million_yen,
  net_assets_million_yen,

  SAFE_DIVIDE(ordinary_income_million_yen, net_sales_million_yen) * 100
    AS ordinary_income_margin_pct,

  SAFE_DIVIDE(net_assets_million_yen, total_assets_million_yen) * 100
    AS net_assets_ratio_pct,

  SAFE_DIVIDE(employee_salary_million_yen, net_sales_million_yen) * 100
    AS personnel_cost_ratio_pct,

  SAFE_DIVIDE(real_investment_million_yen, net_sales_million_yen) * 100
    AS real_investment_ratio_pct,

  SAFE_DIVIDE(ordinary_income_million_yen, total_assets_million_yen) * 100
    AS ordinary_income_to_ending_assets_pct

FROM
  pivoted_values;
*/