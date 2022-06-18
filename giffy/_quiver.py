"""Handles the quiver cases."""

from numpy.typing import ArrayLike
import numpy as np
from typing import Union
from matplotlib import cm
from matplotlib.colors import Normalize

from ._basesub import Gif2d
from ._helper import assert_condition, get_array_by_3daxis, set_axis_labels


class GifQuiver(Gif2d):
    """A Gif Glyph for animating quiver plots."""

    def __init__(self, U, V, x, y):
        """Initialise the quiver animation.
        
        U, V are 3d matrices with a given time axis. x and y are 1d vectors representing the linspace.
        """
        assert_condition(U.ndim == 3, "`U` must be 3d")
        assert_condition(V.ndim == 3, "`V` must be 3d")
        self.U = U
        self.V = V
        self.X = x
        self.y = y
        self._time_axis = 2
    
    def lerp(self, factor: Union[int,str] = 'auto', kind: str = 'linear'):
        raise NotImplementedError("lerp() not implemented with quiver. Coming in later version.")

    def _get_update(self):
        def __update(i):
            _array_u = get_array_by_3daxis(self.U, self._curve_f(i), self._time_axis)
            _array_v = get_array_by_3daxis(self.V, self._curve_f(i), self._time_axis)
            self.mpl.set_UVC(_array_u, _array_v)
            return (self.mpl,)
        return __update
    
    def _animate(self, time_seconds):
        # override - make a quiver
        U0 = get_array_by_3daxis(self.U, 0, self._time_axis)
        V0 = get_array_by_3daxis(self.V, 0, self._time_axis)
        # make initial quiver
        self.mpl = self.ax.quiver(self.X, self.y, U0, V0, scale=50)
        set_axis_labels(self.ax, self._xval, self._yval)
        # now return the update method
        return self._get_update()
