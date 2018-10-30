
# coding: utf-8


# In[2]:

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import numpy as np
import plotly
from dash.dependencies import Input, Output, State

import pandas as pd
import re

from app import app, hdf_file, file_names, extract_parameters

## Load set metric files
#############################
duplicate_set_names = sorted([name for name in file_names if ('DuplicateSetMetric' in name)])

parameters = extract_parameters(duplicate_set_names[0])
set_name_same = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
parameters['ngenes'] -= 1
set_name_lower = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'

df_set_same = pd.read_csv(filepath + set_name_same, sep=" ")
df_set_lower = pd.read_csv(filepath + set_name_lower, sep=" ")
df_set_dup = pd.read_csv(filepath + duplicate_set_names[0], sep=" ")

display_names = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity', 'neutral_size', 'analysed', 'misclassified', 'pIDs']
metrics = ['srobustness', 'irobustness', 'evolvability', 'meta_evolvability', 'rare', 'unbound', 'diversity']

## Page layout
#############################
layout = html.Div([
    html.H3('Which file do you wish to explore?'),
    html.Div(
        dcc.Dropdown(id='dropdown-file-set-ultimate-duplicate',
            options=[{'label': name, 'value': name} for name in duplicate_set_names],
            value=duplicate_set_names[0], multi=False, placeholder=duplicate_set_names[0]),
        style={'width': '400px'}),
    dcc.Graph(id='graph-set-ultimate-duplication'),
], className="container")


## Interactive functions
#############################

## Update Table with data from desired file
##########################################################
# @app.callback(
#     Output('datatable-set-duplication', 'rows'),
#     [Input('dropdown-file-set-ultimate-duplicate', 'value')])
# def update_displayed_file(file_name):
#     df_set_dup = pd.read_csv(filepath + file_name, sep=" ")
#     # df_set_dup['diversity_tracker'] = df_set_dup['diversity_tracker'].apply(lambda x: np.array(eval(x)))
#     return df_set_dup.round(3).to_dict('records')

## Update Set Table with data from the corresponding ngenes - 1 file
##############################################################################
# @app.callback(
#     Output('datatable-set-bis', 'rows'),
#     [Input('dropdown-file-set-ultimate-duplicate', 'value')])
# def update_displayed_file(file_name):
#     parameters = extract_parameters(file_name)
#     parameters['ngenes'] -= 1
#     set_name = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
#     df_set = pd.read_csv(filepath + set_name, sep=" ")
#     # df_set['diversity_tracker'] = df_set['diversity_tracker'].apply(lambda x: np.array(eval(x)))
#     return df_set.round(3).to_dict('records')

@app.callback(
    Output('graph-set-ultimate-duplication', 'figure'),
    [Input('dropdown-file-set-ultimate-duplicate', 'value')])
def update_figure(file):

    return fig
