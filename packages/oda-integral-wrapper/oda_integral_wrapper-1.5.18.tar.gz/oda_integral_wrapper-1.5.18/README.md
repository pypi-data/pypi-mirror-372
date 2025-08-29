oda_api_wrapper
==========================================
*wrapper of API for cdci_data_analysis. 
Main features are:
- It launches jobs in chunks of arbitrary number of science windows (default to 50) with asynchronous calls.
- It combines results in summed spectra and mosaic images, or stitched light curves.
- It saves spectra in fits files ready to use with Xspec or other standard tools.
- It visualizes images into the notebook 
- It  allows to save the catalog of found sources with the most common cleaning options: duplicates and new sources
- It ensures that the source of interest has FLAG = 1 in the catalog so that JEM-X spectra and light curves are extracted
- It provides functionality to access the list of science windows with specialized services.
- It contains some facilities to output parameters of spectral fits in latex and plain text.
- It plots light curves
This wrapper was originally written to overcome 50 scw limitation in INTEGRAL analysis for general users, 
but acquired more general reach.*

What's the license?
-------------------

oda_api_wrapper is distributed under the terms of The MIT License.

Who's responsible?
-------------------
Carlo Ferrigno

Astronomy Department of the University of Geneva, Chemin d'Ecogia 16, CH-1290 Versoix, Switzerland


Installation
-------------------
1) Anaconda
    * `while read requirement; do conda install --yes $requirement; done < requirements.txt`
    * `python setup.py install`
    
2) PIP
    * `pip install oda_integral_wrapper`
Or from local source code
    * `pip install -r requirements.txt`
    * `python setup.py install`

Documentation
-------------------
In the test directory, you can find a notebook with example of usage.

These methods are an elaboration of what can be found at
https://github.com/cdcihub/oda_api_benchmark/tree/master/examples

We refer to oda_api for further documentation.
