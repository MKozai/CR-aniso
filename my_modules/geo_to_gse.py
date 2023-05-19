#PySPEDAS library for coordinate system: https://pyspedas.readthedocs.io/en/latest/
#pyshtools library for spherical harmonics: https://pypi.org/project/pyshtools/
import os
from contextlib import redirect_stdout
import pandas as pd
import numpy as np
from datetime import datetime as dt
from scipy.spatial.transform import Rotation as rot
import pyshtools as pysh
from pyspedas.utilities.time_double import time_double
from pyspedas.cotrans.cotrans_lib import subcotrans

def geo_to_gse(data_geo):
    """
    Transform harmonics anisotropy from GEO coordinate to GSE coordinate.

    Parameters
    ----------
    data_geo: DataFrame
        Data table of anisotropy.

    Returns
    -------
    DataFrame
        Data table of the anisotropy transformed to GSE coordinate.
    """

    #Read input data.
    data_other = pd.DataFrame()
    dict_gse = dict()
    for col in data_geo.columns:
        if (col.startswith('XC.') or col.startswith('XS.')) and int(col.split('.')[1]) > 0:
            dict_gse[col] = list()
            n_max = int(col.split('.')[1])
        else:
            data_other[col] = data_geo[col].copy()

    #Calculation for each time (row).
    str_month_pre = ''
    for index, row in data_geo.iterrows():
        str_month = index.strftime('%Y/%m')
        if str_month!=str_month_pre:
            print(str_month, end=' ')
            str_month_pre = str_month

        if row.isna().any():
            for key in dict_gse.keys():
                dict_gse[key] += [None]
        else:
            str_time = dt(index.year,index.month,index.day).strftime('%Y-%m-%d/%H:%M:%S')
            spedas_time = time_double(str_time)
            
            #Calculate transformation matrix (3x3) using pyspedas.
            mat_trans = np.empty((0,3))
            for j in range(3):
                vec_geo = np.zeros(3)
                vec_geo[j] = 1.
                with redirect_stdout(open(os.devnull, 'w')):
                    vec_gse = subcotrans([spedas_time], [vec_geo], 'geo','gse')
                mat_trans = np.append(mat_trans, vec_gse, axis=0)
            mat_trans = mat_trans.T

            rot_trans = rot.from_matrix(mat_trans)
            euler_trans = rot_trans.as_euler('ZYZ', degrees=True)
            alpha = euler_trans[0]
            beta = euler_trans[1]
            gamma = euler_trans[2]

            array_geo = np.zeros((2,n_max+1, n_max+1))
            for key in dict_gse.keys():
                n = int(key.split('.')[1])
                m = int(key.split('.')[2])
                i = 0 if key.startswith('XC.') else 1 if key.startswith('XS.') else None
                array_geo[i,n,m] = row[key]

            #Transform spherical harmonics using pyshtools.
            coef_geo = pysh.SHCoeffs.from_array(array_geo)
            coef_gse = coef_geo.rotate(alpha,beta,gamma,body=True,degrees=True)
            array_gse = coef_gse.to_array()

            for key in dict_gse.keys():
                n = int(key.split('.')[1])
                m = int(key.split('.')[2])
                i = 0 if key.startswith('XC.') else 1 if key.startswith('XS.') else None
                dict_gse[key] += [array_gse[i,n,m]]

    data_gse = pd.DataFrame(data=dict_gse,index=data_geo.index)
    data_gse = pd.concat([data_gse,data_other],axis='columns')
    print('Finished!')
    return data_gse
