from func_set.trans_sys import compute_trans_graph
from func_set.show_graph import nx_to_graphviz_trans

trans_graph = compute_trans_graph('robot1.txt')
trans_dot_graph = nx_to_graphviz_trans(trans_graph)
trans_dot_graph.show('view transgraph')
