import itertools
import numpy
import logging
import argparse
import networkx as nx
import pydevd

EPS = 1e-8

def simrank(G, r=0.8, max_iter=10, eps=EPS):
 
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
            sim[nodes_i[u]][nodes_i[v]] = (r * s_uv) / (len(u_ns) * len(v_ns) + EPS)
        logging.info('iter %d'%(i + 1))
 
    return sim

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Calculates SimRank.')
  parser.add_argument('infile', help='input file in graphml format')
  parser.add_argument('itr', type=int, help='number of iterations')
  args = parser.parse_args()

  g = nx.read_graphml(args.infile)
  #pydevd.settrace('192.168.11.214', port=45634, stdoutToServer=True, stderrToServer=True)
  logging.root.setLevel(logging.WARNING)
  print simrank(g, max_iter=args.itr)
