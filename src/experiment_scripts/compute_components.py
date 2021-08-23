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
        f.write('t # ' + str(i) + '\n')
        temp_graph = nx.convert_node_labels_to_integers(graph, first_label=0)
        # sort indices
        vertices = temp_graph.nodes(data=True)
        for node, data in vertices:
            f.write("v " + str(node) + " " + data['label'] + '\n')
        edges = temp_graph.edges(data=True)
        for source, target, data in edges:
            f.write("e " + str(source) + " " + str(target) + " " + data['label'] + '\n')
            # TODO REMOVE IF WRONG
            # f.write("e " + str(target) + " " + str(source) + " " + data['label'] + '\n')
        i = i + 1
    f.close()


def export_TLV_numeric_labels(graph_db, path, label_path):
    f = open(path, 'w')
    i = 0
    labels = {}
    current = 1
    edge_count = 100
    for graph in graph_db:
        f.write('t # ' + str(i) + '\n')
        temp_graph = nx.convert_node_labels_to_integers(graph, first_label=0)
        # sort indices
        vertices = temp_graph.nodes(data=True)
        for node, data in vertices:
            label = data['label']
            if label not in labels:
                labels[label] = current
                current += 1
            f.write("v " + str(node) + " " + str(labels[label]) + '\n')
        edges = temp_graph.edges(data=True)
        for source, target, data in edges:
            label = data['label']
            if label not in labels:
                labels[label] = current
                current += 1
            f.write("e " + str(source) + " " + str(target) + " " + str(labels[label]) + '\n')
            # TODO REMOVE IF WRONG
            # f.write("e " + str(target) + " " + str(source) + " " + str(labels[label]) + '\n')
        i = i + 1
    f.close()

    f = open(label_path, 'w')
    for k, v in labels.items():
        f.write(k + " " + str(v) + '\n')
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


def export_subdue_c_graph(graph_db, path):
    with open(path, 'w') as output_graph_file:
        last_node_id_from_last_graph = 1
        last_edge_id_from_last_graph = 1

        for i, graph in enumerate(graph_db):
            temp_graph = nx.convert_node_labels_to_integers(graph, first_label=0)
            vertices = temp_graph.nodes(data=True)
            edges = temp_graph.edges(data=True)

            starting_node_id_from_current_graph = last_node_id_from_last_graph

            for n, node in enumerate(vertices):
                output_graph_file.write('v ' + str(last_node_id_from_last_graph + n) + ' ' + node[1]['label'] + '\n')
                # Last edge
                if n == len(vertices) - 1:
                    last_node_id_from_last_graph = last_node_id_from_last_graph + n + 1

            for j, edge in enumerate(edges):
                output_graph_file.write('u ' + str(edge[0] + starting_node_id_from_current_graph) + ' ' + str(
                    edge[1] + starting_node_id_from_current_graph) + ' ' + str(edge[2]['label']) + '\n')


def export_subdue_python_json(graph_db, path):
    with open(path, 'w') as output_graph_file:
        output_graph_file.write('[\n')
        last_node_id_from_last_graph = 0
        last_edge_id_from_last_graph = 0

        for i, graph in enumerate(graph_db):
            temp_graph = nx.convert_node_labels_to_integers(graph, first_label=0)
            vertices = temp_graph.nodes(data=True)
            edges = temp_graph.edges(data=True)

            starting_node_id_from_current_graph = last_node_id_from_last_graph

            for n, node in enumerate(vertices):
                output_graph_file.write('  {"vertex": {\n')
                output_graph_file.write('    "id": "' + str(last_node_id_from_last_graph + n) + '",\n')
                output_graph_file.write('    "attributes": {"label": "' + node[1]['label'] + '"}}},\n')
                # Last edge
                if n == len(vertices) - 1:
                    last_node_id_from_last_graph = last_node_id_from_last_graph + n + 1

            for j, edge in enumerate(edges):
                output_graph_file.write('  {"edge": {\n')
                output_graph_file.write('    "id": "' + str(last_edge_id_from_last_graph + j) + '",\n')
                output_graph_file.write('    "source": "' + str(edge[0] + starting_node_id_from_current_graph) + '",\n')
                output_graph_file.write('    "target": "' + str(edge[1] + starting_node_id_from_current_graph) + '",\n')
                output_graph_file.write('    "directed": "false",\n')

                # Check for the last edge
                if j == len(edges) - 1:
                    last_edge_id_from_last_graph = last_edge_id_from_last_graph + j + 1
                    # Dont write a comma for the last attribute in the file
                    if len(graph_db) == i + 1:
                        output_graph_file.write('    "attributes": {"label": "' + str(edge[2]['label']) + '"}}}\n')
                    else:
                        output_graph_file.write('    "attributes": {"label": "' + str(edge[2]['label']) + '"}}},\n')
                else:
                    output_graph_file.write('    "attributes": {"label": "' + str(edge[2]['label']) + '"}}},\n')

        output_graph_file.write(']\n')


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


def convert_node_link_graph_to_parsemis_directed_graph(input_file, output_file):
    """
    Convert node link graph to graph used in the parsemis graph lib https://github.com/timtadh/parsemis.
    """
    json_file = json.load(open(input_file))

    with open(output_file, 'a') as the_file:
        the_file.write('t # graph_id\n')

        # Add vertex
        for node in json_file['nodes']:
            the_file.write('v' + ' ' + str(node['id']) + ' ' + node['label'] + '\n')

        # Add edge
        for i, edge in enumerate(json_file['links']):
            the_file.write('e' + ' ' + str(edge['source']) + ' ' + str(edge['target']) + ' ' + edge['label'] + '\n')


def convert_node_link_graph_to_subdue_c_graph(input_file, output_file):
    """
    Convert node link graph to graph used in the subdue_python c implementation https://github.com/gromgull/subdue.
    """
    json_file = json.load(open(input_file))

    with open(output_file, 'a') as the_file:

        # Add vertex
        for node in json_file['nodes']:
            the_file.write('v' + ' ' + str(int(node['id']) + 1) + ' ' + node['label'] + '\n')

        # Add edge
        for i, edge in enumerate(json_file['links']):
            the_file.write('u' + ' ' + str(int(edge['source']) + 1) + ' ' +
                           str(int(edge['target']) + 1) + ' ' + edge['label'] + '\n')


def convert_node_link_graph_to_subdue_python_graph(input_file, output_file):
    """
    Convert node link graph to graph used in the subdue_python python implementation https://github.com/holderlb/Subdue.
    """
    json_file = json.load(open(input_file))

    with open(output_file, 'a') as the_file:
        the_file.write('[\n')

        # Add vertex
        for node in json_file['nodes']:
            the_file.write('  {"vertex": {\n')
            the_file.write('    "id": "' + str(node['id']) + '",\n')
            the_file.write('    "attributes": {"label": "' + node['label'] + '"}}},\n')

        # Add edge
        for i, edge in enumerate(json_file['links']):
            the_file.write('  {"edge": {\n')
            the_file.write('    "id": "' + str(i + 1) + '",\n')
            the_file.write('    "source": "' + str(edge['source']) + '",\n')
            the_file.write('    "target": "' + str(edge['target']) + '",\n')
            the_file.write('    "directed": "false",\n')
            if i != len(json_file['links']) - 1:
                the_file.write('    "attributes": {"label": "' + edge['label'] + '"}}},\n')
            # Last element
            else:
                the_file.write('    "attributes": {"label": "' + edge['label'] + '"}}}\n')

        # Add edge
        the_file.write(']\n')


def export_node_link_graph_from_subdue_c_graph(input_file, output_file):
    empty_input = False
    with open(output_file, 'w') as output:
        output.write("[\n")

        with open(input_file, "r") as check_empty:
            if check_empty.readline() == "":
                empty_input = True

        if empty_input is False:
            with open(input_file, "r") as input_g:
                edge_id = 1
                for line in input_g.readlines():
                    if line.startswith("v"):
                        elements = line.split(" ")
                        label_without_linebreak = elements[2].split("\n")
                        output.write('  {"vertex": {\n')
                        output.write('    "id": "' + elements[1] + '",\n')
                        output.write('    "attributes": {"label": "' + label_without_linebreak[0] + '"}}},\n')
                    if line.startswith("u"):
                        elements = line.split(" ")
                        label_without_linebreak = elements[3].split("\n")
                        output.write('  {"edge": {\n')
                        output.write('    "id": "' + str(edge_id) + '",\n')
                        output.write('    "source": "' + elements[1] + '",\n')
                        output.write('    "target": "' + elements[2] + '",\n')
                        output.write('    "directed": "false",\n')
                        output.write('    "attributes": {"label": "' + label_without_linebreak[0] + '"}}},\n')
                        edge_id = edge_id + 1
        output.write("]")

    if empty_input is False:
        with open(output_file, 'rb+') as remove_last_comma_handler:
            remove_last_comma_handler.seek(-4, 2)
            remove_last_comma_handler.truncate()
        with open(output_file, "a") as add_last_bracket_handler:
            add_last_bracket_handler.write("\n]")


def convert_node_link_graph_to_nx_graph(file):
    json_file = json.load(open(file))
    nodes = []
    node_names = []
    edges = []
    edge_names = []

    for json_dict in json_file:
        for key, value in json_dict.items():
            if key == 'vertex':
                nodes.insert(int(value['id']), value['attributes']['label'])
                node_names.insert(int(value['id']), value['id'])

            if key == 'edge':
                edges.insert(int(value['id']), [value['source'], value['target']])
                edge_names.insert(int(value['id']), value['attributes']['label'])

    graph = nx.Graph()

    # Add nodes to nx graph
    i = 0
    for node in node_names:
        graph.add_node(node, label=nodes[i])
        i = i + 1

    # Add edges to nx graph
    i = 0
    for edge in edges:
        graph.add_edge(edge[0], edge[1], label=edge_names[i])
        i = i + 1

    return graph


def main(args):
    set_name = args
    # Load components
    components, nb_of_components_per_diff = load_components_networkx(set_name + '/diffgraphs', filtered=True)
    # Exports
    export_TLV(components, set_name + '/connected_components.lg')
    export_TLV_numeric_labels(components, set_name + '/connected_components_numeric.lg', set_name + '/labels.out')
    export_aids(components, set_name + '/connected_components.aids')
    export_subdue_c_graph(components, set_name + '/connected_components.g')
    export_subdue_python_json(components, set_name + '/connected_components.json')


if __name__ == "__main__":
    main(sys.argv[1])
