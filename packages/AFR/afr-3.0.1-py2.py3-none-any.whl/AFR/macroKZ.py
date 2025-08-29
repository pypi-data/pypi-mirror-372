import pkg_resources
import pandas as pd

def load_macroKZ():
    """
           Loads macroKZ dataset. More details in the description of the dataset.

           """
    file_path = pkg_resources.resource_filename('AFR', 'load/macroKZ.csv')
    df = pd.read_csv(file_path)
    num_rows = len(df)

    start_date = '2010-01-01'
    date_range = pd.date_range(start=start_date, periods=num_rows, freq='Q')

    df['Date'] = date_range
    df.set_index('Date', inplace=True)

    return df