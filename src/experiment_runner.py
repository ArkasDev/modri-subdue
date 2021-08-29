"""

"""

import os
import sys
import math
import pickle
import time
import experiment_scripts.evaluation as evaluation
import experiment_scripts.compute_components as compute
from guppy import hpy

# python subdue v1.4
from lib.subdue_python_1_4 import Subdue as subdue_1_4
from lib.subdue_python_1_4 import Parameters as parameters_subdue_1_4

# python subdue v1.4 under test implementation
from subdue_python import Subdue as subdue_1_4_under_test
from subdue_python import Parameters as parameters_subdue_1_4_under_test

# python subdue v1.1
from lib.subdue_python_1_1_pv_2_7 import subdue_python_1_1
from lib.subdue_python_1_1_pv_2_7 import parameters_subdue_python_1_1

# subdue c
from lib.subdue_c import subdue_c as subdue_c
from lib.subdue_c import parameters_subdue_c as parameters_subdue_c

# gspan and gaston
from lib.parsemis.parsemis import ParsemisMiner

# My local experiment_scripts folder paths
experiment_folder_prefix = "SingleEO"
experiment_0_path = "../data/experiment_0"
experiment_1_path = "../data/experiment_1"
experiment_2_path = "../data/experiment_2"

python_v_2_7_path = "C:\\Python2716\\python.exe"

# Relative threshold for the frequent subgraph mining algorithms
relative_threshold = 0.4


def run_experiment(experiment_data_set_path, algorithm="gaston", experiment_folder_prefix=experiment_folder_prefix,
                   skip_preparation=True, skip_mining=False, skip_evaluation=False):
    """
    :param experiment_data_set_path: Path to the experiment_scripts data set
    :param algorithm: Use an algorithm for graph mining the model repositories: gaston, gspan, subdue_c, subdue_python, modri_subdue
    :param skip_preparation: If true it skips the experiment_scripts preparation. Usually only needs to be performed once
    :param skip_mining: If true it skips the graph mining phase
    :param skip_evaluation: If true it skips the evaluation phase
    """

    if not skip_preparation:
        prepare_experiment(experiment_data_set_path, experiment_folder_prefix=experiment_folder_prefix)

    if not skip_mining:
        run_graph_mining(experiment_data_set_path, algorithm, experiment_folder_prefix=experiment_folder_prefix)

    if not skip_evaluation:
        experiment_evaluation(experiment_data_set_path, algorithm, experiment_folder_prefix=experiment_folder_prefix)


def prepare_experiment(experiment_data_set_path, experiment_folder_prefix=experiment_folder_prefix):
    print("########################################")
    print("### Experiment preparation ")
    print("########################################")

    print("Preparation running...")

    # Loop through all single data sets in the experiment_scripts folder
    for single_set_name in os.listdir(experiment_data_set_path):

        # Ignore other files in the experiment_scripts root folder, just loop through single data set folders
        if not single_set_name.startswith(experiment_folder_prefix):
            continue

        # Create graph input files via compute component script
        # These graph files are required as input for the mining graph algorithms
        compute.main(experiment_data_set_path + "/" + single_set_name)

        # Compute threshold required for the mining phase of the frequent subgraph mining algorithms
        threshold = compute_threshold(experiment_data_set_path + "/" + single_set_name + "/connected_components.aids")

        # Save the threshold for the execution of frequent subgraph mining algorithms
        with open(experiment_data_set_path + "/" + single_set_name + "/threshold.txt", 'w') as threshold_file:
            threshold_file.write(str(threshold))

        # Create empty output graph file so that after the mining phase of each single data set the output graph can be written
        with open(experiment_data_set_path + "/" + single_set_name + "/fsg.output", 'w') as output_graph_file:
            output_graph_file.write("")

        # Plot correct graphs
        graph = []
        correct_graph_1 = pickle.load(open(experiment_data_set_path + "/correct_graph_networkx.p", "rb"))
        graph.append(correct_graph_1)
        evaluation.plot_graphs(graph, experiment_data_set_path + "/correct_graph")
        graph = []
        correct_graph_2 = pickle.load(open(experiment_data_set_path + "/correct_graph_2_networkx.p", "rb"))
        graph.append(correct_graph_2)
        evaluation.plot_graphs(graph, experiment_data_set_path + "/correct_graph_2")

    print("Preparation done")


def run_graph_mining(experiment_data_set_path, algorithm, experiment_folder_prefix=experiment_folder_prefix):
    print("########################################")
    print("### Graph mining")
    print("########################################")

    print("Mining running...")

    # Loop through all single data sets in the experiment_scripts folder
    for single_set_name in os.listdir(experiment_data_set_path):

        # Ignore other files in the experiment_scripts root folder, just loop through single data set folders
        if not single_set_name.startswith(experiment_folder_prefix):
            continue

        # Start performance test, start measuring the runtime and the heap space
        heap = hpy()
        start_heap_status = heap.heap()
        start_time = time.time()

        # Load the threshold calculated during the preparation phase
        with open(experiment_data_set_path + "/" + single_set_name + "/threshold.txt", 'r') as threshold_file:
            threshold = threshold_file.read()

        # Run the selected graph mining algorithm
        if algorithm == "gaston":
            # Load the aggregated graph of all diffs of this single data set
            graph = experiment_data_set_path + "/%s/connected_components.lg" % single_set_name
            # Run Gaston
            run_gaston(experiment_data_set_path + "/" + single_set_name, graph, threshold)
        if algorithm == "gspan":
            # Load the aggregated graph of all diffs of this single data set
            graph = experiment_data_set_path + "/%s/connected_components.lg" % single_set_name
            # Run Gspan
            run_gspan(experiment_data_set_path + "/" + single_set_name, graph, threshold)
        if algorithm == "subdue_python":
            # Load the aggregated graph of all diffs of this single data set
            graph = experiment_data_set_path + "/%s/connected_components.json" % single_set_name
            # Run Python Subdue
            run_subdue_python(experiment_data_set_path + "/" + single_set_name, graph, False)
        if algorithm == "subdue_python_under_test":
            # Load the aggregated graph of all diffs of this single data set
            graph = experiment_data_set_path + "/%s/connected_components.json" % single_set_name
            # Run Python Subdue
            run_subdue_python(experiment_data_set_path + "/" + single_set_name, graph, True)
        if algorithm == "subdue_python_1_1":
            # Load the aggregated graph of all diffs of this single data set
            graph = experiment_data_set_path + "/%s/connected_components.json" % single_set_name
            # Run Python Subdue
            run_subdue_python_1_1(experiment_data_set_path + "/" + single_set_name, graph)
        if algorithm == "subdue_c":
            graph = experiment_data_set_path + "/%s/connected_components.g" % single_set_name
            # Run C Subdue
            run_subdue_c(experiment_data_set_path + "/" + single_set_name)
        if algorithm == "modri_subdue":
            # Load the aggregated graph of all diffs of this single data set
            graph = experiment_data_set_path + "/%s/connected_components.json" % single_set_name
            # Run ModriSubdue
            run_theobald_subdue(experiment_data_set_path + "/" + single_set_name, graph)

        # End performance test
        end_time = time.time()
        end_heap_status = heap.heap()
        runtime = end_time - start_time
        heap_stats = end_heap_status.diff(start_heap_status)
        print("Runtime: %s s" % runtime)
        print("Heap: %s bytes" % str(heap_stats.size))
        print("-------------------------------")

        # Save runtime (seconds) in file for eval
        with open(experiment_data_set_path + "/" + single_set_name + "/runtime.txt", 'w') as runtime_file:
            runtime_file.write(str(runtime))

        # Save heap size (bytes) in file for eval
        with open(experiment_data_set_path + "/" + single_set_name + "/heap_size.txt", 'w') as heap_size_file:
            heap_size_file.write(str(heap_stats.size))

    print("Mining done")


def run_subdue_python(experiment_path, graph_file, under_test_implementation=False):
    # Convert json graph file to the subdue graph data structure
    print("Graph file: " + experiment_path + " --- " + graph_file)
    graph = subdue_1_4_under_test.read_graph(graph_file)

    # Subdue parameters
    parameters = parameters_subdue_1_4_under_test.Parameters()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_python.output"

    parameters.beamWidth = 3
    parameters.iterations = 1
    parameters.limit = 50
    parameters.maxSize = 50
    parameters.minSize = 3
    parameters.numBest = 1
    parameters.overlap = 'vertex'

    # only for under test
    parameters.eval = 3

    parameters.prune = False
    parameters.valueBased = False

    parameters.writeCompressed = False
    parameters.writePattern = True
    parameters.writeInstances = True
    parameters.temporal = False
    parameters.print()
    parameters.set_defaults_for_graph(graph)

    if under_test_implementation is True:
        print("Start mining with Python Subdue v1.4 under test...\n")
        subdue_1_4_under_test.subdue(parameters, graph)
    else:
        print("Start mining with official Python Subdue v1.4...\n")
        subdue_1_4.Subdue(parameters, graph)


def run_subdue_c(experiment_path):
    print("Start mining with C Subdue v1.1...\n")
    parameters = parameters_subdue_c.ParametersSubdueC()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_c_output.g"
    parameters.graphPath = experiment_path + "/connected_components.g"
    parameters.subdue_lib_windows_location = "..\\lib\\subdue_c\\bin\\subdue.exe"

    parameters.beamWidth = 4
    parameters.iterations = 1
    parameters.limit = 0
    parameters.maxSize = 0
    parameters.minSize = 2
    parameters.numBest = 1
    parameters.overlap = True

    parameters.eval = 2
    parameters.undirected = True
    parameters.prune = False
    parameters.valueBased = False

    subdue_c.run(parameters)


def run_subdue_python_1_1(experiment_path, graph_file):
    print("Start mining with Python Subdue v1.1...\n")

    subdue_windows_location = "..\\lib\\subdue_python_1_1_pv_2_7\\src\\Subdue.py"

    parameters = parameters_subdue_python_1_1.ParametersSubduePython1_1()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_python_1_1.output"
    parameters.inputFileName = graph_file

    parameters.beamWidth = 4
    parameters.iterations = 1
    parameters.limit = 0
    parameters.maxSize = 0
    parameters.minSize = 2
    parameters.numBest = 1

    # Not available in the Subdue version 1.1
    # parameters.overlap

    parameters.prune = False
    parameters.valueBased = False

    subdue_python_1_1.run(python_v_2_7_path, subdue_windows_location, parameters)


def run_theobald_subdue(experiment_path, graph):
    return


def run_gaston(experiment_path, graph, threshold):
    print("Start mining with Gaston...\n")
    ParsemisMiner(experiment_path, debug=False, mine_undirected=False).mine_graphs(
        graph,
        minimum_frequency=threshold,
        maximum_node_count=12,
        minimum_node_count=4,
        store_embeddings=True,
        distribution="threads",
        n_threads=1,
        algorithm="gaston"
    )


def run_gspan(experiment_path, graph, threshold):
    print("Start mining with gSpan...\n")
    ParsemisMiner(experiment_path, debug=False, mine_undirected=False).mine_graphs(
        graph,
        minimum_frequency=threshold,
        maximum_node_count=12,
        minimum_node_count=4,
        store_embeddings=True,
        distribution="threads",
        n_threads=1,
        algorithm="gspan"
    )


def compute_threshold(aids_file_path):
    num_lines = sum(1 for _ in open(aids_file_path))
    number_of_components = num_lines / 3
    return math.ceil(relative_threshold * number_of_components)


def experiment_evaluation(experiment_path, algorithm, experiment_folder_prefix=experiment_folder_prefix):
    print("########################################")
    print("### Evaluation")
    print("########################################")

    print("Evaluation running...")

    # Remove old evaluation files and create new empty files
    os.remove(experiment_path + "/stats_topn.csv")
    os.remove(experiment_path + "/stats_topn_frequency.csv")
    with open(experiment_path + "/stats_topn.csv", 'w') as stats_tpn:
        stats_tpn.write(
            '"cnt_diffs", "cnt_eos", "pertubation", "avg_nb_nodes_per_component", "avg_nb_edges_per_component", "avg_degree_per_component", "avg_nb_components_per_diff", "cnt_components", "support_threshold", "size_at_threshold", "cnt_exact_match", "cnt_exact_match_2", "elapsed_time_mining", "heap_size", "score", "score_2"\r\n')
    with open(experiment_path + "/stats_topn_frequency.csv", 'w') as stats_tpn:
        stats_tpn.write(
            '"cnt_diffs", "cnt_eos", "pertubation", "avg_nb_nodes_per_component", "avg_nb_edges_per_component", "avg_degree_per_component", "avg_nb_components_per_diff", "cnt_components", "support_threshold", "size_at_threshold", "cnt_exact_match", "cnt_exact_match_2", "elapsed_time_mining", "heap_size", "score", "score_2"\r\n')

    # Evaluate each experiment_scripts
    for set_name in os.listdir(experiment_path):

        # Skip other files, just loop through dataset folders
        if not set_name.startswith(experiment_folder_prefix):
            continue

        # Read threshold and runtime
        with open(experiment_path + "/" + set_name + "/threshold.txt", 'r') as threshold_file:
            threshold = threshold_file.read()
        with open(experiment_path + "/" + set_name + "/runtime.txt", 'r') as runtime_file:
            runtime = runtime_file.read()
        with open(experiment_path + "/" + set_name + "/heap_size.txt", 'r') as heap_size_file:
            heap_size = heap_size_file.read()

        # Start evaluation script
        # path, threshold, max_n, elapsed_time_mining, is_simulation, is_evaluation, print_results,...
        evaluation.main(experiment_path + "/" + set_name, threshold, 50, runtime, True, True, True, experiment_path,
                        heap_size, algorithm)

    print("Evaluation done")


if __name__ == "__main__":
    if len(sys.argv) == 4:
        experiment_path = sys.argv[1]
        algorithm = sys.argv[2]
        exp_folder_prefix = sys.argv[3]
    else:
        experiment_path = "../data/experiment_3"
        algorithm = "subdue_python_under_test"
        exp_folder_prefix = experiment_folder_prefix
        run_experiment(experiment_data_set_path=experiment_path, algorithm=algorithm,
                       experiment_folder_prefix=exp_folder_prefix,
                       skip_preparation=True, skip_mining=False, skip_evaluation=False)
