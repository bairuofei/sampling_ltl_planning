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

a=[[1,2,3],[5,6,7],[8,9,10]]
d=[11,12,13]

c=[]
for i in range(0,len(a)):
    c.append([])
    

for i in range(0,len(a)):
    for node in d:
        add_node=[]
        add_node.append(node)
        e=a[i]+add_node
        c[i]=e

