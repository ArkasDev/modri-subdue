import networkx as nx
import json


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
    Convert node link graph to graph used in the subdue c implementation https://github.com/gromgull/subdue.
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
    Convert node link graph to graph used in the subdue python implementation https://github.com/holderlb/Subdue.
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
