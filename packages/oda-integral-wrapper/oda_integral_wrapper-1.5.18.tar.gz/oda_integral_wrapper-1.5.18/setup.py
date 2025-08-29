from __future__ import absolute_import, division, print_function

__author__ = 'Carlo Ferrigno'

#!/usr/bin/env python

from setuptools import setup, find_packages
import glob

packs = find_packages()

print('packs', packs)

include_package_data = True

scripts_list = glob.glob('./bin/*')
setup(name='oda_integral_wrapper',
      version="1.5.18",
      description='wrapper for INTEGRAL analysis using the API plugin for Multi-messenger online data analysis',
      author='Carlo Ferrigno',
      author_email='carlo.ferrigno@unige.ch',
      url="https://gitlab.astro.unige.ch/oda/api-clients/oda_api_wrapper",
      scripts=scripts_list,
      packages=packs,
      package_data={'oda_integral_wrapper': ['config_dir/*']},
      include_package_data=True,
      install_requires=[
                        "astropy",
                        "matplotlib",
                        "numpy",
                        "oda_api",
                        "requests",
                        "astroquery",
                        "nlopt",
                        "autologging",
                        "PyYAML",
                        "pymosaic_fits",
                        "pluggy>=1.5.0"
                    ],
    entry_points={
    'console_scripts': [
        'group_spectrum_adaptively.py = oda_integral_wrapper.wrapper:group_spectrum_adaptively',
    ],
},
      python_requires='>=3.8',
      )
