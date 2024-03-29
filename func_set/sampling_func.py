# -*- coding: utf-8 -*-
import random
import logging
import time
import logging
import networkx as nx
from func_set.general_func import buchi_label_test,\
    pts_trans_check, pts_trans_cost, product_trans_check
from func_set.show_graph import nx_to_graphviz_tree


def search_tree_init(init_pts, trans_graph, buchi_init_state):
    """
    init_pts: tpye list. eg: init_pts=['n1','n1']
    buchi_accept_state: type str. eg: buchi_accept_state='accept_all'
    """
    search_tree = nx.DiGraph()
    search_tree.add_node(0,
                         name=str(init_pts)+', '+buchi_init_state,
                         ts_name=init_pts,
                         ts_label=[],
                         buchi_name=buchi_init_state,
                         parent=-1,
                         children=[],
                         cost=0)
    for i in range(0, len(init_pts)):
        search_tree.nodes[0]['ts_label'] += trans_graph[i].nodes[init_pts[i]]['label']
    return search_tree


def sample(search_tree, trans_graph):
    """
    return list type pts_new
    """
    p_rand = random.randint(0, len(search_tree)-1)
    pts_rand = search_tree.nodes[p_rand]['ts_name']  # list
    pts_new = []
    pts_index = 0
    for pts_index, ts_node in enumerate(pts_rand):
        ts_graph = trans_graph[pts_index]
        ts_children = ts_graph.nodes[ts_node]['children']  # list
        ts_rand = random.randint(0, len(ts_children)-1)
        pts_new.append(ts_children[ts_rand])
    return pts_new


def extend(search_tree, trans_graph, buchi_graph, p_new):
    """
    trans entry, search_tree will be changed
    """
    # state in tree that can reach p_new
    pre_p_new = -1
    pre_p_new_cost = float('inf')
    for i in range(0, len(search_tree)):
        # buchi transition check
        if p_new['buchi'] in buchi_graph[search_tree.nodes[i]['buchi_name']]:
            # pts transiton check
            if pts_trans_check(search_tree.nodes[i]['ts_name'], p_new['pts'], trans_graph) == 1:
                buchi_label = buchi_graph[search_tree.nodes[i]
                                          ['buchi_name']][p_new['buchi']]['label']
                ts_node_label = search_tree.nodes[i]['ts_label']
                # product transition check
                if buchi_label_test(buchi_label, ts_node_label) == 1:
                    pts_trans_cost_value = pts_trans_cost(search_tree.nodes[i]['ts_name'],
                                                          p_new['pts'], trans_graph)
                    if pts_trans_cost_value < pre_p_new_cost:
                        pre_p_new = i
                        pre_p_new_cost = pts_trans_cost_value

    if pre_p_new == -1:  # new node can not be added into the tree
        return -1
    else:  # new node will be added into the tree
        # add the node into the tree
        tree_node_index = len(search_tree)
        parent_node_cost = search_tree.nodes[pre_p_new]['cost']
        search_tree.add_node(tree_node_index,
                             name=str(p_new['pts'])+', '+p_new['buchi'],
                             ts_name=p_new['pts'],
                             ts_label=[],
                             buchi_name=p_new['buchi'],
                             parent=pre_p_new,
                             children=[],
                             cost=parent_node_cost+pre_p_new_cost)
        for i in range(0, len(p_new['pts'])):
            search_tree.nodes[tree_node_index]['ts_label'] +=\
                trans_graph[i].nodes[p_new['pts'][i]]['label']
        # add edge into the tree
        search_tree.add_edge(pre_p_new, tree_node_index, weight=pre_p_new_cost,
                             label=buchi_graph[search_tree.nodes[pre_p_new]['buchi_name']][search_tree.nodes[tree_node_index]['buchi_name']]['label'])
        # modify parent node's children attr
        search_tree.nodes[pre_p_new]['children'].append(tree_node_index)
        return tree_node_index


def update_subtree_cost(search_tree, subtree_root, delta_cost):
    """
    after rewiring, update node cost in the subtree of rewiring node.
    delta_cost: positive. All the node cost in subtree should minus the value.
    """
    search_queue = []
    search_queue += search_tree.nodes[subtree_root]['children']
    while len(search_queue) != 0:
        pop_node = search_queue.pop(len(search_queue)-1)
        search_tree.nodes[pop_node]['cost'] -= delta_cost
        if len(search_tree.nodes[pop_node]['children']) > 0:
            search_queue += search_tree.nodes[pop_node]['children']


def rewire(search_tree, trans_graph, buchi_graph, node_tree_check_value):
    p_not_new = {'pts': search_tree.nodes[node_tree_check_value]['ts_name'],
                 'buchi': search_tree.nodes[node_tree_check_value]['buchi_name']}
    for i in range(0, len(search_tree)):
        # check if new node is ndoe i
        if i == node_tree_check_value:
            continue
        else:
            suf_node = {'pts': search_tree.nodes[i]['ts_name'],
                        'buchi': search_tree.nodes[i]['buchi_name']}
            if product_trans_check(trans_graph, buchi_graph, p_not_new, suf_node) == 1:
                pts_trans_cost_value = pts_trans_cost(p_not_new['pts'],
                                                      search_tree.nodes[i]['ts_name'], trans_graph)
                reachable_node_cost = search_tree.nodes[i]['cost']
                current_node_cost = search_tree.nodes[node_tree_check_value]['cost']
                rewire_cost = current_node_cost+pts_trans_cost_value
                if rewire_cost < reachable_node_cost:
                    # rewiring
                    reachable_node_parent = search_tree.nodes[i]['parent']
                    search_tree.remove_edge(reachable_node_parent, i)
                    search_tree.add_edge(node_tree_check_value, i, weight=rewire_cost,
                                         label=buchi_graph[search_tree.nodes[node_tree_check_value]
                                                           ['buchi_name']]
                                         [search_tree.nodes[i]['buchi_name']]['label'])
                    # parent modify
                    search_tree.nodes[i]['parent'] = node_tree_check_value
                    # cost modify
                    search_tree.nodes[i]['cost'] = rewire_cost
                    # children modify
                    search_tree.nodes[node_tree_check_value]['children'].append(
                        i)
                    search_tree.nodes[reachable_node_parent]['children'].remove(
                        i)
                    delta_cost = reachable_node_cost-rewire_cost
                    update_subtree_cost(search_tree, i, delta_cost)


def node_in_tree_check(search_tree, p_new):
    """
    input: 
        p_new: type dict. Two key:'pts',type list; 'buchi',type str        
    output: in: return index
            not in: return -1
    """
    p_new_str = str(p_new['pts'])+', '+p_new['buchi']
    for k in range(0, len(search_tree)):
        if search_tree.nodes[k]['name'] == p_new_str:
            return k
    return -1


def construct_tree_prefix(trans_graph, buchi_graph, init_pts, buchi_init_state, itera_pre_num, samp_start_time):
    search_tree = search_tree_init(init_pts, trans_graph, buchi_init_state)
    accept_tree_nodes = []
    write_log = True
    for i in range(itera_pre_num):
        len_of_accept_tree_nodes = len(accept_tree_nodes)
        if i % 10 == 0:
            print(
                f'prefix interation: {i}. Size of accept tree node: {len_of_accept_tree_nodes}')

        if write_log:
            if len_of_accept_tree_nodes >= 1:
                current_time = time.time()
                logging.info(
                    f'Time finding first prefix path: {current_time-samp_start_time} seconds.')
                write_log = False
        pts_new = sample(search_tree, trans_graph)  # list

        buchi_state_list = list(buchi_graph.nodes)
        for j in range(0, len(buchi_state_list)):
            b_new = buchi_state_list[j]
            p_new = {'pts': pts_new, 'buchi': b_new}
            # check if new node already exists
            node_tree_check_value = node_in_tree_check(search_tree, p_new)
            if node_tree_check_value == -1:
                new_node_index = extend(
                    search_tree, trans_graph, buchi_graph, p_new)
                if new_node_index != -1:
                    # logging.info(f'extend: {p_new}')
                    if p_new['buchi'].find('accept') != -1:
                        accept_tree_nodes.append(new_node_index)
            else:
                rewire(search_tree, trans_graph,
                       buchi_graph, node_tree_check_value)

    return search_tree, accept_tree_nodes


def pre_find_path(pre_accept_tree_nodes, search_tree, is_surveillance):
    """
    input: search tree, current accept state index, pre_path_cost_list
    output: prefix path, list type, whose element type is also list.
            pre_path_cost_list, store each path's cost
    """
    pre_path_list = []
    pre_path_cost_list = []
    for node_index in pre_accept_tree_nodes:
        if not is_surveillance:
            pre_path = []
            backtrack_node = search_tree.nodes[node_index]['parent']
            pre_path_cost_list.append(
                search_tree.nodes[backtrack_node]['cost'])
            while backtrack_node != -1:
                pre_path = [search_tree.nodes[backtrack_node]
                            ['ts_name']]+pre_path
                backtrack_node = search_tree.nodes[backtrack_node]['parent']

        else:
            pre_path = []
            backtrack_node = node_index
            pre_path_cost_list.append(
                search_tree.nodes[backtrack_node]['cost'])
            while backtrack_node != -1:
                pre_path = [search_tree.nodes[backtrack_node]
                            ['ts_name']]+pre_path
                backtrack_node = search_tree.nodes[backtrack_node]['parent']

        if len(pre_path) != 0:
            pre_path_list.append(pre_path)
    return pre_path_list, pre_path_cost_list


def suf_find_path(search_tree, accept_tree_node, actual_accept_node_pts):
    """
    input: search tree, 
           accept_tree_node: type int, node index
           actual_accept_node_pts: type list       
    output: suf_path: path list, whose element is also list
    """
    suf_path = []
    suf_path.append(search_tree.nodes[accept_tree_node]['ts_name'])
    backtrack_node = search_tree.nodes[accept_tree_node]['parent']
    while backtrack_node != -1:
        suf_path = [search_tree.nodes[backtrack_node]['ts_name']]+suf_path
        backtrack_node = search_tree.nodes[backtrack_node]['parent']
    # suf_path.append(actual_accept_node_pts)
    return suf_path


def construct_tree_suffix(trans_graph, buchi_graph, init_pts, buchi_init_state,
                          actual_accept_node, itera_suf_num, first_suffix_start_time, index):
    search_tree = search_tree_init(init_pts, trans_graph, buchi_init_state)
    accept_tree_nodes = []
    accept_tree_nodes_costs = []
    root_node = {'pts': search_tree.nodes[0]['ts_name'],
                 'buchi': search_tree.nodes[0]['buchi_name']}
    # check if it is the accept state
    if (product_trans_check(trans_graph, buchi_graph, root_node, root_node) == 1):
        accept_tree_nodes.append(0)
        accept_tree_nodes_costs.append(pts_trans_cost(root_node['pts'],
                                                      root_node['pts'], trans_graph))
        return search_tree, accept_tree_nodes, accept_tree_nodes_costs

    log_flag = True

    for i in range(itera_suf_num):
        if i % 10 == 0:
            print(f'suffix tree iteration: {i}')
        pts_new = sample(search_tree, trans_graph)  # list
        buchi_state_list = list(buchi_graph.nodes)
        for j in range(0, len(buchi_state_list)):
            b_new = buchi_state_list[j]
            p_new = {'pts': pts_new, 'buchi': b_new}
            # check if new node already exists
            node_tree_check_value = node_in_tree_check(search_tree, p_new)
            if node_tree_check_value == -1:
                new_node_index = extend(
                    search_tree, trans_graph, buchi_graph, p_new)
                if new_node_index != -1:  # new node is added into the tree successfully
                    pre_node = {'pts': search_tree.nodes[new_node_index]['ts_name'],
                                'buchi': search_tree.nodes[new_node_index]['buchi_name']}
                    # check if it is the accept state
                    if (product_trans_check(trans_graph, buchi_graph, pre_node, root_node) == 1):
                        accept_tree_nodes.append(new_node_index)
                        accept_tree_nodes_costs.append(pts_trans_cost(pre_node['pts'],
                                                                      root_node['pts'], trans_graph))
            else:
                rewire(search_tree, trans_graph,
                       buchi_graph, node_tree_check_value)
            if log_flag and index == 0 and len(accept_tree_nodes) != 0:
                logging.info(
                    f'Time finding first suffix path: {time.time()-first_suffix_start_time} seconds.')
                log_flag = False
    return search_tree, accept_tree_nodes, accept_tree_nodes_costs


def sample_suffix_path(trans_graph_list,
                       buchi_graph,
                       pre_search_tree, pre_accept_tree_nodes,
                       itera_suf_num):
    suf_path_list = []
    suf_path_cost_list = []
    for i, node_index in enumerate(pre_accept_tree_nodes):
        first_suffix_start_time = time.time()
        print(
            f'For accept tree node: {node_index} construct suffix tree. Size:{i+1,len(pre_accept_tree_nodes)}')
        actual_accept_node_index = pre_search_tree.nodes[node_index]['parent']
        actual_accept_node = {'pts': pre_search_tree.nodes[actual_accept_node_index]['ts_name'],
                              'buchi': pre_search_tree.nodes[actual_accept_node_index]['buchi_name']}
        suf_init_pts = pre_search_tree.nodes[node_index]['ts_name']
        suf_init_buchi = pre_search_tree.nodes[node_index]['buchi_name']

        [suf_search_tree, suf_accept_tree_nodes, suf_accept_tree_nodes_costs] = \
            construct_tree_suffix(trans_graph_list, buchi_graph, suf_init_pts,
                                  suf_init_buchi, actual_accept_node, itera_suf_num, first_suffix_start_time, i)
        # find minimum loop cost
        suf_path = []
        suf_path_cost = float('inf')
        for j in range(0, len(suf_accept_tree_nodes)):
            suf_accept_tree_node = suf_accept_tree_nodes[j]
            suf_one_path_cost = suf_search_tree.nodes[suf_accept_tree_node]['cost']\
                + suf_accept_tree_nodes_costs[j]
            if suf_one_path_cost < suf_path_cost:
                suf_path_cost = suf_one_path_cost
                suf_path = suf_find_path(suf_search_tree, suf_accept_tree_node,
                                         actual_accept_node['pts'])
        suf_path_list.append(suf_path)
        suf_path_cost_list.append(suf_path_cost)

    return suf_path_list, suf_path_cost_list


def sampling_ltl_planning(robots_init_pos, trans_graph_list,
                          buchi_graph, buchi_init_states,
                          is_surveillance,
                          itera_pre_num, itera_suf_num,
                          path_weight, samp_start_time):
    optimal_path = [[], []]
    optimal_path_cost = [float('inf'), float('inf')]
    # for every buchi init state, which means possible tree root
    for buchi_init_state in buchi_init_states:
        # prefix path
        print(
            f'For buchi init state {buchi_init_state} construct PREFIX tree.')
        [pre_search_tree, pre_accept_tree_nodes] = construct_tree_prefix(trans_graph_list, buchi_graph,
                                                                         robots_init_pos, buchi_init_state,
                                                                         itera_pre_num, samp_start_time)
        # search_dot_pre_tree = nx_to_graphviz_tree(pre_search_tree)
        # search_dot_pre_tree.show('samp_search_tree')
        # for every accept product state in current tree
        [pre_path_list, pre_path_cost_list] = pre_find_path(pre_accept_tree_nodes,
                                                            pre_search_tree, is_surveillance)

        print(
            f'For buchi init state {buchi_init_state} construct SUFFIX tree.')
        # suffix path
        if is_surveillance:   # if has surveillance_task
            [suf_path_list, suf_path_cost_list] = sample_suffix_path(trans_graph_list,
                                                                     buchi_graph,
                                                                     pre_search_tree, pre_accept_tree_nodes,
                                                                     itera_suf_num)
        else:  # if not have surveillance_task
            suf_path_list = [[] for i in range(len(pre_accept_tree_nodes))]
            suf_path_cost_list = [0 for i in range(len(pre_accept_tree_nodes))]

        # find shortest path for a single buchi init state
        single_init_path = [[], []]
        single_init_path_cost = [float('inf'), float('inf')]
        for i in range(len(pre_accept_tree_nodes)):
            one_init_pre_path_cost = pre_path_cost_list[i]*path_weight[0]
            one_init_suf_path_cost = suf_path_cost_list[i]*path_weight[1]
            one_init_path_cost = one_init_pre_path_cost+one_init_suf_path_cost
            if one_init_path_cost < single_init_path_cost[0]+single_init_path_cost[1]:
                single_init_path_cost[0] = one_init_pre_path_cost
                single_init_path_cost[1] = one_init_suf_path_cost
                single_init_path[0] = pre_path_list[i]
                single_init_path[1] = suf_path_list[i]

        # now we have best path for one specific init state
        if single_init_path_cost[0]+single_init_path_cost[1] < optimal_path_cost[0]+optimal_path_cost[1]:
            optimal_path_cost[0] = single_init_path_cost[0]
            optimal_path_cost[1] = single_init_path_cost[1]
            optimal_path[0] = single_init_path[0]
            if is_surveillance:
                optimal_path[1] = single_init_path[1][1:]
                optimal_path[1].append(single_init_path[1][0])
            else:
                optimal_path[1] = single_init_path[1]

    for i, path_cost in enumerate(optimal_path_cost):
        optimal_path_cost[i] = round(path_cost, 2)

    return optimal_path, optimal_path_cost


def samp_get_robot_path(optimal_path, robot_number):
    robot_path = [[[], []] for i in range(robot_number)]
    # 前缀路径
    for i in range(robot_number):
        for pts in optimal_path[0]:
            robot_path[i][0].append(pts[i])
    if len(optimal_path[1]) != 0:
        for i in range(robot_number):
            for pts in optimal_path[1]:
                robot_path[i][1].append(pts[i])
    return robot_path
