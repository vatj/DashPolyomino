
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
parameters['builds'] = 40
parameters['njiggle'] = 200
parameters['threshold'] = 25


## Load set metric files
#############################
filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
jiggle_filename = 'JiggleSetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
parameters['ngenes'] += 1
jiggle_duplicate_filename = 'JiggleDuplicateSetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
set_names = ['srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'analysed', 'total_neutral', 'diversity', 'diversity_tracker', 'pIDs']

df_jiggle = pd.read_csv(filepath + jiggle_filename, sep=" ", header=None, names=set_names)
df_dup = pd.read_csv(filepath + jiggle_duplicate_filename, sep=" ", header=None, names=set_names)

df_jiggle['diversity_tracker'] = df_jiggle['diversity_tracker'].apply(lambda x: np.array(eval(x)))
df_jiggle['evo'] = df_jiggle['evolvability'] - df_jiggle['rare'] - df_jiggle['loop']
df_dup['diversity_tracker'] = df_dup['diversity_tracker'].apply(lambda x: np.array(eval(x)))
df_dup['evo'] = df_dup['evolvability'] - df_dup['rare'] - df_dup['loop']
set_names.insert(3, 'evo')
set_names.remove('diversity_tracker')
#############################

## Load genome metric files
#############################
parameters['ngenes'] -= 1
jiggle_filename_genome = 'JiggleGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
parameters['ngenes'] += 1
jiggle_duplicate_filename_genome = 'JiggleDuplicateGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
genome_names = ['genome', 'srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'diversity', 'neutral_weight', 'frequencies', 'pIDs']

df_jiggle_genome = pd.read_csv(filepath + jiggle_filename_genome, sep=" ", header=None, names=genome_names)
df_dup_genome = pd.read_csv(filepath + jiggle_duplicate_filename_genome, sep=" ", header=None, names=genome_names)

df_jiggle_genome['evo'] = df_jiggle_genome['evolvability'] - df_jiggle_genome['rare'] - df_jiggle_genome['loop']
df_dup_genome['evo'] = df_dup_genome['evolvability'] - df_dup_genome['rare'] - df_dup_genome['loop']
genome_names.insert(4, 'evo')
##########################


## Page layout
#############################
layout = html.Div([
    html.H3('Simple Set Metric Table'),
    dt.DataTable(
        rows=df_jiggle.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=set_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-jiggle'
    ),
    html.H3('Duplicate Set Metric Table'),
    dt.DataTable(
        rows=df_dup.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=set_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-duplicate-jiggle'
    ),
    html.Div(
    dcc.Dropdown(id='dropdown-set-metrics-duplicate',
    options=[{'label': metric, 'value': metric} for metric in genome_names[1:-3]],
    value=genome_names[1], multi=False, placeholder='Metrics :' + genome_names[1]),
    style={'width': '200px'}),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-set-duplicate-jiggle'
    ),
], className="container")


## Interactive functions
#############################
@app.callback(
    Output('datatable-set-jiggle', 'selected_row_indices'),
    [Input('graph-set-duplicate-jiggle', 'clickData')],
    [State('datatable-set-jiggle', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices

# @app.callback(
#     Output('datatable-set-duplicate-jiggle', 'rows'),
#     [Input('datatable-set-jiggle', 'rows'),
#      Input('datatable-set-jiggle', 'selected_row_indices')])
# def update_duplicate_table(rows, selected_row_indices):
#     list_genome=[]
#     for i in (selected_row_indices or []):
#         list_genome.append(df_jiggle['genome'][i][1:-1])
#
#     new_df=df_dup[df_dup.genome.str.contains('|'.join(list_genome))]
#     return new_df.round(3).to_dict('records')

@app.callback(
    Output('graph-set-duplicate-jiggle', 'figure'),
    [Input('datatable-set-jiggle', 'rows'),
     Input('datatable-set-jiggle', 'selected_row_indices'),
     Input('dropdown-set-metrics-duplicate', 'value')])
def update_figure(rows, selected_row_indices, metric):
    data_diversity = pd.DataFrame()
    dff = pd.DataFrame(rows)
    titles = []
    for i in (selected_row_indices or []):
        titles.append(metric + ' histogram for genome representants <br> of pID set : ' + dff['pIDs'][i])
        titles.append('Diversity tracking for pID set : ' + dff['pIDs'][i])
    fig = plotly.tools.make_subplots(
        rows= max(1, len(selected_row_indices)), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    fig_index = 0
    for i in (selected_row_indices or []):
        fig_index += 1
        fig.append_trace({
            'x': df_jiggle_genome[df_jiggle_genome['pIDs'] == dff['pIDs'][i]][metric],
            'type': 'histogram',
            'name': 'simple'
        }, fig_index, 1)
        fig.append_trace({
            'x': df_dup_genome[df_dup_genome['pIDs'] == dff['pIDs'][i]][metric],
            'type': 'histogram',
            'name': 'dup'
        }, fig_index, 1)
        data_diversity[str(i)] = pd.Series(dff['diversity_tracker'][i])
        df_temp = df_dup[df_dup['pIDs'] == (dff['pIDs'][i])]
        data_diversity[str(i) + '_dup'] = pd.Series(df_temp['diversity_tracker'][df_temp['diversity_tracker'].first_valid_index()])
        fig.append_trace({
            'x': pd.Series(range(len(data_diversity[str(i)].dropna()))),
            'y': data_diversity[str(i)],
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'simple'
        }, fig_index, 2)
        fig.append_trace({
            'x': pd.Series(range(len(data_diversity[str(i) + '_dup'].dropna()))),
            'y': data_diversity[str(i) + '_dup'],
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'dup'
        }, fig_index, 2)
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = max(fig_index, 1) * 400
    return fig


# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
