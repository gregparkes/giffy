"""Different linear interpolation techniques based on input."""

from typing import Optional
import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
from scipy.interpolate import interp1d


def lerp_barlike(factor: int, data: pd.DataFrame, lerp_kws: dict):
    """Takes a pandas.DataFrame and interpolates along the rows, returning a new pandas.DataFrame"""
    # barplot
    N = data.shape[0]
    old_x = np.linspace(0, N-1, N)
    new_x = np.linspace(0, N-1, int(N * factor))
    i = np.repeat(data.index.tolist(), factor)
    return pd.DataFrame({
        label: interp1d(old_x, data[label], **lerp_kws)(new_x) for label in data
    }, index=i)


def lerp_pointlike(factor: int, x: ArrayLike, y: ArrayLike, lerp_kws: dict, z: Optional[ArrayLike] = None):
    """Computes linear interpolation on the dataset.
    
    Parameters
    ----------
    factor : int
        Multiplicative factor
    x : ndarray
        A 1d array for the x axis
    y : ndarray
        A 1d array for y
    z : ndarray, optional
        An optional 1d array for z

    Returns
    -------
    new_x, new_y : ndarray 1ds
    or
    new_x, new_y, new_z : ndarray 1ds
        Arrays of new interpolated length.
    """
    # scatter/line plot.
    new_x = np.linspace(x.min(), x.max(), int(x.shape[0] * factor))
    # interpolation method
    if z is not None:
        ylerp = interp1d(x, (y, z), **lerp_kws)
        yn, zn = ylerp(new_x)
        return (new_x, yn, zn)
    else:
        ylerp = interp1d(x, y, **lerp_kws)
        # generate new x, y
        return (new_x, ylerp(new_x))


def lerp_linelike(factor: int, Y: ArrayLike, X: ArrayLike, lerp_kws: dict):
    """Performs line lerping."""
    if X.ndim == 1:
        # if X is 1d, we can simply re-use the interpolation provided by point data, 
        # Y is treated as multiple
        _range, y = lerp_pointlike(factor, X, Y.T, lerp_kws, None)
        return _range, y.T
    else:
        raise NotImplementedError("X being 2d is not implemented.")
