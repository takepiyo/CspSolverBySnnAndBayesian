# Projects: sudoku_pgm
#
# :Author: Jaco du Toit <jacowp357@gmail.com>
# :Date: 01/12/2016
# :Description: Attempt at solving Sudoku (4x4) by using a
#               probabilistic graphical model (PGM) approach.
#
from pgmpy.models import FactorGraph
from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.inference import BeliefPropagation
import numpy as np

if __name__ == '__main__':
    n = 4
    grid = np.arange(n ** 2).reshape(n, n)

    G = FactorGraph()

    # set variable nodes #
    for i in range(n ** 2):
        G.add_node('v_%d' % (i))

    # set variable nodes #
    for i in range(n ** 2):
        G.add_node('r_%d' % (i))

    # set cpd for received cells #
    cpd = []
    for x1 in range(n):
        for x2 in range(n):
            if x1 == x2:
                cpd.append(1)
            else:
                cpd.append(0)

    # setup the fr potentials #
    for i in range(n ** 2):
        locals()["fr_%d" % (i)] = DiscreteFactor(
            ['r_%d' % (i), 'v_%d' % (i)], cardinality=[4, 4], values=cpd)
        G.add_factors(locals()["fr_%d" % (i)])
        G.add_edge('v_%d' % (i), locals()["fr_%d" % (i)])
        G.add_edge('r_%d' % (i), locals()["fr_%d" % (i)])

    # set cpd for row, column and brick factors #
    cpd = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    if len(set([i, j, k, l])) == n:
                        cpd.append(1)
                    else:
                        cpd.append(0)

    # set row factors #
    j = 0
    for i in range(n):
        var = ['v_%d' % (0 + j), 'v_%d' % (1 + j), 'v_%d' %
               (2 + j), 'v_%d' % (3 + j)]
        locals()["frow_%d" % (i)] = DiscreteFactor(var, [4, 4, 4, 4], cpd)
        G.add_factors(locals()["frow_%d" % (i)])
        for edge in var:
            G.add_edge(edge, locals()["frow_%d" % (i)])
        j += 4

    # set column factors #
    j = 0
    for i in range(n):
        var = ['v_%d' % (0 + j), 'v_%d' % (4 + j), 'v_%d' %
               (8 + j), 'v_%d' % (12 + j)]
        locals()["fcol_%d" % (i)] = DiscreteFactor(var, [4, 4, 4, 4], cpd)
        G.add_factors(locals()["fcol_%d" % (i)])
        for edge in var:
            G.add_edge(edge, locals()["fcol_%d" % (i)])
        j += 1

    # set brick factors #
    k = len(grid) // 2
    a, b, c, d = grid[:k, :k], grid[k:, :k], grid[:k, k:], grid[k:, k:]
    bricks = [a, b, c, d]
    for i in range(n):
        elem = bricks[i]
        var = ['v_%d' % (elem[0][0]), 'v_%d' % (elem[0][1]),
               'v_%d' % (elem[1][0]), 'v_%d' % (elem[1][1])]
        locals()["fbrick_%d" % (i)] = DiscreteFactor(var, [4, 4, 4, 4], cpd)
        G.add_factors(locals()["fbrick_%d" % (i)])
        for edge in var:
            G.add_edge(edge, locals()["fbrick_%d" % (i)])

    print(G.check_model())

    # inference #
    belief_propagation = BeliefPropagation(G)
    phi_query = belief_propagation.query(variables=['v_0'], evidence={
                                         'r_1': 0, 'r_2': 2, 'r_4': 1, 'r_11': 2, 'r_13': 1, 'r_14': 0})
    print(phi_query['v_0'])
