# name

## Background
name is a network visualization program that visualizes Dynamic Networks. Initially made to visualize reconstructed dynamic networks. name solves the problem of visualizing a Dynamic Network in easy-to-read layouts with relevant data. The program takes into account time and weight data to generate a moving visualization.


## "Basic Properties" (different name?)
This program is primarily written in Python, with JavaScript used for webpage functions. It uses Dash Cytoscape as well as cytoscape.js to visualize the network on the webpage, as well as NetworkX to organize network info and layout function. name does not require any additional applications to use, as the entire visualization is browser based.

This visualization uses a Force Directed Layout, (more specifically a Frucherman Reingold layout) to visualize the network in the least busy way possible. Using multiple data points, and generating layouts for each point, the visualization uses given information as well as interpolation to generate a smooth visualization animation of a given network.


## Getting Started (User):
### Dependencies: 
- Python 3.8 or later
- NetworkX
- Pandas
- numpy
- dash
- dash cytoscape
- random

### Run
In command prompt, set directory to where you downloaded the program, and use 

    python appClientInterp.py

in command line to have the visualization on your browser. The address should show up in command prompt in the Dash blurb; it should say: "Dash is running on [webpage address]" (The port should be set to 1111).

Loading messages will on the command prompt starting with "Layout loading". The layouts and other data is loaded on the webpage once you see the "Loaded!" message run.

### Overview
Once loaded into the webpage, there will be a network of nodes and edges in a square-ish shape; this is the network with random node loactions, before converged. You may interact with the network now! Each node represents a gene, and each edge represents a relationship between two genes. Larger labeled nodes are Transcription Factors (TFs), while small unlabeled (or small text labeled) nodes are normal genes. The strength between genes can be observed through edge visuals alone: thicker/redder edges denote stronger weight, while thinner/yellower edges denote less weight. Stronger edge weight means a stronger gene-gene relationship.

### Interaction
#### Network/Data
You may also interact with the network, and get more info on the genes being shown. Nodes can be moved around with the mouse. Dragging along an empty space allows panning, and scrolling lets you zoom in and out.

Clicking on a node will highlight it, and provide information on the node and its relationships at the bottom of the webpage. The gene's name, type, and edges will be given. 

Clicking on an edge will label its weight, from a scale of 0 to 1. Currently, edge weights are randomly generated, as the current data is a sample network. Edge weights will still affect the overall layout, though.

#### Moving Visualization
Moving the slider will allow you to see the network moving through "time". Currently, the network is just converging to a Frucherman Reingold layout. Alternatively, there is a Play/Pause button to play the network. Since the layout is Force directed, so you will see larger-weight edges pulling nodes stronger than smaller-weight edges.

Underneath the Play/Pause Button, there is some info on the time data. The time parameter goes from 0 to 1, with any number of data points in between. Currently, there are 11 sample data points evenly spaced through time. Every other network layout is interpolated from the given data.

    "Total bar filled":
will give the percentage of the slider filled, and also represent how far in time from 0% to 100% the displayed network is.

    "Percent filled between times [time point] and [time point]":
will give how far between two data points the current network is.

    "Time points containing data":
will give a list of time points with given data. There are 11 data points spaced through times 0 to 1 in this current sample network.


## Getting Started (developer)
### Dependencies: 
- Python 3.8 or later
- NetworkX
- Pandas
- numpy
- dash
- dash cytoscape
- random

### Files/Folders
The current usable file is "appClientInterp.py". The file "appDynamic.py" is being worked on, to allow dynamic networks to be visualized. "appStressTest.py" is similar to "appClientside.py", just using a large 2000 node and 6000 edge network. Will take longer to run.

The "networks" folder contains sample network data, in .tsv format

The "funcs_notebooks" folder contains archived Jupyter Notebooks (.ipynb), as well as a "functions" folder which contains the library of python function files used in the visualization.


## WIP
This program is currently still a work in progress. The network being used is utilizing generated edge weight data, and is a sample network being converged. Next steps will allow for full user-input dynamic network visualization and gene specific visualizations, along with other things.

## Issues
Please post questions/issues in the issues section

## Contact:
Michael Hu
michaelhu218@gmail.com
