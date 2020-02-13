# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt

from gltl2ba import ltl_formula_to_ba
from construct_product_automaton import product_automaton
from construct_product_automaton import buchi_label_test

# task formula
task="(<> p1) && (<> p2) && (<> p3) && (<> p4)"
# task="(<> p1) && (<> p2) && (<> p3) && (<> p4) && ([] (p2 -> X (NOT p3)))"
# location of ltlfile.txt storing never claim
LTL_FILE_POS='/home/buffa/git_buffa_ubuntu/sampling_ltl_planning/ltlFile.txt'
# convert ltl to buchi automaton
buchi_init_state=[]
buchi_accept_state=[]
[buchi_graph,buchi_init_state,buchi_accept_state]=ltl_formula_to_ba(task,LTL_FILE_POS, True)

# construct weighted transition system
weight_list=[3,5,3,2,4]
trans_graph=nx.DiGraph()
trans_graph.add_node('n1',name='n1',label=['p1'])
trans_graph.add_node('n2',name='n2',label=['p2'])
trans_graph.add_node('n3',name='n3',label=['p3'])
trans_graph.add_node('n4',name='n4',label=['p4'])
trans_graph.add_edge('n1','n2',weight=weight_list[0])
trans_graph.add_edge('n1','n3',weight=weight_list[3])
trans_graph.add_edge('n2','n3',weight=weight_list[4])
trans_graph.add_edge('n2','n4',weight=weight_list[1])
trans_graph.add_edge('n3','n4',weight=weight_list[2])
trans_graph.add_edge('n2','n1',weight=weight_list[0])
trans_graph.add_edge('n3','n1',weight=weight_list[3])
trans_graph.add_edge('n3','n2',weight=weight_list[4])
trans_graph.add_edge('n4','n2',weight=weight_list[1])
trans_graph.add_edge('n4','n3',weight=weight_list[2])

trans_graph.add_edge('n1','n1',weight=1)
trans_graph.add_edge('n2','n2',weight=1)
trans_graph.add_edge('n3','n3',weight=1)
trans_graph.add_edge('n4','n4',weight=1)

# extract buchi graph. TYPE: digraph


## 构建乘积自动机
init_node_list=[]  # 记录乘积自动机中初始状态的编号集合
accept_node_list=[]  # 记录乘积自动机中接受状态的编号集合
other_node_list=[]  # 其它状态的编号集合
# 构建乘积自动机并返回三种类型节点集合
[product_graph,init_node_list,accept_node_list]=\
    product_automaton(trans_graph,buchi_graph);
      
# 绘制乘积自动机
plt.figure()
pos=nx.spring_layout(product_graph)
nx.draw(product_graph,pos,with_labels = True,font_size =15, node_size =4,alpha=0.7)
# edge_labels = nx.get_edge_attributes(product_graph,'weight')
# nx.draw_networkx_edge_labels(product_graph,pos,labels = edge_labels)
nx.draw_networkx_nodes(product_graph, pos, nodelist=init_node_list, node_color='g') # init点为绿色
nx.draw_networkx_nodes(product_graph, pos, nodelist=accept_node_list, node_color='r') # accept点为红色
nx.draw_networkx_nodes(product_graph, pos, nodelist=other_node_list, node_color='y')  # 普通点为蓝色
plt.show()

# plot weighted transition system
plt.figure()
pos=nx.spring_layout(trans_graph)
nx.draw(trans_graph,pos,with_labels = True)
edge_labels = nx.get_edge_attributes(trans_graph,'weight')
nx.draw_networkx_edge_labels(trans_graph,pos,labels = edge_labels)
plt.show()

# 绘出buchi自动机
plt.figure()
nx.draw(buchi_graph,with_labels = True)
plt.show()




# 指定迁移系统的初始状态集合
initial_ts_state='n1'
# 指定目标状态
target_ts_state='n4'
# 指定buchi自动机的初始状态
initial_buchi_state='T0_init'
# 确定乘积自动机的初始状态
initial_product_state=[] # 乘积自动机初始状态集合，与TS系统的初始状态相关
for initial_next_bstate in buchi_graph[initial_buchi_state]: # initial_buchi_state的邻节点
    if buchi_label_test(buchi_graph[initial_buchi_state][initial_next_bstate]['label'],\
                        trans_graph.node[initial_ts_state]['label'])==1:  # 说明在乘积自动机的起点集合中
        for i in range(0,len(product_graph)):
            if product_graph.node[i]['name']==initial_ts_state+','+initial_next_bstate:
                initial_product_state.append(i)
                break
for j in accept_node_list:
    if product_graph.node[j]['ts_name']==target_ts_state:
        print(j)
        target_point=j
        continue
best_path=[]
best_path_weight=float("inf")
for i in initial_product_state:
    result_path_length=nx.dijkstra_path_length(product_graph,i,target_point,weight='weight')
    if result_path_length<best_path_weight:
        best_path_weight=result_path_length
        best_path=nx.dijkstra_path(product_graph,i,target_point,weight='weight')
print('best path node list:')       
print(best_path)
for i in range(0,len(best_path)):
    print(product_graph.node[best_path[i]])
    if i+1!=len(best_path):
        print(product_graph[best_path[i]][best_path[i+1]]['label']) 
print('best path weight:') 
print(best_path_weight)     





