import os
import experiment_scripts.compute_components as compute
from subdue_python import Subdue, Parameters

# data_set = "SingleEO_10_eo1_p0,1"
data_set = "SingleEO_10_eo17_p0,5"

def before():
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

    parameters.beamWidth = 3
    parameters.iterations = 1
    parameters.limit = 30
    parameters.maxSize = 7
    parameters.minSize = 4
    parameters.numBest = 1
    parameters.overlap = 'true'

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
