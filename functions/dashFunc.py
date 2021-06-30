def formatPos(nodes, layout, multiplier):
    names = list(layout.keys())
    coords = list(layout.values())
    nodeData = list(nodes)
    elements = []
    
    for element in range(len(layout)):
        classes = ''
        for attrib in range (len(nodeData[0])-1):
            classes = classes + ' ' + list(nodeData[element][attrib+1].values())[0]
        
        elements.append({'data':{'id':names[element], 'label': names[element]}, 'position': {'x':coords[element][0]*multiplier, 'y':coords[element][1]*multiplier}, 'classes': classes})
        
    
    return elements


def formatEdge(edges):
    edgeList = []
    
    for edge in range (len(edges)):
        edgeList.append({'data':{'source':edges[edge][0], 'target':edges[edge][1], 'label': edges[edge][0] + ' to ' + edges[edge][1]}})
    
    return edgeList