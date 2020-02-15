# Problems
当LTL表达式中包含巡回任务时，巡回任务的执行顺序会影响前缀路径的最优性，同时也会影响后缀路径的最优性。
原因在于LTL中的巡回任务的出现顺序会强制规定为这些任务的执行顺序，即实际上在任务执行前就已经规定了任务的执行顺序。
这个特点削弱了LTL进行自动规划的能力。

# Ideas
1. 基于采样的搜索方法在搜索后缀路径时又重新设置了根节点，搜索了一棵新的树。但是搜索前缀路径时所构建的树有可能用于后缀路径的搜索。
2. 

# networkx
## graph attributes
Add node: `G.add_node(1, label=['5pm'])`
Add edge: `G.add_edge(present_state, pat3_str.group(), weight=4)`

Get specific node: `G.nodes[nodename]`
Get node attr: `G.nodes[nodename][attr_name]`
Get specific attribute of all nodes: `color = nx.get_node_attributes(G, 'color')`
> return dict type

Get edge attr: `G[nodename1][nodename2][attr_name]
> You can also use this line to incrementally adding atttributes.

Get specific attribute of all edges: `mix = nx.get_edge_attributes(G, 'mix')`
> return dict type

Get reachable nodes of specific node: `graph[node_name]`

Node number: `len(G)`
Edge number: `G.size()`
Get all nodes: `G.nodes(data=True)` `list(product_graph.nodes(data=True))`
Get all edges: `G.edges(data=True)`


## graph plot
```py
nx.draw(G,pos = nx.random_layout(G)，node_color = 'b',edge_color = 'r',\
    with_labels = True，font_size =18,node_size =20)
```
- pos 指的是布局 主要有spring_layout , random_layout,circle_layout,shell_layout。
- node_color指节点颜色，有rbykw ,同理edge_color.
- with_labels指节点是否显示名字,size表示大小，font_color表示字的颜色。



# LTL Formula

> 注意：不能直接用next,而要用`-> X`， 否则会报错

对比项：
```bash
(<> p1) && (<> p2) && (<> p3) && (<> p4) && ([] (p2 X (NOT p3)))      # wrong
(<> p1) && (<> p2) && (<> p3) && (<> p4) && ([] (p2 -> X (NOT p3)))   # right
```
构建buchi自动机
task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p2 -> X p3)
task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p2 -> X(NOT p4))
task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p2 -> X((NOT p4) && p3))
task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p1 -> X(p2 && X(p3 && X(p4)))) 
task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p1->X((NOT p3 && NOT p4)U(p2 && X((NOT p4 && NOT p1)U (p3 && X((NOT p1 && NOT p2)U p4))))))

# others
find()方法：查找子字符串，若找到返回从0开始的下标值，若找不到返回1

## python entry
基本数据类型的参数：值传递

列表、元组、字典作为参数：指针传递
> including networkx garph

# Test Case

## Case1: 3 node transition system, no surveillance
```py
# task ltl formula
task1="(<> p1) && (<> p2) && (<> p3)"
surveillance_task=False
# task2="(<> p1) && (<> p2) && (<> p3) && ([](p3 -> X (NOT p2)))"
# task3="(<> p1) && (<> p2) && (<> p3) && ([](p3 -> X (NOT p2))) && ((NOT p3) U p2)"

weight_list1=[3,2,2]
# weight_list2=[3,5,2]
# weight_list3=[3,5,1]
trans_graph=nx.DiGraph()
trans_graph.add_node('n1',name='n1',label=['p1'])
trans_graph.add_node('n2',name='n2',label=['p2'])
trans_graph.add_node('n3',name='n3',label=['p3'])
trans_graph.add_edge('n1','n2',weight=weight_list[0])
trans_graph.add_edge('n2','n3',weight=weight_list[1])
trans_graph.add_edge('n1','n3',weight=weight_list[2])
trans_graph.add_edge('n2','n1',weight=weight_list[0])
trans_graph.add_edge('n3','n2',weight=weight_list[1])
trans_graph.add_edge('n3','n1',weight=weight_list[2])
trans_graph.add_edge('n1','n1',weight=0)
trans_graph.add_edge('n2','n2',weight=0)
trans_graph.add_edge('n3','n3',weight=0)
```

## Case2: 3 node transition system, no surveillance
```py
task="(<> p1) && ([](<> p2)) && ([](<> p3))"
surveillance_task=True

weight_list3=[3,5,1]
```

## Case3: Two Robots
task="(F p11) && (F p12) && (F p13) && (F p21) && (F p22) && (F p23) && (F p24) && ((NOT p22) U p12) && ((NOT p23) U p13)"

task="(F p11) && (F p12) && (F p13) && (F p24) && ((NOT p22) U p12) && ((NOT p23) U p13)"

task="(F p24) && ((NOT p22) U p12) && ((NOT p23) U p13)"

task="(F p23) && ((NOT p22) U p12)"
