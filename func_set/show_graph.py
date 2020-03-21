# -*- coding: utf-8 -*-

from func_set.gltl2ba import Graph


def nx_to_graphviz_product(product_graph):
    """
    convert networkx product graph to a dot graph
    """
    product_dot_graph = Graph()
    product_dot_graph.title("product automaton")
    for node in list(product_graph.nodes):
        if product_graph.nodes[node]['accept']:
            product_dot_graph.node(
                str(node), product_graph.nodes[node]['name'], True)
        else:
            product_dot_graph.node(
                str(node), product_graph.nodes[node]['name'], False)
        for reachable_node in product_graph[node]:
            product_dot_graph.edge(str(node), str(reachable_node), str(
                product_graph[node][reachable_node]['weight']))
    return product_dot_graph


def nx_to_graphviz_trans(trans_graph):
    """
    convert networkx graph to a dot graph
    """
    trans_dot_graph = Graph()
    trans_dot_graph.title("transition system")
    for node in list(trans_graph.nodes):
        trans_dot_graph.node(node, node, False)
        for reachable_node in trans_graph[node]:
            trans_dot_graph.edge(node, reachable_node, str(
                trans_graph[node][reachable_node]['weight']))
    return trans_dot_graph


def nx_to_graphviz_tree(search_tree):
    """
    convert nx tree to dot graph
    """
    search_dot_tree = Graph()
    search_dot_tree.title("sampling search tree")
    for node in list(search_tree.nodes):
        if search_tree.nodes[node]['buchi_name'].find('accept') != -1:
            search_dot_tree.node(str(node), str(
                search_tree.nodes[node]['ts_label']), True)
        else:
            search_dot_tree.node(str(node), str(
                search_tree.nodes[node]['ts_label']), False)
        for child_node in search_tree.nodes[node]['children']:
            search_dot_tree.edge(str(node), str(child_node), str(
                search_tree[node][child_node]['label']))
    return search_dot_tree


# def nx_to_graphviz_tree(search_tree):
#    """
#    convert nx tree to dot graph
#    """
#    search_dot_tree=Graph()
#    search_dot_tree.title("sampling search tree")
#    for node in list(search_tree.nodes):
#        if search_tree.nodes[node]['buchi_name'].find('accept')!=-1:
#            search_dot_tree.node(str(node),search_tree.nodes[node]['name'],True)
#        else:
#            search_dot_tree.node(str(node),search_tree.nodes[node]['name'],False)
#        for child_node in search_tree.nodes[node]['children']:
#            search_dot_tree.edge(str(node),str(child_node),str(search_tree[node][child_node]['weight']))
#    return search_dot_tree
