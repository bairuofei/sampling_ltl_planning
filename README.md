# Introduction
本项目实现了基于线性时序逻辑(Linear Temporal Logic, LTL)的多机器人任务规划。项目包括两种规划方式：
1. 经典(classical)LTL规划方法。即将每个机器人的环境切换系统(transition sytem)融合为联合环境切换系统(product transition system),与LTL生成的buchi automaton相乘，构建完整的乘积自动机(product automaton)。在乘积自动机上运用图搜索算法(Dijkstra)，搜索得到满足LTL任务要求的机器人状态序列。
2. 基于采样(Sampling-based)LTL规划方法。即不再完整构建出联合环境切换系统，而是进行增量式的采样，来搜索乘积自动机的状态空间。
# Installation-系统为Ubuntu16.04
1. 为python3安装**graphviz**模块
```bash
~$ pip install graphviz
```
> 若使用“`pip3 install graphviz`”，提示需要安装pip3工具

2. 下载**ltl2ba**软件包ltl2ba-1.2 .tar.gz并安装。
> ltl2ba-1.2 .tar.gz软件压缩包已经预先下载到工程目录`dependencies`文件夹下
```bash
~$ cd 包含ltl2ba-1.2 .tar.gz的目录下
 $ tar -zxvf ltl2ba-1.2 .tar.gz [-C 目标路径]
 $ cd ltl2ba-1.2
 $ make
 $ export PATH=$PATH:$(pwd)
```
上述方法添加的路径仅在当前shell下有效。为方便起见，我们需要将该路径添加到当前用户的环境变量中。
```bash
 $ pwd
 $ gedit ~/.bashrc
# 在打开的txt文件中，将当前的路径添加到PATH变量中，保存后关闭文件
# 添加格式为： export PATH=$PATH:当前绝对路径

# 运行下一句，则该配置在当前终端窗口立即生效。也可以不执行这一句，新开一个终端窗口，配置信息也会更新
 $ source ~/.bashrc

# 可通过以下命令查看配置是否生效
 $ echo $PYTHONPATH
```
3. \[可选\]下载**spot**软件包并安装
> spot-2.8.5.tar.gz软件压缩包已经预先下载到工程目录｀dependencies`文件夹下

> 详细安装步骤参考[Installing Spot](https://spot.lrde.epita.fr/install.html)，以及软件压缩包中的`README`和`INSTALL`文件
```bash
~$ cd 包含spot-2.8.5.tar.gz的目录下
 $ tar -zxvf spot-2.8.5.tar.gz [-C 目标路径]
 $ cd spot-2.8.5 
# 设置安装目录，可以在--prefix后面指定目录
# 此处在Home目录下建立spot_install文件夹
 $ ./configure --prefix ~/spot_install
 $ make
 $ make install
```
命令行工具：由于没有安装在默认的目录`~/usr`下，因此需要添加文件目录到路径中。
```bash
# 首先将prefix/bin路径添加到系统PATH环境变量
 $ gedit ~/.bashrc
# 添加格式为：　export PATH=$PATH:prefix/bin路径
# 添加结束后重新打开一个终端

# 测试命令行工具是否成功安装
 $ ltl2tgba --version
```
Python bindings： 由于没有安装在默认的目录`~/usr`下，因此需要添加文件目录到路径中
```bash
# 测试Python bindings是否链接成功
 $ python3
 >>> import spot
 >>> print(spot.version())
# 查看当前python搜索路径
 $ python3
 >>> import sys
 >>> print(sys.path)

# 若测试不成功，在~/.bashrc添加PYTHONPATH环境变量
# 添加格式为：　export PYTHONPATH=$PYTHONPATH:文件路径
# 文件路径为：　~/spot_install/lib/python3.7/site-packages

# 可通过以下命令查看配置是否生效
　$ echo $PYTHONPATH
```
Man pages：(路径应该没有问题)
```bash
 $ man spot
# 如果报错"No manual entry for spot"，添加$prefix/man 到环境变量MANPATH中
```

# Project Tree
```bash
.
├── __pycache__
│   
├── dependencies        # 存储ltl2ba工具的未编译源码
│   └── ltl2ba-1.2 .tar.gz
├── test_files          # 编程过程中的一些测试文件
│   ├── test_graph_attr.py
│   ├── test_list_queue.py
│   ├── test_pts.py
│   ├── test_python_entry.py
│   └── test_spot.py
├── gltl2ba.py          # ltl2ba转化功能相关的函数      
├── general_func.py     # 经典方法和采样方法公用的一些函数
├── show_graph.py       # networkx图转化为dot图显示的一些函数
├── trans_sys.py        # 以函数形式给定transition system
├── classical_func.py   # 经典方法用到的一些子函数
├── clasc_ltl_planning.py   # 经典LTL规划主程序
├── sampling_func.py    # 采样方法用到的一些子函数
├── samp_ltl_planning.py    # 采样LTL规划主程序
├── clasc_ltlFile.txt   # *.txt文件存储自动机的never claim格式语句
├── samp_ltlFile.txt
└── README.md
```

# Usage
## 基于product automaton搜索的LTL规划
1. 在文件`trans_sys.py`中，以networkx图的形式给出每个机器人的transition system
2. 在文件`clasc_ltl_planning.py`中，将每个机器人的transition system添加到`trans_graph_list`
3. 在文件`clasc_ltl_planning.py`中，以list形式给定每个机器人的初始位置
4. 在文件`clasc_ltl_planning.py`中，给定LTL表达式，并设置变量`SURVEILLANCE`为`True/False`，表明是否包含巡回任务
5. 运行文件`clasc_ltl_planning.py`


## 基于采样的LTL规划
1. 在文件`trans_sys.py`中，以networkx图的形式给出每个机器人的transition system
2. 在文件`samp_ltl_planning.py`中，将每个机器人的transition system添加到`trans_graph`
3. 在文件`samp_ltl_planning.py`中，以list形式给定每个机器人的初始位置
4. 在文件`samp_ltl_planning.py`中，给定LTL表达式，并设置变量`SURVEILLANCE`为`True/False`，表明是否包含巡回任务
5. 在文件`samp_ltl_planning.py`中，设置采样循环次数`itera_pre_num`和`itera_suf_num`，前者为前缀路径搜索采样次数，后者为后缀路径搜索采样次数
6. 运行文件`samp_ltl_planning.py`

##  其他功能说明
### 绘图功能
1. 对经典LTL规划方法而言，目前提供了对product transition system, buchi automaton和product autumaton三种类型图形的绘制功能，基于graphviz软件包。
> **注意：**　当预估product transition system规模过大时，不建议开启绘图功能。因为绘图所用的时间可能远大于程序规划时间。
2. 对采样LTL规划方法而言，目前提供了对每个机器人的transition system，　buchi automaton和采样搜索树sampling search tree三种类型图形的绘制功能，基于graphviz软件包。


# Problems
当LTL表达式中包含巡回任务时，巡回任务的执行顺序会影响前缀路径的最优性，同时也会影响后缀路径的最优性。

原因在于LTL中的巡回任务的出现顺序会强制规定为这些任务的执行顺序，即实际上在任务执行前就已经规定了任务的执行顺序。
这个特点削弱了LTL进行自动规划的能力。

# Ideas
1. 基于采样的搜索方法在搜索后缀路径时又重新设置了根节点，搜索了一棵新的树。但是搜索前缀路径时所构建的树有可能用于后缀路径的搜索。


# Networkx functions
## Graph attributes
```py
# Add node: 
G.add_node(1, label=['5pm'])

# Add edge: 
G.add_edge(present_state, pat3_str.group(), weight=4)

# Get specific node: 
G.nodes[nodename]

# Get node attr: 
G.nodes[nodename][attr_name]

# Get specific attribute of all nodes: 
color = nx.get_node_attributes(G, 'color')
# return dict type

# Get edge attr: 
G[nodename1][nodename2][attr_name]
# You can also use this line to incrementally adding atttributes.

# Get specific attribute of all edges: 
mix = nx.get_edge_attributes(G, 'mix')
# return dict type

# Get reachable nodes of specific node: 
graph[node_name]

# Node number: 
len(G)

# Edge number: 
G.size()

# Get all nodes: 
G.nodes(data=True)
# Get all nodes name as a list
list(product_graph.nodes(data=True))

# Get all edges: 
G.edges(data=True)
```

## Graph plot
```py
nx.draw(G,\
        pos = nx.random_layout(G)，\
        node_color = 'b',\
        edge_color = 'r',\
        with_labels = True，\
        font_size =18,\
        node_size =20)
```
- pos 指的是布局 主要有spring_layout,random_layout,circle_layout,shell_layout.
- node_color 指节点颜色，有rbykw ,同理edge_color.
- with_labels 指节点是否显示名字,size表示大小，font_color表示字的颜色.



# LTL Formula

对比项：
```bash
# example 1: 不能直接用next,而要用`-> X`， 否则会报错
(<> p1) && (<> p2) && (<> p3) && ([] (p2 X (NOT p3)))      # wrong
(<> p1) && (<> p2) && (<> p3) && ([] (p2 -> X (NOT p3)))   # right

# example 2
(<> p1) && (<> p2) && (<> p3) && ([] ((NOT p2) U p3))      # wrong
(<> p1) && (<> p2) && (<> p3) && ((NOT p2) U p3)           # right

```
构建buchi自动机
```bash
task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p2 -> X p3)

task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p2 -> X(NOT p4))

task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p2 -> X((NOT p4) && p3))

task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p1 -> X(p2 && X(p3 && X(p4)))) 

task_ltl: Fp1 && Fp2 && Fp3 && Fp4 && G(p1->X((NOT p3 && NOT p4)U(p2 && X((NOT p4 && NOT p1)U (p3 && X((NOT p1 && NOT p2)U p4))))))
```

# Others
## Python Function 
- find()方法：查找子字符串，若找到返回从0开始的下标值，若找不到返回1

## python entry
基本数据类型的参数：值传递

列表、元组、字典作为参数：指针传递
> networkx的garph类型进行传递时也是指针传递


# Test case record

## Case4: 2 Robots, 4 trans nodes
```py
    # pay attention to modify the AP label

    trans_graph.add_node('n1',name='n1',label=['p11'])
    trans_graph.add_node('n2',name='n2',label=['p12'])
    trans_graph.add_node('n3',name='n3',label=['p13'])
    trans_graph.add_node('n4',name='n4',label=['p14'])
    trans_graph.add_edge('n1','n3',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n3','n4',weight=3)
    trans_graph.add_edge('n2','n4',weight=3)
    
    trans_graph.add_edge('n3','n1',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n4','n3',weight=3)
    trans_graph.add_edge('n4','n2',weight=3)
    
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1)
    trans_graph.add_edge('n4','n4',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
```
```py
# task 1
task="(<>p14) && ((NOT p14) U p22) && ((NOT p22) U p12) && ([](p12 -> X(NOT p14)))"
SURVEILLANCE=False

# task 2
task="(<>p14) && ((NOT p14) U p22) && ((NOT p22) U p12) && ([](p12 -> X(NOT p14))) && ((NOT p22) U p24) &&  ([](p24 -> X(NOT p22)))"
SURVEILLANCE=False
```

## Case3: 2 Robots, 3 trans nodes
```py
    # pay attention to modify the AP label

    trans_graph.add_node('n1',name='n1',label=['p11'])
    trans_graph.add_node('n2',name='n2',label=['p12'])
    trans_graph.add_node('n3',name='n3',label=['p13'])
    trans_graph.add_edge('n1','n2',weight=3)
    trans_graph.add_edge('n2','n3',weight=3)
    trans_graph.add_edge('n2','n1',weight=3)
    trans_graph.add_edge('n3','n2',weight=3)
    trans_graph.add_edge('n1','n1',weight=0.1)
    trans_graph.add_edge('n2','n2',weight=0.1)
    trans_graph.add_edge('n3','n3',weight=0.1) # we can set a very small number but not zero
    for node in list(trans_graph.nodes):
        trans_graph.nodes[node]['children']=list(trans_graph[node])
```

```py
# task1
task="(<> p23) && ((NOT p22) U p12)"
SURVEILLANCE=False

# task2
task="(<> p23) && ((NOT p22) U p12) && ([](p23 -> p11))"
SURVEILLANCE=False

# task3
task="(<> p23) && ((NOT p22) U p12) && ([](p23 -> p11)) && ((NOT p23) U p13)"
SURVEILLANCE=False

# task4 surveillance
task="([]<> p23) && ([]<> p21) && ((NOT p23) U p13)"
SURVEILLANCE=True
```

## CASE 2: 3 node transition system, surveillance
```py
weight_list=[3,5,1]
task="(<> p1) && ([](<> p2)) && ([](<> p3))"
SURVEILLANCE=True
```

## CASE 1: 1 Robot, 3 node transition system, no surveillance
The case 1 inluding 3 sub cases.
```py
# task 1
weight_list=[3,2,2]
task1="(<> p1) && (<> p2) && (<> p3)"
SURVEILLANCE=False

# task 2
weight_list=[3,5,2]
task2="(<> p1) && (<> p2) && (<> p3) && ([](p3 -> X (NOT p2)))"
SURVEILLANCE=False

# task 3
weight_list=[3,5,1]
task3="(<> p1) && (<> p2) && (<> p3) && ([](p3 -> X (NOT p2))) && ((NOT p3) U p2)"
SURVEILLANCE=False

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
for node in list(trans_graph.nodes):
    trans_graph.nodes[node]['children']=list(trans_graph[node])
```

