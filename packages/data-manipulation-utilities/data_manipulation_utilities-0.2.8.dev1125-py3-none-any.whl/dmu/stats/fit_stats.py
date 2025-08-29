'''
Module with FitStats class
'''

import re
import pprint
import pickle
from typing import Union

import numpy
import pandas                as pnd
from zfit.result            import FitResult  as zres
from dmu.logging.log_store  import LogStore

log = LogStore.add_logger('dmu:fit_stats')
# -------------------------------
class FitStats:
    '''
    Class meant to provide fit statistics
    '''
    # -------------------------------
    def __init__(self, fit_dir : str):
        '''
        fit_dir :  Path to directory where fit outputs are stored
        '''
        self._fit_dir = fit_dir
        self._regex   = r'^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*$'
        self._sig_yld = 'nsig'

        # Functions need to be called at the end
        # When all the needed attributes are already set
        self._df      = self._get_data()
    # -------------------------------
    def _row_from_line(self, line : str) -> Union[list,None]:
        mtch = re.match(self._regex, line)
        if not mtch:
            return None

        [name, value, low, high, is_floating, mu_sg] = mtch.groups()

        if mu_sg == 'none':
            mu = numpy.nan
            sg = numpy.nan
        else:
            [mu, sg] = mu_sg.split('___')
            mu       = float(mu)
            sg       = float(sg)

        is_floating = int(is_floating)  #Direct conversion from '0' to bool will break this
        is_floating = bool(is_floating)
        row         = [name, float(value), float(low), float(high), is_floating, mu, sg]

        return row
    # -------------------------------
    def _get_data(self) -> pnd.DataFrame:
        fit_path = f'{self._fit_dir}/post_fit.txt'

        with open(fit_path, encoding='utf-8') as ifile:
            l_line = ifile.read().splitlines()

        df = pnd.DataFrame(columns=['name', 'value', 'low', 'high', 'float', 'mu', 'sg'])
        for line in l_line:
            row = self._row_from_line(line)
            if row is None:
                log.debug(f'Row not found in line: {line}')
                continue

            df.loc[len(df)] = row

        if len(df) == 0:
            raise ValueError(f'Empty dataframe with statistics built from: {fit_path}')

        df = self._attach_errors(df)
        log.debug(df)

        return df
    # -------------------------------
    def _error_from_res(self, row : pnd.Series, res : zres) -> float:
        if not row['float']: # If this parameter is fixed in the fit, the error is zero
            return 0

        name = row['name']
        if name not in res.params:
            for this_name in res.params:
                log.info(this_name)

            raise KeyError(f'{name} not found')

        d_data = res.params[name]

        if 'hesse' in d_data:
            return d_data['hesse']['error']

        if 'minuit_hesse' in d_data:
            return d_data['minuit_hesse']['error']

        pprint.pprint(d_data)
        raise KeyError('Cannot find error in dictionary')
    # -------------------------------
    def _attach_errors(self, df : pnd.DataFrame) -> pnd.DataFrame:
        pkl_path = f'{self._fit_dir}/fit.pkl'
        with open(pkl_path, 'rb') as ifile:
            res = pickle.load(ifile)

        df['error'] = df.apply(lambda row : self._error_from_res(row, res), axis=1)

        return df
    # -------------------------------
    def print_blind_stats(self) -> None:
        '''
        Will print statistics, excluding signal information
        '''
        df_blind = self._df[self._df['name'] != self._sig_yld]
        log.info(df_blind)
    # -------------------------------
    def get_value(self, name : str, kind : str) -> float:
        '''
        Returns float with value associated to fit
        name : Name of variable, e.g. mu, sg, nsig
        kind : Type of quantity, e.g. value, error
        '''

        log.info(f'Retrieving signal yield from {name} and {kind}')
        df   = self._df[self._df['name'] == name]
        nrow = len(df)
        if nrow != 1:
            self.print_blind_stats()
            raise ValueError(f'Cannot retrieve one and only one row, found {nrow}')

        val = df[kind]

        return float(val)
# -------------------------------
