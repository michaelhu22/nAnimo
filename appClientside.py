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

# gmpNetwork = nx.gnm_random_graph(2000,6000)
numFrames = 1000
frames = formatPosList(gmpNetwork, makeFrames(gmpNetwork,numFrames,inIterations = 1000, inPretendIterations = 50,inStop = 1), 1250, True)

print('layout loaded')
edgeList = formatEdge(list(gmpNetwork.edges(data=True)))
myElements = frames[0] + edgeList
myStylesheet = [
    {
        'selector': '.normal',
        'style': {
            'background-color': 'maroon',
            'background-opacity': '0.4',
            'width': 30,
            'height':30
        }
    },
    {
        'selector': '.TF',
        'style': {
            'content': 'data(label)',
            'font-size': '40px',
            # 'text-color':'red',
            'background-color': '#b74e0e',
            'background-opacity': '0.8',
            'outline': 'black',
            'width': 75,
            'height': 75,
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color' : 'black',
            'width': '1px',
            'opacity': 0.3
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
    dcc.Store(id = 'frames', storage_type='memory', data = frames),
    dcc.Store(id = 'edgeList', storage_type='memory', data = edgeList),
    dcc.Interval(
        id = 'interval',
        interval = 1,
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
        dots = False,
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

# @app.callback(
#     Output('interval', 'n_intervals'),
#     [Input('play-button', 'n_clicks')],
#     [State('time-slider', 'value')]
# )

# def setn_interval(n_clicks, value):
#     return value

app.clientside_callback(
    """
    function(n_clicks, value) {
        return value
    }
    """,
    
    Output('interval', 'n_intervals'),
    Input('play-button', 'n_clicks'),
    State('time-slider', 'value')
)


# @app.callback(
#     Output('time-slider', 'value'),
#     [Input('interval', 'n_intervals')],
#     # [State('time-slider', 'drag_value')]
# )

# def onInterval(n_intervals):
#     return n_intervals

app.clientside_callback(
    """
    function(n_intervals) {
        return n_intervals
    }
    """,

    Output('time-slider', 'value'),
    Input('interval', 'n_intervals')
)

# @app.callback(
#     Output('interval', 'disabled'),
#     [Input('play-button', 'n_clicks')]
# )

# def playPause (n_clicks):
#     if n_clicks % 2 == 0:
#         return True
#     else:
#         return False

app.clientside_callback(
    """
    function(n_clicks){
        if ((n_clicks % 2) == 0)
            return true
        else
            return false
    }
    """,

    Output('interval', 'disabled'),
    Input('play-button', 'n_clicks')
)

# @app.callback(
#     Output('playing?', 'children'),
#     [Input('play-button', 'n_clicks')]
# )

# def playFeedback(n_clicks):
#     if n_clicks % 2 == 0:
#         return 'paused'
#     else:
#         return 'playing'

app.clientside_callback(
    """
    function(n_clicks){
        if ((n_clicks % 2) == 0)
            return 'paused'
        else
            return 'playing'
    }
    """,

    Output('playing?', 'children'),
    Input('play-button', 'n_clicks')
)


# @app.callback(
#     Output('cytoscape', 'elements'),
#     [Input('time-slider', 'value')],
#     [State('cytoscape', 'elements')]
# )

# def sliderFrame(value, elements):
#     return frames[value] + formatEdge(edgeList)

app.clientside_callback(
    """
    function(value, elements, frameData, edgeData){
        return frameData[value].concat(edgeData)
    }
    """,

    Output('cytoscape', 'elements'),
    Input('time-slider', 'value'),
    State('cytoscape', 'elements'),
    State('frames', 'data'),
    State('edgeList', 'data')
)

# @app.callback(
#     Output('frame#', 'children'),
#     [Input('time-slider', 'value')]
# )

# def sliderFrameNum(value):
#     return 'frame# ' + str(value)

app.clientside_callback(
    """
    function(value){
        return 'frame# ' + String(value)
    }
    """,

    Output('frame#', 'children'),
    Input('time-slider', 'value')
)

if __name__ == '__main__':
    app.run_server(debug=True, port = 1111)