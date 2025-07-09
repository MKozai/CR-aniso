[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15844859.svg)](https://doi.org/10.5281/zenodo.15844859)

Please follow the license and cite the DOI when you use this software.

# CR-aniso
Programs to analyze cosmic-ray anisotropies and density mainly observed by the Global Muon Detector Network (GMDN).

GMDN data and descriptions: http://hdl.handle.net/10091/0002001448

## Contents
- my_modules
  - spherical_harmonics.py: Functions handling anisotropy in spherical harmonics.
    - Libraries: fire, numpy, pandarallel, pandas, pyshtools, pyspedas, pytplot, scipy.
    - geo_to_gse(): Convert spherical harmonics from the geocentric (GEO) coordinate system to the Geocentric Solar Ecliptic (GSE) coordinate system.
  - gmdn.py: Functions to handle GMDN data in  NASA's CDF format in the remote repository. This will be integrated into IUGONET and its SPEDAS plugin in the near future.
  - utils.py: Utilities used by some programs above.
- GEO_to_GSE_demo.ipynb: Demonstration to convert spherical harmonics from the GEO to the GSE coordinate system.
- SPEDAS_demo.ipynb: Demonstration to use GMDN data in CDF and SPEDAS by gmdn.py.

## License

These programs are released under the MIT License.

They use the following third-party libraries with individual licenses:

- [NumPy](https://numpy.org/) (BSD 3-Clause)
- [Pandas](https://pandas.pydata.org/) (BSD 3-Clause)
- [SciPy](https://scipy.org/) (BSD 3-Clause)
- [matplotlib](https://matplotlib.org/) (BSD 3-Clause)
- [PySHTOOLS](https://shtools.oca.eu/) (BSD 3-Clause)
- [pandarallel](https://github.com/nalepae/pandarallel) (MIT)
- [PySPEDAS](https://github.com/spedas/pyspedas) (MIT)
- [pytplot](https://github.com/MAVENSDC/pytplot) (MIT)
- [Fire](https://github.com/google/python-fire) (Apache 2.0)

Please refer to each library's repository for license details.
