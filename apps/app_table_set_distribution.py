
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

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

set_metric_names = [name for name in file_names if name[:9] == 'SetMetric']
genome_metric_names = [name for name in file_names if name[:12] == 'GenomeMetric']
set_metric_names.sort(), genome_metric_names.sort()

dict_df_set = dict()
dict_df_genome = dict()

for set_name, genome_name in zip(set_metric_names, genome_metric_names):
    dict_df_set[set_name] = pd.read_csv(filepath + set_name, sep=" ")
    dict_df_set[set_name]['diversity_tracker'] = dict_df_set[set_name]['diversity_tracker'].apply(lambda x: np.array(eval(x)))
    dict_df_genome[genome_name] = pd.read_csv(filepath + genome_name, sep=" ")

display_names = dict_df_set[set_metric_names[0]].columns.values.tolist()
display_names.remove('diversity_tracker')
display_names.remove('misclassified_details')
display_names.remove('originals')

genome_names = dict_df_genome[genome_metric_names[0]].columns.values.tolist()

# parameters = extract_parameters(set_metric_names[0])

layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-metric',
            options=[{'label': name, 'value': name} for name in set_metric_names],
            value=set_metric_names[0], multi=False, placeholder=set_metric_names[0]),
        style={'width': '400px'}),
    # html.H3('Set Metric Table for {ngenes} genes, {colours} coulours'.format(**parameters)),
    # html.P('The metrics have been computed using {metric_colours} colours and \
    # each representant is jiggled {njiggle} times. For each seed, the assembly \
    # is done {builds} times. The threshold for determinism is set at \
    # {threshold}%.'.format(**parameters)),
    dt.DataTable(
        rows=dict_df_set[set_metric_names[0]].round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-distribution'
    ),
    html.Div(id='selected-indexes'),
    html.Div(
    dcc.Dropdown(id='dropdown-metrics-distribution',
    options=[{'label': metric, 'value': metric} for metric in genome_names[2:-3]],
    value=genome_names[2], multi=False, placeholder='Metrics :' + genome_names[2]),
    style={'width': '200px'}),
    dcc.Graph(
        id='graph-set-distribution'
    ),
], className="container")

@app.callback(
    Output('datatable-set-distribution', 'rows'),
    [Input('dropdown-file-set-metric', 'value')])
def update_displayed_file(file):
    return dict_df_set[file].round(3).to_dict('records')

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
    genome_file = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
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
        # marker['color'][i] = '#FF851B'
        data_diversity[str(i)] = pd.Series(dff['diversity_tracker'][i])
        fig.append_trace({
            'x': dict_df_genome[genome_file][dict_df_genome[genome_file]['pIDs'] == dff['pIDs'][i]][metric],
            'type': 'histogram'
        }, fig_index, 1)
        fig.append_trace({
            'x': pd.Series(range(len(data_diversity[str(i)].dropna()))),
            'y': data_diversity[str(i)],
            'type': 'scatter',
            'mode': 'lines+markers'
        }, fig_index, 2)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = max(fig_index, 1) * 400
    return fig

#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
