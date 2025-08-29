import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def dec_plot(model, data):
    """
    The function depicts decomposition of regressors as a stacked barplot describing contribution of each regressor to the regression model.

    Args:
        ------
        model: OLS linear regression model.
        data(pandas.DataFrame): A dataset based on which the model was built.

    Returns
        ------
        plot : matplotlib figure.

    """


    coef = model.params
    names = coef.index.drop('Intercept')

    pred = data[names]*coef[names]

    #plot

    for i in names:
        plt.bar ( pred.index, pred[i], width=1 )
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Decomposition Plot')
    plt.legend(names)
    plt.show()
