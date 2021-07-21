from ipynbs.functions.springLayoutJN1 import fruchterman_reingold_layout_edit

def formatPos(nodes, layout, multiplier, containsNodeData):
    names = list(layout.keys())
    coords = list(layout.values())
    nodeData = list(nodes)
    elements = []
        
    for element in range(len(layout)):
        classes = ''
        shift = 0
        if containsNodeData == True:
            shift = 1
        else:
            shift = 2
        for attrib in range (len(nodeData[0])-shift):
                classes = classes + ' ' + list(nodeData[element][attrib+1].values())[0]
        
        elements.append({'data':{'id':names[element], 'label': names[element]}, 'position': {'x':coords[element][0]*multiplier, 'y':coords[element][1]*multiplier}, 'classes': classes})
        
    
    return elements


def formatEdge(edges):
    edgeList = []
    
    for edge in range (len(edges)):
        edgeList.append({'data':{'source':edges[edge][0], 'target':edges[edge][1], 'label': str(edges[edge][0]) + ' to ' + str(edges[edge][1])}})
    
    return edgeList


def makeFrames(network, numFrames, inIterations, inPretendIterations, inStop):
    posList = []
    layout = fruchterman_reingold_layout_edit(network, seed = 1, iterations = inIterations, pretendIterations = inPretendIterations, stop = inStop)
    for frame in range(numFrames):
        if frame == 0:
            posList.append(layout)
        else:
            nextLayout = fruchterman_reingold_layout_edit(network, seed = 1, iterations = inIterations, pretendIterations = inPretendIterations, pos = layout, stop = inStop)
            posList.append(nextLayout)
            layout = nextLayout
    
    
    return posList


def formatPosList(network, posList, multiplier, containsNodeData):
    dashList = []
    for frame in range(len(posList)):
        dashList.append(formatPos(network.nodes(data = True), posList[frame], multiplier, containsNodeData))
        
    return dashList