import itertools
import statsmodels.api as sm
import pandas as pd
import numpy as np

def check_betas(X, y, criterion, intercept = True):
    """
    Performs all possible subsets regression analysis for the given X and y with with an option to select criterion.
    Described criteria criteria are adjusted r2, t-test.

    Args:
        ------
        X: The predictor variables.
        y: The response variable
        criteria (str): The information criteria based on which
        intercept (bool): Logical; whether to include intercept term in the models.

    Returns
        ------
        pandas DataFrame: A table of subsets number, predictor variables and beta coefficients for each subset model.

    """

    n_pred = X.shape[1]
    subsets = []
    models = []

    # All possible subsets
    for i in range(1, n_pred+1):
        for subset in itertools.combinations(X.columns, i):
            subsets.append(subset)

    for i, subset in enumerate(subsets, 1):
        if intercept:
            X_subset = sm.add_constant(X.loc[:, subset])
            pred_list = list(subset)
            pred_list.insert (0, 'intercept')
        else:
            X_subset = X.loc[:, subset]
        model = sm.OLS(y, X_subset).fit()
        models.append(model)


    #for subsets
    subset_numbers = range(1, len(subsets)+1)
    predictors = [list ( subsets[i] ) for i in range(len(subsets))]

    #output table2
    subset_indices = [i + 1 for i in range ( len ( subsets ) )]
    adj_r_squared = [round(model.rsquared_adj, 3 ) for model in models]
    t_test = [np.max ( np.abs ( round(model.tvalues, 3) ) ) for model in models]

    #output
    table = pd.DataFrame ( {
        'Subset': subset_numbers,
        'Predictors': predictors,
    } )

    table2 = pd.DataFrame ( {
        'Index': subset_indices,
        'Subset': predictors,
        'Adjusted R Squared': adj_r_squared,
        't-test': t_test
    } )

    print (
        f'Based on the given predictors {len ( subsets )} models can be generated based on the scoring criteria {criterion}. See below:' )

    return table
    return table2
