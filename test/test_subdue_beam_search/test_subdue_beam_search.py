import os

import experiment_scripts
import experiment_scripts.compute_components as compute
from experiment_scripts.evaluation import plot_graphs
from subdue_python import Subdue, Parameters

# positive example
# beamWidth=3 iterations=1 limit=30 maxSize=7 minSize=4 numBest=1 overlap='vertex' eval=1
# data_set = "SingleEO_10_eo1_p0,1"

# negative example
# beamWidth=3 iterations=1 limit=30 maxSize=7 minSize=4 numBest=1 overlap='vertex' eval=1
data_set = "SingleEO_10_eo97_p0,5"


def before():
    if not os.path.exists(data_set + '/beam_search'):
        os.mkdir(data_set + '/beam_search')
    if not os.path.exists(data_set + '/beam_search/1. init'):
        os.mkdir(data_set + '/beam_search/1. init')
    if not os.path.exists(data_set + '/beam_search/2. expansion'):
        os.mkdir(data_set + '/beam_search/2. expansion')
    if not os.path.exists(data_set + '/beam_search/3. current'):
        os.mkdir(data_set + '/beam_search/3. current')
    if not os.path.exists(data_set + '/beam_search/4. result'):
        os.mkdir(data_set + '/beam_search/4. result')

    for f in os.listdir(data_set + '/beam_search/1. init'):
        os.remove(os.path.join(data_set + '/beam_search/1. init', f))

    for f in os.listdir(data_set + '/beam_search/2. expansion'):
        for d in os.listdir(data_set + '/beam_search/2. expansion/' + f):
            os.remove(os.path.join(data_set + '/beam_search/2. expansion/' + f + '/', d))
        os.rmdir(os.path.join(data_set + '/beam_search/2. expansion/' + f))

    for list_dir in os.listdir(data_set + '/beam_search/3. current'):
        for step in os.listdir(data_set + '/beam_search/3. current/' + list_dir):
            for file in os.listdir(data_set + '/beam_search/3. current/' + list_dir + '/' + step):
                os.remove(os.path.join(data_set + '/beam_search/3. current/' + list_dir + '/' + step + '/', file))
            os.rmdir(os.path.join(data_set + '/beam_search/3. current/' + list_dir + '/' + step))
        os.rmdir(os.path.join(data_set + '/beam_search/3. current/' + list_dir))

    for f in os.listdir(data_set + '/beam_search/4. result'):
        os.remove(os.path.join(data_set + '/beam_search/4. result', f))


def run_subdue_python(experiment_path, graph_file):
    graph = Subdue.read_graph(graph_file)

    parameters = Parameters.Parameters()
    parameters.experimentFolder = experiment_path
    parameters.outputFileName = experiment_path + "/subdue_python.output"

    parameters.beamWidth = 10
    parameters.iterations = 1
    parameters.limit = 0
    parameters.maxSize = 0
    parameters.minSize = 4
    parameters.numBest = 3
    parameters.overlap = 'vertex'

    parameters.eval = 1

    parameters.prune = False
    parameters.valueBased = False
    parameters.temporal = False

    parameters.beamSearchDebugging = True

    parameters.writeCompressed = False
    parameters.writePattern = True
    parameters.writeInstances = True

    parameters.set_defaults_for_graph(graph)

    Subdue.subdue(parameters, graph)


if __name__ == "__main__":
    before()

    compute.main(data_set)
    graph = data_set + "/connected_components.json"
    run_subdue_python(data_set, graph)

    correct_nx_graph = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(data_set + "/subdue_python.output-pattern-1.json")
    plot_graphs([correct_nx_graph], data_set + "/subdue_python.output-pattern-1")

    correct_nx_graph = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        data_set + "/subdue_python.output-pattern-2.json")
    plot_graphs([correct_nx_graph], data_set + "/subdue_python.output-pattern-2")

    correct_nx_graph = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
        data_set + "/subdue_python.output-pattern-0.json")
    plot_graphs([correct_nx_graph], data_set + "/subdue_python.output-pattern-0")
