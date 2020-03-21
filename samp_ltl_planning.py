# -*- coding: utf-8 -*-
import os
import json
from func_set.trans_sys import compute_trans_graph
from func_set.gltl2ba import ltl_formula_to_ba
from func_set.sampling_func import sampling_ltl_planning
from func_set.show_graph import nx_to_graphviz_tree, nx_to_graphviz_trans


if __name__ == '__main__':
    itera_pre_num = 500
    itera_suf_num = 500

    with open('task_config.txt', 'r') as f:
        config = json.loads(f.read())

    # Transition system
    trans_graph_list = []
    for robot_config_file in config['robots_config_file']:
        trans_graph_list.append(compute_trans_graph(robot_config_file))

    # Init position
    robots_init_pos = config['robots_init_pos']
    robot_number = len(robots_init_pos)

    # LTL task formula
    if config['is_task_surveillance'] == 'False':
        is_surveillance = False
    else:
        is_surveillance = True
    task = config['ltl_task']

    # os.getcwd get current work directory
    LTL_FILE_POS = os.getcwd()+'/clasc_ltlFile.txt'

    # convert ltl to buchi automaton
    [buchi_graph, buchi_init_states, buchi_accept_states,
        buchi_dot_graph] = ltl_formula_to_ba(task, LTL_FILE_POS)

    [optimal_path, optimal_path_cost] = sampling_ltl_planning(robots_init_pos, trans_graph_list,
                                                              buchi_graph, buchi_init_states,
                                                              is_surveillance,
                                                              itera_pre_num, itera_suf_num)

    # record path for every robot
    robot_path = [[] for i in range(robot_number)]
    pre_robot_path = list(zip(*optimal_path[0]))
    suf_robot_path = list(zip(*optimal_path[1]))
    robot_path = list(zip(pre_robot_path, suf_robot_path))

    for i, path in enumerate(robot_path):
        print(f'Robot{i}: {path}')
    print(f'best path weight: {sum(optimal_path_cost)}')
    print(f'pre weight: {optimal_path_cost[0]}')
    print(f'suf weight: {optimal_path_cost[1]}')

    # trans_dot_graph1 = nx_to_graphviz_trans(trans_graph_list[0])
    # trans_dot_graph1.show('samp_trans_graph1')
    # trans_dot_graph2 = nx_to_graphviz_trans(trans_graph_list[1])
    # trans_dot_graph2.show('samp_trans_graph2')
    # buchi_dot_graph.show('samp_buchi_graph')
    # search_dot_pre_tree=nx_to_graphviz_tree(pre_search_tree)
    # search_dot_pre_tree.show('samp_search_tree')
