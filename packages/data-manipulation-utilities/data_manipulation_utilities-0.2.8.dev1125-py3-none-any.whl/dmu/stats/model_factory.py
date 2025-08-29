'''
Module storing ZModel class
'''
# pylint: disable=too-many-lines, import-error, too-many-positional-arguments, too-many-arguments
# pylint: disable=too-many-instance-attributes

from typing import Callable, Union

import zfit

from zfit.interface         import ZfitSpace     as zobs
from zfit.interface         import ZfitPDF       as zpdf
from zfit.interface         import ZfitParameter as zpar

from dmu.stats.parameters   import ParameterLibrary as PL
from dmu.stats.zfit_models  import HypExp
from dmu.stats.zfit_models  import ModExp
from dmu.logging.log_store  import LogStore

log=LogStore.add_logger('dmu:stats:model_factory')
#-----------------------------------------
class MethodRegistry:
    '''
    Class intended to store protected methods belonging to ModelFactory class
    which is defined in this same module
    '''
    # Registry dictionary to hold methods
    _d_method = {}

    @classmethod
    def register(cls, nickname : str):
        '''
        Decorator in charge of registering method for given nickname
        '''
        def decorator(method):
            cls._d_method[nickname] = method
            return method

        return decorator

    @classmethod
    def get_method(cls, nickname : str) -> Union[Callable,None]:
        '''
        Will return method in charge of building PDF, for an input nickname
        '''
        method = cls._d_method.get(nickname, None)

        if method is not None:
            return method

        log.warning('Available PDFs:')
        for value in cls._d_method:
            log.info(f'    {value}')

        return method

    @classmethod
    def get_pdf_names(cls) -> list[str]:
        '''
        Returns list of PDFs that are registered/supported
        '''
        return list(cls._d_method)
#-----------------------------------------
class ModelFactory:
    '''
    Class used to create Zfit PDFs by passing only the nicknames, e.g.:

    ```python
    from dmu.stats.model_factory import ModelFactory

    l_pdf = ['dscb', 'gauss']
    l_shr = ['mu']
    l_flt = ['mu', 'sg']
    d_rep = {'mu' : 'scale', 'sg' : 'reso'}
    mod   = ModelFactory(
            preffix = 'signal', 
            obs     = obs, 
            l_pdf   = l_pdf, 
            l_shared= l_shr, 
            d_rep   = d_rep)

    pdf   = mod.get_pdf()
    ```

    where one can specify which parameters

    - Can be shared among the PDFs
    - Are meant to float if this fit is done to MC, in order to fix parameters in data.
    - Are scales or resolutions that need reparametrizations
    '''
    #-----------------------------------------
    def __init__(self,
        preffix  : str,
        obs      : zobs,
        l_pdf    : list[str],
        l_shared : list[str],
        l_float  : list[str],
        l_reuse  : None | list[zpar]      = None,
        d_fix    : None | dict[str,float] = None,
        d_rep    : None | dict[str,str]   = None):
        '''
        preffix:  used to identify PDF, will be used to name every parameter
        obs:      zfit obserbable
        l_pdf:    List of PDF nicknames which are registered below
        l_shared: List of parameter names that are shared
        l_float:  List of parameter names to allow to float
        l_reuse:  Optional. List of parameters that if given will be used instead of built by factory
        d_fix:    Dictionary with keys as the beginning of the name of a parameter and value as the number
                  to which it has to be fixed. If not one and only one parameter is found, ValueError is raised
        d_rep:    Dictionary with keys as variables that will be reparametrized
        '''
        l_reuse = [] if l_reuse is None else l_reuse

        self._preffix         = preffix
        self._l_pdf           = l_pdf
        self._l_shr           = l_shared
        self._l_flt           = l_float
        self._d_fix           = d_fix
        self._d_rep           = d_rep
        self._d_reuse         = { par.name : par for par in l_reuse }
        self._obs             = obs

        self._d_par : dict[str,zpar] = {}

        self._check_reparametrization()
    #-----------------------------------------
    def _check_reparametrization(self) -> None:
        '''
        This method:

        - Returns if no reparametrization has been requested
        - Raises if reparametrization is on any fixed parameter
        - Raises if trying to reparametrize anything that is not scales and resolutions
        '''
        if self._d_rep is None:
            return

        s_par_1 = set(self._d_rep)
        s_par_2 = set(self._l_flt)

        if not s_par_1.isdisjoint(s_par_2):
            log.info(f'Found  : {s_par_1}')
            log.info(f'Allowed: {s_par_2}')
            raise ValueError('Non empty intersection between floating and reparametrization parameters')

        s_kind  = set(self._d_rep.values())
        if not s_kind.issubset({'scale', 'reso'}):
            raise ValueError(f'Only scales and resolution reparametrizations allowed, found: {s_kind}')
    #-----------------------------------------
    def _split_name(self, name : str) -> tuple[str,str]:
        l_part = name.split('_')
        pname  = l_part[0]
        xname  = '_'.join(l_part[1:])

        return pname, xname
    #-----------------------------------------
    def _get_parameter_name(self, name : str, suffix : str) -> str:
        '''
        Parameters
        ---------------
        name  : Name of pdf and physical name, e.g mu_gauss
        suffix: Identifies this PDF, e.g. index of 3rd gaussian

        Returns
        ---------------
        Name of parameter which:

        - mu_preffix,     if parameter is shared
        - mu_preffix3     if not shared but not floating
        - mu_preffix3_flt if not shared and floating
        '''
        # pname = physical name, is something like mu or sg
        pname, xname = self._split_name(name)
        log.debug(f'Using physical name: {pname}')

        if pname in self._l_flt:
            # If reused parameter is floating
            # find it with flt
            reuse_name = f'{pname}_{suffix}_flt'
        else:
            reuse_name = f'{pname}_{suffix}'

        if reuse_name in self._d_reuse:
            log.debug(f'Picking name {reuse_name} for reused parameter')
            return self._add_float(pname=pname, name=pname)

        if pname in self._l_shr:
            name = f'{pname}_{self._preffix}'
            log.debug(f'Using model specific parameter name {name}')
        else:
            name = f'{pname}_{xname}_{self._preffix}{suffix}'
            log.debug(f'Using component specific parameter name {name}')

        return self._add_float(pname=pname, name=name)
    #-----------------------------------------
    def _add_float(self, pname : str, name : str) -> str:
        '''
        Parameters
        -------------
        pname : Physical name, e.g. mu
        name  : Actual parameter name, e.g. mu_cbl_3

        Returns
        -------------
        Actual parameter name with _flt appended if the physical version is meant to float
        '''
        if pname not in self._l_flt:
            return name

        return f'{name}_flt'
    #-----------------------------------------
    def _get_parameter(
        self,
        kind   : str,
        name   : str,
        suffix : str) -> zpar:
        '''
        Parameters
        ----------------
        kind  : Identifies PDF, e.g. gaus
        name  : Physical name of parameter, e.g. mu
        suffix: If multiple PDFs of this kind, it will be some sort of index, e.g. gaus(1), gaus(2)

        Returns
        ----------------
        Parameter, if it was :

        - Provided as part of l_reuse (e.g. mu), it will pick it up instead of building it
        - Specified as shared, it will build it once and then reuse that one.
        - Otherwise, it will make a new one, with a suffix to diferentiate it from whatever was already created 
        '''

        par_name = self._get_parameter_name(f'{name}_{kind}', suffix)
        log.debug(f'Assigning name: {par_name}')

        if par_name in self._d_reuse:
            log.info(f'Reusing {par_name}')
            return self._d_reuse[par_name]

        if par_name in self._d_par:
            log.info(f'Picking already made parameter {par_name}')
            return self._d_par[par_name]

        is_reparametrized = self._is_reparametrized(name)

        val, low, high = PL.get_values(kind=kind, parameter=name)

        if is_reparametrized:
            init_name, _ = self._split_name(par_name)
            log.info(f'Reparametrizing {par_name}')
            par  = self._get_reparametrization(par_name, init_name, val, low, high)
        else:
            if val == low == high:
                log.warning(f'Upper and lower edges agree, fixing parameter to: {low}')
                par  = zfit.param.Parameter(par_name, val, low - 1 , high + 1)
                par.floating = False
            else:
                log.debug(f'Creating new parameter {par_name}')
                par  = zfit.param.Parameter(par_name, val, low, high)

        self._d_par[par_name] = par

        return par
    #-----------------------------------------
    def _is_reparametrized(self, name : str) -> bool:
        if self._d_rep is None:
            return False

        root_name, _ = self._split_name(name)

        is_rep = root_name in self._d_rep

        log.debug(f'Reparametrizing {name}: {is_rep}')

        return is_rep
    #-----------------------------------------
    def _get_reparametrization(self, par_name : str, init_name : str, value : float, low : float, high : float) -> zpar:
        log.debug(f'Reparametrizing {par_name}')
        par_const = zfit.Parameter(par_name, value, low, high)
        par_const.floating = False

        kind = self._d_rep[init_name]
        if   kind == 'reso':
            par_reso  = zfit.Parameter(f'{par_name}_reso_flt' , 1.0, 0.20, 5.0)
            par       = zfit.ComposedParameter(f'{par_name}_cmp', lambda d_par : d_par['par_const'] * d_par['reso' ], params={'par_const' : par_const, 'reso'  : par_reso } )
        elif kind == 'scale':
            par_scale = zfit.Parameter(f'{par_name}_scale_flt', 0.0, -100, 100)
            par       = zfit.ComposedParameter(f'{par_name}_cmp', lambda d_par : d_par['par_const'] + d_par['scale'], params={'par_const' : par_const, 'scale' : par_scale} )
        else:
            raise ValueError(f'Invalid kind: {kind}')

        return par
    #-----------------------------------------
    @MethodRegistry.register('exp')
    def _get_exponential(self, suffix : str = '') -> zpdf:
        c   = self._get_parameter('exp', 'c', suffix)
        pdf = zfit.pdf.Exponential(c, self._obs, name=f'exp{suffix}')

        return pdf
    # ---------------------------------------------
    @MethodRegistry.register('hypexp')
    def _get_hypexp(self, suffix : str = '') -> zpdf:
        mu = self._get_parameter('hypexp', 'mu', suffix)
        ap = self._get_parameter('hypexp', 'ap', suffix)
        bt = self._get_parameter('hypexp', 'bt', suffix)

        pdf= HypExp(obs=self._obs, mu=mu, alpha=ap, beta=bt, name=f'hypexp{suffix}')

        return pdf
    # ---------------------------------------------
    @MethodRegistry.register('modexp')
    def _get_modexp(self, suffix : str = '') -> zpdf:
        mu = self._get_parameter('modexp', 'mu', suffix)
        ap = self._get_parameter('modexp', 'ap', suffix)
        bt = self._get_parameter('modexp', 'bt', suffix)

        pdf= ModExp(obs=self._obs, mu=mu, alpha=ap, beta=bt, name=f'modexp{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('pol1')
    def _get_pol1(self, suffix : str = '') -> zpdf:
        a   = self._get_parameter('pol1', 'a', suffix)
        pdf = zfit.pdf.Chebyshev(obs=self._obs, coeffs=[a], name=f'pol1{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('pol2')
    def _get_pol2(self, suffix : str = '') -> zpdf:
        a   = self._get_parameter('pol2', 'a', suffix)
        b   = self._get_parameter('pol2', 'b', suffix)
        pdf = zfit.pdf.Chebyshev(obs=self._obs, coeffs=[a, b   ], name=f'pol2{suffix}')

        return pdf
    # ---------------------------------------------
    @MethodRegistry.register('pol3')
    def _get_pol3(self, suffix : str = '') -> zpdf:
        a   = self._get_parameter('pol3', 'a', suffix)
        b   = self._get_parameter('pol3', 'b', suffix)
        c   = self._get_parameter('pol3', 'c', suffix)

        pdf = zfit.pdf.Chebyshev(obs=self._obs, coeffs=[a, b, c], name=f'pol3{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('cbr')
    def _get_cbr(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('cbr', 'mu', suffix)
        sg  = self._get_parameter('cbr', 'sg', suffix)
        ar  = self._get_parameter('cbr', 'ac', suffix)
        nr  = self._get_parameter('cbr', 'nc', suffix)

        pdf = zfit.pdf.CrystalBall(mu, sg, ar, nr, self._obs, name=f'cbr{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('suj')
    def _get_suj(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('suj', 'mu', suffix)
        sg  = self._get_parameter('suj', 'sg', suffix)
        gm  = self._get_parameter('suj', 'gm', suffix)
        dl  = self._get_parameter('suj', 'dl', suffix)

        pdf = zfit.pdf.JohnsonSU(mu, sg, gm, dl, self._obs, name=f'suj{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('cbl')
    def _get_cbl(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('cbl', 'mu', suffix)
        sg  = self._get_parameter('cbl', 'sg', suffix)
        al  = self._get_parameter('cbl', 'ac', suffix)
        nl  = self._get_parameter('cbl', 'nc', suffix)

        pdf = zfit.pdf.CrystalBall(mu, sg, al, nl, self._obs, name=f'cbl{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('gauss')
    def _get_gauss(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('gauss', 'mu', suffix)
        sg  = self._get_parameter('gauss', 'sg', suffix)

        pdf = zfit.pdf.Gauss(mu, sg, self._obs, name=f'gauss{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('dscb')
    def _get_dscb(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('dscb', 'mu', suffix)
        sg  = self._get_parameter('dscb', 'sg', suffix)
        ar  = self._get_parameter('dscb', 'ar', suffix)
        al  = self._get_parameter('dscb', 'al', suffix)
        nr  = self._get_parameter('dscb', 'nr', suffix)
        nl  = self._get_parameter('dscb', 'nl', suffix)

        pdf = zfit.pdf.DoubleCB(mu, sg, al, nl, ar, nr, self._obs, name=f'dscb{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('voigt')
    def _get_voigt(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('voigt', 'mu', suffix)
        sg  = self._get_parameter('voigt', 'sg', suffix)
        gm  = self._get_parameter('voigt', 'gm', suffix)

        pdf = zfit.pdf.Voigt(m=mu, sigma=sg, gamma=gm, obs=self._obs, name=f'voigt{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('qgauss')
    def _get_qgauss(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('qgauss', 'mu', suffix)
        sg  = self._get_parameter('qgauss', 'sg', suffix)
        q   = self._get_parameter('qgauss',  'q', suffix)

        pdf = zfit.pdf.QGauss(q=q, mu=mu, sigma=sg, obs=self._obs, name =f'qgauss{suffix}')

        return pdf
    #-----------------------------------------
    @MethodRegistry.register('cauchy')
    def _get_cauchy(self, suffix : str = '') -> zpdf:
        mu  = self._get_parameter('cauchy', 'mu', suffix)
        gm  = self._get_parameter('cauchy', 'gm', suffix)

        pdf = zfit.pdf.Cauchy(obs=self._obs, m=mu, gamma=gm, name=f'cauchy{suffix}')

        return pdf
    #-----------------------------------------
    def _get_pdf_types(self) -> list[tuple[str,str]]:
        d_name_freq = {}

        l_type = []
        for name in self._l_pdf:
            if name not in d_name_freq:
                d_name_freq[name] = 1
            else:
                d_name_freq[name]+= 1

            frq = d_name_freq[name]
            frq = f'_{frq}'

            l_type.append((name, frq))

        return l_type
    #-----------------------------------------
    def _get_pdf(self, kind : str, preffix : str) -> zpdf:
        fun = MethodRegistry.get_method(kind)
        if fun is None:
            raise NotImplementedError(f'PDF of type \"{kind}\" with preffix \"{preffix}\" is not implemented')

        return fun(self, preffix)
    #-----------------------------------------
    def _add_pdf(self, l_pdf : list[zpdf]) -> zpdf:
        nfrc = len(l_pdf)
        if nfrc == 1:
            log.debug('Requested only one PDF, skipping sum')
            return l_pdf[0]

        l_frc= [ zfit.param.Parameter(f'frc_{self._preffix}_{ifrc + 1}', 0.5, 0, 1) for ifrc in range(nfrc - 1) ]

        pdf = zfit.pdf.SumPDF(l_pdf, name=self._preffix, fracs=l_frc)

        return pdf
    #-----------------------------------------
    def _find_par(self, s_par : set[zpar], name_start : str) -> zpar:
        l_par_match = [ par for par in s_par if par.name.startswith(name_start) ]
        npar        = len(l_par_match)

        if npar!= 1:
            for par in s_par:
                log.info(par.name)

            raise ValueError(f'Found {npar} parameters starting with: {name_start}')

        return l_par_match[0]
    #-----------------------------------------
    def _fix_parameters(self, pdf : zpdf) -> zpdf:
        if self._d_fix is None:
            log.debug('Not fixing any parameter')
            return pdf

        s_par = pdf.get_params()

        log.info('-' * 30)
        log.info('Fixing parameters')
        log.info('-' * 30)
        for name_start, value in self._d_fix.items():
            par = self._find_par(s_par, name_start)
            par.set_value(value)

            log.info(f'{name_start:<20}{value:<20.3f}')
            par.floating = False

        return pdf
    #-----------------------------------------
    def get_pdf(self) -> zpdf:
        '''
        Given a list of strings representing PDFs returns the a zfit PDF which is
        the sum of them
        '''
        l_type=   self._get_pdf_types()
        l_pdf = [ self._get_pdf(kind, preffix) for kind, preffix in l_type ]
        pdf   =   self._add_pdf(l_pdf)
        pdf   =   self._fix_parameters(pdf)

        return pdf
#-----------------------------------------
