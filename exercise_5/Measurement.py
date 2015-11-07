#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Quan zhou'

import os
import time
import functools
import argparse
import logging
import itertools
import collections
import math
import random

def run_time(func):
    '''
    A dectorator used to compute run time in a fucntion
    '''
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        end_time = time.time()
        print "Computation Time of %s: %s" % \
              (func.__name__.capitalize(), end_time - start_time)
        return result
    return wrapper

def mkdir(func):
    '''
    A Fast Way to create a dir
    '''
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print dir(func)
        dir_name = func.__name__
        dirpath = os.path.join('outputs/', dir_name)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        result = func(*args, **kw)
        return result
    return wrapper


DATASETS = {'o': 'Flickr', 't': 'Flickr-test', 'i' : 'inet' }

def nCr(n,r):
    '''
    Return math combination nCr
    '''
    f = math.factorial
    return f(n) / f(r) / f(n-r)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dataset",
        nargs='?',
        type=str,
        help="Select the dataset your want to create the file. \
                Default is 'Flickr-test'",
        default='t'
    )
    return parser.parse_args()

class Graph(object):
    '''
    a graph contains infos about node number, degree, neighours tables of node,
    degree distrubition, and its cumlative degree distribution.
    '''
    def __init__(self, dataname = None):
        self.outputs_path = os.path.join('outputs/', dataname, 'graphs/')
        self.processed_dataset = self._process_dataset(dataname)
        self.node_number = self._compute_node_number()
        self.degree_table = self._compute_node_degree()
        self.nodes_edges = self._compute_nodes_edges()
        self.degree_distribution = self._compute_degree_distribution()

    def _process_dataset(self, dataname):
        '''
        Return the datasets by deleting the possible loops in the original links.
        '''
        datasets_path = os.path.join('datasets/', dataname)
        if not os.path.exists(self.outputs_path):
            os.makedirs(self.outputs_path)
        processed_dataname = os.path.join(self.outputs_path, 
                                          os.path.basename(datasets_path))
        dataset_list = []
        with open(datasets_path, 'r') as f1:
            with open(processed_dataname, 'w') as f2:
                for line in f1.readlines():
                    i, j = [int(x) for x in line.strip().split(' ')]
                    if i != j:
                        dataset_list.append((i,j))
                        f2.write('%i %i\n' % (i, j))
        return dataset_list

    def _compute_node_number(self):
        '''
        Return the node number.
        '''
        n = max([max(i,j) for i, j in self.processed_dataset])
        with open(os.path.join(self.outputs_path, 'graph.n'), 'w') as f:
            f.write(str(n))
        return n

    def _compute_node_degree(self):
        '''
        Return node degree table.
        '''
        degree_table = [0] * (self.node_number + 1)
        for i, j in self.processed_dataset:
            degree_table[i] += 1
            degree_table[j] += 1
        with open(os.path.join(self.outputs_path, 'graph.deg'), 'w') as f:
            for n in degree_table:
                f.write('%s\n' % n)
        return degree_table

    def _compute_nodes_edges(self):
        '''
        Return nodes edges in lists.
        '''
        nodes_edges = collections.defaultdict(list)
        for i, j in self.processed_dataset:
            nodes_edges[i].append(j)
            nodes_edges[j].append(i)  
        return nodes_edges

    def _compute_degree_distribution(self):
        '''
        Return the degree distribution.
        '''
        degree_distribution = collections.defaultdict(int)
        for degree in self.degree_table:
            degree_distribution[degree] += 1
        with open(os.path.join(self.outputs_path, 'graph.dn'), 'w') as f:
            for degree, node in degree_distribution.iteritems():
                f.write('%s %s\n' % (degree , node))
        return degree_distribution
    
    def _cumlative_degree_distribution(self):
        '''
        Return the cumlative degree distribution.
        '''
        cum_degree_distribution = self.degree_distribution.copy()
        n = 0 #inital nodes = 0
        for degree in reversed(sorted(cum_degree_distribution.keys())):
            n = cum_degree_distribution[degree] + n # add nodes has bigger degree to previous nodes
            cum_degree_distribution[degree] = n
        return cum_degree_distribution

    def _compute_triangle_values(self):
        '''
        Return Global Transitive Ratio & Global Clustering Coefficient.
        '''
        value_cc = {}
        num_v, num_tri, sum_tri = 0, 0, 0
        for node in self.nodes_edges.keys():
            if len(self.nodes_edges[node]) <= 1:
                value_cc[node] = 0 
            else:
                num_v += nCr(len(self.nodes_edges[node]), 2)
                for neighbour in self.nodes_edges[node]:
                    for neighbour_of_neighbour in self.nodes_edges[neighbour]:
                        if neighbour_of_neighbour in self.nodes_edges[node]:
                            num_tri += 1
                # (u1, u2) and (u2, u1) should be same, my algorithm counts twice,so here merge them
                num_tri = num_tri / 2.0
                sum_tri += num_tri
                value_cc[node] = (2 * num_tri)/ (len(self.nodes_edges[node]) * (len(self.nodes_edges[node]) - 1) )
                num_tri = 0
        average_tr = sum_tri / num_v
        average_cc = (sum(value_cc.values()) / self.node_number)
        return average_tr, average_cc

    def _average_clustering(self, trials = 1000):
        '''
        Return the approximations of Average clustering.
        '''
        triangles = 0
        for node in [random.randint(0, self.node_number) for _ in xrange(trials)]:
            neighbours = self.nodes_edges[node]
            if len(neighbours) < 2:
                continue
            u, v = random.sample(neighbours, 2)
            if u in self.nodes_edges[v]:
                triangles += 1
        return triangles/ float(trials)


    def graph_infos(self):
        '''
        Print all the characteriscs of the graph.
        '''
        print 'Numbers of degree 0: %s' % self.degree_table.count(0)
        print 'Max Degree: %s' % max(self.degree_table)
        print 'Min Degree: %s' % min(self.degree_table)
        print 'Average Degree: %s' % (sum(self.degree_table) * 1.0 / len(self.degree_table))
        print 'Density: %0.11f' % (2.0 * sum(self.degree_table) / (self.node_number * (self.node_number - 1)))
        print 'Approximations of verage clustering coefficient: %0.11f' % self._average_clustering()
        #print 'transitive ratio: %0.11f\naverage clustering coefficient: %0.11f' % (self._compute_triangle_values())

class Simulation(object):

    def __init__(self, dataname):
        pass


    def measure_primitive(self):
        pass

    @staticmethod
    def random_strategy():
        pass

    @staticmethod
    def simple_strategy():
        pass

    @staticmethod
    def refine_strategt():
        pass



if __name__ == '__main__':
    # Set the log level
    logging.basicConfig(level=logging.INFO)
    cmd = parse_args()
    # Find the data
    try:
        d = DATASETS[cmd.dataset]
    except KeyError:
        print 'Please input the correct abbrevations of filename'
    c = Graph(d)
    c.graph_infos()


