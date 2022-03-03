# -*- coding: utf-8 -*-
import json
import networkx as nx


def compute_trans_graph(robot_xml_file):
    with open("./robot_ts/"+robot_xml_file, 'r') as f:
        config = json.loads(f.read())

    trans_graph = nx.DiGraph()
    for node in config['transgraph_node']:
        trans_graph.add_node(
            node['name'], name=node['name'], label=node['label'])

    for edge in config['transgraph_edge']:
        trans_graph.add_edge(
            edge['current'], edge['successor'], weight=edge['weight'])

    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children'] = list(trans_graph[node])
    return trans_graph
