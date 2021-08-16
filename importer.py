def load_network(diri_base):
	"""Loads dynamic network from folder.
	diri_base: Path of input folder that contains dynamic network. Folder must be output of export.ipynb notebook (or following the format).
	Return:
	time_meta: pandas.DataFrame of shape (n_time,n_property) for properties of time points
	cell_meta: pandas.DataFrame of shape (n_cell,n_property) for time-independent properties of cells
	node_meta: pandas.DataFrame of shape (n_node,n_property) for time-independent properties of nodes
	node_name1: numpy.array of shape (n_regulator) for regulator node names
	node_name2: numpy.array of shape (n_target) for target node names
	cell_data: {property:numpy.array of shape (n_time,n_cell)} for time-dependent properties of cells
	node_data: {property:numpy.array of shape (n_time,n_node)} for time-dependent properties of nodes
	edge_data: {property:numpy.array of shape (n_time,n_regulator,n_target)} for time-dependent properties of edges
	"""
	from os.path import join as pjoin
	from os import listdir
	import numpy as np
	import pandas as pd

	#Load meta data
	cell_meta=pd.read_csv(pjoin(diri_base,'cell_meta.tsv.gz'),header=0,index_col=None,sep='\t')
	node_meta=pd.read_csv(pjoin(diri_base,'node_meta.tsv.gz'),header=0,index_col=None,sep='\t')
	time_meta=pd.read_csv(pjoin(diri_base,'time_meta.tsv.gz'),header=0,index_col=None,sep='\t')
	print('1')
	nc,nn,nt=[len(x) for x in [cell_meta,node_meta,time_meta]]
	with open(pjoin(diri_base,'edge_node1.txt'),'r') as f:
		node_name1=f.readlines()
	with open(pjoin(diri_base,'edge_node2.txt'),'r') as f:
		node_name2=f.readlines()
	node_name1,node_name2=[np.array([y.strip() for y in x]) for x in [node_name1,node_name2]]
	ne1,ne2=[len(x) for x in [node_name1,node_name2]]
	print('2')
	#Load data
	t1=[x[10:-7] for x in listdir(diri_base) if x.startswith('node_data_') and x.endswith('.txt.gz')]
	print('3')
	node_data={x:np.loadtxt(pjoin(diri_base,'node_data_{}.txt.gz'.format(x))).reshape(nt,nn) for x in t1}
	print('4')
	t1=[x[10:-7] for x in listdir(diri_base) if x.startswith('edge_data_') and x.endswith('.txt.gz')]
	print('5')
	edge_data={x:np.loadtxt(pjoin(diri_base,'edge_data_{}.txt.gz'.format(x))).reshape(nt,ne1,ne2) for x in t1}
	print('6')
	t1=[x[10:-7] for x in listdir(diri_base) if x.startswith('cell_data_') and x.endswith('.txt.gz')]
	print('7')
	cell_data={x:np.loadtxt(pjoin(diri_base,'cell_data_{}.txt.gz'.format(x))).reshape(nt,nc) for x in t1}
	return (time_meta,cell_meta,node_meta,node_name1,node_name2,cell_data,node_data,edge_data)

from os.path import join as pjoin
import os
import time
dirbase='../..'
dirname = os.path.dirname(os.path.abspath('template.cys'))
diri_base=pjoin(dirname,'exported_networks\\Blood-B')

start = time.time()
time_meta,cell_meta,node_meta,node_name1,node_name2,cell_data,node_data,edge_data=load_network(diri_base)
elapsed = time.time() - start
print(str(elapsed) + 'secs')

# 'C:\\Users\\micha\\code\\cytoscape_code\\git\\exported_networks\\Blood-B'