get_ipython().run_line_magic('run', 'functions/cytoscapeFunctions')


from py2cytoscape import cyrest
import networkx as nx
import numpy as np
import pandas as pd
import random
import time
import tempfile
from networkx.generators.random_graphs import barabasi_albert_graph as ba


# In[ ]:


# G = nx.fast_gnp_random_graph(10, 0.4)
# G1 = nx.fast_gnp_random_graph(10, 0.6)


# In[ ]:


def addEdgeAttrib (nxGraph, attribName, lowNum, highNum):
    edges = nxGraph.edges(data = True)
    
    for i in range (len(edges)):
        nxGraph[list(edges)[i][0]][list(edges)[i][1]][attribName] = np.random.rand()*(highNum-lowNum)+lowNum


def addHalfEdgeAttrib (nxGraph, attribName, lowNum1, highNum1, lowNum2, highNum2):
    edges = nxGraph.edges(data = True)
    half = int(len(edges)/2)
    
    for i in range (half):
        nxGraph[list(edges)[i][0]][list(edges)[i][1]][attribName] = random.randint(lowNum1, highNum1)
    
    if len(edges)%2 == 0:
        for i in range(half):
            nxGraph[list(edges)[i+(half)][0]][list(edges)[i+half][1]][attribName] = random.randint(lowNum2, highNum2)
    else:
        for i in range(half):
            nxGraph[list(edges)[i+(half)][0]][list(edges)[i+half][1]][attribName] = random.randint(lowNum2, highNum2)
# In[ ]:


# addEdgeAttrib(G, 'weight', 0,1)
# addEdgeAttrib(G, 'test',1,10)
# addEdgeAttrib(G1, 'weight',0,1)
# addEdgeAttrib(G1, 'test',1,10)


# In[ ]:


# if True, return True and element in inputList
def contains (element, inputList):
    for i in range (len(inputList)):
        if inputList[i]==element:
            return (True, i)
    return False


# In[ ]:


# preprossesing
def conformEdges (network1, network2):
    edges1 = list(network1.edges())
    edges2 = list(network2.edges())

    keys = list(list(network1.edges(data = True))[0][2].keys())

    # ranging thru edges1 and checking if
    for i in range (len(edges1)):
        if (not(contains(edges1[i], edges2))):
            network2.add_edge(edges1[i][0],edges1[i][1])
            for key in keys:
                network2[edges1[i][0]][edges1[i][1]][key] = 0

    for i in range(len(edges2)):
        if (not(contains(edges2[i], edges1))):
            network1.add_edge(edges2[i][0], edges2[i][1])
            for key in keys:
                network1[edges2[i][0]][edges2[i][1]][key] = 0


# In[ ]:


# conformEdges (G,G1)


# In[ ]:


# edges1 and edges2 should have the same length, going from edge1 -> edge2
def genShifts(edges1, edges2, columnName, numNetworks):
    numEdges = len(edges1)
    shifts = []
    
    for i in range(numEdges):
        a = list(edges1)[i][2][columnName]
        b = list(edges2)[i][2][columnName]
        shifts.append((b-a)/(numNetworks-1))
    
    return shifts


# In[ ]:


# assume edgeLists same length, and same attribute catagories
def fillBetweenEdges(nxGraph1, nxGraph2, numNetworks):
    edges1, edges2 = list(nxGraph1.edges(data = True)), list(nxGraph2.edges(data = True))
    numEdges = len(edges1)
    keys = list(list(edges1)[0][2].keys())
    networks = []
    
    for networkNum in range(numNetworks):
        tempNetwork = nxGraph1.copy()
        for attrib in keys:
            for edge in range(numEdges):
                source = edges1[edge][0]
                target = edges1[edge][1]
                val1, val2 = nxGraph1[source][target][attrib], nxGraph2[source][target][attrib]
                
                tempNetwork[source][target][attrib] = np.linspace(val1, val2, numNetworks)[networkNum]
                
        networks.append(tempNetwork)
        
    return networks


# postprocessing after network list has already been made
def deleteZeroWeights (networks):
    for network in networks:
        edges = list(network.edges(data = True))
        keys = list(edges[0][2].keys())

        for edge in edges:
            empty = True
            for key in keys:
                if network[edge[0]][edge[1]][key] > 0:
                    empty = False
            if empty == True:
                network.remove_edge(edge[0], edge[1])


# In[ ]:


# path = os.path.join(os.path.dirname(os.path.abspath("template.cys")), "sample.csv")
# for i in range(len(networks)):
#     convertEdge(networks[i]).to_csv(path)
#     time.sleep(0.3)
