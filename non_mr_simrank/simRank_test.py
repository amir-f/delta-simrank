#!/usr/bin/env python

import unittest
import simRank
import numpy as np
import networkx as nx

class TestSimRank(unittest.TestCase):
  def setUp(self):
    self.g = nx.read_graphml('test/simrank_test_graph_widom.graphml')

  def verify_simrank_results(self, sim, mapping):
    # First the SimRank values matrix should be symmetric
    self.assertTrue(np.allclose(sim, sim.transpose()), msg='sim matrix is not symmetric')
    # Verify approx equality for float values
    ground_truth = [('Univ', 'StudentB', 0.034), ('ProfB', 'StudentA', 0.042),
                    ('ProfA', 'StudentB', 0.106), ('Univ', 'Univ', 1),
                    ('ProfA', 'ProfB', 0.414), ('StudentA', 'StudentB', 0.331),
                    ('Univ', 'ProfB', 0.132), ('ProfB', 'StudentB', 0.088)]
    rnd_sim = np.round(sim, decimals=3)
    for a, b, true_s in ground_truth:
      s = rnd_sim[mapping[a], mapping[b]]
      self.assertTrue(np.allclose(s, true_s),
                      msg='SimRank[%s, %s] == %f\t Expected: %f'%(a, b, s, true_s))

  def test_simrank(self):
    sim, mapping = simRank.simrank(self.g, max_iter=20, r=0.8)
    self.verify_simrank_results(sim, mapping)
    
  def test_prll_simrank(self):
    sim, mapping = simRank.prll_simrank(self.g, max_iter=20, r=0.8)
    self.verify_simrank_results(sim, mapping)


if __name__ == '__main__':
  unittest.main()
