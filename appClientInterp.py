import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# import dash_bootstrap_components as dbc
import networkx as nx
import os
import pandas as pd
from funcs_notebooks.functions.springLayout import fruchterman_reingold_layout_edit
from funcs_notebooks.functions.dashFunc import *
from funcs_notebooks.functions.cytoscapeFunctions import *
from funcs_notebooks.functions.edgeFunctions import *
from _pytest import warnings
import time

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

    gmpNodeIndexDF = gmpNodeDF.set_index('Name')
    progNodeIndexDF = progNodeDF.set_index('Name')

    nx.set_node_attributes(gmpNetwork, gmpNodeDF.to_dict('index'))
    nx.set_node_attributes(gmpNetwork, gmpNodeIndexDF.to_dict('index'))

    gmpNetwork1 = gmpNetwork.copy()

    nx.set_node_attributes(progNetwork, progNodeDF.to_dict('index'))
    nx.set_node_attributes(progNetwork, progNodeIndexDF.to_dict('index'))

    return gmpNetwork, progNetwork


gmpNetwork, progNetwork = networkExtract()
addEdgeAttrib(gmpNetwork, 'weight', 0.1, 1)


numFrames = 11
startTime = time.time()
origTime = time.time()
print('')
print('layout loading')
origFrames = makeFrames(gmpNetwork, firstFrameStop=0, numFrames = numFrames, inIterations=1000, inPretendIterations=50, inStop = 25)
print('FR layout applied', end = ' ')
adjDict = nx.to_dict_of_lists(gmpNetwork)
print('adjlist loaded', end = ' ')
print(time.time()-startTime)
print('total time: ' + str(time.time() - origTime))

edgeList = [formatEdge(convertEdge(gmpNetwork))]
addEdgeAttrib(gmpNetwork, 'weight', 0.1, 0.1)
edgeList.append(formatEdge(convertEdge(gmpNetwork)))

formatOrigFrames = formatPosList(gmpNetwork, origFrames, 1250, containsNodeData = True)

timePoints = {0.0: formatOrigFrames[0], 0.1: formatOrigFrames[1], 0.2: formatOrigFrames[2], 0.3: formatOrigFrames[3], 0.4: formatOrigFrames[4], 0.5: formatOrigFrames[5], 0.6: formatOrigFrames[6], 0.7: formatOrigFrames[7], 0.8: formatOrigFrames[8], 0.9: formatOrigFrames[9], 1.0: formatOrigFrames[10]}

myElements = formatOrigFrames[0] + edgeList[0]
myStylesheet = [
    {
        'selector': '.normal',
        'style': {
            'background-color': 'maroon',
            'background-opacity': '0.5',
            'width': 30,
            'height':30
        }
    },
    {
        'selector': '.TF',
        'style': {
            'content': 'data(label)',
            'font-size': '40px',
            'text-color':'red',
            'background-color': 'maroon',
            'background-opacity': '1',
            'outline': 'black',
            'width': 70,
            'height': 70,
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color' : 'mapData(weight, 0, 1, yellow, red)',
            'width' : 'mapData(weight,0,1,0.5,5)',
            'opacity': 'mapData(weight, 0, 1, 0.1, 0.5)',
            'grabbable': False
        }
    },
    {
        'selector': ':selected',
        'style': {
            'background-color': 'purple',
            'content': 'data(label)',
            'font-size' : '50px'
        }
    }
]


app = dash.Dash(__name__)
app.layout = html.Div([ 
    cyto.Cytoscape(
        id='cytoscape1',
        layout={'name' :'preset'},
        style={'width': '800px', 'height': '500px'},
        elements=myElements,
        stylesheet=myStylesheet,
        minZoom=0.1,
    ),
    dcc.Slider(
        id='time-slider1',
        min = 0,
        max = 100000,
        step = 1,
        value= 0,
        dots = False,
        updatemode='drag'
    ),
    html.Button(
        'play/pause',
         id='play-button1',
         n_clicks=0),
    html.Div(id = 'playing?'),
    html.Div(id = 'elements'),
    html.Div(id = 'scrap1'),
    html.Div(id = 'timeList', children = 'times containing \'data\': ' + str(list(timePoints.keys()))),
    html.Div(id = 'nodeTapData'),
    html.Div(id = 'nodeTapMoreData'),
    dcc.Store(id = 'origFrames', storage_type = 'memory', data = formatOrigFrames),
    dcc.Store(id = 'edgeList', storage_type='memory', data = edgeList),
    dcc.Store(id = 'timePoints', storage_type='memory', data = timePoints),
    dcc.Interval(
        id = 'interval',
        interval = 1,
        n_intervals=0,
        max_intervals=100,
        disabled = True
    )
    
])


@app.callback(
    Output('nodeTapData', 'children'),
    Input('cytoscape1', 'tapNode')
)

def nodeTap(data):
    if data is None:
        return 'no node selected'
    else:
        return html.Br(), 'Selected Gene Name: ' + str(data['data']['id']), html.Br(),  'Selected Gene Type: ' + str(data['classes'])

@app.callback(
    Output('nodeTapMoreData', 'children'),
    Input('cytoscape1', 'tapNode')
)

def nodeTapln2(data):
    if data is None:
        return ''
    else:
        edges = ''
        for edge in data['edgesData']:
            edges += edge['source'] + ' to ' + edge['target'] + '; '
        edges = edges[0: len(edges)-2]
        return html.Br(), 'Selected Node edges:', html.Br(), edges, html.Br()


app.clientside_callback(
    """
    function(n_clicks, value, max) {
        let test = (value/max)*100
        return parseInt(test)
    }
    """,
    
    Output('interval', 'n_intervals'),
    Input('play-button1', 'n_clicks'),
    State('time-slider1', 'value'),
    State('time-slider1', 'max'),
)


app.clientside_callback(
    """
    function(n_intervals, max_intervals, max) {
        return n_intervals*(max/max_intervals)
    }
    """,

    Output('time-slider1', 'value'),
    Input('interval', 'n_intervals'),
    State('interval', 'max_intervals'),
    State('time-slider1', 'max')
)

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
    Input('play-button1', 'n_clicks')
)


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
    Input('play-button1', 'n_clicks')
)

app.clientside_callback(
    """
    function (value, max, frameData, edgeData, timePoints){
        var test1 = document.getElementById('cytoscape1')
        var beginTimePointIndex = 0
        var timePointsKeys = Object.keys(timePoints)
        for (time = timePointsKeys.length-1; time > 0; time--){
            if ((value/max)>=timePointsKeys[time]){
                beginTimePointIndex = time
                break
            }
        }
        var percentBetween = ((value/max)-timePointsKeys[beginTimePointIndex])/(timePointsKeys[beginTimePointIndex+1] - timePointsKeys[beginTimePointIndex])
        if (test1 != 'undefined' && frameData[beginTimePointIndex+1] != null){
            cyObject1 = test1._cyreg.cy
            cyObject1.nodes().positions(function(node,i){
                return {
                    x: frameData[beginTimePointIndex][i]['position']['x']*(1-percentBetween) + frameData[beginTimePointIndex+1][i]['position']['x']*(percentBetween),
                    y: frameData[beginTimePointIndex][i]['position']['y']*(1-percentBetween) + frameData[beginTimePointIndex+1][i]['position']['y']*(percentBetween)
                }
            })
        //for (let edge = 0; edge < edgeData[beginTimePointIndex].length; edge++){
        //    prevWeight = edgeData[beginTimePointIndex][edge]['data']['weight']
        //    nextWeight = edgeData[beginTimePointIndex+1][edge]['data']['weight']
        //    var avgWeight = prevWeight*(1-percentBetween) + nextWeight*(percentBetween)
        //    cyObject1.edges()[edge].data('weight', avgWeight)
        // }
        }
        else if (test1 != 'undefined' && frameData[beginTimePointIndex+1] == null){
            cyObject1 = test1._cyreg.cy
            cyObject1.nodes().positions(function(node,i){
                return {
                    x: frameData[frameData.length-1][i]['position']['x'],
                    y: frameData[frameData.length-1][i]['position']['y']
                }
            })
        }
        return 'total bar filled: ' + (value/max).toPrecision(2) + ' --- percent filled between times ' + String(timePointsKeys[beginTimePointIndex]) + ' to ' + String(timePointsKeys[beginTimePointIndex+1]) + ': ' + (percentBetween*100).toPrecision(4) + '%' 
    }
    """,

    Output('scrap1', 'children'),
    Input('time-slider1', 'value'),
    State('time-slider1', 'max'),
    State('origFrames', 'data'),
    State('edgeList', 'data'),
    State('timePoints', 'data')
)



"""
some commmented out code for adjacent node selecting - not in use currently

@app.callback(
    Output('elements', 'children'),
    Input('cytoscape1', 'tapNode'),
    State('cytoscape1', 'elements')
)

def showAdj(node, elements):

    return str(elements[0])
    # return adjDict[str(node['data']['label'])]

@app.callback(
    Output('elements', 'children'),
    Input('cytoscape1', 'tapNode'),
    State('cytoscape1', 'elements')
)

def adjTest(node, elements):
    if node is not None:
        return str(next(item for item in elements if item['data']['id'] == str(node['data']['label'])))

@app.callback(
    Output('elements', 'children'),
    Input('cytoscape1', 'tapNode'),
    State('cytoscape1', 'elements')
)

def adjSelect(node, elements):
    if node is not None:
        # elements[0]['selected'] = True
        # return str(next(item for item in elements if item['data']['id'] == str(node['data']['label'])))
        return str(elements[next(index for (index, i) in enumerate(elements) if i['data']['id'] == str(node['data']['id']))])
"""



if __name__ == '__main__':
    app.run_server(debug=True, port = 1111)