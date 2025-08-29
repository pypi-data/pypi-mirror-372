'''
Module containing derived classes from ZFit minimizer
'''
from typing import Union
import numpy

import zfit
import matplotlib.pyplot as plt

from zfit.result                   import FitResult
from zfit.core.basepdf             import BasePDF           as zpdf
from zfit.minimizers.baseminimizer import FailMinimizeNaN
from dmu.stats.utilities           import print_pdf
from dmu.stats.gof_calculator      import GofCalculator
from dmu.logging.log_store         import LogStore

log = LogStore.add_logger('dmu:ml:minimizers')
# ------------------------
class AnealingMinimizer(zfit.minimize.Minuit):
    '''
    Class meant to minimizer zfit likelihoods by using multiple retries,
    each retry is preceeded by the randomization of the fitting parameters
    '''
    # ------------------------
    def __init__(self, ntries : int, pvalue : float = -1, chi2ndof : float = -1):
        '''
        ntries  : Try this number of times
        pvalue  : Stop tries when this threshold is reached
        chi2ndof: Use this value as a threshold to stop fits
        '''
        self._ntries   = ntries
        self._pvalue   = pvalue
        self._chi2ndof = chi2ndof

        self._check_thresholds()
        self._l_bad_fit_res : list[FitResult] = []

        super().__init__()
    # ------------------------
    def _check_thresholds(self) -> None:
        good_pvalue  = 0 <= self._pvalue < 1
        good_chi2dof = self._chi2ndof > 0

        if good_pvalue and good_chi2dof:
            raise ValueError('Threshold for both chi2 and pvalue were specified')

        if good_pvalue:
            log.debug(f'Will use threshold on pvalue with value: {self._pvalue}')
            return

        if good_chi2dof:
            log.debug(f'Will use threshold on chi2ndof with value: {self._chi2ndof}')
            return

        raise ValueError('Neither pvalue nor chi2 thresholds are valid')
    # ------------------------
    def _is_good_gof(self, ch2 : float, pvl : float) -> bool:
        is_good_pval = pvl > self._pvalue   and self._pvalue   > 0
        is_good_chi2 = ch2 < self._chi2ndof and self._chi2ndof > 0
        is_good      = is_good_pval or is_good_chi2

        if is_good_pval:
            log.info(f'Stopping fit, found p-value: {pvl:.3f} > {self._pvalue:.3f}')

        if is_good_chi2:
            log.info(f'Stopping fit, found chi2/ndof: {ch2:.3f} > {self._chi2ndof:.3f}')

        if not is_good:
            log.debug(f'Could not read threshold, pvalue/chi2: {pvl:.3f}/{ch2:.3f}')

        return is_good
    # ------------------------
    def _is_good_fit(self, res : FitResult) -> bool:
        good_fit = True

        if not res.valid:
            log.debug('Skipping invalid fit')
            good_fit = False

        if res.status != 0:
            log.debug('Skipping fit with bad status')
            good_fit = False

        if not res.converged:
            log.debug('Skipping non-converging fit')
            good_fit = False

        if not good_fit:
            self._l_bad_fit_res.append(res)

        return good_fit
    # ------------------------
    def _get_gof(self, nll) -> tuple[float, float]:
        log.debug('Checking GOF')

        gcl = GofCalculator(nll)
        pvl = gcl.get_gof(kind='pvalue')
        ch2 = gcl.get_gof(kind='chi2/ndof')

        return ch2, pvl
    # ------------------------
    def _randomize_parameters(self, nll):
        '''
        Will move floating parameters of PDF according
        to uniform PDF
        '''

        log.debug('Randomizing parameters')
        l_model = nll.model
        if len(l_model) != 1:
            raise ValueError('Not found and and only one model')

        model = l_model[0]
        s_par = model.get_params(floating=True)
        for par in s_par:
            ival = par.value()
            fval = numpy.random.uniform(par.lower, par.upper)
            par.set_value(fval)
            log.debug(f'{par.name:<20}{ival:<15.3f}{"->":<10}{fval:<15.3f}{"in":<5}{par.lower:<15.3e}{par.upper:<15.3e}')
    # ------------------------
    def _pick_best_fit(self, d_chi2_res : dict) -> Union[FitResult,None]:
        nres = len(d_chi2_res)
        if nres == 0:
            log.error('No fits found')
            return None

        l_chi2_res= list(d_chi2_res.items())
        l_chi2_res.sort()
        chi2, res = l_chi2_res[0]

        log.warning(f'Picking out best fit from {nres} fits with chi2: {chi2:.3f}')

        return res
    #------------------------------
    def _set_pdf_pars(self, res : FitResult, pdf : zpdf) -> None:
        '''
        Will set the PDF floating parameter values as the result instance
        '''
        l_par_flt = list(pdf.get_params(floating= True))
        l_par_fix = list(pdf.get_params(floating=False))
        l_par     = l_par_flt + l_par_fix

        d_val = { par.name : dc['value'] for par, dc in res.params.items()}

        log.debug('Setting PDF parameters to best result')
        for par in l_par:
            if par.name not in d_val:
                par_val = par.value().numpy()
                log.debug(f'Skipping {par.name} = {par_val:.3e}')
                continue

            val = d_val[par.name]
            log.debug(f'{"":<4}{par.name:<20}{"->":<10}{val:<20.3e}')
            par.set_value(val)
    # ------------------------
    def _pdf_from_nll(self, nll) -> zpdf:
        l_model = nll.model
        if len(l_model) != 1:
            raise ValueError('Cannot extract one and only one PDF from NLL')

        return l_model[0]
    # ------------------------
    def _print_failed_fit_diagnostics(self, nll) -> None:
        for res in self._l_bad_fit_res:
            print(res)

        arr_mass = nll.data[0].numpy()

        plt.hist(arr_mass, bins=60)
        plt.show()
    # ------------------------
    def minimize(self, nll, **kwargs) -> FitResult:
        '''
        Will run minimization and return FitResult object
        '''

        d_chi2_res : dict[float,FitResult] = {}
        for i_try in range(self._ntries):
            try:
                res = super().minimize(nll, **kwargs)
            except (FailMinimizeNaN, ValueError, RuntimeError) as exc:
                log.error(f'{i_try:02}/{self._ntries:02}{"Failed":>20}')
                log.debug(exc)
                self._randomize_parameters(nll)
                continue

            if not self._is_good_fit(res):
                log.warning(f'{i_try:02}/{self._ntries:02}{"Bad fit":>20}')
                continue

            chi2, pvl = self._get_gof(nll)
            log.info(f'{i_try:02}/{self._ntries:02}{chi2:>20.3f}')
            d_chi2_res[chi2] = res

            if self._is_good_gof(chi2, pvl):
                return res

            self._randomize_parameters(nll)

        res = self._pick_best_fit(d_chi2_res)
        if res is None:
            self._print_failed_fit_diagnostics(nll)
            pdf = nll.model[0]
            print_pdf(pdf)

            raise ValueError('Fit failed')

        pdf = self._pdf_from_nll(nll)
        self._set_pdf_pars(res, pdf)

        return res
# ------------------------
