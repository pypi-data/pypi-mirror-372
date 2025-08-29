import numpy as np
from statsmodels.regression.linear_model import OLS, OLSResults
from statsmodels.regression.linear_model import RegressionResultsWrapper

def sbic_score(model):
    """
        Performs calculation of Schwarz Bayesian Information criteria(SBIC) for the given model.

        Args:
            ------
            model: OLS model

        Returns
            ------
            result: SBIC metrics.
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
    sbic = n * np.log ( rss / n )  + np.log(n) * k * np.log ( n )/2
    return round(sbic, 3)