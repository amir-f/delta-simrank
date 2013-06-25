#!/usr/bin/env python

import itertools
import numpy
import logging
import argparse
import networkx as nx
import multiprocessing as mp
import traceback
import ctypes

EPS = 1e-4
DIV_EPS = 1e-8


def simrank(G, r=0.8, max_iter=10, eps=EPS):
  """
  This code is based on
  http://www.jontedesco.net/2013/02/01/simrank-in-python/
  """
 
  nodes = G.nodes()
  nodes_i = {k: v for(k, v) in [(nodes[i], i) for i in range(0, len(nodes))]}

  sim_prev = numpy.zeros(len(nodes))
  sim = numpy.identity(len(nodes))

  logging.info('Started iteration')
  for i in range(max_iter):
    if numpy.allclose(sim, sim_prev, atol=eps): logging.info('No change in SimRanks. Stopping...'); break
    sim_prev = numpy.copy(sim)
    for u, v in itertools.product(nodes, nodes):
      if u is v: continue
      u_ns, v_ns = G.neighbors(u), G.neighbors(v)
      s_uv = sum([sim_prev[nodes_i[u_n]][nodes_i[v_n]] for u_n, v_n in itertools.product(u_ns, v_ns)])
      sim[nodes_i[u]][nodes_i[v]] = (r * s_uv) / (len(u_ns) * len(v_ns) + DIV_EPS)
    logging.info('iter %d'%(i + 1))

  return sim


def simrank_map(uv):
  u, v = uv
  if u == v: return
  u_ns, v_ns = G.neighbors(u), G.neighbors(v)
  s_uv = sum([sim_prev[nodes_i[u_n]][nodes_i[v_n]] for u_n, v_n in itertools.product(u_ns, v_ns)])
  sim[nodes_i[u]][nodes_i[v]] = (r * s_uv) / (len(u_ns) * len(v_ns) + DIV_EPS)


def init_pool(G_, nodes_i_, sim_shr, sim_prev_shr, r_):
#  global G, nodes_i, sim, sim_prev, r
  G, nodes_i, r = G_, nodes_i_, r_
  sim = numpy.frombuffer(sim_shr)
  nodes_n = int(numpy.sqrt(len(sim_shr)))
  sim_prev = numpy.frombuffer(sim_prev_shr)
  sim = numpy.reshape(sim, (nodes_n, nodes_n))
  sim_prev = numpy.reshape(sim_prev, (nodes_n, nodes_n))


def prll_simrank(G, r=0.8, max_iter=10, eps=EPS):
  """
  Calculates simrank in parallel using Python Multiprocessing
  """

  nodes = G.nodes()
  nodes_i = {k: v for(k, v) in [(nodes[i], i) for i in range(0, len(nodes))]}
  raw_input(' 1:')
  sim_prev_shr = mp.Array(ctypes.c_double, len(nodes)**2, lock=False)
  sim_shr = mp.Array(ctypes.c_double, len(nodes)**2, lock=False)

  nodes_n = len(nodes)
  raw_input(' 2:')
  sim = numpy.frombuffer(sim_shr)
  sim_prev = numpy.frombuffer(sim_prev_shr)
  sim_prev = numpy.reshape(sim_prev, (nodes_n, nodes_n))
  sim = numpy.reshape(sim, (nodes_n, nodes_n))
  raw_input(' 3:')
  for i in range(nodes_n):
    sim[i][i] = 1.0;
 
  logging.info('Started iteration')
  raw_input(' 4:')
  pool = mp.Pool(mp.cpu_count(), init_pool, (G, nodes_i, sim_shr, sim_prev_shr, r))
  for i in range(max_iter):
    raw_input(' 5:')
    if numpy.allclose(sim, sim_prev, atol=eps): logging.info('No change in SimRanks. Stopping...'); break
    logging.info('Max change in SimRank: %f'%numpy.max(numpy.absolute(sim - sim_prev)))
    logging.info('Copying sim to sim_prev...')
    raw_input(' 6:')
    sim_prev[:,:] = sim[:,:]
    logging.info('Started mapping...')
    try:
      pass
      #pool.map(simrank_map, itertools.product(nodes, nodes))
    except:
      logging.error('Exception in pool map')
      traceback.print_exc()
    logging.info('iter %d'%(i + 1))

  raw_input(' 7:')
  pool.close()
  pool.join()
  return sim


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Calculates SimRank.')
  parser.add_argument('infile', help='input file in graphml format')
  parser.add_argument('outfile', help='output file which will be a npy format')
  parser.add_argument('itr', type=int, help='number of iterations')
  args = parser.parse_args()

  logging.root.setLevel(logging.INFO)
  logging.info('Reading the graph...')
  g = nx.read_graphml(args.infile)
  sim = prll_simrank(g, max_iter=args.itr)
  logging.info('Saving the SimRanks...')
  numpy.save(args.outfile, sim)
