# -*- coding: utf-8 -*-
import os
import json
import time
import logging
import networkx as nx
from func_set.trans_sys import compute_trans_graph
from func_set.gltl2ba import ltl_formula_to_ba
from func_set.classical_func import product_automaton, product_transition, \
    classical_ltl_planning, get_robot_path
from func_set.show_graph import nx_to_graphviz_trans, nx_to_graphviz_product


if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename="classical_planning.log",
                        filemode="w",
                        format=LOG_FORMAT,
                        datefmt=DATE_FORMAT,
                        level=logging.DEBUG)
    logging.info("    ")

    with open('task_config.txt', 'r') as f:
        config = json.loads(f.read())
    clasc_start_time = time.time()

    # path weight
    path_weight = config['path_weight']

    # Transition system
    trans_graph_list = []
    for robot_config_file in config['robots_config_file']:
        trans_graph_list.append(compute_trans_graph(robot_config_file))
    print("start read transition system:")
    trans_graph = product_transition(trans_graph_list)
    print(f"product ts size: {len(trans_graph)}")
    logging.info(f"product ts size: {len(trans_graph)}")

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
    print("start converting buchi automaton:")
    [buchi_graph, buchi_init_states, buchi_accept_states,
        buchi_dot_graph] = ltl_formula_to_ba(task, LTL_FILE_POS)
    print(f'buchi graph size: {len(buchi_graph)}')
    logging.info(f'buchi graph size: {len(buchi_graph)}')

    # 构建乘积自动机并返回三种类型节点集合
    print("start construct product automaton:")
    [product_graph, product_init_states, product_accept_states] =\
        product_automaton(trans_graph, buchi_graph)
    print(f'product automaton size: {len(product_graph)}')
    logging.info(f'product automaton size: {len(product_graph)}')

    [best_path, best_path_length] = classical_ltl_planning(robots_init_pos,
                                                           is_surveillance,
                                                           product_init_states,
                                                           product_graph,
                                                           product_accept_states,
                                                           path_weight)

    robot_path = get_robot_path(
        best_path, best_path_length, robot_number, trans_graph, product_graph)

    clasc_end_time = time.time()

    print(f'computation time: {clasc_end_time-clasc_start_time} seconds.')
    logging.info(
        f'computation time: {clasc_end_time-clasc_start_time} seconds.')

    for i, single_robot_path in enumerate(robot_path):
        print(f'Robot{i}: {single_robot_path[0]} + {single_robot_path[1]}')
        logging.info(f'Robot{i}: {single_robot_path}')
    print(f'best path weight: {best_path_length["whole_path"]}')
    print(f'pre weight: {best_path_length["pre_path"]}')
    print(f'suf weight: {best_path_length["suf_path"]}')
    logging.info(f'best path weight: {best_path_length["whole_path"]}')
    logging.info(f'pre weight: {best_path_length["pre_path"]}')
    logging.info(f'suf weight: {best_path_length["suf_path"]}')

    # trans_dot_graph = nx_to_graphviz_trans(trans_graph_list[0])
    # trans_dot_graph = nx_to_graphviz_trans(trans_graph)
    # product_dot_graph = nx_to_graphviz_product(product_graph)
    # trans_dot_graph.show('clasc_trans_graph')
    # buchi_dot_graph.show('clasc_buchi_graph')
    # product_dot_graph.show('clasc_product_graph')
