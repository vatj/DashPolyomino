
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

from app import app, file_names, extract_parameters, PartitionPhenotype

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
        dcc.Dropdown(id='dropdown-file-set-metric-isomorphic',
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
        id='datatable-set-distribution-isomorphic'
    ),
    html.Div(id='selected-indexes'),
    html.Div(
    [dcc.Dropdown(id='dropdown-metrics-distribution-isomorphic',
    options=[{'label': metric, 'value': metric} for metric in genome_names[2:-3]],
    value=genome_names[2], multi=False, placeholder='Metrics :' + genome_names[2]),
    dcc.Dropdown(id='dropdown-barmode-isomorphic',
    options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
    value='stack', multi=False, placeholder='Barmode')],
    style={'width': '200px'}),
    dcc.Graph(
        id='graph-set-distribution-isomorphic'
    ),
], className="container")

def index_isomorphic(index, df_set, file_genome):
    df_genome = dict_df_genome[file_genome][dict_df_genome[file_genome]['pIDs'] == df_set['pIDs'][index]].copy()
    partition = PartitionPhenotype(list(eval(df_set['originals'][index])))
    # partition = PartitionPhenotype(df_genome.original.unique().apply(lambda x: eval(x)))
    # print(partition.__repr__() + '\n')
    # print(df_genome.original.unique().__repr__() + '\n')
    df_genome['Iso_index'] = df_genome['original'].apply(lambda x: partition[str(eval(x))])
    return df_genome

@app.callback(
    Output('datatable-set-distribution-isomorphic', 'rows'),
    [Input('dropdown-file-set-metric-isomorphic', 'value')])
def update_displayed_file(file):
    return dict_df_set[file].round(3).to_dict('records')

@app.callback(
    Output('graph-set-distribution-isomorphic', 'figure'),
    [Input('datatable-set-distribution-isomorphic', 'rows'),
     Input('datatable-set-distribution-isomorphic', 'selected_row_indices'),
     Input('dropdown-metrics-distribution-isomorphic', 'value'),
     Input('dropdown-file-set-metric-isomorphic', 'value'),
     Input('dropdown-barmode-isomorphic', 'value')])
def update_figure(rows, selected_row_indices, metric, file, barmode):
    dff = pd.DataFrame(rows)
    parameters = extract_parameters(file)
    genome_file = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
    # titles = []
    # for i in (selected_row_indices or []):
    #     titles.append(metric + ' histogram for genome representants <br> of pID set : ' + dff['pIDs'][i])
    #     titles.append('Diversity tracking for pID set : ' + dff['pIDs'][i])
    fig = plotly.tools.make_subplots(
        rows= max(1, len(selected_row_indices)), cols=2,
        # subplot_titles=titles,
        shared_xaxes=False)
    fig_index = 0
    for row_index in (selected_row_indices or []):
        fig_index += 1
        df_genome = index_isomorphic(row_index, dff, genome_file)
        fig.append_trace({
            'x': df_genome[metric],
            'type': 'histogram'
        }, fig_index, 1)
        for iso_index in df_genome.Iso_index.unique():
            fig.append_trace({
                'x': df_genome[df_genome['Iso_index'] == iso_index][metric],
                'type': 'histogram'
            }, fig_index, 2)
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = max(fig_index, 1) * 400
    return fig



#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
