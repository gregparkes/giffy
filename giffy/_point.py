"""Handles the 1D line case."""

from typing import Optional, Union
import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
from functools import partial

from ._basesub import Gif1d
from ._helper import set_axis_labels, format_datetime_xticks, \
     set_named_variable, set_color_dataframe
from ._lerp import lerp_pointlike


def _get_point_array(name: str, x: ArrayLike, j: int):
    if name == 'point':
        return x[j]
    elif name == "point_r":
        return x[-j-1]
    elif name == "lines" or name == "steps":
        return x[:j]
    else:
        return x[-j-1:]


class GifPoint(Gif1d):
    """A Gif Glyph for animating points.

    Gif1d is a declarative object where properties are declared and only on 'plot()' are values computed and
    executed.
    """

    def __init__(self, data: pd.DataFrame):
        """Initialise a growing 1d point/line animation."""
        super().__init__(data)
        # one of ['point', 'grow', 'shrink']
        self._style = "lines"
        self._styles = {'lines', 'lines_r', 'point', 'point_r', 'steps', 'steps_r'}
        self._stephows = {'pre', 'mid', 'post'}
        self._step_where = "pre"
        # one of the matplotlib markers.
        self._marker = ''
        self._ls = "-"
        self._lw = 1
        # by default set x to the index
        self._zval = ""
        self._cval = ""
        self._alpha = 1.
        # hold traces.
        self.traces = []

    ####################### METHODS BEGIN #####################################################

    def mark(self, **kwargs):
        """A function for marking the plot appropriately using lots of options.

        Valid options are ['marker', 'color'|'c', 'style', 'x', 'lw', 'ls', 'alpha'|'a']
        """
        if "marker" in kwargs:
            self._marker = kwargs['marker']
        if "color" in kwargs:
            self._base_color = set_color_dataframe(kwargs['color'], self.data.shape[1])
        elif "c" in kwargs:
            self._base_color = set_color_dataframe(kwargs['c'], self.data.shape[1])
        if "style" in kwargs and kwargs['style'] in self._styles:
            self._style = kwargs['style']
        if "lw" in kwargs:
            self._lw = kwargs['lw']
        if "ls" in kwargs:
            self._ls = kwargs['ls']
        if "x" in kwargs:
            self._xval = set_named_variable(kwargs['x'], self.data)
        if "a" in kwargs:
            # alpha
            self._alpha = kwargs['a']
        elif "alpha" in kwargs:
            self._alpha = kwargs['alpha']
        if "stephow" in kwargs and kwargs['stephow'] in self._stephows:
            self._step_where = kwargs['stephow']
        return self

    def trace(self, y: Union[int,str],
              x: Optional[Union[int,str]] = None,
              z: Optional[Union[int,str]] = None,
              c: Optional[str] = None,
              m: Optional[str] = None,
              ls: Optional[str] = None):
        """Adds a trace.
        
        Parameters
        ----------
        y : int or str
            The index or name of the column on the y axis.
        x : int or str, optional
            The index or name of the column on the x axis.
        z : int or str, optional
            The index or name of the column on the z axis (3d).
        c : str, optional
            The colour name.
        m : str, optional
            The marker type
        ls : str, optional
            The linestyle type
        """
        # convert int to str
        _y = set_named_variable(y, self.data)
        _x = set_named_variable(x, self.data) if x is not None else self._xval
        
        if z is not None:
            _z = set_named_variable(z, self.data)
            self.d3 = True
        else:
            _z = self._zval

        self.traces.append({
            'y': _y,
            'x': _x,
            'z': _z,
            'c': c if c is not None else self._base_color,
            'm': m if m is not None else self._marker,
            'ls': ls if ls is not None else self._ls
        })
        return self

    def _get_update(self):
        def __update(i):
            j = self._curve_f(i)
            for item in self.anim:
                _x = _get_point_array(self._style, item['x'], j)
                _y = _get_point_array(self._style, item['y'], j)
                item['obj'].set_data((_x, _y))
                if "z" in item:
                    item['obj'].set_3d_properties(_get_point_array(self._style, item['z'], j))
                
            return [item['obj'] for item in self.anim]
        return __update

    def _animate(self, time_seconds: float):
        """Overrides base.animate_func."""

        # go through the traces and add animations for them.
        if len(self.traces) == 0:
            # no traces.
            raise ValueError("No traces to plot. Please call trace() to add plots.")
        self.anim = []

        # get ax drawing function
        if self._style in ['steps', 'steps_r']:
            plotting_f = partial(self.ax.step, where=self._step_where)
        else:
            plotting_f = self.ax.plot

        # iterate over all traces and plot data.
        for trace in self.traces:
            # check which of x, y, z, c is selected
            marker_value = f"{trace['m']}{trace['ls']}"
            # compute if x is a marker or data.
            if trace['x'] == '':
                x = self.data.index
            else:
                x = self.data[trace['x']].copy()

            if trace['z'] == '':
                z = None
            else:
                z = self.data[trace['z']].copy()

            y = self.data[trace['y']].copy()

            if self._lerp_factor > 1:
                if z is not None:
                    x, y, z = lerp_pointlike(self._lerp_factor, x=x, y=y, z=z, lerp_kws=self._lerp_kws)
                else:
                    x, y = lerp_pointlike(self._lerp_factor, x=x, y=y, lerp_kws=self._lerp_kws)
                self.n_frames = y.shape[0]

            # define static args.
            args = dict(color=trace['c'], label=trace['y'], lw=self._lw, alpha=self._alpha)

            # calculate 3d data.
            if z is not None:
                self.mpl, = plotting_f(x, y, z, marker_value, **args)
                # create an animate_package for line
                self.anim.append({
                    "obj": self.mpl, 'x': x, 'y': y, 'z': z
                })
            else:
                # just 2d, plot
                self.mpl, = plotting_f(x, y, marker_value, **args)
                # create an animate_package for line
                self.anim.append({
                    "obj": self.mpl, 'x': x, 'y': y
                })
        
        if len(self.traces) == 1:
            # add y label to the axis label
            self._yval = self.traces[0]['y']
        elif self._has_legend:
            self.ax.legend(loc='upper right')
        
        animf = self._get_update()
        # do extra stuff
        set_axis_labels(self.ax, self._xval, self._yval, self._zval)
        # if x is a datetime object, we'll format the xticks
        if "datetime" in x.dtype.name:
            format_datetime_xticks(self.ax, "%m-%d")
            self._xval = "Date"

        return animf
    