"""Defines a base class for all GIF animators."""

from abc import abstractmethod
from typing import Optional, Callable
from numpy.typing import ArrayLike

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from IPython import display

from ._helper import set_axis_labels, get_time_curve, Keywords


class GifBase:
    """A Gif Glyph for handling automatic animation.

    Gif is a declarative object where properties are declared and only on 'draw()'
     are values computed and executed.
    """

    def __init__(self, n_frames: int = 100, interval: int = 20):
        """Base class."""
        # interval and frames
        self.interval = interval
        self.n_frames = n_frames
        # one of ['linear', 'quad', 'cubic', 'sqrt', 'neglinear', 'sine']
        self._curve = "linear"
        self._curves = {'linear', 'quad', 'cubic', 'sqrt', 'neglinear', 'sine'}
        self._curve_f = lambda x: x
        # factors for lerping.
        self._lerp_kws = dict(kind='linear')
        self._lerp_factor = 1
        # ideal frames per second
        self._fps = 24.
        # default time in seconds
        self.time_seconds = 3.
        # whether the plot is 3d or not.
        self.d3 = False
        # an initialization function to call.
        self._init_func = None
        # specify an empty animation.
        self._anim = None

        # other keywords
        self._base_color = "b"
        # default x and y values to place on the labels.
        self._xval = ""
        self._yval = ""
        self._has_legend = False
        self._has_colorbar = True
        # default args list
        self._defargs = Keywords()

    ####################### METHODS BEGIN #####################################################

    @abstractmethod
    def mark(self, **kwargs):
        """Adds properties and markings to the plot."""
        pass

    @abstractmethod
    def _animate(self, time_seconds) -> Callable:
        """Computes the animation and returns the 'animf' object to pass to FuncAnimation"""
        pass
    
    def _generate(self, t_secs: float, ax = None):
        """Generates the animation. Internal method only called from plot() or save()"""
        # make the figure if not specified.
        if ax is None:
            # make a figure and axes
            self.fig = plt.figure()
            # define 3d plot if specified
            if self.d3:
                self.ax = self.fig.add_subplot(111, projection="3d")
            else:
                self.ax = self.fig.add_subplot(111)
        else:
            self.ax = ax
        
        # if 'init' is specified we call the callback method
        if self._init_func is not None:
            self._init_func(self.fig, self.ax)

        """Now modify the number of frames if interpolation is used in advance."""
        # firstly, update the number of frames if we have lerp
        if self._lerp_factor == 'auto':
            # get current fps
            if (self.n_frames / t_secs) > self._fps:
                # do nothing, we have plenty of samples already.
                self._lerp_factor = 1
            else:
                # convert the lerp factor into something that gets as close to 24fps as possible
                self._lerp_factor = int((t_secs * self._fps) / self.n_frames)
        self.n_frames *= self._lerp_factor

        # compute correct curve function and interval
        self._curve_f = get_time_curve(self._curve, self.n_frames)
        self.interval = (t_secs*1000) // self.n_frames

        # compute any linear interpolation here in subclass - this changes n_frames etc.
        if self._lerp_factor > 1:
            self._lerp_data()

        # compute the animation using the appropriate function.
        animf = self._animate(t_secs)

        # call funcanim.
        self._anim = FuncAnimation(
            self.fig, animf, frames=self.n_frames, interval=self.interval)

        # add x and y axis labels by default.
        set_axis_labels(self.ax, self._xval, self._yval)
         # tight figure layout
        self.fig.tight_layout()

    def _set_defargs(self, kwargs, allowed):
        for key, value in kwargs.items():
            # if the key is within the allowed keywords, then adjust the args.
            if key in allowed:
                self._defargs[key] = value

    ##################### HIDDEN Optional Methods to Override ################################

    def _lerp_data(self):
        """Handles any linear interpolation of the data by the subclass."""
        pass
    
    def _get_update(self):
        """Handles the custom update method."""
        raise NotImplementedError("_get_update() not implemented in GifBase.")

    def time_curve(self, curve: str):
        """Determine how quickly to progress through points."""
        if curve in self._curves:
            self._curve = curve
        else:
            raise ValueError(f"curve '{curve}' not a valid time curve option, choose from {self._curves}.")
        return self

    def callback(self, init_func: Optional[Callable] = None):
        """Specify callback methods at different stages of plotting for further customization.

        Parameters
        ----------
        init_func : callable, optional
            A function to be called before animation. init(fig, ax) -> None: takes a Figure 
            and axis and allows for static manipulation. This might be adjustments to the figure,
            ticks, limits and more.

        Returns
        -------
        self
        """
        self._init_func = init_func
        return self

    def lerp(self, factor: int | str = 'auto', **lerp_kws):
        """Linearly interpolates over the data points to make more data points.

        Executing lerp() is declarative and performs no action until the animation starts.

        Parameters
        ----------
        factor : int or str, default="auto"
            The scaling factor of the interpolation. 
            If 'auto' it will interpolate to make up to 24fps.
            If of type int, this value determines the number of steps to insert *between* each data point. 
                Must be positive >=1.
        lerp_kws : keywords
            Arguments to pass to scipy.interpolate.interp1d.
                These might include kind='quadratic'.

        Returns
        -------
        self
        """
        if isinstance(factor, int) and (factor < 1):
            raise ValueError("factor must be a positive integer")
        elif isinstance(factor, str) and factor != "auto":
            raise ValueError("factor must be == 'auto' if str")

        self._lerp_factor = factor
        self._lerp_kws = lerp_kws
        return self

    def legend(self, b: bool = True):
        """Specifies whether to draw a legend if available."""
        self._has_legend = b
        return self

    def cbar(self, b: bool = True):
        """Specifies whether to draw a colorbar if available."""
        self._has_colorbar = b
        return self

    def plot(self, time_seconds: float = 3., axes = None):
        """Draws the animation. 

        Parameters
        ----------
        time_seconds : float
            The length in seconds of the animation
        axes : matplotlib.ax.Axes
            If not specified a figure and axes are created.
        """
        if self._anim is None:
            # use _generate()
            self._generate(time_seconds, axes)
        
        # make video
        self._video = self._anim.to_html5_video()
        self._html = display.HTML(self._video)
        display.display(self._html)
        plt.close()
        return self.ax

    def save(self, fp: str):
        """Saves the animation. This function must be at the end of a function chain.
        
        Parameters
        ----------
        fp : str (filepath)
            Saves the file as a gif. The extension must be included.
        """
        if self._anim is None:
            # use _generate()
            self._generate(self.time_seconds)

        # save the gif
        self._anim.save(fp)
