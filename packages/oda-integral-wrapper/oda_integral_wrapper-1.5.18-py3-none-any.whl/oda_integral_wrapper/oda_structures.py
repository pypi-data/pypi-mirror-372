
from oda_api.data_products import LightCurveDataProduct


class OsaLightCurve(LightCurveDataProduct):
    def __init__(self,
                 name='osa_lc',
                 file_name=None,
                 data=None,
                 file_dir=None,
                 prod_prefix=None,
                 src_name='',
                 meta_data={}):

        if meta_data == {} or meta_data is None:
            self.meta_data = {'product': 'osa_lc',
                              'instrument': 'integral', 'src_name': src_name}
        else:
            self.meta_data = meta_data

        self.meta_data['time'] = 'TIME'
        self.meta_data['rate'] = 'RATE'
        self.meta_data['rate_err'] = 'ERROR'

        data.name = name

        super(OsaLightCurve, self).__init__(name=name,
                                            data=data,
                                            name_prefix=prod_prefix,
                                            file_dir=file_dir,
                                            file_name=file_name,
                                            meta_data=meta_data)
