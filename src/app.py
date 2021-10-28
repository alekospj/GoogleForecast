import os

# General
import pandas as pd

# DASH & Plotly
import dash
from dash import  html
from dash import dcc

import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go
import plotly.express as px


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],title='Forecasting')

app.layout = html.Div(id = 'king-container',children = [

    # This is my Top - Bar!  Don't touch it :p
    html.Div(className='Top-Bar', children=[
        html.H2(['Google Trends Forecast'])
    ]),

    #Here I am starting my Tabs
    dcc.Tabs([
        ##########################################   TAB 1 ################################################################
        dcc.Tab(className='Tabs',label='Preview', children=[
            dbc.Row([
                dbc.Col([
                    html.P("Upload File:"),
                    dcc.Upload(
                        id='upload-data-fuel',
                        disabled=True,
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

                ]),   # End of Column 2
                dbc.Col([]), # End of Column 3
                dbc.Col([]),  # End of Column 4

            ]), # End of Row 1
            dbc.Row([
                dbc.Col(className ="graphContainer" , children =  [
                    dcc.Graph(id = 'avgPerYear-graph')
                ]),  # End of Column 1
                dbc.Col(className ="graphContainer" , children =  [
                    dcc.Graph(id='avgPerMonth-graph')
                ]),  # End of Column 2
            ]), # End of Row 2
            dbc.Row([
                dbc.Col(className ="graphContainerMax" , children =  [
                    dcc.Graph(id='searchOverTime-graph')
                ]),  # End of Column 1
            ]), # End of Row 3

        ]),  # End of Tab 1
        ##########################################   END TAB 1   ##########################################################

        ##########################################   TAB 1 ################################################################
        dcc.Tab(className='Tabs', label='Modeling', children=[
            dbc.Row([
                dbc.Col(className="inp-btn-cont",children =[
                    html.P("Give the step for SARIMA"),
                    dbc.Input(className='input-num',
                              id="input-step",
                              type="number",
                              placeholder="enter step",
                              min=0, max=1000, step=1,
                              )
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
                dbc.Col([]),
            ]), # End of Row 1
            dbc.Row(className='graphContainerMax',children = [
                dcc.Graph(id = 'residuals-graph')
            ]),# End of Row 2
            dbc.Row(className='graphContainerMax',children  = [
                dcc.Graph(id='results-graph')
            ]),# End of Row 3
        ])  # End of Tab 2
        ##########################################   END TAB 2   ##########################################################

    ]) # End of Tabs

]) # End of King Container
##############################################################################################################
###########################    Starting of Callbacks    ######################################################
##############################################################################################################




if __name__ == '__main__':

    app.run_server(debug=True)








































