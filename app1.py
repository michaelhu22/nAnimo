import dash
import dash_cytoscape as cyto
import dash_html_components as html
import networkx as nx
import os
import pandas as pd
from functions.springLayoutJN1 import fruchterman_reingold_layout_edit
from functions.dashFunc import formatPos
from functions.dashFunc import formatEdge
from _pytest import warnings


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

layout = fruchterman_reingold_layout_edit(
    gmpNetwork, seed=1, iterations=1000, pretendIterations=50, stop=400)
edgeList = list(gmpNetwork.edges(data=True))

myElements = formatPos(gmpNetwork.nodes(data=True),layout, 1000) + formatEdge(edgeList)

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
            'content':'data(label)',
            'background-color':'black'
        }
    }
]


print(myElements[0])

app = dash.Dash(__name__)
app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '800px'},
        elements=myElements,
        stylesheet=myStylesheet
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
