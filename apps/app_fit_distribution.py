
# coding: utf-8


# In[2]:

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import plotly
from dash.dependencies import Input, Output, State
import seaborn as sns
import plotly.graph_objs as go
import matplotlib.pyplot as plt

import pandas as pd
import re


from app import app, hdf_file, file_names, extract_parameters, PartitionPhenotype

## Load metric files
#############################
file_names = sorted([name[:-4] for name in file_names if ('GenomeMetric' in name)])

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
sns.set()

with pd.HDFStore(hdf_file) as store:
    default_df = store[file_names[0]]

metrics = ['srobustness', 'irobustness', 'evolvability', 'diversity', 'rare', 'unbound']

## Page layout
#############################
layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-fit-distribution',
            options=[{'label': name, 'value': name} for name in file_names],
            value=file_names[0], multi=False, placeholder=file_names[0]),
        style={'width': '400px'}),
    html.Div(
        [dcc.Dropdown(id='dropdown-metrics-fit-distribution',
            options=[{'label': metric, 'value': metric} for metric in metrics],
            value=metrics[3], multi=False, placeholder=metrics[3]),
        dcc.Dropdown(id='dropdown-pID-fit-distribution',
            options=[{'label': str(pIDs), 'value': pIDs} for pIDs in default_df['pIDs'].unique()],
            value=default_df['pIDs'].unique()[0],
            multi=False, placeholder=default_df['pIDs'].unique()[0]),
        dcc.Dropdown(id='dropdown-genome-fit-distribution',
            options=[{}], value=None, multi=False, placeholder='Genome')],
    style={'width': '400px'}),
    html.Div(id='df-update-fit-distribution'),
    html.Div(
        [dcc.Graph(id='graph-fit-distribution'),
        dcc.RangeSlider(id='xrange-slider-fit-distribution',
            min=0, max=20, step=0.5, value=[5, 15])])
], className="container")


## Interactive functions
#############################

## Update pIDs options from desired file
##########################################################
@app.callback(
    Output('dropdown-pID-fit-distribution', 'options'),
    [Input('dropdown-file-set-fit-distribution', 'value')])
def update_pID_options(file_name):
    with pd.HDFStore(hdf_file) as store:
        df = store[file_name]
    return [{'label': pIDs, 'value': pIDs} for pIDs in df['pIDs'].unique()]

@app.callback(
    Output('df-update-fit-distribution', 'value'),
    [Input('dropdown-pID-fit-distribution', 'value'),
     Input('dropdown-file-set-fit-distribution', 'value')])
def update_df(pID, file):
    with pd.HDFStore(hdf_file,  mode='r') as store:
        df_genome = store.select(file, where='pIDs == pID')
    return df_genome.to_json()

@app.callback(
    Output('dropdown-genome-fit-distribution', 'options'),
    [Input('df-update-fit-distribution', 'value')])
def update_df(df_json):
    df = pd.read_json(df_json)
    originals = df['original'].unique()
    return [{'label': str(genome), 'value': genome} for genome in originals]

@app.callback(
    Output('xrange-slider-fit-distribution', 'min'),
    [Input('df-update-fit-distribution', 'value'),
     Input('dropdown-metrics-fit-distribution', 'value'),
     Input('dropdown-genome-fit-distribution', 'value')])
def update_figure(df_json, metric, genome):
    return pd.read_json(df_json)[metric].min()

@app.callback(
    Output('xrange-slider-fit-distribution', 'max'),
    [Input('df-update-fit-distribution', 'value'),
     Input('dropdown-metrics-fit-distribution', 'value'),
     Input('dropdown-genome-fit-distribution', 'value')])
def update_figure(df_json, metric, genome):
    return pd.read_json(df_json)[metric].max()


@app.callback(
    Output('xrange-slider-fit-distribution', 'step'),
    [Input('xrange-slider-fit-distribution', 'min'),
     Input('xrange-slider-fit-distribution', 'max')])
def update_figure(min, max):
    return (max - min)/100

@app.callback(
    Output('xrange-slider-fit-distribution', 'value'),
    [Input('xrange-slider-fit-distribution', 'min'),
     Input('xrange-slider-fit-distribution', 'max')])
def update_figure(min, max):
    return [min, max]

@app.callback(
    Output('graph-fit-distribution', 'figure'),
    [Input('df-update-fit-distribution', 'value'),
     Input('dropdown-metrics-fit-distribution', 'value'),
     Input('dropdown-genome-fit-distribution', 'value'),
     Input('xrange-slider-fit-distribution', 'value')])
def update_figure(df_json, metric, genome, x_range):
    if (genome is None):
        return plotly.tools.make_subplots(rows=1, cols=1, shared_xaxes=False)
    df = pd.read_json(df_json)
    plot_df = df[df['original'] == genome][metric]
    plot_df = plot_df[plot_df <= x_range[1]]
    plot_df = plot_df[plot_df >= x_range[0]]
    plot_df.describe()
    if plot_df.empty:
        return plotly.tools.make_subplots(rows=1, cols=1, shared_xaxes=False)
    fig, ax = plt.subplots()
    sns.distplot(plot_df, ax=ax)
    plotly_fig = plotly.tools.mpl_to_plotly(fig)
    plotly_fig['layout']['xaxis1']['showgrid'] = True
    plotly_fig['layout']['xaxis1']['range'] = True
    plotly_fig['layout']['yaxis1']['showgrid'] = True
    plotly_fig['layout']['yaxis1']['autorange'] = True
    return plotly_fig
