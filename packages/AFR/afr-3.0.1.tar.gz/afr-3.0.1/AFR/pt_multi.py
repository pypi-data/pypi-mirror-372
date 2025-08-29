import numpy as np
from scipy.stats import norm

def pt_multi(portfolio_distribution, num_defaults, conf_level, num_years):
    """
    Estimates the multi-year probability of default using the Pluto and Tasche model.

    Args:
    portfolio_distribution (numpy array): The distribution of the portfolio loss rate.
    num_defaults (numpy array): The number of defaults observed in each portfolio over the num_years.
    conf_level (float): The confidence level for the estimate.
    num_years (int): Number of years of observations.

    Returns:
    The estimated multi-year probability of default for each portfolio.
    """

    # Calculate the mean and variance of the portfolio loss rate.
    mean = np.mean ( portfolio_distribution )
    var = np.var ( portfolio_distribution )

    # Calculate the threshold for the number of defaults.
    threshold = norm.ppf ( 1 - conf_level ) * np.sqrt ( var * num_years ) + mean * num_years

    # Calculate the excess defaults over the threshold.
    excess_defaults = num_defaults - threshold

    # Calculate the probability of default for each portfolio.
    pd = norm.sf ( excess_defaults / np.sqrt ( var * num_years ) )

    # Reverse the order of the probability of default values.
    pd = pd[::-1].round(3)

    print ( "Estimated probability of default:", pd )
    return pd