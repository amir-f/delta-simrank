#!/usr/bin/env python

__author__ = 'Amir Fayazi'

import networkx as nx
from itertools import product
import argparse
import cPickle as pickle
import logging


def preprocess_graph_mr(g, infile, outdir):
  outfile_prefix = '%s/%s'%(outdir, infile)
  logging.info('Converting the graph into a directed graph...')
  g = nx.DiGraph(g)
  logging.info('Converting node labels to integers...')
  g = nx.convert_node_labels_to_integers(g, discard_old_labels=False)
  logging.info('Storing node label to integer label mapping...')
  with open('%s_labelmap.pickle'%outfile_prefix, 'wb') as f:
    pickle.dump(g.node_labels, f)
  logging.info('Storing directed graph...')
  nx.write_graphml(g, '%s.digraph'%outfile_prefix)

  del g.node_labels
  logging.info('Forming the MapReduce input file...')
  ctr, MAX_CTR, pctg = 0.0, len(g)**2, 0.0
  with open('%s.txt'%outfile_prefix, 'w') as f:
      for a, b in product(g.nodes(), g.nodes()):
          f.write('%d,%d\n'%(a, b))
          # Percentage report
          ctr += 1
          if round(ctr/MAX_CTR * 10) > pctg:
            pctg = round(ctr/MAX_CTR * 10)
            logging.info('%d %% done...'%(int(pctg)*10))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Prepares a graph for mapreduce version of delta simrank.')
  parser.add_argument('infile', help='input file in graphml format')
  parser.add_argument('outdir', help='output dir')
  args = parser.parse_args()

  logging.root.setLevel(logging.INFO)
  logging.info('Reading the graph...')
  g = nx.read_graphml(args.infile)
  preprocess_graph_mr(g, args.infile, args.outdir)
