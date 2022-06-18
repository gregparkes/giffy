"""Helper script for plotting."""
import numpy as np
from numpy.typing import ArrayLike
from typing import Iterable, Callable, List, Optional, Tuple, Union
import itertools as it
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.dates import DateFormatter


def assert_condition(condition: bool, message: str, message_error = ValueError):
    if not condition:
        raise message_error(message)


def set_axis_labels(ax, xlab: str, ylab: str = "", zlab: str = "", title: str = ""):
    """Sets the axis labels in space notation."""
    ax.set_xlabel(xlab.strip())
    if ylab != "":
        ax.set_ylabel(ylab.strip())
    if zlab != "":
        ax.set_zlabel(zlab.strip())
    if title != "":
        ax.set_title(title.strip())


def set_axis_labels2(ax, label: str, math: bool = False):
    """Sets the axis labels in space notation."""
    lab = [l.strip() for l in label.split(", ")]
    if math:
        lab = [r"${}$".format(l) for l in lab]

    if len(lab) == 1:
        ax.set_xlabel(lab[0].strip())
    elif len(lab) == 2:
        ax.set_xlabel(lab[0])
        ax.set_ylabel(lab[1])
    elif len(lab) == 3:
        ax.set_xlabel(lab[0])
        ax.set_ylabel(lab[1])
        ax.set_title(lab[2])
    elif len(lab) == 4:
        ax.set_xlabel(lab[0])
        ax.set_ylabel(lab[1])
        ax.set_title(lab[2])
        ax.set_zlabel(lab[3])


def format_datetime_xticks(ax, fmt: str = "%m-%d"):
    ax.xaxis.set_major_locator(plt.MultipleLocator(5))
    ax.xaxis.set_major_formatter(DateFormatter(fmt))


def get_time_curve(curve: str, size: int) -> Callable[[int], int]:
    """Returns the correct time curve method for calculating index access."""
    def __curve_linear(i):
        return i

    def __curve_neglinear(i):
        return size-i

    def __curve_quadratic(i):
        return int(i**2 / size)

    def __curve_cubic(i):
        return int(i**3 / size**2)

    def __curve_sqrt(i):
        return int(np.sqrt(i) * np.sqrt(size))

    def __curve_sine(i):
        c1 = size/4.
        # do a 'sine wave' between the two points, clipping at 0 and 100.
        return int(np.clip(np.sin(i/4)*c1 + i, 0, size))

    mmap_curve = {"linear": __curve_linear, "neglinear": __curve_neglinear,
                  "quad": __curve_quadratic, "cubic": __curve_cubic,
                  "sqrt": __curve_sqrt, 'sine': __curve_sine}
    return mmap_curve[curve]


def colorwheel() -> Iterable[str]:
    wheel_list = [c['color'] for c in list(rcParams['axes.prop_cycle'])]
    return it.cycle(wheel_list)


def minmax(x: ArrayLike) -> ArrayLike:
    """scales a quantitative vector into [0, 1] for colormaps."""
    xm = np.min(x)
    return (x - xm) / (np.max(x) - xm)


def set_named_variable(x: Union[int,str], data) -> str:
    """Sets the variable according to a pandas.dataframe, x is in data."""
    if isinstance(x, int) and x < data.shape[1]:
        return data.columns[x]
    elif isinstance(x, str) and x in data:
        return x
    else:
        raise ValueError(f"variable `{x}` does not belong in data.")


def set_color_dataframe(col: Union[str,List,Tuple,ArrayLike], k_points: Optional[int] = None):
    """Sets the color attribute for a 1D dataframe."""
    if isinstance(col, (str, list, tuple)):
        return col
    elif isinstance(col, np.ndarray) and k_points is not None:
        # numpy array of shape (p, 4)
        if col.shape[0] != k_points:
            raise ValueError(
                "argument 'c'|'color' numpy object must have the same length as columns.")
        if col.ndim == 2 and col.shape[1] != 4:
            raise ValueError(
                "argument 'c'|'color' numpy object must have 1 or RGBA channels.")
        return col
    else:
        raise ValueError(
            "argument 'c'|'color' must be of type ['str', 'list', 'tuple', 'ndarray']")


def get_array_by_3daxis(data3d: ArrayLike, i: int = 0, t_axis: int = 0) -> ArrayLike:
    if t_axis == 0:
        return data3d[i, :, :]
    elif t_axis == 1:
        return data3d[:, i, :]
    else:
        return data3d[:, :, i]

class Keywords(dict):
    """A helper keyword class which supports aliases."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._alias = {}
    
    def _get_alias(self, k: str):
        if k in self._alias:
            return self._alias[k]
        else:
            return k

    def get_alias(self):
        return self._alias

    def set_alias(self, alias: dict):
        self._alias = alias
        return self
    
    def set_cond_key(self, cond: bool, k_true, k_false, value):
        """Sets a variable key based on a condition."""
        _k1 = self._get_alias(k_true)
        _k2 = self._get_alias(k_false)
        if cond:
            self.__setitem__(_k1, value)
        else:
            self.__setitem__(_k2, value)
        return self

    def remove(self, k: str):
        """Gently attempts to remove k without error"""
        _k = self._alias[k] if k in self._alias else k
        try:
            self.pop(_k)
        except KeyError:
            pass
        return self

    def __getitem__(self, k):
        return super().__getitem__(self._get_alias(k))
    
    def __setitem__(self, k, v):
        super().__setitem__(self._get_alias(k), v)
        return self

    def __contains__(self, k):
        return super().__contains__(self._get_alias(k))
