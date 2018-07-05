
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
sns.set()

genome_metric_names = [name for name in file_names if name[:12] == 'GenomeMetric']
genome_metric_names.sort()

dict_df_genome = dict()

for genome_name in genome_metric_names:
    dict_df_genome[genome_name] = pd.read_csv(filepath + genome_name, sep=" ")

genome_names = dict_df_genome[genome_metric_names[0]].columns.values.tolist()
metrics = ['srobustness', 'irobustness', 'evolvability', 'diversity', 'rare', 'unbound']
subplot_coord = list(itertools.product(range(1, 4), range(1, 3)))

layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-genome-metric-simple-isomorphic-all',
            options=[{'label': name, 'value': name} for name in genome_metric_names],
            value=genome_metric_names[0], multi=False, placeholder=genome_metric_names[0]),
        style={'width': '400px'}),
    html.Div(
    dcc.Dropdown(id='dropdown-pID-simple-isomorphic-all',
    options=[{'label': pIDs, 'value': pIDs} for pIDs in dict_df_genome[genome_metric_names[0]]['pIDs'].unique()],
    value=None, multi=False, placeholder='Choose pID set'),
    style={'width': '200px'}),
    html.Div(
    dcc.Dropdown(id='dropdown-simple-barmode-isomorphic-all',
    options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
    value='stack', multi=False, placeholder='Barmode'),
    style={'width': '200px'}),
    html.Div(
    dcc.Graph(id='graph-simple-isomorphic-all'),
    id='graph-container-simple-isomorphic-all', style={'display': 'none'}
    )
], className="container")

def index_isomorphic(pID, file_genome):
    df_genome = dict_df_genome[file_genome][dict_df_genome[file_genome]['pIDs'] == pID].copy()
    partition = PartitionPhenotype(map(eval, list(df_genome.original.unique())))
    df_genome['Iso_index'] = df_genome['original'].apply(lambda x: partition[str(eval(x))])
    return df_genome

@app.callback(
    Output('dropdown-pID-simple-isomorphic-all', 'options'),
    [Input('dropdown-file-genome-metric-simple-isomorphic-all', 'value')])
def update_displayed_file(file):
    return [{'label': pIDs, 'value': pIDs} for pIDs in dict_df_genome[file]['pIDs'].unique()]

@app.callback(
    Output('graph-container-simple-isomorphic-all', 'style'),
    [Input('dropdown-pID-simple-isomorphic-all', 'value')])
def visibility(pID):
    return {'display': 'none'} if pID is None else {}

@app.callback(
    Output('graph-simple-isomorphic-all', 'figure'),
    [Input('dropdown-pID-simple-isomorphic-all', 'value'),
     Input('dropdown-file-genome-metric-simple-isomorphic-all', 'value'),
     Input('dropdown-barmode-isomorphic-all', 'value')])
def update_figure(pID, file, barmode):
    for metric in metrics:
        titles.append(metric + ' histogram for genome representants <br> of pID set : ' + str(pID))
    fig = plotly.tools.make_subplots(
        rows= max(1, 3), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    df_genome = index_isomorphic(pID, file)
    new_colors = ['rgb' + str(rgb) for rgb in sns.color_palette("hls", df_genome.Iso_index.apply(eval).max() + 1)]
    for iso_index in df_genome.Iso_index.unique():
        for metric, coord in zip(metrics, subplot_coord):
            fig.append_trace({
                'x': df_genome[df_genome['Iso_index'] == iso_index][metric],
                'type': 'histogram',
                'name': str(df_genome[df_genome['Iso_index'] == iso_index]['original'].unique()[0]),
                'marker': dict(color=new_colors[eval(iso_index)])
                }, coord[0], coord[1])
    for index, metric in zip(range(6), metrics):
        axis = 'xaxis' + str(index)
        fig['layout'][axis] = dict(title=metric)
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = 1200
    fig['layout']['title'] = 'Histograms for the metrics of genome <br> representants of pID set : ' + str(pID)
    return fig



#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
