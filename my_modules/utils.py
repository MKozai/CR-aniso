import pickle
import pandas as pd
import numpy as np
from datetime import datetime as dt

def pickle_dump(obj,path):
    with open(path,mode='wb') as f:
        pickle.dump(obj,f)

def pickle_load(path):
    with open(path,mode='rb') as f:
        data = pickle.load(f)
        return data

def bartels(start,end):
    """
    Calculate Bartels rotation start dates.

    Parameters
    ----------
    start: str
        Start of calculation period 'YYYY-MM-DD'.
        Must be later than '2004-01-19'.

    end: str
        End of calculation period 'YYYY-MM-DD'.

    Returns
    -------
    List[int]
        Bartels rotations start dates in pydatetime.
    """

    dates_full = pd.date_range(start='1832-02-08',end=end,freq='27D').to_pydatetime()
    dates = dates_full[dates_full>dt.strptime(start,'%Y-%m-%d')]

    return dates
