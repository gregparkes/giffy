"""Methods for various abstract subclasses to base."""

import numpy as np
import pandas as pd
from matplotlib import cm
from numpy.typing import ArrayLike

from ._base import GifBase
from ._helper import assert_condition


class Gif1d(GifBase):
    """Another abstract class for defining 1d drawing vectors."""

    def __init__(self, data: pd.DataFrame):
        super().__init__(data.shape[0])
        # check to make sure data is a pandas.dataframe
        if not isinstance(data, pd.DataFrame):
            raise TypeError("`data` must be a pandas.DataFrame")
        self.data = data

class Gif2d(GifBase):
    """Another abstract class for defining 2d drawing vectors."""
    def __init__(self, X: ArrayLike):
        # time is always the first dimension.
        super().__init__(X.shape[0])
        
        assert_condition(isinstance(X, np.ndarray), "data must be a numpy.ndarray", TypeError)
        self.X = X
        # use default cmap
        self._cmap = "viridis"
        self._cmobj = cm.get_cmap("viridis").copy()
        self._cm_nan_color = "gray"
        self._cmobj.set_bad(self._cm_nan_color, alpha=.7)
        # name for cmap
        self._cval = ""
    
    def _set_cmap(self, c: str):
        """Sets the colormap and creates an instance of it."""
        self._cmap = c
        # make the object
        self._cmobj = cm.get_cmap(self._cmap).copy()
        # set the 'missing value' color to something.
        self._cmobj.set_bad(self._cm_nan_color, alpha=.7)

    def mark(self, **kwargs):
        """Basic mark behavior for 2d plots.
        
        Attributes provided: ['x', 'y', 'cmap', 'a'|'alpha']
        """
        if "x" in kwargs:
            self._xval = kwargs['x']
        if "y" in kwargs:
            self._yval = kwargs['y']
        if "cmap" in kwargs:
            self._set_cmap(kwargs['cmap'])
        return self
