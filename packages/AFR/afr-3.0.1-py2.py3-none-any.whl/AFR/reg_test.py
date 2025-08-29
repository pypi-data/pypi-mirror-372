from statsmodels.stats.diagnostic import het_breuschpagan,acorr_breusch_godfrey, het_goldfeldquandt
from statsmodels.stats.stattools import durbin_watson

def reg_test(model):
    """
    Tests for detecting violation of Gauss-Markov assumptions.

    Args:
        ------
        model : OLS linear regression model.

    Returns
        ------
        results (dict) : A dictionary containing the results of the four tests.

    """

    #results = model.fit()
    #Tests
    bp_test = het_breuschpagan(model.resid, model.model.exog)
    bg_test = acorr_breusch_godfrey(model)
    dw_test = durbin_watson(model.resid)
    gq_test = het_goldfeldquandt(model.resid, model.model.exog)

    headers = ['Test', 'test statistic', 'p-value']
    dict = {'Breusch-Pagan': [round(bp_test[0],2), round(bp_test[1],2)],
            'Breusch-Godfrey': [round(bg_test[0],2), round(bg_test[1],2)],
            'Durbin-Watson': [round(dw_test, 2), None],
            'Godfrey-Quandt': [round(gq_test[0], 2),round(gq_test[1],2) ]}

    main = "Gauss-Markov assumptions tests"
    centered_main = main.center(45)

    print(centered_main)
    print(f'{headers[0]: <20}{headers[1]: <18}{headers[2]}')

    for key, value in dict.items():
        print(f'{key: <20}{value[0]: <18}{value[1]}')
