WITH comparison AS (
  SELECT
    industry_name,
    capital_size_name,

    MAX(IF(fiscal_year = 2016, net_sales_million_yen, NULL))
      AS net_sales_2016_million_yen,
    MAX(IF(fiscal_year = 2025, net_sales_million_yen, NULL))
      AS net_sales_2025_million_yen,

    MAX(IF(fiscal_year = 2016, ordinary_income_margin_pct, NULL))
      AS ordinary_income_margin_2016_pct,
    MAX(IF(fiscal_year = 2025, ordinary_income_margin_pct, NULL))
      AS ordinary_income_margin_2025_pct,

    MAX(IF(fiscal_year = 2016, net_assets_ratio_pct, NULL))
      AS net_assets_ratio_2016_pct,
    MAX(IF(fiscal_year = 2025, net_assets_ratio_pct, NULL))
      AS net_assets_ratio_2025_pct,

    MAX(IF(fiscal_year = 2016, personnel_cost_ratio_pct, NULL))
      AS personnel_cost_ratio_2016_pct,
    MAX(IF(fiscal_year = 2025, personnel_cost_ratio_pct, NULL))
      AS personnel_cost_ratio_2025_pct,

    MAX(IF(fiscal_year = 2016, real_investment_ratio_pct, NULL))
      AS real_investment_ratio_2016_pct,
    MAX(IF(fiscal_year = 2025, real_investment_ratio_pct, NULL))
      AS real_investment_ratio_2025_pct

  FROM
    `{{PROJECT_ID}}.corporate_finance_mart.financial_kpis`
  GROUP BY
    industry_name,
    capital_size_name
)

SELECT
  *,

  SAFE_DIVIDE(
    net_sales_2025_million_yen - net_sales_2016_million_yen,
    net_sales_2016_million_yen
  ) * 100 AS net_sales_growth_2016_2025_pct,

  ordinary_income_margin_2025_pct - ordinary_income_margin_2016_pct
    AS ordinary_income_margin_change_pp,

  net_assets_ratio_2025_pct - net_assets_ratio_2016_pct
    AS net_assets_ratio_change_pp,

  personnel_cost_ratio_2025_pct - personnel_cost_ratio_2016_pct
    AS personnel_cost_ratio_change_pp,

  real_investment_ratio_2025_pct - real_investment_ratio_2016_pct
    AS real_investment_ratio_change_pp

FROM
  comparison
ORDER BY
  industry_name,
  capital_size_name;