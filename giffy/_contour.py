"""Handles the contour cases."""

from numpy.typing import ArrayLike
import numpy as np
from typing import Union
from matplotlib import cm
from matplotlib.colors import Normalize

from ._basesub import Gif2d
from ._helper import set_axis_labels, get_array_by_3daxis, Keywords, assert_condition


class GifContour(Gif2d):
    """A Gif Glyph for animating contours."""

    def __init__(self, Z: ArrayLike, X: ArrayLike, Y: ArrayLike):
        """Initialize the contour animation

        Z is a 3d matrix with the first dimension being time.
        """
        super().__init__(Z)

        assert_condition(self.X.ndim == 3, "`Z` must be 3D numpy array")
        self._time_axis = 0
        # check X or Y is populated
        if X is not None and Y is not None:
            # if X is a tuple, make a range using C data
            assert_condition(X.ndim == 1, "`X` must be 1D numpy array")
            assert_condition(Y.ndim == 1, "`Y` must be 1D numpy array")
            self._xbound = X
            self._ybound = Y
        else:
            self._xbound = None
            self._ybound = None
        # calculate the minimum and maximum of Z
        self._defargs = Keywords(vmin=np.nanmin(self.X), vmax=np.nanmax(self.X),
                                 levels=5, linewidths=1, linestyles="solid", cmap="viridis",
                                  alpha=1)
        self._defargs.set_alias({"ls":"linestyles", "lw":"linewidths"})
        self._allowed = {'vmin',"vmax","levels","lw","linewidth","ls","linestyle","cmap","alpha"}

    def lerp(self, factor: Union[int,str] = 'auto', kind: str = 'linear'):
        raise NotImplementedError(
            "lerp() not implemented with contour. Coming in later version.")

    def mark(self, **kwargs):
        """A function for marking the plot appropriately using lots of options.

        Valid options are ['x','y','cmap','c'|'color', 'vmin','vmax','alpha'|'a','time']
        """
        super().mark(**kwargs)
        self._set_defargs(kwargs, self._allowed)

        if "time" in kwargs:
            _arg = kwargs['time']
            assert_condition(0 <= _arg <= 2, "time must be in the range [0..2]")
            self._time_axis = _arg
            self.n_frames = self.X.shape[_arg]
        if "c" in kwargs:
            self._cval = kwargs['c']
        elif "color" in kwargs:
            self._cval = kwargs['color']
        return self

    def _get_update(self, preargs, kwargs):
        def __update(i):
            _array = get_array_by_3daxis(
                self.X, self._curve_f(i), self._time_axis)
            # reset the ax collections object.
            self.ax.collections.clear()
            # re-draw
            self.ax.contour(*preargs, _array, **kwargs)
        return __update

    def _animate(self, time_seconds: float):
        Z0 = get_array_by_3daxis(self.X, 0, self._time_axis)
        if self._xbound is not None and self._ybound is not None:
            preargs = (self._xbound, self._ybound)
        else:
            preargs = ()

        self.mpl = self.ax.contour(*preargs, Z0, **self._defargs)
        # make a colorbar
        if self._has_colorbar:
            _cm = cm.ScalarMappable(
                Normalize(self._defargs['vmin'], self._defargs['vmax']), cmap=self._defargs['cmap'])
            self.fig.colorbar(_cm, label=self._cval)

        # animate
        set_axis_labels(self.ax, self._xval, self._yval)
        return self._get_update(preargs, self._defargs)
