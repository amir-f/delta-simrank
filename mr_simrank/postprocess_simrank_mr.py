#!/usr/bin/env python

__author__ = 'Amir Fayazi'

import argparse
import logging
import json
import numpy as np
import networkx as nx


def postprocess_simrank_mr(infile, outfile, nodes_n):
  logging.info('Reading the simrank file...')
  sim = np.ndarray((nodes_n, nodes_n))
  with open(infile, 'r') as f:
    for line in f:
      k, v = line.split('\t')
      a, b = json.loads(k)
      a, b = int(a), int(b)
      v = float(v)
      sim[a][b] = v
  
  np.save(outfile, sim)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Reads the output of MapReduced simrank and forms a python dictionary out of it.')
  parser.add_argument('infile', help='input file in simrank format')
  parser.add_argument('outfile', help='output file as a python pickle')
  parser.add_argument('graphfile', help='the graph which the simrank belongs to')
  args = parser.parse_args()

  logging.root.setLevel(logging.INFO)
  logging.info('Reading the graph...')
  g = nx.read_graphml(args.graphfile)
  postprocess_simrank_mr(args.infile, args.outfile, len(g))
