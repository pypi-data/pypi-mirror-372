'''
This module contains
'''
import os
import sys
import shutil
from types      import NoneType
from pathlib    import Path
from contextlib import contextmanager

from dmu.generic           import hashing
from dmu.logging.log_store import LogStore

log=LogStore.add_logger('dmu:workflow:cache')
# ---------------------------
class Cache:
    '''
    Class meant to wrap other classes in order to

    - Keep track of the inputs through hashes
    - Load cached data, if found, and prevent calculations

    The following directories will be important:

    out_dir  : Directory where the outputs will go, specified by the user
    cache_dir: Subdirectory of out_dir, ${out_dir}/.cache
    hash_dir : Subdirectory of out_dir, ${out_dir}/.cache/{hash}
               Where {hash} is a 10 alphanumeric representing the has of the inputs

    # On skipping caching

    This is controlled by `_l_skip_class` which is a list of class names:

    - These classes will have the caching turned off
    - If the list is empty, caching runs for everything
    - If the list is None, caching is turned off for everything
    '''
    _cache_root     : str|None = None
    _l_skip_class   : list[str]|None = []
    # ---------------------------
    def __init__(self, out_path : str, **kwargs):
        '''
        Parameters
        ---------------
        out_path: Path to directory where outputs will go
        kwargs  : Key word arguments symbolizing identity of inputs, used for hashing
                  If argument `code` is already in kwargs, it will not calculate the
                  code's hash, i.e. Code changes do not invalidate the hash, useful for testing
        '''
        if Cache._cache_root is None:
            raise ValueError('Caching directory not set')

        log.debug(f'Using {Cache._cache_root} root directory for caching')
        if 'code' not in kwargs:
            kwargs['code']  = self._get_code_hash()
        else:
            log.warning('Not using code for hashing')

        self._out_path  = os.path.normpath(f'{Cache._cache_root}/{out_path}')
        log.debug(f'Using {self._out_path} output path')
        os.makedirs(self._out_path, exist_ok=True)

        self._dat_hash  = kwargs

        self._cache_dir = self._get_dir(kind='cache')
        self._hash_dir  : str
    # ---------------------------
    def _get_code_hash(self) -> str:
        '''
        If `MyTool` inherits from `Cache`. `mytool.py` git commit hash
        should be returned
        '''
        cls   = self.__class__
        mod   = sys.modules.get(cls.__module__)
        if mod is None:
            raise ValueError(f'Module not found: {cls.__module__}')

        if mod.__file__ is None:
            raise ValueError(f'Cannot extract file path for module: {cls.__module__}')

        fname = mod.__file__
        fpath = os.path.abspath(fname)
        val   = hashing.hash_file(path=fpath)

        log.debug(f'Using hash for: {fpath} = {val}')

        return val
    # ---------------------------
    def _get_dir(
            self,
            kind : str,
            make : bool = True) -> str:
        '''
        Parameters
        --------------
        kind : Kind of directory, cash, hash
        make : If True (default) will try to make directory
        '''
        if   kind == 'cache':
            dir_path  = f'{self._out_path}/.cache'
        elif kind == 'hash':
            cache_dir = self._get_dir(kind='cache')
            hsh       = hashing.hash_object(self._dat_hash)
            dir_path  = f'{cache_dir}/{hsh}'
        else:
            raise ValueError(f'Invalid directory kind: {kind}')

        if make:
            os.makedirs(dir_path, exist_ok=True)

        return dir_path
    # ---------------------------
    def _cache(self) -> None:
        '''
        Meant to be called after all the calculations finish
        It will copy all the outputs of the processing
        to a hashed directory
        '''
        self._hash_dir  = self._get_dir(kind= 'hash')
        log.info(f'Caching outputs to: {self._hash_dir}')

        for source in Path(self._out_path).glob('*'):
            if str(source) == self._cache_dir:
                continue

            log.debug(str(source))
            log.debug('-->')
            log.debug(self._hash_dir)
            log.debug('')

            if source.is_dir():
                shutil.copytree(source, self._hash_dir+'/'+source.name, dirs_exist_ok=True)
            else:
                shutil.copy2(source, self._hash_dir)

        self._delete_from_output(only_links=False)
        self._copy_from_hashdir()
    # ---------------------------
    def _delete_from_output(self, only_links : bool) -> None:
        '''
        Delete all objects from _out_path directory, except for `.cache`

        only_links: If true will only delete links
        '''
        for path in Path(self._out_path).iterdir():
            if str(path) == self._cache_dir:
                log.debug(f'Skipping cache dir: {self._cache_dir}')
                continue

            # These will always be symbolic links
            if only_links and not path.is_symlink():
                log.warning(f'Found a non-symlink not deleting: {path}')
                continue

            log.debug(f'Deleting {path}')
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
    # ---------------------------
    def _copy_from_hashdir(self) -> None:
        '''
        Copies all the objects from _hash_dir to _out_path
        '''
        for source in Path(self._hash_dir).iterdir():
            target = f'{self._out_path}/{source.name}'
            log.debug(f'{str(source):<50}{"-->"}{target}')

            os.symlink(source, target)
    # ---------------------------
    def _dont_cache(self) -> bool:
        '''
        Returns
        ---------------
        Flag that if:

        True : Will stop the derived class from using caching (i.e. caching is off)
        False: Cache
        '''
        if Cache._l_skip_class is None:
            log.info('No class will be cached')
            return True

        if len(Cache._l_skip_class) == 0:
            log.debug('All classes will be cached')
            return False

        class_name = self.__class__.__name__

        skip = class_name in Cache._l_skip_class

        if skip:
            log.warning(f'Caching turned off for {class_name}')
        else:
            log.debug(f'Caching turned on  for {class_name}')

        return skip
    # ---------------------------
    def _copy_from_cache(self) -> bool:
        '''
        Checks if hash directory exists:

        No : Returns False
        Yes:
            - Removes contents of `out_path`, except for .cache
            - Copies the contents of `hash_dir` to `out_dir`

        Returns
        ---------------
        True if the object, cached was found, false otherwise.
        '''
        if self._dont_cache():
            # If not copying from cache, will need to remove what is
            # in the output directory, so that it gets replaced with
            # new outputs
            self._delete_from_output(only_links=False)
            log.info('Not picking already cached outputs, remaking them')
            return False

        hash_dir = self._get_dir(kind='hash', make=False)
        if not os.path.isdir(hash_dir):
            log.debug(f'Hash directory {hash_dir} not found, not caching')
            self._delete_from_output(only_links=False)
            return False

        self._hash_dir = hash_dir
        log.debug(f'Data found in hash directory: {self._hash_dir}')

        self._delete_from_output(only_links=False)
        self._copy_from_hashdir()

        return True
    # ---------------------------
    @classmethod
    def turn_off_cache(cls, val : list[str]|None):
        '''
        Parameters
        ------------------
        val: List of names of classes that inherit from `Cache`.
        If None, will not cache for any class.
        By default this is an empty list and it will cache for every class
        '''
        if not isinstance(val, (NoneType, list)):
            log.error('This manager expects: list[str]|None')
            raise ValueError(f'Invalid value: {val}')

        old_val = cls._l_skip_class
        @contextmanager
        def _context():
            cls._l_skip_class = val
            try:
                yield
            finally:
                cls._l_skip_class = old_val

        return _context()
    # ---------------------------
    @classmethod
    def set_cache_root(cls, root : str) -> None:
        '''
        Sets the path to the directory WRT which the _out_path_
        will be placed.

        This is meant to be called once per execution and has a lock
        that will raise an exception if called twice
        '''
        if cls._cache_root is not None:
            raise ValueError(f'Trying to set {root}, but already found {cls._cache_root}')

        os.makedirs(root, exist_ok=True)

        cls._cache_root = root
# ---------------------------
