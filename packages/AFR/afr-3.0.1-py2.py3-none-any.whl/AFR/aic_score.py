import numpy as np
from statsmodels.regression.linear_model import OLS, OLSResults
from statsmodels.regression.linear_model import RegressionResultsWrapper

def aic_score(model):
    """
        Performs calculation of Akaike Information criteria(AIC) for the given model.

        Args:
            ------
            model: OLS model

        Returns
            ------
            result: AIC metrics.
        """

    if isinstance(model, OLS):
        model_results = model.fit()
    elif isinstance(model, OLSResults) or isinstance(model, RegressionResultsWrapper):
        model_results = model
    else:
        raise TypeError("Input must be either an OLS model object or an OLSResults object.")
    y_pred = model_results.predict()
    k = model_results.df_model + 1
    n = model_results.nobs
    if isinstance(model, OLS):
        rss = np.sum((y_pred - model_results.endog)**2)
    else:
        rss = model_results.ssr
    aic = n * np.log(rss / n) + 2 * k
    return round(aic, 3)

