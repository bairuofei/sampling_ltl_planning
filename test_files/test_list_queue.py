# -*- coding: utf-8 -*-
import networkx as nx

trans_graph=nx.DiGraph()
trans_graph.add_node(1,label=['p1'],visit=False)
trans_graph.add_node(2,label=['p2'],visit=False)
trans_graph.add_node(3,label=['p3'],visit=False)
trans_graph.add_node(4,label=['p1'],visit=False)
trans_graph.add_node(5,label=['p2'],visit=False)
trans_graph.add_node(6,label=['p3'],visit=False)
trans_graph.add_node(7,label=['p1'],visit=False)
trans_graph.add_node(8,label=['p2'],visit=False)
trans_graph.add_node(9,label=['p3'],visit=False)
trans_graph.add_edge(1,2,weight=3)
trans_graph.add_edge(1,3,weight=3)
trans_graph.add_edge(1,4,weight=3)
trans_graph.add_edge(2,5,weight=3)
trans_graph.add_edge(2,6,weight=3)
trans_graph.add_edge(3,7,weight=3)
trans_graph.add_edge(3,8,weight=3)
trans_graph.add_edge(7,9,weight=3)

for i in range(1,len(trans_graph)+1):
    trans_graph.nodes[i]['children']=list(trans_graph[i])

def dfs(trans_graph,root_node):
    search_queue=[]
    search_queue.append(root_node)  
    while len(search_queue)!=0:
        pop_node=search_queue.pop(len(search_queue)-1)
        trans_graph.nodes[pop_node]['visit']=True
        print(pop_node)
        if len(trans_graph.nodes[pop_node]['children'])>0:
            search_queue+=trans_graph.nodes[pop_node]['children']
            
    
dfs(trans_graph,1)