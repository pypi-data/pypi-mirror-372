'''
Module containing generic utility functions
'''
import os
import time
import json
import pickle
import inspect
from importlib.resources   import files
from importlib.util        import find_spec
from typing                import Callable, Any, cast
from functools             import wraps
from contextlib            import contextmanager

import importlib.util
import yaml
from omegaconf.errors      import ConfigKeyError
from omegaconf             import ListConfig, OmegaConf, DictConfig, ValidationError
from dmu.generic           import hashing
from dmu.generic           import utilities as gut
from dmu.logging.log_store import LogStore

TIMER_ON=False
log = LogStore.add_logger('dmu:generic:utilities')
# --------------------------------
class ConfigValidation:
    '''
    Class used to hold config validation data
    '''
    # If True, it will require:
    # - Existence of schema
    # - That validation passes
    # Or else an exception will be risen
    enforce     = False          
    schema_name = 'ConfigSchema' # When validating OmegaConf configs, this will be the top level class name of the schema
# --------------------------------
class BlockStyleDumper(yaml.SafeDumper):
    '''
    Class needed to specify proper indentation when
    dumping data to YAML files
    '''
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow=flow, indentless=False)
# ---------------------------------
@contextmanager
def enforce_schema_validation(value : bool):
    '''
    Parameters
    -------------
    value:  If True it will raise ValidationError if validation of config fails because of:
            - Schema file not found
            - Problems with the config
    '''
    old_val = ConfigValidation.enforce 
    ConfigValidation.enforce = value
    try:
        yield
    finally:
        ConfigValidation.enforce =old_val
# ---------------------------------
def load_data(package : str, fpath : str) -> Any:
    '''
    This function will load a YAML or JSON file from a data package

    Parameters
    ---------------------
    package: Data package, e.g. `dmu_data`
    path   : Path to YAML/JSON file, relative to the data package

    Returns
    ---------------------
    Dictionary or whatever structure the file is holding
    '''

    cpath = files(package).joinpath(fpath)
    cpath = str(cpath)
    data  = load_json(cpath)

    return data
# --------------------------------
def load_conf(
    package       : str,
    fpath         : str,
    resolve_paths : bool = True) -> DictConfig:
    '''
    This function will load a YAML or JSON file from a data package

    Parameters
    ---------------------
    package: Data package, e.g. `dmu_data`
    fpath  : Path to YAML/JSON file, relative to the data package
    resolve_paths: When the config is too complex, instead of including it
                   in the main YAML file, one includes the path to another
                   YAML file. Those paths will be replaced by the actual config
                   when this flag is True

    Returns
    ---------------------
    DictConfig class from the OmegaConf package
    '''
    cpath = files(package).joinpath(fpath)
    cpath = cast(str, cpath)

    cfg   = OmegaConf.load(cpath)
    cfg   = cast(DictConfig, cfg)

    _validate_schema(cfg=cfg, package=package, fpath=fpath)

    if not resolve_paths:
        return cfg

    return _resolve_sub_configs(cfg=cfg, package=package)
# ----------------------
def _validate_schema(
    cfg     : DictConfig,
    package : str, 
    fpath   : str) -> None:
    '''
    Parameters
    -------------
    cfg    : Config to be validated
    package: Name of data package where config to be validated lives
    fpath  : Relative (to package) path to config file
    '''
    spath   = _get_schema_path(package=package, fpath=fpath)
    if spath is None: 
        log.debug(f'No schema found in: {spath}')
        return

    spec  = importlib.util.spec_from_file_location('placeholder', spath)
    if spec is None:
        raise ValueError(f'Cannot load spec from: {spath}')

    smodule=importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ValueError('Loader not found')

    loader.exec_module(smodule)

    if not hasattr(smodule, ConfigValidation.schema_name):
        raise AttributeError(f'Cannot find {ConfigValidation.schema_name} in module {spath}')

    ConfigSchema = getattr(smodule, ConfigValidation.schema_name)
    schema = OmegaConf.structured(ConfigSchema)

    try:
        cfg_val = OmegaConf.merge(schema, cfg)
        OmegaConf.to_object(cfg_val)
    except (ValidationError, ConfigKeyError) as exc:
        if ConfigValidation.enforce:
            raise RuntimeError(f'Failed to validate {package}/{fpath}') from exc
# ----------------------
def _get_schema_path(package : str, fpath : str) -> str|None:
    '''
    Parameters
    -------------
    package: Name of data package with configs
    fpath  : Path to config relative to `package`

    Returns
    -------------
    Either:

    - Path to schema file, a python module
    - None, if no package was found and schema validation is not enforced 
    '''
    package = package.removesuffix('_data')
    package = f'{package}_schema'
    sname   = os.path.basename(fpath).replace('.yaml', '_config.py')

    if not find_spec(package) and ConfigValidation.enforce:
        raise FileNotFoundError(f'Cannot find schema package: {package}')

    if not find_spec(package):
        return None

    spath = files(package).joinpath(sname)
    spath = str(spath)

    if not os.path.isfile(spath) and ConfigValidation.enforce:
        raise FileNotFoundError('Missing config schema')

    if not os.path.isfile(spath):
        return None

    return spath
# ----------------------
def _resolve_sub_configs(cfg : DictConfig, package : str) -> DictConfig:
    '''
    Parameters
    -------------
    cfg    : Configuration dictionary
    package: Name of data package where secondary configurations will live

    Returns
    -------------
    Input dictionary where yaml paths have been replaced by actual configuration
    '''
    for key, val in cfg.items():
        if isinstance(val, DictConfig):
            _resolve_sub_configs(cfg=val, package=package)
            continue

        if not isinstance(val, str):
            continue

        if not val.endswith(('.yaml','.yml')):
            continue

        log.debug(f'Resolving sub-config: {val}')
        # Do not enforce validation for sub-configs
        # They might not have a schema associated
        # And their validation should be done explicitly
        # I.e. only validate top level configs
        with enforce_schema_validation(value=False):
            cfg[key] = load_conf(package=package, fpath=val)

    return cfg
# --------------------------------
def _get_module_name( fun : Callable) -> str:
    mod = inspect.getmodule(fun)
    if mod is None:
        raise ValueError(f'Cannot determine module name for function: {fun}')

    return mod.__name__
# --------------------------------
def timeit(f):
    '''
    Decorator used to time functions, it is turned off by default, can be turned on with:

    from dmu.generic.utilities import TIMER_ON
    from dmu.generic.utilities import timeit

    TIMER_ON=True

    @timeit
    def fun():
        ...
    '''
    @wraps(f)
    def wrap(*args, **kw):
        if not TIMER_ON:
            result = f(*args, **kw)
            return result

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        mod_nam = _get_module_name(f)
        fun_nam = f.__name__
        log.info(f'{mod_nam}.py:{fun_nam}; Time: {te-ts:.3f}s')

        return result
    return wrap
# --------------------------------
def dump_json(
    data      : dict|str|list|set|tuple|DictConfig|ListConfig,
    path      : str,
    sort_keys : bool = False) -> None:
    '''
    Saves data as JSON or YAML, depending on the extension, supported .json, .yaml, .yml

    Parameters
    data     : dictionary, list, etc
    path     : Path to output file where to save it
    sort_keys: Will set sort_keys argument of json.dump function
    '''
    if isinstance(data, (DictConfig, ListConfig)):
        py_data = OmegaConf.to_container(data)
    else:
        py_data = data

    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as ofile:
        if path.endswith('.json'):
            json.dump(py_data, ofile, indent=4, sort_keys=sort_keys)
            return

        if path.endswith('.yaml') or path.endswith('.yml'):
            yaml.dump(py_data, ofile, Dumper=BlockStyleDumper, sort_keys=sort_keys)
            return

        raise NotImplementedError(f'Cannot deduce format from extension in path: {path}')
# --------------------------------
def load_json(path : str):
    '''
    Loads data from JSON or YAML, depending on extension of files, supported .json, .yaml, .yml

    Parameters
    path     : Path to outut file where data is saved
    '''

    with open(path, encoding='utf-8') as ofile:
        if path.endswith('.json'):
            data = json.load(ofile)
            return data

        if path.endswith('.yaml') or path.endswith('.yml'):
            data = yaml.safe_load(ofile)
            return data

        raise NotImplementedError(f'Cannot deduce format from extension in path: {path}')
# --------------------------------
def dump_pickle(data, path : str) -> None:
    '''
    Saves data as pickle file

    Parameters
    data     : dictionary, list, etc
    path     : Path to output file where to save it
    '''
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)

    with open(path, 'wb') as ofile:
        pickle.dump(data, ofile)
# --------------------------------
def load_pickle(path : str) -> None:
    '''
    loads data file

    Parameters
    path     : Path to output file where to save it
    '''
    with open(path, 'rb') as ofile:
        data = pickle.load(ofile)

    return data
# --------------------------------
@contextmanager
def silent_import():
    '''
    In charge of suppressing messages
    of imported modules
    '''
    saved_stdout_fd = os.dup(1)
    saved_stderr_fd = os.dup(2)

    with open(os.devnull, 'w', encoding='utf-8') as devnull:
        os.dup2(devnull.fileno(), 1)
        os.dup2(devnull.fileno(), 2)
        try:
            yield
        finally:
            os.dup2(saved_stdout_fd, 1)
            os.dup2(saved_stderr_fd, 2)
            os.close(saved_stdout_fd)
            os.close(saved_stderr_fd)
# --------------------------------
# Caching
# --------------------------------
def cache_data(obj : Any, hash_obj : Any) -> None:
    '''
    Will save data to a text file using a name from a hash

    Parameters
    -----------
    obj      : Object that can be saved to a text file, e.g. list, number, dictionary
    hash_obj : Object that can be used to get hash e.g. immutable
    '''
    try:
        json.dumps(obj)
    except Exception as exc:
        raise ValueError('Object is not JSON serializable') from exc

    val  = hashing.hash_object(hash_obj)
    path = f'/tmp/dmu/cache/{val}.json'
    gut.dump_json(obj, path)
# --------------------------------
def load_cached(hash_obj : Any, on_fail : Any = None) -> Any:
    '''
    Loads data corresponding to hash from hash_obj

    Parameters
    ---------------
    hash_obj: Object used to calculate hash, which is in the file name
    on_fail : Value returned if no data was found.
              By default None, and it will just raise a FileNotFoundError
    '''
    val  = hashing.hash_object(hash_obj)
    path = f'/tmp/dmu/cache/{val}.json'
    if os.path.isfile(path):
        data = gut.load_json(path)
        return data

    if on_fail is not None:
        return on_fail

    raise FileNotFoundError(f'Cannot find cached data at: {path}')
# --------------------------------
