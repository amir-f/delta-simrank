#!/usr/bin/env python

__author__ = 'Amir Fayazi'


from mrjob.job import MRJob
from itertools import product
import collections
#import pydevd

EPS = 1e-8

class MRSimRank(MRJob):
  """
  This class implements MapReduce version of SimRank using the method Delta SimRank

  See:
    http://researcher.watson.ibm.com/researcher/files/us-bbfinkel/Delta-SimRank Computing on MapReduce.pdf
    http://ilpubs.stanford.edu:8090/508/1/2001-41.pdf
  """

  def configure_options(self):
    """Allows SimRank parameters to be configured via command line"""
    super(MRSimRank, self).configure_options()
    self.add_passthrough_option('--decay-factor', type='float', default=0.8, help='SimRank decay factor')
    self.add_passthrough_option('--iters', type='int', default=5, help='Number of iterations')

  def init_mapper(self, key, value):
    """
    This mapper reads the prepared input text file and initializes the SimRank values.
    For each pair of nodes, mapers and reducers pass its information through. This information
    includes the list of each node's predecessors, the current value of delta and SimRank and
    the size of the successors of the pair
    The calculation is done by each node emiting its own delta to all node pairs which this pair
    is a successor on the G^2 graph.
    """

    key, value = value.split('\t')
    a, b = key.split(',')
    a, b = int(a), int(b)
    if a == b:
      sim = 1
    else:
      sim = 0
    a_ps, b_ps, ab_nss = value.split(',')
    a_ps, b_ps = a_ps.split(' '), b_ps.split(' ')
    a_ps = [int(n) for n in a_ps]
    b_ps = [int(n) for n in b_ps]
    ab_nss = int(ab_nss)
    yield (a, b), (a_ps, b_ps, ab_nss, sim)

    for c, d in product(a_ps, b_ps):
      yield (c,d), sim
  

  def delta_reducer(self, key, values):
    """
    The reducer updates the value of delta and subsequently the value of SimRank for each pair
    of node. It also passes the node information through.
    """

    a, b = key
    deltas = []
    for v in values:
      if not isinstance(v, collections.Iterable):
        deltas.append(v)
      else:
        a_ps, b_ps, ab_nss, sim = v
    if a == b:
      delta = 0
    else:
      delta = self.options.decay_factor*sum(deltas)/(ab_nss + EPS)
    sim += delta
    yield key, (delta, a_ps, b_ps, ab_nss, sim)


  def delta_mapper(self, key, value):
    """
    This mapper does the same thing as the init_mapper but assumes the input is coming from a 
    previous run of delta_reducer.
    See the description of init_mapper
    """

    a, b = key
    delta, a_ps, b_ps, ab_nss, sim = value

    yield key, (a_ps, b_ps, ab_nss, sim)
    if a == b or delta <= EPS:
      return
    for c, d in product(a_ps, b_ps):
      yield (c,d), delta


  def final_reducer(self, key, values):
    """
    This reducer only strips off all the node information other than its SimRank
    """

    values = list(values)
    assert len(values) == 1
    delta, a_ps, b_ps, ab_nss, sim = values[0]
    yield key, sim


  def steps(self):
    """
    Runs the mappers and reducers subsequently until the desired number of iterations are
    performed
    """

    steps_list = [self.mr(mapper=self.init_mapper, reducer=self.delta_reducer)]
    for i in range(self.options.iters - 1):
      steps_list.append(self.mr(mapper=self.delta_mapper, reducer=self.delta_reducer))
    steps_list.append(self.mr(reducer=self.final_reducer))
    return steps_list


if __name__ == '__main__':
  MRSimRank.JOBCONF['mapred.job.name'] = MRSimRank.__name__
  MRSimRank.JOBCONF['mapred.job.priority'] = 'NORMAL'
  MRSimRank.run()
