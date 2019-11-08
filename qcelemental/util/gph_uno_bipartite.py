"""Functions to enumerate all perfect and maximum matchings in bipartite graph.

Implemented following the algorithms in the paper "Algorithms for Enumerating
All Perfect, Maximum and Maximal Matchings in Bipartite Graphs" by Takeaki Uno,
using numpy and networkx modules of python.

NOTICE: optimization needed.

Author: guangzhi XU (xugzhi1987@gmail.com; guangzhi.xu@outlook.com)
Update time: 2017-06-29 14:41:56.

Copied Dec 2017 LAB Adapted from https://github.com/Xunius/bipartite_matching
Updated Dec 2017 LAB for pep8, py3, more tests, starter_match, and simpler interface

"""
import numpy as np

# commented as untested [Apr 2019]
# def _plotGraph(graph):
#    """Plot graph using nodes as position number."""
#    import networkx as nx
#
#    import matplotlib.pyplot as plt
#    fig = plt.figure()
#    ax = fig.add_subplot(111)
#
#    pos = [(ii[1], ii[0]) for ii in graph.nodes()]
#    pos_dict = dict(zip(graph.nodes(), pos))
#    nx.draw(graph, pos=pos_dict, ax=ax, with_labels=True)
#    plt.show(block=False)
#    return


def _formDirected(g, match):
    """Form directed graph D from G and matching M.

    Parameters
    ----------
    g :
        Undirected bipartite graph. Nodes are separated by their
        'bipartite' attribute.
    match :
        List of edges forming a matching of `g`.

    Returns
    -------
    networkx.DiGraph
	    Directed graph, with edges in `match` pointing from set-0
	    (bipartite attribute==0) to set-1 (bipartite attrbiute==1), and
	    the other edges in `g` but not in `match` pointing from set-1 to
	    set-0.

    """
    import networkx as nx

    d = nx.DiGraph()

    for ee in g.edges():
        if ee in match or (ee[1], ee[0]) in match:
            if g.nodes[ee[0]]["bipartite"] == 0:
                d.add_edge(ee[0], ee[1])
            else:
                d.add_edge(ee[1], ee[0])
        else:
            if g.nodes[ee[0]]["bipartite"] == 0:
                d.add_edge(ee[1], ee[0])
            else:
                d.add_edge(ee[0], ee[1])

    return d


def _enumMaximumMatching(g, starter_match=None):
    """Find all maximum matchings in an undirected bipartite graph `g`.

    Parameters
    ----------
    g : networkx.Graph
        Undirected bipartite graph. Nodes are separated by their
        'bipartite' attribute.
    starter_match : dict, optional
        Single perfect match to inaugurate Uno's algorithm.

    Returns
    -------
    list
        Each is a list of edges forming a maximum matching of `g`.

    Author
    ------
    guangzhi XU (xugzhi1987@gmail.com; guangzhi.xu@outlook.com)
    Update time: 2017-05-21 20:04:51.

    """
    import networkx as nx

    all_matches = []

    # ----------------Find one matching M----------------
    if starter_match is None:
        match = nx.bipartite.hopcroft_karp_matching(g)
    else:
        match = starter_match

    # ---------------Re-orient match arcs---------------
    match2 = []
    for kk, vv in match.items():
        if g.nodes[kk]["bipartite"] == 0:
            match2.append((kk, vv))
    match = match2
    all_matches.append(match)

    # -----------------Enter recursion-----------------
    all_matches = _enumMaximumMatchingIter(g, match, all_matches, None)

    return all_matches


def _enumMaximumMatchingIter(g, match, all_matches, add_e=None):
    """Recurively search maximum matchings.

    Parameters
    ----------
    g :
        Undirected bipartite graph. Nodes are separated by their
        'bipartite' attribute.
    match :
        List of edges forming one maximum matching of `g`.
    all_matches :
	    List, each is a list of edges forming a maximum matching of `g`.
	    Newly found matchings will be appended into this list.
    add_e : tuple, optional
        Edge used to form subproblems. If not `None`, will be added to each
        newly found matchings.

    Returns
    -------
    list
        Updated list of all maximum matchings.

    Author
    ------
    guangzhi XU (xugzhi1987@gmail.com; guangzhi.xu@outlook.com)
    Update time: 2017-05-21 20:09:06.

    """
    import networkx as nx

    # ---------------Form directed graph D---------------
    d = _formDirected(g, match)

    # -----------------Find cycles in D-----------------
    cycles = list(nx.simple_cycles(d))

    if len(cycles) == 0:

        # ---------If no cycle, find a feasible path---------
        all_uncovered = set(g.nodes).difference(set([ii[0] for ii in match]))
        all_uncovered = all_uncovered.difference(set([ii[1] for ii in match]))
        all_uncovered = list(all_uncovered)

        # --------------If no path, terminiate--------------
        if len(all_uncovered) == 0:
            return all_matches

        # ----------Find a length 2 feasible path----------
        idx = 0
        uncovered = all_uncovered[idx]
        while True:

            if uncovered not in nx.isolates(g):
                paths = nx.single_source_shortest_path(d, uncovered, cutoff=2)
                len2paths = [vv for kk, vv in paths.items() if len(vv) == 3]

                if len(len2paths) > 0:
                    reversed = False
                    break

                # ----------------Try reversed path----------------
                paths_rev = nx.single_source_shortest_path(d.reverse(), uncovered, cutoff=2)
                len2paths = [vv for kk, vv in paths_rev.items() if len(vv) == 3]

                if len(len2paths) > 0:
                    reversed = True
                    break

            idx += 1
            if idx > len(all_uncovered) - 1:
                return all_matches

            uncovered = all_uncovered[idx]

        # -------------Create a new matching M'-------------
        len2path = len2paths[0]
        if reversed:
            len2path = len2path[::-1]
        len2path = list(zip(len2path[:-1], len2path[1:]))

        new_match = []
        for ee in d.edges():
            if ee in len2path:
                if g.nodes[ee[1]]["bipartite"] == 0:
                    new_match.append((ee[1], ee[0]))
            else:
                if g.nodes[ee[0]]["bipartite"] == 0:
                    new_match.append(ee)

        if add_e is not None:
            for ii in add_e:
                new_match.append(ii)

        all_matches.append(new_match)

        # ---------------------Select e---------------------
        e = set(len2path).difference(set(match))
        e = list(e)[0]

        # -----------------Form subproblems-----------------
        g_plus = g.copy()
        g_minus = g.copy()
        g_plus.remove_node(e[0])
        g_plus.remove_node(e[1])

        g_minus.remove_edge(e[0], e[1])

        add_e_new = [e]
        if add_e is not None:
            add_e_new.extend(add_e)

        all_matches = _enumMaximumMatchingIter(g_minus, match, all_matches, add_e)
        all_matches = _enumMaximumMatchingIter(g_plus, new_match, all_matches, add_e_new)

    else:
        # ----------------Find a cycle in D----------------
        cycle = cycles[0]
        cycle.append(cycle[0])
        cycle = list(zip(cycle[:-1], cycle[1:]))

        # -------------Create a new matching M'-------------
        new_match = []
        for ee in d.edges():
            if ee in cycle:
                if g.nodes[ee[1]]["bipartite"] == 0:
                    new_match.append((ee[1], ee[0]))
            else:
                if g.nodes[ee[0]]["bipartite"] == 0:
                    new_match.append(ee)

        if add_e is not None:
            for ii in add_e:
                new_match.append(ii)

        all_matches.append(new_match)

        # -----------------Choose an edge E-----------------
        e = set(match).intersection(set(cycle))
        e = list(e)[0]

        # -----------------Form subproblems-----------------
        g_plus = g.copy()
        g_minus = g.copy()
        g_plus.remove_node(e[0])
        g_plus.remove_node(e[1])
        g_minus.remove_edge(e[0], e[1])

        add_e_new = [e]
        if add_e is not None:
            add_e_new.extend(add_e)

        all_matches = _enumMaximumMatchingIter(g_minus, new_match, all_matches, add_e)
        all_matches = _enumMaximumMatchingIter(g_plus, match, all_matches, add_e_new)

    return all_matches


def _enumMaximumMatching2(g):
    """Find all maximum matchings in an undirected bipartite graph `g`.
    Similar to _enumMaximumMatching but implemented using adjacency matrix
    of graph for slight speed boost.

    Parameters
    ----------
    g:
        Undirected bipartite graph. Nodes are separated by their
        'bipartite' attribute.

    Returns
    -------
    list
        Each is a list of edges forming a maximum matching of `g`.

    Author
    ------
    guangzhi XU (xugzhi1987@gmail.com; guangzhi.xu@outlook.com)
    Update time: 2017-05-21 20:04:51.

    """
    import networkx as nx
    from scipy import sparse

    s1 = set(n for n, d in g.nodes(data=True) if d["bipartite"] == 0)
    s2 = set(g) - s1
    n1 = len(s1)
    nodes = list(s1) + list(s2)

    adj = nx.adjacency_matrix(g, nodes).tolil()
    all_matches = []

    # ----------------Find one matching----------------
    match = nx.bipartite.hopcroft_karp_matching(g)

    matchadj = np.zeros(adj.shape).astype("int")
    for kk, vv in match.items():
        matchadj[nodes.index(kk), nodes.index(vv)] = 1
    matchadj = sparse.lil_matrix(matchadj)

    all_matches.append(matchadj)

    # -----------------Enter recursion-----------------
    all_matches = _enumMaximumMatchingIter2(adj, matchadj, all_matches, n1, None, True)

    # ---------------Re-orient match arcs---------------
    all_matches2 = []
    for ii in all_matches:
        match_list = sparse.find(ii[:n1] == 1)
        m1 = [nodes[jj] for jj in match_list[0]]
        m2 = [nodes[jj] for jj in match_list[1]]
        match_list = zip(m1, m2)

        all_matches2.append(match_list)

    print("got all")
    return all_matches2


def _enumMaximumMatchingIter2(adj, matchadj, all_matches, n1, add_e=None, check_cycle=True):
    """Recurively search maximum matchings.
    Similar to _enumMaximumMatching but implemented using adjacency matrix
    of graph for a slight speed boost.

    Parameters
    ----------
#    g :
#        Undirected bipartite graph. Nodes are separated by their
#        'bipartite' attribute.
#    match :
#        List of edges forming one maximum matching of `g`.
#    all_matches :
#	    List, each is a list of edges forming a maximum matching of `g`.
#	    Newly found matchings will be appended into this list.
    add_e : tuple, optional
        Edge used to form subproblems. If not `None`, will be added to each
        newly found matchings.

    Returns
    -------
    list
        Updated list of all maximum matchings.

    Author
    ------
    guangzhi XU (xugzhi1987@gmail.com; guangzhi.xu@outlook.com)
    Update time: 2017-05-21 20:09:06.

    """
    import networkx as nx
    from scipy import sparse

    # -------------------Find cycles-------------------
    if check_cycle:
        d = matchadj.multiply(adj)
        d[n1:, :] = adj[n1:, :] - matchadj[n1:, :].multiply(adj[n1:, :])

        dg = nx.from_numpy_matrix(d.toarray(), create_using=nx.DiGraph())
        cycles = list(nx.simple_cycles(dg))
        if len(cycles) == 0:
            check_cycle = False
        else:
            check_cycle = True

    if check_cycle:
        cycle = cycles[0]
        cycle.append(cycle[0])
        cycle = zip(cycle[:-1], cycle[1:])

        # --------------Create a new matching--------------
        new_match = matchadj.copy()
        for ee in cycle:
            if matchadj[ee[0], ee[1]] == 1:
                new_match[ee[0], ee[1]] = 0
                new_match[ee[1], ee[0]] = 0
                e = ee
            else:
                new_match[ee[0], ee[1]] = 1
                new_match[ee[1], ee[0]] = 1

        if add_e is not None:
            for ii in add_e:
                new_match[ii[0], ii[1]] = 1

        all_matches.append(new_match)

        # -----------------Form subproblems-----------------
        g_plus = adj.copy()
        g_minus = adj.copy()
        g_plus[e[0], :] = 0
        g_plus[:, e[1]] = 0
        g_plus[:, e[0]] = 0
        g_plus[e[1], :] = 0
        g_minus[e[0], e[1]] = 0
        g_minus[e[1], e[0]] = 0

        add_e_new = [e]
        if add_e is not None:
            add_e_new.extend(add_e)

        all_matches = _enumMaximumMatchingIter2(g_minus, new_match, all_matches, n1, add_e, check_cycle)
        all_matches = _enumMaximumMatchingIter2(g_plus, matchadj, all_matches, n1, add_e_new, check_cycle)

    else:
        # ---------------Find uncovered nodes---------------
        uncovered = np.where(np.sum(matchadj, axis=1) == 0)[0]

        if len(uncovered) == 0:
            return all_matches

        # ---------------Find feasible paths---------------
        paths = []
        for ii in uncovered:
            aa = adj[ii, :].dot(matchadj)
            if aa.sum() == 0:
                continue
            paths.append((ii, int(sparse.find(aa == 1)[1][0])))
            if len(paths) > 0:
                break

        if len(paths) == 0:
            return all_matches

        # ----------------------Find e----------------------
        feas1, feas2 = paths[0]
        e = (feas1, int(sparse.find(matchadj[:, feas2] == 1)[0]))

        # ----------------Create a new match----------------
        new_match = matchadj.copy()
        new_match[feas2, :] = 0
        new_match[:, feas2] = 0
        new_match[feas1, e[1]] = 1
        new_match[e[1], feas1] = 1

        if add_e is not None:
            for ii in add_e:
                new_match[ii[0], ii[1]] = 1

        all_matches.append(new_match)

        # -----------------Form subproblems-----------------
        g_plus = adj.copy()
        g_minus = adj.copy()
        g_plus[e[0], :] = 0
        g_plus[:, e[1]] = 0
        g_plus[:, e[0]] = 0
        g_plus[e[1], :] = 0
        g_minus[e[0], e[1]] = 0
        g_minus[e[1], e[0]] = 0

        add_e_new = [e]
        if add_e is not None:
            add_e_new.extend(add_e)

        all_matches = _enumMaximumMatchingIter2(g_minus, matchadj, all_matches, n1, add_e, check_cycle)
        all_matches = _enumMaximumMatchingIter2(g_plus, new_match, all_matches, n1, add_e_new, check_cycle)

    # if len(all_matches) % 1000 == 0:
    #    print('len', len(all_matches))

    # print('another')
    return all_matches


# commented as unused [Apr 2019]
# def _findCycle(adj, n1):
#    from scipy import sparse
#
#    path = []
#    visited = set()
#
#    def visit(v):
#        if v in visited:
#            return False
#        visited.add(v)
#        path.append(v)
#        neighbours = sparse.find(adj[v, :] == 1)[1]
#        for nn in neighbours:
#            if nn in path or visit(nn):
#                return True
#        path.remove(v)
#        return False
#
#    nodes = range(n1)
#    result = any(visit(v) for v in nodes)
#    return result, path


def uno(edges, match=None, verbose=1):
    """Perform Uno's algorithm to enumerate all equivalent matchings among
    the bipartite graph defined by `edges`. Optionally given a single
    known `match`.

    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.107.8179&rep=rep1&type=pdf

    "Algorithms for Enumerating All Perfect, Maximum and Maximal Matchings
    in Bipartite Graphs" by Takeaki UNO

    """
    import networkx as nx

    if match is None:
        p_match = None
    else:
        p_match = {(1, m[0]): (0, m[1]) for m in match}
        p_m_inv = {(0, m[1]): (1, m[0]) for m in match}
        p_match.update(p_m_inv)

    p_edges = [[(1, e[0]), (0, e[1])] for e in edges]
    if verbose >= 2:
        print("Edges:")
        for e in p_edges:
            print("\t", e)

    g = nx.Graph()
    for e in p_edges:
        g.add_node(e[0], bipartite=0)
        g.add_node(e[1], bipartite=1)
        if verbose >= 2:
            print("  Node:", e[0], e[1])
    g.add_edges_from(p_edges)

    all_matches = _enumMaximumMatching(g, starter_match=p_match)
    p_all_matches = [sorted([(pt[0][1], pt[1][1]) for pt in am]) for am in all_matches]

    return p_all_matches
