"""Handles the scatter plot cases."""

from typing import Optional
from numpy.typing import ArrayLike
import numpy as np
from matplotlib import cm, rcParams
from matplotlib.colors import Normalize

from ._basesub import Gif2d
from ._helper import set_color_dataframe, set_axis_labels, assert_condition
from ._lerp import lerp_linelike


class GifScatter(Gif2d):
    """A Gif Glyph for animating moving scatterplots."""

    def __init__(self,
                 X: ArrayLike,
                 Y: ArrayLike,
                 Z: Optional[ArrayLike] = None,
                 C: Optional[ArrayLike] = None,
                 S: Optional[ArrayLike] = None):
        """Initialise the 2d scatter animation"""
        super().__init__(X)

        assert_condition(X.ndim == 2, "`X` must be a 2D numpy array")
        assert_condition(Y.ndim == 2, "`Y` must be a 2D numpy array")
        assert_condition(X.shape == Y.shape,  "`X` and `Y` must have the same shape")
        # size checks
        self.Y = Y
        # handle Z dimension
        if Z is not None:
            assert_condition(Z.ndim == 2, "`Z` must be a 2D numpy array")
            assert_condition(X.shape == Z.shape,  "`X` and `Z` must have the same shape")
            self.Z = Z
            self.d3 = True
        else:
            self.Z = None

        # handle colours
        if C is not None:
            if C.ndim == 1:
                assert_condition(C.shape[0] == X.shape[1], "1D color must be same length as X")
            else:
                assert_condition(C.ndim == 2, "`C` must be a 2D numpy array")
                assert_condition(X.shape == C.shape, "`X` and 2D `C` must have the same shape")
            self.C = C
            # set the colormap object
            self._set_cmap("viridis")
        else:
            self.C = None
        
        # handle sizes
        if S is not None:
            if S.ndim == 1:
                assert_condition(S.shape[0] == X.shape[1], "1D size must be same length as X")
            else:
                assert_condition(S.ndim == 2, "`S` must be a 2D numpy array")
                assert_condition(X.shape == S.shape, "2D size must be same shape as X and Y") 
            self.S = S
        else:
            self.S = None

        # other attributes
        self._marker = "o"
        self._alpha = 1.
        self._zval = ""
        self._s = rcParams['lines.markersize'] ** 2
        self._edgecolor = 'face'

    def mark(self, **kwargs):
        """A function for marking the plot appropriately using lots of options.

        Valid options are ['marker'|'m', 'color'|'c', 'x', 'y', 'z', 'alpha'|'a', 'cmap', 's', 'ec']

        's' is the size factor, when S array is passed, 's' becomes the multiplicative scaling factor.
        """
        # call super to provide x, y, cmap
        super().mark(**kwargs)
        # additional args
        if "marker" in kwargs:
            self._marker = kwargs['marker']
        elif "m" in kwargs:
            self._marker = kwargs['m']
        if "color" in kwargs:
            self._cval = kwargs['color']
            self._base_color = set_color_dataframe(
                kwargs['color'], self.X.shape[1])
        elif "c" in kwargs:
            self._cval = kwargs['c']
            self._base_color = set_color_dataframe(
                kwargs['c'], self.X.shape[1])
        if "z" in kwargs:
            self._zval = kwargs['z']
        if "s" in kwargs:
            self._s = kwargs['s']
        if "ec" in kwargs:
            self._edgecolor = kwargs['ec']
        return self

    def _get_update(self, X, Y, Z, C, S):
        def __update(i):
            j = self._curve_f(i)
            if Z is not None:
                self.mpl._offsets3d = (X[j, :], Y[j, :], Z[j, :])
            else:
                self.mpl.set_offsets(np.c_[X[j, :], Y[j, :]])
            if C is not None:
                self.mpl.set_facecolor(self._cmobj(C[j, :]))
            if S is not None:
                self.mpl.set_sizes(S[j, :])
            return (self.mpl,)
        return __update

    def _animate(self, time_seconds):
        args = dict(marker=self._marker, label='trace1',
                    alpha=self._alpha, edgecolors=self._edgecolor)
        # lerp data - basically the same as line data but for our scattered points.
        if self.C is None:
            args['c'] = self._base_color
            _c = None
        else:
            args['cmap'] = self._cmap
            if self.C.ndim == 1:
                args['c'] = self.C
                _c = None
            else:
                args['c'] = self._cmobj(self.C[0, :])
                _c = self.C

        if self.S is None:
            args['s'] = self._s
            _s = None
        else:
            if self.S.ndim == 1:
                args['s'] = self.S * self._s
                _s = None
            else:
                args['s'] = self.S[0, :] * self._s
                _s = self.S * self._s

        if self._lerp_factor > 1:
            r = np.arange(self.X.shape[0])
            _, x = lerp_linelike(
                self._lerp_factor, self.X, r, lerp_kws=self._lerp_kws)
            _, y = lerp_linelike(
                self._lerp_factor, self.Y, r, lerp_kws=self._lerp_kws)
            if self.Z is not None:
                _, z = lerp_linelike(
                    self._lerp_factor, self.Z, r, lerp_kws=self._lerp_kws)
            else:
                z = self.Z
            if _c is not None:
                _, _c = lerp_linelike(
                    self._lerp_factor, _c, r, lerp_kws=self._lerp_kws)
            if _s is not None:
                _, _s = lerp_linelike(
                    self._lerp_factor, _s, r, lerp_kws=self._lerp_kws)
        else:
            x, y, z = self.X, self.Y, self.Z

        # set axis limits
        self.ax.set_xlim(np.nanmin(x), np.nanmax(x))
        self.ax.set_ylim(np.nanmin(y), np.nanmax(y))
        # now handle first plot
        if z is not None:
            self.ax.set_zlim(np.nanmin(z), np.nanmax(z))
            self.mpl = self.ax.scatter(x[0, :], y[0, :], z[0, :], **args)
        else:
            self.mpl = self.ax.scatter(x[0, :], y[0, :], **args)

        if (self.C is not None) and self._has_colorbar:
            _map = cm.ScalarMappable(
                Normalize(self.C.min(), self.C.max()), cmap=self._cmap)
            self.fig.colorbar(_map, label=self._cval)

        set_axis_labels(self.ax, self._xval, self._yval, self._zval)
        return self._get_update(x, y, z, _c, _s)
