"""
@editor: Liran Funaro <funaro@cs.technion.ac.il>
@author: Alex Nulman <anulman@cs.haifa.ac.il>
"""
import pandas as pd
from bokeh import charts
from bokeh.embed import components
from bokeh.io import save
from os.path import join as join_path
from collections import OrderedDict

#the following is for proof of concept
from bokeh.sampledata.unemployment1948 import data

def description():
    return "Heat Map"


def parameters():
    # return {'Line': {'x-axis':'single', 'y-axis':'single', 'group-by':'multiple'}}
    params = OrderedDict()
    params['x_axis'] = {'type': 'single', 'filterByValue': False}
    params['y_axis'] = {'type': 'single', 'filterByValue': False}
    params['group_by'] = {'type': 'multiple', 'filterByValue': True}
    return params


def image_path():
    return "img/pluginImg/Heat.png"


def plot(filename, sqlpath, x_axis, y_axis, group_by):
    data['Year'] = data['Year'].astype(str)
    unempl = pd.melt(data, var_name='Month', value_name='Unemployment', id_vars=['Year'])
    fig = charts.HeatMap(unempl, x='Year', y='Month', values='Unemployment', stat=None, sort_dim={'x': False}, sizing_mode='stretch_both')
    name = '{}_{}_{}_{}'.format(filename,__name__,x_axis,y_axis)
    name = name.replace(':','')
    unempl.to_json(join_path('static',name+'.json'))
    charts.output_file(join_path('static', name+'.html'), title=name, mode='cdn', root_dir=None)
    save(fig)
    js,div =components(fig, wrap_script = False, wrap_plot_info = True)
    return {'div':div, 'js':js}


