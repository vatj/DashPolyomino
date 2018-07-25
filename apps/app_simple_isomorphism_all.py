
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

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
sns.set()

genome_metric_names = [name[:-4] for name in file_names if name[:12] == 'GenomeMetric']
genome_metric_names.sort()

with pd.HDFStore(hdf_file) as store:
    default_df = store[genome_metric_names[0]]

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
    options=[{'label': pIDs, 'value': str(pIDs)} for pIDs in [None]],
    value='{(2, 0)}', multi=False, placeholder='Choose pID set : {(2,0)}'),
    style={'width': '200px'}),
    html.Div(
    dcc.Dropdown(id='dropdown-barmode-simple-isomorphic-all',
    options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
    value='stack', multi=False, placeholder='Barmode'),
    style={'width': '200px'}),
    dcc.Graph(id='graph-simple-isomorphic-all')
], className="container")

@app.callback(
    Output('dropdown-pID-simple-isomorphic-all', 'options'),
    [Input('dropdown-file-genome-metric-simple-isomorphic-all', 'value')])
def update_pID_options(file_name):
    if file_name is None:
        return {}
    else:
        with pd.HDFStore(hdf_file, mode='r') as store:
            df = store.select(file_name, "columns=['pIDs', 'Iso_index']")
        iso_rank = df.groupby(by='pIDs', sort=False).max()['Iso_index'].tolist()
        return [{'label': pID + ' ' + str(iso + 1), 'value': pID} for pID, iso in zip(df.pIDs.unique(), iso_rank)]

@app.callback(
    Output('graph-simple-isomorphic-all', 'figure'),
    [Input('dropdown-pID-simple-isomorphic-all', 'value'),
     Input('dropdown-file-genome-metric-simple-isomorphic-all', 'value'),
     Input('dropdown-barmode-simple-isomorphic-all', 'value')])
def update_figure(pID, file_name, barmode):
    titles = []
    for metric in metrics:
        titles.append('Distribution ' + metric)
    fig = plotly.tools.make_subplots(
        rows= max(1, 3), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    print(pID)
    with pd.HDFStore(hdf_file,  mode='r') as store:
        df_genome = store.select(file_name, where='pIDs == pID')
    print(df_genome.head())
    new_colors = ['rgb' + str(rgb) for rgb in sns.color_palette("hls", df_genome.Iso_index.max() + 1)]
    for iso_index in df_genome.Iso_index.unique():
        for metric, coord in zip(metrics, subplot_coord):
            fig.append_trace({
                'x': df_genome[df_genome['Iso_index'] == iso_index][metric],
                'type': 'histogram',
                'name': str(df_genome[df_genome['Iso_index'] == iso_index]['original'].unique()[0]),
                'marker': dict(color=new_colors[iso_index]),
                'showlegend': True if metric == 'srobustness' else False
                }, coord[0], coord[1])
    for index, metric in zip(range(1, 7), metrics):
        fig['layout']['xaxis' + str(index)].update(title=metric)
        fig['layout']['yaxis' + str(index)].update(title='Number of genomes')
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = 1200
    fig['layout']['title'] = 'Metric Distributions of pID set : ' + str(pID)
    return fig
