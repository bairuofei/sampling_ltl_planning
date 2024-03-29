# Introduction

This repo implements the Linear Temporal Logic(LTL)-based multi-robot task planning. 
It includes two different methods for solving the LTL-based multi-robot task planning problem:
1. Graph search-based method (inefficient) 
2. Sampling-based method (more efficient)


You can find the extended work based on this repo in the following paper:
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
├── compare_two.py              # Main function includes both tradition and sampling-based methods
├── compare.log                 # Log and results
├── simulation.py               # Example code for visualize the results
├── dependencies                # Our archived ltl2ba package source code
│   └── ltl2ba-1.2 .tar.gz
├── func_set
│   ├── __init__.py
│   ├── classical_func.py       # Functions used in the traditional method
│   ├── general_func.py         # Commonly used functions by both methods
│   ├── gltl2ba.py              # ltl2ba
│   ├── sampling_func.py        # Functions used in the sampling-based method
│   ├── show_graph.py           # Visualization, from networkx to dot
│   └── trans_sys.py            # Construct transition system
├── robot_ts                    # User-defined task specification and robot transition system
│   ├── caseA.txt
│   ├── caseG.txt
│   ├── e-robot1.txt
│   ├── f-robot1.txt
│   └── r-robot1.txt
└── README.md                   

```

# Specify your task requirements

## Graph search-based LTL planning

1. In subdirectory `robot_ts`, specify global task specification and each robot's transition system in `.txt` files
2. Modify the path to the `.txt` files in `clasc_ltl_planning.py`
3. Run `clasc_ltl_planning.py`；
4. You can find the obtained solution in `classical_planning.log`

## Sampling-based LTL planning

1. In subdirectory `robot_ts`, specify global task specification and each robot's transition system in `.txt` files
2. Modify the path to the `.txt` files in `samp_ltl_planning.py`
3. Run `samp_ltl_planning.py`；
4. You can find the obtained solution in `samp_planning.log`

## Comparison of the two methods

1. In subdirectory `robot_ts`, specify global task specification and each robot's transition system in `.txt` files
2. Modify the path to the `.txt` files in `compare_two.py`
3. Run `compare_two.py`；
4. You can find the obtained solution in `compare.log`

# Appendices

## Syntax of LTL language

> Copyed from [LTL2BA: fast translation from LTL formulae to Büchi automata](http://www.lsv.fr/~gastin/ltl2ba/index.php)

> We follow the `Spin` convention of LTL language in this repo.

A LTL formula includes atom propositions, boolean operators, temporal operators and parentheses. 

The atom proposition should be one of the following types:

```text
        true, false
        any lowercase string
```

The boolean operators include the following:
> NOTE: Use `NOT` rather than `!` for negation

```text
        !   (negation)
        ->  (implication)
        <-> (equivalence)
        &&  (and)
        ||  (or)
```

The temporal operators include the following:

```text
        G   (always) (Spin syntax : [])
        F   (eventually) (Spin syntax : <>)
        U   (until)
        R   (realease) (Spin syntax : V)
        X   (next)
```
## Format of task specification

We need two types of files to define the task requirements and the robots' transition systems, respectively.

1. The task specification `.txt` file (Defined once)
```py
# task_config.txt:
{
    "robots_config_file":["robot1_ts.txt"],   # Include all robot_ts.txt, separated by comma
    "path_weight":[1,200],                    # Number of repetitions to execute the prefix and suffix paths
    "robots_init_pos":["c1"],                 # Initial positions of the robots in their transition system, separated by comma
    "ltl_task":"(<>c1) && (<>c2) && (<>c3)",  # Global LTL task specification
    "itera_pre_num":150,                      # Sampling thresholds in prefix path finding
    "itera_suf_num":80                        # Sampling thresholds in suffix path finding
}
```

2. The robot transition system `.txt` file. (Defined for each robot respectively)

```py
# robot1_ts.txt:
{
    "robot_name":"robot-1",
    "transgraph_node": [{"name":"c1","label":["c1"]},
                        {"name":"c2","label":["c2"]},
                        {"name":"c3","label":["c3", "c4"]}],
    "transgraph_edge": [{"current":"c1","successor":"c2","weight":3},
                        {"current":"c2","successor":"c3","weight":3},
                        {"current":"c3","successor":"c1","weight":3}]
}
```

## Büchi automaton visualization

1. For traditional graph search-based LTL planning method, we provide the visualization of product transition system, buchi automaton and product autumaton, based on `graphviz` package.

> **NOTE:**　If the size of the product transition system is too large，the graph rendering may be much slower than solely solving the problem, in which case you should not use the visualization function.

2. For sampling-based LTL planning method, we support the visualization of the robot's transition system，büchi automaton and sampling search tree, also based on `graphviz` package.




## Parameters for Büchi automaton generation

There are many parameters you can specify to simplify the Büchi automaton constructed from the LTL specification.
In **ltl2ba** package, the existing parameters are shown below:

```bash
# Type following in the terminal
~$ ltl2ba -h
# By default, we set the indicators "-c" and "-f" in gltl2ba.py
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


# Reference

1. Traditional graph search-based method: [*Optimal path planning for surveillance with temporal-logic constraints.*](https://pdfs.semanticscholar.org/1fbb/cec5ffaf45af9317c5bddf8f5cf6a365d14f.pdf) Smith,S.L.,etc. (2011).  The International Journal of Robotics Research, 30(14), 1695–1708.
2. Sampling-based method： [*Sampling-Based Optimal Control Synthesis for Multi-Robot Systems under Global Temporal Tasks.*](https://arxiv.org/pdf/1706.04216.pdf) Kantaros, Yiannis & Zavlanos, Michael. (2017). IEEE Transactions on Automatic Control. PP. 10.1109/TAC.2018.2853558.
3. We read the terminal output of the `ltl2ba` package to `gltl2ba.py` by following the repo [gltl2ba](https://github.com/PatrickTrentin88/gltl2ba).