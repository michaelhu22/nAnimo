import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
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

layout = fruchterman_reingold_layout_edit(gmpNetwork, seed=1, iterations=1000, pretendIterations=50, stop=10)
print('layout loaded')
edgeList = list(gmpNetwork.edges(data=True))
myElements = formatPos(gmpNetwork.nodes(data=True),layout, 1000, True) + formatEdge(edgeList)
myStylesheet = [
    {
        'selector': '.normal',
        'style': {
            'background-color': 'maroon'
        }
    },
    {
        'selector': '.TF',
        'style': {
            'content': 'data(label)',
            'background-color': 'black',
            'width': 40,
            'height': 40,
        }
    }
]

# options = {
#     'name': 'cose',
#     'initialTemp': '10',
#     'coolingFactor': '0.99',
#     'minTemp': '0.1',
#     'numIter': '250',
#     'animate': False,
#     'animationThreshold': '1',
#     'refresh': '5',
#     'fit': True,
#     'animationEasing': True,
#     #   'nodeOverlap': '4'
# }


print(myElements[0])

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Button('start/stop', id='go-button', n_clicks=0),
    html.Div(id='output'),
    dcc.Location(id='url', refresh = False),
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name' :'preset'},
        style={'width': '100%', 'height': '600px'},
        elements=myElements,
        stylesheet=myStylesheet
    )
])

app.clientside_callback(
    """
        function(n_clicks){
            let options = {
                'name': 'cose',
                'initialTemp': '10',
                'coolingFactor': '0.9999',
                'minTemp': '0.01',
                'numIter': '250',
                'animate': true,
                'animationThreshold': '1',
                'refresh': '1',
                'fit': true,
                'animationEasing': true,
                'nodeOverlap': '1',
                'gravity': '0',
                'padding':'50'
                }
            
			if (typeof window.coseLayout == 'undefined'){
				window.coseLayout = cy.layout(options)
                window.coseLayout.run()
                setTimeout(function(){
                    window.coseLayout.stop()
                }, 0)
			}
            if (n_clicks % 2 == 1){
                window.coseLayout.stop()
                return 'stop, click# '.concat(String(n_clicks))
            } else {
                window.coseLayout.run()
                return 'start, click # '.concat(String(n_clicks))
            }
        }
    """,

    Output('output', 'children'),
    Input('go-button', 'n_clicks'),
)

# @app.callback(
#     Output('output', 'children'),
#     [Input('go-button', 'n_clicks')]
# )

# def buttonStop(n_clicks):
#     if int(n_clicks)%2==0:
#         return 'go {}'.format(n_clicks)
#     else:
#         # cytoscape.stop()
#         return 'stop {}'.format(n_clicks)

if __name__ == '__main__':
    app.run_server(debug=True, port = 1112)