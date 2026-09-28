CREATE OR REPLACE TABLE
  `{{PROJECT_ID}}.corporate_finance_staging.financial_values`
PARTITION BY DATE(ingested_at)
CLUSTER BY fiscal_year, industry_code, capital_size_code
AS
WITH latest_extraction AS (
  SELECT
    *
  FROM
    `{{PROJECT_ID}}.corporate_finance_raw.estat_api_responses`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY stats_data_id
    ORDER BY ingested_at DESC
  ) = 1
),

exploded_values AS (
  SELECT
    extraction_id,
    ingested_at,
    stats_data_id,
    raw_value
  FROM
    latest_extraction,
    UNNEST(
      JSON_QUERY_ARRAY(
        response_json,
        '$.GET_STATS_DATA.STATISTICAL_DATA.DATA_INF.VALUE'
      )
    ) AS raw_value
)

SELECT
  extraction_id,
  ingested_at,
  stats_data_id,
  JSON_VALUE(raw_value, '$."@time"') AS time_code,
  SAFE_CAST(SUBSTR(JSON_VALUE(raw_value, '$."@time"'), 1, 4) AS INT64) AS fiscal_year,
  JSON_VALUE(raw_value, '$."@cat01"') AS item_code,
  JSON_VALUE(raw_value, '$."@cat02"') AS industry_code,
  JSON_VALUE(raw_value, '$."@cat03"') AS capital_size_code,
  JSON_VALUE(raw_value, '$."@unit"') AS unit,
  JSON_VALUE(raw_value, '$."$"') AS amount_text,
  SAFE_CAST(JSON_VALUE(raw_value, '$."$"') AS NUMERIC) AS amount_million_yen
FROM
  exploded_values;