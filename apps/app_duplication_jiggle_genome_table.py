# coding: utf-8

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import numpy as np
import plotly
from dash.dependencies import Input, Output, State

import pandas as pd
import re

from app import app, file_names, extract_parameters

jiggle_genome_names = [name for name in file_names if name[:7] == 'JiggleG']
duplicate_genome_names = [name for name in file_names if name[:16] == 'JiggleDuplicateG']
jiggle_genome_names.sort()
duplicate_genome_names.sort()

dict_df_genome_jiggle = dict()
dict_df_genome_dup = dict()

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

for name_jiggle, name_duplicate in zip(jiggle_genome_names, duplicate_genome_names):
    dict_df_genome_jiggle[name_jiggle] = pd.read_csv(filepath + name_jiggle, sep=" ")
    dict_df_genome_dup[name_duplicate] = pd.read_csv(filepath + name_duplicate, sep=" ")

display_names = dict_df_genome_jiggle[jiggle_genome_names[0]].columns.values.tolist()
display_names.remove('original')

layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-genome-duplicate',
            options=[{'label': name, 'value': name} for name in jiggle_genome_names],
            value=jiggle_genome_names[0], multi=False, placeholder=jiggle_genome_names[0]),
        style={'width': '400px'}),
    html.H3('Simple Genome Metric Table'),
    dt.DataTable(
        rows=dict_df_genome_jiggle[jiggle_genome_names[0]].round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-polyomino-jiggle'
    ),
    html.H3('Duplicate Genome Metric Table'),
    dt.DataTable(
        rows=dict_df_genome_dup[duplicate_genome_names[0]].round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=display_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-polyomino-duplicate-jiggle'
    )
], className="container")

@app.callback(
    Output('datatable-polyomino-jiggle', 'rows'),
    [Input('dropdown-file-genome-duplicate', 'value')])
def update_displayed_file(file):
    return dict_df_genome_jiggle[file].round(3).to_dict('records')

@app.callback(
    Output('datatable-polyomino-duplicate-jiggle', 'rows'),
    [Input('datatable-polyomino-jiggle', 'rows'),
     Input('datatable-polyomino-jiggle', 'selected_row_indices'),
     Input('dropdown-file-genome-duplicate', 'value')])
def update_duplicate_table(rows, selected_row_indices, jiggle_file):
    parameters = extract_parameters(jiggle_file)
    parameters['ngenes'] += 1
    duplicate_name = 'JiggleDuplicateGenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
    list_genome=[]
    for i in (selected_row_indices or []):
        list_genome.append(dict_df_genome_jiggle[jiggle_file]['genome'][i][1:-1])
    new_df=dict_df_genome_dup[duplicate_name]
    new_df = new_df[new_df.genome.str.contains('|'.join(list_genome))]
    return new_df.round(3).to_dict('records')
