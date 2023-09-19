# Introduction

This repo implements the Linear Temporal Logic(LTL)-based multi-robot task planning. 
It includes two different methods for solving the LTL-based multi-robot task planning problem:
1. Graph search-based method (high complexity) 
2. Sampling-based methods (more efficient )


You can find more related details in our paper:
```
@INPROCEEDINGS{9636287,
  author={Bai, Ruofei and Zheng, Ronghao and Liu, Meiqin and Zhang, Senlin},
  booktitle={2021 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)}, 
  title={Multi-Robot Task Planning under Individual and Collaborative Temporal Logic Specifications}, 
  year={2021},
  volume={},
  number={},
  pages={6382-6389},
  doi={10.1109/IROS51168.2021.9636287}}
```

# Installation (tested on Ubuntu16.04)

1.Install **graphviz** package (Python 3)

> [Graphviz - Graph Visualization Software](https://www.graphviz.org/)

```bash
~$ pip install graphviz
```

> If you use “`pip3 install graphviz`”，you may need to install `pip3` first. 

2.Download **ltl2ba** package `ltl2ba-1.2 .tar.gz` and install.

> [LTL2BA: fast translation from LTL formulae to Büchi automata](http://www.lsv.fr/~gastin/ltl2ba/index.php)

> You can find `ltl2ba-1.2 .tar.gz` that we use under the `dependencies` folder.

```bash
~$ cd to the folder containing ltl2ba-1.2 .tar.gz
 $ tar -zxvf ltl2ba-1.2 .tar.gz [-C target_directory]
 $ cd ltl2ba-1.2
 $ make
 $ export PATH=$PATH:$(pwd)
```

You can also add the path to the global environment `PATH` variable:
```bash
 $ pwd
 $ gedit ~/.bashrc
# Add current path to the file, save and exit.
# Example： export PATH=$PATH:current_path

# Source to make the configuration take effect in current terminal
 $ source ~/.bashrc

# Check whether the path is correctly set 
 $ echo $PYTHONPATH
```

# Functions of each file

```bash
.
├── clasc_ltl_planning.py       # Main function for tradition graph-based search method
├── classical_planning.log      # Log file for graph-based search method
├── samp_ltl_planning.py        # Main function for sampling-based method
├── samp_planning.log           # Log file for sampling-based search method
├── compare_two.py              # 经典与采样LTL规划集成主程序
├── compare.log                 # 调试日志及求解结果
├── simulation.py               # Example code for visualize the results
├── robot_navigation.mp4        # 仿真程序存储得到的mp4视频
├── dependencies                # 存储ltl2ba工具的未编译源码
│   └── ltl2ba-1.2 .tar.gz
├── func_set
│   ├── __init__.py
│   ├── classical_func.py       # 经典方法用到的一些子函数
│   ├── general_func.py         # 经典方法和采样方法公用的一些函数
│   ├── gltl2ba.py              # ltl2ba转化功能相关的函数
│   ├── sampling_func.py        # 采样方法用到的一些子函数
│   ├── show_graph.py           # networkx图转化为dot图显示的一些函数
│   └── trans_sys.py            # 构造transition system的函数
├── robot_ts                    # 用户指定任务要求及无人机加权切换系统
│   ├── caseA.txt
│   ├── caseG.txt
│   ├── e-robot1.txt
│   ├── f-robot1.txt
│   └── r-robot1.txt
└── README.md                   # 使用说明

```

# How to define your own task specification

## Graph search-based LTL planning

1. 在子文件夹`robot_ts`中，以txt文件格式给出全局任务要求，以及每个无人机的加权切换系统；
2. 在文件`clasc_ltl_planning.py`中，将包含全局任务要求的txt文件路径添加到程序读取列表中；
3. 运行文件`clasc_ltl_planning.py`；
4. 运行结果记录在`classical_planning.log`文件中。

## Sampling-based LTL planning

1. 在子文件夹`robot_ts`中，以txt文件格式给出全局任务要求，以及每个无人机的加权切换系统；
2. 在文件`samp_ltl_planning.py`中，将包含全局任务要求的txt文件路径添加到程序读取列表中；
3. 运行文件`samp_ltl_planning.py`；
4. 运行结果记录在`samp_planning.log`文件中。

## 基于图搜索与采样的LTL规划算法对比

1. 在子文件夹`robot_ts`中，以txt文件格式给出全局任务要求，以及每个无人机的加权切换系统；
2. 在文件`compare_two.py`中，将包含全局任务要求的txt文件路径添加到程序读取列表中；
3. 运行文件`compare_two.py`；
4. 运行结果记录在`compare.log`文件中。

# 其他说明

## LTL表达式语法

> 摘自[LTL2BA: fast translation from LTL formulae to Büchi automata](http://www.lsv.fr/~gastin/ltl2ba/index.php)

> 本项目中的LTL表达式采用Spin语法。

一个LTL表达式由命题变量，布尔运算符，时序运算符和括号组成。在不同命题之间需要用空格隔开。

命题变量包含下面几种类型:

```text
        true, false
        any lowercase string
```

布尔运算符包括下面几种类型：
> 注意：建议使用NOT代替！

```text
        !   (negation)
        ->  (implication)
        <-> (equivalence)
        &&  (and)
        ||  (or)
```

时序运算符包括下面几种类型：

```text
        G   (always) (Spin syntax : [])
        F   (eventually) (Spin syntax : <>)
        U   (until)
        R   (realease) (Spin syntax : V)
        X   (next)
```
## 全局任务要求txt文件书写格式

在任务描述部分，需要通过txt文件对全局任务要求和每个无人机的加权切换系统进行描述。以下举两个示例进行说明：
```py
# task_config.txt:
{
    "robots_config_file":["robot1_ts.txt"],   # 任务涉及的无人机切换系统的txt描述文件，多个文件用逗号隔开
    "path_weight":[1,200],                    # 前缀及后缀路径的执行次数
    "robots_init_pos":["s1"],                 # 无人机的初始位置，多个无人机用逗号隔开
    "ltl_task":"(<>r_l1) && (<>r_l2) && (<>r_l3)",  # 全局任务要求
    "itera_pre_num":150,                      # 采样规划中前缀路径采样迭代次数
    "itera_suf_num":80                        # 采样规划中后缀路径采样迭代次数
}
```
```py
# robot1_ts.txt:
{
    "robot_name":"r-robot",
    "transgraph_node": [{"name":"s1","label":["e_s1"]},
                        {"name":"u1","label":["e_u1"]},
                        {"name":"c1","label":["e_c1", "e_c"]}],
    "transgraph_edge": [{"current":"s1","successor":"u1","weight":3},
                        {"current":"u1","successor":"c1","weight":3},
                        {"current":"c1","successor":"s1","weight":3}]
}
```

## 绘图功能

1. 对经典LTL规划方法而言，目前提供了对product transition system, buchi automaton和product autumaton三种类型图形的绘制功能，基于graphviz软件包。

> **注意：**　当预估product transition system规模过大时，不建议开启绘图功能。因为绘图所用的时间可能远大于程序规划时间。

2. 对采样LTL规划方法而言，目前提供了对每个机器人的transition system，buchi automaton和采样搜索树sampling search tree三种类型图形的绘制功能，基于graphviz软件包。

## 仿真界面展示

仿真界面展示程序为一个单独的程序模块。由于仿真界面需要设置无人机实际战场环境中各区域的位置与形状，在实际求解多无人机任务规划问题时相对独立，因此没有与上述求解程序连接，以避免过多的参数设置。

仿真程序修改步骤：  
1. 在`simulation.py`文件中修改`region_list`，对作战区域的名称、位置及种类进行定义；
2. 在`simulation.py`文件中修改`task_set`，包含任务规划得到的无人机任务序列；
3. 在`simulation.py`文件中定义每个无人机的轨迹颜色，初始位置等参数；
4. 运行`simulation.py`文件，展示仿真界面。

现有程序中的仿真界面如下图所示：



## Buchi自动机优化选项

将LTL表达式转化为一个Buchi automaton，会有很多种可能的自动机化简方法。本项目所使用的**ltl2ba**工具包中，提供了部分选项用于修改自动机的化简方式.

```bash
# 在终端输入以下指令
~$ ltl2ba -h
# 终端显示以下配置选项。默认为"-c" "-f".可以在gltl2ba.py文件中修改.
usage: ltl2ba [-flag] -f 'formula'
                   or -F file
 -f 'formula' translate LTL into never claim
 -F file like -f, but with the LTL formula stored in a 1-line file
 -d  display automata (D)escription at each step
 -s  computing time and automata sizes (S)tatistics
 -l  disable (L)ogic formula simplification
 -p  disable a-(P)osteriori simplification
 -o  disable (O)n-the-fly simplification
 -c  disable strongly (C)onnected components simplification
 -a  disable trick in (A)ccepting conditions
```


# 参考资料

1. 经典LTL规划方法参考论文: [*Optimal path planning for surveillance with temporal-logic constraints.*](https://pdfs.semanticscholar.org/1fbb/cec5ffaf45af9317c5bddf8f5cf6a365d14f.pdf) Smith,S.L.,etc. (2011).  The International Journal of Robotics Research, 30(14), 1695–1708.
2. 基于采样LTL规划方法参考论文： [*Sampling-Based Optimal Control Synthesis for Multi-Robot Systems under Global Temporal Tasks.*](https://arxiv.org/pdf/1706.04216.pdf) Kantaros, Yiannis & Zavlanos, Michael. (2017). IEEE Transactions on Automatic Control. PP. 10.1109/TAC.2018.2853558.
3. `gltl2ba.py`中,将ltl2ba功能包的命令行输出结果通过管道读取到程序中的函数，参考自Github项目[gltl2ba](https://github.com/PatrickTrentin88/gltl2ba).
