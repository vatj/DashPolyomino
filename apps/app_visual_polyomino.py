
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import plotly
from dash.dependencies import Input, Output, State
import seaborn as sns
import plotly.graph_objs as go

import pandas as pd
import re

from app import app, import_phenotypes

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
file_name = filepath + 'PhenotypeTable.txt'

table = import_phenotypes(file_name)

## Page layout
#############################
layout = html.Div([
    html.Div(
        dcc.Dropdown(id='dropdown-pIDs-PhenotypeTable-visual',
            options=[{'label': pIDs, 'value': pIDs} for pIDs in table['pIDs']],
            value=[table['pIDs'][0]], multi=True, placeholder=table['pIDs'][0]),
    style={'width': '200px'}),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-PhenotypeTable-visual'
    ),
], className="container")

## Interactive functions
#############################

@app.callback(
    Output('graph-PhenotypeTable-visual', 'figure'),
    [Input('dropdown-pIDs-PhenotypeTable-visual', 'value')])
def update_figure(pIDs):
    traces = []
    for pID in pIDs:
        traces.append(go.Heatmap(z=(table[table['pIDs'] == pID]['visual'].values)[0]))
    return {'data' : traces,
           'layout': go.Layout(hovermode='closest')}
