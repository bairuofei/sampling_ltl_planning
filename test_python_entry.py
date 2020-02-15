# -*- coding: utf-8 -*-

import networkx as nx
product_graph=nx.DiGraph()
product_graph.add_node(1,name='haha,heihei',ts_name='haha',buchi_name='heihei',parent=[])
product_graph.nodes[1]['init']=True
product_graph.nodes[1]['accept']=False
product_graph.nodes[1]['parent'].append(1)
product_graph.nodes[1]['parent'].append(2)

def add_node(product_graph):
    product_graph.add_node(2,name='heihei',ts_name='haha',buchi_name='heihei',parent=[])
    
add_node(product_graph)
