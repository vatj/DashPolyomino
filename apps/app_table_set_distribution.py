
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

from app import app, hdf_file, file_names, extract_parameters

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

set_metric_names = [name for name in file_names if name[:9] == 'SetMetric']
genome_metric_names = [name[:-4] for name in file_names if name[:12] == 'GenomeMetric']
set_metric_names.sort(), genome_metric_names.sort()

df = pd.read_csv(filepath + set_metric_names[0], sep=" ")
df['diversity_tracker'] = df['diversity_tracker'].apply(lambda x: np.array(eval(x)))

display_names = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity', 'neutral_size', 'analysed', 'misclassified', 'pIDs']
metrics = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity']

layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-metric',
            options=[{'label': name, 'value': name} for name in set_metric_names],
            value=set_metric_names[0], multi=False, placeholder=set_metric_names[0]),
        style={'width': '400px'}),
    dt.DataTable(
        rows=df.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[0],
        id='datatable-set-distribution'
    ),
    html.Div(id='selected-indexes'),
    html.Div(
    dcc.Dropdown(id='dropdown-metrics-distribution',
    options=[{'label': metric, 'value': metric} for metric in metrics],
    value='srobustness', multi=False, placeholder='Metrics : srobustness'),
    style={'width': '200px'}),
    dcc.Graph(
        id='graph-set-distribution'
    ),
], className="container")

@app.callback(
    Output('datatable-set-distribution', 'rows'),
    [Input('dropdown-file-set-metric', 'value')])
def update_displayed_file(file_name):
    df = pd.read_csv(filepath + file_name, sep=" ")
    df['diversity_tracker'] = df['diversity_tracker'].apply(lambda x: np.array(eval(x)))
    return df.round(3).to_dict('records')

@app.callback(
    Output('graph-set-distribution', 'figure'),
    [Input('datatable-set-distribution', 'rows'),
     Input('datatable-set-distribution', 'selected_row_indices'),
     Input('dropdown-metrics-distribution', 'value'),
     Input('dropdown-file-set-metric', 'value')])
def update_figure(rows, selected_row_indices, metric, file):
    data_diversity = pd.DataFrame()
    dff = pd.DataFrame(rows)
    parameters = extract_parameters(file)
    genome_file = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)
    titles = []
    for row_index in (selected_row_indices or []):
        titles.append(metric + ' histogram for genome representants <br> of pID set : ' + str(eval(dff['pIDs'][row_index])))
        titles.append('Diversity tracking for pID set : ' + str(eval(dff['pIDs'][row_index])))
    fig = plotly.tools.make_subplots(
        rows= max(1, len(selected_row_indices)), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    fig_index = 0
    for row_index in (selected_row_indices or []):
        fig_index += 1
        data_diversity[str(row_index)] = pd.Series(dff['diversity_tracker'][row_index])
        pID = str(eval(dff['pIDs'][row_index]))
        with pd.HDFStore(hdf_file,  mode='r') as store:
            df_genome = store.select(genome_file, where='pIDs == pID')
        fig.append_trace({
            'x': df_genome[metric],
            'type': 'histogram'
        }, fig_index, 1)
        fig.append_trace({
            'x': pd.Series(range(len(data_diversity[str(row_index)].dropna()))),
            'y': data_diversity[str(row_index)],
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': pID
        }, fig_index, 2)
    for index in range(1, max(fig_index + 1, 2), 2):
        fig['layout']['xaxis' + str(index)].update(title=metric)
        fig['layout']['yaxis' + str(index)].update(title='Number of genomes')
        fig['layout']['xaxis' + str(index + 1)].update(title='Number of genomes analyzed')
        fig['layout']['yaxis' + str(index + 1)].update(title='diversity')
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = max(fig_index, 1) * 400
    return fig
