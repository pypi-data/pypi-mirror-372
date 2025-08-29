import copy

import astropy.wcs as wcs
import oda_api.data_products
import oda_integral_wrapper.helper_functions as helper_functions
import matplotlib
import matplotlib.pylab as plt
import numpy as np
import oda_api.gallery_api
import requests
from astropy import table
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from autologging import logged
import json
import re
import hashlib
import yaml
import os

__author__ = "Carlo Ferrigno"

__all__ = ['INTEGRALwrapper']

# Hopefully, this is stable enough
oda_public_host = 'https://www.astro.unige.ch/mmoda/dispatch-data'


@logged
class INTEGRALwrapper(object):

    # we assume that:
    # - product is compatible with oda_api
    # - the list of science windows can be ordered

    def __init__(self, host_type='production', token=None, 
                 integral_data_rights='public'):

        self.product = 'None'
        self.token = token
        self.integral_data_rights = integral_data_rights

        host = oda_public_host

        if host_type == 'staging-1-3':
            host = 'http://in.internal.odahub.io/staging-1-3/dispatcher'

        if host_type == 'staging-1-2':
            host = 'http://cdcihn.isdc.unige.ch/staging-1.2/dispatcher'

        if host_type == 'staging':
            # host = 'https://frontend-staging.obsuks1.unige.ch/mmoda/dispatch-data'
            host = 'https://dispatcher-staging.obsuks1.unige.ch/'

        if host_type == 'test':
            host = 'http://cdciweb01.isdc.unige.ch:8084/astrooda'
        
        if host_type.lower() == 'esa':
            host = 'http://mmoda-dispatcher.scikubepre.ebe.lan'

        dispatcher_function = oda_api.gallery_api.GalleryDispatcherAPI
        if token is not None:
            # the None token is not handled by the dispatcher
            try:
                self.disp = dispatcher_function(url=host, token=self.token,
                                                instrument='mock')
                # self.disp.get_instrument_description(instrument)
            except Exception:
                try:
                    self.disp = dispatcher_function(url=host, token=self.token,
                                                    instrument='mock')
                    # self.disp.get_instrument_description(instrument)
                except Exception as ee:
                    raise ConnectionError(ee)

    def long_scw_list_call(self, in_total_scw_list, s_max=50, wait=True,
                           sleep_time=10,
                           compute_fluxes=False, save_partial_products=False,
                           session_id_obj=None,
                           **arguments):
        """
        Wraps a long list call to oda_api and sums/stitches results
        :param in_total_scw_list: a list of science windows to elaborate e.g. ['084600340010.001', '084600350010.001']
        :param s_max: if >1 it defines the size of each single submissions to oda_api, if it is <0, it groups by number
                      of revolutions
        :param wait: leave it true for expected behavior
        :param sleep_time: sleeping between retries
        :param compute_fluxes: if fluxes are computed for the catalog, beware, very slow for many sources !
        :param save_partial_products: save products of single calls (just for images, for now)
        :param arguments: the actual oda_api arguments
        :return:
        """
        import time
        total_scw_list = sorted(in_total_scw_list)
        
        def get_revs(loc_scw_list):
            return np.array(sorted(list(set([int(a[0:4]) for a in loc_scw_list]))))
        self.product = arguments['product']
        local_arguments = arguments.copy()

        if s_max > 1:
            if len(total_scw_list) > s_max:
                ind_max = int(len(total_scw_list) / s_max)
                scw_lists = [total_scw_list[i * s_max:(i + 1) * s_max] for i in range(ind_max)]
                if ind_max * s_max < len(total_scw_list):
                    scw_lists.append(total_scw_list[ind_max * s_max:])
            else:
                scw_lists = [total_scw_list]
        else:
            scw_lists = []
            all_revs = get_revs(total_scw_list)
            for rev in all_revs:
                new_scwlist = [s for s in total_scw_list if s.startswith("%04d" % rev)]
                self.__log.debug(new_scwlist)
                scw_lists.append(new_scwlist)
            # by group of revolutions
            if s_max < -1:
                i = 0
                new_scw_lists = []
                while (i < len(scw_lists) / np.abs(s_max)):
                    local_lists = [ll for ll in
                                   scw_lists[i * np.abs(s_max):min(len(scw_lists), (i + 1) * np.abs(s_max))]]
                    local_element = []
                    for ss in local_lists:
                        for kk in ss:
                            local_element.append(kk)
                    new_scw_lists.append(local_element)
                    i += 1
                scw_lists = new_scw_lists
            self.__log.info("There will be %s jobs" % len(scw_lists))
            for i, ss in enumerate(scw_lists):
                self.__log.debug(i, ss[0])

        self.all_data = []
        tot_num = 0

        disp_by_call = {}
        data_by_call = {}
        n_poll = 0
        while True:
            for n_call, scw_list in enumerate(scw_lists):
                if n_poll == 0:
                    self.__log.info("At call %d of %d, we elaborate %d scw" % (n_call+1, len(scw_lists), len(scw_list)))
                    self.__log.info("From %s to %s" % (scw_list[0],
                                                       scw_list[-1]))
                    tot_num += len(scw_list)

                ys = "%06d" % n_call

                if ys not in disp_by_call:
                    disp_by_call[ys] = oda_api.gallery_api.GalleryDispatcherAPI(url=self.disp.url, wait=False,
                                                                                token=self.token)
                    # This is just a submission

                _disp = disp_by_call[ys]
                data = data_by_call.get(ys, None)

                hash_args_dict = json.dumps({**arguments, **{'scw_list': scw_list}}, sort_keys=True)
                hash_obj = hashlib.sha256(hash_args_dict.encode()).hexdigest()
                if session_id_obj is not None and isinstance(session_id_obj, dict):
                    if hash_obj in session_id_obj:
                        _disp._session_id = session_id_obj[hash_obj]
                        self.__log.debug(f"_session_id of _disp, before get_product/poll, is: {session_id_obj[hash_obj]}")

                self.__log.debug(f'\n\n\nn_call {n_call}\nData {data}\nIs failed {_disp.is_failed}')
                if data is None and not _disp.is_failed:
                    revs = get_revs(scw_list)
                    self.__log.debug(f"min rev {revs.min()}")
                    local_arguments['osa_version'] = arguments['osa_version']

                    # Add Token to arguments if not present
                    if self.token is not None and self.token != '' and 'token' not in arguments:
                        local_arguments.update({'token': self.token})
                        self.__log.debug("Inserted token in local arguments")
                    else:
                        self.__log.debug("token present in  input arguments or not defined")
                    # Add integral data rights to arguments if not present
                    if 'integral_data_rights' not in arguments:
                        local_arguments.update({'integral_data_rights': self.integral_data_rights})
                        self.__log.debug("Inserted integral_data_rights in local arguments")
                    else:
                        self.__log.debug("integral_data_rights present in  input arguments")

                    scw_list_str = ",".join([s for s in sorted(set(scw_list))])
                    self.__log.debug(f"Is submitted: {_disp.is_submitted}")
                    n_max_tries = 3
                    n_tries_left = n_max_tries
                    while True:
                        try:
                            if not _disp.is_submitted:
                                # print('list', type(scw_list_str))
                                # for kk in local_arguments:
                                #     print(kk, type(kk), local_arguments[kk])
                                print('par_dict = {')
                                for kk in local_arguments:
                                    print(f'"{kk}" : "{local_arguments[kk]}",')
                                print('"scw_list" : [')
                                for ss in scw_list:
                                    print(f'"{ss}",')
                                print("] }")

                                _disp_session_id = getattr(_disp, '_session_id', None)
                                _disp_job_id = getattr(_disp, 'job_id', None)
                                self.__log.debug(f"_session_id of _disp, right before get_product, is: {_disp_session_id} and job_id is {_disp_job_id}")
                                data = _disp.get_product(scw_list=scw_list_str, **local_arguments)
                                break
                            else:
                                _disp.poll()
                                break
                        except Exception as e:
                            self.__log.error(f"Exception while calling get_product or poll:\n{e}")
                            if 'Failed to acquire lock for directory' in str(e):
                                n_tries_left -= 1
                                if n_tries_left == 0:
                                    raise e
                                else:
                                    self.__log.error(f"Will re-attempt the request {n_tries_left} times")
                            else:
                                raise e

                    _disp_session_id = getattr(_disp, '_session_id', None)
                    _disp_job_id = getattr(_disp, 'job_id', None)
                    self.__log.debug(f"_session_id of _disp, after get_product/poll, is: {_disp_session_id} and job_id is {_disp_job_id}")
                    if session_id_obj is not None and isinstance(session_id_obj, dict):
                        if hash_obj not in session_id_obj:
                            session_id_obj[hash_obj] = _disp_session_id

                    data_by_call[ys] = data
                    self.__log.debug("Is complete %s", _disp.is_complete)
                    if not _disp.is_complete:
                        continue
                    else:
                        data_by_call[ys] = _disp.get_product(scw_list=scw_list_str, **local_arguments)

                    _disp_session_id = getattr(_disp, '_session_id', None)
                    _disp_job_id = getattr(_disp, 'job_id', None)
                    self.__log.debug(f"_session_id of _disp, after get_product/poll when it's done, is: {_disp_session_id} and job_id is {_disp_job_id}")

            self.__log.debug(f'n_poll: {n_poll} ')
            n_complete = len([call for call, _disp in disp_by_call.items() if _disp.is_complete])
            self.__log.debug(f'n_complete: {n_complete}')
            self.__log.debug(f"complete {float(n_complete) / len(disp_by_call)}")
            if n_complete == len(disp_by_call):
                self.__log.info("done!")
                break
            self.__log.debug("not done")
            n_poll += 1

            if not wait:
                return None
            time.sleep(sleep_time)

        loc_keys = data_by_call.keys()

        for kk in sorted(loc_keys):
            self.__log.debug(kk)
            self.all_data.append(data_by_call[kk])

        self.__log.debug(f'{len(total_scw_list)}, {tot_num}')

        if 'spectrum' in self.product:
            return self.sum_spectra()

        if 'lc' in self.product:
            return self.stitch_lc()

        if 'ima' in self.product:
            additional_paramters = {}
            for key in ['detection_threshold', 'projection']:
                if key in arguments.keys():
                    additional_paramters.update({key: arguments[key]})
            try:
                ret_value = self.combine_mosaics(save_partial_products=save_partial_products,
                                                 compute_fluxes=compute_fluxes,
                                                 **additional_paramters)
            except Exception as ee:
                self.__log.warning(ee)
                self.__log.warning("did not manage to combine mosaics, returning the full list of mosaics")
                ret_value = self.all_data

            return ret_value

        return self.all_data
    
    @staticmethod
    def get_oda_catalog_from_region_string(region):
        
        from oda_integral_wrapper import catalog
        
        names = []
        ras = []
        decs = []
        
        lines = region.split('\n')
        for ll in lines:
            if 'text' in ll and 'circle' in ll:
                coords = ll[ll.find("(")+1:ll.find(")")].split(',')
                ras.append(coords[0])
                decs.append(coords[1])
                name = ll[ll.find("{")+1:ll.find("}")].strip()
                names.append(name)
                   
        n_sources = len(names)
        oda_catalog = catalog.BasicCatalog(names, 
                                            ras,
                                            decs,
                                            significance=np.zeros(n_sources),
                                            frame="fk5", unit='deg')
        oda_catalog.add_column(data=np.zeros(n_sources), name='NEW_SOURCE')
        oda_catalog.add_column(data=np.ones(n_sources), name='ISGRI_FLAG', dtype=int)
        oda_catalog.add_column(data=np.zeros(n_sources), name='FLAG', dtype=int)
        oda_catalog.add_column(data=np.zeros(n_sources), name='ERR_RAD', dtype=float)

        return oda_catalog.get_dictionary()

    def load_spectra_from_fits(self, list_spec, list_rmf, list_arf):
        """It loads spectra ARFs anf RMF from the corresponding fits files

        Args:
            list_spec (list): the list of spectrum file names
            list_rmf (list): the list of RMF file names
            list_arf (list): the list of ARF file names
        """   
        class DummyClass():
            # Dummy class to reproduce INTEGRAL plugin formatting partially
            _p_list = None
            _n_list = 3
            
            def __init__(self, p_list):
                self._p_list = p_list
        
        if len(list_spec) != len(list_rmf) or len(list_spec) != len(list_rmf):
            raise Exception('The list of spectra and RMF or ARF have different sizes, cannot combine them')
        
        spec_fname = list_spec[0]
        spec = fits.open(spec_fname)
        header = spec[1].header
        detnam_0 = header.get('DETNAM', 'none')
        detchans_0 = header.get('DETCHANS', 256)
        source_0 = header.get('SOURCEID', 'none')
        spec.close()
        self.__log.info(f'Accumulating spectra for {source_0} using {detnam_0} with {detchans_0} channels')
        self.all_data = []
        for spec_fname, rmf_fname, arf_fname in zip(list_spec, list_rmf, list_arf):
            data_product_spec = oda_api.data_products.NumpyDataProduct.from_fits_file(spec_fname)
            data_product_rmf = oda_api.data_products.NumpyDataProduct.from_fits_file(rmf_fname)
            data_product_arf = oda_api.data_products.NumpyDataProduct.from_fits_file(arf_fname)
            
            spec = data_product_spec.to_fits_hdu_list()
            header = spec[1].header
            detnam = header.get('DETNAM', 'none')
            detchans = header.get('DETCHANS', 256)
            source = header.get('NAME', 'none')
            tfirst = header.get('TSTART', 0)
            
            # Add attributes to the data product class
            data_product_spec.meta_data = {
                'product': f'{detnam}_spectrum',
                'instrument': detnam,
                'src_name': source
                }
            data_product_rmf.meta_data = {
                'product': f'{detnam}_rmf',
                'instrument': detnam,
                'src_name': source
                }
            data_product_arf.meta_data = {
                'product': f'{detnam}_arf',
                'instrument': detnam,
                'src_name': source
                }
            data_product_spec.name = f'{detnam}_spectrum'
            data_product_rmf.name = f'{detnam}_rmf'
            data_product_arf.name = f'{detnam}_arf'
            
            if detnam == detnam_0 and detchans == detchans_0 and source == source_0:
                # Order of the list is assumed to be this one
                dummy_class = DummyClass([data_product_spec, data_product_arf, data_product_rmf])
                self.all_data.append(dummy_class)
                self.__log.info(f'Appending {spec_fname} with TSTART {tfirst}')
            else:
                self.__log.warning(f'Skipping {spec_fname}: source {source} using {detnam} with {detchans} channels')

    def load_light_curves_from_fits(self, list_lc):
        """It loads light curves from a list of fits file names

        Args:
            list_lc (list): list of light curve names to load
        """        
        class DummyClass():
            # Dummy class to reproduce INTEGRAL plugin formatting partially
            _p_list = None
            _n_list = 1
            
            def __init__(self, p_list):
                self._p_list = p_list
        
        lc_fname = list_lc[0]
        lc = fits.open(lc_fname)
        header = lc[1].header
        detnam_0 = header.get('DETNAM', 'none')
        if detnam_0 == 'none':
            detnam_0 = header.get('INSTRUME', 'none')
        e_min_0 = header.get('E_MIN', 75)
        e_max_0 = header.get('E_MAX', 2000)
        source_0 = header.get('SOURCEID', 'none')
        timedel_0 = header.get('TINEDEL', 0)
        if source_0 == 'none':
            source_0 = header.get('NAME', 'none')
        lc.close()
        self.__log.info(f'Accumulating light curves for {source_0} using {detnam_0} between {e_min_0} and {e_max_0} keV')
        self.all_data = []
        for lc_fname in list_lc:
            data_product = oda_api.data_products.NumpyDataProduct.from_fits_file(lc_fname)
            
            lc = data_product.to_fits_hdu_list()
            header = lc[1].header
            detnam = header.get('DETNAM', 'none')
            if detnam == 'none':
                detnam = header.get('INSTRUME', 'none')
            e_min = header.get('E_MIN', 75.)
            e_max = header.get('E_MAX', 2000.)
            source = header.get('SOURCEID', 'none')
            if source == 'none':
                source = header.get('NAME', 'none')
            tfirst = header.get('TFIRST', 0)
            timedel = header.get('TINEDEL', 0)

            # Add attributes to the data product class
            data_product.meta_data = {
                'product': f'{detnam}_lc',
                'instrument': detnam, 
                'src_name': source
                }
            data_product.name = f'{detnam}_lc'
            
            if detnam == detnam_0 and e_min == e_min_0 and e_max == e_max_0 \
               and source == source_0 and timedel == timedel_0:
                dummy_class = DummyClass([data_product])
                self.all_data.append(dummy_class)
                self.__log.info(f'Appending {lc_fname} with tfirst {tfirst}')
            else:
                self.__log.warning(f'Skipping {lc_fname}: source {source}' +
                                   f'using {detnam} between {e_min} ' +
                                   f'and {e_max} keV' +
                                   f'{timedel*86400} s resolution')

    def load_mosaics_and_catalogs(self, list_mosaics, list_catalogs,
                                  from_gallery=False, in_instrument='isgri'):
        """Loads mosaics from a collection of fits files and catalogs

        Args:
            list_mosaics (list): the list of mosaic file names (or URLs)
            list_catalogs (list): the list of catalogs 
            from_gallery (bool, optional): if False, it assumes the catalogs are text files with 
                                            csutom format, if True a set of URL of region files. Defaults to False.
            in_instrument (str, optional): The used instrument. Defaults to 'isgri'.

        Returns:
            _type_: _description_
        """        
        import json
        from urllib.request import urlopen
        self.all_data = []
        if len(list_mosaics) != len(list_catalogs):
            self.__log.error("Size of lists of mosaics is different from catalog")
            return None

        for mosaic, api_file in zip(list_mosaics, list_catalogs):
            self.__log.info("%s %s" % (mosaic, api_file))
            ff = fits.open(mosaic)
            data_units = [oda_api.data_products.NumpyDataUnit.from_fits_hdu(hh) for hh in ff]
            mosaic_image_0_mosaic = oda_api.data_products.NumpyDataProduct(data_units, name='mosaic_image')
            # print(ff[2].header)
            try:
                instrument = ff[2].header['DETNAM'].lower()
            except Exception as ee:
                self.__log.debug(ee)
                instrument = in_instrument

            data_product = instrument+'_image'
            ff.close()
            if from_gallery:
                region = urlopen(api_file).read().decode('utf-8')
                api_cat = INTEGRALwrapper.get_oda_catalog_from_region_string(region)
                self.__log.debug(api_cat)
            else:
                with open(api_file) as f:
                    api_cat_file = f.readlines()
                api_cat = json.loads(api_cat_file[0])
            
            api_catalog = oda_api.data_products.ApiCatalog(api_cat, name='dispatcher_catalog')
                
            data_collection = oda_api.api.DataCollection([mosaic_image_0_mosaic, api_catalog], instrument=instrument,
                                                            product=data_product)

            self.all_data.append(data_collection)

    def combine_mosaics(self, projection='first',
                        detection_threshold=6., compute_fluxes=False, 
                        save_partial_products=False):
        import copy
        summed_data = copy.deepcopy(self.all_data[0])
        import mosaic
        from astropy import table
        import oda_api.data_products

        if save_partial_products:
            for i, data in enumerate(self.all_data):
                if hasattr(data, 'mosaic_image_0_mosaic'):
                    data.mosaic_image_0_mosaic.write_fits_file('mosaic_%03d.fits' % i, overwrite=True)
                else:
                    data.mosaic_image_0.write_fits_file('mosaic_%03d.fits' % i, 
                                                        overwrite=True)
                api_cat_str = INTEGRALwrapper.extract_catalog_string_from_image(data, det_sigma=detection_threshold,
                                                                     update_catalog=False, include_new_sources=True)
                with open('api_cat_str_%03d.txt' % i, 'w') as f:
                    f.write(api_cat_str)

        if len(self.all_data) == 1:
            self.__log.info("We have one mosaic, returning it.")
            return self.all_data[0]
        if hasattr(self.all_data[0], 'mosaic_image_0_mosaic'):
            list_hdus = [dd.mosaic_image_0_mosaic.to_fits_hdu_list() for dd in self.all_data]
        else:
            list_hdus = [dd.mosaic_image_0.to_fits_hdu_list() for dd in self.all_data]
        # Performs the sum !
        summed_mosaic = mosaic.mosaic_list(list_hdus, pixels=projection, 
                                           mock=False)

        sources = []
        for dd in self.all_data:
            tab = dd.dispatcher_catalog_1.table
            if len(tab) > 0:
                ind = (tab['significance'] >= detection_threshold) & (tab['ISGRI_FLAG'] > 0)
                if np.sum(ind) > 0:
                    sources.append(tab[ind])

        # If there are new sources, the type is 'object', we need to replace it
        for ss in sources:
            ss.replace_column('ERR_RAD', ss.columns['ERR_RAD'].astype(np.float64))

        # We stack the table but take just the first occurrence of each source
        if len(sources) > 0:
            stacked_table_known = table.unique(table.vstack(sources, join_type='outer'), keys='src_names')
        else:
            stacked_table_known = None
            self.__log.warning("No sources satisfy the criterion for filtering")

        new_sources = []

        for dd in self.all_data:
            tab = dd.dispatcher_catalog_1.table
            if len(tab) > 0:
                ind = np.logical_and(tab['significance'] >= detection_threshold, tab['ISGRI_FLAG'] == 0)
                if np.sum(ind) > 0:
                    new_sources.append(tab[ind])

        n_new = 1
        for ss in new_sources:
            ss.replace_column('ERR_RAD', ss.columns['ERR_RAD'].astype(np.float64))
            ss.replace_column('src_names', ss.columns['src_names'].astype(np.dtype('U6')))
            for row in ss:
                row['src_names'] = 'NEW_%02d' % n_new
                row['ERR_RAD'] = -1
                n_new += 1

            # We stack the table but take just the first occurrence of each source
        if len(new_sources) > 0:
            stacked_table_new = table.unique(table.vstack(new_sources, join_type='outer'), keys='ra')
        else:
            stacked_table_new = None
            self.__log.warning("No new sources satisfy the criterion for filtering")

        self.__log.debug(new_sources)
        self.__log.debug(stacked_table_new)
        
        if stacked_table_new is not None and stacked_table_known is not None:
            stacked_table = table.unique(table.vstack([stacked_table_new] + [stacked_table_known], join_type='outer'),
                                         keys='src_names')
        elif stacked_table_new is None and stacked_table_known is not None:
            stacked_table = stacked_table_known
        elif stacked_table_new is not None and stacked_table_known is None:
            stacked_table = stacked_table_new
        else:
            stacked_table = None
        if stacked_table is not None:
            idx_f, idx_s = find_duplicates(stacked_table)

            if idx_f is None:
                self.__log.info("No duplicates in final catalog")
            else:
                self.__log.info("Removing %d duplicates" % len(idx_f))
                stacked_table.remove_rows(idx_s)

            summed_data.dispatcher_catalog_1.table = stacked_table
        if hasattr(summed_data, 'mosaic_image_0_mosaic'):
            summed_data.mosaic_image_0_mosaic.data_unit = summed_data.mosaic_image_0_mosaic.data_unit[0:1] + \
                                                      [oda_api.data_products.NumpyDataUnit.from_fits_hdu(hh) for hh in
                                                       summed_mosaic.to_hdu_list()[1:]
                                                       if hh.header['IMATYPE'] != 'NIMAGE']
        else:
            summed_data.mosaic_image_0.data_unit = summed_data.mosaic_image_0.data_unit[0:1] + \
                                                      [oda_api.data_products.NumpyDataUnit.from_fits_hdu(hh) for hh in
                                                       summed_mosaic.to_hdu_list()[1:]
                                                       if hh.header['IMATYPE'] != 'NIMAGE']
        if compute_fluxes:
            summed_data.dispatcher_catalog_1.table = INTEGRALwrapper.compute_fluxes(summed_data, detection_threshold)
        INTEGRALwrapper.display_sources(summed_data.dispatcher_catalog_1.table, detection_threshold)
        self.summed_data = summed_data

        return summed_data

    @staticmethod
    def clean_source_title(source_title):
        return re.sub(r'[\W]+', '_', source_title)

    keys_to_clean = [        
            't1', 't2', 'isgri_raw_mosaic', 'jemx1_raw_mosaic',
            'isgri_request_product_id', 'isgri_raw_sources',
            'isgri_mosaic', 'isgri_sources', 'jemx1_request_product_id', 
            'jemx1_raw_sources', 'jemx1_mosaic', 'jemx1_sources', 
            'jemx2_request_product_id', 'jemx1_raw_mosaic'
            'jemx2_raw_sources', 'jemx2_mosaic', 'jemx2_sources','jemx2_raw_mosaic',
            'isgri_gallery_object', 'jemx1_gallery_object', 'jemx2_gallery_object',
            'isgri_spectra', 'jemx1_spectra', 'jemx2_spectra',
            'isgri_mosaic', 'isgri_sources', 'jemx1_request_product_id', 
            'isgri_lc', 'jemx1_lc', 'jemx2_lc', 

            'isgri_img_fn', 'isgri_raw_sources',
            'isgri_sources', "isgri_fluxed_catalog", 'isgri_myhash', 
            'isgri_sextractor_fname', 'isgri_region_file_name', 'isgri_outfile_name',
            
            'jemx1_img_fn', 'jemx1_raw_sources',
            'jemx1_sources', "jemx1_fluxed_catalog", 'jemx1_myhash', 
            'jemx1_sextractor_fname', 'jemx1_region_file_name', 'jemx1_outfile_name',
            
            'jemx2_img_fn', 'jemx2_raw_sources',
            'jemx2_sources', "jemx2_fluxed_catalog", 'jemx2_myhash', 
            'jemx2_sextractor_fname', 'jemx2_region_file_name', 'jemx2_outfile_name',
            ]

    @staticmethod
    def clean_and_update_observations(observations, keys_to_clean=keys_to_clean, addional_keys_toclean=[],
                                      dictionary_to_update={}):
        """It cleans and updates the list of dictionaries for the observations

        Args:
            observations (_type_): the list of observation dictionaries
            keys_to_clean (_type_, optional): the basic list of keyword to remove from 
                                              observation dictionaries. Defaults to keys_to_clean (see below).
            addional_keys_toclean (list, optional): Keys to be added to the list of keys to clean 
                                            (useful if you need a quick addition) . Defaults to [].
            dictionary_to_update (dict, optional): A dctiories of keys and values to update into dictionaries. Defaults to {}.

        Returns:
            _type_: a copy of the original list of dictionaries with updated values.

            keys_to_clean = [        
            't1', 't2', 'isgri_raw_mosaic', 'jemx1_raw_mosaic',
            'isgri_request_product_id', 'isgri_raw_sources',
            'isgri_mosaic', 'isgri_sources', 'jemx1_request_product_id', 
            'jemx1_raw_sources', 'jemx1_mosaic', 'jemx1_sources', 
            'jemx2_request_product_id', 'jemx1_raw_mosaic'
            'jemx2_raw_sources', 'jemx2_mosaic', 'jemx2_sources','jemx2_raw_mosaic',
            'isgri_gallery_object', 'jemx1_gallery_object', 'jemx2_gallery_object',
            'isgri_spectra', 'jemx1_spectra', 'jemx2_spectra',
            'isgri_mosaic', 'isgri_sources', 'jemx1_request_product_id', 
            'isgri_lc', 'jemx1_lc', 'jemx2_lc', 

            'isgri_img_fn', 'isgri_raw_sources',
            'isgri_sources', "isgri_fluxed_catalog", 'isgri_myhash', 
            'isgri_sextractor_fname', 'isgri_region_file_name', 'isgri_outfile_name',
            
            'jemx1_img_fn', 'jemx1_raw_sources',
            'jemx1_sources', "jemx1_fluxed_catalog", 'jemx1_myhash', 
            'jemx1_sextractor_fname', 'jemx1_region_file_name', 'jemx1_outfile_name',
            
            'jemx2_img_fn', 'jemx2_raw_sources',
            'jemx2_sources', "jemx2_fluxed_catalog", 'jemx2_myhash', 
            'jemx2_sextractor_fname', 'jemx2_region_file_name', 'jemx2_outfile_name',
            ]
        """                                        
        
        copied_observations = copy.deepcopy(observations)
        
        local_keys_to_clean = keys_to_clean + addional_keys_toclean

        for oo in copied_observations:
            for k, v in dictionary_to_update.items():
                oo.update({k: v})
            for kk in local_keys_to_clean:
                if kk in oo.keys():
                    del oo[kk]
        
        return copied_observations

    @staticmethod
    def display_sources(stacked_table, min_sigma):
        if stacked_table is None:
            INTEGRALwrapper.__log.info("No sources to be displayed")
            return
        out_str = 'source_name RA DEC Flux Flux_err\n-----------------------------------'
        INTEGRALwrapper.__log.info(out_str)

        if 'FLUX' in stacked_table.keys():
            for ss in stacked_table:
                if ss['significance'] > min_sigma:
                    out_str = '%s %.3f %.3f %.4f %.4f' % (ss['src_names'], ss['ra'], ss['dec'], ss['FLUX'],
                                                          ss['FLUX_ERR'])
                    INTEGRALwrapper.__log.info(out_str)
        else:
            for ss in stacked_table:
                if ss['significance'] > min_sigma:
                    out_str = '%s %.3f %.3f %.4f %d' % (ss['src_names'], ss['ra'], ss['dec'], ss['significance'],
                                                        ss['FLAG'])
                    INTEGRALwrapper.__log.info(out_str)

    @staticmethod
    def get_html_from_fluxes(fluxed_catalog,
                             columns_to_remove=['meta_ID', 'NEW_SOURCE', 'ISGRI_FLAG', 'FLAG', 'ERR_RAD'],
                             rename_dict={'src_names': 'Name',
                                          'ra': 'RA',
                                          'dec': 'Dec',
                                          'significance': 'Significance',
                                          'FLUX_ERR': 'Uncertainty (1&sigma;, cts/s)',
                                          'FLUX': 'Flux (cts/s)'},
                             htmldict={
                                 'table_class': 'm-3 table table-responsive'
                             },
                             substitute_dict={
                                 '<thead>': '<thead class="table-dark">',
                                 'amp;': ''
                             },
                             output_file='none'
                             ):
        '''
        Write an HTML table from table of sources with fluxes
        :param fluxed_catalog: output of  compute_fluxes function (It assuumes that fluxes are in column FLUX and error in column FLUX_ERR)
        :param columns_to_remove:
        :param rename_dict: a dictionary with the input column names and the output column titles in the html table
        :param htmldict: classes for html output
        :param substitute_dict: a disctionary of strings to substitute into the html table
        :param output_file: writes output also in file (none skips)
        :return: the HTML table as string
        '''

        INTEGRALwrapper.__log.debug(fluxed_catalog)

        if fluxed_catalog is None or 'FLUX' not in fluxed_catalog.colnames:
            INTEGRALwrapper.__log.warning('get_html_from_fluxes :: input table is None, returning \'\'')
            return ''
        copy_tab = fluxed_catalog.copy()

        from astropy.io.ascii import HTML

        for cc in columns_to_remove:
            if cc in copy_tab.columns:
                copy_tab.remove_column(cc)

        for ii in rename_dict.items():
            copy_tab.rename_column(ii[0], ii[1])

        # Moving column at the end
        sig = copy_tab[rename_dict['significance']]
        copy_tab.remove_column(rename_dict['significance'])
        copy_tab.add_column(sig, index=6)

        # Use types for display
        copy_tab[rename_dict['ra']] = copy_tab[rename_dict['ra']].astype('S8')
        copy_tab[rename_dict['dec']] = copy_tab[rename_dict['dec']].astype('S8')
        copy_tab[rename_dict['FLUX']] = copy_tab[rename_dict['FLUX']].astype('S7')
        copy_tab[rename_dict['FLUX_ERR']] = copy_tab[rename_dict['FLUX_ERR']].astype('S7')
        copy_tab[rename_dict['significance']] = copy_tab[rename_dict['significance']].astype('S6')

        # Write the significance with one digit
        for i, s in enumerate(fluxed_catalog['significance']):
            copy_tab['Significance'][i] = '%.1f' % s

        # Use an appropriate number of significant digits
        for i, s in enumerate(zip(fluxed_catalog['FLUX'], fluxed_catalog['FLUX_ERR'])):
            if np.isfinite(s[1]) and s[1] > 0: 
                format_str = '%.' + str(1 + int(np.abs(np.floor(np.log10(s[1]))))) + 'f'
                copy_tab[rename_dict['FLUX_ERR']][i] = format_str % s[1]
            else:
                format_str = '%.1f'
                copy_tab[rename_dict['FLUX_ERR']][i] = 'N/A'

            if np.isfinite(s[0]):
                copy_tab[rename_dict['FLUX']][i] = format_str % s[0]
            else:
                copy_tab[rename_dict['FLUX']][i] = 'N/A'

        local_html = HTML(htmldict)

        list_of_str = local_html.write(copy_tab)
        for ii in substitute_dict.items():
            list_of_str[0] = list_of_str[0].replace(ii[0], ii[1])

        if output_file != 'none':
            with open(output_file, 'w') as ofile:
                ofile.write(list_of_str[0])

        list_of_str2 = list_of_str[0].split('\n ')
        out_html = '\n '.join(list_of_str2[6:-1])
        return out_html

    @staticmethod
    def compute_fluxes(summed_data, min_sigma=5, free_sigma=False,
                       free_constant=False, catalog_file=None,
                       catalog_string=None,
                       only_sources=[], ensure_sources=[]):
        """
        Copunte fluxes of sources in mosaic returned by ODA with ad-hoc function

        Args:
            summed_data (object): returned data structure
            min_sigma (int, optional): minimum sigm to onsider a source. Defaults to 5.
            free_sigma (bool, optional): if sigma needs to be left free in PSF fit. Defaults to False.
            free_constant (bool, optional): if constant should e left free in PSF fit. Defaults to False.
            catalog_file (str, optional): If present, catolg is derived by reading this file, otherwise from the string or data structure. Defaults to None.
            catalog_string (str, optional): If present, catolg is derived from this, otherwise from thefile or data structure. Defaults to None.
            only_sources (list, optional): If set, the flux is computed only for these sources. Defaults to [].
            ensure_sources (list, optional): If set, the flux is surely computed for these sources, without limit on sigma. Defaults to [].
            

        Returns:
            astropy table: table with fluxes in columns FLUX FLUX_ERR and significance
        """        

        # if not hasattr(self, 'summed_data'):
        #     raise RuntimeWarning('No summed mosaic, no computation of fluxes')
        #
        if catalog_string is None and catalog_file is None:
            stacked_table = summed_data.dispatcher_catalog_1.table
        else:
            if catalog_file is not None:
                with open(catalog_file) as f:
                    api_cat_file = f.readlines()
                api_cat = json.loads(api_cat_file[0])
            elif catalog_string is not None:
                api_cat = json.loads(catalog_string)
            else:
                raise Exception('We should not be here')

            api_catalog = oda_api.data_products.ApiCatalog(api_cat, name='dispatcher_catalog')
            stacked_table = api_catalog.table

        stacked_table = INTEGRALwrapper.add_objects_of_interest(stacked_table, only_sources)
        stacked_table = INTEGRALwrapper.add_objects_of_interest(stacked_table, ensure_sources)
        
        if len(stacked_table) == 0:
            INTEGRALwrapper.__log.warning("No sources in the catalog, impossible to compute fluxes")
            return None

        # print('STACKED TABLE **********')
        # print(stacked_table)
        # Filter sources by significance
        if 'significance' in stacked_table.colnames:
            ind = stacked_table['significance'] >= min_sigma
        else:
            ind = np.ones(len(stacked_table), dtype=bool)

        # If only sources is set get flux only for them
        for ss in only_sources:
            for i, nn in enumerate(stacked_table['src_names']):
                if ss != nn:
                    ind[i] = False
                    INTEGRALwrapper.__log.debug(ss, nn)
                else:
                    ind[i] = True
                    INTEGRALwrapper.__log.debug(ss, nn, '!!!!!!!!!!!!!!')

        # Ensure computation
        for ss in ensure_sources:
            for i, nn in enumerate(stacked_table['src_names']):
                if ss == nn:
                    ind[i] = True
                    INTEGRALwrapper.__log.debug(ss, nn)
                    # print('Found', i, ss, nn)

        stacked_table = stacked_table[ind]
        # print('STACKED TABLE **********')
        # print(stacked_table)

        cat_for_image = INTEGRALwrapper.get_source_list_from_table(stacked_table)
        # print(cat_for_image)
        INTEGRALwrapper.__log.debug(cat_for_image)
        import oda_integral_wrapper.fitimage as fitimage
        # import importlib
        # importlib.reload(fitimage)
        if hasattr(summed_data, 'mosaic_image_0_mosaic'):
            fit_image = fitimage.FitMosaicSources(summed_data.mosaic_image_0_mosaic.data_unit, cat_for_image,
                                              free_sigma=free_sigma, free_constant=free_constant)
        else:
            fit_image = fitimage.FitMosaicSources(summed_data.mosaic_image_0.data_unit, cat_for_image,
                                              free_sigma=free_sigma, free_constant=free_constant)
        
        fitted_fluxes = fit_image.get_fluxes()
        # print(fitted_fluxes)
        # print(stacked_table)

        if fitted_fluxes[0][1] is None or len(fitted_fluxes[0][0]) == 0:
            return stacked_table
        
        # print(stacked_table)
        # If some source is not in the FOV, we need to exclude it
        # something False
        ind = stacked_table['significance'] < -100

        for i in range(len(stacked_table['src_names'])):
            for j in range(len(fitted_fluxes[0][0])):
                if stacked_table['src_names'][i] == fitted_fluxes[0][0][j]:
                    ind[i] = True

        stacked_table = stacked_table[ind]
        # print(stacked_table)

        stacked_table['FLUX']= fitted_fluxes[0][1]
        # print(fitted_fluxes[0][1])
        # print(fitted_fluxes[0][2])
        stacked_table['FLUX_ERR'] = fitted_fluxes[0][2]
        stacked_table['significance'] = np.abs(np.array(fitted_fluxes[0][1]) / np.array(fitted_fluxes[0][2]))

        return stacked_table

    @staticmethod
    def write_image_fits(data, filename='mosaic.fits', extension=-1, overwrite=True):
        '''
        Writes an image (or an extension to a fits file
        :param data: data returned from oda_api or oda_integral_wrapper
        :param filename: output filename (default='mosaic.fits')
        :param extension: the extension to output, if <0 writes all images (default=-1)
        :param overwrite: default=True
        :return:
        '''
        if extension < 0:
            if hasattr(data, 'mosaic_image_0_mosaic'):    
                data.mosaic_image_0_mosaic.write_fits_file(filename, overwrite=overwrite)
            elif hasattr(data, 'mosaic_image_0'):
                data.mosaic_image_0.write_fits_file(filename, overwrite=overwrite)
            else:
                INTEGRALwrapper.__log.warning("No attribute to save image")
        else:
            fits.writeto(filename,
                         data.mosaic_image_0_mosaic.to_fits_hdu_list()[extension].data,
                         header=data.mosaic_image_0_mosaic.to_fits_hdu_list()[extension].header,
                         overwrite=overwrite)
        return

    @staticmethod
    def write_ds9_region_file(source_table, filename='ds9.reg', color='green', new_color='white', radius=240):
        '''
        Write ds9 compatible region file from a table of sources
        :param source_table: the catalog table (typycally data.dispatcher_catalog_1.table)
        :param filename: the ds9 region filename (default ds9.reg)
        :param color: color of regions (default is green)
        :param new_color: color of region for new sources (default is white)
        :param radius: radius of regions in arcseconds (default 2400, used for the gallery)
        :return: the string of regions dumped into filename
        '''
        ff = open(filename, 'w')
        out_str = 'global move=0\nglobal color=%s\n' % color
        for row in source_table:
            out_str += 'fk5;circle(%f, %f, %d\')  # text={%s}' % (row['ra'], row['dec'], radius, row['src_names'])
            if 'NEW' in row['src_names']:
                out_str += ' color=%s\n' % new_color
            else:
                out_str += '\n'
        ff.write(out_str)
        ff.close()

        return out_str

    @staticmethod
    def get_catalog_from_web(isdc_general_catalog='http://isdcarc.isdc.unige.ch/arc/rev_3/cat/hec/gnrl_refr_cat_0044.fits'):
        import oda_integral_wrapper.catalog
        ff = fits.open(isdc_general_catalog)
        isdc_sources = ff[1].data
        ff.close()
        mask = (isdc_sources['ISGRI_FLAG'] > 0) | (isdc_sources['JEMX_FLAG']>0)
        n_sources = np.sum(mask)
        oda_catalog = oda_integral_wrapper.catalog.BasicCatalog([ss.strip() for ss in isdc_sources['NAME'][mask]], 
                                            isdc_sources['RA_OBJ'][mask],
                                            isdc_sources['DEC_OBJ'][mask],
                                            significance = np.zeros(n_sources),
                                            frame="fk5", unit='deg')
        oda_catalog.add_column(data=np.zeros(n_sources), name='NEW_SOURCE')
        oda_catalog.add_column(data=isdc_sources['ISGRI_FLAG'][mask], name='ISGRI_FLAG', dtype=int)
        oda_catalog.add_column(data=np.zeros(n_sources), name='FLAG', dtype=int)
        oda_catalog.add_column(data=isdc_sources['ERR_RAD'][mask], name='ERR_RAD', dtype=float)

        return oda_catalog

    @staticmethod
    def get_catalog_from_dict(api_cat):
        from astropy.table import Table
        import oda_integral_wrapper.catalog
        meta = {}

        map_dict = {'cat_frame': 'FRAME',
                    'cat_coord_units': 'COORD_UNIT',
                    'cat_lat_name': 'LAT_NAME',
                    'cat_lon_name': 'LON_NAME'}
        for kk, ii in api_cat.items():
            if 'column' not in kk:
                meta.update({map_dict[kk] : ii})
        
        # Need to reformat with nupy updates
        descriptions = {}
        for pp in api_cat['cat_column_descr']:
            descriptions[pp[0]] = pp[1]
        
        oda_catalog_table = Table(data=api_cat['cat_column_list'], names=api_cat['cat_column_names'], 
            descriptions=descriptions, meta=meta)
        
        oda_catalog = oda_integral_wrapper.catalog.BasicCatalog.from_table(oda_catalog_table)
        
        return oda_catalog

    @staticmethod
    def get_source_list_from_table(my_table):
        src_dict = []
        for row in my_table:
            src_dict.append((row['src_names'], (row['ra'], row['dec'])))
        return src_dict

    def get_sources(self):
        sources = set()
        # It works both on collection and single instance
        try:
            for data in self.all_data:
                # print(set([l.meta_data['src_name'] for l in data._p_list]))
                sources = sources.union(set([l.meta_data['src_name'] for l in data._p_list]))
        except Exception as ee:
            self.__log.info(ee)
            sources = sources.union(set([l.meta_data['src_name'] for l in self.all_data._p_list]))

        return sources

    def stitch_lc(self):
        combined_data = copy.deepcopy(self.all_data[0])
        
        if len(combined_data._p_list) == 0:
            self.__log.warning('Light curve does not contain data !')
            return combined_data
        
        if 'lc' not in combined_data._p_list[0].name:
            raise ValueError('This is not a light curve and you try to stitch them')

        if len(self.all_data) == 1:
            return combined_data
        
        sources = self.get_sources()
        self.__log.debug(sources)
        # gets indexes of source and lc in combined data
        for source in sources:
            for j, dd in enumerate(combined_data._p_list):
                if dd.meta_data['src_name'] == source:
                    IND_src_combined = j
                    for ii, du in enumerate(dd.data_unit):
                        if 'LC' in du.name:
                            IND_lc_combined = ii
            self.__log.debug(IND_lc_combined)
            for data in self.all_data[1:]:
                for dd in data._p_list:
                    if dd.meta_data['src_name'] == source:
                        self.__log.debug('Source ' + source)
                        hdu = combined_data._p_list[IND_src_combined].data_unit[IND_lc_combined].to_fits_hdu()

                        for du in dd.data_unit:
                            self.__log.debug(f'DU name {du.name}')
                            if 'LC' in du.name:

                                self.__log.debug('Original LC size %s' % hdu.data.shape[0])

                                new_data = hdu.data.copy()
                                new_data.resize(((hdu.data.shape[0] + du.data.shape[0])))

                                for i, col in enumerate(hdu.columns):
                                    # print(col)
                                    new_data[col.name] = np.concatenate((hdu.data[col.name], du.data[col.name]))

                                hdu.data = new_data.copy()

                                hdu.header['ONTIME'] += du.header['ONTIME']
                                try:
                                    hdu.header['EXPOSURE'] += du.header['EXPOSURE']
                                    hdu.header['EXP_SRC'] += du.header['EXP_SRC']
                                except Exception as ee:
                                    self.__log.info(ee)
                                    pass

                                if du.header['TSTART'] < hdu.header['TSTART']:
                                    hdu.header['TSTART'] = du.header['TSTART']

                                if du.header['TSTOP'] > hdu.header['TSTOP']:
                                    hdu.header['TSTOP'] = du.header['TSTOP']

                                try:
                                    if du.header['TLAST'] > hdu.header['TLAST']:
                                        hdu.header['TLAST'] = du.header['TLAST']
                                except Exception as ee:
                                    self.__log.info(ee)
                                    pass

                                try:
                                    hdu.header['TELAPSE'] = hdu.header['TSTOP'] - hdu.header['TSTART']
                                except Exception as ee:
                                    self.__log.info(ee)
                                    pass

                        self.__log.debug('Stitched LC size %s' % hdu.data.shape[0])
                        combined_data._p_list[IND_src_combined].data_unit[IND_lc_combined] = du.from_fits_hdu(hdu)

        return combined_data

    @staticmethod
    def normalize_lc_ijd(combined_lc, source_name, Emin, Emax):
        new_combined_lc = copy.deepcopy(combined_lc)
        t, dt, y, dy = INTEGRALwrapper.get_lc(new_combined_lc, source_name)
        if len(t) == 0:
            return new_combined_lc
        ind = t < 5838.086367870370
        from oda_integral_wrapper.get_osa10_11_factor import get_osa10_11_conversion_factor
        f = get_osa10_11_conversion_factor(Emin, Emax)
        y[ind] /= f
        dy[ind] /= f
        INTEGRALwrapper.put_lc(new_combined_lc, source_name, t, y, dy)
        return new_combined_lc

    @staticmethod
    def put_lc(combined_lc, source_name, x, y, dy):
        # In LC name has no "-" nor "+" ??????
        patched_source_name = source_name.replace('-', ' ').replace('+', ' ')

        hdu = None
        j_index = -1
        i_index = -1
        for j, dd in enumerate(combined_lc._p_list):
            INTEGRALwrapper.__log.debug(dd.meta_data['src_name'])
            if dd.meta_data['src_name'] == source_name or dd.meta_data['src_name'] == patched_source_name:
                for ii, du in enumerate(dd.data_unit):
                    if 'LC' in du.name:
                        hdu = du.to_fits_hdu()
                        i_index = ii
                        j_index = j

        if hdu is None:
            INTEGRALwrapper.__log.info('Source ' + source_name + ' not found in lc')
            return None

        hdu.data['TIME'] = x
        hdu.data['RATE'] = y
        hdu.data['ERROR'] = dy

        combined_lc._p_list[j_index].data_unit[i_index].from_fits_hdu(hdu)

        return

    @staticmethod
    def get_lc(combined_lc, source_name, systematic_fraction=0):

        # In LC name has no "-" nor "+" ??????
        patched_source_name = source_name.replace('-', ' ').replace('+', ' ')

        hdu = None
        for j, dd in enumerate(combined_lc._p_list):
            INTEGRALwrapper.__log.debug(dd.meta_data['src_name'])
            if dd.meta_data['src_name'] == source_name or dd.meta_data['src_name'] == patched_source_name or \
                    dd.meta_data['src_name'] == 'query':  # This is for SPI-ACS
                INTEGRALwrapper.__log.debug('Selected ' + dd.meta_data['src_name'])
                for ii, du in enumerate(dd.data_unit):
                    # print('Pippa', du.name)
                    if 'LC' in du.name or 'RATE' in du.name:
                        # print('Pippo')
                        hdu = du.to_fits_hdu()

        if hdu is None:
            INTEGRALwrapper.__log.info('Source ' + source_name +
                                       ' not found in light curves.\nThe available sources are:\n')
            for l in combined_lc._p_list:
                INTEGRALwrapper.__log.warning(l.meta_data['src_name'])
            return [], [], [], []

        x = hdu.data['TIME']
        y = hdu.data['RATE']
        dy = hdu.data['ERROR']

        ind = np.argsort(x)
        x = x[ind]
        y = y[ind]
        dy = dy[ind]

        dy = np.sqrt(dy ** 2 + (y * systematic_fraction) ** 2)
        ind = np.logical_and(np.isfinite(y), np.isfinite(dy))
        ind = np.logical_and(ind, dy > 0)

        # This could only be valid for ISGRI
        try:
            dt_lc = hdu.data['XAX_E']
            INTEGRALwrapper.__log.debug('Get time bin directly from light curve')
        except Exception as ee:
            INTEGRALwrapper.__log.info(ee)
            timedel = hdu.header['TIMEDEL']
            if 'TIMEPIXR' in hdu.header:
                timepix = hdu.header['TIMEPIXR']
            else:
                timepix = 0.5
            t_lc = hdu.data['TIME'] + (0.5 - timepix) * timedel
            dt_lc = t_lc.copy() * 0.0 + timedel / 2
            for i in range(len(t_lc) - 1):
                dt_lc[i + 1] = np.fabs(min(timedel / 2, t_lc[i + 1] - t_lc[i] - dt_lc[i]))
            INTEGRALwrapper.__log.debug('Computed time bin from TIMEDEL')

        return x[ind], dt_lc[ind], y[ind], dy[ind]

    @staticmethod
    def plot_lc(combined_lc, source_name, systematic_fraction=0,
                ng_sig_limit=3, find_excesses=False):
        # if ng_sig_limit <1 does not plot range
        from scipy import stats
        x, dx, y, dy = INTEGRALwrapper.get_lc(combined_lc, source_name, 
                                              systematic_fraction)
        if len(x) == 0:
            INTEGRALwrapper.__log.debug('Light curve is empty ?')
            return None
        meany = np.sum(y / dy ** 2) / np.sum(1. / dy ** 2)
        err_mean = np.sum(1 / dy ** 2)

        std_dev = np.std(y)
        INTEGRALwrapper.__log.debug('Plotting')
        fig = plt.figure()
        _ = plt.errorbar(x, y, xerr=dx, yerr=dy, marker='o', capsize=0, 
                         linestyle='', label='Lightcurve')
        _ = plt.axhline(meany, color='green', linewidth=3)
        _ = plt.xlabel('Time [IJD]')
        _ = plt.ylabel('Rate')

        if ng_sig_limit >= 1:
            ndof = len(y) - 1
            prob_limit = stats.norm().sf(ng_sig_limit)
            chi2_limit = stats.chi2(ndof).isf(prob_limit)
            band_width = np.sqrt(chi2_limit / err_mean)
            INTEGRALwrapper.__log.debug('%g %g %g %g %g %g %g' % (
                meany, err_mean, std_dev, prob_limit, chi2_limit, band_width, ng_sig_limit))
            _ = plt.axhspan(meany - band_width, meany + band_width, color='green', alpha=0.3,
                            label=f'{ng_sig_limit} $\sigma_m$, {100 * systematic_fraction}% syst')

            _ = plt.axhspan(meany - std_dev * ng_sig_limit, meany + std_dev * ng_sig_limit,
                            color='cyan', alpha=0.3,
                            label=f'{ng_sig_limit} $\sigma_d$, {100 * systematic_fraction}% syst')

            _ = plt.legend()

        plot_title = source_name
        _ = plt.title(plot_title)
        if find_excesses:
            ind = (y - band_width) / dy > ng_sig_limit
            if np.sum(ind) > 0:
                _ = plt.plot(x[ind], y[ind], marker='x', color='red', linestyle='', markersize=10)
                INTEGRALwrapper.__log.info('We found positive excesses on the lightcurve at times')
                good_ind = np.where(ind)
                # print(good_ind[0][0:-1], good_ind[0][1:])
                old_time = -1
                if len(good_ind[0]) == 1:
                    INTEGRALwrapper.__log.info('%f' % (x[good_ind[0][0]]))
                else:
                    for i, j in zip(good_ind[0][0:-1], good_ind[0][1:]):
                        # print(i,j)
                        if j - i > 2:
                            if x[i] != old_time:
                                INTEGRALwrapper.__log.info('%f' % x[i])
                                _ = INTEGRALwrapper.plot_zoom(x, y, dy, i)
                            INTEGRALwrapper.__log.info('%f' % (x[j]))
                            _ = INTEGRALwrapper.plot_zoom(x, y, dy, j)
                        else:
                             INTEGRALwrapper.__log.info('%f' % ((x[i]+x[j])/2))

                        old_time = x[j]

        return fig

    @staticmethod
    def plot_zoom(x, y, dy, i, n_before=5, n_after=15, save_plot=True, name_base='burst_at_'):
        fig = plt.figure()
        _ = plt.errorbar(x[i - n_before:i + n_after], y[i - n_before:i + n_after], yerr=dy[i - n_before:i + n_after],
                         marker='o', capsize=0, linestyle='', label='Lightcurve')
        _ = plt.xlabel('Time [IJD]')
        _ = plt.ylabel('Rate')
        if save_plot:
            _ = plt.savefig(name_base + '%d.png' % i)
        return fig

    @staticmethod
    def extract_catalog_from_image(image, include_new_sources=False, det_sigma=5, objects_of_interest=[],
                                   flag=1, isgri_flag=2, update_catalog=False, new_source_suffix='',  isdc_ref_cat=None, separation=2.0):
        import json
        catalog_str = INTEGRALwrapper.extract_catalog_string_from_image(image, include_new_sources, det_sigma,
                                                                        objects_of_interest,
                                                                        flag, isgri_flag, update_catalog,
                                                                        new_source_suffix=new_source_suffix,
                                                                         isdc_ref_cat=isdc_ref_cat, separation=separation)
        return json.loads(catalog_str)

    @staticmethod
    def extract_catalog_table_from_image(image, det_sigma=5, objects_of_interest=[],
                                          flag=1, isgri_flag=2, new_source_suffix='' , isdc_ref_cat=None, separation=2.0):
        if image.dispatcher_catalog_1.table is None:
            INTEGRALwrapper.__log.warning("No sources in the catalog")
            if objects_of_interest != []:
                return INTEGRALwrapper.add_objects_of_interest(None, objects_of_interest,
                                                               flag, isgri_flag)
            else:
                return None
        
        return_table = image.dispatcher_catalog_1.table[image.dispatcher_catalog_1.table['significance'] >= det_sigma]

        return_table.replace_column('src_names', return_table['src_names'].astype('S64'))
        if isdc_ref_cat is not None:
            from astropy import units as u
            ref = SkyCoord(ra=isdc_ref_cat['RA_OBJ'], dec=isdc_ref_cat['DEC_OBJ'], unit=(u.deg, u.deg))
            c = SkyCoord(ra=return_table['ra'], dec=return_table['dec'], unit=(u.deg, u.deg))
            idx_self, d2d_self, d3d_self = c.match_to_catalog_sky(ref, nthneighbor=1)
            ind_first_match = np.argwhere(d2d_self.arcmin < separation).flatten()
            INTEGRALwrapper.__log.info("There are %d matches with ISDC catalog" % (len(ind_first_match)))
            if len(ind_first_match) > 0:
                # ind_first_match = ind_first_match
                for i in range(len(c)):
                    INTEGRALwrapper.__log.info("%f %s %s", d2d_self[i].arcmin, return_table['src_names'][i], isdc_ref_cat['NAME'][idx_self[i]])
                    if d2d_self[i].arcmin < separation and return_table['src_names'][i] != isdc_ref_cat['NAME'][idx_self[i]]:
                        INTEGRALwrapper.__log.info('We are changing the name of %s to %s' % (return_table['src_names'][i] , isdc_ref_cat['NAME'][idx_self[i]]))
                        return_table['src_names'][i] = isdc_ref_cat['NAME'][idx_self[i]]
        
        for i, ss in enumerate(return_table['src_names']):
            if "NEW" in ss:
                new_ss = ss + new_source_suffix
                return_table['src_names'][i] = new_ss 
                #print('Update source name '+ ss + ' ' + new_ss)

        return return_table

    @staticmethod
    def extract_catalog_string_from_image(image, include_new_sources=False, det_sigma=5, objects_of_interest=[],
                                          flag=1, isgri_flag=2, update_catalog=True, new_source_suffix='', isdc_ref_cat=None,
                                          separation=2.0):
        
        # TODO : match a new reference catalog

        # Example: objects_of_interest=['Her X-1']
        #         objects_of_interest=[('Her X-1', Simbad.query )]
        #         objects_of_interest=[('Her X-1', Skycoord )]
        #         objects_of_interest=[ Skycoord(....) ]
        sources = INTEGRALwrapper.extract_catalog_table_from_image(image, det_sigma, objects_of_interest, flag,
                                                                   isgri_flag, new_source_suffix=new_source_suffix, 
                                                                   isdc_ref_cat=isdc_ref_cat, separation=separation)

        if sources is None and objects_of_interest is None:
            return 'none'

        if sources is None and objects_of_interest is not None:
            unique_sources = INTEGRALwrapper.add_objects_of_interest(sources, objects_of_interest, flag, isgri_flag)
        else:
            if not include_new_sources and len(sources) > 0:
                ind = ['NEW' not in ss for ss in sources['src_names']]
                clean_sources = sources[ind]
                INTEGRALwrapper.__log.debug(ind)
                INTEGRALwrapper.__log.debug(sources)
                INTEGRALwrapper.__log.debug(clean_sources)
            else:
                clean_sources = sources

            unique_sources = INTEGRALwrapper.add_objects_of_interest(clean_sources, objects_of_interest,
                                                                    flag, isgri_flag)

        copied_image = copy.deepcopy(image)
        copied_image.dispatcher_catalog_1.table = unique_sources

        if update_catalog:
            image.dispatcher_catalog_1.table = unique_sources

        return copied_image.dispatcher_catalog_1.get_api_dictionary()

    @staticmethod
    def make_one_source_catalog_string(name, ra, dec, isgri_flag, flag):
        out_str_templ = '{"cat_frame": "fk5", "cat_coord_units": "deg", "cat_column_list": [[1], ["%s"], [0.0], [%f], [%f], [-32768], [%d], [%d], [0.001]], "cat_column_names": ["meta_ID", "src_names", "significance", "ra", "dec", "NEW_SOURCE", "ISGRI_FLAG", "FLAG", "ERR_RAD"], "cat_column_descr": [["meta_ID", "<i8"], ["src_names", "<U7"], ["significance", "<f8"], ["ra", "<f8"], ["dec", "<f8"], ["NEW_SOURCE", "<i8"], ["ISGRI_FLAG", "<i8"], ["FLAG", "<i8"], ["ERR_RAD", "<f8"]], "cat_lat_name": "dec", "cat_lon_name": "ra"}'
        return out_str_templ % (name, ra, dec, isgri_flag, flag)

    @staticmethod
    def add_objects_of_interest(clean_sources, objects_of_interest, flag=1, 
                                isgri_flag=2, tolerance=1. / 60.):
        """Add an object of interest to the catalog table

        Args:
            clean_sources (astropy table): The table of the clean sources
            objects_of_interest (list): list of object of interest
            flag (int, optional): catalog flag. Defaults to 1.
            isgri_flag (int, optional): isgri_flag. Defaults to 2.
            tolerance (float, optional): tolerance to add a source by coordinates (degrees). Defaults to 1./60..

        Raises:
            Exception: Generic failure

        Returns:
            astropy table: table with object of interest added.
        """

        if objects_of_interest is None:
            return clean_sources

        for ooi in objects_of_interest:
            if isinstance(ooi, tuple):
                ooi, t = ooi
                if isinstance(t, SkyCoord):
                    source_coord = t
            # elif isinstance(ooi, SkyCoord):
            #     t = Simbad.query_region(ooi)
            elif isinstance(ooi, str):
                t = helper_functions.call_simbad_query_object(ooi, logger=INTEGRALwrapper.__log)
            else:
                raise Exception("fail to elaborate object of interest")

            if isinstance(t, table.Table):
                if 'RA' in t.keys() and 'DEC' in t.keys() and \
                    t['RA'].value != '' and t['DEC'].value != '':
                    source_coord = SkyCoord(t['RA'], t['DEC'], 
                                            unit=(u.hourangle, u.deg), 
                                            frame="fk5")
                elif 'ra' in t.keys() and 'dec' in t.keys() \
                    and t['ra'].value != '' and t['dec'].value != '':
                    source_coord = SkyCoord(t['ra'], t['dec'], 
                                            unit=(u.deg, u.deg), 
                                            frame="fk5")
                else:
                    INTEGRALwrapper.__log.warning('Source coordinates cannot be found in Simbad in add_object_of_interest, skip')
                    continue
            elif isinstance(t, SkyCoord):
                INTEGRALwrapper.__log.debug('Found source coordinates')
            else:
                INTEGRALwrapper.__log.warning('Source %s cannot be found in Simbad' % ooi)
                continue

            INTEGRALwrapper.__log.info("Elaborating object of interest: %s %f %f" %
                                       (ooi, source_coord.ra.deg, source_coord.dec.deg))
            ra = source_coord.ra.deg
            dec = source_coord.dec.deg
            INTEGRALwrapper.__log.info("RA=%g Dec=%g" % (ra, dec))

            if clean_sources is not None and len(clean_sources) > 0:
                # Look for the source of interest in NEW sources by coordinates
                for ss in clean_sources:
                    if 'NEW' in ss['src_names']:
                        if np.abs(ra - ss['ra']) <= tolerance and np.abs(dec - ss['dec']) <= tolerance:
                            INTEGRALwrapper.__log.info('Found ' + ooi + ' in catalog as ' + ss['src_names'])
                            ind = clean_sources['src_names'] == ss['src_names']
                            clean_sources['FLAG'][ind] = flag
                            clean_sources['ISGRI_FLAG'][ind] = isgri_flag
                            clean_sources['src_names'][ind] = ooi

                # Look for the source of interest in catalog both by name or coordinates
                cc = SkyCoord(clean_sources['ra'], clean_sources['dec'], unit=(u.deg, u.deg))
                separation = source_coord.separation(cc).deg
                ind = np.logical_or(clean_sources['src_names'] == ooi, separation <= tolerance)

                if np.count_nonzero(ind) > 0:
                    INTEGRALwrapper.__log.warning('Found ' + ooi + ' in catalog as ' + ' '.join(
                        clean_sources['src_names'][ind]) + ', renaming')
                    clean_sources['FLAG'][ind] = flag
                    if 'ISGRI_FLAG' in clean_sources.keys():
                        clean_sources['ISGRI_FLAG'][ind] = isgri_flag
                    if 'JEMX_FLAG' in clean_sources.keys():
                        clean_sources['JEMX_FLAG'][ind] = isgri_flag
                    clean_sources['src_names'][ind] = ooi
                    # This is done because otherwise the workflow will not 
                    # pick up the source name from LC or spectra
                else:
                    INTEGRALwrapper.__log.info('Adding ' + ooi + ' to catalog')
                    if ('flux' in clean_sources.colnames or 'Flux' in clean_sources.colnames or \
                        'FLUX' in clean_sources.colnames) and 'ISGRI_FLAG' in clean_sources.colnames:
                        INTEGRALwrapper.__log.debug('Flux is present')
                        clean_sources.add_row((0, ooi, 0, ra, dec, 0, isgri_flag, flag, 1e-3, 0, 0))
                    elif 'ISGRI_FLAG' in clean_sources.colnames:
                        INTEGRALwrapper.__log.debug('Flux is NOT present but ISGRI_FLAG is present')
                        clean_sources.add_row((0, ooi, 0, ra, dec, 0, isgri_flag, flag, 1e-3))
                    else:
                        INTEGRALwrapper.__log.debug('Flux and ISGRI_FLAG are NOT present')
                        clean_sources.add_row((0, ooi, 0, ra, dec, flag, 1e-3))

                clean_sources = table.unique(clean_sources, keys=['src_names'])      
            else:
                api_cat = INTEGRALwrapper.make_one_source_catalog_string(ooi, ra, dec, isgri_flag, flag)
                api_catalog = oda_api.data_products.ApiCatalog(json.loads(api_cat), name='dispatcher_catalog')
                return api_catalog.table
                
        return clean_sources

    @staticmethod
    def sum_spectral_products(spectrum_results, source_name):
        d = spectrum_results[0]

        ID_spec = -1
        ID_arf = -1
        ID_rmf = -1

        for ID, s in enumerate(d._p_list):
            if ('spectrum' in s.meta_data['product']):
                ID_spec = ID
            if ('arf' in s.meta_data['product']):
                ID_arf = ID
            if ('rmf' in s.meta_data['product']):
                ID_rmf = ID

            if ID_arf > 0 and ID_spec > 0 and ID_rmf > 0:
                break
        INTEGRALwrapper.__log.info('Initialize with IDs for spe, arf and rmf %d %d %d' % (ID_spec, ID_arf, ID_rmf))

        # d = spectrum_results[0]
        spec = d._p_list[ID_spec].data_unit[1].data
        arf = d._p_list[ID_arf].data_unit[1].data
        rmf = d._p_list[ID_rmf].data_unit[2].data
        rate = spec['RATE'] * 0.
        err = spec['STAT_ERR'] * 0.
        syst = spec['SYS_ERR'] * 0.
        rate.fill(0)
        err.fill(0)
        syst.fill(0)
        # qual=spec['QUALITY']
        # This is necessary for ISGRI, but gives an error with JEM-X
        if d._p_list[ID_spec].data_unit[1].header['INSTRUME'] == 'IBIS':
            if not hasattr(rmf['MATRIX'], 'element_dtype'):
                rmf['MATRIX'].element_dtype = np.float32
        matrix = rmf['MATRIX'] * 0.
        specresp = arf['SPECRESP'] * 0.
        tot_expos = 0.
        tot_src_expos = 0.
        tot_ontime = 0.

        tstart = 1e10
        tstop = -1e10

        corr_expos = np.zeros(len(rate))
        # print(len(rate))
        for num_spec, d in enumerate(spectrum_results):

            ID_spec = -1
            ID_arf = -1
            ID_rmf = -1

            for ID, s in enumerate(d._p_list):
                if (s.meta_data['src_name'] == source_name):
                    if ('spectrum' in s.meta_data['product']):
                        ID_spec = ID
                    if ('arf' in s.meta_data['product']):
                        ID_arf = ID
                    if ('rmf' in s.meta_data['product']):
                        ID_rmf = ID

            if ID_arf < 0 or ID_spec < 0 or ID_rmf < 0:
                INTEGRALwrapper.__log.warning('Not found products for source %s in spec #%d' % (source_name, num_spec))
                break

            INTEGRALwrapper.__log.info(
                'For source %s the IDs for spe, arf and rmf are %d %d %d' % (source_name, ID_spec, ID_arf, ID_rmf))

            spec = d._p_list[ID_spec].data_unit[1].data
            arf = d._p_list[ID_arf].data_unit[1].data
            rmf = d._p_list[ID_rmf].data_unit[2].data
            expos = d._p_list[ID_spec].data_unit[1].header['EXPOSURE']

            # This should not be done !!!!
            # if np.sum(spec['RATE']) == 0 or np.sum(np.isnan(spec['RATE'])) > 0  \
            #         or np.sum(np.isnan(rmf['MATRIX'].flatten())) > 0:
            #     INTEGRALwrapper.__log.warning('There are zeros or NaN in the spectrum # %d of source %s' %
            #                                   (num_spec, source_name))
            #     continue
            tot_expos += expos
            try:
                tot_src_expos += d._p_list[ID_spec].data_unit[1].header['EXP_SRC']
            except Exception as ee:
                INTEGRALwrapper.__log.debug(ee)
                pass

            tot_ontime += d._p_list[ID_spec].data_unit[1].header['ONTIME']

            loc_tstart = d._p_list[ID_spec].data_unit[1].header['TSTART']
            loc_tstop = d._p_list[ID_spec].data_unit[1].header['TSTOP']

            if loc_tstart < tstart:
                tstart = loc_tstart
            if loc_tstop > tstop:
                tstop = loc_tstop

            INTEGRALwrapper.__log.debug(expos)
            for j in range(len(rate)):
                if (spec['QUALITY'][j] == 0 and spec['STAT_ERR'][j]>0):
                    rate[j] += spec['RATE'][j] / (spec['STAT_ERR'][j]) ** 2
                    err[j] += 1. / (spec['STAT_ERR'][j]) ** 2
                    syst[j] += (spec['SYS_ERR'][j]) ** 2 * expos
                    corr_expos[j] += expos
            if d._p_list[ID_spec].data_unit[1].header['INSTRUME'] == 'IBIS':
                if not hasattr(rmf['MATRIX'], 'element_dtype'):
                    rmf['MATRIX'].element_dtype = np.float32
            matrix += rmf['MATRIX'] * expos
            specresp += arf['SPECRESP'] * expos

        for i in range(len(rate)):
            if err[i] > 0.:
                rate[i] = rate[i] / err[i]
                err[i] = 1. / np.sqrt(err[i])
        matrix = matrix / tot_expos
        specresp = specresp / tot_expos
        syst = np.sqrt(syst / (corr_expos + 1.))

        INTEGRALwrapper.__log.info('Total exposure: %.1f s' % tot_expos)

        return rate, err, matrix, specresp, syst, tot_expos, tot_src_expos, \
            tot_ontime, tstart, tstop

    def sum_spectra(self):

        summed_data = copy.deepcopy(self.all_data[0])

        if len(summed_data._p_list) == 0:
            self.__log.warning('Spectrum does not contain data !')
            return summed_data

        if 'spectrum' not in summed_data._p_list[0].meta_data['product']:
            raise ValueError('This is not a spectrum and you try to sum spectra')

        if len(self.all_data) == 1:
            return summed_data

        sources = self.get_sources()
        self.__log.debug(sources)
        for source in sources:

            ID_spec = -1
            ID_arf = -1
            ID_rmf = -1

            for ID, s in enumerate(summed_data._p_list):
                if (s.meta_data['src_name'] == source):
                    if ('spectrum' in s.meta_data['product']):
                        ID_spec = ID
                    if ('arf' in s.meta_data['product']):
                        ID_arf = ID
                    if ('rmf' in s.meta_data['product']):
                        ID_rmf = ID

            if ID_arf < 0 or ID_spec < 0 or ID_rmf < 0:
                self.__log.warning('Not found products for source %s' % source)
                break

            self.__log.info(
                'For source %s the IDs for spe, arf and rmf are %d %d %d' % (source, ID_spec, ID_arf, ID_rmf))

            rate, err, matrix, specresp, syst, tot_expos, tot_src_expos, tot_ontime, \
                tstart, tstop = self.sum_spectral_products(self.all_data, source)

            summed_data._p_list[ID_spec].data_unit[1].data['RATE'] = rate
            summed_data._p_list[ID_spec].data_unit[1].data['STAT_ERR'] = err
            summed_data._p_list[ID_spec].data_unit[1].data['SYS_ERR'] = syst

            summed_data._p_list[ID_spec].data_unit[1].header['EXPOSURE'] = tot_expos
            summed_data._p_list[ID_spec].data_unit[1].header['EXP_SRC'] = tot_src_expos
            summed_data._p_list[ID_spec].data_unit[1].header['ONTIME'] = tot_ontime
            summed_data._p_list[ID_spec].data_unit[1].header['TELAPSE'] = tstop - tstart

            summed_data._p_list[ID_spec].data_unit[1].header['TSTART'] = tstart
            summed_data._p_list[ID_spec].data_unit[1].header['TSTOP'] = tstop

            summed_data._p_list[ID_arf].data_unit[1].data['SPECRESP'] = specresp

            if summed_data._p_list[ID_spec].data_unit[1].header['INSTRUME'] == 'IBIS':
                if not hasattr(summed_data._p_list[ID_rmf].data_unit[2].data['MATRIX'], 'element_dtype'):
                    summed_data._p_list[ID_rmf].data_unit[2].data['MATRIX'].element_dtype = np.float32
                summed_data._p_list[ID_rmf].data_unit[2].data['MATRIX'].max = \
                    len(summed_data._p_list[ID_rmf].data_unit[2].data['MATRIX'])
            summed_data._p_list[ID_rmf].data_unit[2].data['MATRIX'] = matrix
            summed_data._p_list[ID_rmf].data_unit[2].to_fits_hdu()

        return summed_data

    @staticmethod
    def write_all_lc_fits_files(lc, subcases_pattern, systematic_fraction=0,
                                output_dir='.'):

        sources = [l.meta_data['src_name'] for l in lc._p_list if l.meta_data['src_name'].lower() != 'background']
        sources = list(set(sources))
        INTEGRALwrapper.__log.info("We write lc for the sources " + ' '.join(sources))
        lc_fn_s = []
        tstart_s = []
        tstop_s = []
        exposure_s = []

        for src in sources:
            lc_fn, tstart, tstop, exposure = \
                INTEGRALwrapper.write_lc_fits_files(lc, src, subcases_pattern, output_dir)

            lc_fn_s.append(lc_fn)
            tstart_s.append(tstart)
            tstop_s.append(tstop)
            exposure_s.append(exposure)

        return sources, lc_fn_s, tstart_s, tstop_s, exposure_s

    @staticmethod
    def write_lc_fits_files(lc, source_name, subcases_pattern, output_dir='.'):
        # In LC name has no "-" nor "+" ??????
        patched_source_name = source_name.replace('-', ' ').replace('+', ' ')
        if len(lc._p_list) == 0:
            INTEGRALwrapper.__log.warning("No light curve is present")
            return "none", 0, 0, 0
        instrument = lc._p_list[0].data_unit[1].header['INSTRUME']
        if instrument == 'SPI-ACS':
            lcprod = [l for l in lc._p_list]
        else:
            lcprod = [l for l in lc._p_list if l.meta_data['src_name'] in source_name or \
                  l.meta_data['src_name'] in patched_source_name]

        if (len(lcprod) < 1):
            INTEGRALwrapper.__log.warning("source %s not found in light curve products\nThe available sources are:\n"
                                          % source_name)
            for l in lc._p_list:
                INTEGRALwrapper.__log.warning(l.meta_data['src_name'])

            return "none", 0, 0, 0

        if (len(lcprod) > 1):
            # The first occurrence in JEM-X contains rate for more than one source
            INTEGRALwrapper.__log.warning(
                "source %s is found more than once light curve products, writing only the last one" % source_name)

        if instrument == 'IBIS' or instrument == 'SPI-ACS' or \
           len(lcprod[-1].data_unit) < 3:
            ind_extension = 1
        else:
            ind_extension = 2

        lc_fn = output_dir + "/%s_lc_%s_%s.fits" % (instrument, 
                                                    source_name.replace(' ', '_'),
                                                    subcases_pattern)
        hdu = lcprod[-1].data_unit[ind_extension].to_fits_hdu()
        timedel = hdu.header['TIMEDEL']
        if 'TIMEPIXR' in hdu.header:
            timepixr = hdu.header['TIMEPIXR']
        else:
            timepixr = 0.5

        dt = timedel * timepixr
        conversion = 1
        if instrument == 'SPI-ACS':
            INTEGRALwrapper.__log.debug('SPI-ACS times are in seconds in the header')
            conversion = 86400.
            hdu.header['TFIRST'] = hdu.header['TSTART']
            hdu.header['TLAST'] = hdu.header['TSTART']
            # hdu.header['TSTART'] = hdu.header['TSTART'] / conversion
            # hdu.header['TSTOP'] = hdu.header['TSTOP']  / conversion
        else:
            hdu.header['TSTART'] = hdu.data['TIME'][0] - dt
            hdu.header['TSTOP'] = hdu.data['TIME'][-1] + dt
            hdu.header['TFIRST'] = hdu.data['TIME'][0] - dt
            hdu.header['TLAST'] = hdu.data['TIME'][-1] + dt
        hdu.header['TELAPSE'] = hdu.header['TLAST'] - hdu.header['TFIRST']

        ontime = 0
        if 'FRACEXP' in hdu.header:
            for x in hdu.data['FRACEXP']:
                ontime += x * timedel

        hdu.header['ONTIME'] = ontime

        fits.writeto(lc_fn, hdu.data, header=hdu.header, overwrite=True)

        mjdref = float(hdu.header['MJDREF'])
        INTEGRALwrapper.__log.debug('%g %g' % (float(hdu.header['TSTART']),
                                               float(hdu.header['TSTOP'])))
        tstart = float(hdu.header['TSTART']) / conversion + mjdref
        tstop = float(hdu.header['TSTOP']) / conversion + mjdref
        if 'EXPOSURE' in hdu.header:
            exposure = float(hdu.header['EXPOSURE'])
        else:
            exposure = -1

        return lc_fn, tstart, tstop, exposure

    @staticmethod
    def write_all_spectra_fits_files(spectrum, subcases_pattern, grouping=[0, 0, 0], systematic_fraction=0,
                                     output_dir='.'):

        sources = [l.meta_data['src_name'] for l in spectrum._p_list if l.meta_data['src_name'].lower() != 'background']
        sources = list(set(sources))
        INTEGRALwrapper.__log.info("We write spectra for the sources " + ' '.join(sources))
        spec_fn_s = []
        tstart_s = []
        tstop_s = []
        exposure_s = []

        for src in sources:
            spec_fn, tstart, tstop, exposure = \
                INTEGRALwrapper.write_spectrum_fits_files(spectrum, src,
                                                          subcases_pattern,
                                                          grouping,
                                                          systematic_fraction,
                                                          output_dir)

            spec_fn_s.append(spec_fn)
            tstart_s.append(tstart)
            tstop_s.append(tstop)
            exposure_s.append(exposure)

        return sources, spec_fn_s, tstart_s, tstop_s, exposure_s

    @staticmethod
    def write_spectrum_fits_files(spectrum, source_name, subcases_pattern, 
                                  grouping=[0, 0, 0], systematic_fraction=0,
                                  output_dir='.'):

        # Grouping argument is [minimum_energy, maximum_energy, number_of_bins]
        # number of bins > 0, linear grouping
        # number_of_bins < 0, logarithmic binning

        specprod = [l for l in spectrum._p_list if l.meta_data['src_name'] in source_name]

        if (len(specprod) < 1):
            INTEGRALwrapper.__log.warning("source %s not found in spectral products" % source_name)
            return "none", 0, 0, 0

        instrument = specprod[0].data_unit[1].header['INSTRUME']

        out_name = source_name.replace(' ', '_').replace('+', 'p')
        spec_fn = output_dir + "/%s_spectrum_%s_%s.fits" % (instrument, out_name, subcases_pattern)
        arf_fn = output_dir + "/%s_arf_%s_%s.fits" % (instrument, out_name, subcases_pattern)
        rmf_fn = output_dir + "/%s_rmf_%s_%s.fits" % (instrument, out_name, subcases_pattern)

        INTEGRALwrapper.__log.info("Saving spectrum %s with rmf %s and arf %s" % (spec_fn, rmf_fn, arf_fn))

        specprod[0].write_fits_file(spec_fn)
        specprod[1].write_fits_file(arf_fn)
        specprod[2].write_fits_file(rmf_fn)

        ff = fits.open(spec_fn, mode='update')

        ff[1].header['RESPFILE'] = rmf_fn
        ff[1].header['ANCRFILE'] = arf_fn
        mjdref = ff[1].header['MJDREF']
        tstart = float(ff[1].header['TSTART']) + mjdref
        tstop = float(ff[1].header['TSTOP']) + mjdref
        exposure = ff[1].header['EXPOSURE']
        ff[1].data['SYS_ERR'] = np.zeros(len(ff[1].data['SYS_ERR'])) \
            + systematic_fraction
        ind = np.isfinite(ff[1].data['RATE'])
        ff[1].data['QUALITY'][ind] = 0

        if np.sum(grouping) != 0:
            if grouping[1] <= grouping[0] or grouping[2] == 0:
                raise RuntimeError('Wrong grouping arguments')

            ff_rmf = fits.open(rmf_fn)

            e_min = ff_rmf['EBOUNDS'].data['E_MIN']
            e_max = ff_rmf['EBOUNDS'].data['E_MAX']

            ff_rmf.close()

            ind1 = np.argmin(np.abs(e_min - grouping[0]))
            ind2 = np.argmin(np.abs(e_max - grouping[1]))

            n_bins = np.abs(grouping[2])

            ff[1].data['GROUPING'][0:ind1] = 0
            ff[1].data['GROUPING'][ind2:] = 0

            ff[1].data['QUALITY'][0:ind1] = 1
            ff[1].data['QUALITY'][ind2:] = 1

            if grouping[2] > 0:
                step = int((ind2 - ind1 + 1) / n_bins)
                INTEGRALwrapper.__log.info('Linear grouping with step %d' % step)
                for i in range(1, step):
                    j = range(ind1 + i, ind2, step)
                    ff[1].data['GROUPING'][j] = -1
            else:
                ff[1].data['GROUPING'][ind1:ind2] = -1
                e_step = (e_max[ind2] / e_min[ind1]) ** (1.0 / n_bins)
                INTEGRALwrapper.__log.info('Geometric grouping with step %.3f' % e_step)
                loc_e = e_min[ind1]
                while (loc_e < e_max[ind2]):
                    ind_loc_e = np.argmin(np.abs(e_min - loc_e))
                    ff[1].data['GROUPING'][ind_loc_e] = 1
                    loc_e *= e_step

        ff.flush()
        ff.close()

        return spec_fn, tstart, tstop, exposure

    @staticmethod
    def show_spectral_products(summed_data):
        for dd, nn in zip(summed_data._p_list, summed_data._n_list):
            INTEGRALwrapper.__log.debug(nn)
            dd.show_meta()
            # for kk in dd.meta_data.items():
            if 'spectrum' in dd.meta_data['product']:
                INTEGRALwrapper.__log.debug(dd.data_unit[1].header['EXPOSURE'])
            dd.show()

    @staticmethod
    def plot_image(ext_sig, sources, det_sigma=7, objects_of_interest=[], cmap=matplotlib.cm.gist_earth,
                   levels=np.linspace(1, 10, 10)):

        plt.figure(figsize=(8, 6))
        data = ext_sig.data
        data = np.ma.masked_equal(data, np.nan)

        w = wcs.WCS(ext_sig.header)
        ax = plt.subplot(projection=w)
        cs = plt.contourf(data, cmap=cmap, levels=levels,
                          extend="both", zorder=0)
        cs.cmap.set_under('k')
        cs.set_clim(np.min(levels), np.max(levels))

        cb = plt.colorbar(cs)

        if sources is not None:
            if len(sources) > 0:
                ras = np.array([x for x in sources['ra']])
                decs = np.array([x for x in sources['dec']])
                names = np.array([x for x in sources['src_names']])
                sigmas = np.array([x for x in sources['significance']])
                # Defines relevant indexes for plotting regions

                m_new = np.array(['NEW' in name for name in names])

                m_noisy = sigmas < 5

                # plot new sources as pink circles

                try:
                    m = m_new & (sigmas > det_sigma)
                    ra_coord = ras[m]
                    dec_coord = decs[m]
                    new_names = names[m]
                except:
                    ra_coord = []
                    dec_coord = []
                    new_names = []

                plt.scatter(ra_coord, dec_coord, s=100, marker="o", facecolors = 'none',
                            edgecolors='pink',
                            lw=3, label="NEW any", zorder=5, transform=ax.get_transform('world'))
                for i in range(len(ra_coord)):
                    plt.text(ra_coord[i],
                             dec_coord[i] + 0.5,
                             new_names[i], color="pink", size=15, transform=ax.get_transform('world'))

        # CF Plots object of interest as green
        if objects_of_interest is not None:
            for ooi in objects_of_interest:
                if isinstance(ooi, tuple):
                    ooi, t = ooi
                    c = t
                elif isinstance(ooi, SkyCoord):
                    c = SkyCoord(ooi)
                elif isinstance(ooi, str):
                    t = helper_functions.call_simbad_query_object(ooi, logger=INTEGRALwrapper.__log)
                    if 'RA' in t.colnames:
                        c = SkyCoord(t['RA'], t['DEC'], unit=(u.hourangle, u.deg), frame="fk5")
                    elif 'ra' in t.colnames:
                        c = SkyCoord(t['ra'], t['dec'], unit=(u.deg, u.deg), frame="fk5")
                    else:
                        INTEGRALwrapper.__log.warning(f"Simbad coordinates for object {ooi} has empty coordinates, filled as (0,0)")
                        c = SkyCoord(0.0, 0.0, unit=[u.deg, u.deg])
                else:
                    raise Exception("fail")

                INTEGRALwrapper.__log.debug(f"object: {ooi} , {c}")
                
                plt.scatter(c.ra.deg, c.dec.deg, marker="o", facecolors='none', s=100,
                            edgecolors='green',
                            lw=3, label="Added", zorder=5, transform=ax.get_transform('world'))
                plt.text(c.ra.deg,
                         c.dec.deg + 0.5,
                         str(ooi), color="green", size=15, transform=ax.get_transform('world'))

        try:
            m = ~m_new & (sigmas > det_sigma - 1)
            ra_coord = ras[m]
            dec_coord = decs[m]
            cat_names = names[m]
        except:
            ra_coord = []
            dec_coord = []
            cat_names = []

        plt.scatter(ra_coord, dec_coord, s=100, marker="o", facecolors='none',
                    edgecolors='magenta', lw=3, label="known", zorder=5, transform=ax.get_transform('world'))
        for i in range(len(ra_coord)):
            # print("%f %f %s\n"%(ra_coord[i], dec_coord[i], names[i]))
            plt.text(ra_coord[i],
                     dec_coord[i] + 0.5,
                     cat_names[i], color="magenta", size=15, transform=ax.get_transform('world'))

        plt.grid(color="grey", zorder=10)

        plt.xlabel("RA")
        plt.ylabel("Dec")

    @staticmethod
    def get_pointings(ra, dec, radius, tstart='2003-01-01T00:00:00', tstop='2020-04-01T00:00:00', type='cons',
                      min_good_isgri=500):
        '''
        GET the pointings for a source
        :param ra:
        :param dec:
        :param radius: radius of search
        :param tstart: UTC format
        :param tstop: UTC format
        :param type: NRT or CONS
        :param min_good_isgri: minimum good ISGRI if <=0, it is not checked
        :return: the request response a dictionary with SWID,RA_SCX,DEC_SCX
        '''
        if type.lower() != 'nrt' and type.lower() != 'cons':
            raise Exception("get pointings: input type must be cons or nrt, you have given %s" % type)
        url = oda_public_host + '/gw/timesystem/api/v1.0/scwlist/' + type.lower() + '/'
        url += tstart + '/' + tstop + '?'
        if min_good_isgri > 0:
            url += 'ra=%.4f&dec=%.4f&radius=%.2f&min_good_isgri=%.0f&return_columns=SWID,RA_SCX,DEC_SCX' % (
                float(ra), float(dec), float(radius), float(min_good_isgri))
        else:
            url += 'ra=%.4f&dec=%.4f&radius=%.2f&return_columns=SWID,RA_SCX,DEC_SCX' % (float(ra), float(dec), float(radius))
        INTEGRALwrapper.__log.debug(url)
        r = requests.get(url).json()
        INTEGRALwrapper.__log.debug(json.dumps(r))
        
        if 'SWID' not in r.keys():
            INTEGRALwrapper.__log.warning('Possibly empty list from get_pointings')
            return r

        # Removes slews
        to_clean = []
        for i, ss in enumerate(r['SWID']):
            if not ss.endswith('0'):
                to_clean.append(i)
        r_clean = r.copy()
        if len(to_clean) > 0:
            for k, l in r.items():
                for j in sorted(to_clean, reverse=True):
                    del l[j]
                r_clean[k] = l

        return r_clean

    @staticmethod
    def get_utc_from_revnum(revnum):
        url = oda_public_host + '/gw/timesystem/api/v1.0/converttime/REVNUM/%04d/IJD' % revnum
        try:
            json_res = requests.get(url).json()
            ijd_start = json_res[1]
            ijd_stop = json_res[2]
        except:
            text_res = requests.get(url).text
            text_res_split = text_res.split()
            ijd_start = text_res_split[1]
            ijd_stop = text_res_split[2]
        url2 = oda_public_host + '/gw/timesystem/api/v1.0/converttime/IJD/%s/UTC'
        try:
            utc_start = requests.get(url2 % ijd_start).json()
        except:
            utc_start = requests.get(url2 % ijd_start).text
        try:
            utc_stop = requests.get(url2 % ijd_stop).json()
        except:
            utc_stop = requests.get(url2 % ijd_stop).text
        return utc_start, utc_stop

    # This is copied from integralclient by V. Savchenko
    @staticmethod
    def converttime(informat, intime, outformat, debug=True):
        import time
        informat_i = informat
        intime_i = intime
        if informat.lower() == 'mjd':
            informat_i = 'IJD'
            intime_i = float(intime_i) - 51544.

        url = oda_public_host + '/gw/timesystem/api/v1.0/converttime/' + \
              informat_i + '/' + t2str(intime_i) + '/' + outformat

        ntries_left = 3

        while ntries_left > 0:
            try:
                r = requests.get(url)
                if r.status_code != 200:
                    raise ValueError('error converting ' + url + '; from timesystem server: ' + str(r.text))

                if outformat == "ANY":
                    try:
                        return r.json()
                    except:
                        pass
                return r.text.strip().strip("\"")

            except Exception as e:
                if 'is close' in repr(e):
                    raise

                ntries_left -= 1

                if ntries_left > 0:

                    time.sleep(5)
                    continue
                else:
                    raise


def get_format_string(res, ep, em):
    # e_max=np.max(np.abs(ep), np.abs(em))
    e_min = np.min([np.abs(ep), np.abs(em)])
    myformat = "%.2f"

    if res == 0 or e_min == 0:
        return myformat

    decade = np.floor(np.log10(np.abs(res)))
    if e_min != res:
        decade_min = np.floor(np.log10(np.abs(res - e_min)))
    else:
        decade_min = np.floor(np.log10(np.abs(e_min)))

    # print("Getting Format")
    # print(res, em, ep, decade, decade_min)

    if (np.abs(decade) <= 2 and decade_min > 0):
        myformat = "%.0f"
    elif (np.abs(decade) == 0 and decade_min == 0):
        myformat = "%.1f"
    else:
        if (np.abs(decade) <= 2 and decade_min < 0):
            myformat = "%." + "%d" % (-decade_min) + "f"
            if np.abs(e_min / 10 ** (decade_min)) < 2:
                myformat = "%." + "%d" % (-decade_min + 1) + "f"
        else:
            myformat = "%." + "%d" % (np.abs(decade_min - decade)) + "e"
            if np.abs(e_min / 10 ** (decade_min)) < 2:
                myformat = "%." + "%d" % (np.abs(decade_min - decade) + 1) + "e"

    return myformat


@logged
def find_duplicates(data, separation=3):
    # Prints out duplicates and returns two arrays of indexes: first and second sources
    # separation is the threshold separation in arcminutes

    ind = np.ones(len(data), dtype=bool)
    c = SkyCoord(ra=data['ra'], dec=data['dec'])

    idx_self, d2d_self, d3d_self = c.match_to_catalog_sky(c, nthneighbor=2)

    ind_first_match = np.argwhere(d2d_self.arcmin < separation).flatten()

    find_duplicates._log.debug("There are %d duplicates" % (len(ind_first_match)))

    if len(ind_first_match) == 0:
        return None, None

    ind_first_match = ind_first_match
    ind_second_match = idx_self[ind_first_match]

    for i in range(len(c)):
        if d2d_self[i].arcmin < separation:
            find_duplicates._log.debug("%d %d %s %f %f %s %f %f" % (
                i, idx_self[i], data['src_names'].data[ind][i], data['ra'].data[ind][i],
                data['dec'].data[ind][i],
                data['src_names'].data[ind][idx_self[i]], data['ra'].data[ind][idx_self[i]],
                d2d_self[i].arcmin))

    return ind_first_match, ind_second_match


def get_parameter_output_string(comp, par, par_range=True, threshold_plusminus=0.1, latex_out=False):
    xspec_input = True
    try:
        unit = par.unit
    except:
        xspec_input = False

    if xspec_input:
        # Xspec parameters
        val = par.values[0]
        unit = par.unit
        lval = par.error[0]
        uval = par.error[1]
        if comp.name == 'cflux' and par.name == 'lg10Flux':
            val = 10 ** (val + 10)
            lval = 10 ** (lval + 10)
            uval = 10 ** (uval + 10)
            unit = 'x1e-10 erg/s/cm^2'
        if comp.name == 'pegpwrlw' and par.name == 'norm':
            unit = 'x1e-12 erg/s/cm^2'
        output_par = not par.frozen and par.link == ''
        par_name = par.name
        comp_name = comp.name
    else:
        # pandas quantiles
        val = par[0.5]
        lval = par[0.16]
        uval = par[0.84]
        unit = ''

        if 'lg10Flux' in par:
            val = 10 ** (val + 10)
            lval = 10 ** (lval + 10)
            uval = 10 ** (uval + 10)

        par_name = comp.split('__')[0]
        comp_name = ''
        output_par = True

    if output_par:

        format_str = get_format_string(val, uval, lval)
        if par_range:
            output_str = "%s %s " + format_str + " %s (" + format_str + "-" + format_str + ")"
            return_str = output_str % (comp_name, par_name, val, unit, lval, uval)
        else:
            # print(np.abs((lval + uval - 2*val) / (-lval+uval) * 2))
            if np.abs((lval + uval - 2 * val) / (-lval + uval) * 2) > threshold_plusminus:
                output_str = "%s %s " + format_str + " (" + format_str + " +" + format_str + ") %s"
                if latex_out:
                    output_str = "%s & %s & " + format_str + "$_{" + format_str + "}^{+" + format_str + "}$ & %s \\\\"
                return_str = output_str % (comp_name, par_name, val, lval - val, uval - val, unit)
            else:
                output_str = "%s %s " + format_str + " +/- " + format_str + " %s"
                if latex_out:
                    output_str = "%s & %s & " + format_str + " &$\pm$ " + format_str + " & %s \\\\"
                return_str = output_str % (comp_name, par_name, val, (uval - lval) / 2, unit)

    elif not par.link == '':
        format_str = get_format_string(val, val, val)
        output_str = "%s %s " + format_str + " %s (%s)"
        if latex_out:
            output_str = "%s & %s & " + format_str + " & %s & (%s) \\\\"
        return_str = output_str % (comp.name, par.name, val, unit, par.link)
    else:
        format_str = get_format_string(val, val, val)
        output_str = "%s %s " + format_str + " %s "
        if latex_out:
            output_str = "%s & %s & " + format_str + " & -- & %s \\\\"
        return_str = output_str % (comp.name, par.name, par.values[0], par.unit)

    return return_str

#Copied from pyxmmsas and adapted from VS
def dump_yaml(to_save, file_name='dump.yaml'):
    """
    def dump_yaml(to_save, file_name='dump.yaml'):
    :param to_save: Dictionary to save
    :param file_name: file name to save
    :return:
    """
    import astropy.table.table
    def simplify(x):
        if isinstance(x, np.ndarray):
            return simplify(list(x))

        # if isinstance(x, np.core.multiarray.scalar):
        #    return float(x)

        if isinstance(x, list):
            return [simplify(a) for a in x]

        if isinstance(x, tuple):
            return tuple([simplify(a) for a in x])

        if isinstance(x, dict):
            return {simplify(a): simplify(b) for a, b in x.items()}

        if isinstance(x, astropy.table.table.Table):
            return x.to_pandas().to_dict()

        try:
            return float(x)
        except:
            # print("Dump_yaml do not not to return", x)
            return x

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    with open(file_name, 'w') as ff:
        yaml.dump(simplify(to_save), ff)


# Copied from VS's integralclient
def t2str(t):
    if isinstance(t, float):
        return "%.20lg" % t

    if isinstance(t, int):
        return "%i" % t

    if isinstance(t, str):
        return t

import click
@click.command()
@click.argument('infile')
@click.option('--s_n_threshold', default=2.0, help='The minimum S/N')
@click.option('--outfile', default=None, help='the output file name, if None, it appends _rbn.pi removing anything after a dot in the infile name.')
def group_spectrum_adaptively(infile, s_n_threshold, outfile=None):
    """groups a spectrum by reaching a minimum S/N starting from low energy

    Args:
        infile (str): the input file name
        s_n_threshold (float): the minimum S/N to stop grouping
        outfile (str, optional): the output file name, if None, it appends _rbn.pi removing anything after a dot in the infile name. Defaults to None.

    Returns:
        numpy array:  the grouping vector
    """    
    from astropy.io import fits as pf

    ff = pf.open(infile)
    rate = ff[1].data['RATE']
    stat_err = ff[1].data['STAT_ERR']
    sys_err = ff[1].data['SYS_ERR']
    quality = ff[1].data['QUALITY']
    grouping = ff[1].data['GROUPING']
    current_s_n = 0

    for i, (r, sy_e, st_e, q, g) in enumerate(zip(rate, sys_err, stat_err, quality, grouping)):
        if q != 0 or g ==0 or st_e == 0:
            grouping[i] = 0
            continue
        current_s_n += (r / np.sqrt( (r*sy_e)**2+st_e**2))**2
        if np.sqrt(current_s_n) >= s_n_threshold:
            grouping[i] = 1
            current_s_n =0
        else:
            grouping[i] = -1

    if outfile is None:
        outfile = infile.split('.')[0] + '_grp.pi'
    ff.writeto(outfile, overwrite=True)

    return grouping

