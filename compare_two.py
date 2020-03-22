import os
import json
import time
from func_set.trans_sys import compute_trans_graph
from func_set.gltl2ba import ltl_formula_to_ba
from func_set.sampling_func import sampling_ltl_planning
from func_set.classical_func import product_automaton, product_transition, \
    classical_ltl_planning, get_robot_path
from func_set.show_graph import nx_to_graphviz_tree, nx_to_graphviz_trans
from func_set.show_graph import nx_to_graphviz_trans, nx_to_graphviz_product


if __name__ == '__main__':

    with open('task_config.txt', 'r') as f:
        config = json.loads(f.read())

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

    # classical planning start:
    clasc_time_start = time.time()

    clasc_trans_graph_list = []
    for robot_config_file in config['robots_config_file']:
        clasc_trans_graph_list.append(compute_trans_graph(robot_config_file))
    trans_graph = product_transition(clasc_trans_graph_list)

    # 构建乘积自动机并返回三种类型节点集合
    [product_graph, product_init_states, product_accept_states] =\
        product_automaton(trans_graph, buchi_graph)

    [clasc_optimal_path, clasc_optimal_path_cost] = classical_ltl_planning(
        robots_init_pos, is_surveillance, product_init_states, product_graph, product_accept_states)

    robot_path = get_robot_path(
        clasc_optimal_path, clasc_optimal_path_cost, robot_number, trans_graph, product_graph)

    # classical planning end
    clasc_time_end = time.time()

    print(
        f'Classical planning computing time: {clasc_time_end-clasc_time_start} seconds.')
    for i, single_robot_path in enumerate(robot_path):
        print(f'Robot{i}: {single_robot_path}')
    print(f'best path weight: {clasc_optimal_path_cost["whole_path"]}')
    print(f'pre weight: {clasc_optimal_path_cost["pre_path"]}')
    print(f'suf weight: {clasc_optimal_path_cost["suf_path"]}')

    # trans_dot_graph = nx_to_graphviz_trans(trans_graph_list[0])
    # trans_dot_graph = nx_to_graphviz_trans(trans_graph)
    # product_dot_graph = nx_to_graphviz_product(product_graph)
    # trans_dot_graph.show('clasc_trans_graph')
    # buchi_dot_graph.show('clasc_buchi_graph')
    # product_dot_graph.show('clasc_product_graph')

    # sampling planning start
    samp_time_start = time.time()

    samp_trans_graph_list = []
    for robot_config_file in config['robots_config_file']:
        samp_trans_graph_list.append(compute_trans_graph(robot_config_file))

    itera_pre_num = config['itera_pre_num']
    itera_suf_num = config['itera_suf_num']

    [samp_optimal_path, samp_optimal_path_cost] = sampling_ltl_planning(robots_init_pos, samp_trans_graph_list,
                                                                        buchi_graph, buchi_init_states,
                                                                        is_surveillance,
                                                                        itera_pre_num, itera_suf_num)
    # record path for every robot
    robot_path = [[] for i in range(robot_number)]
    pre_robot_path = list(zip(*samp_optimal_path[0]))
    suf_robot_path = list(zip(*samp_optimal_path[1]))
    robot_path = list(zip(pre_robot_path, suf_robot_path))

    # sampling planning end
    samp_time_end = time.time()

    print(
        f'Sampling planning computing time: {samp_time_end-samp_time_start} seconds.')

    for i, path in enumerate(robot_path):
        print(f'Robot{i}: {path}')
    print(f'best path weight: {sum(samp_optimal_path_cost)}')
    print(f'pre weight: {samp_optimal_path_cost[0]}')
    print(f'suf weight: {samp_optimal_path_cost[1]}')

    # trans_dot_graph1 = nx_to_graphviz_trans(trans_graph_list[0])
    # trans_dot_graph1.show('samp_trans_graph1')
    # trans_dot_graph2 = nx_to_graphviz_trans(trans_graph_list[1])
    # trans_dot_graph2.show('samp_trans_graph2')
    # buchi_dot_graph.show('samp_buchi_graph')
    # search_dot_pre_tree=nx_to_graphviz_tree(pre_search_tree)
    # search_dot_pre_tree.show('samp_search_tree')
