finratKZ dataset
===============
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

    from finratKZ import load_finratKZ()

**Reference** :
The Agency of the Republic of Kazakhstan for Regulation and Development of Financial Market.