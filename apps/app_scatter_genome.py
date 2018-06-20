
# coding: utf-8

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

from app import app

import plotly.graph_objs as go

import pandas as pd
import re

ngenes = 3
colours = 7
metric_colours = 9
filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V4/exhaustive/threshold95p/'
genome_filename = "GenomeMetrics_N" + format(ngenes) + "_C" + format(colours) + "_Cx" + format(metric_colours) + ".txt"
genome_names = ['genome', 'srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'diversity', 'neutral_weight', 'pIDs']


df_genome = pd.read_csv(filepath + genome_filename, sep=" ", header=None, names=genome_names)


layout = html.Div(children=[
    html.H3(children='Genome Metrics'),
    dcc.Dropdown(id='dropdown-x-genome', options=[
        {'label': i, 'value': i} for i in df_genome.columns.values[1:-1]
    ], multi=False, placeholder='x-axis, ' + genome_names[1]),
    dcc.Dropdown(id='dropdown-y-genome', options=[
        {'label': i, 'value': i} for i in df_genome.columns.values[1:-1]
    ], multi=False, placeholder='y-axis, ' + genome_names[2]),
    dcc.Dropdown(id='dropdown-genome', options=[
        {'label': i, 'value': re.escape(i)} for i in df_genome.pIDs.unique()
    ], multi=True, placeholder='Filter by pID set :' + df_genome.pIDs[11]),
    dcc.Graph(id='graph-container-genome'),
    dcc.Link('Go to Set Scatter', href='/apps/app_scatter_set')
], className="content")

@app.callback(
    Output('graph-container-genome', 'figure'),
    [Input('dropdown-x-genome', 'value'),
     Input('dropdown-y-genome', 'value'),
     Input('dropdown-genome', 'value')])
def update_figure_genome(dropdown_x, dropdown_y, dropdown_pIDs):
    if dropdown_x is None:
        xaxis = genome_names[1]
    else:
        xaxis = dropdown_x
    if dropdown_y is None:
        yaxis = genome_names[2]
    else:
        yaxis = dropdown_y
    if dropdown_pIDs is None:
        pIDs = re.escape(df_genome.pIDs[11])
    else:
        pIDs = dropdown_pIDs
        print(pIDs)

    dff_genome = df_genome[df_genome.pIDs.str.contains('|'.join(pIDs))]

    traces = []

    traces.append(go.Scatter(
        x=dff_genome[xaxis], y=dff_genome[yaxis], text=dff_genome['pIDs'],
        mode='markers'))

    return {'data' : traces,
           'layout': go.Layout(
               xaxis={'title' : xaxis}, yaxis={'title' : yaxis},
               hovermode='closest')}
