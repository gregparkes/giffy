"""Main script for glyph gifs."""

from typing import Optional
from numpy.typing import ArrayLike
import pandas as pd

from ._point import GifPoint
from ._bar import GifBarShort1D, GifBarLong1D
from ._pie import GifPie
from ._line import GifLine1D
from ._scatter import GifScatter
from ._colormesh import GifColorMesh
from ._contour import GifContour
from ._quiver import GifQuiver


def Point(data: pd.DataFrame):
    """Generates a Giffy Point chart to manipulate.

    Parameters
    ----------
    data : pandas.DataFrame
        Rows represent time (animating dimension), 
        columns are the different datasets to animate.

    Returns
    -------
    g : GifPoint object
        Our custom object for handling point aniamtions.
    """
    return GifPoint(data)


def Bar(data: pd.DataFrame, long: bool = False):
    """Generates a Giffy Bar chart to manipulate.

    Parameters
    ----------
    data : pandas.DataFrame
        Rows represent time (animating dimension), 
        columns are the category axis.
    long : bool, default=False
        Whether the dataframe is in long or short format. If `data` is in long form
        a pivot is performed prior to animation.

    Returns
    -------
    g : GifBarShort1D or GifBarLong1D
        Based on `long`, a custom object for handling barplot animations.
    """
    if not long:
        return GifBarShort1D(data)
    else:
        # use a different object if in long form - allow for colors/hue etc.
        return GifBarLong1D(data)


def Pie(data: pd.DataFrame):
    """Generates a Giffy Pie chart to manipulate.

    Parameters
    ----------
    data : pandas.DataFrame
        Rows represent time (animating dimension), 
        columns are the category axis.

    Returns
    -------
    g : GifPie
        Our custom object for handling piechart aniamtions.
    """
    return GifPie(data)


def Line(Y: ArrayLike, X: Optional[ArrayLike] = None):
    """Generates a Giffy Line chart to manipulate.

    Parameters
    ----------
    Y : ndarray 2d (time, y)
        data to plot on the y axis (axis=0 is time.)
    X : ndarray, optional
        if 1d, must align to y axis of Y. if 2d must be same shape as Y.

    Returns
    -------
    g : GifLine1D
        Our custom object for handling line animations.
    """
    return GifLine1D(Y, X)


def Scatter(X: ArrayLike,
            Y: ArrayLike,
            Z: Optional[ArrayLike] = None,
            C: Optional[ArrayLike] = None,
            S: Optional[ArrayLike] = None):
    """Generates a Giffy Scatter chart to manipulate.

    Parameters
    ----------
    X : ndarray 2d (time, x)
        data to plot on the x axis (axis=0 is time.)
    Y : ndarray 2d (time, y)
        data to plot on the y axis (axis=0 is time.)
    Z : ndarray, optional
        3d dimensional data, If provided, must be same shape and format as X and Y
    C : ndarray, optional
        colour data associated with the points.
        if 1d, must be the same length as X non-time axis
        if 2d, must be same shape and format as X and Y
    S : ndarray, optional
        size data associated with the size of each point
        if 1d, must be the same length as X non-time axis
        if 2d, must be same shape and format as X and Y

    Returns
    -------
    g : GifScatter
        Our custom object for handling scatterplot animations.
    """
    return GifScatter(X, Y, Z, C, S)


def ColorMesh(C: ArrayLike,
              X: Optional[ArrayLike] = None,
              Y: Optional[ArrayLike] = None):
    """Generates a Giffy Colormesh chart to manipulate.

    Parameters
    ----------
    C : ndarray 3d (time, x, y)
        data matrix with time as the first axis.
    X : ndarray 1d | tuple(2)
        grid to plot on the x-axis (instead of default)
    Y : ndarray 1d | tuple(2)
        grid to plot on the y-axis (instead of default)

    Returns
    -------
    g : GifColorMesh
        Our custom object for handling colormesh animations.
    """
    return GifColorMesh(C, X, Y)


def Contour(Z: ArrayLike,
            X: Optional[ArrayLike] = None,
            Y: Optional[ArrayLike] = None):
    """Generates a Giffy Contour chart to manipulate.

    Parameters
    ----------
    Z : ndarray 3d (time, x, y)
        data matrix with time as the first axis.
    X : ndarray 1d | tuple(2)
        grid to plot on the x-axis (instead of default)
    y : ndarray 1d | tuple(2)
        grid to plot on the y-axis (instead of default)

    Returns
    -------
    g : GifContour
        Our custom object for handling contour animations.
    """
    return GifContour(Z, X, Y)


def Quiver(U: ArrayLike,
           V: ArrayLike,
           X: Optional[ArrayLike] = None,
           Y: Optional[ArrayLike] = None):
    """Generates a Giffy Colormesh chart to manipulate.

    Parameters
    ----------
    U : ndarray 3d (x, y, time)
        data matrix of U coordinates with time as the last axis.
    V : ndarray 3d (x, y, time)
        data matrix of V coordinates with time as the last axis.
    X : ndarray 1d | tuple(2)
        grid to plot on the x-axis (instead of default)
    Y : ndarray 1d | tuple(2)
        grid to plot on the y-axis (instead of default)

    Returns
    -------
    g : GifQuiver
        Our custom object for handling quiver animations.
    """
    return GifQuiver(U, V, X, Y)
