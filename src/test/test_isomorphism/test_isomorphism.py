import pickle
from experiment.script.eval import get_position_sorted_list
from experiment.script.eval import plot_graphs
import experiment.script.converter as converter
from termcolor import colored


def test_isomorphism_load_pickle():
    print("test_isomorphism_load_pickle")
    correct = pickle.load(open("correct_graph_networkx.p", "rb"))
    pattern = converter.convert_node_link_graph_to_nx_graph("correct_graph.json")
    score_1 = get_position_sorted_list(correct, [pattern])

    plot_graphs([correct], "correct_graph_networkx")
    plot_graphs([pattern], "correct_graph")

    if score_1 == -1:
        print(colored("Error. Output: " + str(score_1), "red"))
    else:
        print(colored("Passed. Output: " + str(score_1), "green"))
    print("--------------------------------------------")


def test_isomorphism_node_link_graphs():
    print("test_isomorphism_node_link_graphs")
    correct = converter.convert_node_link_graph_to_nx_graph("correct_graph_isomorphic.json")
    pattern = converter.convert_node_link_graph_to_nx_graph("correct_graph.json")
    score_1 = get_position_sorted_list(correct, [pattern])

    plot_graphs([correct], "correct_graph_isomorphic")

    if score_1 == -1:
        print(colored("Error. Output: " + str(score_1), "red"))
    else:
        print(colored("Passed. Output: " + str(score_1), "green"))
    print("--------------------------------------------")


if __name__ == "__main__":
    test_isomorphism_load_pickle()
    test_isomorphism_node_link_graphs()
