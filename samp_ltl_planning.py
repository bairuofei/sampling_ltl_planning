# -*- coding: utf-8 -*-
import os
import trans_sys
from gltl2ba import ltl_formula_to_ba
from sampling_func import construct_tree
from show_graph import nx_to_graphviz_tree
from show_graph import nx_to_graphviz_trans

# transition systems
trans_graph=[]
trans_graph.append(trans_sys.samp_trans_graph1())
trans_graph.append(trans_sys.samp_trans_graph2())

# task formula
task="(<> p23) && ((NOT p22) U p12) && ([](p23 -> p11)) && ((NOT p23) U p13)"
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

minimum_cost_tree_node=-1
tree_minimum_cost=float('inf')

for buchi_init_state in buchi_init_states:
    [search_tree,accept_tree_nodes]=construct_tree(trans_graph,buchi_graph,\
                                    init_pts,buchi_init_state,itera_pre_num)
    print("buchi_init_state: "+buchi_init_state)
    print("tree_accept_nodes: "+str(accept_tree_nodes))
    for node_index in accept_tree_nodes:
        if search_tree.nodes[node_index]['cost']<tree_minimum_cost:
            minimum_cost_tree_node=node_index
            tree_minimum_cost=search_tree.nodes[node_index]['cost']
        print("node "+str(node_index)+": "+search_tree.nodes[node_index]['name']+'  cost='+\
              str(search_tree.nodes[node_index]['cost']))
    print('len(tree)='+str(len(search_tree)))

pre_path_list=[]
backtrack_node=search_tree.nodes[minimum_cost_tree_node]['parent']
while backtrack_node!=-1:
    append_list=[search_tree.nodes[backtrack_node]['ts_name']]
    pre_path_list=append_list+pre_path_list
    backtrack_node=search_tree.nodes[backtrack_node]['parent']

print('Best prefix path: '+str(pre_path_list))

search_dot_tree=nx_to_graphviz_tree(search_tree)
search_dot_tree.show('search_tree')

trans_dot_graph1=nx_to_graphviz_trans(trans_graph[0])
trans_dot_graph1.show('trans_graph1')
trans_dot_graph2=nx_to_graphviz_trans(trans_graph[1])
trans_dot_graph2.show('trans_graph2')

# print(search_tree.nodes[19]['name'])
