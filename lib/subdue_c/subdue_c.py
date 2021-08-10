"""
This is a wrapper script for the Subdue C implementation
https://github.com/gromgull/subdue
"""

import os


def run(parameters):
    print("Graph path: " + parameters.graphPath)

    graph = parameters.graphPath
    prune = '-prune ' if parameters.prune is True else ''
    value_based = '-valuebased ' if parameters.valueBased is True else ''
    overlap = '-overlap ' if parameters.overlap is True else ''

    undirected = '-undirected ' if parameters.undirected is True else ''
    eval = '-eval 1' if parameters.eval == 1 else '-eval 2'

    limit = '-limit ' + str(parameters.limit) if parameters.limit != 0 else ''
    maxsize = '-maxsize ' + str(parameters.maxSize) if parameters.maxSize != 0 else ''

    subdue_lib_windows_location = parameters.subdue_lib_windows_location

    # parameters.outputFileName = "C:\\Users\\david\\PycharmProjects\\theobald-subdue\\data\\experiment_subdue_c\\SingleEO_10_eo1_p0,1\\test"
    # parameters.outputFileName = "C:/Users/david/PycharmProjects/theobald-subdue/data/experiment_subdue_c/SingleEO_10_eo1_p0,1/test"
    # print(parameters.outputFileName)

    if not os.path.isfile(subdue_lib_windows_location):
        raise Exception("Subdue C lib could not found.")

    if os.name == "posix":
        raise Exception("Subdue C wrapper not defined under linux.")

    if os.name == "nt":
        os.system(subdue_lib_windows_location + ' '
                  '-out ' + parameters.outputFileName + ' '
                  '-beam ' + str(parameters.beamWidth) + ' '
                  '' + eval + ' '
                  '-minsize ' + str(parameters.minSize) + ' '
                  '' + maxsize + ' '
                  '' + undirected + ' '
                  '' + limit + ' '
                  '-iterations ' + str(parameters.iterations) + ' '
                  '-nsubs ' + str(parameters.numBest) + ' '
                  '' + overlap + ''
                  '' + value_based + ''
                  '' + prune + ''
                  '' + graph
                  )
