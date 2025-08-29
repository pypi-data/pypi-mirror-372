import numpy as np

def checkdata(dataset):
    """
    Preliminary check of dataset for missing values, numeric format, outliers.

    Args:
        ------
        dataset (pandas.DataFrame): name of the dataset for analysis for preliminary check

    Returns
        ------
        str: A conclusion of the preliminary analysis.

    Example:
        ------
        >>> import pandas as pd
        >>> from utils import checkdata
        >>> d = pd.read_csv( "AFR/load/macroKZ.csv" )
        >>> checkdata.checkdata(d)

    Raises:
        ------
        FileNotFoundError: If the specified dataset cannot be found.
        pd.errors.EmptyDataError: If the specified dataset is empty.

    """

    #outlier function
    def outliers(column):
        """
        Identify outliers in the item's series in a dataset
        Args:
            column: a column of a dataset for analysis for preliminary check.

        Returns:
            number: number of non-numeric items in a dataset.
        """
        lower_bound = column.mean() - 3* column.std()
        upper_bound = column.mean() + 3* column.std()
        outlier = column[(lower_bound > column) | (upper_bound < column)]
        if outlier.empty:
            return False
        else:
            return True

    #numeric function
    def is_num(value):
        return isinstance(value, (int, float, np.number))

    non_num = 0
    for column in dataset.columns:
        for value in dataset[column]:
            if not is_num(value):
                non_num +=1
                break
    if non_num > 0:
        print(f'There are {non_num} non-numeric values in the dataset.')
    else:
        print(f'All values in the dataset are numeric.')

    #check for missing data
    missing = dataset.isna().sum().sum()
    if missing > 0:
        for column in dataset.iloc[:, 1:]:
            print(f'There are {missing} missing values in {column}.')
    else:
        print(f'There are no missing values in the dataset.')

    #check for outliers
    for column in dataset.iloc[:, 1:]:
        if is_num(dataset[column].iloc[0]):
            if outliers(dataset[column]):
                print( f'{column} column has outliers.' )
            else:
                continue
        else:
            print ( 'The dataset has no outliers.' )