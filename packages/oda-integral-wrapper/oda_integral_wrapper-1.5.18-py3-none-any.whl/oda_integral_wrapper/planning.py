from __future__ import print_function

import os
import re
import socket
import time
import glob

import astropy.io.fits as fits
import pandas as pd
import numpy as np
import oda_integral_wrapper.itime as itime

current_hostname = socket.gethostname()

computing_node_regex_patter = 'node(\d*).cluster.astro.unige.ch'

if 'lesta' in current_hostname or re.match(computing_node_regex_patter, current_hostname) is not None:
    arc_url = "/isdc/arc/rev_3"
    pvphase_url = "/isdc/pvphase/nrt/ops"
else:
    arc_url = "ftp://isdcarc.unige.ch/arc/rev_3"
    pvphase_url = "ftp://isdcarc.unige.ch/pvphase/nrt/ops"


def interpret_exclude(s):
    return map(str.strip, s.split())


def get_current_pad(rev_num=0, num_ao=2, columns_to_remove=['KEY_PROP_ID']):
    from datetime import date

    ao_start = 0
    ao_stop = int(date.today().year)-2012

    if int(rev_num) > 0:
        ijd = itime.converttime('REVNUM', rev_num, 'IJD')
        utc = itime.converttime('IJD', ijd.split()[1], 'UTC')
        year = int(utc[0:4])
        ao_stop = year - 2002
        ao_start = max(0, ao_stop-num_ao)
        print("searching pad from AO%02d to AO%02d" % (ao_start, ao_stop) )

    ao_list = []

    for ao_i in range(ao_start, ao_stop+1):
        print("need AO pad for %02d" % ao_i)
        current_hostname = socket.gethostname()
        pad_pattern = arc_url + "/aux/org/AO%02d/pad_%02d" % (ao_i, ao_i) + "_%04d.fits"
        pad_list = []
        for num in range(1, 1000):
            pad_test = pad_pattern % num
            try:
                ff = fits.open(pad_test)
                pad_list.append(pad_test)
                ff.close()
            except Exception:
                print(pad_test + " not found")
                break
        print("found {} pads as {}".format(len(pad_list), pad_pattern))

        ao = None
        for pad in pad_list[::-1]:
            try:
                ao = fits.getdata(pad, 1)        
                for cc in columns_to_remove:
                    if cc in ao.columns.names:
                        print(f'deleting {cc} from {pad}')
                        new_cols = ao.columns.del_col(cc)
                        ao = fits.FITS_rec.from_columns(new_cols)
                print(f"found valid pad {pad}")
                ao_list.append(ao)
                break
            except Exception as e:
                print("WARNING: unable to open pad {}, choosing previous one".format(pad), e)

    return np.concatenate(ao_list)


def get_pointings(revid, kind="historic", getdata=True, max_version=5, data_version=None):
    if getdata:
        getter = lambda x: fits.getdata(x, 1)
    else:
        getter = lambda x: helpers.fits_table_to_pandas(x)

    if data_version is None:
        if kind == 'historic':
            data_version = '001'
        else:
            data_version = '000'


    if kind == 'historic':
        if data_version == '001':
            pt = arc_url + "/aux/adp/%s.%s/pointing_definition_%s.fits.gz" % (revid, data_version, kind)
        else:
            pt = pvphase_url + "/aux/adp/%s.%s/pointing_definition_%s.fits.gz" % (revid, data_version, kind)
    elif kind == 'predicted':
        pt = pvphase_url + "/aux/adp/%s.%s/pointing_definition_%s_" % (revid, data_version, kind)
    else:
        raise IOError('no kind \'' + kind + '\'')
    pods = []

    if kind == 'predicted':
        for num in range(1, max_version):
            pt_test = pt + '%04d.fits' % num
            try:
                ff = fits.open(pt_test)
                pods.append(pt_test)
                ff.close()
            except:
                print(pt_test + " not found")
                continue
    elif kind == 'historic':
        try:
            ff = fits.open(pt)
            pods.append(pt)
            ff.close()
        except:
            try:
                pt=pt.replace('.gz', '')
                ff = fits.open(pt)
                pods.append(pt)
                ff.close()
            except:
                print(pt + " and " + pt+'.gz not found')

    if len(pods) == 0:
        raise Exception("no pointing definition as " + pt + ' or ' + pt+'.gz')
    print("Found pods ", pods)
    pod = pods[-1]
    return getter(pod)


def get_pod(revid, lower_range=1, upper_range=16):
    
    """gets a POD file from auxiliary files

    Args:
        revid (str): REvolution ID, e.g.  0102 2524 0080
        upper_range (int, optional): It will loop to search POD with names up to upper_range and retain the upper one. Defaults to 16.

    Returns:
        list: POD LIST of entries in the fits file
    """    
    pod_list = []

    pvphase_pod_folder_path = os.path.join(pvphase_url, f"aux/org/{revid}")
    arc_pod_folder_path = os.path.join(arc_url, f"aux/org/{revid}")

    if not pvphase_pod_folder_path.startswith('ftp://'):

        if os.path.exists(pvphase_pod_folder_path):
            fits_list = glob.glob(os.path.join(pvphase_pod_folder_path, f"pod_{revid}_*.fits"))
            for fits_file in fits_list:
                print(f"{fits_file} found")
                ff = fits.open(fits_file)
                pod_list.append(fits_file)
                ff.close()

        elif os.path.exists(arc_pod_folder_path):
            fits_gz_list = glob.glob(os.path.join(arc_pod_folder_path, f"pod_{revid}_*.fits*"))
            for fits_gz_file in fits_gz_list:
                print(f"{fits_gz_file} found")
                ff = fits.open(fits_gz_file)
                pod_list.append(fits_gz_file)
                ff.close()
        else:
            return None
    else:
        for num in range(lower_range, upper_range):
            pod_test = pvphase_url + "/aux/org/%s/pod_%s_%04d.fits" % (revid, revid, num)
            try:
                ff = fits.open(pod_test)
                pod_list.append(pod_test)
                ff.close()
            except:
                print(pod_test + " not found")
                pod_test = arc_url + "/aux/org/%s/pod_%s_%04d.fits.gz" % (revid, revid, num)
                try:
                    ff = fits.open(pod_test)
                    pod_list.append(pod_test)
                    ff.close()
                except:
                    print(pod_test + " not found")
                    try:
                        pod_test = pod_test.replace('.gz', '')
                        ff = fits.open(pod_test)
                        pod_list.append(pod_test)
                        ff.close()
                    except:
                        print(pod_test + ' not found')
        
    if len(pod_list) > 0:
        return sorted(pod_list)[-1]
    
    print("no pod file has been found")
    return None


def planned_pointings(t1, t2, slews=False, onlyassigned=True,):
    #t1 = itime.Time(_t1)
    #t2 = itime.Time(_t2)
    #print(getattr(t1, 'REVNUM'))
    print(vars(t1))
    d = None
    for rev in range(int(t1.REVNUM), int(t2.REVNUM)+1):
        d_rev = get_pointings(rev, "predicted", getdata=False)
        if d is None:
            d = d_rev
        else:
            d = pd.concat([d,d_rev])

    m=(d.TIME >= t1.IJD) & (d.TIME < t2.IJD)
    if not slews:
        m &= d.POINTING_TYPE == 0

    if onlyassigned:
        m &= map(str.strip,d.EXPID) != ""

    #print("planned", t1.UTC, t2.UTC, len(d[m]))

    return d[m]

def planned_pointings_by_proposal(t1,t2,only_available=False):
    scwids = [s+"0010" for s in planned_pointings(t1, t2).POINTING_ID]
    d = extract_scwid_pi(scwids, only_available=only_available)
    #print("searching planned_pointings_by_proposal", len(scwids),"got",len(d))

    groups = {}
    for group in set(d.groupname):
        groups[group] = d[d.groupname == group]
     #   print("group", group, only_available, len(groups[group]))

    return groups

def summarize_planned_pointings_by_proposal(t1,t2,processed=[]):
    groups = []

    try:
        planned_available = planned_pointings_by_proposal(t1, t2, only_available=True)
    except Exception as e:
        print("unable to find historic planning", e)
        raise

    planned_all = planned_pointings_by_proposal(t1, t2, only_available=False)
    for group in sorted(set(planned_all.keys()+planned_available.keys())):
        try:
            d = planned_available[group]
        except KeyError:
            print("\033[31mERROR: group {} not available in planned, have {}\033[0m".format(
                    group,
                    planned_available.keys(),
                ))
            continue        

        d_all = planned_all[group]

        assert len(set(d.piname)) == 1
        groups.append(dict(
            group=group,
            piname=list(set(d.piname))[0],
            total_exposure_planned=np.nansum(d_all.duration),
            total_pointings_planned=len(d_all),
            exposure_processed = 0.,
            exposure_available = np.nansum(d.duration),
            total_pointings_available=len(d_all),
        ))

    return groups


class PointingDefinitions:
    pointing_definition_by_rev = {}

    def for_rev(self, revid, kind, only_available=False):
        if revid not in self.pointing_definition_by_rev:
            print("revid", revid)
            self.pointing_definition_by_rev[revid] = get_pointings(revid, kind=kind)

        return self.pointing_definition_by_rev[revid]

    def for_scw(self, scwid, kind):
        pointid = scwid[:8]
        rev_pdef = self.for_rev(scwid[:4], kind)

        m = (rev_pdef['POINTING_ID'] == pointid) & \
            (rev_pdef['POINTING_TYPE'] == 0)

        return rev_pdef[m]

def extract_scwid_pi(scwids, only_available=True, pdef_kind=None):
    if only_available:
        scwids_interpreted = pathtools.interpret_scwids(scwids, return_path=False)
        print("found:", len(scwids_interpreted), "searching for", len(scwids))
    else:
        scwids_interpreted = scwids

    pad = get_current_pad()
    
    pod_by_rev = {}

    pointing_definitions=PointingDefinitions()

    dicts = []
    for scwid in scwids_interpreted:
        revid = scwid[:4]
        pointid = scwid[:8]

        if pdef_kind is None:
            if only_available:
                pdef_kind = "historic"
            else:
                pdef_kind = "predicted"

        scw_pdef = pointing_definitions.for_scw(scwid,pdef_kind)

        expids = list(set(scw_pdef['EXPID']))

        if len(expids) > 1:
            print(expids)
            print("scwid:", scwid)
            print("WARNING: multiple expids!")
            print("WARNING: pointing skipped")
            continue

        if len(expids) == 0:
            print("no executed exposure ids for "+scwid+"?")
            expid = ""
            duration = 0
        else:
            expid = expids[0]
            duration = scw_pdef['DURATION'][0]

        if expid.strip() != "":
            if revid not in pod_by_rev:
                fn = get_pod(revid)
                pod_by_rev[revid] = fits.open(fn)[1].data

            m = pod_by_rev[revid]["EXP_ID"] == expid

            assert(len(pod_by_rev[revid][m]['OBS_ID']) == 1)
            obsid = pod_by_rev[revid][m]['OBS_ID'][0]
            srcname = pod_by_rev[revid][m]['SRC_NAME'][0]
            propid = obsid[:7]

            m = pad['PROP_ID'] == propid.encode()
            #print(propid)
            #print(scwid)#,map(str.strip,set(pad[m].DD_EMAIL)))
            if len(set(pad[m]['DD_EMAIL'])) == 1:
                dd_email = pad[m]['DD_EMAIL'][0]
                prop_title = pad[m]['PROP_TITLE'][0]
                pi_email = pad[m]['PI_EMAIL'][0]
            elif len(set(pad[m]['DD_EMAIL'])) == 0:
                dd_email = "??"
                prop_title = "Unknown Proposal"
                pi_email = "??"

            #print(pad[m])

            try:
                piname = pad['PI_NAME'][m][0].decode()
            except:
                piname = "Public"
        else:
            obsid = ""
            srcname = ""
            propid = ""
            piname = "unassigned"
            dd_email = ""
            pi_email = ""
            prop_title = "undefined"

        dicts.append(
            dict(
                scwid=scwid,
                duration=duration,
                pointid=pointid,
                revid=revid,
                expid=expid,
                obsid=obsid,
                srcname=srcname,
                propid=propid,
                piname=piname,
                dd_email=dd_email,
                pi_email=pi_email,
                prop_title=prop_title,
                groupname=pathtools.format_directory_name(piname.replace("\'","").split()[0])+"_"+propid
            )
        )

    return pd.DataFrame(dicts)

def write_scwid_lists(pattern, outputdirlist=None):
    if outputdirlist is not None and os.path.exists(outputdirlist):
        os.remove(outputdirlist)

    try:
        df = extract_scwid_pi(pattern, True)
    except Exception as e:
        print("unable to extract historic pointings!", e)
        df = extract_scwid_pi(pattern, True, pdef_kind="predicted")

    if len(df) == 0:
        print("nothing here")
        return

    rootdir = "/home/scientist/MOSAIC/"

    tag = "" if "TAG" not in os.environ else os.environ["TAG"]

    exclude_isgri = []
    exclude_jemx = []
    if 'EXCLUDE' in os.environ:
        exclude_isgri += interpret_exclude(os.environ['EXCLUDE'])
        exclude_jemx += interpret_exclude(os.environ['EXCLUDE'])
    if 'EXCLUDE_ISGRI' in os.environ:
        exclude_isgri += interpret_exclude(os.environ['EXCLUDE_ISGRI'])
    if 'EXCLUDE_JEMX' in os.environ:
        exclude_jemx += interpret_exclude(os.environ['EXCLUDE_JEMX'])

    try:
        m_exclude_isgri = np.ones(len(df.piname), bool)
        m_exclude_jemx = np.ones(len(df.piname), bool)
    except:
        print(df)
        raise

    for no_isgri in exclude_isgri:
        m_exclude_isgri &= df.scwid != no_isgri

    for no_jemx in exclude_jemx:
        m_exclude_jemx &= df.scwid != no_jemx

    if tag != "":
        tag = "_" + tag

    dirlist = []
    for groupname in set(df.groupname):
        m = df.groupname == groupname
        rev = df.revid[m]

        obs_tag = tag
        for no_isgri in df.scwid[~m_exclude_isgri & m]:
            obs_tag += "_no.isgri." + no_isgri

        for no_jemx in df.scwid[~m_exclude_jemx & m]:
            obs_tag += "_no.jemx." + no_jemx

        if rev.min() == rev.max():
            mydir = rootdir + "/{rev}_{me}/{groupname}/{nscw}_{scw1}_{scw2}{tag}".format(
                rev=rev.max(),
                me=who_am_i(),
                groupname=groupname,
                src="_".join([pathtools.format_directory_name(srcname) for srcname in sorted(set((df[m].srcname)))]),
                nscw=sum(m),
                scw1=df[m].pointid.min(),
                scw2=df[m].pointid.max(),
                tag=obs_tag,
            )
        else:
            mydir = rootdir + "/{rev1}_{rev2}_{me}/{groupname}/{nscw}_{scw1}_{scw2}{tag}".format(
                rev1=rev.min(),
                rev2=rev.max(),
                me=who_am_i(),
                groupname=groupname,
                src="_".join([pathtools.format_directory_name(srcname) for srcname in sorted(set((df[m].srcname)))]),
                nscw=sum(m),
                scw1=df[m].pointid.min(),
                scw2=df[m].pointid.max(),
                tag=obs_tag,
            )

        if not os.path.exists(mydir):
            os.makedirs(mydir)

        symlink=os.path.dirname(os.path.realpath(mydir)) + "/latest"
        if os.path.exists(symlink):
            os.remove(symlink)
        os.symlink(os.path.basename(mydir),symlink)

        fn = mydir + "/scw_obs.list"
        scwid_list = df[m].scwid
        open(fn, "w").write("\n".join(scwid_list))
        print("created", fn, "with", len(scwid_list))

        fn = mydir + "/scw_obs_ibis.list"
        scwid_list = df[m & m_exclude_isgri].scwid
        open(fn, "w").write("\n".join(scwid_list))
        if sum(m_exclude_isgri & m) < sum(m):
            print("created reduced", fn, "with", len(scwid_list))

        fn = mydir + "/scw_obs_jemx1.list"
        scwid_list = df[m & m_exclude_jemx].scwid
        open(fn, "w").write("\n".join(scwid_list))
        if sum(m_exclude_jemx & m) < sum(m):
            print("created reduced", fn, "with", len(scwid_list))

        dirlist.append(mydir)
    if outputdirlist:
        open("/tmp/mosaic_dir_list", "w").write("\n".join(dirlist))


def find_results_of_planned_pointings(t1, t2, allowed_fraction=0.7):
    planned=planned_pointings(t1,t2)

    stats={'complete':[],'anomalies':[]}

    allowed_fraction=0.8

    for i,pr in planned.iterrows():
      #  print("searching for",pr.POINTING_ID)

        try:
            scwid=pr.POINTING_ID.decode()+"0010"
            d_ii = fits.open(pathtools.scwid2isgri_ima_path(scwid))[2]
            d_swg = fits.open(pathtools.pointid2path(pr.POINTING_ID) + "/swg.fits")[1]

            if d_swg.header['TELAPSE']<=pr.DURATION*allowed_fraction:   # threshold, some are too long!
                stats['anomalies'].append(dict(
                        scwid=scwid,
                        reason=dict(
                                summary='short',
                                expected=pr.DURATION,
                                elapsed=d_swg.header['TELAPSE'],
                                ii_elapsed=d_ii.header['TELAPSE'],
                                isgri_ontime=d_ii.header['ONTIME']
                        )
                    ))
            elif d_ii.header['telapse']<=pr.DURATION*allowed_fraction:   # threshold, some are too long!
                stats['anomalies'].append(dict(
                        scwid=scwid,
                        reason=dict(
                                summary='short isgri',
                                expected=pr.DURATION,
                                elapsed=d_swg.header['TELAPSE'],
                                ii_elapsed=d_ii.header['TELAPSE'],
                                isgri_ontime=d_ii.header['ONTIME']
                        )
                    ))
            elif d_ii.header['ONTIME']<=pr.DURATION*allowed_fraction:   # threshold, some are too long!
                stats['anomalies'].append(dict(
                        scwid=scwid,
                        reason=dict(
                                summary='short isgri ontime',
                                expected=pr.DURATION,
                                elapsed=d_swg.header['TELAPSE'],
                                ii_elapsed=d_ii.header['TELAPSE'],
                                isgri_ontime=d_ii.header['ONTIME']
                        )
                    ))

            if d_ii.header['TELAPSE']>=pr.DURATION/allowed_fraction:
                stats['complete'].append(scwid)
                stats['anomalies'].append(dict(
                    scwid=scwid,
                    reason=dict(
                        summary='long',
                        expected=pr.DURATION,
                        elapsed=d_swg.header['TELAPSE'],
                        ii_elapsed=d_ii.header['TELAPSE'],
                        isgri_ontime=d_ii.header['ONTIME']
                    )
                ))

        except (IOError, IndexError) as e:

           # print("did not find",e)
            delay_h=(itime.now().IJD-pr.TIME)*24

            if delay_h<6:
                if delay_h>0:
                    print(pr.TIME, pr.POINTING_ID, pr.DURATION, "late for %.3lg h" % delay_h)
                else:
                    print(pr.TIME, pr.POINTING_ID, pr.DURATION, "expected execution in %.3lg h" % -delay_h)

                stats['anomalies'].append(dict(
                    scwid=scwid,
                    reason=dict(
                        summary='expected',
                        expected=pr.DURATION,
                        delay=delay_h,
                    )
                ))

            else:
                stats['anomalies'].append(dict(
                    scwid=scwid,
                    reason=dict(
                        summary='missing',
                        expected=pr.DURATION,
                    )
                ))

    return stats

