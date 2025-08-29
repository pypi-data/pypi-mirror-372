import oda_integral_wrapper.wrapper
import oda_integral_wrapper.helper_functions as helper_functions
import subprocess
from astropy import units as u
from astropy.coordinates import SkyCoord
import copy
import os
from astropy.io import fits
import numpy as np
from glob import glob
import oda_api.plot_tools
import pandas as pd
import json
import re
import ast

url_default_catalog = "https://www.astro.unige.ch/integral/catalog/MMODA-api-catalog.txt"


def parse_source_multiline(source: str, logger) -> dict[str, list[dict]]:

    result = {'assign': [], 'standalone': []}

    parsed = ast.parse(source)

    for node in parsed.body:
    
        node_code = "\n".join(source.split('\n')[node.lineno-1:node.end_lineno])
        
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                raise NotImplementedError(f'Multiple assignment is not supported:\n{node_code}')
            varname = node.targets[0].id
            type_annotation = None
            value_node = node.value
        elif isinstance(node, ast.AnnAssign):
            varname = node.target.id
            type_annotation = ast.unparse(node.annotation)
            value_node = node.value
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Name):
            # "hanging" output declaration
            value_node = None
            type_annotation = None
            varname = node.value.id
        else:
            logger.info(f"Skipping {node}")
            continue

        if value_node is not None:
            try:
                value = ast.literal_eval(value_node)
            except ValueError:
                value = ast.unparse(value_node)
        else:
            value = None

        result['assign'].append(dict(varname=varname, 
                                     type_annotation=type_annotation, 
                                     value=value, 
                                     raw_line=node_code))

    return result


def extract_parameters_from_cells(logger, cells, nb_inp_fname='NoName'):
    
    parameters = {}

    get_nbname(logger, parameters, nb_inp_fname=nb_inp_fname)
    
    ordered_cells = []

    for cell in cells:
        if not cell.startswith('# Parameters'):
            ordered_cells.append(cell)
    
    for cell in cells:
        if cell.startswith('# Parameters'):
            ordered_cells.append(cell)
    
    for cell in ordered_cells:

        res = parse_source_multiline(cell, logger) 

        for x in res['assign']:
            parameters[x['varname']] = x['value']
            
    return parameters


def get_source_coords_catalog_from_obs(observation, instrument):
    source_catalog = observation.get(f'{instrument}_source_catalog', None)
    sources_coord_obs = {}
    if source_catalog is not None:
        source_catalog_obj = json.loads(source_catalog)
        source_names = source_catalog_obj['cat_column_list'][1]
        ras = source_catalog_obj['cat_column_list'][3]
        decs = source_catalog_obj['cat_column_list'][4]
        sources_coord_obs = { k: v for k, v in zip(source_names, zip(ras, decs)) }

    return sources_coord_obs


def get_nbname(logger, parameters, nb_inp_fname='NoName'):
    
    # It does not work from papermill
    try:
        import ipynbname
        nb_fname = ipynbname.name()+'.ipynb'
    except Exception as e:
        logger.warning('Using input name %s', nb_inp_fname)
        logger.warning(e)
        nb_fname = nb_inp_fname

    from git import Repo
    try:
        repo = Repo('.')
        repo_name = repo.remotes.origin.url.split('.git')[0]
        origin_notebook = repo_name.replace(':','/').replace('git@', 'https://')
        if 'renkulab.io' in origin_notebook:
            if not ('gitlab' in origin_notebook):
                origin_notebook = origin_notebook.replace('renkulab.io', 'gitlab.renkulab.io') 
        origin_notebook += '/-/blob/%s/' % repo.active_branch + nb_fname
    except:
        logger.warning('Not in a git repository, no provenance')
        origin_notebook = nb_fname
    logger.info('Origin Notebook ' + origin_notebook)
    parameters['origin_notebook'] = origin_notebook


def prepare_observation(logger, parameters):
    # To build science window lists
    import matplotlib.pylab as plt

    if parameters['RA'] == 0.0 and parameters['DEC'] == 0.0:
        simbad = helper_functions.call_simbad_query_object(parameters['src_name'], logger=logger)
        if simbad is not None and 'RA' in simbad.colnames:
            coord = SkyCoord(simbad['RA'][0], simbad['DEC'][0],
                             unit=[u.hour, u.deg])
        elif simbad is not None and 'ra' in simbad.colnames:
            coord = SkyCoord(simbad['ra'][0], simbad['dec'][0],
                             unit=[u.deg, u.deg])
        else:
            logger.warning(f"Simbad coordinates for object {parameters['src_name']} has empty coordinates, filled as (0,0)")
            coord = SkyCoord(0.0, 0.0, unit=[u.deg, u.deg])
        coord.fk5
    else:
        coord = SkyCoord(parameters['RA'], parameters['DEC'], unit=[u.deg, u.deg])
        coord.fk5

    logger.info("Coordinates for %s are RA=%.4f, Dec=%.4f" % (parameters['src_name'],
                                                            coord.ra.deg, coord.dec.deg ) )

    revs = []
    if type(parameters['T1']) is list:
        for t1, t2 in zip(parameters['T1'],  parameters['T2']):
            revs.append({'coord': coord, 'tstart': t1, 'tstop': t2,
                         'name': parameters['src_name'],
                         'label': '', 'RA': parameters['RA'],
                         'DEC': parameters['DEC']})
    else:
        revs.append({'coord': coord, 'tstart': parameters['T1'],
                     'tstop': parameters['T2'],
                     'name': parameters['src_name'],
                     'label': '', 'RA': parameters['RA'],
                     'DEC': parameters['DEC']})
    # from importlib import reload
    # reload(oda_integral_wrapper.wrapper)
    wrap=oda_integral_wrapper.wrapper.INTEGRALwrapper(token=parameters['token'], 
                                                      integral_data_rights=parameters.get('integral_data_rights', 'public'))

    for i, source in enumerate(revs):
        
        #logger.info(source['coord'].ra.deg, source['tstart'])
        r = wrap.get_pointings(ra=source['coord'].ra.deg, dec=source['coord'].dec.deg, radius=parameters['radius'], 
                        tstart=source['tstart'], tstop=source['tstop'], type=parameters.get('data_version', 'CONS'))
        
        if 'SWID' in r.keys():
            scwids = r['SWID']
            logger.info(source['name'] + ' nscw=%d'%(len(scwids)))
            revs[i].update(scwids=scwids)
            revs[i].update( {'RA_SCX':r['RA_SCX'], 
                            'DEC_SCX':r['DEC_SCX']}
                        )
            if len(scwids)>1:
                fig = plt.figure()
                ra = np.array(r['RA_SCX'])
                # ra[ra>180]-=180.
                plt.scatter(ra, r['DEC_SCX'])
                plt.title(source['name'])
                plt.scatter(source['coord'].ra.deg, source['coord'].dec.deg, 
                            color='red', marker='x')
                plt.xlabel('RA')
                plt.ylabel('Dec')
                source['Figure'] = fig
        else:
            logger.warning('SCWID keyword not in response for %s (%s)', source['name'], r)
            # raise Exception('No scwids found for %s' % source['name'])
    
    return revs


def get_catalog(revs, parameters, logger, instrument):
    import matplotlib.pylab as plt
    import random
    if parameters['data_version'].lower() == 'nrt':
        suffix_version = '.000'
    else:
        suffix_version = '.001'

    # from importlib import reload
    # reload(oda_integral_wrapper.wrapper)
    wrap=oda_integral_wrapper.wrapper.INTEGRALwrapper(token=parameters['token'], integral_data_rights=parameters['integral_data_rights'], 
                                                    host_type=parameters['host_type'])
    
    if 'jemx_unit' in parameters:
        jemx_unit = str(parameters['jemx_unit'])
    else:
        jemx_unit = ''

    if 'api_catalog_file' in parameters and parameters['api_catalog_file'] != '':
        api_catalog_file = parameters['api_catalog_file'] 
    else:
        api_catalog_file = 'api_cat_str_%s_%s%s.txt'%(parameters['src_name'].replace(' ','_').replace('+','p'), instrument, jemx_unit)

    if  not parameters['make_image'] and parameters['use_default_catalog'] is False:
        if os.path.isfile(api_catalog_file):
            with open(api_catalog_file) as f: 
                api_cat_file = f.readlines() 
            
            api_cat=json.loads(api_cat_file[0])
        else:
            logger.warning('There is no catalog file, we force image creation')
            parameters['make_image'] = True

    if parameters['make_image'] and (not parameters['use_default_catalog']):
        
        scwids = []
        ra_scx = []
        dec_scx = []

        for source in revs:
            scwids += source['scwids']
            ra_scx += source['RA_SCX']
            dec_scx += source['DEC_SCX']

        logger.info('%s', scwids)
        # We assume that the source is the same for each cunck of observation and equal to the first one
        source = revs[0]

        random.seed(0)
        ind_sample = range(len(scwids))
        if parameters['n_scw_image'] > 0 and parameters['n_scw_image'] < len(scwids):
            ind_sample = np.array(sorted(random.sample(range(len(scwids)),parameters['n_scw_image'])))
        elif parameters['n_scw_image'] > -1:
            n_sample = int(np.abs(parameters['n_scw_image'] * len(scwids)))
            if n_sample < 1:
                n_sample = len(ind_sample)
            ind_sample = np.array(sorted(random.sample(range(len(scwids)),n_sample)))
        if len(ind_sample) > 0:
            plt.scatter(np.array(ra_scx)[ind_sample], np.array(dec_scx)[ind_sample], marker='o', color='red')
        else:
            logger.warning('No science windows are available')
            raise Exception('No data are available for the selected parameters')

        scw_list=[ss+suffix_version for ss in np.array(scwids)[ind_sample] if ss.endswith('0')]
        logger.info(f"We have {len(scw_list)} science windows")

        par_dict = dict(s_max=parameters['s_max'], sleep_time=120,
                        instrument=instrument,
                        product='%s_image' % instrument,
                        E1_keV=parameters['E1_keV'],
                        E2_keV=parameters['E2_keV'],
                        osa_version=parameters['osa_version'],
                        detection_threshold=parameters['detection_threshold'],
                        product_type='Real',
                        src_name=parameters['src_name'],
                        T1=parameters['T1'],
                        T2=parameters['T2'],
                        RA=float(source['coord'].ra.deg),
                        DEC=float(source['coord'].dec.deg) )
        
        if 'jemx_unit' in parameters:
            par_dict.update({'jemx_num' : parameters['jemx_unit']})
        
        logger.info('par_dict %s', par_dict)
        logger.info('scw_list %s', scw_list)   
        
        data=wrap.long_scw_list_call(scw_list, **par_dict)

        try:
            mosaic = data.mosaic_image_0_mosaic
        except:
            try:
                mosaic =  data.mosaic_image_0
            except:
                mosaic = None
                logger.error('No Mosaic in preparing catalog !')
                return mosaic
            
        mosaic.write_fits_file(source['name'].replace(' ','_').replace('+','p')+
                                                        source['label']+'_%s%s_mosaic.fits' % (instrument, jemx_unit),
                                            overwrite=True)

        api_cat_str = wrap.extract_catalog_string_from_image(data, det_sigma=parameters['detection_threshold'], 
                                                            objects_of_interest=[(parameters['src_name'], source['coord'])],
                                                            update_catalog=True)
        
        api_cat = json.loads(api_cat_str)
    
        sources=data.dispatcher_catalog_1.table

        with open(api_catalog_file,'w') as f: 
            f.write(api_cat_str) 

        if len(mosaic.data_unit) >4:
            wrap.plot_image(mosaic.data_unit[4], sources, 
                            objects_of_interest=[(parameters['src_name'], source['coord'])], det_sigma=parameters['detection_threshold'])

    if parameters['make_image'] and parameters['use_default_catalog'] is False:
        
        table_catalog = data.dispatcher_catalog_1.table
        
        if table_catalog is not None:
            logger.debug('%s', table_catalog['src_names'])

    if parameters['use_default_catalog']:
        import requests
        response = requests.get(url_default_catalog)
        
        if response.status_code == 200:
            api_cat = json.loads(response.text)
        else:
            raise Exception('Could not read default catalog')
        oda_catalog = oda_integral_wrapper.wrapper.INTEGRALwrapper.get_catalog_from_dict(api_cat)
        for source in revs:
            oda_catalog_table = wrap.add_objects_of_interest(oda_catalog._table, [(source['name'], source['coord'])])
        oda_catalog = oda_catalog.from_table(oda_catalog_table)
        api_cat_str = json.dumps(oda_catalog.get_dictionary())
        api_cat = json.loads(api_cat_str)
    
        with open(api_catalog_file,'w') as f: 
            f.write(api_cat_str) 
    
    

    logger.info(json.dumps(api_cat))
    return api_cat

import nbformat
import ipynbname


def get_notebook_cells(notebook_path=None, cell_types=["markdown", "code", "raw"]):
    if not notebook_path:
        notebook_path = ipynbname.path()

    with open(notebook_path, "r", encoding="utf-8") as rf:
        nb = nbformat.read(rf, as_version=4)

    cells = [cell for i, cell in enumerate(nb.cells) if cell["cell_type"] in cell_types]
    return cells


def get_cell_id():
    cell_id = get_ipython().get_parent()["metadata"]["cellId"]
    return cell_id


def get_cell_index():
    cell_id = get_cell_id()
    cells = get_notebook_cells()
    for idx, cell in enumerate(cells):
        if cell["id"] == cell_id:
            return idx


def clean_mosaics(instruments, observations, isdc_sources, logger, parameters):

    # from importlib import reload
    # reload(oda_integral_wrapper.wrapper)
    
    wrap = oda_integral_wrapper.wrapper.INTEGRALwrapper(token=parameters['token'],
                                                        integral_data_rights='all-private',
                                                        host_type=parameters['host_type'] )
    import mosaic.treat
    # from importlib import reload
    # reload(mosaic.treat)   

    for instr in instruments:
        for source in observations:

            data = source['%s_raw_mosaic' % instr]
            
            if type(data) is str or data is None:
                continue

            src_name = ''
            if 'title' in source.keys():
                src_name = source['title']
            elif 'src_name' in parameters.keys():
                src_name = parameters['src_name']

            sanitized_source_title = oda_integral_wrapper.wrapper.INTEGRALwrapper.clean_source_title(src_name)

            outfile_name = sanitized_source_title 
            if 'expid' in source.keys():
                outfile_name += '_' + str(source['expid']) 
            outfile_name += '_%s_mosaic.fits' % instr

            flag_skip = False
            if hasattr(data, 'mosaic_image_0_mosaic'):
                my_mosaic = data.mosaic_image_0_mosaic
            elif hasattr(data, 'mosaic_image_0'):
                my_mosaic = data.mosaic_image_0
            else:
                logger.warning('Mosaic "%s" for %s is empty' % (source.get('title',''),
                                                                instr))
                continue
                
            list_hdus = my_mosaic.to_fits_hdu_list()
            for hdu in list_hdus[1:]:
                if 'IMATYPE' in hdu.header:
                    if hdu.header['IMATYPE'] == 'SIGNIFICANCE':
                        # print('PIPPO MIN %f ************* %s ***********\n' % (np.min(hdu.data[(hdu.data != 0 ) & np.isfinite(hdu.data)]), source['title']) )

                        if np.sum(hdu.data != 0) > 0 and \
                                np.min(hdu.data[hdu.data != 0]) < -25.:
                            logger.warning(f'Mosaic {source["title"]} for {instr} is strange, skipping')
                            flag_skip = True
            my_mosaic.write_fits_file(outfile_name, overwrite=True)
                
            if flag_skip:
                continue
            
            logger.debug(f"Querying the object {src_name} from Simbad")
            
            simbad = helper_functions.call_simbad_query_object(src_name,
                                                               logger=logger)
            
            # Default
            object_of_interest = None
            if 'coord' in source.keys():
                object_of_interest = [(src_name, source['coord'])]
            
            # Override default is object is in simbad
            if simbad is not None:
                ra_key = 'RA'
                dec_key = 'DEC'
                simbad_units = [u.hour, u.deg]
                if 'ra' in simbad.colnames:
                    ra_key = 'ra'
                    dec_key = 'dec'
                    simbad_units = [u.deg, u.deg]

                if simbad[ra_key].value != '' and simbad[dec_key].value != '':
                    coord = SkyCoord(simbad[ra_key], simbad[dec_key],
                                     unit=simbad_units)
                    object_of_interest = [(src_name, coord)]
                    
            if 'source_to add' in parameters:
                if parameters['source_to_add'] != {}:
                    source_of_interest = (parameters['source_to_add']['name'],
                                          SkyCoord(parameters['source_to_add']['ra'],
                                          parameters['source_to_add']['dec'],
                                          unit=u.deg, frame='fk5'))
                    if object_of_interest is not None:
                        object_of_interest.append(source_of_interest)
                    else:
                        object_of_interest = [source_of_interest]

            data2 = copy.copy(data)
            new_source_suffix = ''
            if 'obsid' in source.keys():
                # avoid to add it twice or more
                if source['obsid'] not in new_source_suffix:
                    new_source_suffix = '_'+source['obsid']
            
            api_cat_str = wrap.extract_catalog_string_from_image(data2, det_sigma=parameters['detection_threshold'], 
                                                                objects_of_interest=object_of_interest,
                                                                update_catalog=True, 
                                                                include_new_sources=parameters['include_new_sources'],
                                                                new_source_suffix=new_source_suffix, 
                                                                isdc_ref_cat=isdc_sources)

            # print('\n\nCOMPUTE FLUXES\n\n')
            # Compute fluxes on the original image
            if object_of_interest is None:
                fluxed_catalog = wrap.compute_fluxes(data2, parameters['detection_threshold'])
            else:
                fluxed_catalog = wrap.compute_fluxes(data2, parameters['detection_threshold'], 
                                                     ensure_sources=[x[0] for x in object_of_interest])
            # except:
            #     logger.warning("We could not compute the fluxes, returning None!!!")
            #     fluxed_catalog = None
            
            # print(fluxed_catalog)
            # print('\n\nCOMPUTED FLUXES\n\n')
                        
            if api_cat_str is not None:
                # api_cat = json.loads(api_cat_str)
                api_cat_fname = 'api_cat_str_%s_%s.txt' % (sanitized_source_title, instr)
                
                source.update({'api_cat_fname': api_cat_fname})
                
                with open(api_cat_fname, 'w') as f:
                    f.write(api_cat_str) 

            sources = wrap.extract_catalog_table_from_image(data2, objects_of_interest=object_of_interest)
            # change with outfile_path ?
            oia = mosaic.treat.OSAMosaicImageAnalysis(outfile_name, 
                                                    outfile_name.replace('_mosaic.fits','_mosaic_clean_'),
                                                    source_analysis = True, 
                                                    exposure_fraction_cut = 100)
            oia.reference_catalog = isdc_sources
            try:
                oia.main()
            except Exception as e:
                logger.warning(f"WARNING\nCould not process {outfile_name}\nskipping with error: {str(e)}")
                continue
                
            csv_outfile_name = outfile_name.replace('_mosaic.fits', '_mosaic_clean_source_results.csv')
            if os.path.isfile(csv_outfile_name):
                sources_sextractor = pd.read_csv(csv_outfile_name)
            else:
                sources_sextractor = []
            
            if instr == 'isgri':
                sextractor_fname = outfile_name.replace('_mosaic.fits',
                                                '_mosaic_clean_significance%.0f_%.0f.fits') % (float(parameters['E1_keV']),
                                                                                            float(parameters['E2_keV']))
            else:
                if 'J_E1_keV' in parameters.keys():
                    e1 = parameters['J_E1_keV']
                else:
                    e1 = parameters['E1_keV']
                if type(e1) is float:
                    sextractor_fname = glob(outfile_name.replace('_mosaic.fits',
                                                '_mosaic_clean_significance%.0f*_*.fits' % e1))[0]
                else:
                    sextractor_fname = glob(outfile_name.replace('_mosaic.fits',
                                                '_mosaic_clean_significance%s*_*.fits' % e1))[0]

            logger.info("Using this file name " + sextractor_fname)
            
            f_image_sexttractor = fits.open(sextractor_fname)
            # We get the actual start and stop times
            image_sextractor = f_image_sexttractor[0].data
            f_image_sexttractor.close()
            if hasattr(data2, 'mosaic_image_0_mosaic'):
                my_mosaic = data2.mosaic_image_0_mosaic
            elif hasattr(data2, 'mosaic_image_0'):
                my_mosaic = data2.mosaic_image_0
            else:
                raise Exception('Clean mosaic: data product has no mosaic?')
            my_mosaic.data_unit[4].data = image_sextractor
            if 'DATE-OBS' in my_mosaic.data_unit[1].header:
                source['tstart'] = my_mosaic.data_unit[1].header['DATE-OBS']
            else:
                t_start_ijd = my_mosaic.data_unit[1].data['TSTART'][0]
                source['tstart'] = wrap.converttime('IJD', t_start_ijd, 'UTC')
            if 'DATE-END' in my_mosaic.data_unit[1].header:
                source['tstop'] = my_mosaic.data_unit[1].header['DATE-END']
            else:
                t_stop_ijd = my_mosaic.data_unit[1].data['TSTOP'][0]
                if t_stop_ijd == t_start_ijd:
                    # print(np.nanmax(data2.mosaic_image_0_mosaic.data_unit[5].data)/86400.)
                    t_stop_ijd += np.nanmax(data2.mosaic_image_0_mosaic.data_unit[5].data)/86400.
                    logger.debug('Update tstop')
                source['tstop'] = wrap.converttime('IJD', t_stop_ijd, 'UTC')
            sources2 = copy.copy(sources)
            mask = np.zeros(len(sources2), dtype=bool)
            for i, ss in enumerate(sources2):
                # print(i,ss)
                if parameters['include_new_sources']:
                    if "NEW" in ss['src_names']:
                        mask[i] = True
                #         #continue
                if len(sources_sextractor) > 0:
                    # print(type(sources_sextractor))
                    for _,ss2 in sources_sextractor.iterrows():
                        if ss2['name'] == ss['src_names'] or np.sqrt((ss2['ra'] - ss['ra'])**2 + (ss2['dec'] - ss['dec'])**2) < 1./60. :
                            mask[i] = True
                            if 'NEW' not in ss2['name']:
                                # This gives the name found in sextractor
                                # It ill become useless
                                ss['src_names'] = ss2['name']
                            else:
                                if ~parameters['include_new_sources']:
                                    mask[i] = False

                            # print (ss['src_names'])
                            break
                else:
                    # patch if sextractor did not save sources
                    mask[i] = True

    #         im = cdci_data_analysis.analysis.plot_tools.Image(data2.mosaic_image_0_mosaic.data_unit[4].data, 
    #                                            data2.mosaic_image_0_mosaic.data_unit[4].header)
    #         html_dict = im.get_html_draw(w=600,h=600)

    #         with open('test_%s.html' % sextractor_fname.replace('.fits', ''), 'w') as ff:
    #             ff.write('''<script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.4.2.min.js"></script>
    # <script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.4.2.min.js"></script>
    # ''')
    #             ff.write(html_dict['div'])
    #             ff.write(html_dict['script'])

            sources2 = sources2[mask]
            region_file_name = sextractor_fname.replace('.fits', '.reg')
            wrap.write_ds9_region_file(sources2, region_file_name)
            
            subprocess.check_call(['gzip', '-f', 
                                   os.getcwd()+'/'+sextractor_fname])
            subprocess.check_call(['gzip', '-f', os.getcwd()+'/'+outfile_name])
            
            image_product = oda_api.plot_tools.OdaImage(data2)
            
            # attrs = vars(image_product.data)
            # print(', '.join("%s: %s" % item for item in attrs.items()))
            
            if not os.path.isdir('out'):
                os.mkdir('out')
            img_fn = image_product.get_image_for_gallery(sources=sources2, 
                                                         output_folder='out')

            # generate one fits files
            image_product.write_fits(file_prefix=sanitized_source_title)
            
            # We want a unique file name for each revision
            myhash = img_fn.split('.')[1]
            
            # Dumps parameters into pickle
    #         with open(my_hash+'.pickle', 'wb') as f:
    #             pickle.dump(_i1, f, pickle.HIGHEST_PROTOCOL)
            
            subprocess.check_call(['cp', '-f', outfile_name + '.gz', myhash+'_' + outfile_name+'.gz'])
            subprocess.check_call(['cp', '-f', sextractor_fname + '.gz', myhash+'_'+ sextractor_fname+'.gz'])
            subprocess.check_call(['cp', '-f', region_file_name, myhash + '_' + region_file_name])
                                  
            source.update({
                        '%s_region_file_name' % instr : region_file_name,
                        '%s_sextractor_fname' % instr : sextractor_fname,
                        '%s_myhash' % instr : myhash,
                        '%s_img_fn' % instr : img_fn,
                        '%s_source_catalog' % instr : api_cat_str,
                        '%s_raw_sources' % instr : sources,
                        '%s_mosaic' % instr : data2,
                        '%s_sources' % instr : sources2,
                        "%s_fluxed_catalog" % instr : fluxed_catalog,
                        "%s_outfile_name" % instr :outfile_name
                        }
                        )

def make_product_id_image(parameters):
    
    e1 = float(parameters['E1_keV'])
    e2 = float(parameters['E2_keV'])

    isgri_params_dic_product_id = {
        'E1_keV': "%.1f" % e1,
        'E2_keV': "%.1f" % e2,
        'osa_version': parameters['osa_version'],
        'detection_threshold': parameters['detection_threshold'],
        'instrument': 'isgri',
        'product': 'isgri_image'
    }

    if 'J_E1_keV' in parameters.keys():
        e1 = float(parameters['J_E1_keV'])
    if 'J_E2_keV' in parameters.keys():
        e2 = float(parameters['J_E2_keV'])
        
    jemx1_params_dic_product_id = {
        'J_E1_keV': "%.1f" % e1,
        'J_E2_keV': "%.1f" % e2,
        'osa_version': parameters['osa_version'],
        'detection_threshold': parameters['detection_threshold'],
        'instrument' : 'jemx',
        'product' : 'jemx_image',
        'jemx_num' : 1
    }

    jemx2_params_dic_product_id = {
        'J_E1_keV': "%.1f" % e1,
        'J_E2_keV': "%.1f" % e2,
        'osa_version': parameters['osa_version'],
        'detection_threshold': parameters['detection_threshold'],
        'instrument' : 'jemx',
        'product' : 'jemx_image',
        'jemx_num' : 2
    }

    for kk in ['T1', 'T2', 'tstart', 'tstop', 'src_name']:
        if kk in parameters.keys():
            isgri_params_dic_product_id.update({kk : parameters[kk]})
            jemx1_params_dic_product_id.update({kk : parameters[kk]})
            jemx2_params_dic_product_id.update({kk : parameters[kk]})

    return isgri_params_dic_product_id, jemx1_params_dic_product_id, jemx2_params_dic_product_id


def upload_spectrum_to_gallery(observations, instruments, parameters, logger):
    import oda_api.plot_tools

    wrap2 = oda_integral_wrapper.wrapper.INTEGRALwrapper(token=parameters['token'], host_type=parameters['host_type'])

    parameters_copy = copy.deepcopy(parameters)
    parameters_copy['host_type'] = 'production'
    del parameters_copy['token']
    del parameters_copy['notebooks_folder']

    additional_information = 'parameters = ' + json.dumps(parameters_copy, indent=4)

    for obs in observations:
        # print(obs)
        for ins in instruments:
            dict_ins_key = '%s_spectra' % ins
            spectra = obs.get(dict_ins_key, None)
            
            sources_coord_obs = get_source_coords_catalog_from_obs(obs, ins)
            
            systematic_fraction = parameters.get('isgri_systematic_fraction', 0.0)
            if systematic_fraction == 0.0:
                systematic_fraction = parameters.get('systematic_fraction', 0.0)
            
            xlim = [20,200]
            
            e1 = 1
            e2 = 100

            if 'jemx' in ins:
                systematic_fraction = parameters.get('jemx_systematic_fraction', 0.0)
                if systematic_fraction == 0.0:
                    systematic_fraction = parameters.get('systematic_fraction', 0.0)

                xlim = [2,30]

            if 'E1_isgri' in obs or 'E1_jemx' in obs:
                k1 = 'E1_isgri'
                k2 = 'E2_isgri'
                if 'jemx' in ins:
                    k1 = 'E1_jemx'
                    k2 = 'E2_jemx'
                    
                e1 = obs.get(k1, e1)
                e2 = obs.get(k2, e2)
            elif 'E1_keV' in parameters:
                e1 = parameters['E1_keV']
                e2 = parameters['E2_keV']

            logger.info(f"E1_keV: {e1}")
            logger.info(f"E2_keV: {e2}")

            if spectra is not None and type(spectra) is not str:
                if '%s_sources' % ins in obs:
                    logger.debug('Found %s_sources' % ins)
                    sources = obs['%s_sources' % ins]
                elif 'src_name' in parameters:
                    logger.debug('NOT Found %s_sources' % ins)
                    sources=[parameters['src_name']]
                else:
                    logger.debug('No sources !')
                    sources= [] 
                image_product = oda_api.plot_tools.OdaSpectrum(spectra)
                
                # print(spectra.as_list())
                for i,src in enumerate(sources):
                    
                    if 'MULTIPLE ID' in src:
                        continue
                    # print(src)
                    
                    if not os.path.isdir('out'):
                        os.mkdir('out')
                        
                    img_fn = image_product.get_image_for_gallery( in_source_name=src, 
                                                                systematic_fraction=systematic_fraction,
                                                                xlim=xlim,
                                                                output_folder='out')
                    
                    if 'rev_num' in parameters: 
                        par_dict_product_id = {
                            'source_name': src,
                            'obsid': obs['obsid'],
                            'instrument' : '%s' % ins,
                            'product_type' : '%s_spectrum' % ins, 
                            "rev_num" : parameters['rev_num']
                        }
                    else:
                        par_dict_product_id={    
                            'source_name': parameters['src_name'],
                            'e1_kev' : e1, 
                            'e2_kev' : e2,
                            't1': obs['%s_files' % ins]['tstart'],
                            't2': obs['%s_files' % ins]['tstop'],
                            'radius': parameters['radius'],
                            'instrument' : ins,
                            'product_type' : '%s_spectrum' % ins
                        }

                    product_id = oda_api.api.DispatcherAPI.calculate_param_dict_id(par_dict_product_id)
                    
                    if type(obs['%s_files' % ins]['fname']) == list:
                        spec = obs['%s_files' % ins]['fname'][i]
                    else:
                        spec = obs['%s_files' % ins]['fname']

                    nrt_string = ''
                    if parameters['data_version'].upper() == 'NRT':
                        nrt_string = ' (NRT)'

                    par_dict={    
                                'token': parameters['token'],
                                'e1_kev' : e1, 
                                'e2_kev' : e2,
                                'RA' : sources_coord_obs.get(src, [None, None])[0],
                                'DEC' : sources_coord_obs.get(src, [None, None])[1],
                                'product_title' : src + ' %s spectrum' % ins + nrt_string,
                                'gallery_image_path' : img_fn,
                                'fits_file_path' : [spec, spec.replace('spectrum', 'rmf'), 
                                                    spec.replace('spectrum', 'arf')],
                                'src_name' : src, 
                                'instrument' : ins,
                                'insert_new_source' : True,
                                'force_insert_not_valid_new_source' : True,
                                'validate_source' : True,
                                'apply_fields_source_resolution': True,
                                'product_type' : '%s_spectrum' % ins ,
                                'product_id' : product_id,
                                'additional_information' : additional_information,
                                'html_image': image_product.get_html_image(src, 
                                                                        systematic_fraction, 
                                                                        x_range = xlim),
                                'produced_by' : parameters['origin_notebook']
                    }
                    if 'obsid' in obs:
                        par_dict.update({'obsid': obs['obsid']})
                    if 'tstart' in obs:
                        par_dict.update({'T1': re.sub('\.\d+', '', obs['tstart']),
                        'T2': re.sub('\.\d+', '', obs['tstop'])})
                    else:
                        par_dict.update({'T1': obs['%s_files' % ins]['tstart'],
                            'T2': obs['%s_files' % ins]['tstop']})
                    n_max_tries = 3
                    n_tries_left = n_max_tries
                    while True:
                        try:
                            d = wrap2.disp.post_data_product_to_gallery(**par_dict)
                            gallery_object = obs.get("%s_gallery_object" % ins, [])
                            gallery_object.append(d.copy())
                            obs.update({
                                "%s_gallery_object" % ins : gallery_object,
                                })
                            if 'error_message' not in d:
                                obs.update({
                                    'processed_spectra':  True
                                })
                                break
                            else:
                                n_tries_left -= 1
                                if n_tries_left == 0:
                                    break
                                else:
                                    logger.error(f"Exception while posting a product on the gallery, will re-attempt to post {n_tries_left} times")
                        except Exception as e:
                            logger.error(f"Exception while posting a product on the gallery, will re-attemp to post:\n{e}")
                            n_tries_left -= 1
                            if n_tries_left == 0:
                                break
                            else:
                                logger.error(f"Exception while posting a product on the gallery, will re-attempt to post {n_tries_left} times")


def upload_image_to_gallery(observations, instruments, parameters, logger):

    import json

    parameters_copy = copy.deepcopy(parameters)
    parameters_copy['host_type'] = 'production'
    del parameters_copy['token']
    del parameters_copy['notebooks_folder']

    additional_information = 'parameters = ' + json.dumps(parameters_copy, indent=4)

    logger.debug(additional_information)

    isgri_params_dic_product_id, jemx1_params_dic_product_id, jemx2_params_dic_product_id = make_product_id_image(parameters)

    for instr in instruments:
        for source in observations:

            if not (('%s_img_fn' % instr) in source):
                logger.warning('%s_img_fn is not present, skipping' % instr)
                continue
            img_fn = source['%s_img_fn' % instr]
            api_cat_str = source['%s_source_catalog' % instr]
            sources = source['%s_raw_sources' % instr]
            data2 = source['%s_mosaic' % instr]
            sources2 = source['%s_sources' % instr]
            fluxed_catalog = source["%s_fluxed_catalog" % instr]        
            myhash = source['%s_myhash' % instr]
            sextractor_fname = source['%s_sextractor_fname' % instr]
            region_file_name = source['%s_region_file_name' % instr]
            outfile_name = source['%s_outfile_name' % instr]
            
            if fluxed_catalog is not None:
                source_list = list(fluxed_catalog['src_names'])
            else:
                source_list = []
                
            # from importlib import reload
            # reload(oda_integral_wrapper.wrapper)

            wrap2 = oda_integral_wrapper.wrapper.INTEGRALwrapper(token=parameters['token'], host_type=parameters['host_type'])
            # It builds a unique product id
            if 'rev_num' in parameters.keys() and 'obsid' in source.keys():
                if instr == 'isgri':
                    isgri_params_dic_product_id.update({'rev_num': str(parameters['rev_num']),
                                                    'obsid': source['obsid']})
                elif instr == 'jemx1':
                    jemx1_params_dic_product_id.update({'rev_num': str(parameters['rev_num']),
                                                'obsid': source['obsid']})
                elif instr == 'jemx2':
                    jemx2_params_dic_product_id.update({'rev_num': str(parameters['rev_num']),
                                                'obsid': source['obsid']})

            if instr == 'isgri':
                source['isgri_request_product_id'] = \
                    oda_api.api.DispatcherAPI.calculate_param_dict_id(isgri_params_dic_product_id)
            elif instr == 'jemx1':
                source['jemx1_request_product_id'] = \
                    oda_api.api.DispatcherAPI.calculate_param_dict_id(jemx1_params_dic_product_id)
            elif instr == 'jemx2':
                source['jemx2_request_product_id'] = \
                    oda_api.api.DispatcherAPI.calculate_param_dict_id(jemx2_params_dic_product_id)

            e1 = parameters['E1_keV']
            e2 = parameters['E2_keV']
            if 'jemx' in instr and 'J_E1_keV' in parameters.keys() and 'J_E2_keV' in parameters.keys():
                e1 = parameters['J_E1_keV']
                e2 = parameters['J_E2_keV']
            nrt_string = ''
            if parameters['data_version'].upper() == 'NRT':
                nrt_string = ' (NRT)'

            if 'RA' not in source.keys():
                if 'coord' in source.keys():
                    source['RA'] = source['coord'].ra.deg
                    source['DEC'] = source['coord'].dec.deg
                else:
                    # print(source.keys())
                    raise IOError("No coord in source")

            # This is just a patch in case Dec is used instead of DEC
            if 'Dec' in source:
                source['DEC'] = source['Dec']
                    
            product_title = ''
            if 'title' in source.keys():
                product_title = source['title']
            elif 'src_name' in parameters.keys():
                product_title = parameters['src_name']

            if 'rev_num' in parameters.keys():
                product_title += " Rev. " + str(parameters['rev_num'])
            
            product_title += nrt_string

            par_dict_gallery = {
                'token': parameters['token'],
                'RA': source['RA'],
                'DEC': source['DEC'],
                'e1_kev': e1,
                'e2_kev': e2,
                'product_title': product_title,
                'gallery_image_path': img_fn,
                'fits_file_path': [myhash + '_' + sextractor_fname + '.gz',
                                   myhash + '_' + outfile_name + '.gz',
                                   myhash + '_' + region_file_name],
                'src_name': source_list, 
                'instrument': instr,
                'insert_new_source': True,
                'force_insert_not_valid_new_source': True,
                'validate_source': True,
                'apply_fields_source_resolution': True,
                'product_type': '%s_image' % instr,
                'product_id': source['%s_request_product_id' % instr],
                'detected_sources': wrap2.get_html_from_fluxes(fluxed_catalog,
                                                               output_file=outfile_name.replace(
                                                                   '_mosaic.fits','_table.html')),
                # input parameters assuming they are in cell #1
                'additional_information': additional_information,
                'html_image': oda_api.plot_tools.OdaImage.get_js9_html(myhash + '_' + sextractor_fname + '.gz', 
                                                                    region_file = myhash + '_' + region_file_name, 
                                                                    js9_id='myJS9',
                                                base_url='/mmoda/gallery/sites/default/files'),
                'produced_by': parameters['origin_notebook'],
            }
            
            if 'obsid' in source.keys():
                par_dict_gallery['obsid'] = source['obsid']
            
            if 'tstart' in source:
                par_dict_gallery.update({'T1' : re.sub('\.\d+', '', source['tstart']), 
                                        'T2': re.sub('\.\d+', '', source['tstop'])})
            n_max_tries = 3
            n_tries_left = n_max_tries
            logger.debug('%s', par_dict_gallery)
            while True:
                try:
                    #print(par_dict_gallery)
                    d = wrap2.disp.post_data_product_to_gallery(**par_dict_gallery)
                    gallery_object = source.get("%s_gallery_object" % instr, [])
                    gallery_object.append(d.copy())
                    source.update({
                                "%s_gallery_object" % instr : gallery_object,
                        })
                    if 'error_message' not in d:
                        source.update({
                            'processed_mosaics':  True
                        })
                        break
                    else:
                        n_tries_left -= 1
                        if n_tries_left == 0:
                            break
                        else:
                            logger.warning(f"Exception while posting a product on the gallery, will re-attempt to post {n_tries_left} times")
                except Exception as e:
                    logger.warning(f"Exception while posting a product on the gallery, will re-attemp to post:\n{e}")
                    n_tries_left -= 1
                    if n_tries_left == 0:
                        logger.error(f"Exception while posting a product on the gallery, no attempts left.")
                        break
                    else:
                        logger.warning(f"Exception while posting a product on the gallery, will re-attempt to post {n_tries_left} times")


def upload_lc_to_gallery(observations, instruments, parameters, logger, use_energy_params=False):
    # Upload LC to Gallery

    wrap2 = oda_integral_wrapper.wrapper.INTEGRALwrapper(token=parameters['token'], 
                                                         host_type=parameters['host_type'])

    parameters_copy = copy.deepcopy(parameters)
    parameters_copy['host_type'] = 'production'
    del parameters_copy['token']
    del parameters_copy['notebooks_folder']

    additional_information = 'parameters = ' + json.dumps(parameters_copy, indent=4)

    for obs in observations:
        logger.debug(obs)
        for ins in instruments:
            sources_coord_obs = get_source_coords_catalog_from_obs(obs, ins)

            lc = obs.get('%s_lc' % ins, None)
            
            #Sets upload variables, defaults ISGRI
            e1 = 28
            e2 = 40
            systematic_fraction = parameters.get('systematic_fraction', 0.0)
            if not use_energy_params:
                if 'E1_isgri' in obs or 'E1_jemx' in obs:
                    k1 = 'E1_isgri'
                    k2 = 'E2_isgri'
                    if 'jemx' in ins:
                        systematic_fraction = parameters.get('jemx_systematic_fraction', 0.0)
                        if systematic_fraction == 0.0:
                            systematic_fraction = parameters.get('systematic_fraction', 0.0)
                        e1 = 3
                        e2 = 20
                        k1 = 'E1_jemx'
                        k2 = 'E2_jemx'
                        
                    e1 = obs.get(k1, e1)
                    e2 = obs.get(k2, e2)
                elif 'E1_keV' in parameters:
                    e1 = parameters['E1_keV']
                    e2 = parameters['E2_keV']
            else:
                if 'E1_keV' in parameters:
                    e1 = parameters['E1_keV']
                    e2 = parameters['E2_keV']
                if 'jemx' in ins:
                    if 'J_E1_keV' in parameters.keys():
                        e1 = parameters['J_E1_keV']
                    if 'J_E2_keV' in parameters.keys():
                        e2 = parameters['J_E2_keV']

            logger.info(f"E1_kev: {e1}")
            logger.info(f"E2_keV: {e2}")
            
            if lc is not None and type(lc) is not str:
                print(obs)
                if '%s_sources' % ins in obs:
                    sources = obs['%s_sources' % ins]
                else:
                    sources = [parameters['src_name']]
                image_product = oda_api.plot_tools.OdaLightCurve(lc)
                
                
                for i,src in enumerate(sources):
                    if 'MULTIPLE ID' in src:
                        continue
                    
                    logger.debug(src)
                    
                    if not os.path.isdir('out'):
                        os.mkdir('out')
                        
                    img_fn = image_product.get_image_for_gallery( in_source_name=src, 
                                                                systematic_fraction=systematic_fraction, 
                                                                output_folder='out')
                    

                    if 'rev_num' in parameters: 
                        par_dict_product_id = {
                            'source_name': src,
                            'obsid': obs['obsid'],
                            'instrument': '%s' % ins,
                            'product_type': '%s_lc' % ins, 
                            "rev_num": parameters['rev_num'],
                            'time_bin': parameters['lc_time_bin']
                        }
                    else:
                        par_dict_product_id = {    
                            'source_name': parameters['src_name'],
                            'e1_kev': e1,
                            'e2_kev': e2,
                            't1': obs['tstart'],
                            't2': obs['tstop'],
                            'radius': parameters['radius'],
                            'instrument': ins,
                            'product_type': '%s_lc' % ins,
                            'time_bin': parameters['lc_time_bin']
                        }

                    product_id = oda_api.api.DispatcherAPI.calculate_param_dict_id(par_dict_product_id)
                    if '%s_files' % ins in obs:
                        lc_fn = obs['%s_files' % ins]['fname'][i]
                    else:                        
                        lc_fn, tstart_mjd, tstop_mjd, exposure = \
                            oda_integral_wrapper.wrapper.INTEGRALwrapper.write_lc_fits_files(lc, src, '%d-%d'%(parameters['E1_keV'],parameters['E2_keV']))

                    nrt_string = ''
                    if parameters['data_version'].upper() == 'NRT':
                        nrt_string = ' (NRT)'
                        
                    par_dict = {    
                                'token': parameters['token'],
                                # if observation is incomplete (NRT) it would create new products at a later run
                                'T1': re.sub('\.\d+', '', obs['tstart']),
                                'T2': re.sub('\.\d+', '', obs['tstop']),
                                'RA': sources_coord_obs.get(src, [None, None])[0],
                                'DEC': sources_coord_obs.get(src, [None, None])[1],
                                'e1_kev': e1, 
                                'e2_kev': e2,
                                'product_title': src + ' %s light curve' % ins + nrt_string,
                                'gallery_image_path': img_fn,
                                'fits_file_path': [lc_fn],
                                'src_name': src, 
                                'instrument': ins,
                                'insert_new_source': True,
                                'force_insert_not_valid_new_source': True,
                                'validate_source': True,
                                'apply_fields_source_resolution': True,
                                'product_type': '%s_lc' % ins,
                                'product_id': product_id,
                                'additional_information': additional_information,
                                'html_image': image_product.get_html_image(src, systematic_fraction),
                                'produced_by': parameters['origin_notebook'],
                                'time_bin': parameters['lc_time_bin']
                    }
                    if 'obsid' in obs.keys():
                        par_dict.update({'obsid': obs['obsid']})
                    
                    n_max_tries = 3
                    n_tries_left = n_max_tries
                    while True:
                        try:
                            d = wrap2.disp.post_data_product_to_gallery(**par_dict)
                            gallery_object = obs.get("%s_gallery_object" % ins, [])
                            gallery_object.append(d.copy())
                            obs.update({
                                "%s_gallery_object" % ins : gallery_object,
                                })
                            if 'error_message' not in d:
                                obs.update({
                                    'processed_lc':  True
                                })
                                break
                            else:
                                n_tries_left -= 1
                                if n_tries_left == 0:
                                    break
                                else:
                                    logger.error(f"Exception while posting a product on the gallery, will re-attempt to post {n_tries_left} times")
                        except Exception as e:
                            logger.error(f"Exception while posting a product on the gallery, will re-attemp to post:\n{e}")
                            n_tries_left -= 1
                            if n_tries_left == 0:
                                break
                            else:
                                logger.error(f"Exception while posting a product on the gallery, will re-attempt to post {n_tries_left} times")

        #print(obs)