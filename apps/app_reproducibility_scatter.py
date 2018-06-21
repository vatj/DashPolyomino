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
parameters['njiggle'] = 100
parameters['threshold'] = 50

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V5/meeting/'
set_filename = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}_Iso.txt'.format(**parameters)
set_names = ['srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'analysed', 'total_neutral', 'diversity', 'pIDs']

df_ref1 = pd.read_csv(filepath + set_filename, sep=" ", header=None, names=set_names)

set_filename = 'SetMetrics2_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}_Iso.txt'.format(**parameters)

df_ref2 = pd.read_csv(filepath + set_filename, sep=" ", header=None, names=set_names)

df_ref1['evo'] = df_ref1['evolvability'] - df_ref1['rare'] - df_ref1['loop']
df_ref2['evo'] = df_ref2['evolvability'] - df_ref2['rare'] - df_ref2['loop']
set_names.insert(3, 'evo')


layout = html.Div(children=[
    html.H3(children='Reproducibility'),
    dcc.Dropdown(id='dropdown-reproducibility-x',
                 value=set_names[0],
                 options=[{'label': i, 'value': i} for i in set_names[:-1]],
                 multi=False, placeholder='x-axis, ' + set_names[0]),
    dcc.Dropdown(id='dropdown-reproducibility-y',
                 value=set_names[1],
                 options=[{'label': i, 'value': i} for i in set_names[:-1]],
                 multi=False, placeholder='y-axis, ' + set_names[1]),
    dcc.Graph(id='graph-container-reproducibility-set')
], className="content")


@app.callback(
    Output('graph-container-reproducibility-set', 'figure'),
    [Input('dropdown-reproducibility-x', 'value'),
     Input('dropdown-reproducibility-y', 'value')])
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
        x=df_ref1[xaxis], y=df_ref1[yaxis], text=df_ref1.pIDs, mode='markers'))
    traces.append(go.Scatter(
        x=df_ref2[xaxis], y=df_ref2[yaxis], text=df_ref2.pIDs, mode='markers'))

    return {'data' : traces,
           'layout': go.Layout(
               xaxis={'title' : xaxis}, yaxis={'title' : yaxis},
               hovermode='closest')}
