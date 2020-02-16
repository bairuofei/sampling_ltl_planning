# -*- coding: utf-8 -*-
import os
import trans_sys
from gltl2ba import ltl_formula_to_ba
from sampling_func import construct_tree_prefix
from sampling_func import construct_tree_suffix
from sampling_func import pre_find_path
from sampling_func import suf_find_path
from show_graph import nx_to_graphviz_tree
from show_graph import nx_to_graphviz_trans

# transition systems
trans_graph=[]
trans_graph.append(trans_sys.samp_trans_graph1())
trans_graph.append(trans_sys.samp_trans_graph2())

# task formula
task="(<>p14) && ((NOT p14) U p22) && ((NOT p22) U p12) && ([](p12 -> X(NOT p14))) && ((NOT p22) U p24) &&  ([](p24 -> X(NOT p22)))"
surveillance_task=False
# os.getcwd get current work directory
LTL_FILE_POS=os.getcwd()+'/samp_ltlFile.txt'

# initial_location
init_pts=['n1','n1']
itera_pre_num=10000
itera_suf_num=10000

# convert ltl to buchi automaton
buchi_init_states=[]
buchi_accept_states=[]
[buchi_graph,buchi_init_states,buchi_accept_states]=ltl_formula_to_ba(task,LTL_FILE_POS,True)


optimal_path=[[],[]]
optimal_path_cost=[float('inf'),float('inf')]
# for every buchi init state, which means possible tree root
for buchi_init_state in buchi_init_states:
    ## prefix path
    [pre_search_tree,pre_accept_tree_nodes]=construct_tree_prefix(trans_graph,buchi_graph,\
                                    init_pts,buchi_init_state,itera_pre_num)
    print("buchi_init_state: "+buchi_init_state)
    print("tree_accept_nodes: "+str(pre_accept_tree_nodes))
    
    pre_path_list=[]
    pre_path_cost_list=[]
    # for every accept product state in current tree
    for node_index in pre_accept_tree_nodes:
        [pre_path_list,pre_path_cost_list]=\
            pre_find_path(pre_search_tree,node_index,pre_path_list,pre_path_cost_list)
    
    ## suffix path
    suf_path_list=[]
    suf_path_cost_list=[]
    if surveillance_task:   # if has surveillance_task
        # TODO: accept state self loop check
        for node_index in pre_accept_tree_nodes:
            # below line is wrong, as the loop must contain accept status
            # actual_accept_node=pre_search_tree.nodes[node_index]['parent']
            actual_accept_node_index=pre_search_tree.nodes[node_index]['parent']
            actual_accept_node={'pts':pre_search_tree.nodes[actual_accept_node_index]['ts_name'],\
                                'buchi':pre_search_tree.nodes[actual_accept_node_index]['buchi_name']}
            suf_init_pts=pre_search_tree.nodes[node_index]['ts_name']
            suf_init_buchi=pre_search_tree.nodes[node_index]['buchi_name']
            [suf_search_tree,suf_accept_tree_nodes,suf_accept_tree_nodes_costs]=construct_tree_suffix(trans_graph,\
                    buchi_graph,suf_init_pts,suf_init_buchi,actual_accept_node,itera_suf_num)
            # find minimum loop cost
            suf_path=[]
            suf_path_cost=float('inf')
            suf_delta_cost=pre_search_tree.nodes[node_index]['cost']-\
                    pre_search_tree.nodes[actual_accept_node_index]['cost']
            for i in range(0,len(suf_accept_tree_nodes)):
                suf_accept_tree_node=suf_accept_tree_nodes[i]
                suf_one_path_cost=suf_search_tree.nodes[suf_accept_tree_node]['cost']\
                        +suf_accept_tree_nodes_costs[i]\
                        +suf_delta_cost
                if suf_one_path_cost<suf_path_cost:
                    suf_path_cost=suf_one_path_cost
                    suf_path=suf_find_path(suf_search_tree,suf_accept_tree_node,\
                                           actual_accept_node['pts'])
            suf_path_list.append(suf_path)
            suf_path_cost_list.append(suf_path_cost)
    
    else: # if not have surveillance_task
        for node_index in pre_accept_tree_nodes:
            suf_path_list.append([])
            suf_path_cost_list.append(0)
        
    ## find shortest path for a single buchi init state
    buchi_init_path=[[],[]]
    buchi_init_path_cost=[float('inf'),float('inf')]
    for i in range(0,len(pre_accept_tree_nodes)):
        one_init_path_cost=pre_path_cost_list[i]+suf_path_cost_list[i]
        if one_init_path_cost<buchi_init_path_cost[0]+buchi_init_path_cost[1]:
            buchi_init_path_cost[0]=pre_path_cost_list[i]
            buchi_init_path_cost[1]=suf_path_cost_list[i]
            buchi_init_path[0]=pre_path_list[i]
            buchi_init_path[1]=suf_path_list[i]
        
    # now we have best path for one specific init state
    if buchi_init_path_cost[0]+buchi_init_path_cost[1]<\
                                optimal_path_cost[0]+optimal_path_cost[1]:
        optimal_path_cost[0]=buchi_init_path_cost[0]
        optimal_path_cost[1]=buchi_init_path_cost[1]
        optimal_path[0]=buchi_init_path[0]
        optimal_path[1]=buchi_init_path[1]
    
    
print(optimal_path)
print(optimal_path_cost)
#for i in range(0,len(pre_path_list)):
#    print(pre_path_list[i])
#    print('cost = '+str(pre_path_cost_list[i]))
    
# print(search_tree.nodes[28]['name'])


#search_dot_pre_tree=nx_to_graphviz_tree(pre_search_tree)
#search_dot_pre_tree.show('search_tree')

trans_dot_graph1=nx_to_graphviz_trans(trans_graph[0])
trans_dot_graph1.show('trans_graph1')
trans_dot_graph2=nx_to_graphviz_trans(trans_graph[1])
trans_dot_graph2.show('trans_graph2')

# print(search_tree.nodes[19]['name'])
