
# coding: utf-8

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

from app import app, file_names, extract_parameters

import plotly.graph_objs as go

import pandas as pd
import re

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

genome_metric_names = [name for name in file_names if name[:7] == 'GenomeM']
genome_metric_names.extend([name for name in file_names if name[:7] == 'JiggleG'])
genome_metric_names.extend([name for name in file_names if name[:16] == 'JiggleDuplicateG'])

dict_df_genome = dict()
for name in genome_metric_names:
    dict_df_genome[name] = pd.read_csv(filepath + name, sep=" ")

display_names = dict_df_genome[genome_metric_names[0]].columns.values.tolist()
display_names.remove('original')
metric_names = dict_df_genome[genome_metric_names[0]].columns.values.tolist()
metric_names.remove('original')
metric_names.remove('genome')
metric_names.remove('pIDs')

# df_genome = dict_df_genome[genome_metric_names[0]]

layout = html.Div(children=[
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-genome-metric',
            options=[{'label': name, 'value': name} for name in genome_metric_names],
            value=genome_metric_names[0], multi=False, placeholder=genome_metric_names[0]),
        style={'width': '400px'}),
    html.H3('Genome Metrics'),
    dcc.Dropdown(id='dropdown-x-genome', value=metric_names[1],
    options=[{'label': i, 'value': i} for i in metric_names],
    multi=False, placeholder='x-axis, ' + metric_names[1]),
    dcc.Dropdown(id='dropdown-y-genome', value=metric_names[2],
    options=[{'label': i, 'value': i} for i in metric_names],
    multi=False, placeholder='y-axis, ' + metric_names[2]),
    dcc.Dropdown(id='dropdown-pID-genomes',
    options=[{'label': i, 'value': re.escape(i)}
    for i in dict_df_genome[genome_metric_names[0]].pIDs.unique()],
    multi=True, value=re.escape(dict_df_genome[genome_metric_names[0]].pIDs[0]),
    placeholder='Filter by pID set :' + dict_df_genome[genome_metric_names[0]].pIDs[0]),
    dcc.Graph(id='graph-container-genome')
], className="content")

@app.callback(
    Output('dropdown-pID-genome', 'options'),
    [Input('dropdown-file-genome-duplicate', 'value')])
def update_displayed_pID_menu(file):
    return [{'label': i, 'value': re.escape(i)} for i in dict_df_genome[file].pIDs.unique()]

@app.callback(
    Output('dropdown-pID-genome', 'value'),
    [Input('dropdown-file-genome-duplicate', 'value')])
def update_displayed_pID_menu(file):
    return re.escape(dict_df_genome[file].pIDs[0])


@app.callback(
    Output('graph-container-genome', 'figure'),
    [Input('dropdown-x-genome', 'value'),
     Input('dropdown-y-genome', 'value'),
     Input('dropdown-pID-genomes', 'value'),
     Input('dropdown-file-genome-metric', 'value')])
def update_figure_genome(dropdown_x, dropdown_y, dropdown_pIDs, file):
    dff_genome = dict_df_genome[file]
    if dropdown_x is None:
        xaxis = genome_names[1]
    else:
        xaxis = dropdown_x
    if dropdown_y is None:
        yaxis = genome_names[2]
    else:
        yaxis = dropdown_y
    if dropdown_pIDs is None:
        pIDs = re.escape(dff_genome.pIDs[0])
    else:
        pIDs = dropdown_pIDs

    dff_genome = dff_genome[dff_genome.pIDs.str.contains('|'.join(pIDs))]

    traces = []

    traces.append(go.Scatter(
        x=dff_genome[xaxis], y=dff_genome[yaxis], text=dff_genome['genome'],
        mode='markers'))

    return {'data' : traces,
           'layout': go.Layout(
               xaxis={'title' : xaxis}, yaxis={'title' : yaxis},
               hovermode='closest')}
