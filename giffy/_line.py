"""Handles the 1D line movement case."""

from typing import Optional
from numpy.typing import ArrayLike
import numpy as np

from ._base import GifBase
from ._helper import set_axis_labels, Keywords, assert_condition
from ._lerp import lerp_linelike


class GifLine1D(GifBase):
    """A Gif Glyph for animating moving lines."""

    def __init__(self, Y: ArrayLike, X: Optional[ArrayLike]):
        """Initialise a moving 1d line animation."""
        super().__init__(Y.shape[0])
        # if X is None, make a range, if X is 1d, make y_data move,
        # if X is 2D, move both X and Y

        assert_condition(Y.ndim == 2, "`Y` must be a 2D numpy array")
        self.Y = self._y = Y
        if X is None:
            # X ranges on the non-time axis.
            self.X = self._x = np.arange(Y.shape[1])
        else:
            assert_condition(X.ndim <= 2, "`X` must be a 1D or 2D numpy array")
            if X.ndim == 1:
                assert_condition(X.shape[0] == Y.shape[1], "1d X must be same length as Y non-time")
            else:
                assert_condition(X.shape == Y.shape, "X 2d shape must be same shape as Y")
            self.X = self._x = X
        # other variables.
        self._defargs = Keywords(lw=1, marker="", linestyle="-", color='b',
                                 label=self._yval, alpha=1)
        # alias that maps abbreviations to long form.
        self._defargs.set_alias(
            {"m": "marker", "c": "color", "a": "alpha", "ls": "linestyle", "y":"label"})
        self._allowed = {"lw","marker","m","color","c","linestyle","ls","label","y","alpha","a"}

    def mark(self, **kwargs):
        """A function for marking the plot appropriately using lots of options.

        Valid options are ['marker', 'color'|'c', 'x', 'y', 'lw', 'ls', 'alpha'|'a']
        """
        self._set_defargs(kwargs, self._allowed)

        if "x" in kwargs:
            self._xval = kwargs['x']
        if "y" in kwargs:
            self._yval = self._defargs['y'] = kwargs['y']
        return self

    def _get_update(self, y, x):
        def __update_1d(i):
            j = self._curve_f(i)
            self.mpl.set_ydata(y[j, :])
            return (self.mpl,)

        def __update_2d(i):
            j = self._curve_f(i)
            self.mpl.set_data((x[j, :], y[j, :]))
            return (self.mpl,)

        if x.ndim > 1:
            return __update_2d
        else:
            return __update_1d

    def _lerp_data(self):
        """Overrides base._lerp_data(). Only called if lerp factor > 1"""
        _, self._y = lerp_linelike(self._lerp_factor, self.Y,
                                   np.arange(self.Y.shape[0]), lerp_kws=self._lerp_kws)
        if self.X.ndim > 1:
            _, self._x = lerp_linelike(self._lerp_factor, self.X,
                                       np.arange(self.X.shape[0]), lerp_kws=self._lerp_kws)

    def _animate(self, time_seconds: float):
        """Overrides base._animate_func"""
        
        #marker_value = f"{self._defargs['marker']}{self._defargs['linestyle']}"
        # set the ylim
        self.ax.set_ylim(self._y.min(), self._y.max())

        if self.X.ndim == 1:
            self.mpl, = self.ax.plot(
                self.X, self._y[0, :], **self._defargs)
            animf = self._get_update(self._y, self.X)
        else:
            self.ax.set_xlim(self._x.min(), self._x.max())
            self.mpl, = self.ax.plot(
                self._x[0, :], self._y[0, :], **self._defargs)
            animf = self._get_update(self._y, self._x)

        # generate the animation
        set_axis_labels(self.ax, self._xval, self._yval)
        return animf
