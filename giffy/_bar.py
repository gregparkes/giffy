"""Handles the 1D bar case."""


from multiprocessing.sharedctypes import Value
from typing import List
import itertools as it
import numpy as np
import pandas as pd
from matplotlib import cm

from ._basesub import Gif1d
from ._helper import get_time_curve, colorwheel, set_named_variable, Keywords
from ._lerp import lerp_barlike


def get_bar_update(bar_obj, title: str, data: pd.DataFrame, curve_f, orient: str = 'vert'):
    def __update(i):
        j = curve_f(i)
        title.set_text(data.index[j])
        for bar, value in zip(bar_obj, data.iloc[j]):
            bar.set_height(value) if orient == 'vert' else bar.set_width(value)
    return __update


def get_multibar_update(bars_obj, title: str, datas: List[pd.DataFrame], curve_f, orient: str = 'vert'):
    def __update(i):
        j = curve_f(i)
        title.set_text(datas[0].index[j])
        for bar_obj, data in zip(bars_obj, datas):
            for bar, value in zip(bar_obj, data.iloc[j]):
                bar.set_height(
                    value) if orient == 'vert' else bar.set_width(value)
    return __update


###########################################################################################################

class _GifBarBase(Gif1d):
    """Abstract base class for 1d bar charts."""

    def __init__(self, data: pd.DataFrame):
        # short or long form.
        super().__init__(data)
        self._data = self.data = data
        self._orient = "vert"
        self._orients = {'vert', 'horz'}
        self._thick = .8
        self._cmap = None

        # define some keyword arguments
        self._defargs = Keywords(
            color='b', linewidth=0, edgecolor='b', fill=True, hatch=None, alpha=1
        )
        self._defargs.set_alias(
            {"c": "color", "ec": "edgecolor", "lw": "linewidth", 'a':'alpha'})
        self._allowed = {'color', 'c', 'alpha', 'a', 'fill',
                         'ec', 'edgecolor', 'lw', 'linewidth', 'hatch', 'width', 'height'}

    def _set_thickness(self, thick):
        if thick < 0 or thick > 1:
            raise ValueError("'thick' must be in range [0, 1]")
        self._thick = thick

    def _set_cmap(self, cmap):
        if not isinstance(cmap, str):
            raise TypeError("'cmap' must be of type str")
        self._cmap = cmap

    def mark(self, **kwargs):
        """A function for marking the plot appropriately using lots of options.

        Valid options are ['orient', 'color'|'c', 'cmap', 'lw', 'ec', 'thick']
        """
        self._set_defargs(kwargs, self._allowed)

        if "orient" in kwargs and kwargs['orient'] in self._orients:
            # orient = 'vert'|'horz'
            self._orient = kwargs['orient']
        if 'cmap' in kwargs:
            self._set_cmap(kwargs['cmap'])
        if "thick" in kwargs:
            self._set_thickness(kwargs['thick'])
        return self


############################################ SHORT BAR #############################################################

class GifBarShort1D(_GifBarBase):
    """A Gif Glyph for animating bar charts.

    This object is used when long_form is False and the data is compact in short form.

    Gif1d is a declarative object where properties are declared and only on 'plot()' are values computed and
    executed.
    """

    def _lerp_data(self):
        self._data = lerp_barlike(self._lerp_factor, data=self.data,
                                  lerp_kws=self._lerp_kws)

    def _animate(self, time_seconds):
        # if a colormap is present, overwrite the colours parameter.
        if self._cmap is not None:
            # override colours
            self._defargs['color'] = cm.get_cmap(self._cmap)(
                np.linspace(0, 1, self.data.shape[1]))

        # set defargs width/height based on condition
        #self._defargs.set_cond_key(self._orient == "vert", "width", "height", self._thick)

        if self._orient == 'vert':
            plot_f = self.ax.bar
            self._defargs['width'] = self._thick
            self._defargs.remove("height")
            self.ax.set_ylim(np.nanmin(self._data.values),
                             np.nanmax(self._data.values))
        else:
            plot_f = self.ax.barh
            self._defargs['height'] = self._thick
            self._defargs.remove("width")
            self.ax.set_xlim(np.nanmin(self._data.values),
                             np.nanmax(self._data.values))
        # compute
        self.mpl = plot_f(self._data.columns.tolist(),
                          self._data.iloc[0, :], **self._defargs)
        # add text for index.
        self.ttl = self.ax.text(.5, 1.005, '', transform=self.ax.transAxes)
        return get_bar_update(self.mpl, self.ttl, self._data, self._curve_f, self._orient)


########################################### LONG BAR ###############################################################

class GifBarLong1D(_GifBarBase):
    """A Gif Glyph for animating bar charts.

    This object is used when long_form is True and the data is in long form.
    """

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self._totaln = data.shape[0]
        self._thick = .7
        self._hue = ""

    def mark(self, **kwargs):
        """Valid extended markers are ['x','y','hue']"""
        super().mark(**kwargs)
        if "x" in kwargs:
            self._xval = set_named_variable(kwargs['x'], self.data)
        if "y" in kwargs:
            self._yval = set_named_variable(kwargs['y'], self.data)
        if "hue" in kwargs:
            self._hue = kwargs['hue']
        return self

    def _animate(self, time_seconds):
        # fetch the number of uniques in x
        if self._xval == "":
            raise ValueError("`x` property must be specified prior to plot.")
        if self._yval == "":
            raise ValueError("`y` property must be specified prior to plot")

        x_unique = self.data[self._xval].unique()
        nx = x_unique.shape[0]
        x_positions = np.arange(nx)
        # handle non-hue case
        if self._hue == "":
            self.n_frames = margin = self._totaln // nx
        else:
            hues = self.data[self._hue].unique()
            hn = hues.shape[0]
            self.n_frames = margin = self._totaln // (nx * hn)

        if self._orient == 'vert':
            plot_f = self.ax.bar
            self.ax.set_xlabel(self._xval)
            self.ax.set_ylabel(self._yval)
            self.ax.set_xticks(x_positions, x_unique)
            self.ax.set_ylim(self.data[self._yval].min(),
                             self.data[self._yval].max())
        else:
            plot_f = self.ax.barh
            self.ax.set_ylabel(self._xval)
            self.ax.set_xlabel(self._yval)
            self.ax.set_yticks(x_positions, x_unique)
            self.ax.set_xlim(self.data[self._yval].min(),
                             self.data[self._yval].max())

        
        # add text for index.
        self.ttl = self.ax.text(.5, 1.005, '', transform=self.ax.transAxes)

        # the number of time steps is the total divided by number of uniques.
        self.interval = (time_seconds*1000) // self.n_frames
        curve_f = get_time_curve(self._curve, self.n_frames)

        if self._hue == "":
            # reshape the data
            # if a colormap is present, overwrite the colours parameter.
            if self._cmap is not None:
                # override colours
                self._defargs['color'] = cm.get_cmap(self._cmap)(np.linspace(0, 1, nx))
            else:
                self._defargs['color'] = self._base_color

            piv = self.data.assign(t=np.repeat(np.arange(self.n_frames), nx)).pivot(
                index='t', columns=self._xval, values=self._yval)
            # optional lerp
            if self._lerp_factor > 1:
                data = lerp_barlike(self._lerp_factor, data=piv,
                                    lerp_kws=self._lerp_kws)
                self.n_frames = data.shape[0]
                self.interval = (time_seconds*1000) // self.n_frames
                curve_f = get_time_curve(self._curve, self.n_frames)
            else:
                data = piv

            mpl = plot_f(x_unique, data.iloc[0, :],
                         self._thick, **self._defargs)
            animf = get_bar_update(mpl, self.ttl, data, curve_f, self._orient)
        else:
            datas, mpls = [], []
            prop_bar_size = self._thick / hn
            self._defargs.remove("color")

            if self._cmap is not None:
                # use the colormap
                colors = cm.get_cmap(self._cmap)(np.linspace(0, 1, hn))
            else:
                colors = list(it.islice(colorwheel(), 0, hn))

            # iterate through the hues and add them to the list.
            for i, (name, group) in enumerate(self.data.groupby(self._hue)):
                # add time to this group.
                group['t'] = np.repeat(np.arange(margin), nx)
                transformed_group = group.pivot(
                    index='t', columns=self._xval, values=self._yval)
                # lerp data if possible
                if self._lerp_factor > 1:
                    data = lerp_barlike(self._lerp_factor, data=transformed_group,
                                        lerp_kws=self._lerp_kws)
                    self.n_frames = data.shape[0]
                    self.interval = (time_seconds*1000) // self.n_frames
                    curve_f = get_time_curve(self._curve, self.n_frames)
                else:
                    data = transformed_group

                # make a plot
                mpl = plot_f(x_positions + (prop_bar_size*i) - (prop_bar_size/2)*(hn-1),
                             data.iloc[0, :],
                             prop_bar_size, color=colors[i], label=name, **self._defargs)
                datas.append(data)
                mpls.append(mpl)
            
            if self._has_legend:
                self.ax.legend(loc='lower left', title=self._hue)
            animf = get_multibar_update(
                mpls, self.ttl, datas, curve_f, self._orient)

        return animf
