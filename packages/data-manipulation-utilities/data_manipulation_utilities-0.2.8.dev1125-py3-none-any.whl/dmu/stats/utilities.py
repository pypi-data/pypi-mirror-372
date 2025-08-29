'''
Module with utility functions related to the dmu.stats project
'''

from contextlib import contextmanager
import os
import re
import pickle
from typing     import Union, Mapping, Any, cast

import yaml
import numpy
import pandas            as pnd
import matplotlib.pyplot as plt

import dmu.pdataframe.utilities as put
import dmu.generic.utilities    as gut

from dmu.stats.zfit         import zfit
from dmu.stats.fitter       import Fitter
from dmu.stats.zfit_plotter import ZFitPlotter
from dmu.logging.log_store  import LogStore

import tensorflow as tf

from omegaconf        import OmegaConf, DictConfig
from zfit.interface   import ZfitData      as zdata
from zfit.interface   import ZfitSpace     as zobs
from zfit.interface   import ZfitModel     as zmod
from zfit.interface   import ZfitParameter as zpar
from zfit.loss        import ExtendedUnbinnedNLL, UnbinnedNLL
from zfit.pdf         import BasePDF       as zpdf

from zfit.minimizers.interface   import ZfitResult    as zres

log = LogStore.add_logger('dmu:stats:utilities')
Loss= Union[ExtendedUnbinnedNLL, UnbinnedNLL]
#-------------------------------------------------------
class Data:
    '''
    Data class
    '''
    weight_name = 'weight'
    l_blind_vars= []
# ----------------------
@contextmanager
def blinded_variables(regex_list : list[str]|None = None):
    '''
    Parameters
    -------------
    regex_list: List of regular expressions for variable names to be blinded
    '''
    if regex_list is None:
        raise ValueError('No regex list of variables to blind passed')

    old_val = Data.l_blind_vars
    Data.l_blind_vars = regex_list

    try:
        yield
    finally:
        Data.l_blind_vars = old_val
#-------------------------------------------------------
def name_from_obs(obs : zobs) -> str:
    '''
    Takes zfit observable, returns its name
    It is assumed this is a 1D observable
    '''
    if not isinstance(obs.obs, tuple):
        raise ValueError(f'Cannot retrieve name for: {obs}')

    if len(obs.obs) != 1:
        raise ValueError(f'Observable is not 1D: {obs.obs}')

    return obs.obs[0]
#-------------------------------------------------------
def range_from_obs(obs : zobs) -> tuple[float,float]:
    '''
    Takes zfit observable, returns tuple with two floats, representing range
    '''
    if not isinstance(obs.limits, tuple):
        raise ValueError(f'Cannot retrieve name for: {obs}')

    if len(obs.limits) != 2:
        raise ValueError(f'Observable has more than one range: {obs.limits}')

    minx, maxx = obs.limits

    if not isinstance(minx, numpy.ndarray):
        raise ValueError(f'Minx is not an array but: {minx}')

    if not isinstance(maxx, numpy.ndarray):
        raise ValueError(f'Minx is not an array but: {maxx}')

    return float(minx[0][0]), float(maxx[0][0])
#-------------------------------------------------------
def yield_from_zdata(data : zdata) -> float:
    '''
    Parameter
    --------------
    data : Zfit dataset

    Returns
    --------------
    Yield, i.e. number of entries or sum of weights if weighted dataset
    '''

    if data.weights is not None:
        val     = data.weights.numpy().sum()
    else:
        arr_val = data.to_numpy()
        val     = len(arr_val)

    if val < 0:
        raise ValueError(f'Yield cannot be negative, found {val}')

    return val
#-------------------------------------------------------
# Check PDF
#-------------------------------------------------------
def is_pdf_usable(pdf : zpdf) -> bool:
    '''
    Parameters
    ---------------
    pdf: PDF to check

    Returns
    ---------------
    True if PDF is usable
    '''
    minx, maxx = range_from_obs(obs=pdf.space)

    arr_x = numpy.linspace(minx, maxx, 100)
    tf_x  = tf.convert_to_tensor(arr_x)

    try:
        pdf.pdf(tf_x)
    except tf.errors.InvalidArgumentError:
        log.warning('PDF cannot be evaluated')
        return False

    return True
#-------------------------------------------------------
#Zfit/print_pdf
#-------------------------------------------------------
def _get_const(par : zpar , d_const : Union[None, dict[str, tuple[float,float]]]) -> str:
    '''
    Takes zfit parameter and dictionary of constraints
    Returns a formatted string with the value of the constraint on that parameter
    '''
    if d_const is None or par.name not in d_const:
        return 'none'

    obj = d_const[par.name]
    if isinstance(obj, (list, tuple)):
        [mu, sg] = obj
        val      = f'{mu:.3e}___{sg:.3e}' # This separator needs to be readable and not a space
    else:
        val      = str(obj)

    return val
#-------------------------------------------------------
def _get_unblinded_vars(
    s_par   : set, 
    l_blind : list[str]|None = None) -> set[zpar]:
    '''
    Parameters
    -----------------
    s_par  : PDF parameters
    l_blind: List of regular expressions that will be used to select parameters to blind 

    Returns
    -----------------
    set of zfit parameters that should be unblinded
    '''
    s_par_unblinded = set()
    l_blind_regex   = [] if l_blind is None else l_blind

    for par in s_par:
        if _is_par_blinded(name=par.name, l_blind=l_blind_regex):
            continue

        log.debug(f'Blinding {par.name}')
        s_par_unblinded.add(par)

    return s_par_unblinded
# ----------------------
def _is_par_blinded(name : str, l_blind : list[str]) -> bool:
    '''
    Parameters
    -------------
    name   : Name of parameter
    l_blind: List of regular expressions corresponding to parameters to blind

    Returns
    -------------
    True if it is meant to be blinded
    '''
    if len(l_blind) == 0:
        return False

    log.debug(f'Blinding any of: {l_blind}')

    rgx_ors = '|'.join(l_blind)
    regex   = f'({rgx_ors})'

    if re.match(regex, name):
        return True

    return False
#-------------------------------------------------------
def _get_pars(
    pdf   : zpdf|zmod,
    blind : None|list[str]) -> tuple[list, list]:
    '''
    Parameters
    ----------------
    pdf  : zfit PDF
    blind: List of regular expressions that match all variables to be blinded, or None in case of no blinding

    Returns
    ----------------
    Tuple with:
    - List of floating(fixed) parameters

    Blinded parameters are removed from this list
    '''
    s_par_flt = pdf.get_params(floating= True)
    s_par_fix = pdf.get_params(floating=False)

    s_par_flt = _get_unblinded_vars(s_par_flt, l_blind=blind)
    s_par_fix = _get_unblinded_vars(s_par_fix, l_blind=blind)

    l_par_flt = list(s_par_flt)
    l_par_fix = list(s_par_fix)

    l_par_flt = sorted(l_par_flt, key=lambda par: par.name)
    l_par_fix = sorted(l_par_fix, key=lambda par: par.name)

    return l_par_flt, l_par_fix
#-------------------------------------------------------
def _get_messages(
    pdf       : zpdf|zmod,
    l_par_flt : list,
    l_par_fix : list,
    d_const   : None|dict[str,tuple[float,float]] = None) -> list[str]:

    str_space = str(pdf.space)

    l_msg=[]
    l_msg.append('-' * 20)
    l_msg.append(f'PDF: {pdf.name}')
    l_msg.append(f'OBS: {str_space}')
    l_msg.append(f'{"Name":<50}{"Value":>15}{"Low":>15}{"High":>15}{"Floating":>5}{"Constraint":>25}')
    l_msg.append('-' * 20)
    for par in l_par_flt:
        value = par.value().numpy()
        low   = par.lower
        hig   = par.upper
        const = _get_const(par, d_const)
        l_msg.append(f'{par.name:<50}{value:>15.3e}{low:>15.3e}{hig:>15.3e}{par.floating:>5}{const:>25}')

    l_msg.append('')

    for par in l_par_fix:
        value = par.value().numpy()
        low   = par.lower
        hig   = par.upper
        const = _get_const(par, d_const)
        l_msg.append(f'{par.name:<50}{value:>15.3e}{low:>15.3e}{hig:>15.3e}{par.floating:>5}{const:>25}')

    return l_msg
#-------------------------------------------------------
def print_pdf(
    pdf      : zpdf|zmod,
    d_const  : None|dict[str,tuple[float, float]] = None,
    txt_path : str|None                           = None,
    level    : int                                = 20,
    blind    : None|list[str]                     = None) -> list[str]:
    '''
    Function used to print zfit PDFs

    Parameters
    -------------------
    pdf (zfit.PDF): PDF
    d_const (dict): Optional dictionary mapping {par_name : [mu, sg]}
    txt_path (str): Optionally, dump output to text in this path
    level (str)   : Optionally set the level at which the printing happens in screen, default info
    blind (list)  : List of regular expressions matching variable names to blind in printout

    Returns
    -------------------
    List of strings with contents of file to be written.
    Needed for testing
    '''
    blind  = [] if blind is None else blind
    blind += Data.l_blind_vars

    l_par_flt, l_par_fix = _get_pars(pdf, blind)
    l_msg                = _get_messages(pdf, l_par_flt, l_par_fix, d_const)

    if txt_path is not None:
        log.debug(f'Saving to: {txt_path}')
        message  = '\n'.join(l_msg)
        dir_path = os.path.dirname(txt_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(txt_path, 'w', encoding='utf-8') as ofile:
            ofile.write(message)

        return l_msg

    for msg in l_msg:
        if   level == 20:
            log.info(msg)
        elif level == 30:
            log.debug(msg)
        else:
            raise ValueError(f'Invalid level: {level}')

    return l_msg
#---------------------------------------------
def _parameters_from_result(result : zres) -> dict[str,tuple[float,float]]:
    d_par = {}
    log.debug('Reading parameters from:')
    if log.getEffectiveLevel() < 20:
        print(result)

    log.debug(60 * '-')
    log.debug('Reading parameters')
    log.debug(60 * '-')
    for name, d_val in result.params.items():
        name = str(name) # Result object is frozen already, name should be a string
        if _is_par_blinded(name=name, l_blind=Data.l_blind_vars):
            continue

        value = d_val['value']
        error = None
        if 'hesse'         in d_val:
            error = d_val['hesse']['error']

        if 'minuit_hesse'  in d_val:
            error = d_val['minuit_hesse']['error']

        log.debug(f'{name:<20}{value:<20.3f}{error}')

        if value is None:
            raise ValueError(f'No value found for parameter {name}')

        if error is None:
            raise ValueError(f'No value found for parameter {name}')

        d_par[name] = float(value), float(error)

    return d_par
#---------------------------------------------
def save_fit(
    data    : zdata,
    model   : zpdf|zmod|None,
    res     : zres|None,
    fit_dir : str,
    plt_cfg : DictConfig,
    d_const : dict[str,tuple[float,float]]|None = None) -> None:
    '''
    Parameters
    --------------------
    model: PDF to be plotted, if None, will skip steps
    '''
    _save_fit_plot(data=data, model=model, cfg=plt_cfg, fit_dir=fit_dir)
    _save_result(fit_dir=fit_dir, res=res)

    df    = data.to_pandas(weightsname=Data.weight_name)
    opath = f'{fit_dir}/data.json'
    log.debug(f'Saving data to: {opath}')
    df.to_json(opath, indent=2)

    if model is None:
        return

    print_pdf(model, txt_path=f'{fit_dir}/post_fit.txt', d_const=d_const)
    pdf_to_tex(path=f'{fit_dir}/post_fit.txt', d_par={'mu' : r'$\mu$'}, skip_fixed=True)
# ----------------------
def _save_fit_plot(
    data   : zdata, 
    model  : zpdf|zmod|None, 
    fit_dir: str,
    cfg    : DictConfig) -> None:
    '''
    Parameters
    -------------
    data   : Data from fit
    model  : Fitted model
    fit_dir: Directory where plot will go
    cfg    : Config used for plotting
    '''
    os.makedirs(fit_dir, exist_ok=True)
    fit_path_lin = f'{fit_dir}/fit_linear.png'
    fit_path_log = f'{fit_dir}/fit_log.png'
    log.info(f'Saving fit to: {fit_dir}')

    if model is None:
        log.warning('Model not found, saving dummy plot')
        plt.figure()
        plt.savefig(fit_path_lin)
        plt.savefig(fit_path_log)
        plt.close('all')
        return

    ptr = ZFitPlotter(data=data, model=model)
    ptr.plot(**cast(Mapping[str, Any], cfg)) # Need this casting to remove error from pyright

    log.info(f'Saving fit to: {fit_path_lin}')
    plt.savefig(fit_path_lin)

    ptr.axs[0].set_yscale('log')
    ptr.axs[0].set_ylim(bottom=0.1, top=1e7)
    log.info(f'Saving fit to: {fit_path_log}')
    plt.savefig(fit_path_log)
    plt.close()
#-------------------------------------------------------
def _save_result(fit_dir : str, res : zres|None) -> None:
    '''
    Saves result as yaml, JSON, pkl

    Parameters
    ---------------
    fit_dir: Directory where fit result will go
    res    : Zfit result object
    '''
    if res is None:
        log.info('No result object found, not saving parameters in pkl or JSON')
        return

    # TODO: Remove this once there be a safer way to freeze
    # see https://github.com/zfit/zfit/issues/632
    try:
        res.freeze()
    except AttributeError:
        pass

    with open(f'{fit_dir}/fit.pkl', 'wb') as ofile:
        pickle.dump(res, ofile)

    d_par  = _parameters_from_result(result=res)
    d_par  = dict(sorted(d_par.items()))

    opath  = f'{fit_dir}/parameters.json'
    log.debug(f'Saving parameters to: {opath}')
    gut.dump_json(d_par, opath)

    opath  = f'{fit_dir}/parameters.yaml'
    log.debug(f'Saving parameters to: {opath}')
    gut.dump_json(d_par, opath)
#-------------------------------------------------------
# Make latex table from text file
#-------------------------------------------------------
def _reformat_expo(val : str) -> str:
    regex = r'([\d\.]+)e([-,\d]+)'
    mtch  = re.match(regex, val)
    if not mtch:
        raise ValueError(f'Cannot extract value and exponent from: {val}')

    [val, exp] = mtch.groups()
    exp        = int(exp)

    return f'{val}\cdot 10^{{{exp}}}'
#-------------------------------------------------------
def _format_float_str(val : str) -> str:
    '''
    Takes number as string and returns a formatted version
    '''

    fval = float(val)
    if abs(fval) > 1000:
        return f'{fval:,.0f}'

    val = f'{fval:.3g}'
    if 'e' in val:
        val = _reformat_expo(val)

    return val
#-------------------------------------------------------
def _info_from_line(line : str) -> tuple|None:
    regex = r'(^\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
    mtch  = re.match(regex, line)
    if not mtch:
        return None

    log.debug(f'Reading information from: {line}')

    [par, _, low, high, floating, cons] = mtch.groups()

    low  = _format_float_str(low)
    high = _format_float_str(high)

    if cons != 'none':
        [mu, sg] = cons.split('___')

        mu   = _format_float_str(mu)
        sg   = _format_float_str(sg)

        cons = f'$\mu={mu}; \sigma={sg}$'

    return par, low, high, floating, cons
#-------------------------------------------------------
def _df_from_lines(l_line : list[str]) -> pnd.DataFrame:
    df = pnd.DataFrame(columns=['Parameter', 'Low', 'High', 'Floating', 'Constraint'])

    for line in l_line:
        info = _info_from_line(line=line)
        if info is None:
            continue

        par, low, high, floating, cons = info

        df.loc[len(df)] = {'Parameter' : par,
                           'Low'       : low,
                           'High'      : high,
                           'Floating'  : floating,
                           'Constraint': cons,
                           }

    return df
#-------------------------------------------------------
def pdf_to_tex(path : str, d_par : dict[str,str], skip_fixed : bool = True) -> None:
    '''
    Creates a latex table with the same name as `path` but `txt` extension replaced by `tex`

    Parameters
    -----------------
    path : Path to a `txt` file produced by stats/utilities:print_pdf
    d_par: Dictionary mapping parameter names in this file to proper latex names
    '''

    path = str(path)
    with open(path, encoding='utf-8') as ifile:
        l_line = ifile.read().splitlines()
        l_line = l_line[4:] # Remove header

    df = _df_from_lines(l_line)
    df['Parameter']=df.Parameter.apply(lambda x : d_par.get(x, x.replace('_', ' ')))

    out_path = path.replace('.txt', '.tex')

    if skip_fixed:
        df = df[df.Floating == '1']
        df = df.drop(columns='Floating')

    df_1 = df[df.Constraint == 'none']
    df_2 = df[df.Constraint != 'none']

    df_1 = df_1.sort_values(by='Parameter', ascending=True)
    df_2 = df_2.sort_values(by='Parameter', ascending=True)
    df   = pnd.concat([df_1, df_2])

    put.df_to_tex(df, out_path)
#---------------------------------------------
# Fake/Placeholder fit
#---------------------------------------------
def get_model(
    kind   : str,
    nsample: int       = 1000,
    obs    : zobs|None = None,
    suffix : str|None  = None,
    lam    : float     = -0.0001) -> zpdf:
    '''
    Returns zfit PDF for tests

    Parameters:

    kind   : 'signal' for Gaussian, 's+b' for Gaussian plus exponential
    nsample: Number of entries for normalization of each component, default 1000
    obs    : If provided, will use it, by default None and will be built in function
    suffix : Optional, can be used in case multiple models are needed
    lam    : Decay constant of exponential component, set to -0.0001 by default
    '''
    if suffix is not None:
        suffix = f'_{suffix}'
    else:
        suffix = ''

    if obs is None:
        obs  = zfit.Space(f'mass{suffix}', limits=(4500, 7000))

    mu   = zfit.Parameter(f'mu{suffix}', 5200, 4500, 6000)
    sg   = zfit.Parameter(f'sg{suffix}',   50,   10, 200)
    gaus = zfit.pdf.Gauss(obs=obs, mu=mu, sigma=sg)

    if kind == 'signal':
        return gaus

    c   = zfit.Parameter(f'c{suffix}', lam, -0.01, 0)
    expo= zfit.pdf.Exponential(obs=obs, lam=c)

    if kind == 's+b':
        nexpo = zfit.param.Parameter(f'nbkg{suffix}', nsample, 0, 1000_000)
        ngaus = zfit.param.Parameter(f'nsig{suffix}', nsample, 0, 1000_000)

        bkg   = expo.create_extended(nexpo)
        sig   = gaus.create_extended(ngaus)
        pdf   = zfit.pdf.SumPDF([bkg, sig])

        return pdf

    raise NotImplementedError(f'Invalid kind of fit: {kind}')
# ----------------------
def get_nll(kind : str) -> Loss:
    '''
    Parameters
    -------------
    kind : Type of model, e.g. s+b, signal

    Returns
    -------------
    Extended NLL from a gaussian plus exponential model
    '''
    pdf = get_model(kind=kind)

    if kind == 's+b':
        dat = pdf.create_sampler()
        return zfit.loss.ExtendedUnbinnedNLL(model=pdf, data=dat)

    if kind == 'signal':
        dat = pdf.create_sampler(n=1000)
        return zfit.loss.UnbinnedNLL(model=pdf, data=dat)

    raise NotImplementedError(f'Invalid kind: {kind}')
#---------------------------------------------
def _pdf_to_data(pdf : zpdf, add_weights : bool) -> zdata:
    numpy.random.seed(42)
    zfit.settings.set_seed(seed=42)

    nentries = 10_000
    data     = pdf.create_sampler(n=nentries)
    if not add_weights:
        return data

    arr_wgt  = numpy.random.normal(loc=1, scale=0.1, size=nentries)
    data     = data.with_weights(arr_wgt)

    return data
#---------------------------------------------
def placeholder_fit(
    kind     : str,
    fit_dir  : str|None,
    df       : pnd.DataFrame|None = None,
    plot_fit : bool               = True) -> zres:
    '''
    Function meant to run toy fits that produce output needed as an input
    to develop tools on top of them

    Parameters
    --------------
    kind    : Kind of fit, e.g. s+b for the simples signal plus background fit
    fit_dir : Directory where the output of the fit will go, if None, it won't save anything
    df      : pandas dataframe if passed, will reuse that data, needed to test data caching
    plot_fit: Will plot the fit or not, by default True

    Returns
    --------------
    FitResult object
    '''
    pdf  = get_model(kind)
    if fit_dir is not None:
        print_pdf(pdf, txt_path=f'{fit_dir}/pre_fit.txt')

    if df is None:
        log.warning('Using user provided data')
        data = _pdf_to_data(pdf=pdf, add_weights=True)
    else:
        data = zfit.Data.from_pandas(df, obs=pdf.space, weights=Data.weight_name)

    d_const = {'sg' : (50., 3.)}

    obj = Fitter(pdf, data)
    res = obj.fit(cfg={'constraints' : d_const})

    if fit_dir is None:
        log.debug('Not saving placeholder fit')
        return res

    log.debug('Saving placeholder fit')
    if plot_fit:
        obj   = ZFitPlotter(data=data, model=pdf)
        obj.plot(nbins=50, stacked=True)

    save_fit(
        data   =data, 
        model  =pdf, 
        res    =res, 
        fit_dir=fit_dir, 
        plt_cfg={'nbins' : 50, 'stacked' : True},
        d_const=d_const)

    return res
#---------------------------------------------
def _reformat_values(d_par : dict, fall_back_error : float|None = None) -> dict:
    '''
    Parameters
    --------------
    d_par: Dictionary formatted as:

        {'minuit_hesse': {'cl': 0.6,
                         'error': np.float64(0.04),
                         'weightcorr': <WeightCorr.FALSE: False>},
         'value'       : 0.34},

    fall_back_error: If specified (default None), will pick that value, if error not found

    Returns
    --------------
    Dictionary formatted as:

    {
        'error' : 0.04,
        'value' : 0.34
    }
    '''

    try:
        error = d_par['minuit_hesse']['error']
    except KeyError as exc:
        if fall_back_error is not None:
            error = fall_back_error
        else:
            log.error(yaml.dump(d_par))
            raise KeyError('Cannot extract error from parameters') from exc

    error = float(error)

    value = d_par['value']

    return {'value' : value, 'error' : error}
#---------------------------------------------
# Zfit utilities 
#---------------------------------------------
def zres_to_cres(res : zres, fall_back_error : float|None = None) -> DictConfig:
    '''
    Parameters
    --------------
    res            : Zfit result object
    fall_back_error: If specified (default None), will pick that value, if error not found

    Returns
    --------------
    OmegaConfig's DictConfig instance
    '''
    # This should prevent crash when result object was already frozen
    try:
        res.freeze()
    except AttributeError:
        pass

    par   = res.params
    try:
        d_par = { name : _reformat_values(d_par=d_par, fall_back_error=fall_back_error) for name, d_par in par.items()}
    except KeyError as exc:
        print(res)
        raise KeyError('Fit parameters cannot be used') from exc

    cfg = OmegaConf.create(d_par)

    return cfg
# ----------------------
def val_from_zres(res : zres, name : str) -> float:
    '''
    Parameters
    -------------
    res: Zfit result, before or after freezing
    name: Name of fitting parameter

    Returns
    -------------
    Numerical value of fitting parameter
    '''
    for par, d_val in res.params.items():
        par_name = par if isinstance(par, str) else par.name
        if par_name == name:
            return d_val['value']

    log.info(res)
    raise ValueError(f'Cannot find parameter: {name}')
#---------------------------------------------
