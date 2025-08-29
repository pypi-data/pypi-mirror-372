'''
Module intended to wrap zfit

Needed in order to silence tensorflow messages
'''
# pylint: disable=unused-import, wrong-import-order

try:
    import ROOT
except ImportError:
    pass

import dmu.generic.utilities as gut
with gut.silent_import():
    import tensorflow

import zfit
