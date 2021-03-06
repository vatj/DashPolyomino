import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import plotly.graph_objs as go
import pandas as pd
import re


parameters = dict()
parameters['ngenes'] = 3
parameters['colours'] = 7
parameters['metric_colours'] = 9
parameters['builds'] = 10
parameters['njiggle'] = 30
parameters['threshold'] = 50

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V5/meeting/'
set_filename = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}_Iso.txt'.format(**parameters)
set_names = ['srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'analysed', 'total_neutral', 'diversity', 'pIDs']

df_set = pd.read_csv(filepath + set_filename, sep=" ", header=None, names=set_names)

df_set['evo'] = df_set['evolvability'] - df_set['rare'] - df_set['loop']
set_names.insert(3, 'evo')


layout = html.Div(children=[
    html.H3(children='Set Metrics'),
    dcc.Dropdown(id='dropdown-x',
                 value=set_names[0],
                 options=[{'label': i, 'value': i} for i in set_names[:-1]],
                 multi=False, placeholder='x-axis, ' + set_names[0]),
    dcc.Dropdown(id='dropdown-y',
                 value=set_names[1],
                 options=[{'label': i, 'value': i} for i in set_names[:-1]],
                 multi=False, placeholder='y-axis, ' + set_names[1]),
    dcc.Graph(id='graph-container-set')
], className="content")


@app.callback(
    Output('graph-container-set', 'figure'),
    [Input('dropdown-x', 'value'),
     Input('dropdown-y', 'value')])
def update_figure(dropdown_x, dropdown_y):
    if dropdown_x is None:
        xaxis = set_names[0]
    else:
        xaxis = dropdown_x
    if dropdown_y is None:
        yaxis = set_names[1]
    else:
        yaxis = dropdown_y

    traces = []

    traces.append(go.Scatter(
        x=df_set[xaxis], y=df_set[yaxis], text=df_set.pIDs, mode='markers'))

    return {'data' : traces,
           'layout': go.Layout(
               xaxis={'title' : xaxis}, yaxis={'title' : yaxis},
               hovermode='closest')}
