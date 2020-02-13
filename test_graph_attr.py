# -*- coding: utf-8 -*-
import networkx as nx
product_graph=nx.DiGraph()
product_graph.add_node(1,name='haha,heihei',ts_name='haha',buchi_name='heihei')
product_graph.nodes[1]['init']=True
product_graph.nodes[1]['accept']=False

