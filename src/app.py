# General
import pandas as pd
import base64
import io

# DASH & Plotly
import dash
from dash import html
from dash import dcc

import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import os

from sc_1_forecast import forecastingGoogle

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title='Forecasting')

app.layout = html.Div(id='king-container', children=[

    # This is my Top - Bar!  Don't touch it :p
    html.Div(className='Top-Bar', children=[
        html.H2(['Google Trends Forecast'])
    ]),

    # Here I am starting my Tabs
    dcc.Tabs([
        ##########################################   TAB 1 ################################################################
        dcc.Tab(className='Tabs', label='Preview', children=[
            dbc.Row([
                dbc.Col([
                    html.P("Upload File:"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select File')
                        ]),
                        style={
                            'width': '80%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=False)

                ]),  # End of Column 1
                dbc.Col([
                    html.P("Press to Upload"),
                    dbc.Button(className="button-gen",
                               id='button-upload-file',
                               children='Upload',
                               n_clicks=0,
                               ),  # End of Button

                ]),  # End of Column 2
                dbc.Col([
                    html.P("Select File for Analysis:"),
                    dcc.Dropdown(
                        id='select-file-analysis',
                        className='dropdown',
                        clearable=True,
                        placeholder='Select File'
                    ),
                ]),  # End of Column 3
                dbc.Col([
                    dcc.Textarea(id='output-data-upload', className='commun')
                ]),  # End of Column 4

            ]),  # End of Row 1
            dbc.Row([
                dbc.Col(className="graphContainer", children=[
                    dcc.Graph(id='avgPerYear-graph')
                ]),  # End of Column 1
                dbc.Col(className="graphContainer", children=[
                    dcc.Graph(id='avgPerMonth-graph')
                ]),  # End of Column 2
            ]),  # End of Row 2
            dbc.Row([
                dbc.Col(className="graphContainerMax", children=[
                    dcc.Graph(id='searchOverTime-graph')
                ]),  # End of Column 1
            ]),  # End of Row 3

        ]),  # End of Tab 1
        ##########################################   END TAB 1   ##########################################################

        ##########################################   TAB 2 ################################################################
        dcc.Tab(className='Tabs', label='Modeling', children=[
            dbc.Row([
                dbc.Col(className="input-num-container", children=[
                    html.P("Give the step for SARIMA"),
                    dbc.Input(className='input-num',
                              id="input-step",
                              type="number",
                              placeholder="enter step",
                              min=0, max=1000, step=1,
                              )
                ]),
                dbc.Col([
                    html.P("Select File for Fit:"),
                    dcc.Dropdown(
                        id='select-file-fit',
                        className='dropdown',
                        clearable=True,
                        placeholder='Select File'
                    ),
                ]),
                dbc.Col([
                    dbc.Col(className="inp-btn-cont", children=[
                        html.P("Press to Fit the model"),
                        dbc.Button(className='button-gen',
                                   id="button-fit",
                                   children='Fit',
                                   n_clicks=0,
                                   )
                    ]),
                ]),
                dbc.Col([]),
            ]),  # End of Row 1
            dbc.Row(className='graphContainerMax', children=[
                dcc.Graph(id='residuals-graph')
            ]),  # End of Row 2
            dbc.Row(className='graphContainerMax', children=[
                dcc.Graph(id='results-graph')
            ]),  # End of Row 3
        ])  # End of Tab 2
        ##########################################   END TAB 2   ##########################################################

    ])  # End of Tabs

])  # End of King Container


##############################################################################################################
###########################    Starting of Callbacks    ######################################################
##############################################################################################################

##############################################################################################################
###########################     Update Graphs 2    ###########################################################
##############################################################################################################
@app.callback(
    Output('residuals-graph', 'figure'),
    Output('results-graph', 'figure'),
    [Input('select-file-fit', 'value'),
     Input('button-fit','n_clicks'),
     Input('input-step','value')]
)
def updateGraphs1(file_selected,n_clicks,step):
    if n_clicks == 0 or file_selected == None:

        print('file selcted is:',file_selected)

        raise PreventUpdate

    elif n_clicks !=0 and file_selected != None and step != None:

        df = pd.read_csv('data/'+file_selected)

        forcElem = forecastingGoogle(df)
        forcElem.pre_pro()
        forcElem.graphs_gen()
        fig1,fig2 = forcElem.train_sarimax_model(step)

        return fig2,fig1


##############################################################################################################
###########################     Update Graphs 1    ###########################################################
##############################################################################################################
@app.callback(
    Output('avgPerYear-graph', 'figure'),
    Output('avgPerMonth-graph', 'figure'),
    Output('searchOverTime-graph', 'figure'),
    [Input('select-file-analysis', 'value')]
)
def updateGraphs1(file_selected):
    if file_selected == None:
        raise PreventUpdate

    else:
        df = pd.read_csv('data/' + file_selected)
        forer = forecastingGoogle(df)
        forer.pre_pro()

        fig1, fig2, fig3 = forer.graphs_gen()

        return fig1, fig2, fig3


##############################################################################################################
###########################     Select FILE  #################################################################
##############################################################################################################

# Functionality for upload file
@app.callback(
    Output('output-data-upload', 'value'),
    Output('select-file-analysis', 'options'),
    Output('select-file-fit', 'options'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename'),
     Input('button-upload-file', 'n_clicks')]
)
def upload_csv_to_server(content, filename, n_clicks):
    # # Here we have the available files
    # files_uploaded = os.listdir(super_url + '\\csvs\\')

    # If I do not have something to upload
    if n_clicks == 0:
        files_uploaded = os.listdir('data/')
        opt = [{'label': x, 'value': x} for x in files_uploaded]

        return 'not any files for upload', opt,opt


    # If the file is a csv and I want to upload it
    elif n_clicks > 0 and 'csv' in filename:

        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        # Here I am reading the file to df, in order to send it to the database
        if 'csv' in filename:
            # Assume that the user uploaded a CSV
            try:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8'))).drop('Unnamed: 0', axis=1)
            except:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))



        # Save file to the database
        df.to_csv('data/' + filename)
        n_clicks = 0

        files_uploaded = os.listdir('data/')
        opt = [{'label': x, 'value': x} for x in files_uploaded]

        return '*** ' + filename + ' uploaded ***', opt,opt


if __name__ == '__main__':
    app.run_server(debug=True)
