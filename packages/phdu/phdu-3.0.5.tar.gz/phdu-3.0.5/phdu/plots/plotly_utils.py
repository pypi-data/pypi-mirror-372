"""
Helper funcs for plotly figures
"""
import numpy as np
import pandas as pd
import re
import warnings
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except:
    warnings.warn("'plotly' not available.", RuntimeWarning)
try:
    import colorlover as cl
except:
    warnings.warn("'colorlover' not available.", RuntimeWarning)
from collections import defaultdict
from collections.abc import Iterable
from functools import partial
from .. import _helper
from .base import color_std, plotly_default_colors, color_gradient

def add_offset(x0, xf, offset=0.05):
    """x0 (xf) == lower (upper) limit for the axis range."""
    inverse_transform = lambda *xs: [(xf-x0)*x + x0 for x in xs]
    return inverse_transform(-offset, 1+offset)

def get_common_range(fig, axes=["x", "y"], offset=[0.05, 0.05]):
    data = defaultdict(list)
    for plot in fig.data:
        for ax in axes:
            if hasattr(plot, f"error_{ax}") and getattr(plot, f"error_{ax}").array is not None:
                additions = [np.array([*plot[f"error_{ax}"]["array"]]), -np.array([*plot[f"error_{ax}"]["array"]])]
            else:
                additions = [0]
            for addition in additions:
                try:
                    arr = (plot[ax] + addition)[~np.isnan(plot[ax])]
                except:
                    continue
                arr_min, arr_max = arr.min(), arr.max()
                data[f"{ax}-min"].append(arr_min)
                data[f"{ax}-max"].append(arr_max)
    for k, v in data.items():
        func = min if "min" in k else max
        data[k] = func(v)
    ranges = {ax: add_offset(data[f"{ax}-min"], data[f"{ax}-max"], offset=off) for ax, off in zip(axes, offset)}
    return ranges

def get_nplots(fig):
    return sum(1 for x in fig.layout if "xaxis" in x)

def mod_delete_axes(fig, axes=["x", "y"]):
    non_visible_axes_specs = dict(visible=False, showgrid=False, zeroline=False)
    return {f"{ax}axis{i}": non_visible_axes_specs for ax in axes for i in [""] + [*range(1, get_nplots(fig) + 1)]}

def mod_simple_axes(fig, axes=["x", "y"]):
    simple_axes=dict(showline=True, linecolor='black', linewidth=2.4)
    return {f"{ax}axis{i}": simple_axes for ax in axes for i in [""] + [*range(1, get_nplots(fig) + 1)]}

def get_mod_layout(key, val=None):
    def mod_layout(fig, val, axes=["x","y"]):
        if isinstance(val, Iterable) and not isinstance(val, str):
            return {"{}axis{}_{}".format(ax, i, key): v for (ax, v) in zip(axes, val) for i in [""] + [*range(1, get_nplots(fig) + 1)]}
        else:
            return {"{}axis{}_{}".format(ax, i, key): val for ax in axes for i in [""] + [*range(1, get_nplots(fig) + 1)]}
    if val is None:
        return mod_layout
    else:
        def mod_layout_fixed_val(fig, axes=["x", "y"]):
            return mod_layout(fig, val, axes)
        return mod_layout_fixed_val

mod_dashes           = partial(_helper.sequence_or_stream, ["solid", "dash", "dot"])
mod_ticksize         = get_mod_layout("tickfont_size")
mod_logaxes          = get_mod_layout("type", "log")
mod_expfmt           = get_mod_layout("exponentformat", "power")
mod_range            = get_mod_layout("range")
mod_logaxes_expfmt   = lambda fig, axes=["x", "y"]: {**mod_logaxes(fig, axes=axes), **mod_expfmt(fig, axes=axes)}

def mod_common_range(fig, axes=["x", "y"], **kwargs):
    return mod_range(fig, val=get_common_range(fig, axes=axes, **kwargs), axes=axes)

def fig_base_layout(ticksize=32, **kwargs):
    base = dict(margin=dict(l=100, r=20, b=80, t=20, pad=1),
                height=800, width=1000, yaxis=dict(tickfont_size=ticksize),
                xaxis=dict(tickfont_size=ticksize), font_size=40, legend_font_size=40,
                font_family="sans-serif", hovermode=False
                )
    base.update(kwargs)
    return base

def get_figure(height=800, width=1000, ticksize=32, font_size=40, margin=None, font_family="sans-serif", hovermode=False, delete_axes=False, simple_axes=True, **kwargs):
    """
    Attributes:
    - delete_axes:   delete axes and gridlines
    - simple_axes:        white background, black axes and gridlines
    """
    args = {k: v for k, v in locals().items() if k not in ['kwargs', 'delete_axes', 'simple_axes']}
    args.update(kwargs)

    fig = go.Figure(layout=fig_base_layout(**args))
    if delete_axes:
        fig.update_layout(**mod_delete_axes(fig), margin=dict(l=0, t=0, b=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    elif simple_axes:
        fig.update_layout(**mod_simple_axes(fig), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def subplots_base_layout(cols, rows=1, make_subplots_kwargs={}, **layout_kwargs):
    layout = dict(margin=dict(l=100, r=20, b=80, t=60, pad=1), height=800*rows, width=2500)
    layout.update(layout_kwargs)

    base = dict(layout=layout,
                shared_yaxes=True, shared_xaxes=True,
                horizontal_spacing=0.03, vertical_spacing=0.03, rows=rows, cols=cols,
                )
    base.update(make_subplots_kwargs)
    return base

def get_subplots(cols, rows=1, horizontal_spacing=0.03, vertical_spacing=0.03, height=None, width=2500, ticksize=32, font_size=40, font_family="sans-serif",
                 hovermode=False, delete_axes=False, simple_axes=True, shared_xaxes=True, shared_yaxes=True, layout_kwargs={},
                 **make_subplots_kwargs):
    height = 800*rows if height is None else height
    fig = make_subplots(figure=go.Figure(layout=dict(margin=dict(l=100, r=20, b=80, t=60, pad=1), height=height, width=width)),
                        shared_yaxes=shared_yaxes, shared_xaxes=shared_xaxes,
                        horizontal_spacing=horizontal_spacing, vertical_spacing=vertical_spacing, rows=rows, cols=cols,
                        **make_subplots_kwargs
                       )

    fig.for_each_annotation(lambda a: a.update(font={'size':font_size, "family":font_family}))
    fig.update_layout(**mod_ticksize(fig, val=ticksize), legend_font_size=font_size, hovermode=hovermode, **layout_kwargs)
    if delete_axes:
        fig.update_layout(**mod_delete_axes(fig), margin=dict(l=0, t=0, b=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    elif simple_axes:
        fig.update_layout(**mod_simple_axes(fig),  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def transparent_colorscale(fig=None, colorscale=None, threshold=1e-10):
    """Values below threshold are invisible."""
    if fig is not None:
        colorscale = fig.layout["coloraxis"]["colorscale"]
    else:
        assert colorscale is not None, "fig or colorscale must be provided."
    low_limit = colorscale[0]
    new_low_limit = (threshold, low_limit[1])
    new_colorscale = ((0, 'rgba(0,0,0,0)'), new_low_limit, *colorscale[1:])
    return new_colorscale

def multiindex_to_label(i, depth=2):
    return [i.get_level_values(k).to_list() for k in range(depth)]

def set_multicategory_from_df(fig, df):
    fig.update_layout(xaxis_type="multicategory", yaxis_type="multicategory")
    fig.data[0]["x"] = multiindex_to_label(df.columns)
    fig.data[0]["y"] = multiindex_to_label(df.index)
    return

def CI_plot(*, df=None, x=None, y=None, CI=None, label=None, width=0.05, ms=10, color='rgba(255, 127, 14, 0.3)', color_sample_stat="green", width_sample_stat=8,  fig=None, x_title=None, y_title=None, color_legend=None, plot_stat_for_nan_CI=True, **fig_kwargs):
    """
    Box plot where the box corresponds to the CI.

    Attributes:
        - x:    x coordinate for the CI
        - y:    value of the magnitude for the sample. Example: the mean if CI is a CI for the mean.
        - CI:   Confidence interval for y.
    """
    if df is not None:
        x = df.index.tolist()
        y = df.sample_stat.values
        CI = np.vstack(df.CI.values)

    if fig is None:
        fig = get_figure(xaxis_title=x_title, yaxis_title=y_title, **fig_kwargs)
    if color_legend is None:
        color_legend = color

    idx_to_xlabel = {i: x_val for i, x_val in enumerate(x)}
    for i, (ci, _, ci_stat) in enumerate(zip(CI, x, y)):
        if not np.isnan(ci).all():
            fig.add_shape(type="line", xref="x", yref="y", line=dict(color=color_sample_stat, width=width_sample_stat),  x0=i-width, y0=ci_stat, x1=i+width, y1=ci_stat)
            fig.add_shape(type="rect", xref="x", yref="y", line=dict(color="gray",width=4), fillcolor=color, x0=i-width, y0=ci[0], x1=i+width, y1=ci[1])
            fig.add_trace(go.Scatter(x=[i]*2, y=ci[::-1], showlegend=False, mode="markers",
                                     marker=dict(color=color, symbol=["arrow-bar-down", "arrow-bar-up"], size=ms, line=dict(color="gray", width=2))
                                ))
        elif plot_stat_for_nan_CI:
            fig.add_shape(type="line", xref="x", yref="y", line=dict(color=color_sample_stat, width=width_sample_stat),  x0=i-width, y0=ci_stat, x1=i+width, y1=ci_stat)

        fig.update_layout(xaxis=dict(tickvals=[*idx_to_xlabel.keys()], ticktext=[*idx_to_xlabel.values()]))
    if label is not None:
        yrange = [*get_common_range(fig, axes=["y"]).values()][0]
        fig.add_trace(go.Scatter(x=[1000], y=[1000], mode="markers", name=label, showlegend=True,
                                 marker=dict(symbol="square", color=color_legend, size=22), line=dict(color="gray", width=2)))
        fig.update_layout(**mod_range(fig, ([-0.25, len(x)-0.75], yrange)))
    return fig

def CI_ss_plot(df, label=False, width=0.05, ms=10, ns_color='#323232', ss_lower_color='#1f77b4', ss_upper_color='#ff7f0e', color_sample_stat='black', width_sample_stat=5, **CI_plot_kwargs):
    """
    df: Dataframe containing the x coordinate in the index
        and columns:
            - 'sample stat': sample statistic
            - 'CI':          confidence interval
            - 'lb':          lower bound
            - 'ub':          upper bound
    """
    def map_to_nan(x, bool_arr):
        y = x.copy()
        y[bool_arr] = np.NaN
        return y
    lb_sign = np.sign(df['lb'])
    ss = lb_sign == np.sign(df['ub'])
    ss_upper = ss & (lb_sign == 1)
    ss_lower = ss & (lb_sign == -1)
    df_ns, df_ss_upper, df_ss_lower = df.copy(), df.copy(), df.copy()
    cis = np.vstack(df.CI.values)
    df_ns['CI'] = map_to_nan(cis, ss).tolist()
    df_ss_upper['CI'] = map_to_nan(cis, ~ss_upper).tolist()
    df_ss_lower['CI'] = map_to_nan(cis, ~ss_lower).tolist()
    # NS intervals
    fig = CI_plot(df=df_ns, width=width, ms=ms, color=color_std(ns_color, opacity=0.55), label='Not SS' if label else None,
                  color_sample_stat=color_sample_stat, width_sample_stat=width_sample_stat,
                  **CI_plot_kwargs)
    # Adding significant intervals
    figdata = {'SS (>0)': (df_ss_upper, ss_upper_color), 'SS (<0)': (df_ss_lower, ss_lower_color)}
    for label_ss, (df_ss, ss_color) in figdata.items():
        fig = CI_plot(df=df_ss, width=width, ms=ms, fig=fig, color=color_std(ss_color, opacity=0.2), label=label_ss if label else None, color_sample_stat=color_sample_stat, width_sample_stat=width_sample_stat)
    # colorizing the index
    def colorize(index_upper, index_lower):
        """
        index: pd.Series where index is the feature name and value is of type bool.
        """
        ticktext = []
        for f, is_ss_upper in index_upper.items():
            if is_ss_upper:
                ticktext.append(f"<span style='color:{str(ss_upper_color)}'> {str(f)} </span>")
            elif index_lower[f]: # is_ss_lower
                ticktext.append(f"<span style='color:{str(ss_lower_color)}'> {str(f)} </span>")
            else:
                ticktext.append(f"<span style='color:{str(ns_color)}'> {str(f)} </span>")
        return ticktext
    ticktext = colorize(ss_upper, ss_lower)
    fig.update_layout(xaxis=dict(tickmode='array', ticktext=ticktext, tickvals=np.arange(ss.size)))

    fig.update_layout(plot_bgcolor='white', yaxis=dict(showline=True, linecolor='black', linewidth=2.4),
                      xaxis=dict(showline=True, linecolor='black', linewidth=2.4))
    fig.add_hline(y=0, line=dict(color='black', width=1, dash='dash'))
    return fig

def CI_bar_plot(df, *, x, group, base, y_label, color=None, group_order=None, x_order=None, width=0.5, y_range=[0, 1], baseline_in_legend=True, default_x_order='descending', default_group_order='descending', format_label=True):
    """
    This function creates a bar plot with confidence intervals (CI) for a given DataFrame. For each 'x' value, the plot shows a bar for each 'group' value, with the height of the bar representing the sample statistic and the CI represented by the error bars. The baseline value is also plotted as a gray bar.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data to be plotted. Must have columns for 'x', 'group', 'sample_stat', 'CI', and 'base'.
    x (str): The column name in df to be used as the x-axis.
    group (str): The column name in df to be used for grouping the data.
    base (str): The column name in df to be used as the baseline for the plot.
    y_label (str): The label to be used for the y-axis.
    group_order (list, optional): The order in which the groups should be plotted. If not provided, groups are ordered based on their mean values.
    x_order (list, optional): The order in which the x-axis values should be plotted. If not provided, x-axis values are ordered based on their mean values.
    width (float, optional): The width of the bars in the plot. Default is 0.5.
    y_range (list, optional): The range of the y-axis. Default is [0, 1].
    baseline_in_legend (bool, optional): Whether to include the baseline in the legend. Default is True.
    default_x_order (str, optional): The default order for the x-axis values if x_order is not provided. Can be 'ascending' or 'descending'. Default is 'descending'.
    default_group_order (str, optional): The default order for the groups if group_order is not provided. Can be 'ascending' or 'descending'. Default is 'descending'.

    Returns:
    plotly.graph_objs._figure.Figure: The resulting bar plot with confidence intervals.

    Raises:
    AssertionError: If group_order is not a subset of the unique values in df[group].
    AssertionError: If x_order is not a subset of the unique values in df[x].
    """
    if format_label:
        def label_fmt(x):
            if x == x.upper():
                return x
            else:
                return x.capitalize()
    else:
        label_fmt = lambda x: x

    def get_order(df, column, default_order):
        if default_order == 'ascending':
            return df.groupby(column)['sample_stat'].mean().sort_values(ascending=True).index
        elif default_order == 'descending':
            return df.groupby(column)['sample_stat'].mean().sort_values(ascending=False).index
        else:
            return np.unique(df[column].values)
    if group_order is None:
        group_order = get_order(df, group, default_group_order)
    if x_order is None:
        x_order = get_order(df, x, default_x_order)

    assert set(df[group].values) >= set(group_order), f"group_order must be a subset of the unique values in df['{group}']"
    assert set(df[x].values) >= set(x_order), f"x_order must be a subset of the unique values in df['{x}']"

    X = np.arange(df.index.size)
    num_groups = len(group_order)
    width /= num_groups
    X0 = X - (num_groups-1)*width

    if color is not None:
        if isinstance(color, str) and color in df.columns:
            colors = df.set_index(group_order)[color].to_dict()
        else:
            colors = {g: c for g, c in zip(group_order, color)}
    else:
        if num_groups > 2:
            color_gen = plotly_default_colors()
        else:
            color_gen = plotly_default_colors(4)[1:]
        colors = {k: c for k, c in zip(group_order, color_gen)}

    fig = get_figure(xaxis_title=label_fmt(x), yaxis_title=label_fmt(y_label))
    xaxis_ticktext = []
    for i, idx in enumerate(x_order):
        df_i = df[df[x] == idx]
        xaxis_ticktext.append(idx)
        for j, g in enumerate(group_order):
            if g in df_i[group].values:
                color_g = colors[g]
                Xj = X0[i] + j*width
                df_g = df_i[df_i[group] == g].iloc[0]
                y = df_g.sample_stat
                CI = df_g.CI.squeeze()
                baseline = df_g[base]
                error_up = np.clip(CI[1], *y_range) - y
                error_down = y - np.clip(CI[0], *y_range)
                # plot bars
                fig.add_trace(go.Bar(x=[Xj], y=[y], name=label_fmt(g), marker=dict(color=color_g), width=width, showlegend=i == 0))
                fig.add_trace(go.Bar(x=[Xj], y=[baseline], name=label_fmt(base), marker=dict(color='grey'), width=width, showlegend=baseline_in_legend and i == 0 and j == (num_groups-1)))
                # plot error
                fig.add_trace(go.Scatter(x=[Xj], y=[y], error_y=dict(type='data', array=[error_up], arrayminus=[error_down], color=color_gradient(color_g, 'black', 6)[1], width=4, thickness=3), mode='markers', marker=dict(color=color_g, size=0.5), showlegend=False))

    fig.update_layout(yaxis_range=y_range, barmode='overlay',
                      xaxis=dict(tickvals=np.vstack((X, X0)).mean(axis=0),
                                 ticktext=xaxis_ticktext,
                                 tickangle=90),
                     legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    return fig

def permtest_plot(df, H1="", colorscale="Inferno", log=True, height=800, width=1000, font_size=40, bar_len=0.9, bar_x=0.95, bar_thickness=100):
    """H1 should not contain latex code. Use unicode and HTML for super/sub-indices."""
    if log:
        df = np.log10(df)
        zmin, zmax = np.log10(0.05), 0
        legtitle = "log<sub>10</sub>P-value"
    else:
        zmin, zmax = None, None
        legtitle = "P-value"
    fig = px.imshow(df, zmin=zmin, zmax=zmax, color_continuous_scale=colorscale)
    fig.update_layout(coloraxis_colorbar=dict(len=bar_len, x=bar_x, title=f"{legtitle}<br>H<sub>1</sub>: {H1}", thickness=bar_thickness),
                      height=height, width=width, font_size=font_size, hovermode=False,
                      margin=dict(l=0, b=0, t=0, r=0)
                     )
    return fig

def violin(df, CI=None, CI_line="mean", **CI_kwargs):
    """
    Violin plot including optionally the CI.

    Attributes:
        - df:   melted DataFrame. Contains only two columns: variable name (x) and value (y).
                                  The column names set the OX and OY labels.
    """
    x, y = df.columns
    fig = get_figure(xaxis_title=x, yaxis_title=y)
    fig.add_trace(go.Violin(x=df[x], y=df[y], showlegend=False))
    if CI is not None:
        fig = CI_plot(df[x].unique(), getattr(df.groupby(x), CI_line)().values.squeeze(), CI, fig=fig, **CI_kwargs)
    return fig

def rgb_to_hex(rgb):
    if isinstance(rgb, str):
        rgb = rgb_text_to_rgb(rgb)
    return '#' + '%02x%02x%02x' % rgb

def rgb_text_to_rgb(text):
    colors = re.findall(r'rgb\((.*?)\)', text)[0]
    return tuple(int(c) for c in colors.split(","))

def rgb_to_text(rgb):
    return 'rgb({},{},{})'.format(*rgb)

def p_value_colorscale(base_cs="RdBu_r", out='rgb-text', interpolate=True, step=0.05):
    """
    Colorscale where color difference is proportional to the probability of a type I error.
    Example: p=0.1 has double probability of type I error than p=0.05.
             p=0.5 has 10 times the probability of type I error of p=0.05.
    """
    cs_len = int(0.5 / step)
    def keep_first_appearance(colorscale):
        s, c = zip(*colorscale)
        _, unique_idxs = np.unique(c, return_index=True)
        unique_idxs = np.sort(unique_idxs)
        unique_s = np.array(s)[unique_idxs]
        unique_c = np.array(c)[unique_idxs]
        return [[s, c] for s, c in zip(unique_s, unique_c)]

    if interpolate:
        cs_interpolated = cl.to_rgb(cl.interp([*zip(*px.colors.get_colorscale("RdBu_r"))][1], 2*cs_len + 1))
        cg_low = [rgb_to_hex(c) for c in cs_interpolated[:cs_len+1]]
        cg_upper = [rgb_to_hex(c) for c in cs_interpolated[cs_len+1:]][::-1]
        c0, cm, cf = [rgb_to_hex(c) for c in np.array(cs_interpolated)[[0, cs_len, -1]]]
    else:
        c0, cm, cf = [rgb_to_hex(c) for s, c in np.array(px.colors.get_colorscale(base_cs))[[0, 5, -1]]]
        cg_low = color_gradient(c0, cm, cs_len)
        cg_upper = color_gradient(cf, cm, cs_len)
    r = np.arange(step, 0.5+step, step).round(3)
    idxs = (cs_len - 1/(2*r)).astype(int)
    lower_half = keep_first_appearance([[0, c0]] + [[r_i, cg_low[i]] for i, r_i in zip(idxs, r)])
    upper_half = keep_first_appearance([[1, cf]] + [[r_i, cg_upper[i]] for i, r_i in zip(idxs, (1-r).round(3))])[::-1][1:]
    colorscale = lower_half + upper_half
    if out == 'rgb-text':
        func = lambda c: rgb_to_text(px.colors.hex_to_rgb(c))
    elif out == 'rgb':
        func = px.colors.hex_to_rgb
    elif out == 'hex':
        func = lambda c: c
    else:
        raise ValueError(f"out '{out}' not valid. Available: 'rgb-text', 'rgb', 'hex'.")
    colorscale = [[s, func(c)] for s, c in colorscale]
    return colorscale

def plot_cs(cs):
    from IPython.display import HTML
    if isinstance(cs[0], list):
        _, c = zip(*cs)
    else:
        c = cs
    return HTML(cl.to_html(cl.to_hsl(c)))

def plot_confidence_bands(*, fig=None, df=None, x=None, y=None, CI=None, label=None, color='#1f77b4', lw=6, opacity=0.3, line_specs={}, yaxis='y', **fig_kwargs):
    """
    Plots a curve with confidence intervals as bands.

    Parameters:
    - fig: The figure object to which the traces will be added. If None, a new figure will be created with specs from fig_kwargs.
    - df: (Optional) The DataFrame containing the data to be plotted. Must contain columns 'sample_stat' and 'CI', and the index will be used as the x-coordinates.
    - x: The x-coordinates of the data points.
    - y: The y-coordinates of the data points (mean values).
    - CI: 2D array of confidence interval data, where CI[:, 0] is the lower bound and CI[:, 1] is the upper bound.
    - color: (Optional) The color of the plot. Default is blue.
    - lw: (Optional) The line width of the plot. Default is 6.
    - opacity: (Optional) The opacity of the confidence interval band. Default is 0.3.
    - fig_kwargs: (Optional) Additional keyword arguments to be passed to the get_figure function.
    """
    input_fig = fig is not None
    if not input_fig:
        fig = get_figure(**fig_kwargs)
    if df is not None:
        x = df.index
        y = df.sample_stat.values
        CI = np.vstack(df.CI.values)

    # Plot the main line (mean curve)
    fig.add_trace(go.Scatter(x=x, y=y,
                             line=dict(width=lw, color=color, **line_specs),
                             name=label,
                             showlegend=label is not None,
                             yaxis=yaxis))

    # Plot the confidence interval as a band
    fig.add_trace(go.Scatter(
        x=np.hstack([x, x[::-1]]), # x, then x reversed
        y=np.hstack([CI[:, 0], CI[:, 1][::-1]]), # upper CI, then lower CI reversed
        fill='toself',
        fillcolor=color,
        line=dict(color=color, width=0),
        opacity=opacity,
        yaxis=yaxis,
        showlegend=False,
    ))
    if not input_fig:
        return fig
    else:
        return
