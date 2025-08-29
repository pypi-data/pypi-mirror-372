from statsmodels.regression.linear_model import OLS, OLSResults
from statsmodels.regression.linear_model import RegressionResultsWrapper

def adjr2_score(model):
    """
        Performs calculation of Adjusted R squared (Adj R2) for the given model.

        Args:
            ------
            model: OLS model

        Returns
            ------
            result: Adj R2 metrics.
        """

    if isinstance(model, OLS):
        model_results = model.fit()
    elif isinstance(model, (OLSResults, RegressionResultsWrapper)):
        model_results = model
    else:
        raise TypeError("Input must be an OLS model, OLSResults object, or RegressionResultsWrapper object.")

    k = model_results.df_model + 1
    n = model_results.nobs

    r2 = model_results.rsquared
    adj_r2 = 1 - ((1 - r2) * (n - 1)) / (n - k - 1)

    return round(adj_r2, 3)