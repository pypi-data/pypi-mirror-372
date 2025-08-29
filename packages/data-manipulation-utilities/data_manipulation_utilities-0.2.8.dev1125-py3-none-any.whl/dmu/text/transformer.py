'''
Module used to hold transformer class
'''

import os
import pprint

import toml
import numpy

from dmu.logging.log_store import LogStore

log = LogStore.add_logger('dmu:text:transformer')
# -------------------------------------------------------------------------------------------
class transformer:
    # pyling disable = invalid-name
    '''
    Class used to apply transformations to text files
    '''
    # -----------------------------------------
    def __init__(self, txt_path=None, cfg_path=None):
        '''
        txt_path (str): Path to text file to be transformed, can have any extension, py, txt, log, etc
        cfg_path (str): Path to TOML file holding configuration needed for transformations
        '''
        self._txt_path = txt_path
        self._cfg_path = cfg_path
        self._suffix   = 'trf'

        self._l_line   = None
        self._cfg      = None

        self._initialized = False
    # -----------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        self._check_file(self._txt_path)
        self._check_file(self._cfg_path)
        self._load_input()
        self._cfg = toml.load(self._cfg_path)

        self._initialized=True
    # -----------------------------------------
    def _check_file(self, file_path):
        '''
        Will raise exception if path not found

        file_path (str): path to file
        '''
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')

        log.debug(f'Found: {file_path}')
    # -----------------------------------------
    def _load_input(self):
        '''
        Will open  self._txt_path and put the lines in self._l_line
        '''
        with open(self._txt_path) as ifile:
            self._l_line = ifile.read().splitlines()

            nline = len(self._l_line)
            log.info(f'Found {nline} lines in {self._txt_path}')
    # -----------------------------------------
    def _get_out_path(self, out_path):
        '''
        Will return name of output file
        If arg is not None, will make directory (in case it does not exist) and return arg
        If arg is None, will rename input path using suffix  and return
        '''
        if out_path is not None:
            dir_name = os.path.dirname(out_path)
            os.makedirs(dir_name, exist_ok=True)

            return out_path

        file_name = os.path.basename(self._txt_path)
        if '.' not in file_name:
            return f'{file_name}_{self._suffix}'

        l_part     = file_name.split('.')
        bef_ext    = l_part[-2]
        l_part[-2] = f'{bef_ext}_{self._suffix}'

        file_name  = '.'.join(l_part)
        file_dir   = os.path.dirname(self._txt_path)

        return f'{file_dir}/{file_name}'
    # -----------------------------------------
    def _transform(self, l_line, trf):
        log.info(f'{"":<4}{trf}')

        if trf == 'append':
            return self._apply_append(l_line)
        else:
            raise ValueError(f'Invalid transformation: {trf}')

        return l_line
    # -----------------------------------------
    def _apply_append(self, l_line):
        '''
        Will take list of lines
        and return list of lines with extra lines appended
        according to config file
        '''
        d_append = self._cfg['trf']['append']

        for target, l_to_be_added in d_append.items():
            l_to_be_added = self._format_lines(l_to_be_added)
            arr_line      = numpy.array(self._l_line)
            arr_index,    = numpy.where(self._find_append_index(arr_line, target))

            if arr_index.size  == 0:
                pprint.pprint(self._l_line)
                raise RuntimeError(f'No instance of \"{target}\" found in \"{self._txt_path}\"')

            for index in arr_index:
                org_line      = l_line[index]
                ext_line      = '\n'.join(l_to_be_added)
                l_line[index] = f'{org_line}\n{ext_line}'

        return l_line
    # -----------------------------------------
    def _find_append_index(self, l_line, target):
        '''
        Returns list of flags denoting if target was or not fouund in list l_line
        target can be exact or included in the l_line elements
        '''
        is_subst = False
        try:
            is_subst = self._cfg['settings']['as_substring']
        except:
            pass

        if not is_subst:
            log.debug(f'Searching exact matches for target: {target}')
            l_flag = [ target == element for element in l_line ]
        else:
            log.debug(f'Searching with substrings for target: {target}')
            l_flag = [ target in element for element in l_line ]

        return l_flag
    # -----------------------------------------
    def _format_lines(self, l_line):
        '''
        If format was specified in the settings section, will format the
        elements of the input list of lines
        '''
        if 'settings' not in self._cfg:
            return l_line

        if 'format'   not in self._cfg['settings']:
            return l_line

        fmt         = self._cfg['settings']['format']
        l_formatted = [ fmt.format(line) for line in l_line ]

        return l_formatted
    # -----------------------------------------
    def save_as(self, out_path=None):
        '''
        Saves text file after transformation to `out_path`
        If no path is passed, will name as:

        /some/dir/file.txt -> /some/dir/file_trf.txt
        '''
        self._initialize()

        log.info(20 * '-')
        log.info('Applying transformations')
        log.info(20 * '-')
        for trf in  self._cfg['trf']:
            self._l_line = self._transform(self._l_line, trf)

        out_path = self._get_out_path(out_path)
        log.info(f'Saving to: {out_path}')
        with open(out_path, 'w') as ofile:
            text = '\n'.join(self._l_line)
            ofile.write(text)
# -------------------------------------------------------------------------------------------
