import util.converter as converter


def convert_node_link_to_subdue_python_graph():
    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_1.json',
                                                '../asset/output/diff_1_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_2.json',
                                                '../asset/output/diff_2_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_3.json',
                                                '../asset/output/diff_3_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_4.json',
                                                '../asset/output/diff_4_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_5.json',
                                                '../asset/output/diff_5_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_6.json',
                                                '../asset/output/diff_6_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_7.json',
                                                '../asset/output/diff_7_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_8.json',
                                                '../asset/output/diff_8_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_9.json',
                                                '../asset/output/diff_9_subdue_graph.json')

    converter.convert_node_link_graph_to_subdue_python_graph('../../asset/data/phasetransition/diff_10.json',
                                                '../asset/output/diff_10_subdue_graph.json')


def convert_node_link_to_subdue_c_graph():
    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_1.json',
                                                             '../asset/output/subdue_c/diff_1_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_2.json',
                                                             '../asset/output/subdue_c/diff_2_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_3.json',
                                                             '../asset/output/subdue_c/diff_3_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_4.json',
                                                             '../asset/output/subdue_c/diff_4_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_5.json',
                                                             '../asset/output/subdue_c/diff_5_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_6.json',
                                                             '../asset/output/subdue_c/diff_6_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_7.json',
                                                             '../asset/output/subdue_c/diff_7_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_8.json',
                                                             '../asset/output/subdue_c/diff_8_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_9.json',
                                                             '../asset/output/subdue_c/diff_9_subdue_c_graph.g')

    converter.convert_node_link_graph_to_subdue_c_graph('../../asset/data/phasetransition/diff_10.json',
                                                             '../asset/output/subdue_c/diff_10_subdue_c_graph.g')


def convert_node_link_to_parsemis_graph():
    converter.convert_node_link_graph_to_parsemis_directed_graph('../../asset/data/phasetransition/diff_1.json',
                                                             '../asset/output/parsemis/diff_1_parsemis.lg')


if __name__ == "__main__":
    # convert_node_link_to_subdue_python_graph()
    # convert_node_link_to_subdue_c_graph()
    convert_node_link_to_parsemis_graph()
