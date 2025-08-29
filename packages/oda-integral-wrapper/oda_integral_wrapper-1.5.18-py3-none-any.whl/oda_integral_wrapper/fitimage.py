#import astropy.io.fits as pyfits
from numpy import *
import astropy.wcs as pywcs
from autologging import logged

#
# Adapted from https://github.com/volodymyrss/dda-imagesources/
#

__author__ = "Volodymyr Savchenko"

__all__ = ['FitMosaicSources']


@logged
class FitMosaicSources(object):

    def __init__(self, mosaic_hdulist, cat, free_sigma=False, free_constant=False):

    #cat=[('Tycho SNR',(6.3583,64.1528))]
    #cat=[('Cas A',(350.85,58.810))]

        self.cat = cat
        self.mosaic_hdu_list = mosaic_hdulist
        self.fluxes = ones(len(cat))
        self.radius = 5
        self.free_constant = free_constant
        self.usexy = False
        self.sigma = 1.1578793
        self.free_sigma = free_sigma
        self.get_wcs()
        self.validate_cat()

    def get_wcs(self):
        f = self.mosaic_hdu_list

        intensity_i = []

        for ie, e in enumerate(f):
            if 'IMATYPE' in e.header and ( e.header['IMATYPE'] == "INTENSITY" or e.header['IMATYPE'] == "RECONSTRUCTED"):
                    intensity_i.append(ie)

        for i_i in intensity_i:
            #print self.e1,self.e2
            e = f[i_i]
            rate = e.data
            self.wcs = pywcs.WCS(e.header)
            self.data_shape = rate.shape

    def validate_cat(self):
        if not hasattr(self, 'wcs'):
            raise RuntimeError('No WCS attribute')
        
        new_cat = []
        for (sn, (ra, dec)), flux in zip(self.cat, self.fluxes):
            #print (sn,ra,dec,flux)

            if self.usexy:
                sx, sy = [ra], [dec]
            else:
                sx, sy = self.wcs.wcs_world2pix([ra], [dec], 0)
            
            if isnan(sx[0]) or isnan(sy[0]) or sx[0] > self.data_shape[0] or sy[0] > self.data_shape[1]:
                self.__log.warning('WARNING, source %s not in FOV' % sn)
            else:
                new_cat.append( (sn, (ra, dec)) )
        
        self.cat= new_cat
        self.fluxes = ones(len(self.cat))
        if len (new_cat) == 0:
            self.__log.warning('Null catalog in fit image')
        

    def model(self):
        if not hasattr(self, 'wcs'):
            raise RuntimeError('No WCS attribute')

       # print("data shape",self.data_shape)

        model = (zeros(self.data_shape)) # x,y?..
        mask = (zeros(self.data_shape, dtype=bool))
        #
        # CF Need to transpose and invert
        #
        y, x = meshgrid(arange(model.shape[0]), arange(model.shape[1]))
        x = transpose(x)
        y = transpose(y)
        sigma = self.sigma

        center = None

        self.centers=[]

        # print(self.cat,self.fluxes)

        for (sn, (ra, dec)), flux in zip(self.cat, self.fluxes):
            # print (sn,ra,dec,flux)

            if self.usexy:
                sx, sy = [ra], [dec]
            else:
                sx, sy = self.wcs.wcs_world2pix([ra], [dec], 0)
            
            if isnan(sx[0]) or isnan(sy[0]):
                continue
            if sx[0] > model.shape[0] or sy[0] > model.shape[1]:
                continue

            # print('The source coordinates', sx[0], sy[0])
            # print('The shape %d %d' %(model.shape[0], model.shape[1]))
            self.centers.append([sx[0], sy[0]])

            if center is None:
                center = {'x': sx[0], 'y': sy[0], 'n': 1}
            else:
                center['n'] += 1
                center['x'] = (center['x']*(center['n']-1)+sx[0])/center['n']
                center['y'] = (center['y']*(center['n']-1)+sy[0])/center['n']

            model += exp(-((x-sx)**2+(y-sy)**2)/sigma**2/2)*flux

            mask ^= (((x - sx) ** 2 + (y - sy) ** 2) < self.radius ** 2)

        if self.free_constant:
            model += self.constant

        # c = center['x'], center['y'], self.radius
        # print("center", c)
        
        # mask = ((x - c[0]) ** 2 + (y - c[1]) ** 2) < (c[2] ** 2)
        # the above is the original one it looks an error
        # mask = (((x - c[1]) ** 2 + (y - c[0]) ** 2) < c[2] ** 2)

        # print('Mask: ', sum(mask))
        return model, mask

    def fit_image(self,rate,variance):

        if len(self.cat) ==0:
            return [], []

        import nlopt

        def myfunc(x, grad):
            # print(":::::::", x)

            if self.free_sigma:
                self.sigma = x[0]
                x = x[1:]

            if self.free_constant:
                self.constant = x[0]
                x = x[1:]

            #
            # The fitting variable, passed to model implicitly !
            #
            self.fluxes = x[:]

            local_model, mask = self.model()

            # Manipulation to avoid divide by zero
            r = rate * 0.0
            ind_ok = (variance > 0) & (isfinite(variance))
            r[ind_ok] = (rate[ind_ok]-local_model[ind_ok])/ (variance[ind_ok]**0.5)

            self.residuals = r
            self.residuals[~mask] = 0
            ndof = r[mask].flatten().shape[0]
            if ndof > 0:
                residual = (r[mask]**2).sum()/ndof
            else:
                residual = 0    
            self.__log.debug("-------------> %s %f %f %f %f", x, local_model.sum(), residual, ndof, residual)
            return residual

        x0 = []
        xmin = []
        xmax = []

        if self.free_sigma:
            x0.append(1)
            xmin.append(0.1)
            xmax.append(2)
        elif self.free_constant:
            x0.append(0)
            xmin.append(-10)
            xmax.append(10)
            self.constant = 0.
            #print('SETTING')
        else:
            x0 += [0.0]*len(self.fluxes)

        loc_mod, loc_mask = self.model()
        # print(3 * (array(rate[loc_mask]).max()))
        if sum(loc_mask) > 0: 
            xmin += [-5*abs(array(rate[loc_mask]).max())]*len(self.fluxes)
            xmax += [10*abs(array(rate[loc_mask]).max())]*len(self.fluxes)
        else:
            return None, None
            # This woul lead to inconsistency, returning None is better
            # xmin += [-100.] *len(self.fluxes)
            # xmax += [100.] *len(self.fluxes)
            

        opt = nlopt.opt(nlopt.LN_BOBYQA, len(x0))
        #opt = nlopt.opt(nlopt.LN_COBYLA, len(x0))
        opt.set_lower_bounds(xmin)
        opt.set_upper_bounds(xmax)
        opt.set_min_objective(myfunc)
        opt.set_xtol_rel(1e-4)
        #print('fsad', self.cat, self.fluxes, x0, xmin,xmax)
        try:
            x = opt.optimize(x0)
        except nlopt.RoundoffLimited:
            # self.fluxes is assigned at each iteration of myfunc
            x = self.fluxes
            self.__log.warning('We had a RoundOff Limited exception, using the output in any case: %s', x)


        # print('CHECKKKK')
        # for t1, t2, t3, t4 in zip(rate.flatten(), self.model()[0].flatten(), self.model()[1].flatten(), variance.flatten()) :
        #     if t3:
        #         print(t1, t4, t2, t3)
        # print('END CHECKKKK')

        if self.free_sigma:
            self.sigma = x[0]
            x = x[1:]

        if self.free_constant:
            self.constant = x[0]
            x = x[1:]

        self.fluxes = x[:]


        self.flux_errors = [variance[int(c[1]), int(c[0])]**0.5 for c in self.centers]

        # for i, c in enumerate(self.centers):
        #     print(self.cat[i][0], c[0], c[1], rate[int(c[1]), int(c[0])], variance[int(c[1]), int(c[0])]**0.5,
        #           self.fluxes[i], self.flux_errors[i])
        # minf = opt.last_optimum_value()
        # print("optimum at ", x)
        # print("minimum value = ", minf)
        # print("result code = ", opt.last_optimize_result())


        return self.fluxes, self.flux_errors

    def get_fluxes(self):
        #
        # for convenience
        #
        f = self.mosaic_hdu_list

        intensity_i = []
        variance_i = []

        for ie, e in enumerate(f):
            if 'IMATYPE' in e.header and ( e.header['IMATYPE'] == "INTENSITY" or e.header['IMATYPE'] == "RECONSTRUCTED"):
                    intensity_i.append(ie)

            if 'IMATYPE' in e.header and e.header['IMATYPE'] == "VARIANCE":
                    variance_i.append(ie)

        spectra = []
        src_names = [cc[0] for cc in self.cat]
        for i_i, i_v in zip(intensity_i, variance_i):
            #print self.e1,self.e2

            e = f[i_i]
            rate = e.data
            self.wcs = pywcs.WCS(e.header)
            self.data_shape = rate.shape

            variance = f[i_v].data
            
            self.fluxes, self.flux_errors = self.fit_image(rate, variance)
            
            spectra.append((src_names, self.fluxes, self.flux_errors))


        #savetxt("spectra.txt",spectra)
        self.spectra=spectra

        return spectra
