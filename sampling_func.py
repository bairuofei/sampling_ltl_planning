# -*- coding: utf-8 -*-
import random
import networkx as nx
from general_func import buchi_label_test
from general_func import pts_trans_check
from general_func import pts_trans_cost
from general_func import product_trans_check


def search_tree_init(init_pts,trans_graph,buchi_init_state):
    """
    init_pts: tpye list. eg: init_pts=['n1','n1']
    buchi_accept_state: type str. eg: buchi_accept_state='accept_all'
    """
    search_tree=nx.DiGraph()
    search_tree.add_node(0,\
                         name=str(init_pts)+', '+buchi_init_state,\
                         ts_name=init_pts,\
                         ts_label=[],\
                         buchi_name=buchi_init_state,\
                         parent=-1,\
                         children=[],\
                         cost=0)
    for i in range(0,len(init_pts)):
        search_tree.nodes[0]['ts_label']+=trans_graph[i].nodes[init_pts[i]]['label']
    return search_tree
    

def sample(search_tree,trans_graph):
    """
    return list type pts_new
    """
    p_rand=random.randint(0,len(search_tree)-1)
    pts_rand=search_tree.nodes[p_rand]['ts_name'] # list
    pts_new=[]
    pts_index=0
    for ts_node in pts_rand:
        ts_graph=trans_graph[pts_index]
        ts_children=ts_graph.nodes[ts_node]['children'] # list
        ts_rand=random.randint(0,len(ts_children)-1)
        pts_new.append(ts_children[ts_rand])
        pts_index+=1
    return pts_new


    

def extend(search_tree,trans_graph,buchi_graph,p_new):
    """
    trans entry, search_tree will be changed
    """
    # state in tree that can reach p_new
    pre_p_new=-1
    pre_p_new_cost=float('inf')
    for i in range(0,len(search_tree)):
        # buchi transition check
        if p_new['buchi'] in buchi_graph[search_tree.nodes[i]['buchi_name']]:
            # pts transiton check           
            if pts_trans_check(search_tree.nodes[i]['ts_name'],p_new['pts'],trans_graph)==1:
                buchi_label=buchi_graph[search_tree.nodes[i]['buchi_name']][p_new['buchi']]['label']
                ts_node_label=search_tree.nodes[i]['ts_label']
                # product transition check
                if buchi_label_test(buchi_label,ts_node_label)==1:
                    pts_trans_cost_value=pts_trans_cost(search_tree.nodes[i]['ts_name'],\
                                                        p_new['pts'],trans_graph)
                    if pts_trans_cost_value<pre_p_new_cost:
                        pre_p_new=i
                        pre_p_new_cost=pts_trans_cost_value     

    if pre_p_new ==-1: # new node can not be added into the tree
        return -1
    else: # new node will be added into the tree
        # add the node into the tree
        tree_node_index=len(search_tree)
        parent_node_cost=search_tree.nodes[pre_p_new]['cost']
        search_tree.add_node(tree_node_index,\
                             name=str(p_new['pts'])+', '+p_new['buchi'],\
                             ts_name=p_new['pts'],\
                             ts_label=[],\
                             buchi_name=p_new['buchi'],\
                             parent=pre_p_new,\
                             children=[],\
                             cost=parent_node_cost+pre_p_new_cost)
        for i in range(0,len(p_new['pts'])):
            search_tree.nodes[tree_node_index]['ts_label']+=\
                     trans_graph[i].nodes[p_new['pts'][i]]['label']
        # add edge into the tree
        search_tree.add_edge(pre_p_new,tree_node_index,weight=pre_p_new_cost,\
                             label=buchi_graph[search_tree.nodes[pre_p_new]['buchi_name']][search_tree.nodes[tree_node_index]['buchi_name']]['label'])
        # modify parent node's children attr
        search_tree.nodes[pre_p_new]['children'].append(tree_node_index)
        return tree_node_index

        
        
def update_subtree_cost(search_tree,subtree_root,delta_cost):
    """
    after rewiring, update node cost in the subtree of rewiring node.
    delta_cost: positive. All the node cost in subtree should minus the value.
    """
    search_queue=[]
    search_queue+=search_tree.nodes[subtree_root]['children']
    while len(search_queue)!=0:
        pop_node=search_queue.pop(len(search_queue)-1)
        search_tree.nodes[pop_node]['cost']-=delta_cost
        if len(search_tree.nodes[pop_node]['children'])>0:
            search_queue+=search_tree.nodes[pop_node]['children']



        
    
    
        
def rewire(search_tree,trans_graph,buchi_graph,node_tree_check_value):
    p_not_new={'pts':search_tree.nodes[node_tree_check_value]['ts_name'],\
               'buchi':search_tree.nodes[node_tree_check_value]['buchi_name']}
    for i in range(0,len(search_tree)):
        # check if new node is ndoe i
        if i==node_tree_check_value:
            continue
        else:
            suf_node={'pts':search_tree.nodes[i]['ts_name'],\
                      'buchi':search_tree.nodes[i]['buchi_name']}
            if product_trans_check(trans_graph,buchi_graph,p_not_new,suf_node)==1:
                pts_trans_cost_value=pts_trans_cost(p_not_new['pts'],\
                        search_tree.nodes[i]['ts_name'],trans_graph)
                reachable_node_cost=search_tree.nodes[i]['cost']
                current_node_cost=search_tree.nodes[node_tree_check_value]['cost']
                rewire_cost=current_node_cost+pts_trans_cost_value
                if rewire_cost<reachable_node_cost:
                    # rewiring
                    reachable_node_parent=search_tree.nodes[i]['parent']
                    search_tree.remove_edge(reachable_node_parent,i)
                    search_tree.add_edge(node_tree_check_value,i,weight=rewire_cost,\
                                label=buchi_graph[search_tree.nodes[node_tree_check_value]['buchi_name']]\
                                    [search_tree.nodes[i]['buchi_name']]['label'])
                    # parent modify
                    search_tree.nodes[i]['parent']=node_tree_check_value
                    # cost modify
                    search_tree.nodes[i]['cost']=rewire_cost
                    # children modify
                    search_tree.nodes[node_tree_check_value]['children'].append(i)
                    search_tree.nodes[reachable_node_parent]['children'].remove(i)
                    delta_cost=reachable_node_cost-rewire_cost
                    update_subtree_cost(search_tree,i,delta_cost)
            
    
def node_in_tree_check(search_tree,p_new):
    """
    input: 
        p_new: type dict. Two key:'pts',type list; 'buchi',type str        
    output: in: return index
            not in: return -1
    """
    p_new_str=str(p_new['pts'])+', '+p_new['buchi']
    for k in range(0,len(search_tree)):
        if search_tree.nodes[k]['name']==p_new_str:
            return k
    return -1
    
    
def construct_tree_prefix(trans_graph,buchi_graph,init_pts,buchi_init_state,itera_pre_num):
    search_tree=search_tree_init(init_pts,trans_graph,buchi_init_state)
    accept_tree_nodes=[]
    for i in range(0,itera_pre_num):
        pts_new=sample(search_tree,trans_graph) # list
        buchi_state_list=list(buchi_graph.nodes)
        for j in range(0,len(buchi_state_list)):
            b_new=buchi_state_list[j]
            p_new={'pts':pts_new,'buchi':b_new}
            # check if new node already exists
            node_tree_check_value=node_in_tree_check(search_tree,p_new)
            if node_tree_check_value==-1:
                new_node_index=extend(search_tree,trans_graph,buchi_graph,p_new)     
                if new_node_index!=-1:
                    if p_new['buchi'].find('accept')!=-1:
                        accept_tree_nodes.append(new_node_index)
            else:
                rewire(search_tree,trans_graph,buchi_graph,node_tree_check_value)
    return search_tree,accept_tree_nodes
    
def pre_find_path(search_tree,accept_tree_node,pre_path_list,pre_path_cost_list):
    """
    input: search tree, current accept state index, pre_path_cost_list
    output: prefix path, list type, whose element type is also list.
            pre_path_cost_list, store each path's cost
    """
    pre_path=[]
    backtrack_node=search_tree.nodes[accept_tree_node]['parent']
    pre_path_cost_list.append(search_tree.nodes[backtrack_node]['cost'])
    while backtrack_node!=-1:
        pre_path=[search_tree.nodes[backtrack_node]['ts_name']]+pre_path
        backtrack_node=search_tree.nodes[backtrack_node]['parent']
    if len(pre_path)!=0:
        pre_path_list.append(pre_path)
    return pre_path_list,pre_path_cost_list


def suf_find_path(search_tree,accept_tree_node,actual_accept_node_pts):
    """
    input: search tree, 
           accept_tree_node: type int, node index
           actual_accept_node_pts: type list       
    output: suf_path: path list, whose element is also list
    """
    suf_path=[]
    suf_path.append(search_tree.nodes[accept_tree_node]['ts_name'])
    backtrack_node=search_tree.nodes[accept_tree_node]['parent']
    while backtrack_node!=-1:
        suf_path=[search_tree.nodes[backtrack_node]['ts_name']]+suf_path
        backtrack_node=search_tree.nodes[backtrack_node]['parent']
    suf_path.append(actual_accept_node_pts)
    return suf_path



def construct_tree_suffix(trans_graph,buchi_graph,init_pts,buchi_init_state,actual_accept_node,itera_suf_num):
    search_tree=search_tree_init(init_pts,trans_graph,buchi_init_state)
    accept_tree_nodes=[]
    accept_tree_nodes_costs=[]
    for i in range(0,itera_suf_num):
        pts_new=sample(search_tree,trans_graph) # list
        buchi_state_list=list(buchi_graph.nodes)
        for j in range(0,len(buchi_state_list)):
            b_new=buchi_state_list[j]
            p_new={'pts':pts_new,'buchi':b_new}
            # check if new node already exists
            node_tree_check_value=node_in_tree_check(search_tree,p_new)
            if node_tree_check_value==-1:
                new_node_index=extend(search_tree,trans_graph,buchi_graph,p_new)     
                if new_node_index!=-1: # new node is added into the tree successfully
                    pre_node={'pts':search_tree.nodes[new_node_index]['ts_name'],\
                              'buchi':search_tree.nodes[new_node_index]['buchi_name']}
                    # check if it is the accept state
                    if product_trans_check(trans_graph,buchi_graph,pre_node,actual_accept_node)==1:
                        accept_tree_nodes.append(new_node_index)
                        accept_tree_nodes_costs.append(pts_trans_cost(pre_node['pts'],\
                                        actual_accept_node['pts'],trans_graph))
            else:
                rewire(search_tree,trans_graph,buchi_graph,node_tree_check_value)
    return search_tree,accept_tree_nodes,accept_tree_nodes_costs

