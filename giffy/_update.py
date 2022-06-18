"""A global update script."""
from typing import Callable, Optional
import numpy as np

from ._helper import get_array_by_3daxis


def _get_point_array(name: str, x, j: int):
    if name == 'point':
        return x[j]
    elif name == "point_r":
        return x[-j-1]
    elif name == "lines" or name == "steps":
        return x[:j]
    else:
        return x[-j-1:]


def global_update(data: dict,
                  plot_type: str,
                  mpl_objs: dict,
                  time_curve_function: Optional[Callable] = None,
                  custom_update_callback: Optional[Callable] = None):
    """This is a global update method for returning an appropriate update step function.

    data : dict of data
    plot_type : str, one of ['scatter','point','bar','pie','contour','colormesh']
    mpl_objs : matplotlib object(s) to draw on
    time_curve_function : a callable for curving time.
    custom_update_callback : a user function given i to do additional things.
    """
    def __custom_update(i):
        # the internal custom update method.
        j = time_curve_function(i) if time_curve_function is not None else i
        # insert custom callback here
        if custom_update_callback is not None:
            custom_update_callback(j)

        plots_ = ('bar_single', 'bar_multi', 'point', 'line', 'colormesh', 'contour', 'scatter', 'pie')

        # now do different things based on object type
        if plot_type == 'bar_single':
            # data : {X: pd.DataFrame, orient: str}, mpl_objs: {bar, title}
            mpl_objs['title'].set_text(data['X'].index[j])
            for b, v in zip(mpl_objs['bar'], data['X'].iloc[j]):
                b.set_height(v) if data['orient'] == 'vert' else b.set_width(v)
        
        elif plot_type == 'bar_multi':
            # data : {X: list of [pd.DataFrame], orient: str}, mpl_objs: {bars, title}
            mpl_objs['title'].set_text(data['X'][0].index[j])
            for b_obj, X in zip(mpl_objs['bars'], data['X']):
                for b, v in zip(b_obj, X.iloc[j]):
                    b.set_height(v) if data['orient'] == 'vert' else b.set_width(v)
        
        elif plot_type == 'point':
            # data : {traces: list of [{obj, x, y, z (optional)}], style: str}
            for trace in data['traces']:
                _x = _get_point_array(data['style'], trace['x'], j)
                _y = _get_point_array(data['style'], trace['y'], j)
                trace['obj'].set_data((_x, _y))
                # if we have z axis, trace that also
                if "z" in trace:
                    trace['obj'].set_3d_properties(_get_point_array(data['style'], trace['z'], j))
            #return [trace['obj'] for trace in data['traces']]
        
        elif plot_type == 'line':
            if data['X'].ndim > 1:
                # data: {Y: 2d array}, mpl_objs: {line}
                mpl_objs['line'].set_ydata(data['Y'][j, :])
            else:
                mpl_objs['line'].set_data((data['X'][j, :], data['Y'][j, :]))

        elif plot_type == 'colormesh':
            # data: {Z: 3d array, time: axis number}, mpl_objs: {mesh}
            _arr = get_array_by_3daxis(data['Z'], j, data['time'])
            mpl_objs['mesh'].set_array(_arr.flatten())

        elif plot_type == 'contour':
            raise NotImplementedError("contour is fundamentally different.")
        
        elif plot_type == 'scatter':
            # data : {X : 2d array, Y: 2d array, (Z, C, S: optional): 2d array, cmap}
            if "Z" in data:
                mpl_objs['scat']._offsets3d = (data['X'][j, :], data['Y'][j, :], data['Z'][j, :])
            else:
                mpl_objs['scat'].set_offsets(np.c_[data['X'][j, :], data['Y'][j, :]])
            
            if "C" in data:
                mpl_objs['scat'].set_facecolor(data['cmap'](data['C'][j, :]))
            if "S" in data:
                mpl_objs['scat'].set_sizes(data['S'][j, :])
        
        elif plot_type == 'pie':
            # data : {X : pd.DataFrame}, mpl_objs : {patches, texts, (annots, optional)}
            # normalize the data
            _sumx = np.sum(data['X'].iloc[j])
            _norm_x = (data['X'].iloc[j] / _sumx) * 360.
            _perc_x = (data['X'].iloc[j] / _sumx) * 100.
            # cumulative sum of angles
            cum_theta = np.hstack((0., np.cumsum(_norm_x)))
            # compute the positions in radians for each wedge
            pos_radian = np.radians(cum_theta[:-1] + (cum_theta[1:] - cum_theta[:-1]) / 2.)
            # modify theta for each patch
            for k, patch in enumerate(mpl_objs['patches']):
                patch.set_theta1(cum_theta[k])
                patch.set_theta2(cum_theta[k+1])
            # modify text locations and values.
            lab_dist = data['labeldist']
            for t, text in enumerate(mpl_objs['texts']):
                if _perc_x[t] > 1e-4:
                    # rotate text with the current wedge position.
                    text.set_x(lab_dist * np.cos(pos_radian[t]))
                    text.set_y(lab_dist * np.sin(pos_radian[t]))
                    text.set_text(data['X'].columns[t])
                else:
                    text.set_text("")
            # if we have annotations ,do these also
            if "annots" in mpl_objs:
                # compute the magnitude of annotations
                mag = (data['width'] * 0.6) + (1 - data['width'])
                for a, annot in enumerate(mpl_objs['annots']):
                    if _perc_x[a] > 1e-4:
                        annot.set_x(mag * np.cos(pos_radian[a]))
                        annot.set_y(mag * np.sin(pos_radian[a]))
                        if _perc_x[a] >= 1.:
                            annot.set_text(data['X'].columns[a])
                        else:
                            annot.set_text("<1%")
                    else:
                        annot.set_text("")
        
    # now leave the method
    return __custom_update
