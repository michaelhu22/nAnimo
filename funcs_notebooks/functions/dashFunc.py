
"""
dashFunc.py:
Functions used to generate and convert data to Dash Cytoscape readable formats
"""

from funcs_notebooks.functions.springLayout import fruchterman_reingold_layout_edit
import numpy as np

def formatPos(nodes, layout, multiplier, containsNodeData = None):
    """
    Returns node/layout information from networkx to a list of dicts readable by dash, scaling x/y coordinates to webpage.

        nodes (networkx.classes.reportviews.NodeDataView) = networkx Graph's raw node data (called with data = True)
        layout (dict) = dictionary of nodes to their coordinates, formatted as name:coordinates (use return of fruchterman_reingold_layout_edit function)
        multiplier (int) = value used to spread nodes out on the webpage, higher multiplier = larger spread
        containsNodeData (bool) = (to be taken out) whether or not the nx nodes contain any attribute data

    Returns:
        elements (list): list of elements readable by dash, containing node data and coordinate positions
    """
    names = list(layout.keys())
    coords = list(layout.values())
    nodeData = list(nodes)
    elements = []
    
    for element in range(len(layout)):
        classes = ''
        shift = 0
        for attrib in range (len(nodeData[element][1])):
                classes = classes + ' ' + list(nodeData[element][attrib+1].values())[0]
        
        elements.append({'data':{'id':names[element], 'label': names[element]}, 'position': {'x':coords[element][0]*multiplier, 'y':coords[element][1]*multiplier}, 'classes': classes})
        
    
    return elements


def formatEdge(edges):
    """
    Returns edge information from networkx to a list of dicts readable by dash

        edges (pandas.DataFrame) = DataFrame of edgeData, with 'source', 'target' and 'weight' (optional) columns. (use return from convertEdge function in cytoscapeFunctions.py)
    
    Returns:
        edgeList (list) = list of edges with source/target info and weight attributes, readable by dash
    """
    edgeList = []
    
    for edge in range (len(edges)):
        if 'weight' in edges.columns:
            edgeList.append({'data':{'source':edges['source'][edge], 'target':edges['target'][edge], 'label': str(edges['source'][edge]) + ' to ' + str(edges['target'][edge]), 'weight': edges['weight'][edge]}})
        else:
            edgeList.append({'data':{'source':edges['source'][edge], 'target':edges['target'][edge], 'label': str(edges['source'][edge]) + ' to ' + str(edges['target'][edge])}})


    return edgeList


def makeFrames(network, firstFrameStop, numFrames, inIterations = 1000, inPretendIterations =50, inStop = None):
    """
    Returns a list of layouts of a networkx graph object. Each layout in the list is more converged than the previous. This function uses the fruchterman_reingold_layout_edit() function to generate layout coordinates

        network (networkx.classes.graph.Graph) = a networkx Graph object with nodes and edges
        firstFrameStop (int) = number of iterations for the first layout in the list
        numFrames (int) = number of layouts in the return list
        inIterations (int) = number of total iterations for each time the layout function is run
        inPretendIterations (int) = number of iterations
        inStop (int) = how many iterations to be run before stopping (will be stopped at this number for each new layout in the list)
    
    Returns:
        posList (list) = Each element is a layout, return from fruchterman_reingold_layout_edit() function. Each layout is converged to inStop iterations past the previous layout, except for the first layout, which is converged to firstFrameStop iterations.
    """

    posList = []
    layout = fruchterman_reingold_layout_edit(network, seed = 1, iterations = inIterations, pretendIterations = inPretendIterations, stop = firstFrameStop)
    for frame in range(numFrames):
        if frame == 0:
            posList.append(layout)
        else:
            nextLayout = fruchterman_reingold_layout_edit(network, seed = 1, iterations = inIterations, pretendIterations = inPretendIterations, pos = layout, stop = inStop)
            posList.append(nextLayout)
            layout = nextLayout
    
    
    return posList


def formatPosList(network, posList, multiplier, containsNodeData):
    """
    Returns a list of dash readable networkx data, with nodes, edges, attributes and positions.

    network (networkx.classes.graph.Graph) = networkx graph object with nodes and edges
    posList (list) = list of graph layouts with coordinate positions for each node (use return of makeFrames function)
    multiplier (int) = value used to spread nodes out on the webpage, higher multiplier = larger spread
    containsNodeData (bool) = (to be taken out) whether or not the nx nodes contain any attribute data
    """

    dashList = []
    for frame in range(len(posList)):
        dashList.append(formatPos(network.nodes(data = True), posList[frame], multiplier, containsNodeData))
        
    return dashList
