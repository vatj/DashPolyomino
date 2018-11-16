import matplotlib
matplotlib.use('Agg')
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import re
import json
from scripts.extra import extract_parameters, import_phenotypes
from scripts.graph_methods import PartitionPhenotype

from dash.dependencies import Input, Output

os.nice(15)

app = dash.Dash()
server = app.server
app.config.suppress_callback_exceptions = True

with open("./index.json") as fopen:
    file_names = json.load(fopen)

hdf_file = '/rscratch/vatj2/public_html/Polyominoes/data/gpmap/V8/experiment/Processed_GenomeMetrics.h5'

# from apps import app_table_set, app_table_genome
# from apps import app_scatter_set, app_scatter_genome
# from apps import app_table_set_new, app_table_genome_new
# from apps import app_reproducibility_scatter, app_reproducibility_table
# from apps import app_duplication_jiggle_set_table #, app_duplication_jiggle_genome_table
from apps import app_table_set_distribution, app_table_isomorphism
from apps import app_table_isomorphism_all, app_simple_isomorphism_all
# from apps import app_duplication_set_table, app_duplication_isomorphism
from apps import app_fit_distribution
from apps import app_visual_polyomino


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    html.Div(
    [#html.P(dcc.Link('Go to Set Table', href='/apps/app_table_set_new')),
    #html.P(dcc.Link('Go to Genome Table', href='/apps/app_table_genome_new')),
    # html.P(dcc.Link('Go to Set scatter plot', href='/apps/app_scatter_set')),
    # html.P(dcc.Link('Go to Genome scatter plot', href='/apps/app_scatter_genome')),
    # html.P(dcc.Link('Go to Reproducibility scatter plot', href='/apps/app_reproducibility_scatter')),
    # html.P(dcc.Link('Go to Reproducibility Table', href='/apps/app_reproducibility_table')),
    # html.P(dcc.Link('Go to Duplication Genome Table', href='/apps/app_duplication_jiggle_genome_table')),
    # html.P(dcc.Link('Go to Duplication Set Table', href='/apps/app_duplication_jiggle_set_table')),
    # html.P(dcc.Link('Go to Duplication Set Table', href='/apps/app_duplication_set_table')),
    # html.P(dcc.Link('Go to Duplication Isomorphic', href='/apps/app_duplication_isomorphism')),
    html.P(dcc.Link('Go to PhenotypeTable', href='/apps/app_visual_polyomino')),
    html.P(dcc.Link('Go to Set Distribution Table', href='/apps/app_table_set_distribution')),
    html.P(dcc.Link('Go to Isomorphic Table', href='/apps/app_table_isomorphism')),
    html.P(dcc.Link('Go to Isomorphic Table All Metrics', href='/apps/app_table_isomorphism_all')),
    html.P(dcc.Link('Go to Isomorphic All Metrics', href='/apps/app_simple_isomorphism_all')),
    html.P(dcc.Link('Go to Fit Distribution', href='/apps/app_fit_distribution'))],
    style={'align': 'center'})
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    # if pathname == '/apps/app_table_set_new':
    #     return app_table_set_new.layout
    # elif pathname == '/apps/app_table_genome_new':
    #     return app_table_genome_new.layout
    # elif pathname == '/apps/app_scatter_set':
    #     return app_scatter_set.layout
    # elif pathname == '/apps/app_scatter_genome':
    #     return app_scatter_genome.layout
    # elif pathname == '/apps/app_reproducibility_scatter':
    #     return app_reproducibility_scatter.layout
    # elif pathname == '/apps/app_reproducibility_table':
    #     return app_reproducibility_table.layout
    # elif pathname == '/apps/app_duplication_jiggle_genome_table':
    #     return app_duplication_jiggle_genome_table.layout
    # elif pathname == '/apps/app_duplication_jiggle_set_table':
    #     return app_duplication_jiggle_set_table.layout
    # if pathname == '/apps/app_duplication_set_table':
        # return app_duplication_set_table.layout
    # elif pathname == '/apps/app_duplication_isomorphism':
        # return app_duplication_isomorphism.layout
    if pathname == '/apps/app_visual_polyomino':
        return app_visual_polyomino.layout
    elif pathname == '/apps/app_fit_distribution':
        return app_fit_distribution.layout
    elif pathname == '/apps/app_table_set_distribution':
        return app_table_set_distribution.layout
    elif pathname == '/apps/app_table_isomorphism':
        return app_table_isomorphism.layout
    elif pathname == '/apps/app_table_isomorphism_all':
        return app_table_isomorphism_all.layout
    elif pathname == '/apps/app_simple_isomorphism_all':
        return app_simple_isomorphism_all.layout
    else:
        return '404'

app.css.append_css({"external_url": "http://files.tcm.phy.cam.ac.uk/~vatj2/assets/css/main.css"})
