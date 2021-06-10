"""
This is a wrapper script for the Subdue C implementation
https://github.com/gromgull/subdue
"""

import subprocess
import os
import subdue_python.Parameters as Parameters
from termcolor import colored

def run(parameters):
    print("Graph path: " + parameters.graphPath)

    graph = parameters.graphPath
    prune = '-prune ' if parameters.prune is True else ''
    value_based = '-valuebased ' if parameters.valueBased is True else ''
    overlap = '-overlap ' if parameters.overlap is True else ''
    subdue_lib_windows_location = parameters.subdue_lib_windows_location

    if os.name == "posix":
        raise Exception("Subdue C wrapper not defined under linux.")

    if os.name == "nt":
        os.system(subdue_lib_windows_location + ' '
                  '-beam ' + str(parameters.beamWidth) + ' '
                  '-minsize ' + str(parameters.minSize) + ' '
                  '-maxsize ' + str(parameters.maxSize) + ' '
                  '-limit ' + str(parameters.limit) + ' '
                  '-iterations ' + str(parameters.iterations) + ' '
                  '-nsubs ' + str(parameters.numBest) + ' '
                  '' + overlap + ''
                  '' + value_based + ''
                  '' + prune + ''
                  '-out ' + parameters.outputFileName + ' '
                  '' + graph)
