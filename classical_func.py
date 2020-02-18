# -*- coding: utf-8 -*-
import time
import networkx as nx
from general_func import pts_trans_check
from general_func import pts_trans_cost
from general_func import buchi_label_test


def product_automaton(trans_graph,buchi_graph):
    product_graph=nx.DiGraph()
    init_node_list=[]  # 记录乘积自动机中初始状态的编号集合
    accept_node_list=[]  # 记录乘积自动机中接受状态的编号集合
    # 构建状态
    trans_node_set=trans_graph.nodes()
    buchi_node_set=buchi_graph.nodes()
    product_add_node_index=0
    for trans_node in trans_node_set:
        for buchi_node in buchi_node_set:
            # ts_name: type str
            product_graph.add_node(product_add_node_index,\
                                   name=str(trans_node)+','+buchi_node,\
                                   ts_name=str(trans_node),\
                                   buchi_name=buchi_node,\
                                   init=False,\
                                   accept=False,\
                                   parent=[])      
            if buchi_node.find('init')!=-1:  # 起始节点
                init_node_list.append(product_add_node_index)
                product_graph.nodes[product_add_node_index]['init']=True
            elif buchi_node.find('accept')!=-1:  #终止节点
                accept_node_list.append(product_add_node_index)    
                product_graph.nodes[product_add_node_index]['accept']=True
            product_add_node_index=product_add_node_index+1
    # 构建乘积自动机的边
    product_state_num=len(product_graph) # get the number of nodes
    # consider all the combination of two states once, check bi-direction simultaneously
    # which means ignore self loop
    for i in range(0,product_state_num-1):
        for j in range(i,product_state_num):
            if (product_graph.nodes[j]['ts_name'] in trans_graph[product_graph.nodes[i]['ts_name']])\
                    and (product_graph.nodes[j]['buchi_name'] in buchi_graph[product_graph.nodes[i]['buchi_name']]):
                # 获取i到j边上的AP表达式
                buchi_label=buchi_graph[product_graph.nodes[i]['buchi_name']]\
                        [product_graph.nodes[j]['buchi_name']]['label']
                #  current TS节点的AP list集合
                ts_node_label=trans_graph.node[product_graph.nodes[i]['ts_name']]['label']
                if buchi_label_test(buchi_label,ts_node_label)==1:  #如果返回1，则表明转移条件成立
                    product_graph.add_edge(i,j,weight=trans_graph[product_graph.nodes[i]['ts_name']]\
                                           [product_graph.nodes[j]['ts_name']]['weight'],\
                                           label=buchi_label)
                    # modify parent node list
                    product_graph.nodes[j]['parent'].append(i)
#                print("buchi label: "+buchi_label)
#                print(ts_node_label)
#                print(buchi_label_test(buchi_label,ts_node_label))
#                print(" ")
#                time.sleep(8)
            if(j!=i):   # self loop only be checked once
                if (product_graph.nodes[i]['ts_name'] in trans_graph[product_graph.nodes[j]['ts_name']])\
                        and (product_graph.nodes[i]['buchi_name'] in buchi_graph[product_graph.nodes[j]['buchi_name']]):
                    # 边上的AP表达式
                    buchi_label=buchi_graph[product_graph.nodes[j]['buchi_name']]\
                            [product_graph.nodes[i]['buchi_name']]['label']
                    # current TS节点的AP list集合
                    ts_node_label=trans_graph.node[product_graph.nodes[j]['ts_name']]['label']
                    if buchi_label_test(buchi_label,ts_node_label)==1:  #如果返回1，则表明转移条件成立
                        product_graph.add_edge(j,i,weight=trans_graph[product_graph.nodes[j]['ts_name']]\
                                               [product_graph.nodes[i]['ts_name']]['weight'],\
                                               label=buchi_label) 
                        product_graph.nodes[i]['parent'].append(j)
#                    print("buchi label: "+buchi_label)
#                    print(ts_node_label)
#                    print(buchi_label_test(buchi_label,ts_node_label))
#                    print(" ")
#                    time.sleep(8)
    return product_graph,init_node_list,accept_node_list
                    




def product_transition(trans_graph_list):
    """
    input: clasc_trans_graph list
    output: one product transition graph
    """
    product_trans_graph=nx.DiGraph()    
    ## construct product transiton state
    robot_num=len(trans_graph_list)
    # created nodes in every cycle
    pts_nodes_list=[]
    for i in range(0,robot_num):
        pts_nodes_list.append([])
    i=0
    while i!=robot_num:
        if i==0:
            for single_ts_node in list(trans_graph_list[i].nodes):
                # elements in pts_nodes_list[i] is aslo list
                pts_nodes_list[i].append([single_ts_node])
        else:
            for pre_product_node in pts_nodes_list[i-1]:
                for single_ts_node in list(trans_graph_list[i].nodes):
                    add_node=[]
                    add_node.append(single_ts_node)
                    pts_nodes_list[i].append(pre_product_node+add_node)
        i+=1
    # pts_node_list[robot_num-1]: each element is list type
    for pts_node in pts_nodes_list[robot_num-1]:
        label_list=[]
        for j in range(0,robot_num):
            label_list+=trans_graph_list[j].nodes[pts_node[j]]['label']
        product_trans_graph.add_node(str(pts_node),name=str(pts_node),\
                                     label=label_list,ts_list=pts_node)
    
    ## construct product transition edge
    node_num=len(product_trans_graph)
    for k in range(0,node_num):
        for m in range(k,node_num):
            if pts_trans_check(pts_nodes_list[robot_num-1][k],\
                        pts_nodes_list[robot_num-1][m],trans_graph_list)==1:
                trans_cost=pts_trans_cost(pts_nodes_list[robot_num-1][k],\
                        pts_nodes_list[robot_num-1][m],trans_graph_list)
                product_trans_graph.add_edge(str(pts_nodes_list[robot_num-1][k]),\
                        str(pts_nodes_list[robot_num-1][m]),weight=trans_cost)
            if k!=m:
                if pts_trans_check(pts_nodes_list[robot_num-1][m],\
                        pts_nodes_list[robot_num-1][k],trans_graph_list)==1:
                    trans_cost=pts_trans_cost(pts_nodes_list[robot_num-1][m],\
                        pts_nodes_list[robot_num-1][k],trans_graph_list)
                    product_trans_graph.add_edge(str(pts_nodes_list[robot_num-1][m]),\
                        str(pts_nodes_list[robot_num-1][k]),weight=trans_cost)
    return product_trans_graph
    
    
    

    
    
    
    
    
    
    
    
    
    
    


