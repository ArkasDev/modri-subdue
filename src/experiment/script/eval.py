import csv
import pickle
import re
import sys
import os
import time
import functools
import matplotlib.pyplot as plt
import networkx as nx
from experiment.script.algos import most_frequent_induced_subgraphs_compression_based, most_frequent_induced_subgraphs, \
    find_induced_subgraph_hops, is_subgraph, is_subgraph_mono, is_label_isomorphic
from experiment.script.compute_components import load_components_networkx
import experiment.script.converter as converter
from termcolor import colored

data_set_path = None
experiment_path = None
print_results_bool = None


def main(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10):
    # parameters
    global data_set_path
    global experiment_path
    global print_results_bool
    data_set_path = arg1
    threshold = int(arg2)
    min_freq = threshold
    hops_i = 200
    max_n = int(arg3)
    elapsed_time = float(arg4)
    heap_size = arg9
    is_simulation = arg5
    is_evaluation = arg6
    print_results_bool = arg7
    experiment_path = arg8
    algorithm = arg10

    print(colored("Evaluation Settings:", 'yellow'))
    print(colored("set_name: " + str(data_set_path), 'yellow'))
    print(colored("threshold: " + str(threshold), 'yellow'))
    print(colored("max_n: " + str(max_n), 'yellow'))
    print(colored("elapsed_time: " + str(elapsed_time), 'yellow'))
    print(colored("heap_size: " + str(heap_size), 'yellow'))
    print(colored("is_simulation: " + str(is_simulation), 'yellow'))
    print(colored("is_evaluation: " + str(is_evaluation), 'yellow'))
    print(colored("print_results: " + str(print_results_bool), 'yellow'))
    print(colored("experiment_path: " + str(experiment_path), 'yellow'))

    # cut off slash
    if data_set_path.endswith('/'):
        data_set_path = data_set_path[:-1]

    # For a simulation, we have some parameters that we can read out of the set_names
    if is_simulation:
        # Parse experiment params
        regex = r".*\D(\d+)_eo(\d+)_p(\d,\d)"
        match = re.match(regex, data_set_path)
        nb_diffs = int(match.group(1))
        nb_eos = int(match.group(2))
        pertubation = float(match.group(3).replace(",", "."))

    ####################################### SCRIPT START ##########################################################################
    # Read components
    # TODO load components from the final component output, and handle the counting somehow differently
    components, nb_of_components_per_diff = load_components_networkx(data_set_path + '/diffgraphs')
    nb_components = len(components)
    print("{} components in total.", nb_components)

    sorted_recommendation_pruned = None
    sorted_recommendation_pruned_f = None

    if (algorithm == "gaston") or (algorithm == "gspan"):
        # Import the frequent trees dict with key=freq and value = dict with key=size and value = list of trees with freq and size
        print("Loading graphs from file...")
        graphs = import_tlv(data_set_path + "/fsg.output")

        print("Sorting for compression...")
        # sort for compression (first freq then compression)
        graphs_compression = {k: v for k, v in sorted(graphs.items(), key=lambda item: item[1], reverse=True)}
        graphs_compression = {k: (v - 1) * (len(k.nodes()) + len(k.edges())) for k, v in
                              sorted(graphs_compression.items(),
                                     key=lambda item: (item[1] - 1) * (len(item[0].nodes()) + len(item[0].edges())),
                                     reverse=True)}

        print("Sorting for frequency...")
        # sort for size and frequency (first compression then frequency)
        graphs_frequency = {k: v for k, v in
                            sorted(graphs.items(), key=lambda item: len(item[0].nodes()) + len(item[0].edges()),
                                   reverse=True)}
        graphs_frequency = {k: v for k, v in sorted(graphs_frequency.items(), key=lambda item: item[1], reverse=True)}

        # compression based
        print("Eval compression based...")
        sg_lattice = create_subgraph_lattice(graphs_compression)
        sorted_recommendation_pruned, lattice_pruned = lattice_pruned_list_sorted(sg_lattice, best_compression,
                                                                                  compression_key)

        # frequency based
        print("Eval frequency based...")
        sg_lattice_f = create_subgraph_lattice(graphs_frequency)
        sorted_recommendation_pruned_f, lattice_pruned_f = lattice_pruned_list_sorted(sg_lattice_f, best_frequency,
                                                                                      frequency_key)

        ################################## PRINT GRAPHS ############################################
        # print as dictionary parent with children
        print_results(lattice_pruned, sg_lattice, 10, lambda element: compression_key(sg_lattice, element),
                      10, label="compression", export_pickle=True)
        print_results(lattice_pruned_f, sg_lattice, 10, lambda element: frequency_key(sg_lattice, element),
                      10, label="frequency", export_pickle=True)

    else:
        print("Skip compression and frequency computation for subdue")

            # print as list
            # print_results_list(sorted_recommendation_pruned, 15, label="compression")
            # print_results_list(sorted_recommendation_pruned_f, 15, label="frequency")

    ################################## EVALUATION ############################################
    if is_evaluation:
        # Load and plot the correct graph
        correct_graph_1 = pickle.load(open(experiment_path + "/correct_graph_networkx.p", "rb"))
        correct_graph_2 = pickle.load(open(experiment_path + "./correct_graph_2_networkx.p", "rb"))

        if correct_graph_1 is None or correct_graph_2 is None:
            print(colored("Error: correct graph could not be loaded", "red"))

        def evaluate_candidates(output_file, candidates, label):
            score_1 = get_position_sorted_list(correct_graph_1, candidates)
            score_2 = get_position_sorted_list(correct_graph_2, candidates)
            # position = get_position(correct_graph, candidates, key)
            # score = position[0]*(position[1]+1)
            # print_results_list(candidates, 5, label)

            # number_of_labels = average([len(set([node[1] for node in component.nodes.data('label')])) for component in components])
            nodes_vs_edges = [(len(component.nodes()), len(component.edges())) for component in components]
            number_of_nodes_per_component = average([node_edges[0] for node_edges in nodes_vs_edges])
            number_of_edges_per_component = average([node_edges[1] for node_edges in nodes_vs_edges])
            degree_per_component = average([2 * node_edges[1] / node_edges[0] for node_edges in nodes_vs_edges])
            avg_nb_of_components_per_diff = average(nb_of_components_per_diff)
            # if we want to prune, we need to know look at all graphs but threshold - 1, if we want to avoid looking into huge graphs, what is the smallest size of graph we have to consider?
            components_size_desc = sorted(components, key=lambda component: len(component.nodes()), reverse=True)
            size_at_threshold = len(components_size_desc[threshold - 1].nodes())
            cnt_exact_match_1 = sum([is_label_isomorphic(correct_graph_1, comp, "label") for comp in components])
            cnt_exact_match_2 = sum([is_label_isomorphic(correct_graph_2, comp, "label") for comp in components])

            with open(output_file, 'a') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                writer.writerow(
                    [nb_diffs, nb_eos, pertubation, str(number_of_nodes_per_component),
                     str(number_of_edges_per_component),
                     str(degree_per_component), str(avg_nb_of_components_per_diff), str(nb_components), str(threshold),
                     str(size_at_threshold), str(cnt_exact_match_1), str(cnt_exact_match_2), str(elapsed_time), str(heap_size), score_1,
                     score_2])

        if (algorithm == "gaston") or (algorithm == "gspan"):
            evaluate_candidates(experiment_path + '/stats_topn.csv', sorted_recommendation_pruned, "comp")
            evaluate_candidates(experiment_path + '/stats_topn_frequency.csv', sorted_recommendation_pruned_f, "freq")
        elif algorithm == "subdue_python":
            # convert subdue best pattern to nx graph
            # with open(experiment_path + "/" + set_name + "/threshold.txt", 'r') as threshold_file:
            #     threshold = threshold_file.read()
            # graphs = converter.create_nx_graph_for_subdue_python_output()
            evaluate_candidates(experiment_path + '/stats_topn.csv', sorted_recommendation_pruned, "comp")


# Plot graphs
def plot_graphs(S, file_path, labels=True):
    for i in range(len(S)):
        plt.clf()
        plt.figure(i)
        plt.margins(0.15, 0.15)
        pos = nx.spring_layout(S[i], scale=10)

        if labels:
            nx.draw(S[i], pos, node_size=1500)
            node_labels = dict([(v, d['label']) for v, d in S[i].nodes(data=True)])
            y_off = 0.02
            nx.draw_networkx_labels(S[i], pos={k: ([v[0], v[1] + y_off]) for k, v in pos.items()}, font_size=8,
                                    labels=node_labels)
            # nx.draw_networkx_edge_labels(S[i], pos)
        else:
            nx.draw(S[i], pos, node_size=30)

        if len(S) > 1:
            save_path = file_path + "_" + str(i) + ".png"
        else:
            save_path = file_path + ".png"

        # Save
        plt.savefig(save_path, format="PNG")


# eval script
def stats_to_csv(components, nb_of_components_per_diff):
    number_of_labels = [len(set([node[1] for node in component.nodes.data('label')])) for component in components]
    nodes_vs_edges = [(len(component.nodes()), len(component.edges())) for component in components]
    number_of_nodes_per_component = [node_edges[0] for node_edges in nodes_vs_edges]
    number_of_edges_per_component = [node_edges[1] for node_edges in nodes_vs_edges]
    degree_per_component = [2 * node_edges[1] / node_edges[0] for node_edges in nodes_vs_edges]
    timing = []

    with open(experiment_path + '/stats_' + data_set_path + '.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(nb_of_components_per_diff)
        writer.writerow(number_of_labels)
        writer.writerow(nodes_vs_edges)
        writer.writerow(number_of_nodes_per_component)
        writer.writerow(number_of_edges_per_component)
        writer.writerow(degree_per_component)


# Import the trees (output of lwg are trees in CString, but we will import here the trees in AIDS)
def import_tlv(path):
    graph_db = open(path, 'r')
    next_line = graph_db.readline()
    graphs = {}
    regex_header = r"t # \d+.*"
    regex_node = r"v (\d+) (.+).*"
    regex_edge = r"e (\d+) (\d+) (.+).*"
    regex_embedding = r"#=> (\d+) .*"
    # if tlv header continue parsing
    if re.match(regex_header, next_line):
        next_line = graph_db.readline()
    else:
        print("Error parsing graph db. Expecting TLV.")
        return {}

    while next_line:
        graph = nx.Graph()
        support_set = set()
        while next_line and not re.match(regex_header, next_line):
            match_node = re.match(regex_node, next_line)
            match_edge = re.match(regex_edge, next_line)
            match_embedding = re.match(regex_embedding, next_line)
            if match_node:
                graph.add_node(int(match_node.group(1)), label=str(match_node.group(2)))
            elif match_edge:
                graph.add_edge(int(match_edge.group(1)), int(match_edge.group(2)), label=str(match_edge.group(3)))
            elif match_embedding:
                support_set.add(int(match_embedding.group(1)))
            next_line = graph_db.readline()
        graphs[graph] = len(support_set)
        next_line = graph_db.readline()
    return graphs


# Create a subgraph lattice for the frequent induced subgraphs
def create_subgraph_lattice(frequent_induced_graphs):
    start = time.time()
    # sort according to graph size (node count)
    induced_sgs = {k: v for k, v in
                   sorted(frequent_induced_graphs.items(), key=lambda item: len(item[0].nodes()), reverse=True)}
    # used to store the graphs, their frequency and their direct (i.e., #nodes - 1) subgraphs
    # {key: graph, value: [compression, frequency, list of direct subgraphs]}
    graph_lattice = {}
    # initialize the current size, i.e., the size of the first graph
    current_size = len(next(iter(induced_sgs.keys())).nodes())
    # TODO by connecting only consecutive graphs, we could omit a chain where one subgraph is missing (which could happen in the approximate mining case)
    current_level_graphs = []
    previous_level_graphs = []
    for key, value in induced_sgs.items():
        number_of_nodes = len(key.nodes())
        # determine if next level has been reached
        if number_of_nodes < current_size:
            previous_level_graphs = current_level_graphs.copy()
            current_level_graphs = []
            current_size = number_of_nodes
        # Check for duplicates
        is_duplicate = False
        for graph in current_level_graphs:
            if is_label_isomorphic(key, graph):
                is_duplicate = True
                break
        if is_duplicate:
            continue
        for candidate_supergraph in previous_level_graphs:
            if is_subgraph_mono(key, candidate_supergraph):
                # add lattice link, item 2 is the list of children
                graph_lattice[candidate_supergraph][2].append(key)
        # value = [compression_factor, frequency, children] note that the children will be determined in the next level
        graph_lattice[key] = [(value - 1) * (number_of_nodes + len(key.edges())), value, []]
        # check if there is a supergraph or a subgraph on the current level (= node count)
        for graph in current_level_graphs:
            if is_subgraph_mono(key, graph):
                graph_lattice[graph][2].append(key)
            if is_subgraph_mono(graph, key):
                graph_lattice[key][2].append(graph)
        current_level_graphs.append(key)
    end = time.time()
    print("Creating lattice took " + str(end - start) + " seconds")
    return graph_lattice


# prune lattice
# find some better way to make this pruning more adaptable in the future
def prune_lattice(lattice, graph, level=0):
    # good_children are children which have a higher frequency than their parents (other definitions possible)
    good_children = []
    if graph in lattice.keys():
        children = lattice[graph][2]
        for child in (set(children) & set(lattice.keys())):
            # child could already be pruned
            if child in lattice.keys():
                # index 1 is the frequency
                if lattice[child][1] > lattice[graph][1]:
                    good_children.append(child)
                good_children = good_children + prune_lattice(lattice, child, level=level + 1)
        if level > 0:
            lattice.pop(graph, None)
    return good_children


def best_pruned_using_sorting(lattice, sorting_lambda, reverse=True):
    # sort for sorting_lambda
    lattice = {k: v for k, v in sorted(lattice.items(), key=sorting_lambda, reverse=reverse)}
    lattice_copy = lattice.copy()
    print("Before: " + str(len(lattice_copy.keys())))
    pruned = {}
    for key in list(lattice_copy.keys()):
        if key in lattice_copy.keys():
            pruned[key] = prune_lattice(lattice_copy, key)
    print("After: " + str(len(pruned.keys())))
    return pruned


def best_compression(lattice):
    # sort for compression (item[1][0] is the compression)
    return best_pruned_using_sorting(lattice, lambda item: item[1][0], reverse=True)


def best_frequency(lattice):
    # sort for frequency (item[1][1] is the frequency)
    return best_pruned_using_sorting(lattice, lambda item: item[1][1], reverse=True)


def print_single(lattice, graph, label, label_draw, export_pickle=False):
    if print_results_bool:
        print("Frequency: " + str(lattice[graph][1]))
        print("Compression: " + str(lattice[graph][0]))
    file_path = data_set_path + '/results/' + label
    file_path_drawing = data_set_path + '/results/' + label_draw
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plot_graphs([graph], file_path_drawing)
    if export_pickle:
        pickle.dump(graph, open(file_path + ".p", "wb"))


def print_results(pruned_lattice, original_lattice, top_k, good_children_sorting, max_good_children,
                  label="compression", export_pickle=False):
    position = 1
    # for key, value in list(islice(pruned_lattice.items(), top_k)):
    for key, value in pruned_lattice.items():
        if position > top_k:
            break
        if print_results_bool:
            print("-----------LEADING GRAPH------------------")
            print_single(original_lattice, key, label + "/" + str(position) + ":0", label + "/" + str(position) + "_0", export_pickle=export_pickle)
            print("-----------Good children:----------------")
        # get the "good children" and sort them
        value.sort(key=good_children_sorting, reverse=True)
        child_position = 1
        for child in value[:max_good_children]:
            print_single(original_lattice, child, label + "/" + str(position) + ":" + str(child_position), label + "/" + str(position) + "_" + str(child_position),
                         export_pickle=export_pickle)
            child_position += 1
        position += 1


def print_results_list(result_list, top_k, label_prefix):
    counter = 0
    for graph in result_list:
        # print("score: " + str(value))
        plot_graphs([graph], "./" + data_set_path + '/results/' + label_prefix + '_' + str(counter))
        counter = counter + 1
        if counter >= top_k:
            return


# Get the position of the graph in the lattice
def get_position(graph, lattice, good_children_sorting):
    position = 1
    for key, value in lattice.items():
        children = value
        if is_label_isomorphic(graph, key, "label"):
            return (position, 0)
        else:
            children.sort(key=good_children_sorting, reverse=True)
        child_position = 1
        for child in children:
            if is_label_isomorphic(graph, child, "label"):
                return (position, child_position)
            child_position = child_position + 1
        position = position + 1
    return (-1, 0)


# Get the position of the correct in the total list of graphs
def get_position_sorted_list(correct, sorted_list):
    if correct is None:
        print(colored("Error: correct graph is not set", "red"))
        return

    if sorted_list is None:
        print(colored("Error: sorted list of graphs mined by subgraph mining is not set", "red"))
        return

    position = 1
    for graph in sorted_list:
        if is_label_isomorphic(correct, graph, "label"):
            return position
        position += 1
    return -1


def frequency_key(lattice, element):
    return lattice[element][1]


def compression_key(lattice, element):
    return lattice[element][0]


def compression_key_item(lattice, item):
    return lattice[item[0]][0]


def lattice_pruned_list_sorted(sg_lattice, pruning, sorting_key):
    pruned_lattice = pruning(sg_lattice)
    output = []
    for key in pruned_lattice.keys():
        output.append(key)
        output = output + pruned_lattice[key]
    output.sort(key=functools.partial(sorting_key, sg_lattice), reverse=True)
    return output, pruned_lattice


def average(lst):
    return sum(lst) / len(lst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10])
