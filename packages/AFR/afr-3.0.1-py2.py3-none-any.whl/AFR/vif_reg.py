import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor


def vif_reg(model):
    """
    Calculates the variation inflation factors of all predictors in regression models.

    Args:
        ------
        model (statsmodels.regression.linear_model.OLS): OLS linear regression model.

    Returns
        ------
        vif (pandas DataFrame): A Dataframe containing the vIF score for each independent factor.
    """

    X = model.model.exog
    vif_df = pd.DataFrame(index=model.params.index.drop('Intercept'), columns = ['VIF'])

    for i, col in enumerate(vif_df.index):
        vif = variance_inflation_factor(X, i)
        vif_df.at[col, 'VIF'] = round (vif, 2)

        if vif > 5:
            print ('Warning: The variable "{}" has a VIF of {:.2f} that exceeds acceptable threshold of 5.'.format(col, vif))

    print(f'\nIf statistics exceeds 5, please be aware of multicollinearity.\n')
    print (vif_df)




