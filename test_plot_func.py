# -*- coding: utf-8 -*-
import os
import networkx as nx
from gltl2ba import ltl_formula_to_ba
from construct_product_automaton import product_automaton
from construct_product_automaton import buchi_label_test

# from gltl2ba import Graph

weight_list=[3,5,3,2,4]
trans_graph=nx.DiGraph()
trans_graph.add_node('n1',name='n1',label=['p1'])
trans_graph.add_node('n2',name='n2',label=['p2'])
trans_graph.add_node('n3',name='n3',label=['p3'])
trans_graph.add_edge('n1','n2',weight=1)
trans_graph.add_edge('n2','n3',weight=3)
trans_graph.add_edge('n1','n3',weight=2)
trans_graph.add_edge('n2','n1',weight=1)
trans_graph.add_edge('n3','n2',weight=3)
trans_graph.add_edge('n3','n1',weight=2)

# task formula
task="(<> p1) && (<> p2) && (<> p3)"
# os.getcwd get current work directory
LTL_FILE_POS=os.getcwd()+'/ltlFile.txt'

# convert ltl to buchi automaton
buchi_init_state=[]
buchi_accept_state=[]
[buchi_graph,buchi_init_state,buchi_accept_state]=ltl_formula_to_ba(task,LTL_FILE_POS,True)

def nx_to_graphviz_trans(trans_graph):
    """
    convert networkx graph to a dot graph
    """
    trans_dot_graph=Graph()
    trans_dot_graph.title("transition system")
    for node in list(trans_graph.nodes):
        trans_dot_graph.node(node,node,False)
        for reachable_node in trans_graph[node]:
            trans_dot_graph.edge(node,reachable_node,str(trans_graph[node][reachable_node]['weight']))
    return trans_dot_graph
graph1=nx_to_graphviz_trans(trans_graph)
graph1.show()
    

try:
    best_path=nx.dijkstra_path(trans_graph,'n1','n3',weight='weight')
    print(best_path)
except nx.NetworkXNoPath:
    print('haha')
