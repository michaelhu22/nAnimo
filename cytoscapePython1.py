#!/usr/bin/env python
# coding: utf-8

from py2cytoscape import cyrest
import networkx as nx
import numpy as np
import pandas as pd
import random
import time
import tempfile
from networkx.generators.random_graphs import barabasi_albert_graph as ba


def generateNetworks(num, d, n, time):
    """
    Returns a dictionary of elements time:network
    
    Parameters:
        num (int): Number of networks generated
        d (int): Degree of each node in the networks
        n (int): Number of nodes in each network
        time (int): Total time of the dictionary
        
    Returns:
        networkDict (dict): Dictionary of {time:network} of num length. Keys range from 0 to time, in acending order.
        Values are randomly generated networks with n nodes, each node with d degree.
    """
    networkDict = {}
    times = []
    for i in range (num):
        rand = random.random()*time
        while rand in times:
            rand = random.random()*time
        times.append(rand)
    times[num-1] = time
    times.sort()
    for i in range (num):
        networkDict[times[i]] = nx.random_regular_graph(d,n)
    return networkDict

# In[165]:


def addNodeAttributes (network, attribute, value):
    """
    Adds an attribute to all nodes in a networkX network
    
    Parmeters:
        network (networkx.classes.graph.Graph): networkX graph to have node attributes added
        attribute (str): Name of attribute category
        value (str): Value of each attribute
    """
    for x in range (len(network.nodes())):
        nx.set_node_attributes(network, {x:value}, attribute)


# In[166]:


def convertEdge (network):
    """
    Return a DataFrame of readable edge data from a networkX graph
    
    Parameters:
        network (networkx.classes.graph.Graph): A networkX graph with edges
        
    Returns:
        edges (DataFrame): DataFrame of readable edge data, sorted by source node values
    """
    networkEdges = network.edges(data = True)
    d = {'source':[], 'target':[]}
    for i in networkEdges:
        d['source'].append(i[0])
        d['target'].append(i[1])
    columns = list((list(networkEdges)[0][2]).keys())
    for i in range (len(columns)):
        d[columns[i]] = [x[2][columns[i]] for x in networkEdges]
    edges = pd.DataFrame(d)
    edges.sort_values('source')
    return edges


# In[167]:


def convertNode (network):
    """
    Returns a DataFrame of readable node data from a networkX graph
    
    Parameters:
        network (networkx.classes.graph.Graph): A networkX graph with nodes
        
    Returns:
        nodes (DataFrame): DataFrame of readable node data
    """
    networkNodes = network.nodes(data = True)
    keys = list(dict(networkNodes).keys())
    values = list(dict(networkNodes).values())
    nodes = pd.DataFrame(values, index = keys)
    nodes.sort_index()
    return nodes


# In[168]:


def addSpringCoords (network,spread):
    """
    Returns a DataFrame of node data from a networkX graph, with additional x and y columns of spring layout coordinates
    for each node
    
    Parameters:
        network (networkx.classes.graph.Graph): A networkX graph with nodes
        spread (int): Space between nodes
        
    Returns:
        nodes(DataFrame): A DataFrame of nx's node data with additional x/y columns for coordinates
    """
    nodeData = convertNode(network)
#     using networkx spring_layout function
    coords = nx.spring_layout(network)
    for i in range (len(coords)):
        for j in range (2):
            coords[i][j] = int(coords[i][j]*spread)
    arr = np.array([coords[x] for x in range (len(coords))])
    df = pd.DataFrame(arr, columns = ['x', 'y'])
    nodeData['x'] = df['x']
    nodeData['y'] = df['y']
    nodes =  pd.DataFrame(nodeData)
    nodes = nodes.sort_index()
    return nodes


# In[169]:


def importNode(nodes):
    """
    Sends node data to cytoscape from a DataFrame
    
    Parameters:
        nodes(DataFrame): A DataFrame with node data to be imported
        
    *Cytoscape requires network to already exist, or else importing node data will not work.
     Use cytoscape.network.create_empty() or importEdge() prior if receiving error.
    """
    nodes.to_csv('data/nodeData.csv')
    cytoscape.table.import_file(
        keyColumnIndex = "1",
        startLoadRow = "0",
        dataTypeList = "String",
        firstRowAsColumnNames = 'True',
        afile = 'C:/Users/micha/code/cytoscape_code/jn/data/nodeData.csv')


# In[170]:


def importEdge(edges):
    """
    Sends edge data to cytoscape from a DataFrame
    
    Parameters:
        edges(DataFrame): A DataFrame with edge data to be imported
        
    *Will create a new network in Cytoscape instead of overwriting current network
    """
    edges.to_csv('data/edgeData.csv')
    cytoscape.network.import_file(
        indexColumnSourceInteraction="2",
        indexColumnTargetInteraction ="3",
        firstRowAsColumnNames = "true",
        startLoadRow = '0',
        afile ='C:/Users/micha/code/cytoscape_code/jn/data/edgeData.csv')
    time.sleep(0.1)


# In[171]:


def toCytoscape(nodes, edges):
    """
    Sends node and edge data to cytoscape from DataFrames
    
    Parameters:
        nodes(DataFrame): A DataFrame with node data to be imported
        edges(DataFrame): A DataFrame with edge data to be imported
        
    *Will create a new network in Cytoscape instead of overwriting current network
    """
    edges.to_csv('data/edgeData.csv')
    nodes.to_csv('data/nodeData.csv')
    
    cytoscape.network.import_file(
        indexColumnSourceInteraction="2",
        indexColumnTargetInteraction ="3",
        firstRowAsColumnNames = "true",
        startLoadRow = '0',
        afile ='C:/Users/micha/code/cytoscape_code/jn/data/edgeData.csv')
    time.sleep(0.1)
    cytoscape.table.import_file(
        keyColumnIndex = "1",
        startLoadRow = "0",
        dataTypeList = "String",
        firstRowAsColumnNames = 'True',
        afile = 'C:/Users/micha/code/cytoscape_code/jn/data/nodeData.csv')


# In[172]:


def predictTimes(networks):
    """
    Returns a DataFrame of times between networks based on the time keys of a time:network dictionary
    
    Parameters:
        networks (dict): Dictionary of time:network elements
        
    Returns:
        predictedTimes (DataFrame): Column of integers that represent time between networks
    """
    keys = list(networks.keys())
    a = [keys[0]]
    for x in range (len(networks)-1):
        a.append(keys[x+1] - keys[x])
    predictedTimes = pd.DataFrame(a,columns = ['seconds'])
    return predictedTimes

# importNetworks takes a dictionary of time keys and network values, and sends the networks to cytoscape in order.
# network sending is delayed between networks based on the times keys of each network. toJpeg is a boolean value which
# decides whether or not to send each frame to a jpeg file
def importNetworks(networks, toJpeg):
    """
    Sends
    """
    timeKeys = list(networks.keys())
    for x in range (len(networks)):
        if x == 0:
            time.sleep(timeKeys[0])
        nodes = addSpringCoords(networks[timeKeys[x]], 500)
        edges = convertEdge(networks[timeKeys[x]])
        toCytoscape(nodes, edges)
#         buffering to keep up with cytoscape lag. this will make the times less accurate.
        time.sleep(0.3)
        cytoscape.view.fit_content()
        if (x<len(networks)-1):
            time.sleep(timeKeys[x+1]-timeKeys[x])
# In[173]:


def createFrames(df1, df2, columnName, frames):
    """
    Returns a DataFrame of node rows and frame columns. 
    
    Parameters:
        df1 (DataFrame): DataFrame containing coordinate data of starting frame
        df2 (DataFrame): DataFrame containing coordinate data of ending frame, with same length as df1
        columnName (str): Name of column that contains x or y data in both DataFrames (must be a shared column name in both DataFrames)
        frames (int): total number of frames between starting and ending coordinates
        
    Returns:
        coords (DataFrame): DataFrame with nod rows and frame columns, with evenly spaced coordinates between each frame
        
    *Remember to use this twice, once for x and once for y coordinates.
    """
#     preserve node order
    df1 = df1.sort_index()
    df2 = df2.sort_index()
    
    if columnName not in df1.columns or columnName not in df2.columns:
        raise Exception('missing column name')
    mat = [[0 for x in range (len(df1))] for x in range (frames)]
    
#     setting first and last frame to d1 and d2 coords
    mat[0] = df1[columnName].array
    mat[len(mat)-1] = df2[columnName].array
    coords = pd.DataFrame(mat)
    coords = coords.transpose()
    
#     filling in between first and last frame
    for row in range (len(coords)):
        frameShift = (coords[len(coords.columns)-1][row] - coords[0][row])/(frames-1)
        for col in range (frames):
            if col != 0:
                coords[col][row] = coords[col-1][row] + frameShift
    coords = coords.round(1)
    
#     naming rows and columns
    for i in range (len(coords.columns)):
        coords = coords.rename(columns={i:'f'+str(i)})
    for i in range (len(coords)):
        coords = coords.rename(index = {i:'node' + str(i)})
    
    return coords


# In[174]:


def playFrames(xFrames, yFrames, export, startIndex):
    """
    Plays frames into Cytoscape from DataFrames with node# rows and frame# columns.
    
    Parameters:
        xFrames (DataFrame): DataFrame of node# rows and frame# columns of x coordinate data
        yFrames (DataFrame): DataFrame of node# rows and frame# columns of y coordinate data
        export (bool): If export == True, playFrames will export every frame from Cytoscape as a .jpeg
        startIndex (int): Starting index of named image files (creates no naming overlap if running playFrames multiple times for the same image folder)
    """
    
    temp = pd.DataFrame()
    
#     copying each frames x/y coordinates to temp and importing them (could possibly take out temp and directly import
#     frames?)
    for i in range (len(xFrames.columns)):
        temp['x'] = xFrames['f'+str(i)].array
        temp['y'] = yFrames['f'+str(i)].array
        importNode(temp)
        time.sleep(0.3)
        cytoscape.view.fit_content()
        time.sleep(0.3)
        if export:
            cytoscape.view.export(
                options = 'jpeg',
                outputFile = 'C:/Users/micha/code/cytoscape_code/jn/data/output/test/frame'+ str(startIndex + i) +'.jpeg')


# In[175]:


def playNetworks(networks, frameMultiplier, spread):
    """
    Plays networks from a dictionary of time:network. It plays all the frames between networks in order.
    the number of frames between two networks is decided by the time keys. playNetworks automatically exports each frame
    to a .jpeg file.
    
    Parameters:
        networks (dictionary): Dictionary of time:network. Networks will be played in order with frames added between network node coordinates
        frameMultiplier (int): frameMultiplier decides how many frames each unit of time recieves
        spread (int): Space between nodes, the greater the spread the farther apart the nodes will be
        
    """
#     first importing edges so nodes coordinates can be imported later
    initialEdge = convertEdge(networks[list(networks.keys())[0]])
    importEdge(initialEdge)
    time.sleep(0.3)
    
#     create a list of DataFrames for each network node list (with spring layout coordinates) outside of the for loop,
#     because networkx may create a different set of coordiantes for the same network every time nx.spring_layout is run. 
    nodeList = []
    for x in range (len(networks)):
        nodeList.append(addSpringCoords(networks[list(networks.keys())[x]], spread))
        nodeList[0]

#    create a list of keys (times) so the corresponding number of frames can be made between each network
    times = list(networks.keys())
    
#     counting total frames in for loop so files can be named correctly for ffmpeg
    totalFrames = 0
    
#     for every network, create frames between networks and play the frames
    for x in range (len(networks)-1):
        frames = int((times[x+1]-times[x])*frameMultiplier)
        xFrames = createFrames(nodeList[x], nodeList[x+1], 'x', frames)
        yFrames = createFrames(nodeList[x], nodeList[x+1], 'y', frames)
        
#         import the current node coordinates to make sure graph node locations are continuous with each playFrames run.
        importNode(nodeList[x])
        
        playFrames(xFrames,yFrames, export = True, startIndex = totalFrames)
        
#         import edges of next graph, which should have node coordinates in place after playframes is run.
        n2Edges = convertEdge(networks[list(networks.keys())[x+1]])
        importEdge(n2Edges)
        
        totalFrames += frames

        time.sleep(1)