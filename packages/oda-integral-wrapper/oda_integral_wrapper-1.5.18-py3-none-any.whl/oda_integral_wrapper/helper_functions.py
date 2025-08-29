import time

from astroquery.simbad import Simbad

def call_simbad_query_object(src_name, logger=None):
    result = None
    for i in range(10):
        try:
            result = Simbad.query_object(src_name)
            return result
        except Exception as e:
            if logger is not None:
                logger.debug(f'Issues when calling querying the object {src_name} from Simbad: {repr(e)}')
            time.sleep(2)

    return result