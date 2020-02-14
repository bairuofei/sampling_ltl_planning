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
trans_graph.add_edge('n1','n1',weight=0.1)
trans_graph.add_edge('n2','n2',weight=0.1)
trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero

# task formula
task="(<> p1) && ([](<> p2)) && ([](<> p3))"
surveillance_task=True
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

# best path for specific init state
single_init_best_path={'whole_path':[],'pre_path':[],'suf_path':[]}
single_init_path_length={'whole_path':float("inf"),'pre_path':float("inf"),'suf_path':float("inf")}
best_path={'whole_path':[],'pre_path':[],'suf_path':[]}
best_path_length={'whole_path':float("inf"),'pre_path':float("inf"),'suf_path':float("inf")}

search_init_states=[]  # init state to search
for product_init_state in product_init_states:
    if product_graph.nodes[product_init_state]['ts_name']==init_pos:
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
        
    if surveillance_task:
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
    best_pre_path_trans.append(product_graph.node[best_path['pre_path'][i]]['name'])
best_suf_path_trans=[]
for i in range(0,len(best_path['suf_path'])):
    best_suf_path_trans.append(product_graph.node[best_path['suf_path'][i]]['name'])
best_path_trans=best_pre_path_trans+best_suf_path_trans 

print('best path: '+str(best_path_trans))
print('best prefix path: '+str(best_pre_path_trans))
print('best suffix path: '+str(best_suf_path_trans))     
print('best path weight:'+str(best_path_length['whole_path'])) 
print('pre weight: '+str(best_path_length['pre_path'])+\
      ', suf weight: '+str(best_path_length['suf_path'])) 


#search_init_states=[]  # init state to search
#for product_init_state in product_init_states:
#    if product_graph.nodes[product_init_state]['ts_name']==init_pos:
#        # if more than one init state in NBA, then so as the product init state
#        search_init_states.append(product_init_state)
#for search_init_state in search_init_states:
#    prefix_path=[]
#    prefix_path_length=float("inf")  
#    # for all accept states, find minimize prefix path
#    for product_accept_state in product_accept_states:
#
#        try:
#            one_pre_path=nx.dijkstra_path(product_graph,\
#                        search_init_state,product_accept_state,weight='weight')
#            one_pre_path_length=nx.dijkstra_path_length(product_graph,\
#                        search_init_state,product_accept_state,weight='weight')
#            if one_pre_path_length<prefix_path_length:
#                prefix_path_length=one_pre_path_length
#                prefix_path=one_pre_path
#        except nx.NetworkXNoPath:
#            print('[Prefix ATTENTION], node '+str(search_init_state)+' to node '+\
#                  str(product_accept_state)+' has no path!!')
#            continue
#        
#    if surveillance_task:
#        suffix_target_nodes=product_graph.nodes[prefix_path[-2]]['parent']
#        suffix_path=[]
#        suffix_path_length=float("inf")
#        for suffix_target_node in suffix_target_nodes:
#            try:
#                one_suf_path=nx.dijkstra_path(product_graph,prefix_path[-2],\
#                                        suffix_target_node,weight='weight')
#                one_suf_path_length=nx.dijkstra_path_length(product_graph,\
#                            prefix_path[-2],suffix_target_node,weight='weight')
#                one_suf_path_length+=product_graph[suffix_target_node][prefix_path[-2]]['weight']
#                if one_suf_path_length<suffix_path_length:
#                    suffix_path_length=one_suf_path_length
#                    suffix_path=one_suf_path
#            except nx.NetworkXNoPath:
#                print('[Suffix ATTENTION], node '+str(prefix_path[-2])+' to node '+\
#                  str(suffix_target_node)+' has no path!!')
#                continue
#        single_init_best_path['pre_path']=prefix_path[:-1]
#        single_init_best_path['suf_path']=suffix_path[1:]+suffix_path[0:1]
#        single_init_best_path['whole_path']=single_init_best_path['pre_path']+\
#                single_init_best_path['suf_path']
#        single_init_path_length['pre_path']=prefix_path_length-product_graph[prefix_path[-2]]\
#                [prefix_path[-1]]['weight']
#        single_init_path_length['suf_path']=suffix_path_length
#        single_init_path_length['whole_path']=prefix_path_length+suffix_path_length
#        
#    else:
#        single_init_best_path['whole_path']=prefix_path[:-1]
#        single_init_best_path['pre_path']=prefix_path[:-1]
#        # no suffix path
#        single_init_path_length['whole_path']=prefix_path_length-product_graph[prefix_path[-2]]\
#                [prefix_path[-1]]['weight']
#        single_init_path_length['pre_path']=single_init_path_length['whole_path']
#        single_init_path_length['suf_path']=0
#    
#    if single_init_path_length['whole_path']<best_path_length['whole_path']:
#        best_path_length=single_init_path_length
#        best_path=single_init_best_path
#    
#best_pre_path_trans=[]
#for i in range(0,len(best_path['pre_path'])):
#    best_pre_path_trans.append(product_graph.node[best_path['pre_path'][i]]['name'])
#best_suf_path_trans=[]
#for i in range(0,len(best_path['suf_path'])):
#    best_suf_path_trans.append(product_graph.node[best_path['suf_path'][i]]['name'])
#best_path_trans=best_pre_path_trans+best_suf_path_trans 
#
#print('best path: '+str(best_path_trans))
#print('best prefix path: '+str(best_pre_path_trans))
#print('best suffix path: '+str(best_suf_path_trans))     
#print('best path weight:'+str(best_path_length['whole_path'])) 
#print('pre weight: '+str(best_path_length['pre_path'])+\
#      ', suf weight: '+str(best_path_length['suf_path'])) 






#best_path=[]
#best_path_length=float("inf")
#search_init_states=[]  # init state to search
#for product_init_state in product_init_states:
#    if product_graph.nodes[product_init_state]['ts_name']==init_pos:
#        # if more than one init state in NBA, then so as the product init state
#        search_init_states.append(product_init_state)
#for search_init_state in search_init_states:
#    for product_accept_state in product_accept_states:
#        try:
#            one_path=nx.dijkstra_path(product_graph,\
#                        search_init_state,product_accept_state,weight='weight')
#            one_path_length=nx.dijkstra_path_length(product_graph,\
#                        search_init_state,one_path[-2],weight='weight')
#            if one_path_length<best_path_length:
#                best_path_length=one_path_length
#                best_path=one_path
#        except nx.NetworkXNoPath:
#            print('ATTENTION, node '+str(search_init_state)+' to node '+\
#                  str(product_accept_state)+' has no path!!')
#            
#best_path_trans=[]
#for i in range(0,len(best_path)-1):
#    best_path_trans.append(product_graph.node[best_path[i]]['ts_name'])
#print('best path:')  
#print(best_path_trans)      
#print('best path weight:') 
#print(best_path_length)  
#for i in range(0,len(best_path)):
#    print(product_graph.node[best_path[i]])
#    if i+1!=len(best_path):
#        print(product_graph[best_path[i]][best_path[i+1]]['label']) 


