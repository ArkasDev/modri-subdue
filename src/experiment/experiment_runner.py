import os
import math
import time
import experiment.script.eval as evaluation
import experiment.script.compute_components as compute
from guppy import hpy
from util.parsemis import ParsemisMiner

experiment_0_path = "../../data/experiment_0"
experiment_1_path = "../../data/experiment_1"
experiment_2_path = "../../data/experiment_2"

relative_threshold = 0.1


def run_experiment(data_set_path, algorithm="gaston", skip_preparation=True, skip_mining=False, skip_evaluation=False):
    if not skip_preparation:
        prepare_experiment(data_set_path)

    if not skip_mining:
        run_graph_mining(data_set_path, algorithm)

    if not skip_evaluation:
        experiment_evaluation(data_set_path)


def prepare_experiment(experiment_path):
    print("########################################")
    print("### Experiment preparation ")
    print("########################################")

    for set_name in os.listdir(experiment_path):

        # Skip other files, just loop through dataset folders
        if not set_name.startswith("SingleEO"):
            continue

        # Create .lg and .aids file via compute component script
        compute.main(experiment_path + "/" + set_name)

        # Compute threshold
        threshold = compute_threshold(experiment_path + "/" + set_name + "/connected_components.aids")

        # Save the threshold for the execution of frequent subgraph mining algorithms
        with open(experiment_path + "/" + set_name + "/threshold.txt", 'w') as threshold_file:
            threshold_file.write(str(threshold))

        # Create empty output graph file
        with open(experiment_path + "/" + set_name + "/fsg.output", 'w') as output_graph_file:
            output_graph_file.write("")


def run_graph_mining(experiment_path, algorithm):
    print("########################################")
    print("### Graph mining")
    print("########################################")

    for set_name in os.listdir(experiment_path):

        # Skip other files, just loop through dataset folders
        if not set_name.startswith("SingleEO"):
            continue

        graph = experiment_path + "/%s/connected_components.lg" % set_name

        # Start performance test
        heap = hpy()
        start_heap_status = heap.heap()
        start_time = time.time()

        # Load threshold
        with open(experiment_path + "/" + set_name + "/threshold.txt", 'r') as threshold_file:
            threshold = threshold_file.read()

        # Run mining algorithm
        if algorithm == "gaston":
            run_gaston(experiment_path + "/" + set_name, graph, threshold)
        if algorithm == "gspan":
            run_gspan(experiment_path + "/" + set_name, graph, threshold)

        # End performance test
        end_time = time.time()
        end_heap_status = heap.heap()
        runtime = end_time - start_time
        heap_stats = end_heap_status.diff(start_heap_status)
        print("Runtime: %s s" % runtime)
        print("Heap: %s bytes" % heap_stats.size)
        print("-------------------------------")

        # Save runtime in file for eval
        with open(experiment_path + "/" + set_name + "/runtime.txt", 'w') as runtime_file:
            runtime_file.write(str(runtime))


def run_gaston(experiment_path, graph, threshold):
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
    ParsemisMiner(experiment_path, debug=False, mine_undirected=False).mine_graphs(
        graph,
        minimum_frequency=threshold,
        maximum_node_count=12,
        minimum_node_count=4,
        store_embeddings=True,
        distribution="threads",
        n_threads=1,
        algorithm="gpsan"
    )


def compute_threshold(aids_file_path):
    num_lines = sum(1 for _ in open(aids_file_path))
    number_of_components = num_lines / 3
    return math.ceil(relative_threshold * number_of_components)


def experiment_evaluation(experiment_path):
    print("########################################")
    print("### Evaluation")
    print("########################################")

    for set_name in os.listdir(experiment_path):

        # Skip other files, just loop through dataset folders
        if not set_name.startswith("SingleEO"):
            continue

        # Read threshold and runtime
        with open(experiment_path + "/" + set_name + "/threshold.txt", 'r') as threshold_file:
            threshold = threshold_file.read()
        with open(experiment_path + "/" + set_name + "/runtime.txt", 'r') as runtime_file:
            runtime = runtime_file.read()

        # Start evaluation script
        evaluation.main(experiment_path + "/" + set_name, threshold, 50, runtime, True, True, False, experiment_path)


if __name__ == "__main__":
    run_experiment(data_set_path=experiment_0_path, algorithm="gaston", skip_preparation=True, skip_mining=True, skip_evaluation=False)
