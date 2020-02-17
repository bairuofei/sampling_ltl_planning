# -*- coding: utf-8 -*-
import os
import networkx as nx
from gltl2ba import ltl_formula_to_ba
from construct_pba import product_automaton
from construct_pba import product_transition
# from construct_pba import buchi_label_test
from show_graph import nx_to_graphviz_trans
from show_graph import nx_to_graphviz_product
import trans_sys

trans_graph_list=[]
trans_graph_list.append(trans_sys.samp_trans_graph1())
trans_graph_list.append(trans_sys.samp_trans_graph2())
trans_graph=product_transition(trans_graph_list)

trans_dot_graph1=nx_to_graphviz_trans(trans_sys.samp_trans_graph1())
trans_dot_graph1.show('trans_graph1')
trans_dot_graph2=nx_to_graphviz_trans(trans_sys.samp_trans_graph2())
trans_dot_graph2.show('trans_graph2')

trans_dot_graph=nx_to_graphviz_trans(trans_graph)
trans_dot_graph.show('trans_graph')
