macroKZ dataset
===============
The dataset was gathered by the ARDFM based on Kazakhstan' official and public data from the `Bureau of National Statistics <https://stat.gov.kz/>`_.
The dataset contains 50 historic macroeconomic and 10 hypothetical financial data over 61 quarters of 2010-2025 period.
The *macroKZ* dataset will be updated periodically as the official statistical information is released.

**Dataset contains following data** :

- **real_gdp** Real GDP
- **GDD_Agr_R** Real gross value added Agriculture
- **GDD_Min_R** Real gross value added Mining
- **GDD_Man_R** Real gross value added Manufacture
- **GDD_Elc_R** Real gross value added Electricity
- **GDD_Con_R** Real gross value added Construction
- **GDD_Trd_R** Real gross value added Trade
- **GDD_Trn_R** Real gross value added Transportation
- **GDD_Inf_R** Real gross value added Information
- **GDD_Est_R** Real gross value added for Real estate
- **GDD_R** Real gross value added
- **GDP_DEF** GDP deflator
- **Rincpop_q** Real population average monthly income
- **Rexppop_q** Real population average monthly expenses
- **Rwage_q** Real population average monthly wage
- **imp** Import
- **exp** Export
- **cpi** Inflation
- **realest_resed_prim** Real price for estate in primary market
- **realest_resed_sec** Real price for estate in secondary market
- **realest_comm** Real price for commercial estate
- **index_stock_weighted** Change in stock value for traded companies
- **ntrade_Agr** Change in stock value for non-traded companies Agriculture
- **ntrade_Min** Change in stock value for non-traded companies Mining
- **ntrade_Man** Change in stock value for non-traded companies Manufacture
- **ntrade_Elc** Change in stock value for non-traded companies Electricity
- **ntrade_Con** Change in stock value for non-traded companies Construction
- **ntrade_Trd** Change in stock value for non-traded companies Trade
- **ntrade_Trn** Change in stock value for non-traded companies Transportation
- **ntrade_Inf** Change in stock value for non-traded companies Information
- **fed_fund_rate** Federal Funds Rate
- **govsec_rate_kzt_3m** Return on government securities in KZT, 3 m
- **govsec_rate_kzt_1y** Return on government securities in KZT, 1 year
- **govsec_rate_kzt_7y** Return on government securities in KZT, 7 years
- **govsec_rate_kzt_10y** Return on government securities in KZT, 10 years
- **tonia_rate** TONIA
- **rate_kzt_mort_0y_1y** Weighted average mortgage lending rate for new loans, less than a year
- **rate_kzt_mort_1y_iy** Weighted average mortgage lending rate for new loans, more than a year
- **rate_kzt_corp_0y_1y** Weighted average mortgage lending rate for new loans to non-financial organizations in KZT, less than a year
- **rate_usd_corp_0y_1y** Weighted average mortgage lending rate for new loans to non-financial organizations in CKB, less than a year
- **rate_kzt_corp_1y_iy** Weighted average mortgage lending rate for new loans to non-financial organizations in KZT, more than a year
- **rate_usd_corp_1y_iy** Weighted average mortgage lending rate for new loans to non-financial organizations in CKB, more than a year
- **rate_kzt_indv_0y_1y** Weighted average mortgage lending rate for consumer loans in KZT, less than a year
- **rate_kzt_indv_1y_iy** Weighted average mortgage lending rate for consumer loans in KZT, less than a year
- **usdkzt** USD KZT exchange rate
- **eurkzt** EUR KZT exchange rate
- **rurkzt** RUB KZT exchange rate
- **poil** Price for Brent
- **realest_resed_prim_rus** Real price for estate in primary market in Russia
- **realest_resed_sec_rus** Real price for estate in secondary market in Russia
- **cred_portfolio** credit portfolio
- **coef_k1** k1 prudential coefficient
- **coef_k3** k3 prudential coefficient
- **provisions** provisions
- **percent_margin** percent margin
- **com_inc** commissionary income
- **com_exp** commissionary expenses
- **oper_inc** operational income
- **oth_inc** other income
- **DR** default rate

**Example** :

.. code-block:: python

    from macroKZ import load_macroKZ()

**Reference** :
The Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market.