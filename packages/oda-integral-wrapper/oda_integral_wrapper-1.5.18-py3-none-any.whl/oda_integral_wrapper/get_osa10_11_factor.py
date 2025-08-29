from autologging import logged
import subprocess
import json
import yaml


@logged
def get_existing_dict():
    try:
        with open('secret.yaml', 'r') as ff:
            secret = yaml.full_load(ff)
    except:
        secret = None

    if secret is None:
        cmd = 'git clone https://gitlab.astro.unige.ch/oda/integral-osa-additional-parameters.git'
        get_existing_dict._log.warning("It will not be possible to upload the recomputed factor")
    else:

        cmd = 'git clone https://oauth2:%s@gitlab.astro.unige.ch/oda/integral-osa-additional-parameters.git' % (
            secret['token'])
        cmd += ';cd integral-osa-additional-parameters;' + \
               'git remote set-url origin ' + \
               'https://oauth2:%s@gitlab.astro.unige.ch/oda/integral-osa-additional-parameters.git' % (
                   secret['token'])
        get_existing_dict._log.info("It will be possible to upload the recomputed factor")

    if (subprocess.call(cmd, shell=True)):
        get_existing_dict._log.warning('Cloning error')
    else:
        get_existing_dict._log.info("Cloned the parameter repository")

    subprocess.call('cd integral-osa-additional-parameters;git pull', shell=True)
    try:
        with open('integral-osa-additional-parameters/osa11-10-conversion.json', 'r') as ff:
            conversion_dict = json.load(ff)
    except:
        conversion_dict = {}
    get_existing_dict._log.debug(conversion_dict)

    return conversion_dict


@logged
def get_osa10_11_conversion_factor(E1_isgri_keV, E2_isgri_keV, radius=10., oda_platform="staging-1-2",
                                   s_max=50, lc_time_bin=3000):
    import os.path

    conversion_dict = get_existing_dict()

    factor = conversion_dict.get('%.0f-%.0f' % (E1_isgri_keV, E2_isgri_keV))
    if factor is None:
        compute_factor = True
    else:
        compute_factor = False

    if compute_factor:

        if not os.path.isfile('secret.yaml'):
            get_osa10_11_conversion_factor._log.warning(
                "As the file secret.yaml does not exist, I do not perform the computation of the value")
            return -1.0

        import oda_integral_wrapper.wrapper
        wrap = oda_integral_wrapper.wrapper.INTEGRALwrapper(host_type=oda_platform)

        source_name = 'Crab'
        r1644 = wrap.converttime('REVNUM', '1644', 'IJD')
        r1648 = wrap.converttime('REVNUM', '1648', 'IJD')
        tstart = wrap.converttime('IJD', r1644.split()[1], 'UTC')
        tstop = wrap.converttime('IJD', r1648.split()[2], 'UTC')
        from astroquery.simbad import Simbad
        from astropy import units as u
        from astropy.coordinates import SkyCoord
        import numpy as np

        simbad = Simbad.query_object(source_name)
        coord = SkyCoord(simbad['RA'], simbad['DEC'], unit=[u.hour, u.deg])
        _ = coord.fk5

        get_osa10_11_conversion_factor._log.debug(
            "Coordinates for %s are RA=%.4f, Dec=%.4f" % (source_name, coord.ra.deg[0], coord.dec.deg[0]))

        ra = coord.ra.deg[0]
        dec = coord.dec.deg[0]
        revs = [{'coord': coord, 'tstart': tstart, 'tstop': tstop, 'name': source_name, 'label': 'OSA10.2'},
                {'coord': coord, 'tstart': tstart, 'tstop': tstop, 'name': source_name, 'label': 'OSA11.0'}]

        import astroquery.heasarc

        Heasarc = astroquery.heasarc.Heasarc()

        def _get_scw_list(ra_obj, dec_obj, rr, start_date, end_date):
            rr = Heasarc.query_region(
                position=SkyCoord(ra_obj, dec_obj, unit='deg'),
                radius=f"{rr} deg",
                mission='intscw',
                time=start_date + " .. " + end_date,
                good_isgri=">1000",
            )

            rr.sort('SCW_ID')

            return rr

        def get_scw_list(ra_obj, dec_obj, rr, start_date, end_date):
            for ii in range(10):
                try:
                    return _get_scw_list(ra_obj, dec_obj, rr, start_date, end_date)
                except Exception as e:
                    get_osa10_11_conversion_factor._log.warning(e)
            raise RuntimeError

        for i, source in enumerate(revs):
            get_osa10_11_conversion_factor._log.debug(source['coord'].ra.deg, source['tstart'])
            r = get_scw_list(ra, dec, radius, tstart, tstop)

            scwids = r['SCW_ID']
            scwver = r['SCW_VER']
            get_osa10_11_conversion_factor._log.debug(source['name'], ' nscw=%d' % (len(scwids)))
            revs[i].update(scwids=scwids)
            revs[i].update(scwver=scwver)
            revs[i].update({'RA_SCX': r['RA'], 'DEC_SCX': r['DEC']})

        api_cat = {
            "cat_frame": "fk5",
            "cat_coord_units": "deg",
            "cat_column_list": [
                [0, 7],
                ["1A 0535+262", "Crab"],
                [125.4826889038086, 1358.7255859375],
                [84.72280883789062, 83.63166809082031],
                [26.312734603881836, 22.016284942626953],
                [-32768, -32768],
                [2, 2],
                [0, 0],
                [0.0002800000074785203, 0.0002800000074785203]],
            "cat_column_names": [
                "meta_ID",
                "src_names",
                "significance",
                "ra",
                "dec",
                "NEW_SOURCE",
                "ISGRI_FLAG",
                "FLAG",
                "ERR_RAD"
            ],
            "cat_column_descr":
                [
                    ["meta_ID", "<i8"],
                    ["src_names", "<U11"],
                    ["significance", "<f8"],
                    ["ra", "<f8"],
                    ["dec", "<f8"],
                    ["NEW_SOURCE", "<i8"],
                    ["ISGRI_FLAG", "<i8"],
                    ["FLAG", "<i8"],
                    ["ERR_RAD", "<f8"]
                ],
            "cat_lat_name": "dec",
            "cat_lon_name": "ra"
        }

        all_lc = {}
        for source in revs:

            name = source['name'] + source['label']
            scw_list = [ss + '.' + vv.strip() for ss, vv in zip(np.array(source['scwids'], dtype=str),
                                                                np.array(source['scwver'], dtype=str)) if
                        ss.endswith('0')]

            out_str = 'We process %d science windows: ' % (len(scw_list)) + ' '.join(scw_list)
            get_osa10_11_conversion_factor._log.info(out_str)

            if all_lc.get(name, None) is None:
                all_lc.update({name: {'scw_list': scw_list}})

            combined_data = wrap.long_scw_list_call(scw_list, s_max=s_max, sleep_time=120,
                                                    instrument="isgri",
                                                    product='isgri_lc',
                                                    E1_keV=E1_isgri_keV,
                                                    E2_keV=E2_isgri_keV,
                                                    query_type='Real',
                                                    osa_version=source['label'],
                                                    product_type='Real',
                                                    time_bin=lc_time_bin,
                                                    selected_catalog=json.dumps(api_cat))

            all_lc[name].update({'isgri': combined_data})
            wrap.write_lc_fits_files(combined_data, source_name,
                                     '%d-%d-%s' % (E1_isgri_keV, E2_isgri_keV, source['label']))

        t1_10, dt_10, r_10, dr_10 = wrap.get_lc(all_lc['CrabOSA10.2']['isgri'], 'Crab')
        t1_11, dt_11, r_11, dr_11 = wrap.get_lc(all_lc['CrabOSA11.0']['isgri'], 'Crab')

        factor = np.mean(r_10) / np.mean(r_11)
        get_osa10_11_conversion_factor._log.info("Conversion factor is %f" % factor)
        conversion_dict.update({'%.0f-%.0f' % (E1_isgri_keV, E2_isgri_keV): float(factor)})
        import oda_integral_wrapper
        with open('integral-osa-additional-parameters/osa11-10-conversion.json', 'w') as ff:
            json.dump(conversion_dict, ff)
        subprocess.call('cd integral-osa-additional-parameters;' +
                        'git config  user.email "%s";' % (oda_integral_wrapper.__author_email__) +
                        'git config --global user.name "%s";' % (oda_integral_wrapper.__author__) +
                        'git commit osa11-10-conversion.json -m "Update factor %.0f-%.0f";' % (
                        E1_isgri_keV, E2_isgri_keV) +
                        'git push ', shell=True)

    return factor
