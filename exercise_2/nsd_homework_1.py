#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh zhou'

#!/usr/bin/env python 2.7.8
# -*- coding: utf-8 -*-

'''
This program is about Part 2 'Basic operations and properties'.
'''

import functools ,time, itertools, operator, math
import matplotlib.pyplot as plt

# a dectorator used to compute run time in a fucntion
def run_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        end_time = time.time()
        print "Computation Time of %s: %s" % (func.__name__.capitalize(), end_time - start_time)
        return result
    return wrapper

# used to count combination (n r)
def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)

class Graph(object):
    '''
    a graph contains info
    '''
    def __init__(self, dataset = None):

        self.dataset = []
        self.process_dataset(dataset)

        self.node_file = dataset.split('.')[0] + '_graphe.n'
        self.node_number = 0
        self.compute_node_number()

        self.degree_file = dataset.split('.')[0] + '_graphe.dg'
        self.degree_table = []
        
        # key is No. node, value is its neighbour nodes 
        self.nodes_dict = {}

        self.graph_in_memory = []

        # key is degree, value is number of nodes
        self.degree_distribution = {}
        self.degree_distribution_file = dataset.split('.')[0] + '_graphe.dn'

        self.cum_degree_distribution = {}


    # exercise_2 : compute the number of nodes
    @run_time
    def compute_node_number(self):
        l = []
        for element in self.dataset:
            for i in element:
                l.append(i)
        with open(self.node_file,'w') as fn:
            fn.write(str(max(l)))
        self.node_number = max(l)
    
    # exercise_3 : compute the degree of each node
    @run_time
    def compute_node_degree(self):
        self.degree_table = [0] * (self.node_number + 1)
        for element in self.dataset:
            for i in element:
                if self.degree_table[i] != 0:
                    self.degree_table[i] += 1
                else:
                    self.degree_table[i] = 1
        with open(self.degree_file, 'w') as fd:
            for n in self.degree_table:
                fd.write('%s\n' % n)
    
    # exercise_4 : store in the memory
    @run_time
    def store_in_memory(self):
        self.graph_in_memory = [0] * sum(self.degree_table)
        # build the index table for storage table 
        index_table =[]
        index_base = 0
        for i in self.degree_table:
            index_table.append(index_base)
            index_base += i
        # index of i and j
        for element in self.dataset:
            i, j = element
            # the index of certain node in storage table
            index_i, index_j = index_table[i], index_table[j]
            # add the node to each other's table
            self.graph_in_memory[index_i] = j
            index_table[i] += 1
            self.graph_in_memory[index_j] = i
            index_table[j] += 1
        print self.graph_in_memory
        return self.graph_in_memory

    # exercise_5 : compute some infos about graph
    @run_time
    def graph_infos(self):
        print 'Numbers of degree 0: %s' % self.degree_table.count(0)
        print 'Max Degree: %s' % max(self.degree_table) 
        print 'Min Degree: %s' % min(self.degree_table)
        print 'Average Degree: %s' % (sum(self.degree_table) * 1.0 / len(self.degree_table))
        print 'Density of graph: %s' % (1.0 * sum(self.degree_table) / (len(self.degree_table) * (len(self.degree_table) - 1)))

    # exercise_6 : compute the degree distrubition
    @run_time
    def compute_degree_distribution(self):
        for degree in self.degree_table:
            if degree in self.degree_distribution:
                self.degree_distribution[degree] += 1
            else:
                self.degree_distribution[degree] = 1
        with open(self.degree_distribution_file, 'w') as f:
            for degree, node in self.degree_distribution.iteritems():
                f.write('%s %s\n' % (degree , node))

    # exercise_7 : delete loop & duplicate element like (i,j) & (j,i) 
    @run_time
    def process_dataset(self, dataset):
        with open(dataset, 'r') as f:
            l = []
            for line in f.readlines():
                i, j = [int(x) for x in line.strip().split(' ')] 
                if i != j:
                    l.append([i, j] if i >j else [j, i])
            for k, g in itertools.groupby(sorted(l)):
                self.dataset.append(k)
        return self.dataset

    # exercise_8 : compute the cumlative degree distribution
    @run_time
    def cumlative_degree_distribution(self):
        self.cum_degree_distribution = self.degree_distribution.copy()
        # link copy and cum_degree_distribution just for easily reading
        copy = self.cum_degree_distribution
        n = 0 #inital nodes = 0
        for degree in sorted(copy.keys()):
            n = copy[degree] + n # add nodes has bigger degree to previous nodes
            copy[degree] = n
        return self.cum_degree_distribution

    @run_time
    def compute_nodes_dict(self):
        self.nodes_dict = {n:[] for n in xrange(self.node_number + 1)}
        for element in self.dataset:
            i, j = element
            self.nodes_dict[i].append(j)
            self.nodes_dict[j].append(i)
        return self.nodes_dict

    @run_time
    def make_plot(self):
        plot1, plot2 = self.degree_distribution, self.cum_degree_distribution
        f, (ax1, ax2) = plt.subplots(1, 2, sharex=True)
        ax1.scatter(plot1.keys(), plot1.values())
        ax1.axis([1, 1000, 1, 10000])
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax2.scatter(plot2.keys(), plot2.values())
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        plt.show()

    @run_time
    def compute_all(self):
        self.compute_node_number()
        print self.node_number
        self.compute_node_degree()
        print self.degree_table
        self.store_in_memory()
        self.graph_infos() 
        self.compute_degree_distribution()
        print self.degree_distribution
        self.cumlative_degree_distribution()
        print self.cum_degree_distribution
        self.compute_nodes_dict()

# exercise_10 : compute cluster coefficient and transitive ratio for each node 
@run_time
def compute_density(graph):
    cc, tr = [], 0
    num_v, num_tri, sum_tri = 0, 0, 0
    for n, v in graph.nodes_dict.iteritems():
        if v == []:
            cc.append('Undefined') # cc of node without connection should be undefined
        elif len(v) == 1:
            cc.append(0.0) # 1 neighbour => no value
        else:
            num_v += nCr(len(v), 2)
            for u1 in v:
                for u2 in graph.nodes_dict[u1]:
                    if u2 in v:
                        num_tri += 1
            # (u1, u2) and (u2, u1) should be same, my algorithm counts twice,so here merge them
            num_tri = num_tri / 2.0
            sum_tri += num_tri
            cc.append((2 * num_tri)/ (len(v) * (len(v) - 1) )) 
            num_tri = 0     
    tr = sum_tri / num_v
    print cc
    print tr


# exercise_11 : show the BFS of graph

def bfs(graph, s):
    discovered = {}
    level = [s]
    discovered[s] = 0
    while len(level) > 0:
        next_level = []
        for u1 in level:
            for u2 in graph.nodes_dict[u1]:
                if u2 not in discovered:
                    discovered[u2] = discovered[u1] + 1
                    next_level.append(u2)
        level = next_level
    sorted_discovered = sorted(discovered.items(), key = operator.itemgetter(1))
    print ['%d => %d ' % (k, v ) for v, k in sorted_discovered]

# exercise_12 : compute the 

def compute_size(graph):
    discovered = [None] * len(graph.nodes_dict.keys()) 
    for x,_ in enumerate(discovered):
        if discovered[x] is None:
            if not graph.nodes_dict[x]:
                discovered[x] = 'connectless'
            else:
                level = [x]
                while len(level) > 0:
                    next_level = []
                    for u1 in level:
                        for u2 in graph.nodes_dict[u1]:
                            if discovered[u2] is None:
                                discovered[u2] = x
                                next_level.append(u2)
                    level = next_level
    component = {}
    for k, g in itertools.groupby(sorted(discovered)):
        if k != 'connectless':
            size = len(list(g))
            component[k] = size
            print 'component: %s, size: %s' % (k, size)
    sorted_componet = sorted(component.items(), key = operator.itemgetter(0))
    d = {}
    for size in sorted(component.values()):
        if size in d:
            d[size] += 1
        else:
            d[size] = 1
    print d
    #plt.scatter(d.values(), d.keys())
    #plt.axis([1, 100, 1, 100])
    #plt.xscale('log')
    #plt.yscale('log')
    #plt.show()

    # exercies_13 : isloate the biggest componet
    root = sorted_componet[0][0]
    size = sorted_componet[0][1]
    print 'biggest component: %d, size: %d' % (root, size)
    biggest_component = []
    for x,_ in enumerate(discovered):
        if discovered[x] == root:
            biggest_component.append(x)
    print biggest_component

# exercise 14

def set_of_shortest_paths(graph):
    discovered = {x:[] for x in graph.nodes_dict.keys()}
    stage_table = [0] * (graph.node_number + 1)
    print graph.nodes_dict
    print graph.nodes_dict[4]
    for x,_ in enumerate(discovered):
        if not discovered[x]:
            if not graph.nodes_dict[x]:
                discovered[x] = 'disconnected'
                stage_table[x] = 'disconnected'
            else:
                level = [x]
                discovered[x].append(-1)
                while len(level) > 0:
                    next_level = []
                    for u1 in level:
                        for u2 in graph.nodes_dict[u1]:
                            if len(discovered[u2]) == 0:
                                stage_table[u2] = stage_table[u1] + 1
                                discovered[u2].append(u1)
                                next_level.append(u2)
                            elif len(discovered[u2]) > 0:
                                if stage_table[u2] == stage_table[u1] + 1:
                                    if u1 not in discovered[u2]:
                                        discovered[u2].append(u1)
                    level = next_level
    print discovered
    print stage_table
    return [discovered, stage_table]

# exercise 15



if __name__  == "__main__":
    
    g = Graph('dataset.txt')
    g.compute_all()
    compute_density(g)
    bfs(g, 0)
    compute_size(g)
    set_of_shortest_paths(g)



