"""Handles the color mesh cases."""

from numpy.typing import ArrayLike
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize

from ._basesub import Gif2d
from ._helper import set_axis_labels, get_array_by_3daxis, Keywords, assert_condition


class GifColorMesh(Gif2d):
    """A Gif Glyph for animating color meshes."""

    def __init__(self, C: ArrayLike, X: ArrayLike, Y: ArrayLike):
        """Initialise the colormesh animation.

        C is a 3d matrix with the first dimension being time.
        """
        super().__init__(C)

        assert_condition(self.X.ndim == 3, "`C` must be a 3D numpy array." )
        # check X or Y is populated
        if X is not None and Y is not None:
            # if X is a tuple, make a range using C data
            assert_condition(X.ndim == 1, "`X` must be a 1D numpy array." )
            assert_condition(Y.ndim == 1, "`Y` must be a 1D numpy array." )
            self._xbound = X
            self._ybound = Y
        else:
            self._xbound = None
            self._ybound = None

        self._time_axis = 0
        # other parameters
        self._shadings = {'flat', 'nearest', 'gouraud', 'auto'}
        self._shade = "auto"
        # calculate the minimum and maximum of C
        self._defargs = Keywords(vmin=np.nanmin(self.X), vmax=np.nanmax(self.X),
                            edgecolors=None, alpha=1, cmap=self._cmap)
        self._defargs.set_alias({"a":"alpha", "ec":"edgecolors"})
        self._allowed = {'a', "alpha", "vmin", "vmax", "ec", "edgecolors", "cmap"}

    def lerp(self, factor: int | str = 'auto', kind: str = 'linear'):
        raise NotImplementedError("lerp() not implemented with colormesh. Coming in later version.")

    def mark(self, **kwargs):
        """A function for marking the plot appropriately using lots of options.

        Valid options are ['x','y','cmap','c'|'color', 'vmin','vmax','alpha'|'a','ec','shade','time']
        """
        # call to super
        super().mark(**kwargs)
        self._set_defargs(kwargs, self._allowed)

        if "c" in kwargs:
            self._cval = kwargs['c']
        elif "color" in kwargs:
            self._cval = kwargs['color']
        if "shade" in kwargs and kwargs['shade'] in self._shadings:
            self._shade = kwargs['shade']
        if "time" in kwargs:
            _arg = kwargs['time']
            self._time_axis = _arg
            self.n_frames = self.X.shape[_arg]
        return self

    def _get_update(self):
        def __update(i):
            _array = get_array_by_3daxis(self.X, self._curve_f(i), self._time_axis)
            self.mpl.set_array(_array.flatten())
            return (self.mpl,)
        
        return __update

    def _animate(self, time_seconds):
        # make colormesh
        C0 = get_array_by_3daxis(self.X, 0, self._time_axis)
        # add x an y args if present
        if self._xbound is not None and self._ybound is not None:
            _local = (self._xbound, self._ybound, C0)
        else:
            _local = (C0,)
        
        self.mpl = self.ax.pcolormesh(*_local, **self._defargs)
        # make a colorbar
        if self._has_colorbar:
            _cm = cm.ScalarMappable(
                Normalize(self._defargs['vmin'], self._defargs['vmax']), cmap=self._defargs['cmap'])
            self.fig.colorbar(_cm, label=self._cval)
        # animate
        set_axis_labels(self.ax, self._xval, self._yval)
        return self._get_update()
