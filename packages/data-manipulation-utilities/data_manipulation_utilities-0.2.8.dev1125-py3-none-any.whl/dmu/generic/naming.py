'''
This module contains functions meant to deal with names
i.e. strings that represent names
'''

import re

from dmu.logging.log_store import LogStore

log=LogStore.add_logger('dmu:generic:naming')
# --------------------------------
def clean_special_characters(name : str) -> str:
    '''
    Parameters
    ----------------
    name: String with potentially parenthesis, dollar signs, etc

    Returns
    ----------------
    Cleaned string, where special signs were removed or replaced
    '''
    name = name.replace('/' ,  '_')
    name = name.replace('\\',  '_')
    name = name.replace('||', 'or')
    name = name.replace(' ' ,  '_')
    name = name.replace('<' , 'lt')
    name = name.replace('>' , 'gt')
    name = name.replace('=' , 'eq')
    name = name.replace('{' ,  '_')
    name = name.replace('}' ,  '_')
    name = name.replace('.' ,  'p')
    name = name.replace('$' ,  '_')
    name = name.replace('^' ,'hat')
    name = name.replace('&&','and')
    name = re.sub(r'_+' , '_', name)

    return name
# --------------------------------
