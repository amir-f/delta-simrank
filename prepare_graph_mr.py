#!/usr/bin/env python

__author__ = 'Amir Fayazi'

import networkx as nx
from itertools import product
import argparse
import cPickle as pickle
import logging


def prepare_graph_mr(g, outfile):
  logging.info('Converting the graph into a directed graph...')
  g = nx.DiGraph(g)
  logging.info('Converting node labels to integers...')
  g = nx.convert_node_labels_to_integers(g, discard_old_labels=False)
  logging.info('Storing node label to integer label mapping...')
  with open('%s_oldlabels.pickle'%outfile, 'wb') as f:
    pickle.dump(g.node_labels, f)

  logging.info('Forming the MapReduce input file...')
  ctr, MAX_CTR, pctg = 0.0, len(g)**2, 0.0
  with open(outfile, 'w') as f:
      for a, b in product(g.nodes(), g.nodes()):
          a_ps = [str(n) for n in g.predecessors(a)]
          b_ps = [str(n) for n in g.predecessors(b)]
          ab_nss = len(g.successors(a))*len(g.successors(b))
          f.write('%d,%d\t%s,%s,%d\n'%(a, b, ' '.join(a_ps), ' '.join(b_ps), ab_nss))
          # Percentage report
          ctr += 1
          if round(ctr/MAX_CTR * 10) > pctg:
            pctg = round(ctr/MAX_CTR * 10)
            logging.info('%d percent complete...'%(int(pctg)*10))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Prepares a graph for mapreduce version of delta simrank.')
  parser.add_argument('infile', help='input file in graphml format')
  parser.add_argument('outfile', default='g_mapred_input.txt', help='outputfile in textual format to be read by mapper of mapreduce')
  args = parser.parse_args()

  logging.root.setLevel(logging.INFO)
  logging.info('Reading the graph...')
  g = nx.read_graphml(args.infile)
  prepare_graph_mr(g, args.outfile)
