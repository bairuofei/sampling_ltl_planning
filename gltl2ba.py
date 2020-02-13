# -*- coding: utf-8 -*-
from graphviz.dot import Digraph
from subprocess import Popen, PIPE
import re
# import argparsetemporal_logic_planning
import sys
import __main__
import networkx as nx


# draw graph of Buchi Automaton


class Graph:
    def __init__(self):
        self.dot = Digraph()

    def title(self, str):
        self.dot.graph_attr.update(label=str)

    def node(self, name, label, accepting=False):
        num_peripheries = '2' if accepting else '1'
        self.dot.node(name, label, shape='circle', peripheries=num_peripheries)

    def edge(self, src, dst, label):
        self.dot.edge(src, dst, label)

    def show(self,graph_name):
        self.dot.render(graph_name,view=True)

    def save_render(self, path, on_screen):
        self.dot.render(path, view=on_screen)

    def save_dot(self, path):
        self.dot.save(path)

    def __str__(self):
        return str(self.dot)


#
# parser for ltl2ba output
#


class Ltl2baParser:
    prog_title = re.compile('^never\s+{\s+/\* (.+?) \*/$')
    prog_node = re.compile('^([^_]+?)_([^_]+?):$')
    prog_edge = re.compile('^\s+:: (.+?) -> goto (.+?)$')
    prog_skip = re.compile('^\s+(?:skip)$')
    prog_ignore = re.compile('(?:^\s+do)|(?:^\s+if)|(?:^\s+od)|'
                             '(?:^\s+fi)|(?:})|(?:^\s+false);?$')

    @staticmethod
    def parse(ltl2ba_output, ignore_title=True):
        graph = Graph()
        src_node = None
        for line in ltl2ba_output.split('\n'):
            if Ltl2baParser.is_title(line):
                title = Ltl2baParser.get_title(line)
                if not ignore_title:
                    graph.title(title)
            elif Ltl2baParser.is_node(line):
                name, label, accepting = Ltl2baParser.get_node(line)
                graph.node(name, label, accepting)
                src_node = name
            elif Ltl2baParser.is_edge(line):
                dst_node, label = Ltl2baParser.get_edge(line)
                assert src_node is not None
                graph.edge(src_node, dst_node, label)
            elif Ltl2baParser.is_skip(line):
                assert src_node is not None
                graph.edge(src_node, src_node, "(1)")
            elif Ltl2baParser.is_ignore(line):
                pass
            else:
                print("--{}--".format(line))
                raise ValueError("{}: invalid input:\n{}"
                                 .format(Ltl2baParser.__name__, line))
        return graph

    @staticmethod
    def is_title(line):
        return Ltl2baParser.prog_title.match(line) is not None

    @staticmethod
    def get_title(line):
        assert Ltl2baParser.is_title(line)
        return Ltl2baParser.prog_title.search(line).group(1)

    @staticmethod
    def is_node(line):
        return Ltl2baParser.prog_node.match(line) is not None

    @staticmethod
    def get_node(line):
        assert Ltl2baParser.is_node(line)
        prefix, label = Ltl2baParser.prog_node.search(line).groups()
        return (prefix + "_" + label, label,
                True if prefix == "accept" else False)

    @staticmethod
    def is_edge(line):
        return Ltl2baParser.prog_edge.match(line) is not None

    @staticmethod
    def get_edge(line):
        assert Ltl2baParser.is_edge(line)
        label, dst_node = Ltl2baParser.prog_edge.search(line).groups()
        return (dst_node, label)

    @staticmethod
    def is_skip(line):
        return Ltl2baParser.prog_skip.match(line) is not None

    @staticmethod
    def is_ignore(line):
        return Ltl2baParser.prog_ignore.match(line) is not None
    
    
    
def ltl_formula_to_ba(ltl,LTL_FILE_POS,show_graph):
    """调用gltl2ba,将ltl表达式转化为never claim
    将promela表达式转化成一个有向图,返回有向图"""
    buchi_init_state=[]
    buchi_accept_state=[]
    # 调用gltl2ba,将ltl表达式转化为never claim并存储在txt中
    gltl2ba(ltl,LTL_FILE_POS,show_graph)
    # 预编译正则表达式
    pat_state = re.compile(r'\w*_\w*')
    pat_transtion = re.compile(r'(?<=::.).*(?=.->)')
    pat_endstate = re.compile(r'(?<=goto.)\w*_\w*')
    # 提取所有的状态
    f = open(LTL_FILE_POS,'r')
    line = f.readline()
    G=nx.DiGraph()
    while line:
        if (line[0]!='\t') and (line[0:5]!='never') and line[0]!='}': # 说明是状态行
            pat1_str=pat_state.search(line)
            if pat1_str.group().find('init')!=-1:     # 说明是init
                G.add_node(pat1_str.group(),name=pat1_str.group(),label='init')
                buchi_init_state.append(pat1_str.group())
            elif pat1_str.group().find('accept')!=-1:  # 说明是accpet状态
                G.add_node(pat1_str.group(),name=pat1_str.group(),label='accept')
                buchi_accept_state.append(pat1_str.group())
            else:
                G.add_node(pat1_str.group(),name=pat1_str.group())
        line = f.readline()
    f.close()    
    # 提取边及边的label
    f = open(LTL_FILE_POS,'r')
    line = f.readline()
    present_state=''
    while line:
        if (line[0]!='\t') and (line[0:5]!='never') and line[0]!='}': # 说明是状态行
            pat1_str=pat_state.search(line)
            present_state=pat1_str.group()
        elif line[0:3]=='\t::':
            pat2_str=pat_transtion.search(line)
            pat3_str=pat_endstate.search(line)
            G.add_edge(present_state, pat3_str.group(), label=pat2_str.group())    
        line = f.readline()
    f.close()
    return G,buchi_init_state,buchi_accept_state



def gltl2ba(ltl,LTL_FILE_POS,show_graph):

    (output, err, exit_code) = run_ltl2ba(ltl)

    if exit_code != 1:
        with open(LTL_FILE_POS,"w") as f:
            f.write(output)

        prog = re.compile("^[\s\S\w\W]*?"
                          "(never\s+{[\s\S\w\W]+?})"
                          "[\s\S\w\W]+$")
        match = prog.search(output)
        assert match, output

        graph = Ltl2baParser.parse(match.group(1))
        if show_graph:
            graph.show('buchi_graph')
#       print(graph)
    else:
        eprint("{}: ltl2ba error:".format(__main__.__file__))
        eprint(output)
        sys.exit(exit_code)
    return


def run_ltl2ba(ltl):
    ltl2ba_args = ["ltl2ba", "-f", ltl]
    
    try:
        process = Popen(ltl2ba_args, stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()
    except FileNotFoundError as e:
        eprint("{}: ltl2ba not found.\n".format(__main__.__file__))
        eprint("Please download ltl2ba from\n")
        eprint("\thttp://www.lsv.fr/~gastin/ltl2ba/ltl2ba-1.2b1.tar.gz\n")
        eprint("compile the sources and add the binary to your $PATH, e.g.\n")
        eprint("\t~$ export PATH=$PATH:path-to-ltlb2ba-dir\n")
        sys.exit(1)

    output = output.decode('utf-8')

    return output, err, exit_code

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
    

