"""
@editor: Liran Funaro <funaro@cs.technion.ac.il>
@author: Alex Nulman <anulman@cs.haifa.ac.il>
"""
import pandas as pd
import numpy as np
from bokeh import plotting
from bokeh.embed import components
from bokeh.io import save
from os.path import join as join_path
from collections import OrderedDict

ignore_plugin = True

def description():
    return "Box Plot"


def parameters():
    params = OrderedDict()
    params['x_axis'] = {'label': 'X axis', 'type': 'single',
                        'default': 'timestamp', 'required': True}
    params['y_axis'] = {'label': 'Y axis', 'type': 'single',
                        'required': True}
    params['group_by'] = {'label': "Group By", 'type': 'single',
                          'required': True, 'filterByValue': {
        'type': 'multiple',
        'required': False
    }}
    return params


def image_path():
    return "img/pluginImg/Boxplot.png"


def plot(data, x_axis, y_axis, group_by):
    cats = list("abcdef")
    yy = np.random.randn(2000)
    g = np.random.choice(cats, 2000)
    for i, l in enumerate(cats):
        yy[g == l] += i // 2
    df = pd.DataFrame(dict(score=yy, group=g))

    # find the quartiles and IQR for each category
    groups = df.groupby('group')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    # find the outliers for each category
    def outliers(group):
        cat = group.name
        return group[(group.score > upper.loc[cat]['score']) | (group.score < lower.loc[cat]['score'])]['score']
    out = groups.apply(outliers).dropna()

    # prepare outlier data for plotting, we need coordinates for every outlier.
    if not out.empty:
        outx = []
        outy = []
        for cat in cats:
            # only add outliers if they exist
            if not out.loc[cat].empty:
                for value in out[cat]:
                    outx.append(cat)
                    outy.append(value)

        p = plotting.figure(tools="save", background_fill_color="#EFE8E2", title="", x_range=cats)

# if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.score = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'score']),upper.score)]
    lower.score = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'score']),lower.score)]

    # stems
    p.segment(cats, upper.score, cats, q3.score, line_color="black")
    p.segment(cats, lower.score, cats, q1.score, line_color="black")

    # boxes
    p.vbar(cats, 0.7, q2.score, q3.score, fill_color="#E08E79", line_color="black")
    p.vbar(cats, 0.7, q1.score, q2.score, fill_color="#3B8686", line_color="black")

    # whiskers (almost-0 height rects simpler than segments)
    p.rect(cats, lower.score, 0.2, 0.01, line_color="black")
    p.rect(cats, upper.score, 0.2, 0.01, line_color="black")

    # outliers
    if not out.empty:
        p.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="12pt"
    name = '{}_{}_{}_{}'.format(filename,__name__,x_axis,y_axis)
    name = name.replace(':','')
    plotting.output_file(join_path('static', name+'.html'), title=name, mode='cdn', root_dir=None)
    save(p)
    js,div =components(p, wrap_script = False, wrap_plot_info = True)
    return {'div':div, 'js':js}