
# coding: utf-8


# In[2]:

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import numpy as np
import plotly
from dash.dependencies import Input, Output, State
import itertools
import seaborn as sns
import plotly.graph_objs as go


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
metrics = ['srobustness', 'irobustness', 'evolvability', 'diversity', 'rare', 'unbound']
subplot_coord = list(itertools.product(range(1, 4), range(1, 3)))
sns.set()

# parameters = extract_parameters(set_metric_names[0])

layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-metric-isomorphic-all',
            options=[{'label': name, 'value': name} for name in set_metric_names],
            value=set_metric_names[0], multi=False, placeholder=set_metric_names[0]),
        style={'width': '400px'}),
    dt.DataTable(
        rows=dict_df_set[set_metric_names[0]].round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-distribution-isomorphic-all'
    ),
    html.Div(id='selected-indexes'),
    html.Div(
    # [dcc.Dropdown(id='dropdown-metrics-distribution-isomorphic-all',
    # options=[{'label': metric, 'value': metric} for metric in genome_names[2:-3]],
    # value=genome_names[2], multi=False, placeholder='Metrics :' + genome_names[2]),
    dcc.Dropdown(id='dropdown-barmode-isomorphic-all',
    options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
    value='stack', multi=False, placeholder='Barmode'),#],
    style={'width': '200px'}),
    dcc.Graph(
        id='graph-set-distribution-isomorphic-all'
    ),
], className="container")

def index_isomorphic(index, df_set, file_genome):
    df_genome = dict_df_genome[file_genome][dict_df_genome[file_genome]['pIDs'] == df_set['pIDs'][index]].copy()
    partition = PartitionPhenotype(list(eval(df_set['originals'][index])))
    df_genome['Iso_index'] = df_genome['original'].apply(lambda x: partition[str(eval(x))])
    return df_genome

@app.callback(
    Output('datatable-set-distribution-isomorphic-all', 'rows'),
    [Input('dropdown-file-set-metric-isomorphic-all', 'value')])
def update_displayed_file(file):
    return dict_df_set[file].round(3).to_dict('records')

@app.callback(
    Output('graph-set-distribution-isomorphic-all', 'figure'),
    [Input('datatable-set-distribution-isomorphic-all', 'rows'),
     Input('datatable-set-distribution-isomorphic-all', 'selected_row_indices'),
     Input('dropdown-file-set-metric-isomorphic-all', 'value'),
     Input('dropdown-barmode-isomorphic-all', 'value')])
def update_figure(rows, selected_row_indices, file, barmode):
    dff = pd.DataFrame(rows)
    parameters = extract_parameters(file)
    genome_file = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
    titles = []
    for i in (selected_row_indices or []):
        for metric in metrics:
            titles.append(metric + ' histogram for genome representants <br> of pID set : ' + dff['pIDs'][i])
    fig = plotly.tools.make_subplots(
        rows= max(1, 3 * len(selected_row_indices)), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    fig_index = -3
    for row_index in (selected_row_indices or []):
        fig_index += 3
        df_genome = index_isomorphic(row_index, dff, genome_file)
        new_colors = ['rgb' + str(rgb) for rgb in sns.color_palette("hls", df_genome.Iso_index.apply(eval).max() + 1)]
        for iso_index in df_genome.Iso_index.unique():
            for metric, coord in zip(metrics, subplot_coord):
                fig.append_trace({
                    'x': df_genome[df_genome['Iso_index'] == iso_index][metric],
                    'type': 'histogram',
                    'name': str(df_genome[df_genome['Iso_index'] == iso_index]['original'].unique()),
                    'marker': dict(color=new_colors[eval(iso_index)])
                    }, coord[0] + fig_index, coord[1])
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = max(fig_index, 1) * 1200
    return fig



#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
