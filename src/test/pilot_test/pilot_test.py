import pickle
from experiment.script.eval import get_position_sorted_list
from experiment.script.eval import plot_graphs
import experiment.script.converter as converter
import experiment.script.compute_components as compute
from termcolor import colored
import experiment_runner as runner
import subdue_c.subdue_c as subdue_c
from subdue_c import parameters_subdue_c
from subdue_python import Subdue, Parameters


def pilot_test_1():
    print("create pilot_test_1")
    correct_nx_graph = converter.convert_node_link_graph_to_nx_graph("test_1/graph_1.json")
    pickle.dump(correct_nx_graph, open("test_1/graph_1.p", "wb"))
    plot_graphs([correct_nx_graph], "test_1/graph_1")
    compute.export_subdue_c_graph([correct_nx_graph], 'test_1/graph_1.g')

    run_subdue_c("test_1", "test_1/graph_1.g")
    converter.export_node_link_graph_from_subdue_c_graph("test_1/subdue_c_output.g", "test_1/subdue_c_output.json")

    run_subdue_python("test_1", "test_1/graph_1.json")


def pilot_test_2():
    print("create pilot_test_2")
    correct_nx_graph = converter.convert_node_link_graph_to_nx_graph("test_2/graph_2.json")
    pickle.dump(correct_nx_graph, open("test_2/graph_2.p", "wb"))
    plot_graphs([correct_nx_graph], "test_2/graph_2")
    compute.export_subdue_c_graph([correct_nx_graph], 'test_2/graph_2.g')

    run_subdue_c("test_2", "test_2/graph_2.g")
    converter.export_node_link_graph_from_subdue_c_graph("test_2/subdue_c_output.g", "test_2/subdue_c_output.json")

    run_subdue_python("test_2", "test_2/graph_2.json")


def run_subdue_c(experiment_path, graph_path):
    parameters = parameters_subdue_c.ParametersSubdueC()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_c_output.g"
    parameters.graphPath = graph_path
    parameters.subdue_lib_windows_location = "..\\..\\..\\lib\\subdue_c\\bin\\subdue.exe"

    parameters.beamWidth = 4
    parameters.iterations = 1
    parameters.limit = 50
    parameters.maxSize = 50
    parameters.minSize = 1
    parameters.numBest = 1
    parameters.overlap = True

    parameters.prune = False
    parameters.valueBased = False

    subdue_c.run(parameters)


def run_subdue_python(experiment_path, graph_file):
    graph = Subdue.read_graph(graph_file)

    parameters = Parameters.Parameters()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_python_output"

    parameters.beamWidth = 4
    parameters.iterations = 1
    parameters.limit = 50
    parameters.maxSize = 50
    parameters.minSize = 1
    parameters.numBest = 1
    parameters.overlap = 'vertex'

    parameters.prune = False
    parameters.valueBased = False

    parameters.writeCompressed = False
    parameters.writePattern = True
    parameters.writeInstances = True
    parameters.temporal = False
    parameters.print()
    parameters.set_defaults_for_graph(graph)

    Subdue.subdue(parameters, graph)


def check_test_1_python():
    print("check_test_1_python")
    correct_pattern = converter.convert_node_link_graph_to_nx_graph("test_1/subdue_python_output-pattern-1.json")
    mined_pattern = converter.convert_node_link_graph_to_nx_graph("test_1/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def check_test_2_python():
    print("check_test_2_python")
    correct_pattern = converter.convert_node_link_graph_to_nx_graph("test_2/subdue_python_output-pattern-1.json")
    mined_pattern = converter.convert_node_link_graph_to_nx_graph("test_2/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def check_test_1_c():
    print("check_test_1_c")
    correct_pattern = converter.convert_node_link_graph_to_nx_graph("test_1/subdue_c_output.json")
    mined_pattern = converter.convert_node_link_graph_to_nx_graph("test_1/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def check_test_2_c():
    print("check_test_2_c")
    correct_pattern = converter.convert_node_link_graph_to_nx_graph("test_2/subdue_c_output.json")
    mined_pattern = converter.convert_node_link_graph_to_nx_graph("test_2/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


if __name__ == "__main__":
    pilot_test_1()
    pilot_test_2()

    check_test_1_python()
    check_test_2_python()
    check_test_1_c()
    check_test_2_c()
