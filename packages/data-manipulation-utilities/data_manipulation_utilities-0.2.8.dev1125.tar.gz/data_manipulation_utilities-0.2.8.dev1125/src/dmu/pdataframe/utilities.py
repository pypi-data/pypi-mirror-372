'''
Module containing utilities for pandas dataframes
'''
import os
import yaml
import pandas as pnd

from dmu.logging.log_store import LogStore

log=LogStore.add_logger('dmu:pdataframe:utilities')
# -------------------------------------
def df_to_tex(df         : pnd.DataFrame,
              path       : str,
              hide_index : bool         = True,
              d_format   : dict[str,str]= None,
              **kwargs   : str       ) -> None:
    '''
    Saves pandas dataframe to latex

    Parameters
    -------------
    df              : Dataframe with data
    path     (str)  : Path to latex file
    hide_index      : If true (default), index of dataframe won't appear in table
    d_format (dict) : Dictionary specifying the formattinng of the table, e.g. `{'col1': '{}', 'col2': '{:.3f}', 'col3' : '{:.3f}'}`
    kwargs          : Arguments needed in `to_latex`
    '''

    if path is not None:
        dir_name = os.path.dirname(path)
        os.makedirs(dir_name, exist_ok=True)

    st = df.style
    if hide_index:
        st=st.hide(axis='index')

    if d_format is not None:
        st=st.format(formatter=d_format)

    log.info(f'Saving to: {path}')
    buf = st.to_latex(buf=path, hrules=True, **kwargs)

    return buf
# -------------------------------------
def to_yaml(df : pnd.DataFrame, path : str):
    '''
    Takes a dataframe and the path to a yaml file
    Makes the directory path if not found and saves data in YAML file
    '''
    dir_path = os.path.dirname(path)
    if dir_path != '':
        os.makedirs(dir_path, exist_ok=True)

    data = df.to_dict()

    with open(path, 'w', encoding='utf-8') as ofile:
        yaml.dump(data, ofile, Dumper=yaml.CDumper)
# ----------------------
def to_markdown(df : pnd.DataFrame, path : str) -> None:
    '''
    Parameters
    -------------
    df  : Pandas dataframe
    path: Path to markdown file
    '''
    dir_path = os.path.dirname(path)
    if dir_path != '':
        os.makedirs(dir_path, exist_ok=True)

    text = df.to_markdown()
    with open(path, 'w', encoding='utf-8') as ofile:
        ofile.write(text)
# -------------------------------------
def from_yaml(path : str) -> pnd.DataFrame:
    '''
    Takes path to a yaml file
    Makes dataframe from it and returns it
    '''
    with open(path, encoding='utf-8') as ifile:
        data = yaml.load(ifile, Loader=yaml.CSafeLoader)

    df = pnd.DataFrame(data)

    return df
# -------------------------------------
def dropna(df : pnd.DataFrame, max_frac : float = 0.02) -> pnd.DataFrame:
    '''
    Parameters
    ----------------
    df      : Pandas dataframe potentially with NaNs
    max_frac: Maximum fraction of the data that can be dropped, will raise exception beyond
    '''

    ini = len(df)
    df  = df.dropna()
    fin = len(df)

    if ini == fin:
        log.debug('No NaNs were found')
        return df

    # If fewer elements survive the filter, raise
    if fin < ini * (1 - max_frac):
        raise ValueError(f'Too man NaNs were detected: {ini} --> {fin}')

    log.info(f'Found NaNs: {ini} --> {fin}')

    return df
# -------------------------------------
