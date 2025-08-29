'''
Module with ParameterLibrary class
'''
import math

from contextlib          import contextmanager
from importlib.resources import files

from dmu.stats.zfit               import zfit
from dmu.logging.log_store        import LogStore
from zfit.interface               import ZfitParameter as zpar
from omegaconf                    import DictConfig, OmegaConf

log=LogStore.add_logger('dmu:parameters')
# --------------------------------
class ParameterLibrary:
    '''
    Class meant to:

    - Connect to database (YAML file) with parameter values and make them available
    - Allow parameter values to be overriden
    '''
    _values : DictConfig
    _yld_cfg: DictConfig|None = None # Configuration used for yields
    _d_par  : dict[str,zpar]  = {}   # When building parameters, they will be stored here, such that they can be reused, for simultaneous fits
    # --------------------------------
    @classmethod
    def _load_data(cls) -> None:
        if hasattr(cls, '_values'):
            return

        data_path = files('dmu_data').joinpath('stats/parameters/data.yaml')
        data_path = str(data_path)

        values = OmegaConf.load(data_path)
        if not isinstance(values, DictConfig):
            raise TypeError(f'Wrong (not dictionary) data loaded from: {data_path}')

        cls._values = values
    # --------------------------------
    @classmethod
    def print_parameters(cls, kind : str) -> None:
        '''
        Method taking the kind of PDF to which the parameters are associated
        and printing the values.
        '''
        cfg = cls._values
        if kind not in cfg:
            raise ValueError(f'Cannot find parameters for PDF of kind: {kind}')

        log.info(cfg[kind])
    # --------------------------------
    @classmethod
    def get_values(cls, kind : str, parameter : str) -> tuple[float,float,float]:
        '''
        Parameters
        --------------
        kind     : Kind of PDF, e.g. gaus, cbl, cbr, suj
        parameter: Name of parameter for PDF, e.g. mu, sg

        Returns
        --------------
        Tuple with central value, minimum and maximum
        '''
        if kind not in cls._values:
            raise ValueError(f'Cannot find PDF of kind: {kind}')

        if parameter not in cls._values[kind]:
            raise ValueError(f'For PDF {kind}, cannot find parameter: {parameter}')

        val = cls._values[kind][parameter]['val' ]
        low = cls._values[kind][parameter]['low' ]
        hig = cls._values[kind][parameter]['high']

        return val, low, hig
    # --------------------------------
    @classmethod
    def values(
        cls,
        kind      : str,
        parameter : str,
        val       : float,
        low       : float,
        high      : float):
        '''
        This function will override the value and range for the given parameter
        It should be typically used before using the ModelFactory class
        '''
        old_val, old_low, old_high   = cls.get_values(kind=kind, parameter=parameter)
        cls._values[kind][parameter] = {'val' : val, 'low' : low, 'high' : high}

        @contextmanager
        def _context():
            try:
                yield
            finally:
                cls._values[kind][parameter] = {'val' : old_val, 'low' : old_low, 'high' : old_high}

        return _context()
    # ----------------------
    @classmethod
    def parameter_schema(cls, cfg : DictConfig):
        '''
        This context manager sets `_yld_cfg`, which defines

        - How parameters are related. I.e. if they are multiplied
        - What their values are

        Parameters
        -------------
        cfg: DictConfig representing the values and relationships between paramaters
        '''
        old_val      = cls._yld_cfg
        cls._yld_cfg = cfg

        @contextmanager
        def _context():
            try:
                yield
            finally:
                cls._yld_cfg = old_val

        return _context()
    # ----------------------
    @classmethod
    def get_yield(cls, name : str) -> zpar:
        '''
        Parameters
        -------------
        name: Name of parameter

        Returns
        -------------
        Zfit parameter
        '''
        log.debug(f'Picking up parameter: {name}')
        if name in cls._d_par:
            return cls._d_par[name]

        if cls._yld_cfg is None:
            raise ValueError('Parameter schema not set')

        yld_cfg = cls._yld_cfg
        if name not in yld_cfg:
            log.error(OmegaConf.to_yaml(yld_cfg))
            raise ValueError(f'Parameter {name} not found in configuration')

        if 'alias' in yld_cfg[name]:
            l_par    = [ cls.get_yield(name=comp_name) for comp_name in yld_cfg[name]['alias'] ]
            comp_par = cls._multiply_pars(name=name, pars=l_par)
            cls._d_par[name] = comp_par
            return comp_par

        # This is a non-alias, non-scl parameter, e.g. simple one
        if 'scl' not in yld_cfg[name]:
            par = cls._parameter_from_conf(name=name, cfg=yld_cfg)
            cls._d_par[name] = par
            return par

        # scl and non alias
        l_par    = [ cls.get_yield(name=comp_name) for comp_name in yld_cfg[name]['scl'] ]
        par      = cls._parameter_from_conf(name=name, cfg=yld_cfg, is_scale=True)
        l_par.append(par)
        comp_par = cls._multiply_pars(name=name, pars=l_par)

        return comp_par
    # ----------------------
    @classmethod
    def _multiply_pars(cls, name : str, pars : list[zpar]) -> zpar:
        '''
        Parameters
        -------------
        name: Name of product parameter
        pars: List of parameters

        Returns
        -------------
        Product of parameters
        '''
        if len(pars) == 0:
            raise ValueError(f'No factor parameters found for: {name}')

        comp_par = zfit.ComposedParameter(name, lambda pars : math.prod(pars), params=pars)

        return comp_par
    # ----------------------
    @classmethod
    def _parameter_from_conf(cls, name : str, cfg : DictConfig, is_scale : bool = False) -> zpar:
        '''
        Parameters
        -------------
        name    : Name of parameter to be returned
        cfg     : Config defining values of parameter bounds and default value of parameter
        is_scale: If True, this parameter is a scale, not an actual yield. Scales on yield nPar is called s_nPar

        Returns
        -------------
        A zfit parameter
        '''
        val = cfg[name]['val']
        minv= cfg[name]['min']
        maxv= cfg[name]['max']

        preffix  = cfg[name].get('preffix', 's')
        par_name = f'{preffix}_{name}' if is_scale else name

        if minv > maxv:
            raise ValueError(f'For parameter {name}, minimum edge is larger: {minv:.3e} > {maxv:.3e}')

        if math.isclose(minv, maxv, rel_tol=1e-5):
            par = zfit.Parameter(par_name, val, minv, maxv + 1, floating=False)
        else:
            par = zfit.Parameter(par_name, val, minv, maxv + 0, floating= True)

        return par
# --------------------------------
ParameterLibrary._load_data()
