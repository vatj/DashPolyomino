
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

from app import app, file_names, hdf_file

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
genome_metric_names = [name[:-4] for name in file_names if ('GenomeMetric' in name)]

with pd.HDFStore(hdf_file,  mode='r') as store:
    df_genome = store.select(genome_metric_names[0])

display_names = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity', 'pIDs']

layout = html.Div([
    html.H3('Genome Metric Table'),
    html.H4('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='datatable-polyomino-genome-file-selector',
            options=[{'label': name, 'value': name} for name in genome_metric_names],
            value=genome_metric_names[0], multi=False, placeholder=genome_metric_names[0]),
        style={'width': '400px'}),
    dt.DataTable(
        rows=df_genome.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-polyomino-genome'
    ),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-polyomino-genome'
    ),
], className="container")

@app.callback(
    Output('datatable-polyomino-genome', 'rows'),
    [Input('datatable-polyomino-genome-file-selector', 'value')])
def update_displayed_file(file_name):
    with pd.HDFStore(hdf_file,  mode='r') as store:
        df_genome = store.select(file_name)
    return df_genome.round(3).to_dict('records')

@app.callback(
    Output('datatable-polyomino-genome', 'selected_row_indices'),
    [Input('graph-polyomino-genome', 'clickData')],
    [State('datatable-polyomino-genome', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices


@app.callback(
    Output('graph-polyomino-genome', 'figure'),
    [Input('datatable-polyomino-genome', 'rows'),
     Input('datatable-polyomino-genome', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=3, cols=1,
        subplot_titles=('Robustness', 'Neutral Weight', 'Evolvability',),
        shared_xaxes=True)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace({
        'x': dff['pIDs'],
        'y': dff['irobustness'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['pIDs'],
        'y': dff['unbound'],
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
    fig['layout']['height'] = 800
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    fig['layout']['yaxis2']['type'] = 'log'
    return fig
