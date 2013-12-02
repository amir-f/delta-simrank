#!/usr/bin/env python

import itertools
import numpy
import logging
import argparse
import networkx as nx
import multiprocessing as mp
import traceback
import ctypes
import json

EPS = 1e-4
DIV_EPS = 1e-8
CHUNK_SIZE = 2000

__all__ = ['simrank', 'prll_simrank']

def simrank(G, r=0.8, max_iter=10, eps=EPS):
  """
  This code is based on
  http://www.jontedesco.net/2013/02/01/simrank-in-python/
  """
 
  nodes = G.nodes()
  pred_func = G.predecessors if isinstance(G, nx.DiGraph) else G.neighbors
  nodes_i = {k: v for(k, v) in [(nodes[i], i) for i in range(0, len(nodes))]}

  sim_prev = numpy.zeros(len(nodes))
  sim = numpy.identity(len(nodes))

  logging.info('Started iteration')
  for i in range(max_iter):
    if numpy.allclose(sim, sim_prev, atol=eps): logging.info('No change in SimRanks. Stopping...'); break
    sim_prev = numpy.copy(sim)
    for u, v in itertools.product(nodes, nodes):
      if u is v: continue
      u_ps, v_ps = pred_func(u), pred_func(v)
      s_uv = sum([sim_prev[nodes_i[u_n]][nodes_i[v_n]] for u_n, v_n in itertools.product(u_ps, v_ps)])
      sim[nodes_i[u]][nodes_i[v]] = (r * s_uv) / (len(u_ps) * len(v_ps) + DIV_EPS)
    logging.info('iter %d'%(i + 1))

  return sim, nodes_i


def simrank_map(uvps):
  u, v, u_ps, v_ps = uvps
  if u == v: return
  s_uv = sum([sim_prev[nodes_i[u_n]][nodes_i[v_n]] for u_n, v_n in itertools.product(u_ps, v_ps)])
  sim[nodes_i[u]][nodes_i[v]] = (r * s_uv) / (len(u_ps) * len(v_ps) + DIV_EPS)


def init_pool(nodes_n, nodes_i_, sim_shr, sim_prev_shr, r_):
  global nodes_i, sim, sim_prev, r
  nodes_i, r = nodes_i_, r_
  sim = numpy.frombuffer(sim_shr).view()
  sim_prev = numpy.frombuffer(sim_prev_shr).view()
  sim.shape = (nodes_n, nodes_n)
  sim_prev.shape = (nodes_n, nodes_n)
  for i in range(nodes_n):
    sim[i][i] = 1.0;
 

def prll_simrank(G, r=0.8, max_iter=10, eps=EPS):
  """
  Calculates simrank in parallel using Python Multiprocessing
  """
 
  nodes = G.nodes()
  nodes_i = {k: v for(k, v) in [(nodes[i], i) for i in range(0, len(nodes))]}
  sim_prev_shr = mp.Array(ctypes.c_double, len(nodes)**2, lock=False)
  sim_shr = mp.Array(ctypes.c_double, len(nodes)**2, lock=False)
 
  logging.info('Started iteration')
  init_pool(len(nodes), nodes_i, sim_shr, sim_prev_shr, r)
  pool = mp.Pool(mp.cpu_count())
  pred_func = G.predecessors if isinstance(G, nx.DiGraph) else G.neighbors
 
  for i in range(max_iter):
    if numpy.allclose(sim, sim_prev, atol=eps): logging.info('No change in SimRanks. Stopping...'); break
    logging.info('Max change in SimRank: %f'%numpy.max(numpy.absolute(sim - sim_prev)))
    logging.info('Copying sim to sim_prev...')
    sim_prev[:,:] = sim[:,:]
    logging.info('Started mapping...')
    try:
      pool.map(simrank_map,
                [(u, v, pred_func(u), pred_func(v)) for u, v in itertools.product(nodes, nodes)],
                chunksize=CHUNK_SIZE)
    except:
      logging.error('Exception in pool map')
      traceback.print_exc()
    logging.info('iter %d'%(i + 1))
 
  pool.close()
  pool.join()
  return sim, nodes_i


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Calculates SimRank.')
  parser.add_argument('infile', help='input file in graphml format')
  parser.add_argument('outfile', help='output filename. There will be a .npy file create for the SimRank values matrix and another list in JSON format where the index of each graph node label corresponds to its index in the matrix')
  parser.add_argument('itr', type=int, help='number of iterations')
  parser.add_argument('--parallel', action='store_true',
                      help='Use python multiprocessing to speed up calculation')
  parser.add_argument('--verbose', action='store_true', help='Output more verbose log')
  args = parser.parse_args()

  logging.root.setLevel(logging.WARNING) if not args.verbose else logging.root.setLevel(logging.DEBUG)
  logging.info('Reading the graph...')
  g = nx.read_graphml(args.infile)
  if args.parallel:
    logging.info('Calculating SimRank in Parallel...')
    sim_mat, mapping = prll_simrank(g, max_iter=args.itr)
  else:
    logging.info('Calculating SimRank not in Parallel...')
    sim_mat, mapping = simrank(g, max_iter=args.itr)
  logging.info('Saving the SimRanks...')
  numpy.save('%s_simrank_mat.npy'%args.outfile, sim_mat)
  logging.info('Saving the mapping...')
  with open('%s_simrank_mapping.json'%args.outfile, 'w') as out_file:
    json.dump(sorted(mapping, key=mapping.get), out_file)
