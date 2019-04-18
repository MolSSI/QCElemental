# [Apr 2019]
# * split off from gph_uno_bipartite.py file for test suite. see that file for attributions.
# * AmbiguousSolution errors seem to have cropped up, though not in the alignment usage.

import pytest
from ..tests.addons import using_networkx, using_scipy

from qcelemental.util.gph_uno_bipartite import uno, _enumMaximumMatching, _enumMaximumMatching2


@using_networkx
def test_example4(alg=1):

    edges = [(0, 0),
            (0, 1),
            (1, 5),
            (1, 6),
            (2, 0),
            (2, 1),
            (3, 5),
            (3, 6),
            (4, 2),
            (4, 3),
            (5, 2),
            (5, 3),
            (6, 4),
            (6, 7),
            (7, 4),
            (7, 7)]
    match = [(0, 0), (2, 1), (4, 2), (5, 3), (6, 4), (3, 5), (1, 6), (7, 7)]

    ref = [[(0, 0), (2, 1), (4, 2), (5, 3), (6, 4), (3, 5), (1, 6), (7, 7)],  # ----
           [(0, 1), (2, 0), (4, 2), (5, 3), (6, 4), (3, 5), (1, 6), (7, 7)],  # *---

           [(0, 0), (2, 1), (4, 3), (5, 2), (6, 4), (3, 5), (1, 6), (7, 7)],  # -*--
           [(0, 1), (2, 0), (4, 3), (5, 2), (6, 4), (3, 5), (1, 6), (7, 7)],  # **--

           [(0, 0), (2, 1), (4, 2), (5, 3), (6, 7), (3, 5), (1, 6), (7, 4)],  # --*-
           [(0, 1), (2, 0), (4, 2), (5, 3), (6, 7), (3, 5), (1, 6), (7, 4)],  # *-*-

           [(0, 0), (2, 1), (4, 2), (5, 3), (6, 4), (3, 6), (1, 5), (7, 7)],  # ---*
           [(0, 1), (2, 0), (4, 2), (5, 3), (6, 4), (3, 6), (1, 5), (7, 7)],  # *--*

           [(0, 0), (2, 1), (4, 3), (5, 2), (6, 7), (3, 5), (1, 6), (7, 4)],  # -**-
           [(0, 1), (2, 0), (4, 3), (5, 2), (6, 7), (3, 5), (1, 6), (7, 4)],  # ***-

           [(0, 0), (2, 1), (4, 3), (5, 2), (6, 4), (3, 6), (1, 5), (7, 7)],  # -*-*
           [(0, 1), (2, 0), (4, 3), (5, 2), (6, 4), (3, 6), (1, 5), (7, 7)],  # **-*

           [(0, 0), (2, 1), (4, 3), (5, 2), (6, 7), (3, 6), (1, 5), (7, 4)],  # -***
           [(0, 1), (2, 0), (4, 3), (5, 2), (6, 7), (3, 6), (1, 5), (7, 4)],  # ****

           [(0, 0), (2, 1), (4, 2), (5, 3), (6, 7), (3, 6), (1, 5), (7, 4)],  # --**
           [(0, 1), (2, 0), (4, 2), (5, 3), (6, 7), (3, 6), (1, 5), (7, 4)],  # *-**
        ]
    ref = [sorted(r) for r in ref]

#cost:
# [[ 0.000  0.000  83.505  83.505  53.406  3.378  3.378  53.406]
# [ 3.398  3.398  53.169  53.169  29.828  0.000  0.000  29.828]
# [ 0.000  0.000  83.293  83.293  53.237  3.336  3.336  53.237]
# [ 3.359  3.359  53.323  53.323  29.944  0.000  0.000  29.944]
# [ 83.559  83.559  0.000  0.000  3.372  53.380  53.380  3.372]
# [ 83.297  83.297  0.000  0.000  3.320  53.171  53.171  3.320]
# [ 53.240  53.240  3.379  3.379  0.000  29.830  29.830  0.000]
# [ 53.468  53.468  3.322  3.322  0.000  30.001  30.001  0.000]]
#ptsCR [(0, 0), (2, 1), (4, 2), (5, 3), (6, 4), (3, 5), (1, 6), (7, 7)]

#    ans = uno(edges, verbose=2)
#    _check('Example 4a (internal match)', ans, ref, verbose=2)

    ans = uno(edges, verbose=2, match=match)
    _check('Example 4b (provided match)', ans, ref, verbose=2)


@using_networkx
def test_example3(alg=1):

    match = [(1, 2), (3, 4), (5, 6), (7, 8)]
    edges = [(1, 2),
             (1, 4),
             (1, 6),
             (3, 4),
             (3, 6),
             (3, 8), 
             (5, 6),
             (5, 8),
             (5, 2),
             (7, 8),
             (7, 2),
             (7, 4)]

    ref = [ [(1, 2), (3, 6), (5, 8), (7, 4)],
            [(1, 2), (3, 4), (5, 6), (7, 8)],
            [(1, 2), (3, 8), (5, 6), (7, 4)],
            [(1, 4), (3, 6), (5, 2), (7, 8)],
            [(1, 4), (3, 6), (5, 8), (7, 2)],
            [(1, 4), (3, 8), (5, 6), (7, 2)],
            [(1, 6), (3, 4), (5, 2), (7, 8)],
            [(1, 6), (3, 4), (5, 8), (7, 2)],
            [(1, 6), (3, 8), (5, 2), (7, 4)]]

    ans = uno(edges, verbose=2)
    _check('Example 3a (internal match)', ans, ref)

    ans = uno(edges, verbose=2, match=match)
    _check('Example 3b (provided match)', ans, ref, verbose=2)


def _check(msg, ans, ref, verbose=1):

    tans = [tuple(qw) for qw in ans]
    tref = [tuple(qw) for qw in ref]
    extra_answers = set(tans).difference(set(tref))
    missd_answers = set(tref).difference(set(tans))
    if verbose >= 2:
        for a in tans:
            print('Computed:', a)
        for a in tref:
            print('Supplied:', a)

    assert (extra_answers == set())
    assert (missd_answers == set())
    #    print(msg, 'failed:')
    #    if extra_answers != set():
    #        for a in extra_answers:
    #            print('Incomplete Ref:', a)
    #    if missd_answers != set():
    #        for a in missd_answers:
    #            print('Incomplete Soln:', a)


@using_networkx
@pytest.mark.parametrize("alg", [
    pytest.param(1),
    pytest.param(2, marks=using_scipy),
])
def test_example2(alg):
    """https://mathematica.stackexchange.com/questions/77410/find-all-perfect-matchings-of-a-graph/82893#82893"""
    import networkx as nx

    g = nx.Graph()
    edges = [[(1, 1), (0, 2)],
             [(1, 1), (0, 4)],
             [(1, 1), (0, 6)],
             [(1, 3), (0, 4)],
             [(1, 3), (0, 6)],
             [(1, 3), (0, 8)], 
             [(1, 5), (0, 6)],
             [(1, 5), (0, 8)],
             [(1, 5), (0, 2)],
             [(1, 7), (0, 8)],
             [(1, 7), (0, 2)],
             [(1, 7), (0, 4)]]

#1 <-> 2, 3 <-> 6, 4 <-> 7, 5 <-> 8
#1 <-> 2, 3 <-> 4, 5 <-> 6, 7 <-> 8
#1 <-> 2, 3 <-> 8, 4 <-> 7, 5 <-> 6
#1 <-> 4, 2 <-> 5, 3 <-> 6, 7 <-> 8
#1 <-> 4, 2 <-> 7, 3 <-> 6, 5 <-> 8
#1 <-> 4, 2 <-> 7, 3 <-> 8, 5 <-> 6
#1 <-> 6, 2 <-> 5, 3 <-> 4, 7 <-> 8
#1 <-> 6, 2 <-> 7, 3 <-> 4, 5 <-> 8
#1 <-> 6, 2 <-> 5, 3 <-> 8, 4 <-> 7

#Match2: [(1, 2), (3, 6), (5, 8), (7, 4)]
#Match2: [(1, 2), (3, 4), (5, 6), (7, 8)]
#Match2: [(1, 2), (3, 8), (5, 6), (7, 4)]
#Match2: [(1, 4), (3, 6), (5, 2), (7, 8)]
#Match2: [(1, 4), (3, 6), (5, 8), (7, 2)]
#Match2: [(1, 4), (3, 8), (5, 6), (7, 2)]
#Match2: [(1, 6), (3, 4), (5, 2), (7, 8)]
#Match2: [(1, 6), (3, 4), (5, 8), (7, 2)]
#Match2: [(1, 6), (3, 8), (5, 2), (7, 4)]

    for ii in edges:
        g.add_node(ii[0], bipartite=0)
        g.add_node(ii[1], bipartite=1)

    g.add_edges_from(edges)
    #plotGraph(g)

    if alg == 1:
        all_matches = _enumMaximumMatching(g)
    elif alg == 2:
        all_matches = _enumMaximumMatching2(g)

    ref = [ [(1, 2), (3, 6), (5, 8), (7, 4)],
            [(1, 2), (3, 4), (5, 6), (7, 8)],
            [(1, 2), (3, 8), (5, 6), (7, 4)],
            [(1, 4), (3, 6), (5, 2), (7, 8)],
            [(1, 4), (3, 6), (5, 8), (7, 2)],
            [(1, 4), (3, 8), (5, 6), (7, 2)],
            [(1, 6), (3, 4), (5, 2), (7, 8)],
            [(1, 6), (3, 4), (5, 8), (7, 2)],
            [(1, 6), (3, 8), (5, 2), (7, 4)]]

    for mm in all_matches:
        ans = sorted([(ii[0][1], ii[1][1]) for ii in mm])
        if ans in ref:
            ref.remove(ans)
        print('Match2:', ans)
        g_match = nx.Graph()
        for ii in mm:
            g_match.add_edge(ii[0], ii[1])
        #plotGraph(g_match)

    assert (ref == [])
    print('Example 2 passed')


# Apparently, an AmbiguousSolution
#def test_example1(alg=1):
#    g=nx.Graph()
#    edges=[
#            [(1,0), (0,0)],
#            [(1,0), (0,1)],
#            [(1,0), (0,2)],
#            [(1,1), (0,0)],
#            [(1,2), (0,2)],
#            #[(1,2), (0,5)],
#            [(1,3), (0,2)],
#            #[(1,3), (0,3)],
#            [(1,4), (0,3)],
#            [(1,4), (0,5)],
#            [(1,5), (0,2)],
#            [(1,5), (0,4)],
#            #[(1,5), (0,6)],
#            [(1,6), (0,1)],
#            [(1,6), (0,4)],
#            [(1,6), (0,6)]
#            ]
#
#    for ii in edges:
#        g.add_node(ii[0], bipartite=0)
#        g.add_node(ii[1], bipartite=1)
#        print('  Node:', ii[0], ii[1])
#
#    g.add_edges_from(edges)
#    #plotGraph(g)
#
#    if alg == 1:
#        all_matches = _enumMaximumMatching(g)
#    elif alg == 2:
#        all_matches = _enumMaximumMatching2(g)
#
#    for mm in sorted(all_matches):
#        ans = [(ii[0][1], ii[1][1]) for ii in mm]
#        #print('Match:', mm)
#        print('Match2:', sorted(ans))
#        g_match = nx.Graph()
#        for ii in mm:
#            g_match.add_edge(ii[0], ii[1])
#        #plotGraph(g_match)


# Single-commented actually work
## test_example1(alg=1)
#test_example2(alg=1)
## test_example1(alg=2)
#test_example2(alg=2)
#test_example3(alg=1)
#test_example4(alg=1)
## test_example1(alg=2)
