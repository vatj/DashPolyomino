
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

from app import app

parameters = dict()
parameters['ngenes'] = 3
parameters['colours'] = 7
parameters['metric_colours'] = 9
parameters['builds'] = 40
parameters['njiggle'] = 200
parameters['threshold'] = 25

filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V6/experiment/'
set_filename = 'SetMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
set_names = ['srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'analysed', 'total_neutral', 'diversity', 'diversity_tracker', 'pIDs']

df_set = pd.read_csv(filepath + set_filename, sep=" ", header=None, names=set_names)

df_set['diversity_tracker'] = df_set['diversity_tracker'].apply(lambda x: np.array(eval(x)))
df_set['evo'] = df_set['evolvability'] - df_set['rare'] - df_set['loop']
set_names.insert(3, 'evo')
set_names.remove('diversity_tracker')

genome_filename = 'GenomeMetrics_N{ngenes}_C{colours}_T{threshold}_B{builds}_Cx{metric_colours}_J{njiggle}.txt'.format(**parameters)
genome_names = ['genome', 'srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'diversity', 'neutral_weight', 'frequencies', 'pIDs']

df_genome = pd.read_csv(filepath + genome_filename, sep=" ", header=None, names=genome_names)

df_genome['neutral_weight'] = df_genome['neutral_weight'] * parameters['njiggle']
df_genome['evo'] = df_genome['evolvability'] - df_genome['rare'] - df_genome['loop']
genome_names.insert(4, 'evo')


layout = html.Div([
    html.H3('Set Metric Table for {ngenes} genes, {colours} coulours'.format(**parameters)),
    html.P('The metrics have been computed using {metric_colours} colours and \
    each representant is jiggled {njiggle} times. For each seed, the assembly \
    is done {builds} times. The threshold for determinism is set at \
    {threshold}%.'.format(**parameters)),
    dt.DataTable(
        rows=df_set.round(3).to_dict('records'),
        # optional - sets the order of columns
        columns=set_names,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-set-distribution'
    ),
    html.Div(id='selected-indexes'),
    html.Div(
    dcc.Dropdown(id='dropdown-metrics-distribution',
    options=[{'label': metric, 'value': metric} for metric in genome_names[1:-3]],
    value=genome_names[1], multi=False, placeholder='Metrics :' + genome_names[1]),
    style={'width': '200px'}),
    dcc.Graph(
        id='graph-set-distribution'
    ),
], className="container")


@app.callback(
    Output('datatable-set-distribution', 'selected_row_indices'),
    [Input('graph-set-distribution', 'clickData')],
    [State('datatable-set-distribution', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices


@app.callback(
    Output('graph-set-distribution', 'figure'),
    [Input('datatable-set-distribution', 'rows'),
     Input('datatable-set-distribution', 'selected_row_indices'),
     Input('dropdown-metrics-distribution', 'value')])
def update_figure(rows, selected_row_indices, metric):
    data_diversity = pd.DataFrame()
    dff = pd.DataFrame(rows)
    titles = []
    for i in (selected_row_indices or []):
        titles.append(metric + ' histogram for genome representants <br> of pID set : ' + dff['pIDs'][i])
        titles.append('Diversity tracking for pID set : ' + dff['pIDs'][i])
    fig = plotly.tools.make_subplots(
        rows= max(1, len(selected_row_indices)), cols=2,
        subplot_titles=titles,
        shared_xaxes=False)
    fig_index = 0
    for i in (selected_row_indices or []):
        fig_index += 1
        # marker['color'][i] = '#FF851B'
        data_diversity[str(i)] = pd.Series(dff['diversity_tracker'][i])
        fig.append_trace({
            'x': df_genome[df_genome['pIDs'] == dff['pIDs'][i]][metric],
            'type': 'histogram'
        }, fig_index, 1)
        fig.append_trace({
            'x': pd.Series(range(len(data_diversity[str(i)].dropna()))),
            'y': data_diversity[str(i)],
            'type': 'scatter',
            'mode': 'lines+markers'
        }, fig_index, 2)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = max(fig_index, 1) * 400
    return fig

#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
