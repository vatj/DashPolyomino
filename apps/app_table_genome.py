
# coding: utf-8


# In[2]:

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import re

from app import app

ngenes = 3
colours = 7
metric_colours = 9
filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V4/exhaustive/threshold95p/'
genome_filename = "GenomeMetrics_N" + format(ngenes) + "_C" + format(colours) + "_Cx" + format(metric_colours) + ".txt"
genome_names = ['genome', 'srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'diversity', 'neutral_weight', 'pIDs']

df_genome = pd.read_csv(filepath + genome_filename, sep=" ", header=None, names=genome_names)

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


layout = html.Div(children=[
    html.H3(children='Genome Metrics DataFrame'),
    dcc.Dropdown(id='dropdown-genome', options=[
        {'label': i, 'value': re.escape(i)} for i in df_genome.pIDs.unique()
    ], multi=True, placeholder='Filter by pID set'),
    dcc.Slider(
        id='max-row-genome',
        min=0,
        max=len(df_genome),
        value=10,
        step=1
#         marks={str(rows): str(rows) for rows in range(0, len(df_genome), int(len(df_genome) / 5))}
    ),
    html.Div(id='table-container-genome'),
    dcc.Link('Go to Set Table', href='/apps/app_table_set')
])

@app.callback(
    Output('table-container-genome', 'children'),
    [Input('dropdown-genome', 'value'),
     Input('max-row-genome', 'value')])
def display_table(dropdown_value, max_row_value):
    if dropdown_value is None:
        return generate_table(df_genome.round(3), max_row_value)

    dff_genome = df_genome[df_genome.pIDs.str.contains('|'.join(dropdown_value))]
    return generate_table(dff_genome.round(3), max_row_value)

@app.callback(
    Output('max-row-genome', 'max'),
    [Input('dropdown-genome', 'value')])
def max_length_genome(dropdown_value):
    if dropdown_value is None:
        return len(df_genome)

    dff_genome = df_genome[df_genome.pIDs.str.contains('|'.join(dropdown_value))]
    return len(dff_genome)

#
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#
# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8080, debug=True)
