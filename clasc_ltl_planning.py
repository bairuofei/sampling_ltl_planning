# -*- coding: utf-8 -*-
import os
import json
import networkx as nx
from trans_sys import compute_trans_graph
from gltl2ba import ltl_formula_to_ba
from classical_func import product_automaton, product_transition, \
    classical_ltl_planning, get_robot_path
from show_graph import nx_to_graphviz_trans, nx_to_graphviz_product


if __name__ == '__main__':
    with open('task_config.txt', 'r') as f:
        config = json.loads(f.read())

    # Transition system
    trans_graph_list = []
    for robot_config_file in config['robots_config_file']:
        trans_graph_list.append(compute_trans_graph(robot_config_file))
    trans_graph = product_transition(trans_graph_list)

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

    # 构建乘积自动机并返回三种类型节点集合
    [product_graph, product_init_states, product_accept_states] =\
        product_automaton(trans_graph, buchi_graph)

    [best_path, best_path_length] = classical_ltl_planning(
        robots_init_pos, is_surveillance, product_init_states, product_graph, product_accept_states)

    robot_path = get_robot_path(
        best_path, best_path_length, robot_number, trans_graph, product_graph)

    for i, single_robot_path in enumerate(robot_path):
        print(f'Robot{i}: {single_robot_path}')
    print(f'best path weight: {best_path_length["whole_path"]}')
    print(f'pre weight: {best_path_length["pre_path"]}')
    print(f'suf weight: {best_path_length["suf_path"]}')

    # trans_dot_graph = nx_to_graphviz_trans(trans_graph_list[0])
    # trans_dot_graph = nx_to_graphviz_trans(trans_graph)
    # product_dot_graph = nx_to_graphviz_product(product_graph)
    # trans_dot_graph.show('clasc_trans_graph')
    # buchi_dot_graph.show('clasc_buchi_graph')
    # product_dot_graph.show('clasc_product_graph')
