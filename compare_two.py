import os
import json
import time
import logging
from func_set.trans_sys import compute_trans_graph
from func_set.gltl2ba import ltl_formula_to_ba
from func_set.sampling_func import sampling_ltl_planning, samp_get_robot_path
from func_set.classical_func import product_automaton, product_transition, \
    classical_ltl_planning, get_robot_path
from func_set.show_graph import nx_to_graphviz_tree, nx_to_graphviz_trans, nx_to_graphviz_product


if __name__ == '__main__':

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    # filemode="a" / "w"
    logging.basicConfig(filename="compare.log",
                        filemode="w",
                        format=LOG_FORMAT,
                        datefmt=DATE_FORMAT,
                        level=logging.DEBUG)

    #'./robot_ts/c1p1.txt', './robot_ts/c1p2.txt', './robot_ts/c1p3.txt','./robot_ts/c2p1.txt',

    # './robot_ts/c2p2r2.txt', './robot_ts/c2p2r3.txt',
    #                  './robot_ts/c2p2r4.txt', './robot_ts/c2p2r5.txt', './robot_ts/c2p2r6.txt',
    #                  './robot_ts/c2p2r7.txt'

    for txt_name in ['./robot_ts/caseA.txt']:
        logging.info('-------------------------------------------------')
        with open(txt_name, 'r') as f:
            config = json.loads(f.read())

        # path weight
        path_weight = config['path_weight']

        # Init position
        robots_init_pos = config['robots_init_pos']
        robot_number = len(robots_init_pos)

        # LTL task formula
        # if config['is_task_surveillance'] == 'False':
        #     is_surveillance = False
        # else:
        #     is_surveillance = True
        task = config['ltl_task']
        logging.info(f'ltl task: {task}')
        if "[]<>" in task or "[] <>" in task:
            is_surveillance = True
        else:
            is_surveillance = False

        # os.getcwd get current work directory
        LTL_FILE_POS = os.getcwd()+'/clasc_ltlFile.txt'

        # convert ltl to buchi automaton
        print("start converting buchi automaton:")
        [buchi_graph, buchi_init_states, buchi_accept_states,
            buchi_dot_graph] = ltl_formula_to_ba(task, LTL_FILE_POS)
        print(f'buchi graph size: {len(buchi_graph)}')
        logging.info(f'buchi graph size: {len(buchi_graph)}')

        ##################################################
        # classical planning start:
        print("CLASSICAL PLANNING START:")
        logging.info("CLASSICAL PLANNING START:")
        clasc_start_time = time.time()

        print("start read transition system:")
        clasc_trans_graph_list = []
        for robot_config_file in config['robots_config_file']:
            clasc_trans_graph_list.append(
                compute_trans_graph(robot_config_file))
        trans_graph = product_transition(clasc_trans_graph_list)
        print(f"product transition system size: {len(trans_graph)}")
        logging.info(f"product ts size: {len(trans_graph)}")

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

        # classical planning end
        clasc_end_time = time.time()

        print(f'computation time: {clasc_end_time-clasc_start_time} seconds.')
        logging.info(
            f'computation time: {clasc_end_time-clasc_start_time} seconds.')

        for i, single_robot_path in enumerate(robot_path):
            print(f'Robot{i}: {single_robot_path[0]} + {single_robot_path[1]}')
            logging.info(
                f'Robot{i}: {single_robot_path[0]} + {single_robot_path[1]}')
        print(f'best path weight: {best_path_length["whole_path"]}')
        print(f'pre weight: {best_path_length["pre_path"]}')
        print(f'suf weight: {best_path_length["suf_path"]}')
        logging.info(f'best path weight: {best_path_length["whole_path"]}')
        logging.info(f'pre weight: {best_path_length["pre_path"]}')
        logging.info(f'suf weight: {best_path_length["suf_path"]}')

        print("CLASSICAL PLANNING END")
        logging.info("CLASSICAL PLANNING END")

        # trans_dot_graph = nx_to_graphviz_trans(trans_graph_list[0])
        # trans_dot_graph = nx_to_graphviz_trans(trans_graph)
        # product_dot_graph = nx_to_graphviz_product(product_graph)
        # trans_dot_graph.show('clasc_trans_graph')
        # buchi_dot_graph.show('clasc_buchi_graph')
        # product_dot_graph.show('clasc_product_graph')

        ##################################################
        # sampling planning start
        print("SAMPLE PLANNING START:")
        logging.info("SAMPLE PLANNING START:")
        samp_start_time = time.time()

        samp_trans_graph_list = []
        for robot_config_file in config['robots_config_file']:
            samp_trans_graph_list.append(
                compute_trans_graph(robot_config_file))

        itera_pre_num = config['itera_pre_num']
        itera_suf_num = config['itera_suf_num']
        logging.info(f'iteration number: {itera_pre_num,itera_suf_num}')

        print("start sampling planning:")
        [optimal_path, optimal_path_cost] = sampling_ltl_planning(robots_init_pos, samp_trans_graph_list,
                                                                  buchi_graph, buchi_init_states,
                                                                  is_surveillance,
                                                                  itera_pre_num, itera_suf_num,
                                                                  path_weight, samp_start_time)
        # record path for every robot
        robot_path = samp_get_robot_path(optimal_path, robot_number)

        samp_end_time = time.time()
        print(f'computation time: {samp_end_time-samp_start_time} seconds.')
        logging.info(
            f'computation time: {samp_end_time-samp_start_time} seconds.')

        for i, path in enumerate(robot_path):
            print(f'Robot{i}: {path[0]} + {path[1]}')
            logging.info(f'Robot{i}: {path[0]} + {path[1]}')
        print(f'best path weight: {sum(optimal_path_cost)}')
        print(f'pre weight: {optimal_path_cost[0]}')
        print(f'suf weight: {optimal_path_cost[1]}')
        logging.info(f'best path weight: {sum(optimal_path_cost)}')
        logging.info(f'pre weight: {optimal_path_cost[0]}')
        logging.info(f'suf weight: {optimal_path_cost[1]}')

        print("SAMPLE PLANNING END")
        logging.info("SAMPLE PLANNING END")
        # trans_dot_graph1 = nx_to_graphviz_trans(trans_graph_list[0])
        # trans_dot_graph1.show('samp_trans_graph1')
        # trans_dot_graph2 = nx_to_graphviz_trans(trans_graph_list[1])
        # trans_dot_graph2.show('samp_trans_graph2')
        # buchi_dot_graph.show('samp_buchi_graph')
        # search_dot_pre_tree=nx_to_graphviz_tree(pre_search_tree)
        # search_dot_pre_tree.show('samp_search_tree')
