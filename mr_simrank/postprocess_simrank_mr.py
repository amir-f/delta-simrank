#!/usr/bin/env python

__author__ = 'Amir Fayazi'

import argparse
import logging
import json
import cPickle as pickle


def postprocess_simrank_mr(infile, outfile):
  logging.info('Reading the simrank file...')
  sim = {}
  with open(infile, 'r') as f:
    for line in f:
      k, v = line.split('\t')
      a, b = json.loads(k)
      a, b = int(a), int(b)
      v = float(v)
      if a not in sim: sim[a] = {}
      sim[a][b] = v
  
  with open(outfile, 'wb') as f:
    pickle.dump(sim, f)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Reads the output of MapReduced simrank and forms a python dictionary out of it.')
  parser.add_argument('infile', help='input file in simrank format')
  parser.add_argument('outfile', help='output file as a python pickle')
  args = parser.parse_args()

  logging.root.setLevel(logging.INFO)
  postprocess_simrank_mr(args.infile, args.outfile)
