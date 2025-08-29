'''
Module with FWHM plugin class
'''
import numpy
import matplotlib.pyplot as plt

from dmu.stats.zfit        import zfit
from dmu.logging.log_store import LogStore

log = LogStore.add_logger('dmu:plotting:fwhm')
# --------------------------------------------
class FWHM:
    '''
    Class meant to be used to calculate Full Width at Half Maximum
    as a Plotter1d plugin
    '''
    # -------------------------
    def __init__(self, cfg : dict, val : numpy.ndarray, wgt : numpy.ndarray, maxy : float):
        self._cfg     = cfg
        self._arr_val = val
        self._arr_wgt = wgt
        self._maxy    = maxy
    # -------------------------
    def _normalize_yval(self, arr_pdf_val : numpy.ndarray) -> None:
        max_pdf_val = numpy.max(arr_pdf_val)
        arr_pdf_val*= self._maxy / max_pdf_val

        return arr_pdf_val
    # -------------------------
    def _get_fwhm(self, arr_x : numpy.ndarray, arr_y : numpy.ndarray) -> float:
        maxy = numpy.max(arr_y)
        arry = numpy.where(arr_y > maxy/2.)[0]
        imax = arry[ 0]
        imin = arry[-1]

        x1 = arr_x[imax]
        x2 = arr_x[imin]

        if self._cfg['plot']:
            plt.plot([x1, x2], [maxy/2, maxy/2], linestyle=':', linewidth=1, color='k')

        return x2 - x1
    # -------------------------
    def run(self) -> float:
        '''
        Runs plugin and return FWHM
        '''
        [minx, maxx] = self._cfg['obs']

        log.info('Running FWHM pluggin')
        obs = zfit.Space('mass', limits=(minx, maxx))
        pdf= zfit.pdf.KDE1DimISJ(obs=obs, data=self._arr_val, weights=self._arr_wgt)

        xval = numpy.linspace(minx, maxx, 200)
        yval = pdf.pdf(xval)
        yval = self._normalize_yval(yval)

        if self._cfg['plot']:
            plt.plot(xval, yval, linestyle='-', linewidth=2, color='gray')

        fwhm = self._get_fwhm(xval, yval)

        return fwhm
# --------------------------------------------
