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
buchi_init_states=[]
buchi_accept_states=[]
[buchi_graph,buchi_init_states,buchi_accept_states]=ltl_formula_to_ba(task,LTL_FILE_POS,True)

## 构建乘积自动机
product_init_states=[]  # 记录乘积自动机中初始状态的编号集合
product_accept_states=[]  # 记录乘积自动机中接受状态的编号集合
# 构建乘积自动机并返回三种类型节点集合
[product_graph,product_init_states,product_accept_states]=\
    product_automaton(trans_graph,buchi_graph)
    
product_dot_graph=nx_to_graphviz_product(product_graph)
product_dot_graph.show('product_graph')
        
    


trans_dot_graph=nx_to_graphviz_trans(trans_graph)
trans_dot_graph.show('trans_graph')
    
#init_pos='n1'
#for buchi_init_state in buchi_init_states:
    



try:
    best_path=nx.dijkstra_path(trans_graph,'n1','n3',weight='weight')
    print(best_path)
except nx.NetworkXNoPath:
    print('haha')
