# -*- coding: utf-8 -*-
import networkx as nx
product_graph=nx.DiGraph()
product_graph.add_node(1,name='haha,heihei',ts_name='haha',buchi_name='heihei',parent=[])
product_graph.nodes[1]['init']=True
product_graph.nodes[1]['accept']=False
product_graph.nodes[1]['parent'].append(1)
product_graph.nodes[1]['parent'].append(2)

trans_graph=nx.DiGraph()
trans_graph.add_node('n1',name='n1',label=['p1'])
trans_graph.add_node('n2',name='n2',label=['p2'])
trans_graph.add_node('n3',name='n3',label=['p3'])
trans_graph.add_edge('n1','n2',weight=3)
trans_graph.add_edge('n2','n3',weight=3)
trans_graph.add_edge('n1','n3',weight=1)
trans_graph.add_edge('n2','n1',weight=3)
trans_graph.add_edge('n3','n2',weight=3)
trans_graph.add_edge('n3','n1',weight=1)
trans_graph.add_edge('n1','n1',weight=0.1)
trans_graph.add_edge('n2','n2',weight=0.1)
trans_graph.add_edge('n3','n3',weight=0.1)
trans_graph.remove_edge('n1','n3')
