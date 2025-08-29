import matplotlib.pyplot as plt
import statsmodels.api as sm
from mlxtend.feature_selection import SequentialFeatureSelector
from mlxtend.plotting import plot_sequential_feature_selection as plot_sfs
from sklearn.linear_model import LinearRegression
from sklearn.metrics import make_scorer, r2_score, accuracy_score, explained_variance_score
import numpy as np
import warnings

def rss(X, y):
    model = LinearRegression ().fit ( X, y )
    y_pred = model.predict ( X )
    rss_met = np.sum ( (y_pred - y) ** 2 )
    return rss_met

def aic_score(X, y):
    n = len ( y )
    k = X.shape[1]
    aic = n * np.log ( rss (X, y) / n ) + 2 * k
    return aic

def bic_score(X, y):
    n = len ( y )
    k = X.shape[1]
    bic = n * np.log ( rss(X, y) / n ) + k * np.log ( n )
    return bic

def sbic_score(X, y):
    model = LinearRegression ().fit ( X, y )
    n = len (y)
    k = len ( model.coef_ ) + 1
    sbic = n * np.log ( rss (X, y)/ n )  + np.log(n) * k * np.log ( n )/2
    return sbic

def adjr2_score(X, y):
    model = LinearRegression ().fit ( X, y )
    y_pred = model.predict ( X )
    k = X.shape[1]
    n = len(y)
    adj_r2 = 1 - ((1 - r2_score(y, y_pred)) * (n - 1)) / (n - k - 1)
    return adj_r2

def regsel_f(X, y, data, p_value = 0.05, scoring = 'r2'):
    """
    Allows to select the best model based on stepwise forward regression analysis with all possible models.
    The best model is chosen according to the specified scoring.

    Args:
        ------
        X: independent/predictor variable(-s)
        y: dependent/response variable
        data (pandas.DataFrame): dataset
        p_value (float): Variables with p-value less than {p_value} will enter into the model.
        scoring (str): Statistical metrics used to estimate the best model. The default value is R squared, r2.
        Other possible options for {scoring} are:
            'aic' , 'bic', 'sbic', 'accuracy',  'r2', 'adjr2', 'explained_variance' and other.

    Returns
        ------
        results: The best model and the plot of the coefficients.

    """

    y = y.values.reshape(-1, 1)

    model = LinearRegression().fit(X,y)

    custom_scoring = {
        'aic': make_scorer ( aic_score),
        'bic': make_scorer ( bic_score ),
        'sbic': make_scorer ( sbic_score ),
        'adjr2': make_scorer(adjr2_score)
    }

    built_scoring = {'r2': make_scorer(r2_score),
        'accuracy': make_scorer(accuracy_score),
        'explained_variance': make_scorer(explained_variance_score)
    }

    all_scoring = {**custom_scoring, **built_scoring}

    if scoring not in all_scoring:
        raise ValueError (
            f"Invalid scoring function '{scoring}'. Available options are: {list ( all_scoring.keys () )}" )

    sfs = SequentialFeatureSelector(model, k_features='best', forward = True,
                                    scoring = all_scoring[scoring], cv=None)

    sfs.fit(X, y)

    selected_features = sfs.k_feature_names_

    scores = sfs.get_metric_dict()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sfs.fit(X,y)



    print ( f'Selected regressors: {selected_features} based on the scoring criteria {scoring}\n' )

    #new dataset for the best regression model
    avg_scores = []
    for i in scores:
        avg_scores.append ( scores[i]['avg_score'] )

    max_index = avg_scores.index ( max ( avg_scores ) ) + 1
    final_reg = scores[max_index]

    col_name = final_reg['feature_names']
    X_new = data[list ( col_name )]

    #best regression
    X_new = sm.add_constant ( X_new )
    best = sm.OLS ( y, X_new )
    print ( best.fit ().summary () )

    #plot
    plot_sfs ( sfs.get_metric_dict (), kind='std_dev' )
    plt.xlabel ( 'Number of regressors' )
    plt.title ( 'Stepwise Forward Selection Regression (st.dev)' )
    plt.grid ()
    plt.show ()





