
# coding: utf-8

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

from app import app

import plotly.graph_objs as go

import pandas as pd
import re

parameters = dict()
parameters['ngenes'] = 3
parameters['colours'] = 7
parameters['metric_colours'] = 9
parameters['builds'] = 10
parameters['njiggle'] = 30
parameters['threshold'] = 50

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V5/meeting/'
genome_filename = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}_Iso.txt'.format(**parameters)
genome_names = ['genome', 'srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'diversity', 'neutral_weight', 'pIDs']

df_genome = pd.read_csv(filepath + genome_filename, sep=" ", header=None, names=genome_names)

df_genome['evo'] = df_genome['evolvability'] - df_genome['rare'] - df_genome['loop']
genome_names.insert(4, 'evo')


layout = html.Div(children=[
    html.H3(children='Genome Metrics'),
    dcc.Dropdown(id='dropdown-x-genome', value=genome_names[1], options=[
        {'label': i, 'value': i} for i in genome_names[1:-1]
    ], multi=False, placeholder='x-axis, ' + genome_names[1]),
    dcc.Dropdown(id='dropdown-y-genome', value=genome_names[2], options=[
        {'label': i, 'value': i} for i in genome_names[1:-1]
    ], multi=False, placeholder='y-axis, ' + genome_names[2]),
    dcc.Dropdown(id='dropdown-genome', options=[
        {'label': i, 'value': re.escape(i)} for i in df_genome.pIDs.unique()
    ], multi=True, value=re.escape(df_genome.pIDs[11]),
     placeholder='Filter by pID set :' + df_genome.pIDs[11]),
    dcc.Graph(id='graph-container-genome')
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
