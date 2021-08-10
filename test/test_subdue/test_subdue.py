import pickle

import src.experiment_scripts.compute_components
from src import experiment_scripts
from src.experiment_scripts.evaluation import get_position_sorted_list
from src.experiment_scripts.evaluation import plot_graphs
import src.experiment_scripts.compute_components as compute
from termcolor import colored
import os
from lib.subdue_c import parameters_subdue_c, subdue_c as subdue_c
from src.subdue_python import Subdue, Parameters
import lib.subdue_python_1_1_pv_2_7.subdue_python_1_1 as subdue_python_1_1

python_v_2_7_path = "C:\\Python2716\\python.exe"


def before():
    for f in os.listdir('test_1/results'):
        os.remove(os.path.join('test_1/results', f))
    for f in os.listdir('test_2/results'):
        os.remove(os.path.join('test_2/results', f))


def run_subdue_test_1():
    print("create pilot_test_1")
    correct_nx_graph = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph("test_1/graph_1.json")
    pickle.dump(correct_nx_graph, open("test_1/results/graph_1.p", "wb"))
    plot_graphs([correct_nx_graph], "test_1/results/graph_1")
    compute.export_subdue_c_graph([correct_nx_graph], 'test_1/results/graph_1.g')

    run_subdue_c("test_1/results", "test_1/results/graph_1.g")
    experiment_scripts.compute_components.export_node_link_graph_from_subdue_c_graph("test_1/results/subdue_c_output.g",
                                                                                     "test_1/results/subdue_c_output.json")

    run_subdue_python("test_1/results", "test_1/graph_1.json")

    run_subdue_python_1_1("test_1/results", "test_1/graph_1.json")


def run_subdue_test_2():
    print("create pilot_test_2")
    correct_nx_graph = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph("test_2/graph_2.json")
    pickle.dump(correct_nx_graph, open("test_2/results/graph_2.p", "wb"))
    plot_graphs([correct_nx_graph], "test_2/results/graph_2")
    compute.export_subdue_c_graph([correct_nx_graph], 'test_2/results/graph_2.g')

    run_subdue_c("test_2/results", "test_2/results/graph_2.g")
    experiment_scripts.compute_components.export_node_link_graph_from_subdue_c_graph("test_2/results/subdue_c_output.g",
                                                                                     "test_2/results/subdue_c_output.json")

    run_subdue_python("test_2/results", "test_2/graph_2.json")

    run_subdue_python_1_1("test_2/results", "test_2/graph_2.json")


def run_subdue_c(experiment_path, graph_path):
    parameters = parameters_subdue_c.ParametersSubdueC()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_c_output.g"
    parameters.graphPath = graph_path
    parameters.subdue_lib_windows_location = "..\\..\\lib\\subdue_c\\bin\\subdue.exe"

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


def run_subdue_python_1_1(experiment_path, graph_file):
    subdue_windows_location = "..\\..\\lib\\subdue_python_1_1_pv_2_7\\src\\Subdue.py"

    parameters = Parameters.Parameters()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_python_1_1_output"
    parameters.inputFileName = graph_file

    parameters.beamWidth = 4
    parameters.iterations = 1
    parameters.limit = 50
    parameters.maxSize = 50
    parameters.minSize = 1
    parameters.numBest = 1

    # Not available in the Subdue version 1.1
    # parameters.overlap

    parameters.prune = False
    parameters.valueBased = False

    parameters.writeCompressed = False
    parameters.writePattern = True
    parameters.writeInstances = True
    parameters.temporal = False

    subdue_python_1_1.run(python_v_2_7_path, subdue_windows_location, parameters)


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


def test_1_python():
    print("test_1_python")
    correct_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_1/results/subdue_python_output-pattern-1.json")
    mined_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_1/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def test_2_python():
    print("test_2_python")
    correct_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_2/results/subdue_python_output-pattern-1.json")
    mined_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_2/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def test_1_python_1_1():
    print("test_1_python_1_1")
    correct_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_1/results/subdue_python_1_1_output-pattern-1.json")
    mined_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_1/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def test_2_python_1_1():
    print("test_2_python_1_1")
    correct_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_2/results/subdue_python_1_1_output-pattern-1.json")
    mined_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_2/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def test_1_c():
    print("test_1_c")
    correct_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_1/results/subdue_c_output.json")
    mined_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_1/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


def test_2_c():
    print("test_2_c")
    correct_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_2/results/subdue_c_output.json")
    mined_pattern = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        "test_2/correct_graph.json")
    score = get_position_sorted_list(correct_pattern, [mined_pattern])
    if score == -1:
        print(colored("Error. Output: " + str(score), "red"))
    else:
        print(colored("Passed. Output: " + str(score), "green"))
    print("--------------------------------------------")


if __name__ == "__main__":
    before()

    run_subdue_test_1()
    run_subdue_test_2()

    test_1_python()
    test_2_python()
    test_1_python_1_1()
    test_2_python_1_1()
    test_1_c()
    test_2_c()
