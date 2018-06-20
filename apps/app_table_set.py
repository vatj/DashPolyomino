import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import re

from app import app

ngenes = 3
colours = 7
metric_colours = 9
filepath = 'http://files.tcm.phy.cam.ac.uk/~vatj2/Polyominoes/data/gpmap/V4/exhaustive/'
set_filename = "SetMetrics_N" + format(ngenes) + "_C" + format(colours) + "_Cx" + format(metric_colours) + ".txt"
set_names = ['srobustness', 'interrobustness', 'evolvability', 'rare', 'loop', 'analysed', 'total_neutral', 'diversity', 'pIDs']

df_set = pd.read_csv(filepath + set_filename, sep=" ", header=None, names=set_names)

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
    html.H3(children='Set Metrics DataFrame'),
    dcc.Dropdown(id='dropdown-set', options=[
        {'label': i, 'value': re.escape(i)} for i in df_set.pIDs.unique()
    ], multi=True, placeholder='Filter by pID set'),
    dcc.Slider(
        id='max-row-set',
        min=0,
        max=len(df_set),
        value=10,
        step=1
#         marks={str(rows): str(rows) for rows in range(0, len(df_set), int(len(df_set) / 5))}
    ),
    html.Div(id='table-container-set'),
    dcc.Link('Go to Genome Table', href='/apps/app_table_genome')
])

@app.callback(
    Output('table-container-set', 'children'),
    [Input('dropdown-set', 'value'),
     Input('max-row-set', 'value')])
def display_table(dropdown_value, max_row_value):
    if dropdown_value is None:
        return generate_table(df_set.round(3), max_row_value)

    dff_set = df_set[df_set.pIDs.str.contains('|'.join(dropdown_value))]
    return generate_table(dff_set.round(3), max_row_value)

@app.callback(
    Output('max-row-set', 'max'),
    [Input('dropdown-set', 'value')])
def max_length_set(dropdown_value):
    if dropdown_value is None:
        return len(df_set)

    dff_set = df_set[df_set.pIDs.str.contains('|'.join(dropdown_value))]
    return len(dff_set)
