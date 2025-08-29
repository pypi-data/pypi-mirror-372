import statsmodels.api as sm
from statsmodels.formula.api import ols

def opt_size(model):
    """
    Calculation of the number of observations necessary to generate the regression for a given number of regressors.

    Args:
        ------
        model: OLS linear regression model.

    Returns
        ------
        size (int) : Number of observations necessary to generate the model.

    """

    if isinstance ( model, sm.regression.linear_model.OLS ):
        exog = model.exog
        nobs = model.nobs
    elif isinstance ( model, sm.regression.linear_model.RegressionResultsWrapper ):
        exog = model.model.exog
        nobs = model.nobs
    else:
        raise ValueError ( "Invalid model type. Model must be of type sm.OLS or statsmodels.formula.api.ols." )

    n = exog.shape[1] - 1
    min_obs = int(6 * n)

    if nobs < min_obs:
        print (
            f'Warning: There are only {round(nobs)} observations in the dataset, which is less than the recommended minimum of {min_obs} for this model with {n} independent variable(s).' )
    else:
        print (
            f'There are {round(nobs)} observations in the dataset, which is sufficient for this model with {n} independent variable(s).' )

