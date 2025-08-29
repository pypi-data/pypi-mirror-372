'''
Module holding zfitter class
'''
# pylint: disable=wrong-import-order, import-error

import contextlib
import pprint
from typing                   import Protocol, Union
from functools                import lru_cache

import numpy
import pandas as pd

from dmu.logging              import messages  as mes
from dmu.stats.zfit           import zfit
from dmu.logging.log_store    import LogStore
from dmu.stats.gof_calculator import GofCalculator

from zfit.minimizers.strategy import FailMinimizeNaN
from zfit.result              import FitResult     as zres
from zfit.interface           import ZfitModel     as zpdf
from zfit.interface           import ZfitParameter as zpar
from zfit.data                import Data          as zdat

log = LogStore.add_logger('dmu:statistics:fitter')
#------------------------------
class ParameterHolder(Protocol):
    '''
    Class representing object with `get_params` method
    '''
    # ----------------------
    def get_params(self, floating : bool) -> set[zpar]:
        ...
#------------------------------
class FitterGofError(Exception):
    '''
    Exception used when GoF cannot be calculated
    '''
#------------------------------
class FitterFailedFit(Exception):
    '''
    Exception used when fitter fails
    '''
#------------------------------
class Fitter:
    '''
    Class meant to be an interface to underlying fitters
    '''
    # This is meant to be used through a context manager
    # To allow the errors to be calculated or not
    _turn_off_errors  = False

    # These are substrings found in tensorflow messages
    # that are pretty useless and need to be hidden
    _l_hidden_tf_lines= [
        'Loaded cuDNN version',
        'abnormal_detected_host @',
        'Skipping loop optimization for Merge',
        'Creating GpuSolver handles for stream',
        'Loaded cuDNN version',
        'All log messages before absl::InitializeLog()']
    #------------------------------
    def __init__(self, pdf : zpdf, data : zdat):
        '''
        Parameters
        ---------------
        pdf : PDF to fit
        data: Datasets to fit
        '''
        self._data_in = data
        self._pdf     = pdf

        self._data_zf : zdat 
        self._data_np : numpy.ndarray
        self._obs     : zfit.Space

        self._ndof           = 10
        self._pval_threshold = 0.01
        self._initialized    = False
    #------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_data()

        self._initialized = True
    #------------------------------
    def _check_data(self):
        if   isinstance(self._data_in, numpy.ndarray):
            data_np = self._data_in
        elif isinstance(self._data_in, zfit.Data):
            data_np = zfit.run(zfit.z.unstack_x(self._data_in)) # convert original data to numpy array, needed by _calc_gof
        elif isinstance(self._data_in, pd.DataFrame):
            data_np = self._data_in.to_numpy()
        elif isinstance(self._data_in, pd.Series):
            self._data_in = pd.DataFrame(self._data_in)
            data_np = self._data_in.to_numpy()
        else:
            data_type = str(type(self._data_in))
            raise ValueError(f'Data is not a numpy array, zfit.Data or pandas.DataFrame, but {data_type}')

        data_np       = self._check_numpy_data(data_np)
        self._data_np = data_np
        if not isinstance(self._data_in, zfit.Data):
            self._data_zf = zfit.Data.from_numpy(obs=self._pdf.space, array=data_np)
        else:
            self._data_zf = self._data_in
    #------------------------------
    def _check_numpy_data(self, data):
        shp = data.shape
        if   len(shp) == 1:
            pass
        elif len(shp) == 2:
            _, jval = shp
            if jval != 1:
                raise ValueError(f'Invalid data shape: {shp}')
        else:
            raise ValueError(f'Invalid data shape: {shp}')

        ival = data.shape[0]

        data = data[~numpy.isnan(data)]
        data = data[~numpy.isinf(data)]

        fval = data.shape[0]

        if ival != fval:
            log.warning(f'Data was trimmed for inf and nan: {ival} -> {fval}')

        return data
    #------------------------------
    def _bin_pdf(self):
        nbins, min_x, max_x = self._get_binning()
        _, arr_edg = numpy.histogram(self._data_np, bins = nbins, range=(min_x, max_x))

        size = arr_edg.size

        l_bc = []
        for i_edg in range(size - 1):
            low = arr_edg[i_edg + 0]
            hig = arr_edg[i_edg + 1]

            var = self._pdf.integrate(limits = [low, hig])
            val = var.numpy()[0]
            l_bc.append(val * self._data_np.size)

        return numpy.array(l_bc)
    #------------------------------
    def _bin_data(self):
        nbins, min_x, max_x = self._get_binning()
        arr_data, _ = numpy.histogram(self._data_np, bins = nbins, range=(min_x, max_x))
        arr_data    = arr_data.astype(float)

        return arr_data
    #------------------------------
    @lru_cache(maxsize=10)
    def _get_binning(self):
        min_x = numpy.min(self._data_np)
        max_x = numpy.max(self._data_np)
        d_par = self.get_float_pars(pdf=self._pdf)
        nbins = self._ndof + len(d_par)

        log.debug(f'Nbins: {nbins}')
        log.debug(f'Range: [{min_x:.3f}, {max_x:.3f}]')

        return nbins, min_x, max_x
    #------------------------------
    @staticmethod
    def get_float_pars(pdf : zpdf) -> dict[str,zpar]:
        '''
        Parameters
        ---------------
        pdf: Zfit PDF

        Returns
        ---------------
        Dictionary with keys as parameter names 
        and values as floating parameters
        '''
        npar     = 0
        s_par    = pdf.get_params()
        for par in s_par:
            if par.floating:
                npar+=1

        d_par = {par.name : par for par in s_par}

        return d_par
    #------------------------------
    def _reshuffle_pdf_pars(self):
        '''
        Will move floating parameters of PDF according
        to uniform PDF
        '''

        s_par = self._pdf.get_params(floating=True)
        for par in s_par:
            ival = par.value()
            fval = numpy.random.uniform(par.lower, par.upper)
            par.set_value(fval)
            log.debug(f'{par.name:<20}{ival:<15.3f}{"->":<10}{fval:<15.3f}{"in":<5}{par.lower:<15.3e}{par.upper:<15.3e}')
    #------------------------------
    def _set_pdf_pars(self, res):
        '''
        Will set the PDF floating parameter values as the result instance
        '''
        l_par_flt = list(self._pdf.get_params(floating= True))
        l_par_fix = list(self._pdf.get_params(floating=False))
        l_par     = l_par_flt + l_par_fix

        d_val = { par.name : dc['value'] for par, dc in res.params.items()}

        log.debug('Setting PDF parameters to best result')
        for par in l_par:
            if par.name not in d_val:
                log.debug(f'Skipping {par.name} = {par.value().numpy():.3e}')
                continue

            val = d_val[par.name]
            log.debug(f'{"":<4}{par.name:<20}{"->":<10}{val:<20.3e}')
            par.set_value(val)
    #------------------------------
    def _get_ranges(self, cfg : dict) -> list:
        if 'ranges' not in cfg:
            return [None]

        ranges_any = cfg['ranges']

        ranges = [ tuple(elm) for elm in ranges_any ]
        log.info('-' * 30)
        log.info(f'{"Low edge":>15}{"High edge":>15}')
        log.info('-' * 30)
        for rng in ranges:
            log.info(f'{rng[0]:>15.3e}{rng[1]:>15.3e}')

        return ranges
    #------------------------------
    def _get_subdataset(self, cfg : dict) -> zdat:
        if 'nentries' not in cfg:
            return self._data_zf

        nentries_out = cfg['nentries']
        arr_inp      = self._data_zf.to_numpy().flatten()
        nentries_inp = len(arr_inp)
        if nentries_inp <= nentries_out:
            log.warning(f'Input dataset in smaller than output dataset, {nentries_inp} < {nentries_out}')
            return self._data_zf

        has_weights = self._data_zf.weights is not None

        if has_weights:
            arr_wgt = self._data_zf.weights.numpy()
            arr_inp = numpy.array([arr_inp, arr_wgt]).T

        arr_out = numpy.random.choice(arr_inp, size=nentries_out, replace=False)
        if has_weights:
            arr_out = arr_out.T[0]
            arr_wgt = arr_out.T[1]
        else:
            arr_wgt = None

        data = zfit.data.from_numpy(array=arr_out, weights=arr_wgt, obs=self._data_zf.space)

        return data
    #------------------------------
    def _get_binned_observable(self, nbins : int):
        obs = self._pdf.space
        [[minx]], [[maxx]] = obs.limits

        binning = zfit.binned.RegularBinning(nbins, minx, maxx, name=obs.label)
        obs_bin = zfit.Space(obs.label, binning=binning)

        return obs_bin
    #------------------------------
    def _get_nbins(self, cfg : dict) -> Union[None, int]:
        if 'likelihood' not in cfg:
            return None

        if 'nbins' not in cfg['likelihood']:
            return None

        return cfg['likelihood']['nbins']
    #------------------------------
    def _get_nll(self, data_zf, constraints, frange, cfg):
        nbins     = self._get_nbins(cfg)
        if nbins is None:
            log.info('No binning was specified, will do unbinned fit')
            pdf = self._pdf
        else:
            log.info(f'Using {nbins} bins for fit')
            obs     = self._get_binned_observable(nbins)
            pdf     = zfit.pdf.BinnedFromUnbinnedPDF(self._pdf, obs)
            data_zf = data_zf.to_binned(obs)

        if not self._pdf.is_extended and nbins is None:
            nll = zfit.loss.UnbinnedNLL(        model=pdf, data=data_zf, constraints=constraints, fit_range=frange)
            return nll

        if     self._pdf.is_extended and nbins is None:
            nll = zfit.loss.ExtendedUnbinnedNLL(model=pdf, data=data_zf, constraints=constraints, fit_range=frange)
            return nll

        if frange is not None:
            raise ValueError('Fit range cannot be defined for binned likelihoods')

        if not self._pdf.is_extended:
            nll = zfit.loss.BinnedNLL(          model=pdf, data=data_zf, constraints=constraints)
            return nll

        if     self._pdf.is_extended:
            nll = zfit.loss.ExtendedBinnedNLL(  model=pdf, data=data_zf, constraints=constraints)
            return nll

        raise ValueError('Likelihood was neither Binned nor Unbinned nor Extended nor non-extended')
    #------------------------------
    def _get_full_nll(self, cfg : dict):
        constraints = Fitter.get_gaussian_constraints(
            obj = self._pdf,
            cfg = cfg.get('constraints'))

        ranges      = self._get_ranges(cfg)
        data_zf     = self._get_subdataset(cfg)
        l_nll       = [ self._get_nll(data_zf, constraints, frange, cfg) for frange in ranges ]
        nll         = sum(l_nll[1:], l_nll[0])

        return nll
    #------------------------------
    @staticmethod
    def print_pars(cfg : dict, d_par : dict[str,zpar]) -> None:
        '''
        Will print current values parameters in cfg['print_pars'] list, if present
        '''

        if 'print_pars' not in cfg:
            return

        l_par_name = cfg['print_pars']
        d_par_val  = { name : par.value().numpy() for name, par in d_par.items() if name in l_par_name}

        l_name = list(d_par_val.keys())
        l_value= list(d_par_val.values())

        l_form = [   f'{var:<10}' for var in l_name]
        header = ''.join(l_form)

        l_form = [f'{val:<10.3f}' for val in l_value]
        parval = ''.join(l_form)

        log.info(header)
        log.info(parval)
    #------------------------------
    @staticmethod
    def minimize(nll, cfg : dict, ndof : int = 10) -> tuple[zres, tuple]:
        '''
        Parameters
        --------------
        nll : Negative log likelihood
        cfg : Configuration dictionary used for minimization, it should look like:
              print_pars: # Optional, if not passed, will not print parameter values
                - par 1
                - par 2
                ...
              minimization: # Optional, if used, will pass these settings to zfit.minimizers.Minuit()
                setting : value
                setting : value
                ...
        ndof: Number of degrees of freedom needed for goodness of fit calculation through chi2
              by default 10 as recommended by statistics experts

        Returns
        --------------
        Tuple with:

        - Zfit result object
        - Tuple with goodness of fit (pvalue, ndof, chi2)
        '''
        min_cfg = {} if 'minimization' not in cfg else cfg['minimization']

        if not min_cfg:
            log.debug('Using default zfit minimization options')
        else:
            log.debug('Overriding default zfit minimization config with')
            for key, val in min_cfg.items():
                log.debug(f'{key:<30}{val:<30}')

        mnm = zfit.minimize.Minuit(**min_cfg)
        with mes.filter_stderr(banned_substrings=Fitter._l_hidden_tf_lines):
            res = mnm.minimize(nll)

        if not Fitter._turn_off_errors:
            log.debug('Calculating errors')
            res.hesse(name='minuit_hesse')
        else:
            log.warning('Not calculating errors')

        # TODO: Add a check to make sure the errors are added here
        # if not, raise

        gcl = GofCalculator(nll, ndof=ndof)
        try:
            pval = gcl.get_gof(kind='pvalue')
            chi2 = gcl.get_gof(kind='chi2')
        except FitterGofError as exc:
            raise FitterGofError('Cannot calculate GOF') from exc

        stat = res.status

        log.debug(f'{chi2:<10.3f}{pval:<10.3e}{stat:<10}')
        pdf   = nll.model[0] # This class is not meant for simultaneous fits
                             # There should only be one PDF
        d_par = Fitter.get_float_pars(pdf=pdf)
        Fitter.print_pars(cfg, d_par=d_par)

        return res, (chi2, ndof, pval)
    #------------------------------
    def _gof_is_bad(self, gof : tuple[float, int, float]) -> bool:
        chi2, ndof, pval = gof

        good_ndof = 0 <= ndof < numpy.inf
        good_chi2 = 0 <= chi2 < numpy.inf
        good_pval = 0 <= pval < numpy.inf

        return not (good_chi2 and good_pval and good_ndof)
    #------------------------------
    def _fit_retries(self, cfg : dict) -> tuple[dict, zres]:
        ntries       = cfg['strategy']['retry']['ntries']
        pvalue_thresh= cfg['strategy']['retry']['pvalue_thresh']
        ignore_status= cfg['strategy']['retry']['ignore_status']

        nll        = self._get_full_nll(cfg = cfg)
        d_pval_res = {}
        last_res   = None
        for i_try in range(ntries):
            try:
                res, gof = self.minimize(nll, cfg, ndof=self._ndof)
            except (FailMinimizeNaN, FitterGofError, RuntimeError):
                self._reshuffle_pdf_pars()
                log.warning(f'{i_try:03}/{ntries:03} failed due to exception')
                continue

            last_res = res
            bad_fit  = res.status != 0 or not res.valid

            if not ignore_status and bad_fit:
                self._reshuffle_pdf_pars()
                log.info(f'{i_try:03}/{ntries:03} failed, status/validity: {res.status}/{res.valid}')
                continue

            chi2, _, pval   = gof

            if self._gof_is_bad(gof=gof):
                log.debug('Reshufling and skipping, found bad gof')
                self._reshuffle_pdf_pars()
                continue

            d_pval_res[chi2]=res

            if pval > pvalue_thresh:
                log.info(f'Reached {pval:.3f} (> {pvalue_thresh:.3f}) threshold after {i_try + 1} attempts')
                return {chi2 : res}, res

            log.info(f'{i_try:03}/{ntries:03} good fit: {res.status}/{res.valid}')
            self._reshuffle_pdf_pars()

        if last_res is None:
            raise FitterFailedFit('Cannot find any valid fit')

        return d_pval_res, last_res
    #------------------------------
    def _pick_best_fit(self, d_pval_res : dict, last_res : zres) -> zres:
        nsucc = len(d_pval_res)
        if nsucc == 0:
            log.warning('None of the fits succeeded, returning last result')
            self._set_pdf_pars(last_res)

            return last_res

        l_pval_res= list(d_pval_res.items())
        l_pval_res.sort()
        _, res = l_pval_res[0]

        log.debug(f'Picking out best fit from {nsucc} fits')
        for chi2, _ in l_pval_res:
            log.debug(f'{chi2:.3f}')

        self._set_pdf_pars(res)

        return res
    #------------------------------
    def _fit_in_steps(self, cfg : dict) -> zres:
        l_nsample = cfg['strategy']['steps']['nsteps']
        l_nsigma  = cfg['strategy']['steps']['nsigma']
        l_yield   = cfg['strategy']['steps']['yields']

        res = None
        for nsample, nsigma in zip(l_nsample, l_nsigma):
            log.info(f'Fitting with {nsample} samples')
            cfg_step             = dict(cfg)
            cfg_step['nentries'] = nsample

            nll    = self._get_full_nll(cfg = cfg_step)
            res, _ = self.minimize(nll, cfg_step, ndof=self._ndof)
            res.hesse(method='minuit_hesse')
            self._update_par_bounds(res, nsigma=nsigma, yields=l_yield)

        log.info('Fitting full sample')
        nll    = self._get_full_nll(cfg = cfg)
        res, _ = self.minimize(nll, cfg, ndof=self._ndof)

        if res is None:
            nsteps = len(l_nsample)
            raise ValueError(f'No fit out of {nsteps} was done')

        return res
    #------------------------------
    def _result_to_value_error(self, res : zres) -> dict[str, list[float]]:
        d_par = {}
        for par, d_val in res.params.items():
            try:
                val = d_val['value']
                err = d_val['hesse']['error']
            except KeyError as exc:
                pprint.pprint(d_val)
                raise KeyError(f'Cannot extract value, hesse or error from dictionary above') from exc

            d_par[par.name] = [val, err]

        return d_par
    #------------------------------
    def _update_par_bounds(self, res : zres, nsigma : float, yields : list[str]) -> None:
        s_shape_par = self._pdf.get_params(is_yield=False, floating=True)
        d_shp_par   = { par.name : par for par in s_shape_par if par.name not in yields}
        d_fit_par   = self._result_to_value_error(res)

        log.info(60 * '-')
        log.info(f'{"Parameter":<20}{"Low bound":<20}{"High bound":<20}')
        log.info(60 * '-')
        for name, [val, err] in d_fit_par.items():
            if name not in d_shp_par:
                log.debug(f'Skipping {name} parameter')
                continue

            shape       = d_shp_par[name]
            shape.lower = val - nsigma * err
            shape.upper = val + nsigma * err

            log.info(f'{name:<20}{val - err:<20.3e}{val + err:<20.3e}')
    #------------------------------
    @staticmethod
    def get_gaussian_constraints(
        obj : ParameterHolder,
        cfg : dict[str,tuple[float,float]]|None) -> list[zfit.constraint.GaussianConstraint]:
        '''
        Parameters
        --------------
        obj: Object from which `get_params` can be called, such that its parameters will be constrained
        cfg: Dictionary specifying what variables to constrain and values of constraints, e.g.
             mu : (5, 1.0)
             sg : (0, 0.1)

        e.g. dictionary with parameter name and tuple. Latter holds mean value and width

        Returns
        --------------
        List of Gaussian constraints
        '''
        if cfg is None:
            log.debug('Not using any constraint')
            return []

        s_par   = obj.get_params(floating=True)
        d_par   = { par.name : par for par in s_par}

        log.info('Adding constraints:')
        l_const = []
        for par_name, (par_mu, par_sg) in cfg.items():
            if par_name not in d_par:
                log.error(s_par)
                raise ValueError(f'Parameter {par_name} not found among floating parameters of model, above')

            par = d_par[par_name]

            if par_sg == 0:
                par.floating = False
                log.info(f'{"":<4}{par_name:<15}{par_mu:<15.3e}{par_sg:<15.3e}')
                continue

            const = zfit.constraint.GaussianConstraint(params=par, observation=float(par_mu), uncertainty=float(par_sg))
            log.info(f'{"":<4}{par_name:<45}{par_mu:<15.3e}{par_sg:<15.3e}')
            l_const.append(const)

        return l_const
    #------------------------------
    def fit(self, cfg : dict|None = None) -> zres:
        '''
        Runs the fit using the configuration specified by the cfg dictionary
        Parameters
        ----------------------
        cfg : Fit configuration

        Returns
        ----------------------
        zres: Fit result
        '''
        self._initialize()

        cfg = {} if cfg is None else cfg

        log.info(f'{"chi2":<10}{"pval":<10}{"stat":<10}')
        if 'strategy' not in cfg:
            nll    = self._get_full_nll(cfg = cfg)
            res, _ = self.minimize(nll, cfg, ndof=self._ndof)
        elif 'retry' in cfg['strategy']:
            d_pval_res, last_res = self._fit_retries(cfg)
            res = self._pick_best_fit(d_pval_res, last_res)
        elif 'steps' in cfg['strategy']:
            res = self._fit_in_steps(cfg)
        else:
            raise ValueError('Unsupported fitting strategy')

        return res
    # ----------------------
    @classmethod
    def errors_disabled(cls, value : bool):
        '''
        Parameters
        -------------
        value: If true, will not run error calculation
        '''
        old_val = Fitter._turn_off_errors
        Fitter._turn_off_errors = value

        @contextlib.contextmanager
        def _context():
            try:
                yield
            finally:
                Fitter._turn_off_errors = old_val

        return _context()
#------------------------------
