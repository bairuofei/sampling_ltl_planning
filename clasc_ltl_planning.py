# -*- coding: utf-8 -*-
import os
import networkx as nx
from gltl2ba import ltl_formula_to_ba
from classical_func import product_automaton
from classical_func import product_transition
from show_graph import nx_to_graphviz_trans
from show_graph import nx_to_graphviz_product
import trans_sys

## Transition system
trans_graph_list=[]
trans_graph_list.append(trans_sys.clasc_trans_graph1())
trans_graph_list.append(trans_sys.clasc_trans_graph2())
trans_graph=product_transition(trans_graph_list)

# LTL task formula
SURVEILLANCE=True   # !!!!!!!!!! ATTENTION !!!!!!!!!
task="([]<> p23) && ([]<> p21) && ((NOT p23) U p13)"
# task="(<>p22) && ((NOT p22) U p24) && ([](p24 -> X(NOT p22)))"
# os.getcwd get current work directory
LTL_FILE_POS=os.getcwd()+'/clasc_ltlFile.txt'

## Init position
init_pos=['n1','n1']
init_pos_organize=[]
for pos in init_pos:
    init_pos_organize.append(pos)

# convert ltl to buchi automaton
buchi_init_states=[]
buchi_accept_states=[]
[buchi_graph,buchi_init_states,buchi_accept_states,buchi_dot_graph]=ltl_formula_to_ba(task,LTL_FILE_POS)

## 构建乘积自动机
product_init_states=[]  # states have "init" 
product_accept_states=[]  # states have "accept"
# 构建乘积自动机并返回三种类型节点集合
[product_graph,product_init_states,product_accept_states]=\
    product_automaton(trans_graph,buchi_graph)
    
    
trans_dot_graph=nx_to_graphviz_trans(trans_graph)
trans_dot_graph.show('clasc_trans_graph')

buchi_dot_graph.show('clasc_buchi_graph')

product_dot_graph=nx_to_graphviz_product(product_graph)
# product_dot_graph.show('clasc_product_graph')        


    


# best path for specific init state
single_init_best_path={'whole_path':[],'pre_path':[],'suf_path':[]}
single_init_path_length={'whole_path':float("inf"),'pre_path':float("inf"),'suf_path':float("inf")}
best_path={'whole_path':[],'pre_path':[],'suf_path':[]}
best_path_length={'whole_path':float("inf"),'pre_path':float("inf"),'suf_path':float("inf")}

search_init_states=[]  # init state to search
for product_init_state in product_init_states:
    if product_graph.nodes[product_init_state]['ts_name']==str(init_pos_organize):
        # if more than one init state in NBA, then so as the product init state
        search_init_states.append(product_init_state)
for search_init_state in search_init_states:
    prefix_path=[]
    prefix_path_length=float("inf")  
    # for all accept states, find minimize prefix path
    for product_accept_state in product_accept_states:

        try:
            one_pre_path=nx.dijkstra_path(product_graph,\
                        search_init_state,product_accept_state,weight='weight')
            one_pre_path_length=nx.dijkstra_path_length(product_graph,\
                        search_init_state,one_pre_path[-2],weight='weight')
            if one_pre_path_length<prefix_path_length:
                prefix_path_length=one_pre_path_length
                prefix_path=one_pre_path
        except nx.NetworkXNoPath:
            print('[Prefix ATTENTION], node '+str(search_init_state)+' to node '+\
                  str(product_accept_state)+' has no path!!')
            continue
        
    if SURVEILLANCE:
        suffix_path=[]
        suffix_path_length=float("inf")
        for product_accept_state in product_accept_states:
            if product_accept_state in list(product_graph[prefix_path[-2]]):
                try:
                    one_suf_path=nx.dijkstra_path(product_graph,product_accept_state,\
                                        prefix_path[-2],weight='weight')
                    one_suf_path_length=nx.dijkstra_path_length(product_graph,\
                            product_accept_state,prefix_path[-2],weight='weight')
                    one_suf_path_length+=product_graph[prefix_path[-2]][product_accept_state]['weight']
                    if one_suf_path_length<suffix_path_length:
                        suffix_path_length=one_suf_path_length
                        suffix_path=one_suf_path
                except nx.NetworkXNoPath:
                    print('[Suffix ATTENTION], node '+str(product_accept_state)+' to node '+\
                      str(prefix_path[-2])+' has no path!!')
                    continue

        single_init_best_path['pre_path']=prefix_path[:-1]
        single_init_best_path['suf_path']=suffix_path
        single_init_best_path['whole_path']=single_init_best_path['pre_path']+\
                single_init_best_path['suf_path']
        single_init_path_length['pre_path']=prefix_path_length
        single_init_path_length['suf_path']=suffix_path_length
        single_init_path_length['whole_path']=prefix_path_length+suffix_path_length
        
    else:
        single_init_best_path['whole_path']=prefix_path[:-1]
        single_init_best_path['pre_path']=prefix_path[:-1]
        # no suffix path
        single_init_path_length['pre_path']=prefix_path_length
        single_init_path_length['suf_path']=0
        single_init_path_length['whole_path']=single_init_path_length['pre_path']
        
    if single_init_path_length['whole_path']<best_path_length['whole_path']:
        best_path_length=single_init_path_length
        best_path=single_init_best_path
        
    
best_pre_path_trans=[]
for i in range(0,len(best_path['pre_path'])):
    best_pre_path_trans.append(product_graph.node[best_path['pre_path'][i]]['ts_name'])
best_suf_path_trans=[]
for i in range(0,len(best_path['suf_path'])):
    best_suf_path_trans.append(product_graph.node[best_path['suf_path'][i]]['ts_name'])
best_path_trans=best_pre_path_trans+best_suf_path_trans 

print('best path: '+str(best_path_trans))
print('best prefix path: '+str(best_pre_path_trans))
print('best suffix path: '+str(best_suf_path_trans))     
print('best path weight:'+str(best_path_length['whole_path'])) 
print('pre weight: '+str(best_path_length['pre_path'])+\
      ', suf weight: '+str(best_path_length['suf_path'])) 
robot_path_list=[]
for i in range(0,len(trans_graph_list)):
    robot_path_list.append([])
for i in range(0,len(trans_graph_list)):
    for node in best_pre_path_trans:
        robot_path_list[i].append(trans_graph.nodes[node]['ts_list'][i])
    robot_path_list[i].append('+')
    for node in best_suf_path_trans:
        robot_path_list[i].append(trans_graph.nodes[node]['ts_list'][i])
    print('Robot '+str(i)+': '+str(robot_path_list[i]))


