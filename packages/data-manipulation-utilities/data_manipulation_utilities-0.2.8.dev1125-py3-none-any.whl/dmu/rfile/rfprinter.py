'''
Module containing RFPrinter
'''
import os

from typing import Union
from ROOT   import TFile

from dmu.logging.log_store import LogStore

log = LogStore.add_logger('dmu:rfprinter')
#--------------------------------------------------
class RFPrinter:
    '''
    Class meant to print summary of ROOT file
    '''
    #-----------------------------------------
    def __init__(self, path : str):
        '''
        Takes path to root file
        '''
        if not os.path.isfile(path):
            raise FileNotFoundError(f'Cannot find {path}')

        self._root_path = path
    #-----------------------------------------
    def _get_trees(self, ifile):
        '''
        Takes TFile object, returns list of TTree objects
        '''
        l_key=ifile.GetListOfKeys()

        l_tree=[]
        for key in l_key:
            obj=key.ReadObj()
            if obj.InheritsFrom("TTree"):
                fname=ifile.GetName()
                tname=obj.GetName()

                title=f'{fname}/{tname}'
                obj.SetTitle(title)
                l_tree.append(obj)
            elif obj.InheritsFrom("TDirectory"):
                l_tree+=self._get_trees(obj)

        return l_tree
    #---------------------------------
    def _get_tree_info(self, tree):
        '''
        Takes ROOT tree, returns list of strings with information about tree
        '''
        l_branch= tree.GetListOfBranches()
        l_line  = []
        for branch in l_branch:
            bname = branch.GetName()
            leaf  = branch.GetLeaf(bname)
            try:
                btype = leaf.GetTypeName()
            except:
                log.warning(f'Cannot read {bname}')
                continue

            l_line.append(f'{"":4}{bname:<100}{btype:<40}')

        return l_line
    #-----------------------------------------
    def _get_summary_path(self, file_name : Union[str,None]) -> str:
        if file_name is None:
            text_path = self._root_path.replace('.root', '.txt')
            return text_path

        root_dir = os.path.dirname(self._root_path)

        return f'{root_dir}/{file_name}'
    #-----------------------------------------
    def _save_info(self, l_info : list[str], file_name : Union[str,None]) -> None:
        '''
        Takes list of strings, saves it to text file
        '''

        text_path = self._get_summary_path(file_name)
        with open(text_path, 'w', encoding='utf-8') as ofile:
            for info in l_info:
                ofile.write(f'{info}\n')

        log.info(f'Saved to: {text_path}')
    #-----------------------------------------
    def _get_info(self) -> list[str]:
        l_info = []
        log.info(f'Reading from : {self._root_path}')
        with TFile.Open(self._root_path) as ifile:
            l_tree = self._get_trees(ifile)
            for tree in l_tree:
                l_info+= self._get_tree_info(tree)

        return l_info
    #-----------------------------------------
    def save(self, file_name : Union[str,None] = None, to_screen : bool = False, raise_on_fail : bool = True) -> None:
        '''
        Will save a text file with the summary of the ROOT file contents

        file_name    : If used, name the file with the summary this way. Othewise, use ROOT file with .txt extension
        to_screen    : If true, will print to screen, default=False
        raise_on_fail: If cannot open ROOT file, will raise exeption (default), otherwise will only show warning.
        '''

        try:
            l_info = self._get_info()
        except OSError as exc:
            if raise_on_fail:
                raise OSError(f'Cannot open: {self._root_path}') from exc

            log.warning(f'Cannot open: {self._root_path}')
            return

        self._save_info(l_info, file_name=file_name)
        if to_screen:
            for info in l_info:
                log.info(info)
#-----------------------------------------
