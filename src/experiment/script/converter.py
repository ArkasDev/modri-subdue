import networkx as nx
import json
import os

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
