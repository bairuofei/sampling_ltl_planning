# -*- coding: utf-8 -*-
import networkx as nx

g = nx.DiGraph()  # 创建空的有向图
g.add_edge(1, 2, weight=3)
g.add_edge(2, 3, weight=3)
g.add_edge(3, 1, weight=3)
g.add_edge(1, 1, weight=2)
g.add_edge(2, 2, weight=2)
# g.add_edge(3, 3, weight=2)

one_suf_path = nx.dijkstra_path(g, 3,
                                3, weight='weight')
