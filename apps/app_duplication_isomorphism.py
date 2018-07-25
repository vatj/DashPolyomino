
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

## Load metric files
#############################
duplicate_genome_names = [name[:-4] for name in file_names if ('DuplicateGenomeMetric' in name)]
genome_names = [name[:-4] for name in file_names if ('GenomeMetric' in name)]
duplicate_genome_names.sort()
genome_names.sort()

parameters = extract_parameters(duplicate_genome_names[0])
parameters['ngenes'] -= 1
genome_name = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
sns.set()

with pd.HDFStore(hdf_file) as store:
    default_df = store[genome_name]
    default_df_dup = store[duplicate_genome_names[0]]

metrics = ['srobustness', 'irobustness', 'evolvability', 'diversity', 'rare', 'unbound']
subplot_coord = list(itertools.product(range(1, 4), range(1, 3)))

common_pIDs = sorted(list(set(default_df.pIDs.unique()).intersection(set(default_df_dup.pIDs.unique()))))

## Page layout
#############################
layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-duplicate-isomorphic',
            options=[{'label': name, 'value': name} for name in duplicate_genome_names],
            value=duplicate_genome_names[0], multi=False, placeholder=duplicate_genome_names[0]),
        style={'width': '400px'}),
    html.Div(
        [dcc.Dropdown(id='dropdown-barmode-duplicate-isomorphic',
            options=[{'label': mode, 'value': mode} for mode in ['stack', 'grouped']],
            value='grouped', multi=False, placeholder='Barmode'),
        dcc.Dropdown(id='dropdown-pID-duplicate-isomorphic',
            options=[{'label': pIDs, 'value': pIDs} for pIDs in common_pIDs],
            value=common_pIDs[0], multi=False, placeholder=common_pIDs[0])],
    style={'width': '200px'}),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-set-duplication-isomorphic'
    ),
], className="container")


## Interactive functions
#############################

## Update pIDs options from desired file
##########################################################
@app.callback(
    Output('dropdown-pID-duplicate-isomorphic', 'options'),
    [Input('dropdown-file-set-duplicate-isomorphic', 'value')])
def update_pID_options(file_name):
    parameters = extract_parameters(file_name)
    parameters['ngenes'] -= 1
    genome_name = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)
    with pd.HDFStore(hdf_file) as store:
        df = store[genome_name]
        df_dup = store[file_name]
    common_pIDs = sorted(list(set(df.pIDs.unique()).intersection(set(df_dup.pIDs.unique()))))
    return [{'label': pIDs, 'value': pIDs} for pIDs in common_pIDs]

@app.callback(
    Output('graph-set-duplication-isomorphic', 'figure'),
    [Input('dropdown-pID-duplicate-isomorphic', 'value'),
     Input('dropdown-file-set-duplicate-isomorphic', 'value'),
     Input('dropdown-barmode-duplicate-isomorphic', 'value')])
def update_figure(pID, file, barmode):
    titles = []
    for metric in metrics:
        titles.append('Distribution ' + metric)
    fig = plotly.tools.make_subplots(
        rows=3, cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    parameters = extract_parameters(file)
    # file_genome_dup = 'DuplicateGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)
    parameters['ngenes'] -= 1
    file_genome = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}'.format(**parameters)
    with pd.HDFStore(hdf_file,  mode='r') as store:
        df_genome = store.select(file_genome, where='pIDs == pID')
        df_dup = store.select(file, where='pIDs == pID')
    print(df_genome.head())
    new_colors = ['rgb' + str(rgb) for rgb in sns.color_palette("hls", df_genome.Iso_index.max() + df_dup.Iso_index.max() + 2)]
    for iso_index in df_genome.Iso_index.unique():
        for metric, coord in zip(metrics, subplot_coord):
            fig.append_trace({
                'x': df_genome[df_genome['Iso_index'] == iso_index][metric],
                'type': 'histogram',
                'name': str(df_genome[df_genome['Iso_index'] == iso_index]['original'].unique()[0]),
                'marker': dict(color=new_colors[iso_index]),
                'showlegend': True if metric == 'srobustness' else False
                }, coord[0], coord[1])
    for iso_index in df_dup.Iso_index.unique():
        for metric, coord in zip(metrics, subplot_coord):
            fig.append_trace({
                'x': df_dup[df_dup['Iso_index'] == iso_index][metric],
                'type': 'histogram',
                'name': str(df_dup[df_dup['Iso_index'] == iso_index]['original'].unique()[0]),
                'marker': dict(color=new_colors[iso_index + df_genome.Iso_index.max() + 1]),
                'showlegend': True if metric == 'srobustness' else False
                }, coord[0], coord[1])
    for index, metric in zip(range(1, 7), metrics):
        fig['layout']['xaxis' + str(index)].update(title=metric)
        fig['layout']['yaxis' + str(index)].update(title='Number of genomes')
    fig['layout']['barmode'] = barmode
    fig['layout']['showlegend'] = True
    fig['layout']['height'] = 1200
    fig['layout']['title'] = 'Effect of Gene Duplication on Metric Distributions of pID set : ' + str(pID)
    return fig
