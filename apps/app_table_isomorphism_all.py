
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

from app import app, hdf_file, file_names, extract_parameters, PartitionPhenotype

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V8/experiment/'

set_metric_names = [name for name in file_names if name[:9] == 'SetMetric']
genome_metric_names = [name for name in file_names if name[:12] == 'GenomeMetric']
set_metric_names.sort(), genome_metric_names.sort()

df = pd.read_csv(filepath + set_metric_names[0], sep=" ")
df['diversity_tracker'] = df['diversity_tracker'].apply(lambda x: np.array(eval(x)))

# display_names = ['srobustness', 'irobustness', 'evolvability', 'ŕobust_evolvability', 'complex_evolvability', 'rare', 'unbound', 'diversity', 'neutral_size', 'analysed', 'misclassified', 'pIDs']
display_names = ['srobustness', 'irobustness', 'evolvability',  'robust_evolvability', 'complex_evolvability', 'rare', 'unbound', 'complex_diversity', 'diversity', 'pIDs']
metrics = ['srobustness', 'irobustness', 'evolvability',  'complex_diversity', 'diversity', 'robust_evolvability', 'complex_evolvability', 'rare', 'unbound']

subplot_coord = list(itertools.product(range(1, 5), range(1, 3)))
sns.set()

layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-metric-isomorphic-all',
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
        id='datatable-set-distribution-isomorphic-all'
    ),
    html.Div(id='selected-indexes'),
    html.Div(
    dcc.Dropdown(id='dropdown-barmode-isomorphic-all',
    options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
    value='stack', multi=False, placeholder='Barmode'),
    style={'width': '200px'}),
    dcc.Graph(
        id='graph-set-distribution-isomorphic-all'
    ),
], className="container")

@app.callback(
    Output('datatable-set-distribution-isomorphic-all', 'rows'),
    [Input('dropdown-file-set-metric-isomorphic-all', 'value')])
def update_displayed_file(file_name):
    df = pd.read_csv(filepath + file_name, sep=" ")
    df['diversity_tracker'] = df['diversity_tracker'].apply(lambda x: np.array(eval(x)))
    return df.round(3).to_dict('records')


@app.callback(
    Output('graph-set-distribution-isomorphic-all', 'figure'),
    [Input('datatable-set-distribution-isomorphic-all', 'rows'),
     Input('datatable-set-distribution-isomorphic-all', 'selected_row_indices'),
     Input('dropdown-file-set-metric-isomorphic-all', 'value'),
     Input('dropdown-barmode-isomorphic-all', 'value')])
def update_figure(rows, selected_row_indices, file_name, barmode):
    dff = pd.DataFrame(rows)
    parameters = extract_parameters(file_name)
    genome_file = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}_Iso'.format(**parameters)
    titles = []
    for row_index in (selected_row_indices or []):
        for metric in metrics:
            titles.append('Isomorphic ' + metric + ' Distribution of pID set : ' + str(eval(dff['pIDs'][row_index])))
    fig = plotly.tools.make_subplots(
        rows=max(4, 4 * len(selected_row_indices)), cols=2,
        # subplot_titles=titles,
        shared_xaxes=False)
    fig_index = -4
    for row_index in (selected_row_indices or []):
        fig_index += 4
        pID = str(eval(dff['pIDs'][row_index]))
        with pd.HDFStore(hdf_file,  mode='r') as store:
            df_genome = store.select(genome_file, where='pIDs == pID')
        new_colors = ['rgb' + str(rgb) for rgb in sns.color_palette("hls", df_genome.Iso_index.max() + 1)]
        for iso_index in df_genome.Iso_index.unique():
            for metric, coord in zip(metrics, subplot_coord):
                fig.append_trace({
                    'x': df_genome[df_genome['Iso_index'] == iso_index][metric],
                    'type': 'histogram',
                    'name': str(df_genome[df_genome['Iso_index'] == iso_index]['original'].unique()[0]),
                    'marker': dict(color=new_colors[iso_index]),
                    'showlegend': True if metric == 'srobustness' else False
                    }, coord[0] + fig_index, coord[1])
    for index, metric in zip(range(1, 9), metrics):
        fig['layout']['xaxis' + str(index)].update(title=metric)
        fig['layout']['yaxis' + str(index)].update(title='Number of genomes')
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = max(fig_index, 1) * 400 * 4
    return fig



#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
