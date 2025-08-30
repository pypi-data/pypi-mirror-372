"""
Helper funcs for plotting
"""
import numpy as np
from colour import Color
from PIL import ImageColor
from .. import _helper

def rows_cols(nrows, ncols):
    rows, cols = (np.vstack(np.divmod(range(nrows*ncols), ncols)) + 1)
    return rows, cols

def break_str(x, separator="<br>"):
    x_list = x.split(" ")
    mid = len(x_list) // 2
    return "{} {} {}".format(" ".join(x_list[:mid]), separator, " ".join(x_list[mid:]))

def plotly_default_colors(maxlen=None):
    colors = ['#1f77b4', '#ff7f0e',  '#2ca02c',  '#d62728',  '#9467bd',  '#8c564b',  '#e377c2',  '#7f7f7f',  '#bcbd22',  '#17becf']
    return _helper.sequence_or_stream(colors, maxlen=maxlen)

def plotly_colors(maxlen=None):
    cs = """aliceblue, antiquewhite, aqua, aquamarine, azure,
                beige, bisque, black, blanchedalmond, blue,
                blueviolet, brown, burlywood, cadetblue,
                chartreuse, chocolate, coral, cornflowerblue,
                cornsilk, crimson, cyan, darkblue, darkcyan,
                darkgoldenrod, darkgray, darkgrey, darkgreen,
                darkkhaki, darkmagenta, darkolivegreen, darkorange,
                darkorchid, darkred, darksalmon, darkseagreen,
                darkslateblue, darkslategray, darkslategrey,
                darkturquoise, darkviolet, deeppink, deepskyblue,
                dimgray, dimgrey, dodgerblue, firebrick,
                floralwhite, forestgreen, fuchsia, gainsboro,
                ghostwhite, gold, goldenrod, gray, grey, green,
                greenyellow, honeydew, hotpink, indianred, indigo,
                ivory, khaki, lavender, lavenderblush, lawngreen,
                lemonchiffon, lightblue, lightcoral, lightcyan,
                lightgoldenrodyellow, lightgray, lightgrey,
                lightgreen, lightpink, lightsalmon, lightseagreen,
                lightskyblue, lightslategray, lightslategrey,
                lightsteelblue, lightyellow, lime, limegreen,
                linen, magenta, maroon, mediumaquamarine,
                mediumblue, mediumorchid, mediumpurple,
                mediumseagreen, mediumslateblue, mediumspringgreen,
                mediumturquoise, mediumvioletred, midnightblue,
                mintcream, mistyrose, moccasin, navajowhite, navy,
                oldlace, olive, olivedrab, orange, orangered,
                orchid, palegoldenrod, palegreen, paleturquoise,
                palevioletred, papayawhip, peachpuff, peru, pink,
                plum, powderblue, purple, red, rosybrown,
                royalblue, saddlebrown, salmon, sandybrown,
                seagreen, seashell, sienna, silver, skyblue,
                slateblue, slategray, slategrey, snow, springgreen,
                steelblue, tan, teal, thistle, tomato, turquoise,
                violet, wheat, white, whitesmoke, yellow,
                yellowgreen"""
    li = cs.split(',')
    li = [l.replace('\n','') for l in li]
    li = [l.replace(' ','') for l in li]
    return _helper.sequence_or_stream(li, maxlen=maxlen)

def show_plotly_colors():
    import pandas as pd
    import plotly.graph_objects as go

    li = plotly_colors()
    li = [l for l in li]

    df=pd.DataFrame.from_dict({'colour': li})
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Plotly Named CSS colours"],
            line_color='black', fill_color='white',
            align='center', font=dict(color='black', size=14)
        ),
        cells=dict(
            values=[df.colour],
            line_color=[df.colour], fill_color=[df.colour],
            align='center', font=dict(color='black', size=11)
        ))
                          ])

    fig.show()
    return

def color_gradient(start, end, n, to_hex=True):
    colors = [*Color(start).range_to(Color(end), n)]
    if to_hex:
        return [c.hex for c in colors]
    else:
        return colors

def color_std(color, opacity=0.3):
    """Colors for the band y_mean +- y_std"""
    return "rgba" + str((*ImageColor.getrgb(color), opacity))
