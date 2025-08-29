'''
This module contains the ConstraintAdder class
'''
from typing          import Union, cast

import numpy
import zfit
from omegaconf       import DictConfig, DictKeyType, OmegaConf
from zfit            import Parameter
from zfit.constraint import GaussianConstraint, PoissonConstraint
from zfit.loss       import ExtendedUnbinnedNLL, UnbinnedNLL

from dmu.logging.log_store import LogStore

log=LogStore.add_logger('dmu:stats:constraint_adder')
Constraint = Union[GaussianConstraint, PoissonConstraint]
Loss       = Union[ExtendedUnbinnedNLL, UnbinnedNLL]
# ----------------------
class ConstraintAdder:
    '''
    This class is in charge of:

    - Transforming a config object into constrain objects
    - Using those constraints to update the NLL
    '''
    _valid_constraints = ['GaussianConstraint', 'PoissonConstraint']
    # ----------------------
    def __init__(self, nll : Loss, cns : DictConfig):
        '''
        Parameters
        -------------
        nll: Zfit likelihood, before constraints added
        cns: Configuration, describing 
            - What variables to constraint
            - What kind of constraint to use
            - What the means of the contraints should be
            - What the covariances should be
        '''
        self._nll = nll
        self._cns = cns

        self._d_par = self._get_params(nll=nll)
        self._d_cns : dict[str,Parameter] = {}
    # ----------------------
    def _get_params(self, nll : Loss) -> dict[str, Parameter]:
        '''
        Parameters
        -------------
        nll: Likelihood holding parameters

        Returns
        -------------
        Dictionary mapping parameter names with parameters
        '''
        s_par = nll.get_params(floating=True)
        if len(s_par) == 0:
            raise ValueError('No floating parameter found in likelihood')

        return { par.name : cast(Parameter, par) for par in s_par }
    # ----------------------
    def _get_observation(self, cfg : DictConfig) -> list[Parameter]:
        '''
        Parameters
        -------------
        cfg  : Configuration specifying how to build the Gaussian constraint
        mode : Controls the observation value. Either toy or real.

        Returns
        -------------
        List of observations as parameters
        '''
        l_nam = cfg.parameters
        l_val = cfg.observation
        l_par = [ zfit.Parameter(f'{nam}_cns', fval) for nam, fval in zip(l_nam, l_val) ]

        return l_par
    # ----------------------
    def _resample_block(self, cfg : DictConfig) -> None:
        '''
        Updates observation values for parameters of a given block of constraints
        '''
        mu  = cfg.observation
        if cfg.kind == 'PoissonConstraint':
            arr = numpy.random.poisson(mu, size=len(mu))
            # Cannot use a lambda=0 for a Poisson distribution
            # Use very small lambda, if RNG gives zero
            arr = numpy.where(arr == 0, 1e-2, arr)
            self._update_observations(values=arr, names=cfg.parameters)
            return

        cov = cfg.cov
        if cfg.kind == 'GaussianConstraint':
            arr = numpy.random.multivariate_normal(mu, cov, size=1)
            self._update_observations(values=arr[0], names=cfg.parameters)
            return

        raise ValueError(f'Toy observation not defined for: {cfg.kind}')
    # ----------------------
    def _update_observations(self, values : numpy.ndarray, names : list[str]) -> None:
        '''
        This method sets the values of the constraining parameters from resampled values

        Parameters
        -------------
        values: Array with resampled observations
        names : Names of parameters used to constrain likelihood
        '''
        for name, value in zip(names, values):
            log.verbose(f'Setting {name}={value}')

            if name not in self._d_cns:
                raise ValueError(f'Cannot find constraining parameter: {name}')

            par = self._d_cns[name]
            par.set_value(value)
    # ----------------------
    def _get_gaussian_constraint(self, cfg : DictConfig) -> GaussianConstraint:
        '''
        Parameters
        -------------
        cfg  : Configuration specifying how to build the Gaussian constraint
        mode : Controls the observation value. Either toy or real.

        Returns
        -------------
        Zfit gaussian constrain
        '''
        l_name    = cfg.parameters
        l_obs_par = self._get_observation(cfg=cfg)
        l_obs_val = [ par.value for par in l_obs_par ]
        self._d_cns.update(dict(zip(l_name, l_obs_par)))

        log.verbose('Creating Gaussian constraint')
        log.verbose(f'Parameters :\n {l_name}')
        log.verbose(f'Observation:\n {l_obs_val}')
        log.verbose(f'Covariance :\n {cfg.cov}')

        l_par = [ self._d_par[name] for name in cfg.parameters ]
        cns   = zfit.constraint.GaussianConstraint(
            params      = l_par, 
            observation = l_obs_par,
            cov         = cfg.cov)

        return cns
    # ----------------------
    def _get_poisson_constraint(self, cfg : DictConfig) -> PoissonConstraint:
        '''
        Parameters
        -------------
        cfg  : Configuration needed to build constraint

        Returns
        -------------
        Zfit constraint
        '''
        l_name    = cfg.parameters
        l_obs_par = self._get_observation(cfg=cfg)
        l_obs_val = [ obs.value for obs in l_obs_par ]
        self._d_cns.update(dict(zip(l_name, l_obs_par)))

        log.verbose('Creating Poisson constraint')
        log.verbose(f'Parameters :\n{l_name}')
        log.verbose(f'Observation:\n{l_obs_val}')

        l_par = [ self._d_par[name] for name in cfg.parameters ]
        cns   = zfit.constraint.PoissonConstraint(
            params      = l_par, 
            observation = l_obs_par)

        return cns
    # ----------------------
    def _create_constraint(self, block : DictKeyType) -> Constraint:
        '''
        Parameters
        -------------
        block: Name of the constrain block in the configuration passed in initializer

        Returns
        -------------
        Zfit constrain object
        '''
        cfg = self._cns[block]
        if cfg.kind == 'GaussianConstraint':
            return self._get_gaussian_constraint(cfg=cfg)

        if cfg.kind == 'PoissonConstraint':
            return self._get_poisson_constraint(cfg=cfg)

        raise ValueError(f'Invalid constraint type: {cfg.kind}')
    # ----------------------
    @classmethod
    def dict_to_cons(
        cls,
        d_cns : dict[str,tuple[float,float]], 
        name  : str,
        kind  : str) -> DictConfig:
        '''
        Parameters
        -------------
        d_cns: Dictionary mapping variable name to tuple with value and error
        name : Name of block to which these constraints belong, e.g. shape
        kind : Type of constraints, e.g. GaussianConstraint, PoissonConstraint

        Returns
        -------------
        Config object
        '''

        if kind not in cls._valid_constraints:
            raise ValueError(f'Invalid kind {kind} choose from: {cls._valid_constraints}')

        data = None
        if kind == 'PoissonConstraint':
            data = {
                'kind'       : kind,
                'parameters' : list(d_cns),
                'observation': [ val[0] for val in d_cns.values() ]
            }

        if kind == 'GaussianConstraint':
            npar = len(d_cns)
            cov  = []
            for ival, val in enumerate(d_cns.values()):
                zeros       = npar   * [0.]
                var         = val[1] ** 2
                zeros[ival] = var

                cov.append(zeros)

            data = {
                'kind'       : kind,
                'parameters' : list(d_cns),
                'observation': [ val[0] for val in d_cns.values() ],
                'cov'        : cov,
            }

        if data is None:
            raise ValueError('Could not create data needed for constraint object')

        return OmegaConf.create({name : data})
    # ----------------------
    def get_nll(self) -> Loss:
        '''
        Returns
        -------------
        Likelihood with constrain added
        '''
        l_const = [ self._create_constraint(block=block) for block in self._cns ]

        nll = self._nll.create_new(constraints=l_const) # type: ignore
        if nll is None:
            raise ValueError('Could not create a new likelihood')

        return nll
    # ----------------------
    def resample(self) -> None:
        '''
        Will update the parameters associated to constraint
        '''
        for name, cfg_block in self._cns.items():
            log.verbose(f'Resampling block: {name}')
            self._resample_block(cfg=cfg_block)
# ----------------------
