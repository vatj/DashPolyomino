
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

## Load set metric files
#############################
duplicate_set_names = [name for name in file_names if ('DuplicateSetMetric' in name)]
set_names = [name for name in file_names if ('SetMetric' in name)]
duplicate_set_names.sort()
set_names.sort()

parameters = extract_parameters(duplicate_set_names[0])
parameters['ngenes'] -= 1
set_name = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

df_set = pd.read_csv(filepath + set_name, sep=" ")
df_set['diversity_tracker'] = df_set['diversity_tracker'].apply(lambda x: np.array(eval(x)))
df_set_dup = pd.read_csv(filepath + duplicate_set_names[0], sep=" ")
df_set_dup['diversity_tracker'] = df_set_dup['diversity_tracker'].apply(lambda x: np.array(eval(x)))

display_names = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity', 'neutral_size', 'analysed', 'misclassified', 'pIDs']
metrics = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity']


## Page layout
#############################
layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-duplicate',
            options=[{'label': name, 'value': name} for name in duplicate_set_names],
            value=duplicate_set_names[0], multi=False, placeholder=duplicate_set_names[0]),
        style={'width': '400px'}),
    html.H3('Duplicate Set Metric Table'),
    dt.DataTable(
        rows=df_set_dup.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[3],
        id='datatable-set-duplication'
    ),
    html.H3('Set Metric Table'),
    dt.DataTable(
        rows=df_set.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-bis'
    ),
    html.Div(
    [dcc.Dropdown(id='dropdown-set-metrics-duplicate',
    options=[{'label': metric, 'value': metric} for metric in metrics],
    value=metrics[2], multi=False, placeholder='Metrics :' + metrics[2]),
    dcc.Dropdown(id='dropdown-barmode-duplicate',
    options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
    value='grouped', multi=False, placeholder='Barmode')],
    style={'width': '200px'}),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-set-duplication'
    ),
], className="container")


## Interactive functions
#############################

## Update Table with data from desired file
##########################################################
@app.callback(
    Output('datatable-set-duplication', 'rows'),
    [Input('dropdown-file-set-duplicate', 'value')])
def update_displayed_file(file_name):
    df_set_dup = pd.read_csv(filepath + file_name, sep=" ")
    # df_set_dup['diversity_tracker'] = df_set_dup['diversity_tracker'].apply(lambda x: np.array(eval(x)))
    return df_set_dup.round(3).to_dict('records')

## Update Set Table with data from the corresponding ngenes - 1 file
##############################################################################
@app.callback(
    Output('datatable-set-bis', 'rows'),
    [Input('dropdown-file-set-duplicate', 'value')])
def update_displayed_file(file_name):
    parameters = extract_parameters(file_name)
    parameters['ngenes'] -= 1
    set_name = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
    df_set = pd.read_csv(filepath + set_name, sep=" ")
    # df_set['diversity_tracker'] = df_set['diversity_tracker'].apply(lambda x: np.array(eval(x)))
    return df_set.round(3).to_dict('records')

@app.callback(
    Output('graph-set-duplication', 'figure'),
    [Input('datatable-set-duplication', 'rows'),
     Input('datatable-set-bis', 'rows'),
     Input('datatable-set-duplication', 'selected_row_indices'),
     Input('dropdown-set-metrics-duplicate', 'value'),
     Input('dropdown-file-set-duplicate', 'value'),
     Input('dropdown-barmode-duplicate', 'value')])
def update_figure(rows_dup, rows_set, selected_row_indices, metric, file, barmode):
    dff = pd.DataFrame(rows_set)
    parameters = extract_parameters(file)
    file_genome_dup = 'DuplicateGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)
    parameters['ngenes'] -= 1
    file_genome = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)
    titles = []
    for i in (selected_row_indices or []):
        titles.append(metric + ' histogram for genome representants <br> of pID set : ' + rows_dup[i]['pIDs'])
        titles.append('Diversity tracking for pID set : ' + rows_dup[i]['pIDs'])
    fig = plotly.tools.make_subplots(
        rows= max(1, len(selected_row_indices)), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    fig_index = 0
    for row_index in (selected_row_indices or []):
        fig_index += 1
        pID = str(eval(rows_dup[row_index]['pIDs']))
        if not(rows_dup[row_index]['pIDs'] in dff.pIDs.unique()):
            print('Not found')
            continue;
        with pd.HDFStore(hdf_file,  mode='r') as store:
            df_genome = store.select(file_genome, where='pIDs == pID')
            df_genome_dup = store.select(file_genome_dup, where='pIDs == pID')
        fig.append_trace({
            'x': df_genome[metric],
            'type': 'histogram',
            'name': 'simple'
        }, fig_index, 1)
        fig.append_trace({
            'x': df_genome_dup[metric],
            'type': 'histogram',
            'name': 'dup'
        }, fig_index, 1)
        fig.append_trace({
            'x': pd.Series(eval(rows_dup[row_index]['diversity_tracker'])).index.values,
            'y': pd.Series(eval(rows_dup[row_index]['diversity_tracker'])),
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'dup'
        }, fig_index, 2)
        fig.append_trace({
            'y': pd.Series(eval(dff[dff['pIDs'] == rows_dup[row_index]['pIDs']]['diversity_tracker'].values[0])),
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'simple'
        }, fig_index, 2)
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = max(fig_index, 1) * 400
    return fig
