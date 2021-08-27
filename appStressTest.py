import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import networkx as nx
import os
import pandas as pd
from funcs_notebooks.functions.springLayout import fruchterman_reingold_layout_edit
from funcs_notebooks.functions.dashFunc import *
from funcs_notebooks.functions.cytoscapeFunctions import *
from funcs_notebooks.functions.edgeFunctions import *
from _pytest import warnings
import time

# add comments, group callbck functions witih comments


gmpNetwork = nx.gnm_random_graph(2000,6000)


# addEdgeAttrib(gmpNetwork, 'weight', 0.1, 1)


numFrames = 11
print(' ')
print('Layout loading')
origFrames = makeFrames(gmpNetwork, firstFrameStop=0, numFrames = numFrames, inIterations=1000, inPretendIterations=50, inStop = 5)
print('FR layout applied')
adjDict = nx.to_dict_of_lists(gmpNetwork)
print('Adjlist loaded')
print('Loaded!')

edgeList = [formatEdge(convertEdge(gmpNetwork))]

formatOrigFrames = formatPosList(gmpNetwork, origFrames, 1250, containsNodeData = True)

timePoints = {0.0: formatOrigFrames[0], 0.1: formatOrigFrames[1], 0.2: formatOrigFrames[2], 0.3: formatOrigFrames[3], 0.4: formatOrigFrames[4], 0.5: formatOrigFrames[5], 0.6: formatOrigFrames[6], 0.7: formatOrigFrames[7], 0.8: formatOrigFrames[8], 0.9: formatOrigFrames[9], 1.0: formatOrigFrames[10]}

myElements = formatOrigFrames[0] + edgeList[0]
myStylesheet = [
    {
        'selector': '.normal',
        'style': {
            'background-color': 'maroon',
            'background-opacity': '0.5',
            'content': 'data(label)',
            'font-size': '10px',
            'width': 30,
            'height':30
        }
    },
    {
        'selector': '.TF',
        'style': {
            'content': 'data(label)',
            'font-size': '40px',
            'background-color': 'maroon',
            'background-opacity': '0.7',
            'outline': 'black',
            'width': 50,
            'height': 50,
        }
    },
    {
        'selector': 'edge',
        'style': {
            'width' : 0.1,
            'opacity': 0.5,
            'grabbable': False
        }
    },
    {
        'selector': 'edge:selected',
        'style': {
            'background-color': 'purple',
            'content': 'data(weight)',
            'font-size' : '50px',
            'opacity': 1
        }
    },
     {
        'selector': 'node:selected',
        'style': {
            'background-color': '#430022',
            'content': 'data(label)',
            'font-size' : '75px',
            'background-opacity': '0.9',
        }
    }
]


app = dash.Dash(__name__)
app.layout = html.Div([ 
    cyto.Cytoscape(
        id='cytoscape1',
        layout={'name' :'preset'},
        style={'width': '100%', 'height': '500px'},
        elements=myElements,
        stylesheet=myStylesheet,
        minZoom=0.1,
    ),
    html.Div(
        id = 'slider-label',
        children = 'Time Slider'
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
        'Play/Pause',
         id='play-button1',
         n_clicks=0),
    html.Div(id = 'playing?'),
    html.Div(id = 'spacer', children = " "),
    html.Div(id = 'elements'),
    html.Div(id = 'scrap1'),
    html.Div(id = 'timeList', children = 'Time points containing data: ' + str(list(timePoints.keys()))[1:-1]),
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
        return html.Br(), str(data['data']['id']), '\'s edges:', html.Br(), edges, html.Br()


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
            return 'Paused'
        else
            return 'Playing'
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
        return 'Total bar filled: ' + ((value/max)*100).toPrecision(4) + '% ----- Percent filled between times ' + String(timePointsKeys[beginTimePointIndex]) + ' to ' + String(timePointsKeys[beginTimePointIndex+1]) + ': ' + (percentBetween*100).toPrecision(4) + '%' 
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
    app.run_server(debug=True, port = '1111')