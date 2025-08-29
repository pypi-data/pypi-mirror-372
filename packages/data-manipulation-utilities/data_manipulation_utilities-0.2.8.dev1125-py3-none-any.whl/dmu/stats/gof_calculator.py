'''
Module holding GofCalculator class
'''
from contextlib import contextmanager
from functools import lru_cache

import zfit
import numpy
import pandas as pnd

from scipy                  import stats
from zfit.core.basepdf      import BasePDF   as zpdf
from zfit.core.parameter    import Parameter as zpar
from dmu.logging.log_store  import LogStore

log = LogStore.add_logger('dmu:stats:gofcalculator')
# ------------------------
class GofCalculator:
    '''
    Class used to calculate goodness of fit from zfit NLL
    '''
    _disabled = False # If true, it will not run, returning chi2=0 and pvalue=1
    # ---------------------
    def __init__(self, nll, ndof : int = 10):
        if GofCalculator._disabled:
            return

        self._nll     = nll
        self._ndof    = ndof

        self._pdf     = self._pdf_from_nll()
        self._data_in = self._data_from_nll()
        self._data_np = self._data_np_from_data(self._data_in)
        self._data_zf = zfit.Data.from_numpy(obs=self._pdf.space, array=self._data_np)
    # ---------------------
    def _data_np_from_data(self, dat) -> numpy.ndarray:
        if isinstance(dat, numpy.ndarray):
            return dat

        if isinstance(dat, zfit.Data):
            return zfit.run(zfit.z.unstack_x(dat))

        if isinstance(dat, pnd.DataFrame):
            return dat.to_numpy()

        if isinstance(dat, pnd.Series):
            dat    = pnd.DataFrame(dat)
            return dat.to_numpy()

        data_type = str(type(dat))
        raise ValueError(f'Data is not a numpy array, zfit.Data or pandas.DataFrame, but {data_type}')
    # ---------------------
    def _pdf_from_nll(self) -> zpdf:
        l_model = self._nll.model
        nmodel = len(l_model)
        if nmodel != 1:
            for model in l_model:
                log.error(model)
            raise ValueError(f'Not found one and only one model, but {nmodel}')

        return l_model[0]
    # ---------------------
    def _data_from_nll(self) -> zpdf:
        l_data = self._nll.data
        if len(l_data) != 1:
            raise ValueError('Not found one and only one dataset')

        return l_data[0]
    # ---------------------
    def _get_float_pars(self) -> int:
        npar     = 0
        s_par    = self._pdf.get_params()
        for par in s_par:
            if par.floating:
                npar+=1

        return npar
    # ---------------------
    @lru_cache(maxsize=10)
    def _get_binning(self) -> tuple[int, float, float]:
        min_x = numpy.min(self._data_np)
        max_x = numpy.max(self._data_np)
        nbins = self._ndof + self._get_float_pars()

        log.debug(f'Nbins: {nbins}')
        log.debug(f'Range: [{min_x:.3f}, {max_x:.3f}]')

        return nbins, min_x, max_x
    # ---------------------
    def _get_pdf_bin_contents(self) -> numpy.ndarray:
        nbins, min_x, max_x  = self._get_binning()
        _, arr_edg = numpy.histogram(self._data_np, bins = nbins, range=(min_x, max_x))

        size = arr_edg.size

        l_bc = []
        for i_edg in range(size - 1):
            low = arr_edg[i_edg + 0]
            hig = arr_edg[i_edg + 1]

            var : zpar = self._pdf.integrate(limits = [low, hig])
            val = var.numpy()[0]
            l_bc.append(val * self._data_np.size)

        return numpy.array(l_bc)
    #------------------------------
    def _get_data_bin_contents(self) -> numpy.ndarray:
        nbins, min_x, max_x = self._get_binning()
        arr_data, _         = numpy.histogram(self._data_np, bins = nbins, range=(min_x, max_x))
        arr_data            = arr_data.astype(float)

        return arr_data
    #------------------------------
    @lru_cache(maxsize=30)
    def _calculate_gof(self) -> tuple[float, int, float]:
        log.debug('Calculating GOF')

        arr_data    = self._get_data_bin_contents()
        arr_modl    = self._get_pdf_bin_contents()

        log.debug(40 * '-')
        log.debug(f'{"Data":<20}{"Model":<20}')
        log.debug(40 * '-')
        for dval, mval in zip(arr_data, arr_modl):
            log.debug(f'{dval:<20.3f}{mval:<20.3f}')
        log.debug(40 * '-')

        norm        = numpy.sum(arr_data) / numpy.sum(arr_modl)
        arr_modl    = norm * arr_modl
        arr_res     = arr_modl - arr_data

        arr_chi2    = numpy.divide(arr_res ** 2, arr_data, out=numpy.zeros_like(arr_data), where=arr_data!=0)
        sum_chi2    = numpy.sum(arr_chi2)

        pvalue      = 1 - stats.chi2.cdf(sum_chi2, self._ndof)
        pvalue      = float(pvalue)

        log.debug(f'Chi2: {sum_chi2:.3f}')
        log.debug(f'Ndof: {self._ndof}')
        log.debug(f'pval: {pvalue:<.3e}')

        return sum_chi2, self._ndof, pvalue
    # ---------------------
    def get_gof(self, kind : str) -> float:
        '''
        Parameters
        -----------------
        kind: Type of goodness of fit: pvalue, chi2, chi2/ndof

        Returns 
        -----------------
        Goodness of fit of a given kind
        '''
        if GofCalculator._disabled:
            return {'pvalue' : 1, 'chi2' : 0, 'chi2/ndof' : 0}[kind]

        chi2, ndof, pval = self._calculate_gof()

        if kind == 'pvalue':
            return pval

        if kind == 'chi2/ndof':
            return chi2/ndof

        if kind == 'chi2':
            return chi2

        raise NotImplementedError(f'Invalid goodness of fit: {kind}')
    # ---------------------
    @classmethod
    def disabled(cls, value : bool):
        '''
        Context manager used to disable this tool

        Parameters
        ---------------
        value: If true it will disable the tool
        '''
        old_val = cls._disabled
        cls._disabled = value

        if value:
            log.info('GofCalculator is turned off')

        @contextmanager
        def _context():
            try:
                yield
            finally:
                cls._disabled = old_val

        return _context()
# ------------------------
