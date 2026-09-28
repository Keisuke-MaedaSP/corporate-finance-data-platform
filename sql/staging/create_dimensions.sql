CREATE OR REPLACE TABLE
  `{{PROJECT_ID}}.corporate_finance_staging.dim_financial_items`
AS
SELECT
  code AS item_code,
  ANY_VALUE(name) AS item_name
FROM
  `{{PROJECT_ID}}.corporate_finance_staging.estat_metadata_codes`
WHERE
  class_id = "cat01"
GROUP BY
  code;

CREATE OR REPLACE TABLE
  `{{PROJECT_ID}}.corporate_finance_staging.dim_industries`
AS
SELECT
  code AS industry_code,
  ANY_VALUE(name) AS industry_name
FROM
  `{{PROJECT_ID}}.corporate_finance_staging.estat_metadata_codes`
WHERE
  class_id = "cat02"
GROUP BY
  code;

CREATE OR REPLACE TABLE
  `{{PROJECT_ID}}.corporate_finance_staging.dim_capital_sizes`
AS
SELECT
  code AS capital_size_code,
  ANY_VALUE(name) AS capital_size_name
FROM
  `{{PROJECT_ID}}.corporate_finance_staging.estat_metadata_codes`
WHERE
  class_id = "cat03"
GROUP BY
  code;