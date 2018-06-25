
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

from app import app, file_names, extract_parameters

## Load set metric files
#############################
jiggle_set_names = [name for name in file_names if name[:7] == 'JiggleS']
duplicate_set_names = [name for name in file_names if name[:16] == 'JiggleDuplicateS']
jiggle_set_names.sort()
duplicate_set_names.sort()

dict_df_set_jiggle = dict()
dict_df_set_dup = dict()

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

for name_jiggle, name_duplicate in zip(jiggle_set_names, duplicate_set_names):
    dict_df_set_jiggle[name_jiggle] = pd.read_csv(filepath + name_jiggle, sep=" ")
    dict_df_set_jiggle[name_jiggle]['diversity_tracker'] = (dict_df_set_jiggle[name_jiggle]['diversity_tracker']).apply(lambda x: np.array(eval(x)))
    dict_df_set_dup[name_duplicate] = pd.read_csv(filepath + name_duplicate, sep=" ")
    dict_df_set_dup[name_duplicate]['diversity_tracker'] = (dict_df_set_dup[name_duplicate]['diversity_tracker']).apply(lambda x: np.array(eval(x)))

display_names = dict_df_set_jiggle[jiggle_set_names[0]].columns.values.tolist()
display_names.remove('diversity_tracker')
display_names.remove('misclassified_details')
display_names.remove('originals')

# Load genome metric files
#############################
jiggle_genome_names = [name for name in file_names if name[:7] == 'JiggleG']
duplicate_genome_names = [name for name in file_names if name[:16] == 'JiggleDuplicateG']
jiggle_genome_names.sort()
duplicate_genome_names.sort()

dict_df_genome_jiggle = dict()
dict_df_genome_dup = dict()

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

for name_jiggle, name_duplicate in zip(jiggle_genome_names, duplicate_genome_names):
    dict_df_genome_jiggle[name_jiggle] = pd.read_csv(filepath + name_jiggle, sep=" ")
    dict_df_genome_dup[name_duplicate] = pd.read_csv(filepath + name_duplicate, sep=" ")

genome_names = dict_df_genome_jiggle[jiggle_genome_names[0]].columns.values.tolist()

## Page layout
#############################
layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-duplicate',
            options=[{'label': name, 'value': name} for name in jiggle_set_names],
            value=jiggle_set_names[0], multi=False, placeholder=jiggle_set_names[0]),
        style={'width': '400px'}),
    html.H3('Simple Set Metric Table'),
    dt.DataTable(
        rows=dict_df_set_jiggle[jiggle_set_names[0]].round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-jiggle'
    ),
    html.H3('Duplicate Set Metric Table'),
    dt.DataTable(
        rows=dict_df_set_dup[duplicate_set_names[0]].round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-duplicate-jiggle'
    ),
    html.Div(
    dcc.Dropdown(id='dropdown-set-metrics-duplicate',
    options=[{'label': metric, 'value': metric} for metric in genome_names[2:-3]],
    value=genome_names[2], multi=False, placeholder='Metrics :' + genome_names[2]),
    style={'width': '200px'}),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-set-duplicate-jiggle'
    ),
], className="container")


## Interactive functions
#############################

## Update Table with data from desired file
##########################################################
@app.callback(
    Output('datatable-set-jiggle', 'rows'),
    [Input('dropdown-file-set-duplicate', 'value')])
def update_displayed_file(file):
    return dict_df_set_jiggle[file].round(3).to_dict('records')

## Update Duplicate Table with data from the corresponding duplicate file
############################################################################
@app.callback(
    Output('datatable-set-duplicate-jiggle', 'rows'),
    [Input('dropdown-file-set-duplicate', 'value')])
def update_duplicate_table_with_displayed_file(jiggle_file):
    parameters = extract_parameters(jiggle_file)
    parameters['ngenes'] += 1
    duplicate_name = 'JiggleDuplicateSetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
    return dict_df_set_dup[duplicate_name].round(3).to_dict('records')

@app.callback(
    Output('graph-set-duplicate-jiggle', 'figure'),
    [Input('datatable-set-jiggle', 'rows'),
     Input('datatable-set-duplicate-jiggle', 'rows'),
     Input('datatable-set-jiggle', 'selected_row_indices'),
     Input('dropdown-set-metrics-duplicate', 'value'),
     Input('dropdown-file-set-duplicate', 'value')])
def update_figure(rows_jiggle, rows_dup, selected_row_indices, metric, file):
    data_diversity = pd.DataFrame()
    dff = pd.DataFrame(rows_jiggle)
    dff_dup = pd.DataFrame(rows_dup)
    parameters = extract_parameters(file)
    file_genome_jiggle = 'JiggleGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
    parameters['ngenes'] += 1
    file_genome_dup = 'JiggleDuplicateGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
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
            'x': dict_df_genome_jiggle[file_genome_jiggle][dict_df_genome_jiggle[file_genome_jiggle]['pIDs'] == dff['pIDs'][i]][metric],
            'type': 'histogram',
            'name': 'simple'
        }, fig_index, 1)
        fig.append_trace({
            'x': dict_df_genome_dup[file_genome_dup][dict_df_genome_dup[file_genome_dup]['pIDs'] == dff['pIDs'][i]][metric],
            'type': 'histogram',
            'name': 'dup'
        }, fig_index, 1)
        data_diversity[str(i)] = pd.Series(dff['diversity_tracker'][i])
        df_temp = dff_dup[dff_dup['pIDs'] == (dff['pIDs'][i])]
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
