'''
Module containing plot class, used to plot fits
'''
# pylint: disable=too-many-instance-attributes, too-many-arguments

import math
import warnings
import pprint

import zfit
import hist
import mplhep
import tensorflow            as tf
import pandas                as pd
import numpy                 as np
import matplotlib.pyplot     as plt
from matplotlib.axes        import Axes
from zfit.core.basepdf      import BasePDF    as zpdf

import dmu.generic.utilities as gut
from dmu.logging.log_store  import LogStore

log = LogStore.add_logger('dmu:zfit_plotter')
#----------------------------------------
class ZFitPlotter:
    '''
    Class used to plot fits done with zfit
    '''
    #----------------------------------------
    def __init__(self, data=None, model=None, weights=None, result=None, suffix=''):
        '''
        obs: zfit space you are using to define the data and model
        data: the data you are fit on
        weights: 1D numpy array of weights
        total_model: the final total fit model
        '''
        # pylint: disable=too-many-positional-arguments

        self.obs               = model.space
        self.data              = self._data_to_zdata(model.space, data, weights)
        self.lower, self.upper = self.data.data_range.limit1d
        self.total_model       = model
        self.x                 = np.linspace(self.lower, self.upper, 2000)
        self.data_np           = zfit.run(self.data.unstack_x())
        self.data_weight_np    = np.ones_like(self.data_np) if self.data.weights is None else zfit.run(self.data.weights)

        self.errors            = []
        self._l_def_col        = []
        self._result           = result
        self._suffix           = suffix
        self._leg              = {}
        self._col              = {}
        self._l_blind          = None
        self._l_plot_components= None
        self.axs               : tuple[Axes,...]
        self._figsize          = None
        self._leg_loc          = None

        self.dat_xerr : bool

        # zfit.settings.advanced_warnings['extend_wrapped_extended'] = False
        warnings.filterwarnings("ignore")
    #----------------------------------------
    def _initialize(self):
        import matplotlib.colors as mcolors

        self._l_def_col = list(mcolors.TABLEAU_COLORS.keys())
    #----------------------------------------
    def _data_to_zdata(self, obs, data, weights):
        if isinstance(data, zfit.Data):
            return data

        if isinstance(data, np.ndarray):
            data = zfit.Data.from_numpy (obs=obs, array=data           , weights=weights)
        elif isinstance(data, pd.Series):
            data = zfit.Data.from_pandas(obs=obs, df=pd.DataFrame(data), weights=weights)
        elif isinstance(data, pd.DataFrame):
            data = zfit.Data.from_pandas(obs=obs, df=data              , weights=weights)
        else:
            raise ValueError(f'Passed data is of usupported type {type(data)}')

        return data
    #----------------------------------------
    def _get_errors(
            self,
            nbins  : int = 100,
            l_range: list[tuple[float,float]]|None = None) -> list[float]:
        '''
        Parameters
        ---------------------
        nbins  : Number of bins
        l_range: List of ranges where data should be picked, if None, will pick full range

        Returns
        ---------------------
        list of errors associated to histogram filled with data
        '''
        dat, wgt  = self._get_range_data(l_range=l_range, blind=False)
        data_hist = hist.Hist.new.Regular(
                nbins,
                self.lower,
                self.upper,
                name       =self.obs.obs[0],
                underflow  =False,
                overflow   =False)

        data_hist = data_hist.Weight()
        data_hist.fill(dat, weight=wgt)

        tmp_fig, tmp_ax = plt.subplots()
        errorbars       = mplhep.histplot(
            data_hist,
            yerr     =True,
            color    ='white',
            histtype ='errorbar',
            label    =None,
            ax       =tmp_ax)

        lines  = errorbars[0].errorbar[2]
        segs   = lines[0].get_segments()
        values = data_hist.values()

        l_error=[]
        for i in range(nbins):
            seg = segs[i]
            val = values[i]

            try:
                low =  val - seg[0][1]
                up  = -val + seg[1][1]
            except IndexError as exc:
                raise IndexError(f'Cannot read the upper/lower errors, found {seg}') from exc

            l_error.append((low, up))

        plt.close(tmp_fig)

        return l_error
    #----------------------------------------
    def _get_range_data(
            self,
            l_range : list[tuple[float,float]]|None,
            blind   : bool =True) -> tuple[np.ndarray, np.ndarray]:
        '''
        Parameters
        -----------------
        l_range: List of ranges, i.e. tuples of bounds
        blind  : If true (default) will blind the range specified, i.e. will exclude it

        Returns
        -----------------
        Tuple with two numpy arrays defined in those ranges, with the observable and the weights.
        '''
        sdat  = self.data_np
        swgt  = self.data_weight_np
        dmat  = np.array([sdat, swgt]).T

        if blind and self._l_blind is not None:
            log.debug(f'Blinding data with: {self._l_blind}')
            _, min_val, max_val = self._l_blind
            dmat = dmat[(dmat.T[0] < min_val) | (dmat.T[0] > max_val)]

        if l_range is None:
            [dat, wgt] = dmat.T
            self._check_data(dat=dat, wgt=wgt)

            return dat, wgt

        l_dat = []
        l_wgt = []
        for lo, hi in l_range:
            dmat_f = dmat[(dmat.T[0] > lo) & (dmat.T[0] < hi)]

            [dat, wgt] = dmat_f.T

            l_dat.append(dat)
            l_wgt.append(wgt)

        dat_f = np.concatenate(l_dat)
        wgt_f = np.concatenate(l_wgt)

        self._check_data(dat=dat_f, wgt=wgt_f)

        return dat_f, wgt_f
    #----------------------------------------
    def _check_data(
            self,
            dat : np.ndarray,
            wgt : np.ndarray) -> None:
        '''
        Checks for empty data, etc

        Parameters
        ------------
        Numpy arrays with data and weights
        '''

        if dat.shape != wgt.shape:
            raise ValueError(f'Shapes or data and weights differ: {dat.shape}/{wgt.shape}')

        if len(dat) == 0:
            raise ValueError('Dataset is empty')
    #----------------------------------------
    def _plot_data(self, ax, nbins=100, l_range=None):
        dat, wgt  = self._get_range_data(l_range, blind=True)
        data_hist = hist.Hist.new.Regular(nbins, self.lower, self.upper, name=self.obs.obs[0], underflow=False, overflow=False)
        data_hist = data_hist.Weight()
        data_hist.fill(dat, weight=wgt)

        mplhep.histplot(
                data_hist,
                yerr     = True,
                color    = 'black',
                histtype = 'errorbar',
                label    = self._leg.get('Data', 'Data'),
                ax       = ax,
                xerr     = self.dat_xerr)
    #----------------------------------------
    def _pull_hist(self, pdf_hist, nbins, data_yield, l_range=None):
        pdf_values= pdf_hist.values()
        dat, wgt  = self._get_range_data(l_range, blind=False)
        data_hist = hist.Hist.new.Regular(nbins, self.lower, self.upper, name=self.obs.obs[0], underflow=False, overflow=False)
        data_hist = data_hist.Weight()
        data_hist.fill(dat, weight=wgt)

        data_values = data_hist.values()
        pdf_tot     = sum(pdf_values)
        pdf_scl     = data_yield / pdf_tot

        pdf_values  = [ value * pdf_scl for value in pdf_values ]
        pull_errors = [[], []]
        pulls       = []

        for [low, up], pdf_val, dat_val in zip(self.errors, pdf_values, data_values):
            res = float(dat_val - pdf_val)
            err = low if res > 0 else up
            pul = res / err

            # If the data is weighted
            # and the data does not exist
            # The pulls will have an error of zero => pull is inf
            # Ignore these cases
            if math.isinf(pul):
                pass
            elif abs(pul) > 5:
                log.info(f'Pull: {pul:.2f}=({dat_val:.2f}-{pdf_val:.2f})/{err:.2f}')
            else:
                log.debug(f'Pull: {pul:.2f}=({dat_val:.2f}-{pdf_val:.2f})/{err:.2f}')

            pulls.append(pul)
            pull_errors[0].append(low / err)
            pull_errors[1].append(up  / err)

        hst            = hist.axis.Regular(nbins, self.lower, self.upper, name="pulls")
        pull_hist      = hist.Hist(hst)
        pull_hist[...] = pulls

        return pull_hist, pull_errors
    #----------------------------------------
    def _plot_pulls(self, ax, nbins, data_yield, l_range):
        obs_name   = self.obs.obs[0]
        binning    = zfit.binned.RegularBinning(bins=nbins, start=self.lower, stop=self.upper, name=obs_name)
        binned_obs = zfit.Space(obs_name, binning=binning)
        binned_pdf = zfit.pdf.BinnedFromUnbinnedPDF(self.total_model, binned_obs)
        pdf_hist   = binned_pdf.to_hist()

        pull_hist, pull_errors = self._pull_hist(pdf_hist, nbins, data_yield, l_range=l_range)

        mplhep.histplot(
            pull_hist,
            color   = "black",
            histtype= "errorbar",
            yerr    = np.array(pull_errors),
            ax      = ax,
        )
    #----------------------------------------
    def _get_zfit_gof(self):
        if not hasattr(self._result, 'gof'):
            return None

        chi2, ndof, pval = self._result.gof

        rchi2 = chi2/ndof

        return f'$\chi^2$/NdoF={chi2:.2f}/{ndof}={rchi2:.2f}\np={pval:.3f}'
    #----------------------------------------
    def _get_text(self, ext_text):
        gof_text = self._get_zfit_gof()

        if ext_text is     None and gof_text is     None:
            return None

        if ext_text is not None and gof_text is     None:
            return ext_text

        if ext_text is     None and gof_text is not None:
            return gof_text

        return f'{ext_text}\n{gof_text}'
    #----------------------------------------
    def _get_pars(self):
        '''
        Will return a dictionary with:
        ```
        par_name -> [value, error]
        ```

        if error is not available, will assign zeros
        '''
        pdf = self.total_model

        if self._result is not None:
            d_par = {}
            for par, d_val in self._result.params.items():
                val = d_val['value']
                name= par if isinstance(par, str) else par.name
                try:
                    err = d_val['minuit_hesse']['error']
                except KeyError:
                    log.warning(f'Cannot extract {name} Hesse errors, using zeros')
                    pprint.pprint(d_val)
                    err = 0

                d_par[name] = [val, err]
        else:
            s_par = pdf.get_params()
            d_par = {par.name : [par.value(), 0] for par in s_par}

        return d_par
    #----------------------------------------
    def _add_pars_box(self, add_pars):
        '''
        Will add parameter values to box to the right of fit plot

        Parameters:
        ------------------
        add_pars (list|str): List of names of parameters to be added or string with value 'all' to add all fit parameters.
        '''
        d_par = self._get_pars()

        line = ''
        for name, [val, err] in d_par.items():
            if add_pars != 'all' and name not in add_pars:
                continue

            line += f'{name:<20}{val:>10.3e}{"+/-":>5}{err:>10.3e}\n'

        plt.text(0.65, 0.75, line, fontsize=12, transform=plt.gcf().transFigure)
    #----------------------------------------
    def _get_axis(
        self,
        add_pars   : list[str]|None,
        skip_pulls : bool) -> tuple[Axes,...]:
        '''
        Parameters
        ----------------
        add_pars  : Parameters with values to add in figure, by default None
        skip_pulls: If true will only draw fit

        Returns
        ----------------
        Tuple with axes for main fit and pull
        '''
        plt.style.use(mplhep.style.LHCb2)
        if skip_pulls:
            _, (ax) = plt.subplots(1)
            return (ax,)

        if add_pars is None:
            fig       = plt.figure()
            gs        = fig.add_gridspec(nrows=2, ncols=1, hspace=0.1, height_ratios=[4, 1])
            axs       = gs.subplots(sharex=True)
            taxs      = tuple(axs.flat)

            return taxs

        fig = plt.figure(figsize=self._figsize)
        ax1 = plt.subplot2grid((4,40),(0, 0), rowspan=3, colspan=25)
        ax2 = plt.subplot2grid((4,40),(3, 0), rowspan=1, colspan=25)
        plt.subplots_adjust(hspace=0.2)

        self._add_pars_box(add_pars)

        return ax1, ax2
    #----------------------------------------
    def _get_component_yield(self, model, par):
        if model.is_extended:
            par  = model.get_yield()
            nevt = float(par.value())
            return nevt

        yild = self.total_model.get_yield()
        if yild is None:
            nevs = self.data_weight_np.sum()
        else:
            nevs = yild.value().numpy()

        frac = par.value().numpy()

        return frac * nevs
    #----------------------------------------
    def _plot_model_components(self, nbins, stacked):
        if not hasattr(self.total_model, 'pdfs'):
            return

        if self._l_blind is not None:
            [blind_name, _, _] = self._l_blind
        else:
            blind_name = None

        y           = None
        l_y         = []
        was_blinded = False
        for model, par in zip(self.total_model.pdfs, self.total_model.params.values()):
            if model.name == blind_name:
                was_blinded = True
                log.debug(f'Skipping blinded PDF: {blind_name}')
                continue

            nevt = self._get_component_yield(model, par)

            if   model.name in self._l_plot_components and     hasattr(model, 'pdfs'):
                l_model = [ (frc, pdf) for pdf, frc in zip(model.pdfs, model.params.values()) ]
            elif model.name in self._l_plot_components and not hasattr(model, 'pdfs'):
                log.warning(f'Cannot plot {model.name} as separate components, despite it was requested')
                l_model = [ (1, model)]
            else:
                l_model = [ (1, model)]

            l_y += self._plot_sub_components(y, nbins, stacked, nevt, l_model)
            y,_  = l_y[-1]

        l_y.reverse()
        ax  = self.axs[0]
        for y, name in l_y:
            if stacked:
                ax.fill_between(self.x, y, alpha=1.0, label=self._leg.get(name, name), color=self._get_col(name))
            else:
                ax.plot(self.x, y, ':',               label=self._leg.get(name, name), color=self._col.get(name))

        if (blind_name is not None) and (was_blinded is False):
            for model in self.total_model.pdfs:
                log.info(model.name)

            raise ValueError(f'Blinding was requested, but PDF {blind_name} was not found among:')
    #----------------------------------------
    def _get_col(self, name):
        if name in self._col:
            return self._col[name]

        col = self._l_def_col[0]
        del self._l_def_col[0]

        return col
    #----------------------------------------
    def _print_data(self) -> None:
        log.info(f'Data shape  : {self.data_np.shape}')
        log.info(f'Weights shape: {self.data_weight_np.shape}')

        nnans = np.sum(np.isnan(self.data_np))
        log.info(f'NaNs: {nnans}')

        # This function will run before program raises
        # One should be able to drop any plot
        plt.close('all')
        plt.hist(self.data_np, weights=self.data_weight_np)
        plt.show()
    #----------------------------------------
    def _evaluate_pdf(self, pdf : zpdf) -> np.ndarray:
        try:
            arr_y = pdf.pdf(self.x)
        except tf.errors.InvalidArgumentError as exc:
            log.info(f'X values: {self.x}')
            self._print_data()
            raise ValueError('Cannot evaluate PDF') from exc

        return arr_y
    #----------------------------------------
    def _plot_sub_components(self, y, nbins, stacked, nevt, l_model):
        l_y = []
        for frc, model in l_model:
            arr_y  = self._evaluate_pdf(pdf = model)
            this_y = arr_y * nevt * frc / nbins * (self.upper - self.lower)

            if stacked:
                y = this_y if y is None else y + this_y
            else:
                y = this_y

            l_y.append((y, model.name))

        return l_y
    #----------------------------------------
    def _plot_model(self, ax, model, nbins=100, linestyle='-'):
        if self._l_blind is not None:
            log.debug(f'Blinding: {model.name}')
            return

        data_yield = self.data_weight_np.sum()
        try:
            arr_y = self._evaluate_pdf(model)
            y     = arr_y * data_yield / nbins * (self.upper - self.lower)
        except tf.errors.InvalidArgumentError as exc:
            log.warning(f'Data yield: {data_yield:.0f}')
            log.info(self.data_np)
            raise RuntimeError('Cannot parse PDF') from exc

        name = model.name
        ax.plot(self.x, y, linestyle, label=self._leg.get(name, name), color=self._col.get(name))
    #----------------------------------------
    def _get_labels(self, xlabel, ylabel, unit, nbins):
        if xlabel == "":
            xlabel = f"{self.obs.obs[0]} [{unit}]"

        if ylabel == "":
            width  = (self.upper-self.lower)/nbins
            ylabel = f'Candidates / ({width:.0f} {unit})'

        return xlabel, ylabel
    #----------------------------------------
    def _get_xcoor(self, plot_range):
        if plot_range is not None:
            try:
                self.lower, self.upper = plot_range
            except TypeError as exc:
                raise TypeError('plot_range argument is expected to be a tuple with two numeric values') from exc

        return np.linspace(self.lower, self.upper, 2000)
    #----------------------------------------
    def _get_data_yield(self, mas_tup):
        if mas_tup is None:
            return self.data_weight_np.sum()

        minx, maxx = mas_tup
        arr_data   = np.array([self.data_np, self.data_weight_np]).T

        arr_data = arr_data[arr_data[:, 0] > minx]
        arr_data = arr_data[arr_data[:, 0] < maxx]

        [_, arr_wgt] = arr_data.T

        return arr_wgt.sum()
    #----------------------------------------
    @gut.timeit
    def plot(self,
        title             = None,
        stacked           = False,
        blind             = None,
        no_data           = False,
        ranges            = None,
        nbins: int        = 100,
        unit: str         = r'$\rm{MeV}/\it{c}^{2}$',
        xlabel: str       = '',
        ylabel: str       = '',
        d_leg : dict|None = None,
        d_col : dict|None = None,
        plot_range: tuple = None,
        plot_components:list[str] = None,
        ext_text : str    = '',
        add_pars          = None,
        ymax              = None,
        skip_pulls        = False,
        pull_styling :bool= True,
        yscale : str      = 'linear',
        axs               = None,
        figsize:tuple     = (13, 7),
        leg_loc:str       = 'best',
        xerr: bool        = False):
        '''
        title (str)           : Title
        stacked (bool)        : If true will stack the PDFs
        ranges                : List of tuples with ranges if any was used for the fit, e.g. [(0, 3), (7, 10)]
        nbins                 : Bin numbers
        unit                  : Unit for x axis, default is MeV/c^2
        no_data (bool)        : If true data won't be plotted as well as pull
        xlabel                : xlabel
        ylabel                : ylabel
        d_leg                 : Customize legend
        d_col                 : Customize color
        plot_range            : Set plot_range
        pull_styling(bool)    : Will add lines at +/-3 and set range to +/-5 for pull plots, by default True
        plot_components (list): List of strings, with names of PDFs, which are expected to be sums of PDFs and whose components should be plotted separately
        ext_text              : Text that can be added to plot
        add_pars (list|str)   : List of names of parameters to be added or string with value 'all' to add all fit parameters. If this is used, plot won't use LHCb style.
        skip_pulls(bool)      : Will not draw pulls if True, default False
        ymax (float)          : Optional, if specified will be used to set the maximum in plot
        blind (list)          : PDF name for the signal if blinding is needed, followed by blinding range, min and max.
        figsize (tuple)       : Tuple with figure size, default (13, 7)
        leg_loc (str)         : Location of legend, default 'best'
        xerr (bool or float)  : Used to pass xerr to mplhep histplot. True will use error with bin size, False, no error, otherwise it's the size of the xerror bar
        yscale (str)          : Scale for y axis of main plot, either log or linear
        '''
        # pylint: disable=too-many-locals, too-many-positional-arguments, too-many-arguments
        d_leg           = {} if           d_leg is None else d_leg
        d_col           = {} if           d_col is None else d_col
        plot_components = [] if plot_components is None else plot_components

        if not hasattr(self.total_model, 'pdfs'):
            #if it's not a sum of PDFs, do not stack
            stacked=False

        self._figsize = figsize
        self._leg_loc = leg_loc

        self._initialize()

        self._l_plot_components = plot_components

        self._leg     = d_leg
        self._col     = d_col
        self.x        = self._get_xcoor(plot_range)
        self.axs      = self._get_axis(add_pars, skip_pulls) if axs is None else axs
        self._l_blind = blind
        total_entries = self._get_data_yield(plot_range)
        self.errors   = self._get_errors(nbins, ranges)
        self.dat_xerr = xerr

        if not stacked:
            log.debug('Plotting full model, for non-stacked case')
            self._plot_model(self.axs[0], self.total_model, nbins)

        log.debug('Plotting model components')
        self._plot_model_components(nbins, stacked)

        if not no_data:
            log.debug('Plotting data')
            self._plot_data(self.axs[0], nbins, ranges)

        if not skip_pulls and not no_data:
            log.debug('Plotting pulls')
            self._plot_pulls(self.axs[1], nbins, total_entries, ranges)

        text           = self._get_text(ext_text)
        xlabel, ylabel = self._get_labels(xlabel, ylabel, unit, nbins)

        self.axs[0].legend(title=text, fontsize=20, title_fontsize=20, loc=self._leg_loc)
        self.axs[0].set(xlabel=xlabel, ylabel=ylabel)
        self.axs[0].set_xlim([self.lower, self.upper])

        if yscale is not None:
            self.axs[0].set_yscale(yscale)

        if title is not None:
            self.axs[0].set_title(title)

        if ymax is not None:
            self.axs[0].set_ylim([0, ymax])

        if not skip_pulls:
            self.axs[1].set(xlabel=xlabel, ylabel="pulls")
            self.axs[1].set_xlim([self.lower, self.upper])

        for ax in self.axs:
            ax.label_outer()

        if pull_styling and not skip_pulls:
            self.axs[1].axhline(y=-3, color='red' , linestyle='-', lw=2)
            self.axs[1].axhline(y= 0, color='gray', linestyle='-', lw=1)
            self.axs[1].axhline(y=+3, color='red' , linestyle='-', lw=2)
            self.axs[1].set_ylim(-5, 5)
#----------------------------------------
