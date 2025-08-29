from __future__ import print_function

import re
import os
import time
import astropy.io.fits as fits
import copy
import oda_integral_wrapper.wrapper

def now():
    return Time(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))

def converttime(f,i,t):
    wrap = oda_integral_wrapper.wrapper.INTEGRALwrapper()
    return wrap.converttime(f, i, t)

class Time(object):

    def __new__(cls,input_obj,format=None):
        if type(input_obj) == Time:
            #return copy.copy(input_obj)
            return input_obj

        obj = super(Time, cls).__new__(cls)
        obj.interpret_time(input_obj, format=format)
        #self.interpret_time(input_obj,format=format)
        return obj


    def converttime(self,f,i,t):
        try:
            return converttime(f,i,t)
        except RuntimeError('Error in converttime'):
            if t == "":
                return dict([(t, converttime(f, i, t)[t]) for t in ["UTC", "IJD"]])

    def adopt(self, time_dict):
        for k, v in time_dict.items():
            setattr(self, k, v)

        try:
            self.IJD = float(self.IJD)
        except ValueError:
            if self.IJD.startswith("Boundary"):
                self.IJD = [float(kk) for kk in self.IJD.split()[1:]]
            else:
                self.IJD = [float(kk) for kk in self.IJD.split(":")]

        if hasattr(self,'SCWID'):
            self.SCWID=self.SCWID.replace(" is close","")



    def interpret_time(self, input_time, format=None):
        if format is not None:
            return self.adopt(self.converttime(format, input_time, "ANY"))

        if isinstance(input_time, str) and re.match("\d{12}",input_time):
            return self.adopt(self.converttime("SCWID", input_time, "ANY"))

        try:
            float_input = float(input_time)
            return self.adopt(self.converttime("IJD", "%.20lg" % float_input, "ANY"))
        except ValueError:
            try:
                if isinstance(input_time,str):
                    if re.match("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", input_time) or \
                       re.match("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d*", input_time):
                        return self.adopt(self.converttime("UTC", input_time, "ANY"))
                    elif re.match("\d{12}"):
                        return self.adopt(self.converttime("SCWID", input_time, "ANY"))
                    else:
                        raise ValueError
            except:
                raise TypeError

    def __sub__(self, other):
        assert isinstance(other,Time)

        return Time.IJD-other.IJD

def list_scws_in_range_slow(_t1,_t2):
    t1 = Time(_t1)
    t2 = Time(_t2)

    tc = t1

    scw=tc.SCWID

    #yield scw
    while tc.IJD<t2.IJD:
        yield scw

        print("SCW:",scw)

        next_ijd=Time(scw).IJD[1] + 10. / 24 / 3600

        print ("NEXT:",next_ijd)

        tc=Time(next_ijd)
        scw=tc.SCWID

def list_scws_in_range(_t1,_t2, only_pointing=True):
    t1 = Time(_t1)
    t2 = Time(_t2)

    d=fits.getdata(os.environ["REP_BASE_PROD"]+"/idx/scw/GNRL-SCWG-GRP-IDX.fits",1)

    m=(d['TSTART']>t1.IJD) & (d['TSTOP']<t2.IJD)

    if only_pointing:
        m&=d['SW_TYPE']=='POINTING'

    return sorted(d['SWID'][m])
