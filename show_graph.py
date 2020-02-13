# -*- coding: utf-8 -*-

from gltl2ba import Graph

def nx_to_graphviz_product(product_graph):
    """
    convert networkx product graph to a dot graph
    """
    product_dot_graph=Graph()
    product_dot_graph.title("product automaton")
    for node in list(product_graph.nodes):
        if product_graph.nodes[node]['accept']:
            product_dot_graph.node(str(node),product_graph.nodes[node]['name'],True)
        else:
            product_dot_graph.node(str(node),product_graph.nodes[node]['name'],False)
        for reachable_node in product_graph[node]:
            product_dot_graph.edge(str(node),str(reachable_node),str(product_graph[node][reachable_node]['weight']))
    return product_dot_graph

def nx_to_graphviz_trans(trans_graph):
    """
    convert networkx graph to a dot graph
    """
    trans_dot_graph=Graph()
    trans_dot_graph.title("transition system")
    for node in list(trans_graph.nodes):
        trans_dot_graph.node(node,node,False)
        for reachable_node in trans_graph[node]:
            trans_dot_graph.edge(node,reachable_node,str(trans_graph[node][reachable_node]['weight']))
    return trans_dot_graph