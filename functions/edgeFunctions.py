
get_ipython().run_line_magic('run', 'functions/cytoscapeFunctions')


# functions used to format and converge networkx edge data

from py2cytoscape import cyrest
import networkx as nx
import numpy as np
import pandas as pd
import random
import time
import tempfile
from networkx.generators.random_graphs import barabasi_albert_graph as ba
from IPython.core.getipython import get_ipython


def addEdgeAttrib (nxGraph, attribName, lowNum, highNum):
    """
    Adds Edge attribute data (random/numeric) to an exisiting networkx Graph
    
    nxGraph (networkx.classes.graph.Graph) = networkx Graph to add attributes in
    attribName (str) = Name of attribute
    lowNum (float) = low bound of randomly generated number
    highNum (float) high bound of randomly generated number
    
    """
    edges = nxGraph.edges(data = True)
    
    for i in range (len(edges)):
        nxGraph[list(edges)[i][0]][list(edges)[i][1]][attribName] = np.random.rand()*(highNum-lowNum)+lowNum


# if True, return True and element in inputList
def contains (element, inputList):
    for i in range (len(inputList)):
        if inputList[i]==element:
            return (True, i)
    return False


# In[ ]:


# preprossesing
def conformEdges (network1, network2):
    """
    Sets each network with the union of the edges of both networks. New edges will have initial attributes set to 0.
    
    network1 (networkx.classes.graph.Graph) = networkx Graph
    network2 (networkx.classes.graph.Graph) = networkx Graph
    """
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


# assume edgeLists same length, and same attribute catagories
def fillBetweenEdges(nxGraph1, nxGraph2, numNetworks):
    """
    Returns a list with size numNetworks of networkx Graphs, with edge attribute data from nxGraph1 to nxGraph2 evenly spaced between each network. networks[0] will have nxGraph1, and networks[numNetworks-1] will have nxGraph2
    
    nxGraph1 (networkx.classes.graph.Graph) = first networkx Graph in the list of networks
    nxGraph2 (networkx.classes.graph.Graph) = last networkx Graph in the list of networks
    numNetworks (int) = number of networkx Graphs in the returned list of networks
    
    *both networkx Graphs must have the same edges (use conformEdges()). They must also have the same attributes.
    """
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
    """
    Removes edges with all attributes with value 0 from a networkxGraph
    
    networks (list[networkx.classes.graph.Graph]) = list of networkx Graph objects to remove 0 weight edges out of
    """
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
                
def deleteLoneNodes (network):
    for node in list(network.nodes()):
        if len(list(network.adj[node])) == 0:
            network.remove_node(node)

def deleteLoneListNodes (networks):
    for network in networks:
        deleteLoneNodes(network)