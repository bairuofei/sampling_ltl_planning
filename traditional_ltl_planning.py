# -*- coding: utf-8 -*-
import os
import networkx as nx
from gltl2ba import ltl_formula_to_ba
from construct_product_automaton import product_automaton
# from construct_product_automaton import buchi_label_test
from show_graph import nx_to_graphviz_trans
from show_graph import nx_to_graphviz_product

weight_list=[3,5,3,2,4]
trans_graph=nx.DiGraph()
trans_graph.add_node('n1',name='n1',label=['p1'])
trans_graph.add_node('n2',name='n2',label=['p2'])
trans_graph.add_node('n3',name='n3',label=['p3'])
trans_graph.add_edge('n1','n2',weight=3)
trans_graph.add_edge('n2','n3',weight=5)
trans_graph.add_edge('n1','n3',weight=1)
trans_graph.add_edge('n2','n1',weight=3)
trans_graph.add_edge('n3','n2',weight=5)
trans_graph.add_edge('n3','n1',weight=1)
trans_graph.add_edge('n1','n1',weight=0)
trans_graph.add_edge('n2','n2',weight=0)
trans_graph.add_edge('n3','n3',weight=0)

# task formula
task="(<> p1) && (<> p2) && (<> p3) && ([](p3 -> X (NOT p2))) && ((NOT p3) U p2)"
# os.getcwd get current work directory
LTL_FILE_POS=os.getcwd()+'/ltlFile.txt'

# convert ltl to buchi automaton
buchi_init_states=[]
buchi_accept_states=[]
[buchi_graph,buchi_init_states,buchi_accept_states]=ltl_formula_to_ba(task,LTL_FILE_POS,True)

## 构建乘积自动机
product_init_states=[]  # states have "init" 
product_accept_states=[]  # states have "accept"
# 构建乘积自动机并返回三种类型节点集合
[product_graph,product_init_states,product_accept_states]=\
    product_automaton(trans_graph,buchi_graph)
    
product_dot_graph=nx_to_graphviz_product(product_graph)
product_dot_graph.show('product_graph')
        
    


trans_dot_graph=nx_to_graphviz_trans(trans_graph)
trans_dot_graph.show('trans_graph')
    
init_pos='n1'

best_path=[]
best_path_length=float("inf")
search_init_states=[]  # init state to search
for product_init_state in product_init_states:
    if product_graph.nodes[product_init_state]['ts_name']==init_pos:
        search_init_states.append(product_init_state)
for search_init_state in search_init_states:
    for product_accept_state in product_accept_states:
        try:
            one_path=nx.dijkstra_path(product_graph,\
                        search_init_state,product_accept_state,weight='weight')
            one_path_length=nx.dijkstra_path_length(product_graph,\
                        search_init_state,one_path[-2],weight='weight')
            if one_path_length<best_path_length:
                best_path_length=one_path_length
                best_path=one_path
        except nx.NetworkXNoPath:
            print('ATTENTION, node '+str(search_init_state)+' to node '+\
                  str(product_accept_state)+' has no path!!')
            
best_path_trans=[]
for i in range(0,len(best_path)-1):
    best_path_trans.append(product_graph.node[best_path[i]]['ts_name'])
print('best path:')  
print(best_path_trans)      
print('best path weight:') 
print(best_path_length)  
for i in range(0,len(best_path)):
    print(product_graph.node[best_path[i]])
    if i+1!=len(best_path):
        print(product_graph[best_path[i]][best_path[i+1]]['label']) 


