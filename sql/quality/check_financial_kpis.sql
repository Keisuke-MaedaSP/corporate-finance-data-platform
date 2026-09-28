WITH financial_kpis AS (
  SELECT
    *
  FROM
    `{{PROJECT_ID}}.corporate_finance_mart.financial_kpis`
)

SELECT
  COUNT(*) AS record_count,
  COUNT(DISTINCT fiscal_year) AS unique_fiscal_year_count,
  COUNT(DISTINCT industry_code) AS unique_industry_count,
  COUNT(DISTINCT capital_size_code) AS unique_capital_size_count,

  COUNTIF(
    industry_name IS NULL
    OR capital_size_name IS NULL
  ) AS null_dimension_name_count,

  COUNTIF(
    ordinary_income_margin_pct IS NULL
    OR net_assets_ratio_pct IS NULL
    OR personnel_cost_ratio_pct IS NULL
    OR real_investment_ratio_pct IS NULL
    OR ordinary_income_to_ending_assets_pct IS NULL
  ) AS null_kpi_count,

  (
    SELECT COUNT(*)
    FROM (
      SELECT
        fiscal_year,
        industry_code,
        capital_size_code
      FROM financial_kpis
      GROUP BY 1, 2, 3
      HAVING COUNT(*) > 1
    )
  ) AS duplicate_grain_count
FROM
  financial_kpis;