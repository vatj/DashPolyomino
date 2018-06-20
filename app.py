import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import pandas as pd
import re

from dash.dependencies import Input, Output

os.nice(15)

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions = True

# from apps import app_table_set, app_table_genome
from apps import app_scatter_set, app_scatter_genome
from apps import app_table_set_new, app_table_genome_new

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    html.Div(dcc.Link('Go to Set Table', href='/apps/app_table_set_new')),
    html.Div(dcc.Link('Go to Genome Table', href='/apps/app_table_genome_new')),
    html.Div(dcc.Link('Go to Set scatter plot', href='/apps/app_scatter_set')),
    html.Div(dcc.Link('Go to Genome scatter plot', href='/apps/app_scatter_genome'))
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app_table_set_new':
         return app_table_set_new.layout
    elif pathname == '/apps/app_table_genome_new':
         return app_table_genome_new.layout
    # elif pathname == '/apps/app_table_genome':
    #      return app_table_genome.layout
    elif pathname == '/apps/app_scatter_set':
         return app_scatter_set.layout
    elif pathname == '/apps/app_scatter_genome':
         return app_scatter_genome.layout
    else:
        return '404'

app.css.append_css({"external_url": "http://files.tcm.phy.cam.ac.uk/~vatj2/assets/css/main.css"})

# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8031, debug=True)
