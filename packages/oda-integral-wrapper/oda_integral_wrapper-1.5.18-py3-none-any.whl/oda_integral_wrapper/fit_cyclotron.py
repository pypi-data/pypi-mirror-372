#!/usr/bin/env python
# coding: utf-8

# In[24]:

from autologging import logged

__author__ = "Carlo Ferrigno"

__all__ = ['FitCyclotron']

from astropy.io import fits
from astroquery.simbad import Simbad
from astropy import coordinates as coord
from astropy import units as u
import os
import numpy as np
from glob import glob
from astropy.io import fits
from IPython.display import Image
from IPython.display import display
import xspec
import shutil
import oda_api.api
import oda_api.token
from astropy import table
import json
import re
import time


import sys
# lib_path = os.path.abspath("/home/ferrigno/Soft/pysas")
# if lib_path not in sys.path:
#     sys.path.append(lib_path)
# else:
#     fit_cyclotron._log.info("Not appending")

import pyxmmsas
from astropy.table import Table
import corner
import matplotlib.pyplot as plt


def write_fits_files(instrument, spectrum, source_name, output_dir, subcases_pattern,
                     in_systematic_fraction, in_jemx_systematic_fraction):
    specprod = [l for l in spectrum._p_list if l.meta_data['src_name'] == source_name]
    if len(specprod) == 0:
        return 'none', 1e20, 0, 0

    spec_fn = output_dir + "/%s_spectrum_%s_%s.fits" % (instrument, source_name.replace(' ', '_'), subcases_pattern)
    arf_fn = output_dir + "/%s_arf_%s_%s.fits" % (instrument, source_name.replace(' ', '_'), subcases_pattern)
    rmf_fn = output_dir + "/%s_rmf_%s_%s.fits" % (instrument, source_name.replace(' ', '_'), subcases_pattern)

    specprod[0].write_fits_file(spec_fn)
    specprod[1].write_fits_file(arf_fn)
    specprod[2].write_fits_file(rmf_fn)

    ff = fits.open(spec_fn, mode='update')

    ff[1].header['RESPFILE'] = rmf_fn
    ff[1].header['ANCRFILE'] = arf_fn
    mjdref = 51544.
    tstart = float(ff[1].header['TSTART']) + mjdref
    tstop = float(ff[1].header['TSTOP']) + mjdref
    times = '%.4f--%.4f' % (tstart, tstop)
    exposure = ff[1].header['EXPOSURE']
    if 'jemx' in instrument:
        ff[1].data['SYS_ERR'] = np.zeros(len(ff[1].data['SYS_ERR'])) + in_jemx_systematic_fraction
    if 'isgri' in instrument:
        ff[1].data['SYS_ERR'] = np.zeros(len(ff[1].data['SYS_ERR'])) + in_systematic_fraction

    ff.flush()
    ff.close()

    return spec_fn, tstart, tstop, exposure

@logged
def fit_cyclotron(subcases_pattern, source_name, reference_location="subcases/scw_lists", nscw=-1,
                  systematic_fraction=0.01, jemx_systematic_fraction=0.05, integral_data_rights="all-private",
                  jemx_data_rights="public",
                  osa_version="OSA11.0-dev210827.0528-37487--fullbkg", base_mod_file='mod_broad.xcm',  run_chain=True,
                  load_chain=False, plot_chains=True, plot_corners=True, sleep_time=1, just_submit=False,
                  distance=10, isgri_ignore='**-23.0,100.0-**', jemx_ignore='**-3.5,23.0-**'):



    # subcase=None
    # reference_spectrum = None
    scwlist=[]
    for subcase_scw_list in sorted(glob(reference_location+"/list*"+subcases_pattern+"*")):
        fit_cyclotron._log.info("inspecting ", subcase_scw_list)
        
        try:
            scwlist += sorted(open(subcase_scw_list).read().split())
        except: continue

    fit_cyclotron._log.info(scwlist)


    if nscw > 0:
        import random
        random.seed(0)
        scw_pick = random.sample([
                    s+"."+"001"
                    for s in list(sorted(set(scwlist)))
                    if s.endswith("0")
                ], nscw)

        scw_list_str = ",".join(scw_pick)
    else:
        scw_list_str = ",".join([s+"."+"001" for s in sorted(set(scwlist)) if s.endswith('0')])

    fit_cyclotron._log.info(scw_list_str)

    oda_api.token.decode_oda_token(oda_api.token.discover_token())
    result_table = Simbad.query_object(source_name)

    if result_table is None:
        fit_cyclotron._log.warning(f"\033[31mdid not find any Simbad results for {source_name}\033[0m")
        raise RuntimeError(f"\033[31mdid not find any Simbad results for {source_name}\033[0m")

    source_coord = coord.SkyCoord(result_table['RA'][0], result_table['DEC'][0], unit=("hourangle", "deg"))
    fit_cyclotron._log.info(result_table)

    api_file_list =  glob("api_cat_str_*.txt")
    if len(api_file_list) == 0:
        api_cat_exist = False
    else:
        fit_cyclotron._log.info('Found api catalog in file ', api_file_list[0])
        api_cat_exist = True


    if not api_cat_exist:
        fit_cyclotron._log.info("We make a mosaic to extract a catalog")
        image = disp.get_product(instrument="isgri", 
                         product="isgri_image", 
                         product_type="Real", 
                         osa_version=osa_version,
                         integral_data_rights=integral_data_rights,
                         E1_keV=30.0,
                         E2_keV=80.0,
                         scw_list=scw_list_str,
                         token=oda_api.token.discover_token())



    if not api_cat_exist:
        
        sources=image.dispatcher_catalog_1.table[image.dispatcher_catalog_1.table['significance']>=6.0]
        #source = sources[sources['src_names']==source_name]
        unique_sources=table.unique(sources, keys=['src_names'])

        unique_sources



    if not api_cat_exist:
        ##Removes new sources and adds our if not found
        FLAG=0
        torm=[]
        for ID,n in enumerate(unique_sources['src_names']):
            if(n[0:3]=='NEW'):
                torm.append(ID)
            if(n==source_name):
                FLAG=1

        unique_sources.remove_rows(torm)
        # nrows=len(unique_sources['src_names'])

        if FLAG==0:
            unique_sources.add_row((0,source_name,0,source_coord.ra.deg,source_coord.dec.deg,0,2,0,0))

        image.dispatcher_catalog_1.table = unique_sources

        api_cat = image.dispatcher_catalog_1.get_api_dictionary()
        with open(subcase_dir+"/api_cat_str_%s.txt"%(source_name.replace(' ','_').replace('+','p')),'w') as f: 
            f.write(api_cat) 

        fit_cyclotron._log.info(api_cat)





    if api_cat_exist:
        with open(api_file_list[0]) as ff:
            api_cat = json.dumps(json.load(ff), indent=4, sort_keys=True)
        fit_cyclotron._log.info(api_cat)


    def ensure_source_in_api_cat(_api_cat):
        if _api_cat is None:
            return _api_cat
            
        api_cat_dp = oda_api.data_products.ApiCatalog(json.loads(_api_cat))

        m_source = api_cat_dp.table['src_names'] == source_name
        if api_cat_dp.table['ISGRI_FLAG'][m_source] != [1]:
            fit_cyclotron._log.warning(f"WARNING: ISGRI_FLAG was not set for source of interest ({source_name}), setting to 1")

            api_cat_dp.table['ISGRI_FLAG'][m_source] = 1
            _api_cat = api_cat_dp.get_api_dictionary()
            
        if api_cat_dp.table['FLAG'][m_source] != [1]:
            fit_cyclotron._log.warning(f"WARNING: FLAG was not set for source of interest ({source_name}), setting to 1")

            api_cat_dp.table['FLAG'][m_source] = 1
            _api_cat = api_cat_dp.get_api_dictionary()
        return _api_cat

    api_cat = ensure_source_in_api_cat(api_cat)


    #disp = oda_api.api.DispatcherAPI(url="https://www.astro.unige.ch/mmoda/dispatch-data/")

    par_dict = {
    "scw_list": scw_list_str,
    "integral_data_rights": "all-private",
    "product_type": "Real",
    "selected_catalog": api_cat,
    "token": oda_api.token.discover_token(),
    'integral_data_rights': 'public'
    }

    disp_by_call = {}
    data_by_call = {}
    n_poll = 0
    instruments = ['J1', 'J2', 'II']
    while True:
        for ys in instruments:
            if ys == 'J1':
                par_dict.update({"jemx_num": "1",
                                 "osa_version": "OSA11.1", "instrument": "jemx",
                                 "product": "jemx_spectrum", 'integral_data_rights': jemx_data_rights})
            if ys == 'J2':
                par_dict.update({"jemx_num": "2",
                                 "osa_version": "OSA11.1", "instrument": "jemx",
                                 "product": "jemx_spectrum", 'integral_data_rights': jemx_data_rights})
            if ys == 'II':
                if 'jemx_num' in par_dict:
                    del par_dict['jemx_num']

                par_dict.update({
                    "instrument": "isgri",
                    "integral_data_rights": integral_data_rights,
                    "product": "isgri_spectrum",
                    "osa_version": osa_version})


            if ys not in disp_by_call:
                disp_by_call[ys] = oda_api.api.DispatcherAPI(url="https://www.astro.unige.ch/mmoda/dispatch-data/",
                                                             wait=False)
            # This is just a submission
            _disp = disp_by_call[ys]
            data = data_by_call.get(ys, None)

            if data is None and not _disp.is_failed:
                fit_cyclotron._log.debug(f"Is submitted: {_disp.is_submitted}")
                if not _disp.is_submitted:
                    data = _disp.get_product(**par_dict)
                else:
                    _disp.poll()

                data_by_call[ys] = data
                fit_cyclotron._log.debug("Is complete", _disp.is_complete)
                if not _disp.is_complete:
                    continue
                else:
                    data_by_call[ys] = _disp.get_product(**par_dict)

        fit_cyclotron._log.debug(f'n_poll: {n_poll} ')
        n_complete = len([call for call, _disp in disp_by_call.items() if _disp.is_complete])
        fit_cyclotron._log.debug(f'n_complete: {n_complete}')
        fit_cyclotron._log.debug(f"complete {float(n_complete) / len(disp_by_call)}")
        if n_complete == len(disp_by_call):
            fit_cyclotron._log.info("done!")
            break
        fit_cyclotron._log.debug("not done")
        if just_submit:
            fit_cyclotron._log.warning("This is just for submission, returning empty dictionary")
            return {}
        n_poll += 1
        time.sleep(sleep_time)

    jemx1_spectrum = data_by_call['J1']
    jemx2_spectrum = data_by_call['J2']
    isgri_spectrum = data_by_call['II']





    isgri_spec_fn, isgri_tstart, isgri_tstop, isgri_exposure = write_fits_files('isgri', isgri_spectrum, source_name,
                                                                           reference_location, subcases_pattern,
                                                                           systematic_fraction, jemx_systematic_fraction)
    jemx1_spec_fn, jemx1_tstart, jemx1_tstop, jemx1_exposure = write_fits_files('jemx1', jemx1_spectrum, source_name,
                                                                           reference_location, subcases_pattern,
                                                                           systematic_fraction, jemx_systematic_fraction)
    jemx2_spec_fn, jemx2_tstart, jemx2_tstop, jemx2_exposure = write_fits_files('jemx2', jemx2_spectrum, source_name,
                                                                           reference_location, subcases_pattern,
                                                                           systematic_fraction, jemx_systematic_fraction)
    fit_cyclotron._log.info(isgri_spec_fn)


    ignore_string=[isgri_ignore, jemx_ignore, jemx_ignore]
    if jemx1_spec_fn =='none' or jemx2_spec_fn =='none':
        ignore_string=[isgri_ignore, jemx_ignore]
    if jemx1_spec_fn == 'none' and jemx2_spec_fn == 'none':
        ignore_string = [isgri_ignore]
    if isgri_spec_fn == 'none':
        fit_cyclotron._log.warning("We have no ISGRI spectrum, skipping the fit")
        return {}

    chains = []
    fit_by_bin = {}

    mod_file = reference_location + '/' + base_mod_file
    ss = subcases_pattern

    fit_cyclotron._log.info(ss)
    outputfiles_basename = ss+"-" + base_mod_file.replace('.xcm', '').replace('mod_', '')+"-"

    chain_name, fit_res =pyxmmsas.epic_xspec_mcmc_fit(xspec, mod_file, 
                                outputfiles_basename = outputfiles_basename,
                                pn_spec = isgri_spec_fn,
                                mos1_spec = jemx1_spec_fn,
                                mos2_spec = jemx2_spec_fn, 
                                jeffreys_priors=['norm', 'nH', 'Strength', 'cutoffE', 'foldE'],
                                ignore_string=ignore_string,
                                load_chain=load_chain, perform_fit=True, set_priors=True, walkers=40, 
                                               run_chain=run_chain,
                                               compute_errors=True, save_xcm=True, statistics='chi' )
    chains.append(chain_name)

    exposure, tstart, tstop = pyxmmsas.get_spec_exp_times(isgri_spec_fn)

    fit_res.update({'times':[tstart,  tstop]})

    fluxes = []
    xspec.AllModels.calcFlux('20. 100. error 1000 68.0')
    flux1 = np.array(xspec.AllData(1).flux[0:3])
    fluxes.append(flux1)
    if jemx1_spec_fn != 'none' or jemx2_spec_fn != 'none':
        xspec.AllModels.calcFlux('3. 20. error 1000 68.0')
        flux1 = np.array(xspec.AllData(2).flux[0:3])
        fluxes.append(flux1)

    luminosity = np.sum(fluxes, axis=0) * 4 * np.pi * (distance * u.kpc.to(u.cm)) ** 2
    fit_res.update({'luminosity': luminosity})
    fit_by_bin.update({ss: fit_res})


    for i, chain_name in enumerate(chains):

        fit_cyclotron._log.info(chain_name)
        obsid = re.findall(r"\d{4}", chain_name)[0]+'-cut-'

        table_chain = Table.read(chain_name)
        chain_df = table_chain.to_pandas()

        if plot_chains:
            for kk in table_chain.keys():
                if kk != 'FIT_STATISTIC':
                    continue
                ff = plt.figure()
                plt.plot(table_chain[kk], 'o')
                ax = ff.gca()
                ax.set_ylabel(kk)


        chain_par_names=table_chain.keys()

        to_drop = ['FIT_STATISTIC']

        for kk in chain_par_names:
            if 'factor' in kk:
                to_drop.append(kk)

        for kk in to_drop:
            chain_df.drop(kk, 1,  inplace=True)

        labels = [kk for kk in list(chain_df.columns) ]

        if plot_corners:
            corner_plot = corner.corner(chain_df, bins=20,  quantiles=[0.16,0.84], labels=labels )
            corner_plot.savefig(chain_name.replace('.fits','')+'_corner_%s.pdf'%obsid)

        quantiles = chain_df.quantile([0.16,0.5,0.84], axis=0)
        fit_cyclotron._log.info(quantiles)

    fit_result = fit_by_bin
    cyclotron_energy = []
    for ii,kk in fit_by_bin[subcases_pattern].items():
        if 'LineE__' in kk:
            cyclotron_energy.append(ii)
    tstart = min(isgri_tstart, jemx1_tstart, jemx2_tstart)
    tstop = max(isgri_tstop, jemx1_tstop, jemx2_tstop)
    exposures = [isgri_exposure, jemx1_exposure, jemx2_exposure]


    with open('res_%s.txt' % subcases_pattern, 'w') as f:
        out_str = '%.5f %.5f ' % ((tstop+tstart)/2, (tstop-tstart)/2)
        out_str += "%.4g %.4g %.4g " % (luminosity[0], luminosity[1]-luminosity[0], luminosity[2]-luminosity[0])
        for kk, ii in fit_by_bin[subcases_pattern].items():
            if 'LineE__' in kk:
                out_str += "%.3f %.3f %.3f " % (ii[0], ii[1]-ii[0], ii[2]-ii[0])
        f.write('%s' % out_str)

    res = {'fit_result':  fit_result,
            'cyclotron_energy': cyclotron_energy,
            'tstart': tstart,
            'tstop': tstop,
            'exposures': exposures}
    return res
