import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import networkx as nx
import os
import pandas as pd
from ipynbs.functions.springLayoutJN1 import fruchterman_reingold_layout_edit
from ipynbs.functions.dashFunc import *
from _pytest import warnings
import time

# importing networks - kinda messy


def networkExtract():

    networkFolder = os.path.join(os.path.dirname(
        os.path.abspath("template.cys")), 'networks')

    GMP = os.path.join(networkFolder, 'GMP')
    Prog = os.path.join(networkFolder, 'Progenitor')

    GMPedge = os.path.join(GMP, 'edge.tsv')
    GMPnode = os.path.join(GMP, 'node.tsv')

    ProgEdge = os.path.join(Prog, 'edge.tsv')
    ProgNode = os.path.join(Prog, 'node.tsv')

    gmpEdgeDF = pd.read_csv(GMPedge, delimiter='\t')
    gmpNodeDF = pd.read_csv(GMPnode, delimiter='\t')
    progEdgeDF = pd.read_csv(ProgEdge, delimiter='\t')
    progNodeDF = pd.read_csv(ProgNode, delimiter='\t')

    gmpNetwork = nx.Graph()
    gmpOverlap = 0

    for i in range(len(gmpEdgeDF)):
        if gmpNetwork.has_edge(gmpEdgeDF['Regulator'][i], gmpEdgeDF['Target'][i]):
            gmpOverlap += 1
        gmpNetwork.add_edge(gmpEdgeDF['Regulator'][i], gmpEdgeDF['Target'][i])

    progNetwork = nx.Graph()

    progOverlap = 0

    for i in range(len(progEdgeDF)):
        if progNetwork.has_edge(progEdgeDF['Regulator'][i], progEdgeDF['Target'][i]):
            progOverlap += 1
        progNetwork.add_edge(
            progEdgeDF['Regulator'][i], progEdgeDF['Target'][i])

    print(gmpOverlap, progOverlap)

    gmpNodeIndexDF = gmpNodeDF.set_index('Name')
    progNodeIndexDF = progNodeDF.set_index('Name')

    nx.set_node_attributes(gmpNetwork, gmpNodeDF.to_dict('index'))
    nx.set_node_attributes(gmpNetwork, gmpNodeIndexDF.to_dict('index'))

    gmpNetwork1 = gmpNetwork.copy()
    # gmpNetwork1.remove_node('IRF7')

    nx.set_node_attributes(progNetwork, progNodeDF.to_dict('index'))
    nx.set_node_attributes(progNetwork, progNodeIndexDF.to_dict('index'))
    # end of network import

    return gmpNetwork, progNetwork


gmpNetwork, progNetwork = networkExtract()
# end of network import

# G = nx.gnm_random_graph(2000,6000)
numFrames = 100
frames = formatPosList(gmpNetwork, makeFrames(gmpNetwork,numFrames,1000,50,5), 750, True)

print('layout loaded')
edgeList = list(gmpNetwork.edges(data=True))
myElements = frames[0] + formatEdge(edgeList)
myStylesheet = [
    {
        'selector': '.normal',
        'style': {
            'background-color': 'maroon',
            'width': 15,
            'height':15
        }
    },
    {
        'selector': '.TF',
        'style': {
            'content': 'data(label)',
            'background-color': 'blue',
            'width': 50,
            'height': 50,
        }
    }
]

app = dash.Dash(__name__)
app.layout = html.Div([ 
    html.Button(
        'play/pause',
         id='play-button',
         n_clicks=0),
    html.Div(id = 'playing?'),
    html.Div(id = 'frame#'),
    dcc.Interval(
        id = 'interval', 
        interval = 500, 
        n_intervals=0,
        max_intervals=numFrames,
        disabled = False
    ),
    dcc.Slider(
        id='time-slider',
        min = 0,
        max = numFrames,
        step = 1,
        value= 0,
        dots = True,
        updatemode='drag'
    ),
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name' :'preset'},
        style={'width': '100%', 'height': '600px'},
        elements=myElements,
        stylesheet=myStylesheet
    )
])

# app.config.suppress_callback_exceptions = True

@app.callback(
    Output('interval', 'n_intervals'),
    [Input('play-button', 'n_clicks')],
    [State('time-slider', 'value')]
)

def setn_interval(n_clicks, value):
    return value

@app.callback(
    Output('time-slider', 'value'),
    [Input('interval', 'n_intervals')],
    # [State('time-slider', 'drag_value')]
)

def onInterval(n_intervals):
    if n_intervals == None:
        return 0
    else:
        return n_intervals

@app.callback(
    Output('interval', 'disabled'),
    [Input('play-button', 'n_clicks')]
)

def playPause (n_clicks):
    if n_clicks % 2 == 0:
        return True
    else:
        return False

@app.callback(
    Output('playing?', 'children'),
    [Input('play-button', 'n_clicks')]
)

def playFeedback(n_clicks):
    if n_clicks % 2 == 0:
        return 'paused'
    else:
        return 'playing'

# why isn't drag_value working
@app.callback(
    Output('cytoscape', 'elements'),
    [Input('time-slider', 'value')],
    [State('cytoscape', 'elements')]
)

def sliderFrame(value, elements):
    return frames[value] + formatEdge(edgeList)



@app.callback(
    Output('frame#', 'children'),
    [Input('time-slider', 'value')]
)

def sliderFrameNum(value):
    return 'frame# ' + str(value)

if __name__ == '__main__':
    app.run_server(debug=True, port = 1111)