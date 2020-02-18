# -*- coding: utf-8 -*-
import networkx as nx

def clasc_trans_graph1():
    trans_graph=nx.DiGraph()
    trans_graph.add_node('n1',name='n1',label=['p11'])
    trans_graph.add_node('n2',name='n2',label=['p12'])
    trans_graph.add_node('n3',name='n3',label=['p13'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
    return trans_graph

def clasc_trans_graph2():
    trans_graph=nx.DiGraph()
    trans_graph.add_node('n1',name='n1',label=['p21'])
    trans_graph.add_node('n2',name='n2',label=['p22'])
    trans_graph.add_node('n3',name='n3',label=['p23'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
    return trans_graph

def clasc_trans_graph3():
    trans_graph=nx.DiGraph()
    trans_graph.add_node('n1',name='n1',label=['p31'])
    trans_graph.add_node('n2',name='n2',label=['p32'])
    trans_graph.add_node('n3',name='n3',label=['p33'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
    return trans_graph

def samp_trans_graph1():
    trans_graph=nx.DiGraph()
    trans_graph.add_node('n1',name='n1',label=['p11'])
    trans_graph.add_node('n2',name='n2',label=['p12'])
    trans_graph.add_node('n3',name='n3',label=['p13'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
    return trans_graph

def samp_trans_graph2():
    trans_graph=nx.DiGraph()
    trans_graph.add_node('n1',name='n1',label=['p21'])
    trans_graph.add_node('n2',name='n2',label=['p22'])
    trans_graph.add_node('n3',name='n3',label=['p23'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
    return trans_graph

def samp_trans_graph3():
    trans_graph=nx.DiGraph()
    trans_graph.add_node('n1',name='n1',label=['p31'])
    trans_graph.add_node('n2',name='n2',label=['p32'])
    trans_graph.add_node('n3',name='n3',label=['p33'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
    return trans_graph
    
    
    
