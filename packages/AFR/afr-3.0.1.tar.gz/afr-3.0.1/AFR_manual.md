
# Package ‘AFR’


Statistical toolkit aimed to help statisticians, data analysts, data scientists, bankers and other professionals to analyze financial data.

It was designed by the team of the Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market (ARDFM).

AFR toolkit offers functions to upload, preliminary check, analyze data and regressions and interpret results.


##### Authors:

Timur Abilkassymov, the Advisor to the Chairperson of the ARDFM.

Alua Makhmetova, chief specialist of the Department of Banking Analytics and Stress Testing of the ARDFM.

Sultan Zhaparov, maintainer of the project, chief specialist of the Department of Banking Analytics and Stress Testing of the ARDFM.

##### Contact:

Sultan Zhaparov

sultan.saldau@gmail.com

##### Copyright:

The Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market. The [link](https://www.gov.kz/memleket/entities/ardfm?lang=en)



## Datasets


AFR has built-in datasets named _macroKZ_ and _finratKZ_ that were gathered by the ARDFM team. More details below.

## finratKZ dataset

Dataset *finratKZ* was gathered during the supervisory procedure of the banking sector of Kazakhstan. ARDFM team analyzed financial statements of the corporate borrowers and calculated financial ratios.

The data was collected during regular supervisory asset quality review(AQR) procedure. During the AQR corporate borrowers were classified as default and standard (IFRS stage 1).

**Dataset contains following data** :

- **Default** - Dummy variable where 0 - standard(IFRS stage 1) borrower, 1 - default borrower
- **Rev_gr** - Revenue growth rate
- **EBITDA_gr** - EBITDA growth rate
- **Cap_gr** - Capital growth rate
- **CR** - Current ratio
- **QR** - Quick ratio
- **Cash_ratio** - Cash ratio
- **WC_cycle** - Working capital cycle
- **DTA** - Debt-to-assets
- **DTE** -Debt-to-equity
- **LR** - Leverage ratio (Total assets/Total equity)
- **EBITDA_debt** - EBITDA-to-debt
- **IC** - Interest coverage (Income statement)
- **CTI** - Cash-to-income
- **IC_CF** - Interest coverage (Cash flow statement)
- **DCR** - Debt coverage ratio (Cash flow from operations/Total debt)
- **CFR** - Cash flow to revenue
- **CRA** - Cash return on assets (Cash flow from operations/Total assets)
- **CRE** - Cash return on equity (Cash flow from operations/Total equity)
- **ROA** - Return on assets
- **ROE** - Return on equity
- **NPM** - Net profit margin
- **GPM** - Gross profit margin
- **OPM** - Operating profit margin
- **RecT** - Receivables turnover
- **InvT** - Inventory turnover
- **PayT** - Payables turnover
- **TA** - Total assets turnover
- **FA** - Fixed assets turnover
- **WC** - Working capital turnover

**Example** :

.. code-block:: python

    import pandas as pd
    finrat = pd.read_csv('./finratKZ.csv')

**Reference** :
The Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market.


## macroKZ dataset

The dataset was gathered by the ARDFM based on Kazakhstan' official and public data from the [Bureau of National Statistics](https://stat.gov.kz/).

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

    import pandas as pd
    macro = pd.read_csv('./macroKZ.csv')

**Reference** :
The Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market.



## Functions



* **adjr2_score**

Performs calculation of Adjusted R squared (Adj R2) for the given model.

_Arguments_:

model: OLS model

_Result_:

result: Adj R2 metrics.

_Example_:

print(adjr2_score(model))



* **aic_score**

Performs calculation of Akaike Information criteria(AIC) for the given model.

_Arguments_:

model: OLS model

_Result_:

result: AIC metrics.

_Example_:

print(aic_score(model))



* **bic_score**

Performs calculation of Akaike Information criteria(AIC) for the given model.

_Arguments_:

model: OLS model

_Result_:

result: AIC metrics.

_Example_:

print(bic_score(model))



* **check_betas**

Performs all possible subsets regression analysis for the given X and y with with an option to select criterion.
Possible criteria are r2, AIC, BIC.

_Arguments_:

X: The predictor variables.

y: The response variable
criteria (str): The information criteria based on which

intercept (bool): Logical; whether to include intercept term in the models.
        
_Result_:

pandas DataFrame: A table of subsets number, predictor variables and beta coefficients for each subset model.
  
_Example_:

X = macro[['poil', 'cpi', 'usdkzt', 'GDP_DEF', 'exp', 'tonia_rate']]

y = macro['real_gdp']

check_betas(X, y, criterion = 'bic', intercept = False)



* **checkdata**

Preliminary check of dataset for missing values, numeric format, outliers.

_Arguments_:

dataset: name of the CSV file with a dataset for analysis for preliminary check

_Result_:

str: A conclusion of the preliminary analysis.

_Example_:

import pandas as pd

macro = pd.read_csv('./load/macroKZ.csv')

checkdata(macro)



* **corsel**

Correlation matrix for a dataset with an option to set a correlation threshold and option to correlation value as a number or boolean True/False.

_Arguments_:

data: pandas DataFrame or path to CSV file with a dataset for analysis for preliminary check

thrs (float): correlation threshold numeric value to use for filtering. Default is 0.65
        
value_type (str): type of correlation value as a "numeric" or "boolean" value. Default representation is numeric.

_Result_:

pd.DataFrame or boolean : A pair of value name and correlation of the correlation matrix based on the threshold.
Type of data varies in accordance with a chosen value_type parameter.

_Example_:

data = macro[['poil', 'cpi', 'usdkzt', 'GDP_DEF', 'exp', 'GDD_Agr_R', 'rurkzt', 'tonia_rate', 'cred_portfolio', 'fed_fund_rate']]

corsel(data, thrs = 0.65, value_type = "boolean")



* **dec_plot**

The function depicts decomposition of regressors as a stacked barplot.

_Arguments_:

model: OLS linear regression model.

data(pandas.DataFrame): A dataset based on which the model was built.

_Result_:

plot : matplotlib figure.

_Example_:

model = ols('real_gdp ~ poil + cpi + usdkzt + imp', data = macro).fit()

dec_plot(model, macro)



* **opt_size**

Calculation of the number of observations necessary to generate the regression for a given number of regressors.

_Arguments_:

model: OLS linear regression model.

_Result_:

size (int) : Number of observations necessary to generate the model.

_Example_:

model = ols('real_gdp ~ poil + cpi + usdkzt + imp', data = macro).fit()

opt_size(model)



* **pt_multi**

Estimates the multi-year probability of default using the Pluto and Tasche model.

_Arguments_:

portfolio_distribution (numpy array): The distribution of the portfolio loss rate.

num_defaults (numpy array): The number of defaults observed in each portfolio over the num_years.

conf_level (float): The confidence level for the estimate.

num_years (int): Number of years of observations.

_Result_:

The estimated multi-year probability of default for each portfolio.

_Example_:

portfolio_distribution = np.array([10,20,30,40,10,20])

num_defaults = np.array([1, 2, 1, 0, 3, 2])

conf_level = 0.99

num_years = 3

pt_multi(portfolio_distribution, num_defaults, conf_level, num_years)



* **pt_one**

Estimates the one-year probability of default using the Pluto and Tasche model.

_Arguments_:

portfolio_dist (numpy array): The distribution of the portfolio loss rate.

num_defaults (numpy array): The number of defaults observed in each portfolio.

conf_level (float): The confidence level for the estimate.

_Result_:

The estimated one-year probability of default for each portfolio.

_Example_:

portfolio_distribution = np.array([10,20,30,40,10,20])

num_defaults = np.array([1, 2, 1, 0, 3, 2])

conf_level = 0.99

pt_one(portfolio_distribution, num_defaults, conf_level)



* **reg_test**

Tests for detecting violation of Gauss-Markov assumptions.

_Arguments_:

model : OLS linear regression model.

_Result_:

results (dict) : A dictionary containing the results of the four tests.

_Example_:

model = ols('real_gdp ~ poil + cpi + usdkzt + imp', data = macro).fit()

reg_test(model)



* **regsel_f**

Allows to select the best model based on stepwise forward regression analysis with all possible models.
The best model is chosen according to the specified scoring.

_Arguments_:

X: independent/predictor variable(-s)

y: dependent/response variable

data (pandas.DataFrame): dataset

p_value (float): Variables with p-value less than {p_value} will enter into the model.

scoring (str): Statistical metrics used to estimate the best model. The default value is R squared, r2.

Other possible options for {scoring} are: 'aic' , 'bic', 'sbic', 'accuracy',  'r2', 'adjr2', 'explained_variance' and other.

_Result_:

results: The best model and the plot of the coefficients.

_Example_:

X = macro[['poil', 'cpi', 'usdkzt', 'GDP_DEF', 'exp', 'tonia_rate']]

y = macro['real_gdp']

regsel_f(X, y, macro, scoring = 'aic')



* **sbic_score**

Performs calculation of Schwarz Bayesian Information criteria(SBIC) for the given model.

_Arguments_:

model: OLS model

_Result_:

result: SBIC metrics.

_Example_:

model = ols('real_gdp ~ poil + cpi + usdkzt + imp', data = macro).fit()

print(sbic_score(model))



* **vif_reg**

Calculates the variation inflation factors of all predictors in regression models.

_Arguments_:

model: OLS linear regression model.

_Result_:

vif (pandas DataFrame): A Dataframe containing the vIF score for each independent factor.

_Example_:

model = ols('real_gdp ~ poil + cpi + usdkzt + imp', data = macro).fit()

vif_reg(model)
