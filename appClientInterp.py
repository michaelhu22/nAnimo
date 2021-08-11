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
from ipynbs.functions.cytoscapeFunctions import *
from ipynbs.functions.edgeFunctions import *
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

    # print(gmpOverlap, progOverlap)

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
addEdgeAttrib(gmpNetwork, 'weight', 0.5, 1)
# addEdgeAttrib(progNetwork, 'weight', 0.1, 1)
# print(gmpNetwork.edges(data = True))
# print(gmpNetwork.nodes(data = True))

# print(convertNode(gmpNetwork))
# print(convertNode(progNetwork))

# gmpNetwork = nx.gnm_random_graph(2000,6000)
numFrames = 10
startTime = time.time()
origTime = time.time()
print('')
print('layout loading')
origFrames = makeFrames(gmpNetwork, firstFrameStop=150, numFrames = numFrames, inIterations=1000, inPretendIterations=50, inStop = 15)
print('FR layout applied', end = ' ')
# print(time.time()-startTime)
# startTime = time.time()
# interpolatedFrames = []
# numBetweenFrames = 1
# for frame in range(numFrames-1):
#     interpolatedFrames.extend(genBetweenFrames(origFrames[frame], origFrames[frame+1], numBetweenFrames))
# print('interpolated', end = ' ')
# print(time.time()-startTime)
# startTime = time.time()

# frames = formatPosList(gmpNetwork, interpolatedFrames, 1500, containsNodeData=True)
# print(len(frames))
# print('layout formatted', end = ' ')
# print(time.time()-startTime)
# startTime = time.time()
# # print(frames[0])
adjDict = nx.to_dict_of_lists(gmpNetwork)
print('adjlist loaded', end = ' ')
print(time.time()-startTime)
print('total time: ' + str(time.time() - origTime))
# print(frames)

edgeList = [formatEdge(convertEdge(gmpNetwork))]
addEdgeAttrib(gmpNetwork, 'weight', 0.1, 0.1)
edgeList.append(formatEdge(convertEdge(gmpNetwork)))

formatOrigFrames = formatPosList(gmpNetwork, origFrames, 1500, containsNodeData= True)


# timePoints = {0.0: formatOrigFrames[0],0.3: formatOrigFrames[1], 0.35: formatOrigFrames[2], 0.60: formatOrigFrames[3], 0.61: formatOrigFrames[4], 0.62: formatOrigFrames[5], 0.7: formatOrigFrames[6], 1.0: formatOrigFrames[7]}

timePoints = {0.0: formatOrigFrames[0], 1.0: formatOrigFrames[9]}

# print(list(timePoints.keys()))
# print(edgeList[0])
# print(edgeList)
myElements = formatOrigFrames[0] + edgeList[0]
myStylesheet = [
    {
        'selector': '.normal',
        'style': {
            # 'content': 'data(label)',
            # 'font-size': '10px',
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
            'background-color': '#b74e0e',
            'background-opacity': '0.8',
            'outline': 'black',
            'width': 50,
            'height': 50,
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color' : 'mapData(weight, 0, 1, blue, red)',
            'width' : 'mapData(weight,0,1,1,10)',
            'opacity': 0.3,
            'selectable': False,
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
    },
    # {
    #     'selector': '[weight > 5]',
    #     'style': {
    #         'line-color' : 'red',
    #         'width': 5,
    #         'opacity': 0.7,
    #         # 'label': 'data(weight)'
    #     }
    # }
    # SELECTED formatting
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
        # wheelSensitivity= 0.5
    ), 
    dcc.Slider(
        id='time-slider1',
        min = 0,
        max = 10000,
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
    # html.Div(id = 'nodeHoverData'),
    html.Div(id = 'nodeTapData'),
    html.Div(id = 'nodeTapMoreData'),
    html.Div(id = 'elements'),
    html.Div(id = 'scrap1'),
    html.Div(id = 'timeList', children = 'times containing \'data\': ' + str(list(timePoints.keys()))),
    cyto.Cytoscape(
        id='cytoscape2',
        layout={'name' :'preset'},
        style={'width': '500px', 'height': '500px'},
        elements=myElements,
        stylesheet=myStylesheet,
        minZoom=0.1,
        # wheelSensitivity= 0.5
    ),
    # dcc.Slider(
    #     id = 'time-slider2',
    #     min = 0,
    #     max = len(interpolatedFrames)-1,
    #     step = 1,
    #     value = 0,
    #     dots = False,
    #     updatemode = 'drag'
    # ),
    html.Div(id = 'scrap2'),
    # dcc.Store(id = 'frames', storage_type='memory', data = frames),
    dcc.Store(id = 'origFrames', storage_type = 'memory', data = formatOrigFrames),
    dcc.Store(id = 'edgeList', storage_type='memory', data = edgeList),
    dcc.Store(id = 'timePoints', storage_type='memory', data = timePoints),
    dcc.Interval(
        id = 'interval',
        interval = 1,
        n_intervals=0,
        max_intervals=10000,
        disabled = True
    )
    
])


# app.config.suppress_callback_exceptions = True

@app.callback(
    Output('nodeTapData', 'children'),
    Input('cytoscape1', 'tapNode')
)

def nodeTap(data):
    if data is None:
        return 'no node selected'
    else:
        return 'name: ' + str(data['data']['id']) + '; type: ' + str(data['classes'])

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
        return html.Br(), 'edges:', html.Br(), edges

# @app.callback(
#     Output('elements', 'children'),
#     Input('cytoscape1', 'tapNode'),
#     State('cytoscape1', 'elements')
# )

# def showAdj(node, elements):

#     return str(elements[0])
#     # return adjDict[str(node['data']['label'])]

# @app.callback(
#     Output('elements', 'children'),
#     Input('cytoscape1', 'tapNode'),
#     State('cytoscape1', 'elements')
# )

# def adjTest(node, elements):
#     if node is not None:
#         return str(next(item for item in elements if item['data']['id'] == str(node['data']['label'])))

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



app.clientside_callback(
    """
    function(n_clicks, value) {
        return value
    }
    """,
    
    Output('interval', 'n_intervals'),
    Input('play-button1', 'n_clicks'),
    State('time-slider1', 'value')
)


app.clientside_callback(
    """
    function(n_intervals) {
        return n_intervals
    }
    """,

    Output('time-slider1', 'value'),
    Input('interval', 'n_intervals')
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

# app.clientside_callback(
#     """
#     function (value, max, frameData, edgeData){
#         var test1 = document.getElementById('cytoscape1')

#         if (test1 != 'undefined'){
#             cyObject1 = test1._cyreg.cy
#             cyObject1.nodes().positions(function(node,i){
#                 var mult1 = value/max
#                 var mult2 = 1-mult1
#                 return {
#                     x: frameData[0][i]['position']['x']*mult2 + frameData[frameData.length-1][i]['position']['x']*mult1,
#                     y: frameData[0][i]['position']['y']*mult2 + frameData[frameData.length-1][i]['position']['y']*mult1
#                 }
#             })
#         }
#         return String(value/max)
#     }
#     """,

#     Output('scrap1', 'children'),
#     Input('time-slider1', 'value'),
#     State('time-slider1', 'max'),
#     State('frames', 'data'),
#     State('edgeList', 'data'),
# )

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

        //take out later
        console.log(String(timePointsKeys[beginTimePointIndex]) + ' to ' + String(timePointsKeys[beginTimePointIndex+1]))
        console.log(timePointsKeys)
        console.log(timePoints['0.0'][0]['position'])


        var percentBetween = ((value/max)-timePointsKeys[beginTimePointIndex])/(timePointsKeys[beginTimePointIndex+1] - timePointsKeys[beginTimePointIndex])
        if (test1 != 'undefined' && frameData[beginTimePointIndex+1] != null){
            cyObject1 = test1._cyreg.cy
            cyObject1.nodes().positions(function(node,i){
                return {
                    x: frameData[beginTimePointIndex][i]['position']['x']*(1-percentBetween) + frameData[beginTimePointIndex+1][i]['position']['x']*(percentBetween),
                    y: frameData[beginTimePointIndex][i]['position']['y']*(1-percentBetween) + frameData[beginTimePointIndex+1][i]['position']['y']*(percentBetween)
                }
            })
        for (let edge = 0; edge < edgeData[beginTimePointIndex].length; edge++){
            prevWeight = edgeData[beginTimePointIndex][edge]['data']['weight']
            nextWeight = edgeData[beginTimePointIndex+1][edge]['data']['weight']
            var avgWeight = prevWeight*(1-percentBetween) + nextWeight*(percentBetween)
            cyObject1.edges()[edge].data('weight', avgWeight)
        }
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

# app.clientside_callback(
#     """
#     function (value, elements, frameData, edgeData){
#         var test2 = document.getElementById('cytoscape2')
#         if (test2 != 'undefined'){
#             cyObject2 = test2._cyreg.cy
#             cyObject2.nodes().positions(function( node, i ){
#                 return {
#                     x: frameData[value][i]['position']['x'],
#                     y: frameData[value][i]['position']['y']
#                 }
#             })
#         }
#         return 'test'
#     }
#     """,
            
#     Output('scrap2', 'children'),
#     Input('time-slider2', 'value'),
#     State('cytoscape2', 'elements'),
#     State('frames', 'data'),
#     State('edgeList', 'data')
# )

# @app.callback(
#     Output('cytoscape1', 'elements'),
#     Input('cytoscape1', 'tapNode'),
#     State('cytoscape1', 'elements')
# )

# def adjTest(node, elements):
#     if node is not None:
#         tempNode = elements.pop(0)
#         tempNode['selected'] = True
#         elements.append(tempNode)
#     return elements


# @app.callback(
#     # Output('cytoscape1', 'elements'),
#     Output('cytoscape1', 'elements'),
#     Input('cytoscape1', 'tapNode'),
#     Input('time-slider1', 'value'),
#     State('cytoscape1', 'elements'),
#     State('frames', 'data'),
#     State('edgeList', 'data')
# )

# def selectAdjNodes(tapNode, value, elements, frameData, edgeData):
#     if tapNode is None:
#         return frameData[value] + edgeData
#     else:
#         nodeID = str(tapNode['data']['id'])
#         nodeElemIndex = next(index for (index, i) in enumerate(elements) if i['data']['id'] == nodeID)
#         nodeAdjList = adjDict[nodeID]

#         for node in nodeAdjList:
#             nodeIndex = next(index for (index, i) in enumerate(elements) if i['data']['id'] == node)
#             temp = elements.pop(nodeIndex)
#             temp['selected'] = True
#             elements.append(temp)

#         return elements

# app.clientside_callback(
#     """
#     function(tapNode, value, elements, frameData, edgeData)
#     """
# )

        # tempNode['selected'] = True
        # elements.append(tempNode)
        # return elements

if __name__ == '__main__':
    app.run_server(debug=True, port = 1111)