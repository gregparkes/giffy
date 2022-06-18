"""Handles the pie chart cases."""

import itertools as it
from numpy.typing import ArrayLike
import numpy as np
from matplotlib import cm, rcParams
import pandas as pd

from ._basesub import Gif1d
from ._lerp import lerp_barlike
from ._helper import colorwheel, Keywords


class GifPie(Gif1d):
    """A Gif Glyph for animating moving pie charts."""

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        # fill NaNs with 0?
        self.data = self._data = self.data.fillna(0.)
        self._m = self.data.shape[1]
        self._cmap = None
        self._colors = None
        self._annot = False
        self._vmin = 0.
        self._vmax = 1.
        self._labdist = 1.1
        self._width = 1.

        self._defargs = Keywords(labels=self.data.columns.tolist(), colors=None, explode=None, shadow=False)
        self._defargs.set_alias({"c":"colors", "color":"colors"})
        self._allowed1 = {'c','color','colors','labels','shadow'}
        self._wedgeargs = Keywords(linewidth=0, edgecolor='k', width=1.)
    
    def mark(self, **kwargs):
        
        self._set_defargs(kwargs, self._allowed1)

        if "cmap" in kwargs:
            self._cmap = kwargs['cmap']
        if "vmin" in kwargs:
            self._vmin = kwargs['vmin']
        if "vmax" in kwargs:
            self._vmax = kwargs['vmax']
        if "explode" in kwargs:
            self._set_explode(kwargs['explode'])
            self._defargs['explode'] = self._explode
        if "annot" in kwargs:
            self._annot = kwargs['annot']
        if "width" in kwargs:
            self._width = self._wedgeargs['width'] = kwargs['width']
        return self

    def _set_explode(self, e):
        if isinstance(e, str):
            if e in self.data.columns:
                self._explode = np.zeros(self._m)
                self._explode[np.argmax(e == self.data.columns)] = 0.1
            else:
                raise ValueError("property 'explode' as str must be a column name in 'data'")
        else:
            # must be a list of floats the same size as m
            self._explode = e

    def _get_update(self, data):

        def __update(i):
            j = self._curve_f(i)
            # compute normalized thetas.
            norm_x = data.iloc[j] / np.sum(data.iloc[j]) * 360
            perc_x = data.iloc[j] / np.sum(data.iloc[j]) * 100
            # replace nans with 0
            norm_theta = np.hstack((0., np.cumsum(norm_x)))
            # compute the position in radians for each wedge text.
            pos_radian = np.radians(norm_theta[:-1] + (norm_theta[1:] - norm_theta[:-1]) / 2.)
            # iterate over the patches and adjust the theta angle.
            for i, patch in enumerate(self._patches):
                patch.set_theta1(norm_theta[i])
                patch.set_theta2(norm_theta[i+1])
            # update text locations
            for i, text in enumerate(self._texts):
                # set the text to <nothing> if theta1 == theta2. i.e there is no visible wedge
                if perc_x[i] > 1e-4:
                    # calculate new x and y from the normalized x.
                    text.set_x(self._labdist * np.cos(pos_radian[i]))
                    text.set_y(self._labdist * np.sin(pos_radian[i]))
                    text.set_text(data.columns[i])
                else:
                    text.set_text("")
            # if annot is set to true, update these labels also
            if self._annot:
                # compute the annotation magnitude
                mag = (self._width * 0.6) + (1 - self._width)
                # in self._annots
                for i, ann in enumerate(self._annots):
                    # calculate new x and y from the normalized x.
                    if perc_x[i] > 1e-4:
                        ann.set_x(mag * np.cos(pos_radian[i]))
                        ann.set_y(mag * np.sin(pos_radian[i]))
                        if perc_x[i] >= 1.:
                            ann.set_text("{:0.0f}%".format(perc_x[i]))
                        else:
                            ann.set_text("<1%")
                    else:
                        ann.set_text("")

        return __update

    def _lerp_data(self):
        """Overrides base._lerp_data(), set when factor > 1"""
        self._data = lerp_barlike(self._lerp_factor, data=self.data, lerp_kws=self._lerp_kws)

    def _animate(self, time_seconds: float):

        _labels = self._defargs['labels']
        # calculate colours from a color array or cmap.
        if self._cmap is not None:
            self._defargs['colors'] = cm.get_cmap(self._cmap)(
                np.linspace(self._vmin, self._vmax, len(_labels)))
        elif self._defargs['colors'] is None:
            self._defargs['colors'] = list(it.islice(colorwheel(), 0, len(_labels)))

        if self._annot:
            self._defargs['autopct'] = "%.0f%%"
            self._patches, self._texts, self._annots = self.ax.pie(self._data.iloc[0, :],
                                                    **self._defargs,
                                                    wedgeprops=self._wedgeargs)
        else:
            self._patches, self._texts = self.ax.pie(self._data.iloc[0, :],
                                                    **self._defargs,
                                                    wedgeprops=self._wedgeargs)
        return self._get_update(self._data)
