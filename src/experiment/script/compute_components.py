import os
import sys
import json
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np


def connected_components(graph):
    components = [graph.subgraph(c).copy() for c in nx.connected_components(graph)]
    return components


# Export TLV (gSpan consumes TLV)
def export_TLV(graph_db, path):
    f = open(path, 'w')
    i = 0
    for graph in graph_db:
        f.write('t # ' + str(i) + '\r')
        temp_graph = nx.convert_node_labels_to_integers(graph, first_label=0)
        # sort indices
        vertices = temp_graph.nodes(data=True)
        for node, data in vertices:
            f.write("v " + str(node) + " " + data['label'] + '\r')
        edges = temp_graph.edges(data=True)
        for source, target, data in edges:
            f.write("e " + str(source) + " " + str(target) + " " + data['label'] + '\r')
        i = i + 1
    f.close()


# See https://github.com/pwelke/hops/blob/master/smallgraphs/util/converter/gSpan2aids.py
def export_aids(graph_db, path):
    f = open(path, 'w')
    i = 0
    for graph in graph_db:
        temp_graph = nx.convert_node_labels_to_integers(graph, first_label=0)
        vertices = temp_graph.nodes(data=True)
        edges = temp_graph.edges(data=True)
        if len(vertices) == 0:
            return
        # write graph header
        f.write('# ' + str(i) + ' 0 ' + str(len(vertices)) + ' ' + str(len(edges)) + '\r')
        # TODO: sort and check if vertex indices are correctly ordered
        for node, data in vertices:
            f.write(data['label'] + ' ')
        f.write('\r')
        for source, target, data in edges:
            f.write(str(int(source) + 1) + ' ' + str(int(target) + 1) + ' ' + data['label'] + ' ')
        f.write('\r')
        i = i + 1
    f.close()


# TODO this can be done asynchronously using yield
def load_components_networkx(folder, filtered=False):
    components = []
    nb_of_components_per_diff = []
    for filename in os.listdir(folder):
        if not filename.endswith('.json'):
            continue
        with open(os.path.join(folder, filename), 'r') as f:  # open in readonly mode
            json_str = f.read()
            data = json.loads(json_str)
            f.close()
            H = json_graph.node_link_graph(data)
            # Compute connected components for the diff graph
            new_components = connected_components(H)
            if filtered:
                new_components = filter_too_large(filter_too_many_similar_nodes(new_components))
            nb_of_components_per_diff.append(len(new_components))
            components += new_components
    return components, nb_of_components_per_diff


# TODO use some pattern to apply multiple filters
# Filters components with more than nb_nodes/nb_edges nodes/edges. Use -1 for infinity.
def filter_too_large(components: list, nb_nodes=120, nb_edges=220):
    for component in components:
        if nb_nodes != -1 and component.number_of_nodes() > nb_nodes:
            components.remove(component)
        elif nb_edges != -1 and component.number_of_edges() > nb_edges:
            components.remove(component)
    return components


# Several filters need to be applied to filter out components which could lead to too high computational efforts
def filter_too_many_similar_nodes(components: list, max_similar=0, max_nodes=10):
    for component in components:
        labels = label_count_for_component(component)
        # if there are more than n node labels with more than m nodes
        if np.sum(np.array(list(labels.values())) > max_nodes) > max_similar:
            components.remove(component)
    return components


def label_count_for_component(component):
    labels = {}
    for node in component.nodes(data=True):
        if node[1]['label'] in labels.keys():
            labels[node[1]['label']] += 1
        else:
            labels[node[1]['label']] = 1
    return labels


def main(args):
    set_name = args
    # Load components
    components, nb_of_components_per_diff = load_components_networkx("./" + set_name + '/diffgraphs', filtered=True)
    # Export in TLV
    export_TLV(components, "./" + set_name + '/connected_components.lg')
    export_aids(components, "./" + set_name + '/connected_components.aids')


if __name__ == "__main__":
    main(sys.argv[1])
