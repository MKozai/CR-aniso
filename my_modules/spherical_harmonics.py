import pandas as pd
import numpy as np
from datetime import datetime as dt
import fire
from scipy.spatial.transform import Rotation as rot
import pyshtools as pysh
from pandarallel import pandarallel
from pytplot import time_double
from pyspedas.cotrans.cotrans_lib import subcotrans
from my_modules import utils

#PySPEDAS library for coordinate system: https://pyspedas.readthedocs.io/en/latest/
#pyshtools library for spherical harmonics: https://pypi.org/project/pyshtools/

def geo_to_gse(data_geo, output: bool=True):
    """
    Transform spherical harmonics from the GEO coordinate system with its x-axis in midnight direction to the GSE coordinate system.

    Parameters
    ----------
    data_geo: DataFrame
        Spherical-harmonics expansion coefficients in each time. Index is datetime and the column name "XC.n.m" or "XS.n.m" indicates the cosine- or sine-component of the n-th degree and m-th order harmonics.
        Input pickle file path in the CLI mode.

    output: boolean
        Output progress bar.

    Returns
    -------
    DataFrame
        Spherical-harmonics expansion coefficients transformed to the GSE coordinate system.
        Saved in pickle file in the CLI mode.
    """

    from_cli = False
    if isinstance(data_geo, str):
        data_geo = utils.pickle_load(data_geo)
        from_cli = True

    print('make input data')
    data_other = pd.DataFrame()
    params = []
    n_max = 0
    for col in data_geo.columns:
        if (col.startswith('XC.') or col.startswith('XS.')) and int(col.split('.')[1]) > 0:
            params += [col]
            n = int(col.split('.')[1])
            if n>n_max:
                n_max = n
        else:
            data_other[col] = data_geo[col].copy()

    times = []
    list_args = []
    for index in data_geo.index:
        times += [dt(index.year,index.month,index.day).strftime('%Y-%m-%d/%H:%M:%S')]
        list_args += [data_geo.loc[index,params].values]
    data_args = pd.DataFrame({'TIME': times, 'LIST': list_args},index=data_geo.index)

    print('transformation')
    pandarallel.initialize(progress_bar=output)
    data_res = data_args.parallel_apply(lambda x: geo_to_gse_time(x['TIME'],x['LIST'],params,n_max), axis=1)

    data_gse = pd.DataFrame(data_res.values.tolist(),index=data_geo.index,columns=params)
    data_gse = pd.concat([data_gse,data_other],axis='columns')

    print('Finished!')

    if from_cli:
        outfile = 'data_gse.pkl'
        utils.pickle_dump(data_gse, outfile)
        print('Saved in ' + outfile)
        return outfile
    else:
        return data_gse

def geo_to_gse_time(time,list_geo,params,n_max):
    """
    Transform spherical harmonics from the GEO coordinate system with its x-axis in midnight direction to the GSE coordinate system for the input time.

    Parameters
    ----------
    time: datetime

    list_geo: list[float]
        Spherical-harmonics expansion coefficients.

    params: list[str]
        Parameter names of list_geo. "XC.n.m" or "XS.n.m" indicates the cosine- or sine-component of the n-th degree and m-th order harmonics.

    n_max: int
        Maximum degree of the harmonics.

    Returns
    -------
    list
        Spherical-harmonics expansion coefficients transformed to the GSE coordinate system in the same order with list_geo.
    """

    if np.isnan(list_geo).any():
        list_gse = [None]*len(list_geo)
    else:
        spedas_time = time_double(time)
        
        #Calculate transformation matrix (3x3) using pyspedas.
        mat_trans = np.empty((0,3))
        for j in range(3):
            vec_geo = np.zeros(3)
            vec_geo[j] = 1.
            vec_gse = subcotrans([spedas_time], [vec_geo], 'geo','gse')
            mat_trans = np.append(mat_trans, vec_gse, axis=0)
        mat_trans = mat_trans.T

        rot_trans = rot.from_matrix(mat_trans)
        euler_trans = rot_trans.as_euler('ZYZ', degrees=True)
        alpha = euler_trans[0]
        beta = euler_trans[1]
        gamma = euler_trans[2]

        array_geo = np.zeros((2,n_max+1, n_max+1))
        for param in params:
            n = int(param.split('.')[1])
            m = int(param.split('.')[2])
            i = 0 if param.startswith('XC.') else 1 if param.startswith('XS.') else None
            array_geo[i,n,m] = list_geo[params.index(param)]

        #Transform spherical harmonics using pyshtools.
        coef_geo = pysh.SHCoeffs.from_array(array_geo)
        coef_gse = coef_geo.rotate(alpha,beta,gamma,body=True,degrees=True)
        array_gse = coef_gse.to_array()

        list_gse = np.empty(0)
        for param in params:
            n = int(param.split('.')[1])
            m = int(param.split('.')[2])
            i = 0 if param.startswith('XC.') else 1 if param.startswith('XS.') else None
            list_gse = np.concatenate([list_gse,[array_gse[i,n,m]]])

    return list_gse

if __name__ == "__main__":
    fire.Fire(geo_to_gse)
