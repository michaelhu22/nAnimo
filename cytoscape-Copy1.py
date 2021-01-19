#!/usr/bin/env python
# coding: utf-8

# In[1]:


from py2cytoscape import cyrest
import networkx as nx
import numpy as np
import pandas as pd
import random
import time
from networkx.generators.random_graphs import barabasi_albert_graph as ba


# In[2]:


cytoscape =  cyrest.cyclient()


# In[3]:


cytoscape.status()


# In[4]:


from py2cytoscape.data.cyrest_client import CyRestClient
cy = CyRestClient()


# In[5]:


cy.session.delete()


# In[6]:


cytoscape.session.open(session_file = "C:\\Users\\micha\\code\\cytoscape_code\\template.cys")


# In[7]:


# generateNetworks takes a num, d, n and time. returns a dictionary of num length, with keys being randomly generated
# in the range of 0 to time. values are random networks with n nodes with degree d 
def generateNetworks(num, degree, nodes, time):
    ret = {}
    times = []
    for i in range (num):
        rand = random.random()*time
        while rand in times:
            rand = random.random()*time
        times.append(rand)
    times[num-1] = time
    times.sort()
    for i in range (num):
        ret[times[i]] = nx.random_regular_graph(degree,nodes)
    return ret


# In[8]:


# addNodeAttributes takes and nx network, attribute name, and value. it adds an attribute to all the nodes with value 
# value. used to test graphs with more node data than x/y coords.
def addNodeAttributes (network, attribute, value):
    for x in range (len(network.nodes())):
        nx.set_node_attributes(network, {x:value}, attribute)


# In[9]:


#convertEdge takes a Networkx network and returns a DataFrame with the edge data. Rows edges, columns of source/sink/data
def convertEdge (nx):
    nxEdges = nx.edges(data = True)
    d = {'source':[], 'target':[]}
    for i in nxEdges:
        d['source'].append(i[0])
        d['target'].append(i[1])
    columns = list((list(nxEdges)[0][2]).keys())
    for i in range (len(columns)):
        d[columns[i]] = [x[2][columns[i]] for x in nxEdges]
    ret = pd.DataFrame(d)
    ret.sort_values('source')
    return ret


# In[10]:


# convertNode takes a Networkx graph and returns a Dataframe with node data. Rows of nodes, columns of name/data
def convertNode (nx):
    nxNodes = nx.nodes(data = True)
    keys = list(dict(nxNodes).keys())
    values = list(dict(nxNodes).values())
    ret = pd.DataFrame(values, index = keys)
    return ret


# In[11]:


# addSpringCoords take a Networkx Graph and a spread variable, and returns a DataFrame with the node data, as well as
# x and y columns with spring layout coordinates for each node. each coordinate is simply multiplied by the spread for 
# better visibility in cytoscape
def addSpringCoords (nxgraph,spread):
    nodeData = convertNode(nxgraph)
#     using networkx spring_layout function
    coords = nx.spring_layout(nxgraph)
    for i in range (len(coords)):
        for j in range (2):
            coords[i][j] = int(coords[i][j]*spread)
    arr = np.array([coords[x] for x in range (len(coords))])
    df = pd.DataFrame(arr, columns = ['x', 'y'])
    nodeData['x'] = df['x']
    nodeData['y'] = df['y']
    ret =  pd.DataFrame(nodeData)
    ret = ret.sort_index()
    return ret


# In[12]:


# importNodeCoords imports node data from a DataFrame
def importNode(nodes):
    nodes.to_csv('C:/Users/micha/code/cytoscape_code/jn/data/nodeData.csv')
    cytoscape.table.import_file(
        keyColumnIndex = "1",
        startLoadRow = "0",
        dataTypeList = "String",
        firstRowAsColumnNames = 'True',
        afile = 'C:/Users/micha/code/cytoscape_code/jn/data/nodeData.csv')


# In[13]:


# importEdge takes a DataFrame and imports into cytoscape
def importEdge(edges):
    edges.to_csv('C:/Users/micha/code/cytoscape_code/jn/data/edgeData.csv')
    cytoscape.network.import_file(
        indexColumnSourceInteraction="2",
        indexColumnTargetInteraction ="3",
        firstRowAsColumnNames = "true",
        startLoadRow = '0',
        afile ='C:/Users/micha/code/cytoscape_code/jn/data/edgeData.csv')
    time.sleep(0.1)


# In[14]:


# toCytoscape takes a NetoworkX graph and sends it to cytroscape with spring directed layout.
def toCytoscape(nodes, edges):
    edges.to_csv('C:/Users/micha/code/cytoscape_code/jn/data/edgeData.csv')
    nodes.to_csv('C:/Users/micha/code/cytoscape_code/jn/data/nodeData.csv')
    
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


# In[15]:


# predictTimes takes a dictionary of time:networks and returns a dataFrame of how many seconds between networks
# numbers indicate how much between prev network an current network (time next to 0 actually should be 0 in this case, need fix)
def predictTimes(networks):
    keys = list(networks.keys())
    a = [keys[0]]
    for x in range (len(networks)-1):
        a.append(keys[x+1] - keys[x])
    predictedTimes = pd.DataFrame(a,columns = ['seconds'])
    return predictedTimes


# In[16]:


# importNetworks takes a dictionary of time keys and network values, and sends the networks to cytoscape in order.
# network sending is delayed between networks based on the times keys of each network. toJpeg is a boolean value which
# decides whether or not to send each frame to a jpeg file
def importNetworks(networks, toJpeg):
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


# In[17]:


# importNetworks(networks, True)


# In[18]:


# createFrames takes two DataFrames with the same length, shared column name, and number of frames, and returns a 
# DataFrame with frames number of columns.
def createFrames(df1, df2, columnName, frames):
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


# In[19]:


# playFrames takes two dataFrames with each column as coordinates frames and each row as nodes. it sends node coordinates
# to cytoscape with a 0.6 second delay between each, to keep up with Cytoscape lag. if export == True, it will export each frame as a jpeg file. startIndex
# is an integer where playFrames will start naming the jpeg files.
def playFrames(xFrames, yFrames, export, startIndex):
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


# In[20]:


# playNetworks takes a dictionary of time:network, and a frameMultiplier. It plays all the frames between networks in order.
# the number of frames between two networks is decided by the time between them, multiplied by the frameMultiplier.
# a higher frameMultiplier will take longer but will be smoother
# spread is how spread out the nodes are plotted
def playNetworks(networks, frameMultiplier, spread):
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


# In[21]:


networks = generateNetworks(num = 10, degree = 3, nodes =10, time = 15)

for x in range (len(networks)):
    addNodeAttributes(networks[list(networks.keys())[x]], 'test attribute', 'test')
    
predictTimes(networks)


# In[23]:


# should end up with around time*frameMultiplier frames at the end, give or take some because of the casting to int
playNetworks(networks, frameMultiplier = 30, spread = 500)


# In[ ]:


# nx.draw(L, pos = nx.spring_layout(L, iterations = 0, pos = {i:[i,i**2] for i in range (10)}))

