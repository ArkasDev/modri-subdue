import networkx.algorithms.isomorphism as iso

import random
import re
import numpy as np
import scipy as sp
from scipy.spatial import Delaunay
import networkx as nx

from networkx.readwrite import json_graph
import json

import matplotlib.pyplot as plt

import random
from math import ceil, log10, cos, sin, pi
from sklearn.preprocessing import normalize

import os
import time
import subprocess


class GraphMatcherMono(iso.vf2userfunc.GraphMatcher):
    """VF2 isomorphism checker for undirected graphs.
    """

    def __init__(self, G1, G2, node_match=None, edge_match=None):
        iso.vf2userfunc.GraphMatcher.__init__(self, G1, G2, node_match, edge_match)
        self.test = 'mono'


def relabel_graph(H, new_label='predicate'):
    # hops uses key predicate for label names
    for node, data in H.nodes(data=True):
        data['predicate'] = data['label']
    for _, _, data in H.edges(data=True):
        data['predicate'] = data['label']
    return H


def group(lst, n):
    '''
  Groups a list by consecutive n-tuples.
  Does the same as zip(*[lst[i::n] for i in range(n)]) but is more readable.
  '''
    for i in range(0, len(lst), n):
        val = lst[i:i + n]
        if len(val) == n:
            yield tuple(val)


def hops(pattern, data, u=None, vertex_label='label', edge_label='label', init_labels=True):
    '''Convenience method to call HOPS. You may specify the edge and vertex labels that should be considered.
    Currently, both edge and vertex attributes must exist. If you want to compare unlabeled graphs, create a 
    constant label attribute for your edges and/or vertices.
    
    Note that the algorithm expects the networkx vertices in pattern and data to be consecutive integers.
    '''

    if u is None:
        u = 0

    # sample first image of u
    n = len(data.nodes)
    vi = random.randrange(n)
    v = vi

    # check label compatibility of initial vertex
    if pattern.nodes[u][vertex_label] == data.nodes[v][vertex_label]:
        c, phi, phi_inv, traversallist = find_tree_embeddings(u, v, {u: v}, {v: u},
                                                              pattern, data, list(),
                                                              vertex_label=vertex_label,
                                                              edge_label=edge_label)
        c *= n
        return c, phi, phi_inv, traversallist
    else:
        return 0, dict(), dict(), list()


def find_tree_embeddings(u, v, phi, phi_inv, H, G, traversallist, vertex_label, edge_label):
    '''u,v must be integer indices that are used to access nodes in H and G.
    phi and phi inverse give the mapping from H to G and from G to H and should
    be initialized to {u: v} and {v: u} if you call it for a initial node pair.
    See the convenience method hops().
    traversallist should be initialized to the empty list and gives you information 
    on the iterations of the method as dicts.'''

    U_n = list()
    V_n = list()
    for u_neigh in H.neighbors(u):
        if u_neigh not in phi.keys():
            H.nodes[u_neigh]['hops_predicate'] = (
                H.nodes[u_neigh][vertex_label], H.get_edge_data(u, u_neigh)[edge_label])
            U_n.append(u_neigh)
    for v_neigh in G.neighbors(v):
        if v_neigh not in phi_inv.keys():
            G.nodes[v_neigh]['hops_predicate'] = (
                G.nodes[v_neigh][vertex_label], G.get_edge_data(v, v_neigh)[edge_label])
            V_n.append(v_neigh)

    # visualization data
    viz = dict()
    viz['u'] = u
    viz['v'] = v
    viz['U_n'] = U_n
    viz['V_n'] = V_n
    viz['ext'] = list()
    traversallist.append(viz)

    M, c = uniformRandomMaximumMatching(U_n, V_n, H, G)
    if len(M) == len(U_n):
        # add matching to phi
        for x in M.keys():
            y = M[x]
            phi[x] = y
            phi_inv[y] = x
            viz['ext'].append((v, y))

        viz['phi'] = phi.copy()
        viz['phi_inv'] = phi_inv.copy()

        # recurse
        for x in M.keys():
            c_rec, phi, phi_inv, traversallist = find_tree_embeddings(x, M[x], phi, phi_inv, H, G, traversallist,
                                                                      vertex_label, edge_label)
            c *= c_rec
            if c == 0:
                break
    else:
        c = 0

    return c, phi, phi_inv, traversallist


def n_max_matchings(A, B):
    """
    Compute the number of maximum matchings in a complete bipartite graph on A + B vertices.
    A and B are required to be nonnegative.
    Corner Case: If at least one of the sides has zero vertices, there is one maximal matching: the empty set.
    """
    a = min(A, B)
    b = max(A, B)
    c = 1

    if a != 0:
        for i in range(b - a + 1, b + 1):
            c *= i

    return c


def uniformRandomMaximumMatching(N_u, N_v, H, G):
    """
    Draw a maximum matching from a block disjoint bipartite graph uniformly at random and return it and
    the number of such matchings.

    Which vertex x can be assigned to which vertex y is given by x['predicate'] == y['predicate']

    :param N_u: list of vertices from H that must be assigned
    :param N_v: list of vertices from G that can be assigned to
    :return: M, c : a matching M, given as a map and the number of all maximum matchings c
    """

    hu = dict()
    hv = dict()
    c = 1

    # create blocks of identical symbols
    for x in N_u:
        try:
            hu[H.nodes[x]['hops_predicate']].append(x)
        except KeyError:
            hu[H.nodes[x]['hops_predicate']] = [x]

    for y in N_v:
        try:
            hv[G.nodes[y]['hops_predicate']].append(y)
        except KeyError:
            hv[G.nodes[y]['hops_predicate']] = [y]

    # shuffle target list
    for y in hv.keys():
        random.shuffle(hv[y])

    # compute uniform random maximal matching
    matching = dict()
    for x in hu.keys():
        try:
            for i, j in zip(hu[x], hv[x]):
                matching[i] = j
            c *= n_max_matchings(len(hu[x]), len(hv[x]))
        except KeyError:
            pass
    return matching, c


# TODO could use here theoretically a exact subtree isomorphism matcher since this problem is tractable
# TODO there is no qurantee that the graphs get the same integer nodes (but should not be a big problem, since we use additional labels)
def is_subtree(H, G, max_retries=5):
    # hops works with integer nodes
    H = nx.convert_node_labels_to_integers(H, first_label=0)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    c = 0
    retries = 0
    while c == 0:
        c, phi, phi_i, viz = hops(H, G)
        if retries >= max_retries:
            break;
        retries = retries + 1
    return c != 0, phi


def is_subtree_db(H, graph_db):
    match = next((G for G in graph_db if is_subtree(H, G)[0]), None)
    return match is not None


# Using networkx for subgraph isomorphism check (induced sg), VF2 algorithm
# note: This checks for induced subgraph isomorphism!
def is_subgraph(G1, G2, label_name='label'):
    nm = iso.categorical_node_match(label_name, "")
    em = iso.categorical_edge_match(label_name, "")
    GM = iso.GraphMatcher(G2, G1, node_match=nm, edge_match=em)
    return GM.subgraph_is_isomorphic(), GM.mapping


def is_subgraph_mono(G1, G2, label_name='label'):
    nm = iso.categorical_node_match(label_name, "")
    em = iso.categorical_edge_match(label_name, "")
    GM = GraphMatcherMono(G2, G1, node_match=nm, edge_match=em)
    return GM.subgraph_is_monomorphic()


def is_subgraph_mono_mapping(G1, G2, label_name='label'):
    nm = iso.categorical_node_match(label_name, "")
    em = iso.categorical_edge_match(label_name, "")
    GM = GraphMatcherMono(G2, G1, node_match=nm, edge_match=em)
    return GM.subgraph_is_monomorphic(), GM.mapping


def list_difference(l1: list, l2: list):
    '''Computes the difference of two lists by removing as many equal objects as possible and returning the sum of all remaining'''
    # Since we operate on the list, we make a copy first
    # it is most efficient to iterate over the small list
    if (len(l1) > len(l2)):
        _l1 = list(l2)
        _l2 = list(l1)
    else:
        _l1 = list(l1)
        _l2 = list(l2)
    to_be_deleted = []
    for element in _l1:
        if element in _l2:
            to_be_deleted.append(element)
            _l2.remove(element)
    for element in to_be_deleted:
        _l1.remove(element)
    return _l1 + _l2


# todo weighted difference by frequency of total/pattern wide node occurence (?)
def node_label_distance(g1, g2, distinct=False, key_name='label'):
    ''' returns a difference between 0 and 1 for labels of the graphs '''
    if not distinct:
        g1_labels = [d[key_name] for v, d in g1.nodes(data=True)]
        g2_labels = [d[key_name] for v, d in g2.nodes(data=True)]
        return len(list_difference(g1_labels, g2_labels)) / float((len(g1_labels) + len(g2_labels)))
    else:
        g1_labels = set()
        g2_labels = set()
        for _, d in g1.nodes(data=True):
            g1_labels.add(d[key_name])
        for _, d in g2.nodes(data=True):
            g2_labels.add(d[key_name])
        return len(g1_labels.symmetric_difference(g2_labels)) / float(len(g1_labels + g2_labels))


# approximate most distant sampling. 
# Exact solution could for example be done by using a CSP solver. The constraints are given by trying to sample sample_size samples and iteratively removing the smallest "pairs".
# Brute force exact solution would be to consider all possible choice of sample_size elements and compute their minimal distance. But we will have n choose sample_size choices...
# Note that our algorithm does not only maximize the minimal distance but also often to maximies the other distances.
# Another approximate solution that is often mentioned is to add the most distant points iteratively. But this won't give good solutions in many cases, e.g. the circle point set with 3 samples.
# TODO our algorithm might (in theory) get stuck in local maxima (e.g., orthic triangle of a isosceles triangle), maybe consider random restarts and the best of these randoms
def most_distant_sampling(element_list, sample_size, num_of_iterations=None, distance_function=node_label_distance):
    ''' Approximate algorithm to find the sample_size most distant elements (i.e. the minimal distance is maximal) in the given list of elements.
      We randomly choose sample_size nodes and then randomly select one of the nodes and maximize the minimal distance. 
      '''
    # Compute number of iterations
    if num_of_iterations is None:
        num_of_iterations = int(sample_size * 1.2)

    if element_list is None or len(element_list) == 0:
        return None

    if len(element_list) == 1:
        return element_list[0]

    # Array to ensure that all tokens are touched
    coupons = np.arange(0, sample_size)

    # Choose some initial random sample from the list of elements
    most_distant = random.sample(element_list, sample_size)

    # choose random pivot and remove it from the list from the most_distant list, sicne we want to maximize the minimal distance to all other elements
    pivot_index = random.choice(coupons)
    np.delete(coupons, pivot_index)

    pivot = most_distant[pivot_index]

    candidates = list(list_difference(most_distant, element_list))
    # append the pivot
    candidates.append(pivot)
    candidate_distances = np.array(
        [[distance_function(candidate, selected) for selected in most_distant] for candidate in candidates])

    for _ in range(num_of_iterations):
        most_distant_temp = list(most_distant)
        most_distant_temp.pop(pivot_index)
        candidate_distances_temp = np.copy(candidate_distances)
        candidate_distances_temp = np.delete(candidate_distances_temp, [pivot_index], 1)

        best_candidate_index = np.argmax(np.apply_along_axis(np.min, 1, candidate_distances_temp))
        best_candidate = candidates[best_candidate_index]

        most_distant[pivot_index] = best_candidate
        candidate_distances[:, pivot_index] = np.array(
            [distance_function(best_candidate, candidate) for candidate in candidates])

        # choose new pivot and continue
        # If coupons are empty, refill
        if coupons.size == 0:
            coupons = np.arange(0, sample_size)
        pivot_index = random.choice(coupons)
        np.delete(coupons, pivot_index)
        candidates[best_candidate_index] = pivot
        candidate_distances[best_candidate_index] = np.array(
            [distance_function(selected, pivot) for selected in most_distant])
    return most_distant


# check two graphs for isomorphism
def is_label_isomorphic(G, H, label_name="label"):
    nm = iso.categorical_node_match(label_name, "")
    em = iso.categorical_edge_match(label_name, "")
    return nx.is_isomorphic(G, H, node_match=nm, edge_match=em)


def find_induced_subgraph_exact(H, G, max_retries=5, label_name='label'):
    found_pattern, mapping = is_subgraph(H, G, label_name=label_name)
    if found_pattern:
        subgraph = G.subgraph(mapping.keys()).copy()
        return True, subgraph, G.degree(mapping.keys()), subgraph.degree(mapping.keys())
    return False, None, None, None


def find_induced_subgraph_hops(H, G, max_retries=5, label_name='label'):
    # hops works with integer nodes
    # TODO !!!!!!!!!!!!!!!!!!!!we must ensure here a consistent labeling!!!!!!!!!!!!!!!!
    H = nx.convert_node_labels_to_integers(H, first_label=0)
    G = nx.convert_node_labels_to_integers(G, first_label=0)

    c = 0
    retries = 0
    while c == 0:
        c, phi, phi_i, viz = hops(H, G, vertex_label=label_name, edge_label=label_name)
        if retries >= max_retries:
            break
        retries = retries + 1
    if c != 0:
        subgraph = G.subgraph(phi_i.keys()).copy()
        return True, subgraph, G.degree(phi_i.keys()), subgraph.degree(phi_i.keys())
    return False, None, None, None


def find_induced_subgraphs_in_db(H, graph_db, max_retries=5, label_name='label', check_degree=False,
                                 max_degree_diff=2, embedding_algorithm=find_induced_subgraph_hops):
    # a dict, where keys are graphs and values are the number of instances
    subgraphs = {}
    for G in graph_db:
        match, subgraph, instance_degrees, subgraph_degrees = embedding_algorithm(H, G, max_retries,
                                                                                  label_name=label_name)
        if match:
            # TODO This is a cohesion assumption, which needs to be more investigation. E.g., for "central nodes" (like packages, or components,..) this assumption is certainly not true
            # If there are nodes which have a smaller degree (determined by the max_degree_diff parameter)
            # inside the subgraph than inside the original graph, the graph is rejected
            if check_degree:
                instance_degrees = list(instance_degrees)
                subgraph_degrees = list(subgraph_degrees)
                weakly_coupled = False
                for i in range(len(subgraph_degrees)):
                    # "2 * " because we count inside and outside
                    if instance_degrees[i][1] > 2 * subgraph_degrees[i][1] + max_degree_diff:
                        weakly_coupled = True
                        break
                if weakly_coupled:
                    # go to next subgraph TODO actualy we could continue here to look for another instance of the tree
                    break

            found = False
            for sg in subgraphs.keys():
                if is_label_isomorphic(subgraph, sg, label_name):
                    subgraphs[sg] += 1
                    found = True
                    break
            if not found:
                subgraphs[subgraph] = 1
    return subgraphs


def get_induced_sg_for_trees(tree_list, graph_db, min_frequency, retries_induced_subgraph=5, label_name='label',
                             prune=True, embedding_algorithm=find_induced_subgraph_hops, induced_subgraphs={}):
    '''
  Computes the induced subgraphs for the given trees in the given graph database. Only when the induced subgraph has frequency > min_frequency, the subgraph is returned.
  TODO we could add a further heuristic pruning like for example subtree pruning (e.g., something like if bigger tree has some frequency, skip small tree) (but need to think more about this in order to not risk recall)
  TODO another pruning would be to remember trees that have been pruned since there induced subgraphs are not frequent. Then also trees that contain these trees can not have frequent induced subgraphs.
  TODO another heuristic would be the degree heuristic. If the induced subgraph has nodes where the internal degree is less than the external one, the node most propably belongs to another operation or the subgraph is not yet "complete".
  :return a dictionary with keys = subgraphs and value = maximum frequency that has been found (note that this is only approximate)
  '''
    # a dict of subgraphs (keys) and there frequency (value)
    subgraphs = induced_subgraphs
    for tree in tree_list:
        new_subgraphs = find_induced_subgraphs_in_db(tree, graph_db, max_retries=retries_induced_subgraph,
                                                     label_name=label_name, embedding_algorithm=embedding_algorithm)
        for new_subgraph, new_frequency in new_subgraphs.items():
            # prune if freq < min_frequency
            if prune and (new_frequency < min_frequency):
                continue
            # Else check if the subgraph has already been listed
            already_there = False
            for existing_subgraph in subgraphs.keys():
                if is_label_isomorphic(new_subgraph, existing_subgraph, label_name):
                    already_there = True
                    # if more subgraphs have been found via the tree, use maximum (this could happen since hops only works in an approximate way)
                    subgraphs[existing_subgraph] = max(subgraphs[existing_subgraph], new_frequency)
                    break
            if not already_there:
                subgraphs[new_subgraph] = new_frequency
    # print("Found " + str(len(subgraphs.keys())) + " frequent trees.")
    return subgraphs


def most_frequent_induced_subgraphs_compression_based(selected_trees, graph_db, min_frequency, min_return,
                                                      retries_induced_subgraph=5, use_down_sampling=False,
                                                      down_sampling_size=100,
                                                      embedding_algorithm=find_induced_subgraph_hops):
    '''
    Finds the most frequent, largest, induced subgraphs of the selected_trees in the given graph_db. 

    :param selected_trees: a dictionary with keys equal to the frequency of tree and value equal to a dict with keys equals to size (in number of nodes) of the trees and value a list of trees
    :param n_max: the maximum number of trees (not induced subgraphs!), which should be sampled
    :param down_sampling_size: the size of the sample of trees to used for further analysis. Downsampling is only applied to a batch of trees if the size of the batch is greather than 10-times down_sampling_size
    :return: induced_subgraphs : a dictionary with keys equal to the induced subgraph and value equal to its approx. frequency.
  '''
    induced_subgraphs = {}

    # sort trees for compression
    trees_with_compression = {}
    for freq in selected_trees.keys():
        for size in selected_trees[freq].keys():
            for tree in selected_trees[freq][size]:
                trees_with_compression[tree] = (freq - 1) * size

    trees_with_compression = {k: v for k, v in
                              sorted(trees_with_compression.items(), key=lambda item: item[1], reverse=True)}

    # TODO we can somehow do some (down-)sampling here as well

    for tree in trees_with_compression.keys():
        if len(induced_subgraphs.keys()) >= min_return:
            return induced_subgraphs
        # Just some logging every 20 induced subgraphs...
        if (len(induced_subgraphs.keys()) % 20 == 0):
            print("Current compression: " + str(trees_with_compression[tree]))
            print("Found " + str(len(induced_subgraphs.keys())) + " subgraphs.")
        # update the induced subgraphs dictionary with the maximum frequency
        for graph, frequency in get_induced_sg_for_trees([tree], graph_db, min_frequency,
                                                         retries_induced_subgraph=retries_induced_subgraph,
                                                         induced_subgraphs=induced_subgraphs,
                                                         embedding_algorithm=embedding_algorithm).items():
            if graph in induced_subgraphs.keys():
                induced_subgraphs[graph] = max(frequency, induced_subgraphs[graph])
            else:
                induced_subgraphs[graph] = frequency

    return induced_subgraphs


def most_frequent_induced_subgraphs(selected_trees, graph_db, min_frequency, min_return, retries_induced_subgraph=5,
                                    use_down_sampling=False, down_sampling_size=100,
                                    embedding_algorithm=find_induced_subgraph_hops):
    '''
    Finds the most frequent, largest, induced subgraphs of the selected_trees in the given graph_db. Iterates over "batches" of trees that are grouped by their size (number of nodes)
    and frequency.

    :param selected_trees: a dictionary with keys equal to the frequency of tree and value equal to a dict with keys equals to size (in number of nodes) of the trees and value a list of trees
    :param n_max: the maximum number of trees (not induced subgraphs!), which should be sampled
    :param down_sampling_size: the size of the sample of trees to used for further analysis. Downsampling is only applied to a batch of trees if the size of the batch is greather than 10-times down_sampling_size
    :return: induced_subgraphs : a dictionary with keys equal to the induced subgraph and value equal to its approx. frequency.
  '''
    induced_subgraphs = {}
    # check pareto optimal trees (objectives= size, frequency), iterate over the fronts until enough = max_return graphs have been found

    while len(induced_subgraphs.keys()) < min_return and selected_trees:
        frequencies = selected_trees.keys()
        max_size_prev = -1
        for freq in sorted(list(frequencies), reverse=True):
            # continue if enough graphs have been found
            if len(induced_subgraphs.keys()) >= min_return:
                return induced_subgraphs

            print("Current frequency: " + str(freq))
            # if no trees are available for frequency or frequency to small, remove from dict and continue
            if len(selected_trees[freq].keys()) == 0 or freq < min_frequency:
                selected_trees.pop(freq, None)
                continue

            # the largest ones are only pareto optimal, if for the previous frequency, the maximal size was less
            max_size = max(list(selected_trees[freq].keys()))
            # TODO actually for the threshold size (the max_size of the trees), we should have <= instead of <
            if max_size < max_size_prev:
                break

            max_size_prev = max_size
            trees_to_find_embedding = selected_trees[freq][max_size]
            number_of_trees = len(trees_to_find_embedding)
            print("Looking for induced subgraphs for " + str(number_of_trees) + " trees of size " + str(max_size) + ".")
            if use_down_sampling and number_of_trees > down_sampling_size * 10:
                trees_to_find_embedding = most_distant_sampling(trees_to_find_embedding, down_sampling_size,
                                                                num_of_iterations=down_sampling_size,
                                                                distance_function=node_label_distance)

            # update the induced subgraphs dictionary with the maximum frequency
            for graph, frequency in get_induced_sg_for_trees(trees_to_find_embedding, graph_db, min_frequency,
                                                             retries_induced_subgraph=retries_induced_subgraph,
                                                             induced_subgraphs=induced_subgraphs,
                                                             embedding_algorithm=embedding_algorithm).items():
                if graph in induced_subgraphs.keys():
                    induced_subgraphs[graph] = max(frequency, induced_subgraphs[graph])
                else:
                    induced_subgraphs[graph] = frequency

            # print("Finding induced graphs took " + str(end - start) + " secs.")

            # Remove
            selected_trees[freq].pop(max_size, None)
    return induced_subgraphs
