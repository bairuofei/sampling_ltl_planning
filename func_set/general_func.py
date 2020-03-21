# -*- coding: utf-8 -*-
import re

def buchi_label_test(buchi_label,ts_node_label):
    """检查状态转移是否满足buchi自动机转移条件,返回1 通过；返回0 不通过
       输入：buchi自动机边转移表达式；迁移系统节点AP list
       输出：该迁移关系是否满足
    """
    buchi_label_test=0          # 检查是否满足边转移条件
    if buchi_label=='(1)':  # 如果是1，则直接满足
        buchi_label_test=1
        return buchi_label_test
    # 这一句最开始放错了位置： label_piece_test=1
    buchi_label_split=buchi_label.split(' || ')    
    for label_piece in buchi_label_split: # 每一个与表达式
        label_piece_test=1
        pat_singleAP = re.compile(r'(?<=\().*(?=\))') #去掉括号
        pat_str_exclu=pat_singleAP.search(label_piece)
        label_piece_split=pat_str_exclu.group().split(' && ')
        for state_ap in label_piece_split:
            if state_ap[0]!='!':  # 则状态label中必须有
                if state_ap not in ts_node_label:
                    label_piece_test=0
                    break
            else:                 # 对应！pi 项
                state_ap_inverse=state_ap[1:]  # 去掉！符号
                if state_ap_inverse in ts_node_label:
                    label_piece_test=0
                    break            
        if label_piece_test==1:   # 说明label_piece对当前状态下的所有命题没有违反的情况出现
            buchi_label_test=1    # 满足转移条件
            break; 
    return buchi_label_test

def pts_trans_check(pts_now,pts_new,trans_graph):
    """
    input: two list
    output: if pass, return 1
            else return 0
    """
    for i in range(0,len(pts_now)):
        if pts_new[i] in trans_graph[i].nodes[pts_now[i]]['children']:
            continue
        else:
            return 0
    return 1
    
    
def pts_trans_cost(pts_now,pts_new,trans_graph):
    """
    input: two list, include robot state
    return cost
    """
    cost=0
#    print(pts_now)
#    print(pts_new)
    
    for i in range(0,len(pts_now)):
        cost+=trans_graph[i][pts_now[i]][pts_new[i]]['weight']
    return cost

def product_trans_check(trans_graph,buchi_graph,pre_node,suf_node):
    """
    check if there exists a transition between two product nodes
    input node type: dict, two key:'pts','buchi'
    output: exist, return 1
            not exist, return -1
    """
    # buchi transition check
    if suf_node['buchi'] in buchi_graph[pre_node['buchi']]:
        # pts transition check
        if pts_trans_check(pre_node['pts'],suf_node['pts'],trans_graph)==1:
            buchi_label=buchi_graph[pre_node['buchi']][suf_node['buchi']]['label']
            ts_node_label=[]
            for i in range(0,len(pre_node['pts'])):
                ts_node_label+=trans_graph[i].nodes[pre_node['pts'][i]]['label']
            # product transition check
            if buchi_label_test(buchi_label,ts_node_label)==1:
                return 1
    return -1