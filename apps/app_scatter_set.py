import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import plotly.graph_objs as go
import pandas as pd
import re


ngenes = 3
colours = 7
metric_colours = 9
filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V4/exhaustive/threshold95p/'
set_filename = "SetMetrics_N" + format(ngenes) + "_C" + format(colours) + "_Cx" + format(metric_colours) + ".txt"
set_names = ['srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'analysed', 'total_neutral', 'diversity', 'pIDs']

df_set = pd.read_csv(filepath + set_filename, sep=" ", header=None, names=set_names)


layout = html.Div(children=[
    html.H3(children='Set Metrics'),
    dcc.Dropdown(id='dropdown-x',
                 options=[{'label': i, 'value': i} for i in df_set.columns.values[:-1]],
                 multi=False, placeholder='x-axis, ' + set_names[0]),
    dcc.Dropdown(id='dropdown-y',
                 options=[{'label': i, 'value': i} for i in df_set.columns.values[:-1]],
                 multi=False, placeholder='y-axis, ' + set_names[1]),
    dcc.Graph(id='graph-container-set'),
    dcc.Link('Go to Genome Scatter', href='/apps/app_scatter_genome')
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
