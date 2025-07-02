import pytplot

def load(trange, sites, suffix='', time_clip=False, local_path='./gmdn_data/', no_download=False):

    """
    Load GMDN data in CDF format.

        Parameters
    ----------
    trange: list[str]
        list of start and end dates in string 'YYYY-MM-DD'.
    sites: list[str]
        List of site codes.
    suffix: str
        The tplot variable names will be given this suffix. By default, no suffix is added.
    time_clip: bool
        Clip loaded data with the trange. Default is False.
    local_path: str
        Local directory path where downloaded data are stored. Defalut is './gmdn_data/'.
    no_download: bool
        Load file from local. Default is False.
    
    Returns
    ----------
    list[int]
        list of loaded tplot variable names.
    """
    import pandas as pd
    import pyspedas as pys
    from pyspedas.utilities.dailynames import dailynames
    from pyspedas.utilities.download import download
    from pytplot.tplot_math import time_clip as tclip
    import glob

    tvars = []
    for site in sites:
        pathformat = 'gmdn_1h_pcorr_' + site.lower()

        if no_download is True:
            pathformat = local_path + pathformat
            styear = int(trange[0].split('-')[0])
            enyear = int(trange[1].split('-')[0])
            files = []
            for year in range(styear,enyear+1):
                pathformat_y = pathformat + '_' + str(year) + '_v??.cdf'
                files_y = glob.glob(pathformat_y)
                if len(files_y) > 0:
                    files += [files_y[-1]]
            print(files)
        else:
            remote_data_dir = 'https://polaris.nipr.ac.jp/~kozai-cr/data/gmdn/'
            pathformat = pathformat + '_%Y_v??.cdf'
            remote_names = dailynames(file_format=pathformat, trange=trange)

            files = download(remote_file=remote_names, remote_path=remote_data_dir,
                local_path=local_path,last_version=True)

        out_files = []
        if files is not None:
            for file in files:
                out_files.append(file)

        out_files = sorted(out_files)
        tvars += pytplot.cdf_to_tplot(out_files, suffix='_'+site+suffix)

    if time_clip:
        for var_name in tvars:
            tclip(var_name, trange[0], trange[1], suffix='', overwrite=True)

    return tvars

def plot(trange, sites=[], skip=[], figsize=(10,8), display=False, figfile=''):
    """
    Plot GMDN data extracted from tplot object.

        Parameters
    ----------
    trange: list[str]
        list of start and end dates in string 'YYYY-MM-DD'.
    sites: list[str]
        List of site codes. Default is an empty list and plot all site data in tplot.
    skip: list[str]
        Skip this tnames variable in plot.
    figsize: tuple
        Figure size in (x,y) for matplotlib plt.subplots(). Default is (10,8)
    display: bool
        Display plot by matplotlib pyplot.show(). Default is False.
    figfile: str
        Save figure file in this path/file name. Default is '' and not saving figure.
    """

    import numpy as np
    from itertools import chain
    from datetime import datetime, timedelta
    from matplotlib import pyplot as plt
    from matplotlib.ticker import FuncFormatter

    xarrs = pytplot.data_quants

    dict_labels = {}
    nrow = 0
    for key, xarr in xarrs.items():
        if key.strip() in skip:
            continue

        if xarr.attrs['CDF']['GATT']['Project']=='Global Muon Detector Network':
            if len(sites)==0 or xarr.attrs['CDF']['GATT']['Station_code'] in sites:
                labels = xarr.attrs['CDF']['LABELS']

                if labels==None:
                    list_labels = [[key.strip()]]
                    nrow += 1
                else:
                    labels_trim = [s.strip() for s in labels]
                    list_labels = [[s for s in labels_trim if s=='V']]
                    list_labels += [[s for s in labels_trim if len(s)==1 and not s in chain.from_iterable(list_labels)]]
                    list_labels += [[s for s in labels_trim if not s[-1].isdigit() and not s in chain.from_iterable(list_labels)]]
                    list_labels += [[s for s in labels_trim if s.endswith('2') and not s in chain.from_iterable(list_labels)]]
                    list_labels += [[s for s in labels_trim if s.endswith('3') and not s in chain.from_iterable(list_labels)]]
                    list_labels = [l for l in list_labels if len(l)>0]
                    nrow += len(list_labels)

                dict_labels[key] = list_labels
            
    if nrow == 0:
        return

    fig, axs = plt.subplots(nrows=nrow, figsize=figsize, sharex=True)

    xrange = [datetime.strptime(s, '%Y-%m-%d') for s in trange]
    mhour = 3
    xrange = [xrange[0] - timedelta(hours=mhour), xrange[1] + timedelta(hours=mhour)]
    iax = 0
    for key in dict_labels.keys():
        xarr = xarrs[key]

        if xarr.attrs['CDF']['GATT']['Project']=='Global Muon Detector Network':
            if len(sites)==0 or xarr.attrs['CDF']['GATT']['Station_code'] in sites:
                print(key, end=': ')
                labels_raw = xarr.attrs['CDF']['LABELS']
                labels_raw = dict_labels[key] if labels_raw==None else [s.strip() for s in labels_raw]
                unit = xarr.attrs['data_att']['units']
                dims = xarr.dims

                for labels in dict_labels[key]:
                    ax = axs[iax]
                    for label in labels:
                        print(label, end=' ')
                        xarr_plot = xarr if len(dims)==1 else xarr.isel({dims[1]: labels_raw.index(label)})
                        xarr_plot = xarr_plot[xarr_plot>0]
                        if xarr_plot.size<=1:
                            print('Empty Xarray!')
                        elif not np.issubdtype(xarr_plot.dtype, np.number):
                            print('Non-Numeric Data!')
                        elif xarr_plot.count()==0:
                            print('All NaN Xarray!')
                        else:
                            xarr_plot.plot.line(marker='o', markersize=2, linestyle='--', linewidth=0.5, label=label, ax=ax)

                    ax.set_xlim(xrange)
                    ax.set_xlabel('')

                    if key.startswith('count_'):
                        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x:.2e}'))
                    ax.set_ylabel(unit)

                    ax.text(0.99, 0.95, key, transform=ax.transAxes, ha='right', va='top', fontsize=8)
                    if len(labels_raw)>1:
                        ax.legend(loc='center left', bbox_to_anchor=(1,0.5))
                    ax.minorticks_on()
                    ax.tick_params(axis='both', which='both', direction='in')
                    ax.grid()

                    iax += 1

                fig.subplots_adjust(hspace=0.15)
                print()

    if len(figfile)>0:
        plt.savefig(figfile, bbox_inches='tight')
        print(figfile)
            
    if display==True:
        plt.show()
    else:
        plt.close()

    return
