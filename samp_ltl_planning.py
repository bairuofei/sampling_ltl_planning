# -*- coding: utf-8 -*-
import os
import json
import time
import logging
from func_set.trans_sys import compute_trans_graph
from func_set.gltl2ba import ltl_formula_to_ba
from func_set.sampling_func import sampling_ltl_planning, samp_get_robot_path
from func_set.show_graph import nx_to_graphviz_tree, nx_to_graphviz_trans


if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename="samp_planning.log",
                        filemode="a",
                        format=LOG_FORMAT,
                        datefmt=DATE_FORMAT,
                        level=logging.DEBUG)
    logging.info("   ")

    with open('task_config.txt', 'r') as f:
        config = json.loads(f.read())

    samp_start_time = time.time()

    itera_pre_num = config['itera_pre_num']
    itera_suf_num = config['itera_suf_num']

    # path weight
    path_weight = config['path_weight']

    # Transition system
    trans_graph_list = []
    for robot_config_file in config['robots_config_file']:
        trans_graph_list.append(compute_trans_graph(robot_config_file))
    pts_state_num = 1
    for trans_graph in trans_graph_list:
        pts_state_num *= len(trans_graph)
    print(f'pts state number: {pts_state_num}')
    logging.info(f'pts state number: {pts_state_num}')

    # Init position
    robots_init_pos = config['robots_init_pos']
    robot_number = len(robots_init_pos)
    print(f'robot number: {robot_number}')
    logging.info(f'robot number: {robot_number}')

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
    print(f'product automaton size: {len(buchi_graph)*pts_state_num}')
    logging.info(f'product automaton size: {len(buchi_graph)*pts_state_num}')

    print("start sampling planning:")
    [optimal_path, optimal_path_cost] = sampling_ltl_planning(robots_init_pos, trans_graph_list,
                                                              buchi_graph, buchi_init_states,
                                                              is_surveillance,
                                                              itera_pre_num, itera_suf_num,
                                                              path_weight)

    # record path for every robot
    robot_path = samp_get_robot_path(optimal_path, robot_number)

    samp_end_time = time.time()
    print(f'computation time: {samp_end_time-samp_start_time} seconds.')
    logging.info(f'computation time: {samp_end_time-samp_start_time} seconds.')

    for i, path in enumerate(robot_path):
        print(f'Robot{i}: {path[0]} + {path[1]}')
        logging.info(f'Robot{i}: {path[0]} + {path[1]}')
    print(f'best path weight: {sum(optimal_path_cost)}')
    print(f'pre weight: {optimal_path_cost[0]}')
    print(f'suf weight: {optimal_path_cost[1]}')
    logging.info(f'best path weight: {sum(optimal_path_cost)}')
    logging.info(f'pre weight: {optimal_path_cost[0]}')
    logging.info(f'suf weight: {optimal_path_cost[1]}')

    # trans_dot_graph1 = nx_to_graphviz_trans(trans_graph_list[0])
    # trans_dot_graph1.show('samp_trans_graph1')
    # trans_dot_graph2 = nx_to_graphviz_trans(trans_graph_list[1])
    # trans_dot_graph2.show('samp_trans_graph2')
    # buchi_dot_graph.show('samp_buchi_graph')
    # search_dot_pre_tree=nx_to_graphviz_tree(pre_search_tree)
    # search_dot_pre_tree.show('samp_search_tree')
