
# coding: utf-8


# In[2]:

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import numpy as np
import plotly
from dash.dependencies import Input, Output, State


import pandas as pd
import re

from app import app

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

layout = html.Div([
    html.H3('Set Metric Table'),
    dt.DataTable(
        rows=df_set.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=set_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-polyomino-set'
    ),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-polyomino-set'
    ),
], className="container")


@app.callback(
    Output('datatable-polyomino-set', 'selected_row_indices'),
    [Input('graph-polyomino-set', 'clickData')],
    [State('datatable-polyomino-set', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices


@app.callback(
    Output('graph-polyomino-set', 'figure'),
    [Input('datatable-polyomino-set', 'rows'),
     Input('datatable-polyomino-set', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=3, cols=1,
        subplot_titles=('Robustness', 'Diversity', 'Evolvability',),
        shared_xaxes=True)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace({
        'x': dff['pIDs'],
        'y': dff['interrobustness'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['pIDs'],
        'y': dff['diversity'],
        'type': 'bar',
        'marker': marker
    }, 2, 1)
    fig.append_trace({
        'x': dff['pIDs'],
        'y': dff['evolvability'],
        'type': 'bar',
        'marker': marker
    }, 3, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 1200
    # fig['layout']['margin'] = {
    #     'l': 40,
    #     'r': 10,
    #     't': 60,
    #     'b': 200
    # }
    # fig['layout']['yaxis2']['type'] = 'log'
    return fig

#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
