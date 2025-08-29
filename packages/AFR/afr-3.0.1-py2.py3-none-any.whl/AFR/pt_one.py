import numpy as np
from scipy.stats import norm

def pt_one(portfolio_dist, num_defaults, conf_level):
    """
    Estimates the one-year probability of default using the Pluto and Tasche model.

    Args:
    portfolio_dist (numpy array): The distribution of the portfolio loss rate.
    num_defaults (numpy array): The number of defaults observed in each portfolio.
    conf_level (float): The confidence level for the estimate.

    Returns:
    The estimated one-year probability of default for each portfolio.
    """

    # Calculate the mean and variance of the portfolio loss rate.
    mean = np.mean ( portfolio_dist)
    var = np.var ( portfolio_dist)

    # Calculate the threshold for the number of defaults.
    threshold = norm.ppf ( 1 - conf_level ) * np.sqrt ( var ) + mean

    # Calculate the excess defaults over the threshold.
    excess_defaults = num_defaults - threshold

    # Calculate the probability of default for each portfolio.
    pd = norm.sf ( excess_defaults / np.sqrt ( var ) )

    # Reverse the order of the probability of default values.
    pd = pd[::-1].round(3)

    print ( "Estimated probability of default:", pd )
    return pd