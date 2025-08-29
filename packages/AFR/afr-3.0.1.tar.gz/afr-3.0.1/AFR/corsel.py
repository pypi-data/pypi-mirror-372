import pandas as pd

def corsel(data, thrs: float = 0.65, value_type: str = "numeric"):
    """
    Correlation matrix for a dataset with an option to set a correlation threshold and
    option to correlation value as a number or boolean True/False.

    Args:
        ------
        data: pandas DataFrame or path to CSV file with a dataset for analysis for preliminary check
        thrs (float): correlation threshold numeric value to use for filtering. Default is 0.65
        value_type (str): type of correlation value as a "numeric" or "boolean" value. Default representation is numeric.

    Returns
        ------
        pd.DataFrame or boolean : A pair of value name and correlation of the correlation matrix based on the threshold.
        Type of data varies in accordance with a chosen value_type parameter.

    Example:
        ------
        >>> import pandas as pd
        >>> from utils.corsel import corsel
        >>> df = pd.read_csv("AFR/load/macroKZ.csv")
        >>> corsel(df, thrs=0.65, value_type = "numeric")

    Raises:
        ------
        ValueError: If 'thrs' is not in range(0,1).
        ValueError: If 'value_type' is not "numeric" neither "boolean".
        ValueError: If a column in the dataset is not numeric.
        TypeError: If the data is not pandas DataFrame nor path to CSV file.
    """

    #check the type of the input data
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise TypeError("Data must be a pandas DataFrame or a path to CSV file")

    #check the type of the column of the data
    for column in df.columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError("Column {} is not numeric.".format(column))

    #correlation matrix
    corr_matrix = round(df.corr(), 3)
    if value_type != 'numeric' and value_type != 'boolean':
        raise ValueError ( "Invalid value_type. It must be 'numeric' or 'boolean'." )

    if value_type == 'numeric':
        corr_matrix = round(df.corr(), 3)
    else:
        corr_matrix = corr_matrix.abs() > thrs

    return corr_matrix




