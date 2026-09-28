WITH financial_values AS (
  SELECT
    *
  FROM
    `{{PROJECT_ID}}.corporate_finance_staging.financial_values`
)

SELECT
  COUNT(*) AS record_count,
  COUNT(DISTINCT item_code) AS unique_item_count,
  COUNT(DISTINCT industry_code) AS unique_industry_count,
  COUNT(DISTINCT capital_size_code) AS unique_capital_size_count,
  COUNT(DISTINCT fiscal_year) AS unique_fiscal_year_count,

  COUNTIF(
    time_code IS NULL
    OR item_code IS NULL
    OR industry_code IS NULL
    OR capital_size_code IS NULL
    OR fiscal_year IS NULL
    OR unit IS NULL
  ) AS null_dimension_count,

  COUNTIF(amount_million_yen IS NULL) AS null_amount_count,

  COUNTIF(
    item_code IN ("022", "045", "066")
    AND amount_million_yen < 0
  ) AS invalid_negative_count,

  (
    SELECT COUNT(*)
    FROM (
      SELECT
        time_code,
        item_code,
        industry_code,
        capital_size_code
      FROM financial_values
      GROUP BY 1, 2, 3, 4
      HAVING COUNT(*) > 1
    )
  ) AS duplicate_key_count,

  (
    SELECT COUNT(*)
    FROM (
      SELECT
        fiscal_year,
        industry_code,
        capital_size_code,
        COUNT(DISTINCT item_code) AS item_count
      FROM financial_values
      GROUP BY 1, 2, 3
      HAVING item_count != 6
    )
  ) AS incomplete_combination_count
FROM
  financial_values;