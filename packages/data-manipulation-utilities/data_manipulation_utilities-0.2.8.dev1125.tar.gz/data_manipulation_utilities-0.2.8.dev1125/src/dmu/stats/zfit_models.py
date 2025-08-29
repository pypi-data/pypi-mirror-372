'''
Module meant to hold classes defining PDFs that can be used by ZFIT
'''

import zfit
from zfit   import z

#-------------------------------------------------------------------
class HypExp(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'alpha', 'beta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        ap   = self.params['alpha']
        bt   = self.params['beta']

        u   = (x - mu)
        val = z.exp(-bt * x) / (1 + z.exp(-ap * u))

        return val
#-------------------------------------------------------------------
class ModExp(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'alpha', 'beta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        ap   = self.params['alpha']
        bt   = self.params['beta']

        u   = x - mu
        val = (1 - z.exp(-ap * u)) * z.exp(-bt * u)

        return val
#-------------------------------------------------------------------
class GenExp(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'sg', 'alpha', 'beta']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        sg   = self.params['sg']
        ap   = self.params['alpha']
        bt   = self.params['beta']

        u   = (x - mu) / sg
        val = (1 - z.exp(-ap * u)) * z.exp(-bt * u)

        return val
#-------------------------------------------------------------------
class FermiDirac(zfit.pdf.ZPDF):
    _N_OBS  = 1
    _PARAMS = ['mu', 'ap']

    def _unnormalized_pdf(self, x):
        x    = z.unstack_x(x)
        mu   = self.params['mu']
        ap   = self.params['ap']

        exp  = (x - mu) / ap
        den  = 1 + z.exp(exp)

        return 1. / den
#-------------------------------------------------------------------
